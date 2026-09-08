from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from dgn_picks_api.domains.common.enums import GameStatus, MarketStatus, PickResult


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserResponse(ORMModel):
    id: int
    username: str
    display_name: str
    active: bool
    created_at: datetime


class TeamResponse(ORMModel):
    id: int
    name: str
    short_name: str
    abbreviation: str
    conference: str
    logo_url: str | None = None
    active: bool


class GameResponse(ORMModel):
    id: int
    season: int
    week: int
    kickoff_at: datetime
    home_team_id: int
    away_team_id: int
    venue: str | None = None
    status: GameStatus
    home_score: int | None = None
    away_score: int | None = None


class SelectionResponse(ORMModel):
    id: int
    market_id: int
    selection_key: str
    team_id: int | None = None
    player_id: int | None = None
    side: str | None = None


class OddsSnapshotResponse(ORMModel):
    id: int
    selection_id: int
    sportsbook_id: int
    observed_at: datetime
    line_value: Decimal | None = None
    american_odds: int | None = None
    decimal_odds: Decimal
    implied_probability: Decimal | None = None
    source_event_id: str | None = None
    created_at: datetime


class MarketResponse(ORMModel):
    id: int
    game_id: int
    market_type: str
    period: str
    player_id: int | None = None
    team_id: int | None = None
    status: MarketStatus
    selections: list[SelectionResponse] = Field(default_factory=list)


class PickCreate(BaseModel):
    user: str = Field(min_length=1, max_length=32)
    game_id: int = Field(gt=0)
    market_id: int = Field(gt=0)
    selection_id: int | None = Field(default=None, gt=0)
    stake_units: Decimal = Field(gt=0)
    notes: str | None = Field(default=None, max_length=1000)


class PickResponse(ORMModel):
    id: int
    user_id: int
    game_id: int
    market_id: int
    selection_id: int | None = None
    picked_at: datetime
    line_value: Decimal | None = None
    american_odds: int | None = None
    decimal_odds: Decimal | None = None
    stake_units: Decimal
    result: PickResult
    profit_units: Decimal | None = None
    notes: str | None = None


class AnalyticsSummary(BaseModel):
    wins: int
    losses: int
    pushes: int
    pending: int
    void: int
    total_units_risked: Decimal
    profit_units: Decimal
    roi: Decimal | None


class SeedReportResponse(BaseModel):
    users_inserted: int
    users_existing: int
    games_inserted: int
    markets_inserted: int
    snapshots_inserted: int
    picks_inserted: int
    duplicate_snapshots: int
    unresolved_definitions: list[str]
    unresolved_count: int

