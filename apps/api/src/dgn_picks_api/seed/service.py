from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from dgn_picks_api.domains.games.models import Game
from dgn_picks_api.domains.markets.models import Market, Selection
from dgn_picks_api.domains.odds.models import OddsSnapshot, SportsbookSource
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
    for definition in SEEDED_USERS:
        user = session.scalars(select(User).where(User.username == definition.username)).one_or_none()
        if user is None:
            user = User(username=definition.username, display_name=definition.display_name)
            session.add(user)
            report.users_inserted += 1
        else:
            report.users_existing += 1
    session.flush()

    source = session.scalars(
        select(SportsbookSource).where(SportsbookSource.name == "local-fixture")
    ).one_or_none()
    if source is None:
        source = SportsbookSource(name="local-fixture", source_type="fixture")
        session.add(source)
        session.flush()

    provider = FixtureProvider()
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

    session.flush()
    # Names alone cannot resolve the event, date, or taken odds of an imported pick.
    # Product definitions are exposed independently; fixture matches are QA data only.
    report.unresolved_definitions.extend(item.description for item in GATO_PICK_DEFINITIONS)
    session.commit()
    return report
