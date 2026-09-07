from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Protocol

from dgn_picks_api.domains.common.enums import GameStatus


@dataclass(frozen=True)
class NormalizedGame:
    external_id: str
    season: int
    week: int
    kickoff_at: datetime
    away_team: str
    home_team: str
    conference: str
    status: GameStatus
    away_score: int | None = None
    home_score: int | None = None


@dataclass(frozen=True)
class NormalizedSnapshot:
    observed_at: datetime
    line_value: Decimal | None
    american_odds: int
    decimal_odds: Decimal
    source_event_id: str


@dataclass(frozen=True)
class NormalizedMarket:
    external_id: str
    market_type: str
    selection_key: str
    side: str | None
    team: str | None
    player: str | None
    snapshots: tuple[NormalizedSnapshot, ...]


class Provider(Protocol):
    def list_games(self, date_range: tuple[datetime, datetime]) -> list[NormalizedGame]: ...
    def get_game(self, external_game_id: str) -> NormalizedGame: ...
    def list_markets(self, external_game_id: str) -> list[NormalizedMarket]: ...
    def list_props(self, external_game_id: str) -> list[NormalizedMarket]: ...
