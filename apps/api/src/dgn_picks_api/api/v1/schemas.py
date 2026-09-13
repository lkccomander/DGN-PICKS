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


class UserCreate(BaseModel):
    username: str = Field(min_length=1, max_length=32)
    display_name: str = Field(min_length=1, max_length=80)
    active: bool = True


class UserUpdate(BaseModel):
    display_name: str | None = Field(default=None, min_length=1, max_length=80)
    active: bool | None = None


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=256)


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    role: str


class TeamResponse(ORMModel):
    id: int
    external_ids: dict = Field(default_factory=dict)
    name: str
    short_name: str
    abbreviation: str
    conference: str
    logo_url: str | None = None
    active: bool


class TeamCreate(BaseModel):
    external_ids: dict = Field(default_factory=dict)
    name: str = Field(min_length=1, max_length=120)
    short_name: str = Field(min_length=1, max_length=80)
    abbreviation: str = Field(min_length=1, max_length=8)
    conference: str = Field(min_length=1, max_length=64)
    logo_url: str | None = Field(default=None, max_length=500)
    active: bool = True


class TeamUpdate(BaseModel):
    external_ids: dict | None = None
    name: str | None = Field(default=None, min_length=1, max_length=120)
    short_name: str | None = Field(default=None, min_length=1, max_length=80)
    abbreviation: str | None = Field(default=None, min_length=1, max_length=8)
    conference: str | None = Field(default=None, min_length=1, max_length=64)
    logo_url: str | None = Field(default=None, max_length=500)
    active: bool | None = None


class PlayerResponse(ORMModel):
    id: int
    external_ids: dict = Field(default_factory=dict)
    team_id: int
    name: str
    position: str
    active: bool


class PlayerCreate(BaseModel):
    external_ids: dict = Field(default_factory=dict)
    team_id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=120)
    position: str = Field(min_length=1, max_length=16)
    active: bool = True


class PlayerUpdate(BaseModel):
    external_ids: dict | None = None
    team_id: int | None = Field(default=None, gt=0)
    name: str | None = Field(default=None, min_length=1, max_length=120)
    position: str | None = Field(default=None, min_length=1, max_length=16)
    active: bool | None = None


class GameResponse(ORMModel):
    id: int
    external_ids: dict = Field(default_factory=dict)
    season: int
    week: int
    kickoff_at: datetime
    home_team_id: int
    away_team_id: int
    venue: str | None = None
    status: GameStatus
    home_score: int | None = None
    away_score: int | None = None


class GameCreate(BaseModel):
    external_ids: dict = Field(default_factory=dict)
    season: int = Field(gt=0)
    week: int = Field(gt=0)
    kickoff_at: datetime
    home_team_id: int = Field(gt=0)
    away_team_id: int = Field(gt=0)
    venue: str | None = Field(default=None, max_length=160)
    status: GameStatus = GameStatus.SCHEDULED
    home_score: int | None = Field(default=None, ge=0)
    away_score: int | None = Field(default=None, ge=0)


class GameUpdate(BaseModel):
    external_ids: dict | None = None
    season: int | None = Field(default=None, gt=0)
    week: int | None = Field(default=None, gt=0)
    kickoff_at: datetime | None = None
    home_team_id: int | None = Field(default=None, gt=0)
    away_team_id: int | None = Field(default=None, gt=0)
    venue: str | None = Field(default=None, max_length=160)
    status: GameStatus | None = None
    home_score: int | None = Field(default=None, ge=0)
    away_score: int | None = Field(default=None, ge=0)


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


class OddsSnapshotCreate(BaseModel):
    selection_id: int = Field(gt=0)
    sportsbook_id: int = Field(gt=0)
    observed_at: datetime
    line_value: Decimal | None = None
    american_odds: int | None = None
    decimal_odds: Decimal = Field(gt=1)
    implied_probability: Decimal | None = Field(default=None, gt=0, le=1)
    source_event_id: str | None = Field(default=None, max_length=160)


class MarketResponse(ORMModel):
    id: int
    game_id: int
    market_type: str
    period: str
    player_id: int | None = None
    team_id: int | None = None
    status: MarketStatus
    selections: list[SelectionResponse] = Field(default_factory=list)


class MarketCreate(BaseModel):
    game_id: int = Field(gt=0)
    market_type: str = Field(min_length=1, max_length=48)
    period: str = Field(default="game", min_length=1, max_length=24)
    player_id: int | None = Field(default=None, gt=0)
    team_id: int | None = Field(default=None, gt=0)
    status: MarketStatus = MarketStatus.OPEN


class MarketUpdate(BaseModel):
    market_type: str | None = Field(default=None, min_length=1, max_length=48)
    period: str | None = Field(default=None, min_length=1, max_length=24)
    player_id: int | None = Field(default=None, gt=0)
    team_id: int | None = Field(default=None, gt=0)
    status: MarketStatus | None = None


class SelectionCreate(BaseModel):
    market_id: int = Field(gt=0)
    selection_key: str = Field(min_length=1, max_length=80)
    team_id: int | None = Field(default=None, gt=0)
    player_id: int | None = Field(default=None, gt=0)
    side: str | None = Field(default=None, max_length=16)


class SelectionUpdate(BaseModel):
    selection_key: str | None = Field(default=None, min_length=1, max_length=80)
    team_id: int | None = Field(default=None, gt=0)
    player_id: int | None = Field(default=None, gt=0)
    side: str | None = Field(default=None, max_length=16)


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


class PickGrade(BaseModel):
    result: PickResult


class PickUpdate(BaseModel):
    user: str = Field(min_length=1, max_length=32)
    stake_units: Decimal | None = Field(default=None, gt=0)
    notes: str | None = Field(default=None, max_length=1000)


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


class SeedPickDefinitionResponse(BaseModel):
    number: int
    description: str
    market_type: str
    line_value: Decimal
    side: str | None = None
    team_or_player: str
    state: str
