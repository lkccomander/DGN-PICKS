from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from dgn_picks_api.domains.games.models import Game
from dgn_picks_api.domains.markets.models import Market, Selection
from dgn_picks_api.domains.odds.models import OddsSnapshot, SportsbookSource
from dgn_picks_api.domains.picks.models import Pick
from dgn_picks_api.domains.providers.fixture import FixtureProvider
from dgn_picks_api.domains.teams.models import Player, Team
from dgn_picks_api.domains.users.models import User
from dgn_picks_api.seed.data import GATO_PICK_DEFINITIONS, SEEDED_USERS
from dgn_picks_api.seed.report import SeedReport


def _find_team(session: Session, name: str) -> Team | None:
    return session.scalars(select(Team).where(Team.name == name)).one_or_none()


def _find_player(session: Session, name: str) -> Player | None:
    return session.scalars(select(Player).where(Player.name == name)).one_or_none()


def seed_local_data(session: Session) -> SeedReport:
    """Insert the deterministic fixture dataset without replacing history."""
    report = SeedReport()
    users: dict[str, User] = {}
    for definition in SEEDED_USERS:
        user = session.scalars(select(User).where(User.username == definition.username)).one_or_none()
        if user is None:
            user = User(username=definition.username, display_name=definition.display_name)
            session.add(user)
            report.users_inserted += 1
        else:
            report.users_existing += 1
        users[definition.username] = user
    session.flush()

    source = session.scalars(
        select(SportsbookSource).where(SportsbookSource.name == "local-fixture")
    ).one_or_none()
    if source is None:
        source = SportsbookSource(name="local-fixture", source_type="fixture")
        session.add(source)
        session.flush()

    provider = FixtureProvider()
    games_by_external_id: dict[str, Game] = {}
    markets_by_key: dict[tuple[str, str], tuple[Market, Selection, OddsSnapshot | None]] = {}
    for normalized_game in provider.list_games(
        (datetime(2026, 1, 1, tzinfo=UTC), datetime(2027, 1, 1, tzinfo=UTC))
    ):
        away = _find_team(session, normalized_game.away_team)
        if away is None:
            away = Team(
                external_ids={"fixture": normalized_game.away_team},
                name=normalized_game.away_team,
                short_name=normalized_game.away_team,
                abbreviation=normalized_game.away_team[:8].upper(),
                conference=normalized_game.conference,
            )
            session.add(away)
        home = _find_team(session, normalized_game.home_team)
        if home is None:
            home = Team(
                external_ids={"fixture": normalized_game.home_team},
                name=normalized_game.home_team,
                short_name=normalized_game.home_team,
                abbreviation=normalized_game.home_team[:8].upper(),
                conference=normalized_game.conference,
            )
            session.add(home)
        session.flush()

        game = next(
            (
                candidate
                for candidate in session.scalars(select(Game)).all()
                if candidate.external_ids.get("fixture") == normalized_game.external_id
            ),
            None,
        )
        if game is None:
            game = Game(
                external_ids={"fixture": normalized_game.external_id},
                season=normalized_game.season,
                week=normalized_game.week,
                kickoff_at=normalized_game.kickoff_at,
                home_team_id=home.id,
                away_team_id=away.id,
                status=normalized_game.status,
                home_score=normalized_game.home_score,
                away_score=normalized_game.away_score,
            )
            session.add(game)
            report.games_inserted += 1
            session.flush()
        games_by_external_id[normalized_game.external_id] = game

        for normalized_market in provider.list_markets(normalized_game.external_id) + provider.list_props(normalized_game.external_id):
            player = None
            if normalized_market.player:
                player = _find_player(session, normalized_market.player)
                if player is None:
                    player = Player(
                        external_ids={"fixture": normalized_market.player},
                        team_id=home.id,
                        name=normalized_market.player,
                        position="unknown",
                    )
                    session.add(player)
                    session.flush()
            market = session.scalars(
                select(Market).where(
                    Market.game_id == game.id,
                    Market.market_type == normalized_market.market_type,
                )
            ).first()
            if market is None:
                market = Market(
                    game_id=game.id,
                    market_type=normalized_market.market_type,
                    period="game",
                    player_id=player.id if player else None,
                    team_id=home.id if normalized_market.team == normalized_game.home_team else away.id if normalized_market.team else None,
                )
                session.add(market)
                report.markets_inserted += 1
                session.flush()
            selection = session.scalars(
                select(Selection).where(
                    Selection.market_id == market.id,
                    Selection.selection_key == normalized_market.selection_key,
                )
            ).one_or_none()
            if selection is None:
                selection = Selection(
                    market_id=market.id,
                    selection_key=normalized_market.selection_key,
                    side=normalized_market.side,
                    team_id=market.team_id,
                    player_id=market.player_id,
                )
                session.add(selection)
                session.flush()
            latest: OddsSnapshot | None = None
            for normalized_snapshot in normalized_market.snapshots:
                latest = session.scalars(
                    select(OddsSnapshot).where(
                        OddsSnapshot.selection_id == selection.id,
                        OddsSnapshot.sportsbook_id == source.id,
                        OddsSnapshot.observed_at == normalized_snapshot.observed_at,
                        OddsSnapshot.source_event_id == normalized_snapshot.source_event_id,
                    )
                ).one_or_none()
                if latest is None:
                    latest = OddsSnapshot(
                        selection_id=selection.id,
                        sportsbook_id=source.id,
                        observed_at=normalized_snapshot.observed_at,
                        line_value=normalized_snapshot.line_value,
                        american_odds=normalized_snapshot.american_odds,
                        decimal_odds=normalized_snapshot.decimal_odds,
                        source_event_id=normalized_snapshot.source_event_id,
                    )
                    session.add(latest)
                    report.snapshots_inserted += 1
                else:
                    report.duplicate_snapshots += 1
            markets_by_key[(normalized_game.external_id, normalized_market.market_type)] = (market, selection, latest)

    session.flush()
    gato = users["gato"]
    for definition in GATO_PICK_DEFINITIONS:
        if definition.side is None:
            report.unresolved_definitions.append(definition.description)
            continue
        match = next(
            (
                (game, market, selection, snapshot)
                for external_id, game in games_by_external_id.items()
                for (game_key, market_type), (market, selection, snapshot) in markets_by_key.items()
                if game_key == external_id
                and market_type == definition.market_type
                and (
                    definition.team_or_player.lower() == selection.selection_key.lower()
                    or definition.team_or_player.lower() == (selection.side or "").lower()
                    or definition.team_or_player.lower() == (session.get(Team, market.team_id).name.lower() if market.team_id else "")
                    or definition.team_or_player.lower() == (session.get(Player, market.player_id).name.lower() if market.player_id else "")
                )
            ),
            None,
        )
        if match is None:
            report.unresolved_definitions.append(definition.description)
            continue
        game, market, selection, snapshot = match
        existing = session.scalars(
            select(Pick).where(Pick.user_id == gato.id, Pick.game_id == game.id, Pick.market_id == market.id)
        ).first()
        if existing is None:
            session.add(
                Pick(
                    user_id=gato.id,
                    game_id=game.id,
                    market_id=market.id,
                    selection_id=selection.id,
                    line_value=Decimal(definition.line_value),
                    american_odds=snapshot.american_odds if snapshot else None,
                    decimal_odds=snapshot.decimal_odds if snapshot else None,
                    stake_units=Decimal("1"),
                    notes=definition.description,
                )
            )
            report.picks_inserted += 1
    session.commit()
    return report
