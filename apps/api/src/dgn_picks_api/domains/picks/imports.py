"""Explicit, idempotent manual imports with verified event identity and supplied terms.

This path preserves unknown prices and never creates odds observations. It does not
relax the separate eligibility rules for new predictions through the public API.
"""
from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from hashlib import sha256
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator, model_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from dgn_picks_api.domains.common.enums import GameStatus
from dgn_picks_api.domains.games.models import Game
from dgn_picks_api.domains.markets.models import Market, Selection
from dgn_picks_api.domains.odds.calculations import american_to_decimal
from dgn_picks_api.domains.picks.models import Pick
from dgn_picks_api.domains.teams.models import Player, Team
from dgn_picks_api.domains.users.models import User


class ManifestModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class ImportTeam(ManifestModel):
    name: str = Field(min_length=1, max_length=120)
    short_name: str = Field(min_length=1, max_length=80)
    abbreviation: str = Field(min_length=1, max_length=8)
    conference: str = Field(min_length=1, max_length=64)


class ImportGame(ManifestModel):
    key: str = Field(min_length=1, max_length=160)
    kickoff_at: datetime
    season: int = Field(ge=1900, le=2200)
    week: int = Field(ge=0, le=30)
    status: GameStatus
    home_team: ImportTeam
    away_team: ImportTeam
    source_urls: list[HttpUrl] = Field(min_length=1)

    @field_validator("kickoff_at")
    @classmethod
    def utc_kickoff(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("kickoff_at requires a timezone")
        return value.astimezone(UTC)

    @model_validator(mode="after")
    def distinct_teams(self):
        if self.home_team.name == self.away_team.name:
            raise ValueError("A game must have two different teams")
        return self


class ImportPick(ManifestModel):
    key: str = Field(min_length=1, max_length=64)
    game_key: str = Field(min_length=1, max_length=160)
    player_name: str = Field(min_length=1, max_length=120)
    player_team: Literal["home", "away"]
    player_position: str = Field(min_length=1, max_length=16)
    original_text: str = Field(min_length=1, max_length=2000)
    description: str = Field(min_length=1, max_length=1000)
    market_type: Literal["player_rushing_yards", "player_passing_yards", "player_receiving_yards"]
    side: Literal["over", "under"]
    line_value: Decimal = Field(ge=0, max_digits=10, decimal_places=3)
    american_odds: int | None = None
    decimal_odds: Decimal | None = Field(default=None, gt=1, max_digits=10, decimal_places=5)
    stake_units: Decimal = Field(default=Decimal("1"), gt=0, max_digits=10, decimal_places=3)
    source_urls: list[HttpUrl] = Field(min_length=1)

    @model_validator(mode="after")
    def consistent_prices(self):
        if self.american_odds == 0:
            raise ValueError("American odds cannot be zero")
        if self.american_odds is not None:
            converted = american_to_decimal(self.american_odds).quantize(Decimal("0.00001"))
            if self.decimal_odds is not None and abs(self.decimal_odds - converted) > Decimal("0.00001"):
                raise ValueError("Supplied American and decimal odds disagree")
        return self

    @property
    def canonical_odds(self) -> Decimal | None:
        if self.decimal_odds is not None:
            return self.decimal_odds
        if self.american_odds is not None:
            return american_to_decimal(self.american_odds).quantize(Decimal("0.00001"))
        return None


class PickImportManifest(ManifestModel):
    batch_key: str = Field(min_length=1, max_length=63)
    user: str = Field(min_length=1, max_length=32, pattern=r"^[a-zA-Z0-9_-]+$")
    source_file: str = Field(min_length=1, max_length=200)
    pick_date: date
    games: list[ImportGame] = Field(min_length=1)
    picks: list[ImportPick] = Field(min_length=1)

    @model_validator(mode="after")
    def unique_keys(self):
        game_keys = {game.key for game in self.games}
        if len(game_keys) != len(self.games):
            raise ValueError("Duplicate game key")
        if len({pick.key for pick in self.picks}) != len(self.picks):
            raise ValueError("Duplicate pick key")
        if any(pick.game_key not in game_keys for pick in self.picks):
            raise ValueError("Each pick must reference a game in this manifest")
        return self


def _identity(manifest: PickImportManifest, item: ImportPick, game: ImportGame) -> dict:
    """Freeze imported facts; later event status changes do not change pick identity."""
    return {
        "batch_key": manifest.batch_key, "user": manifest.user,
        "source_file": manifest.source_file, "pick_date": manifest.pick_date.isoformat(),
        "pick": item.model_dump(mode="json"),
        "game": game.model_dump(mode="json", exclude={"status"}),
    }


def _fingerprint(identity: dict) -> str:
    return sha256(json.dumps(identity, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _utc(value: datetime) -> datetime:
    # SQLite returns naive datetimes in isolated tests; stored values are UTC.
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)


def _existing_game(session: Session, spec: ImportGame) -> Game | None:
    matches = [game for game in session.scalars(select(Game)).all()
               if game.external_ids.get("manual_import") == spec.key]
    if len(matches) > 1:
        raise ValueError(f"Ambiguous imported game: {spec.key}")
    if not matches:
        return None
    game = matches[0]
    home, away = session.get(Team, game.home_team_id), session.get(Team, game.away_team_id)
    if ("fixture" in game.external_ids or home is None or away is None
        or home.name != spec.home_team.name or away.name != spec.away_team.name
        or _utc(game.kickoff_at) != spec.kickoff_at or game.season != spec.season or game.week != spec.week):
        raise ValueError(f"Imported game identity changed: {spec.key}")
    return game


def _team(session: Session, spec: ImportTeam) -> Team:
    team = session.scalar(select(Team).where(Team.name == spec.name))
    if team is not None:
        return team
    collision = session.scalar(select(Team).where(Team.abbreviation == spec.abbreviation))
    if collision is not None:
        raise ValueError(f"Team abbreviation already belongs to another team: {spec.abbreviation}")
    team = Team(external_ids={}, **spec.model_dump())
    session.add(team)
    session.flush()
    return team


def _game(session: Session, spec: ImportGame) -> Game:
    game = _existing_game(session, spec)
    if game is not None:
        return game
    home, away = _team(session, spec.home_team), _team(session, spec.away_team)
    game = Game(external_ids={"manual_import": spec.key}, season=spec.season, week=spec.week,
                kickoff_at=spec.kickoff_at, home_team_id=home.id, away_team_id=away.id, status=spec.status)
    session.add(game)
    session.flush()
    return game


def _selection(session: Session, game: Game, item: ImportPick) -> tuple[Market, Selection]:
    team_id = game.home_team_id if item.player_team == "home" else game.away_team_id
    # A synthetic fixture player must never establish real-world provenance.
    players = [player for player in session.scalars(select(Player).where(
        Player.name == item.player_name, Player.team_id == team_id)).all()
        if "fixture" not in player.external_ids]
    if len(players) > 1:
        raise ValueError(f"Ambiguous player: {item.player_name}")
    player = players[0] if players else None
    if player is None:
        player = Player(external_ids={"manual_import": item.player_name}, name=item.player_name,
                        team_id=team_id, position=item.player_position)
        session.add(player)
        session.flush()
    markets = list(session.scalars(select(Market).where(
        Market.game_id == game.id, Market.market_type == item.market_type,
        Market.player_id == player.id, Market.team_id == team_id, Market.period == "game")))
    if len(markets) > 1:
        raise ValueError(f"Ambiguous imported market: {item.player_name}")
    market = markets[0] if markets else None
    if market is None:
        # Supplied picks are not a current available line; keep Track disabled.
        market = Market(game_id=game.id, market_type=item.market_type, period="game",
                        player_id=player.id, team_id=team_id, status="closed")
        session.add(market)
        session.flush()
    selection = session.scalar(select(Selection).where(
        Selection.market_id == market.id, Selection.selection_key == item.side))
    if selection is None:
        selection = Selection(market_id=market.id, selection_key=item.side,
                              side=item.side, player_id=player.id, team_id=team_id)
        session.add(selection)
        session.flush()
    return market, selection


def import_pick_manifest(session: Session, manifest: PickImportManifest, *, apply: bool = False) -> dict:
    """Read-only plan by default; apply commits all new picks in one transaction.

    Call with a dedicated clean session. Repeating the same import keeps results,
    taken prices and timestamps. Changed identity or terms fail without rewriting.
    """
    if session.new or session.dirty or session.deleted:
        raise ValueError("Use a clean session for a pick import")
    report = {"batch_key": manifest.batch_key, "user": manifest.user, "applied": apply,
              "created": [], "existing": [], "would_create": []}
    try:
        with session.no_autoflush:
            user = session.scalar(select(User).where(User.username == manifest.user))
            if user is None or not user.active:
                raise ValueError("Import owner must be an existing active user")
            games = {game.key: game for game in manifest.games}
            for spec in manifest.games:
                _existing_game(session, spec)
            pending = []
            for item in manifest.picks:
                import_key = f"{manifest.batch_key}:{item.key}"
                identity = _identity(manifest, item, games[item.game_key])
                fingerprint = _fingerprint(identity)
                existing = session.scalar(select(Pick).where(Pick.user_id == user.id, Pick.import_key == import_key))
                if existing is not None:
                    if ((existing.import_metadata or {}).get("fingerprint") != fingerprint
                        or existing.line_value != item.line_value
                        or existing.american_odds != item.american_odds
                        or existing.decimal_odds != item.canonical_odds
                        or existing.stake_units != item.stake_units):
                        raise ValueError(f"Existing imported pick has different identity or terms: {import_key}")
                    actual_game = session.get(Game, existing.game_id)
                    actual_selection = session.get(Selection, existing.selection_id)
                    actual_market = session.get(Market, existing.market_id)
                    actual_player = session.get(Player, actual_market.player_id) if actual_market and actual_market.player_id else None
                    expected_team_id = (actual_game.home_team_id if item.player_team == "home" else actual_game.away_team_id) if actual_game else None
                    if (actual_game is None or actual_game.external_ids.get("manual_import") != item.game_key
                        or actual_selection is None or actual_selection.market_id != existing.market_id
                        or actual_selection.side != item.side or actual_market is None
                        or actual_market.game_id != existing.game_id or actual_market.market_type != item.market_type
                        or actual_player is None or actual_player.name != item.player_name
                        or actual_player.team_id != expected_team_id or actual_market.team_id != expected_team_id
                        or actual_selection.player_id != actual_player.id or actual_selection.team_id != expected_team_id):
                        raise ValueError(f"Existing imported pick references changed: {import_key}")
                    report["existing"].append({"import_key": import_key, "pick_id": existing.id})
                else:
                    pending.append((item, import_key, identity, fingerprint))
                    report["would_create"].append(import_key)
        if not apply:
            return report
        for item, import_key, identity, fingerprint in pending:
            game = _game(session, games[item.game_key])
            market, selection = _selection(session, game, item)
            pick = Pick(user_id=user.id, game_id=game.id, market_id=market.id, selection_id=selection.id,
                        picked_at=datetime.now(UTC), line_value=item.line_value,
                        american_odds=item.american_odds, decimal_odds=item.canonical_odds,
                        stake_units=item.stake_units, result="pending", profit_units=None,
                        notes=item.description, import_key=import_key,
                        import_metadata={**identity, "fingerprint": fingerprint,
                                         "stake_defaulted": "stake_units" not in item.model_fields_set,
                                         "imported_at": datetime.now(UTC).isoformat()})
            session.add(pick)
            session.flush()
            report["created"].append({"import_key": import_key, "pick_id": pick.id})
        session.commit()
        return report
    except Exception:
        if apply:
            session.rollback()
        raise
