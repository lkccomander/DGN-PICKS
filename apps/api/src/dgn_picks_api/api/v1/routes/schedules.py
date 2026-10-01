from datetime import UTC, date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from dgn_picks_api.api.v1.dependencies import get_db, require_editor_identity
from dgn_picks_api.domains.providers.mlb import MLBProviderError
from dgn_picks_api.domains.providers.mlb_ingestion import list_local_games, sync_mlb

router = APIRouter(prefix="/schedules", tags=["schedules"])


class ScheduleGameResponse(BaseModel):
    external_id: str
    sport: str
    league: str
    kickoff_at: str
    away_team: str
    home_team: str
    status: str
    away_score: int | None = None
    home_score: int | None = None


@router.get("/mlb", response_model=list[ScheduleGameResponse])
def mlb_schedule(game_date: date | None = Query(default=None, alias="date"), db: Session = Depends(get_db)) -> list[ScheduleGameResponse]:
    return [ScheduleGameResponse(**item) for item in list_local_games(db, game_date or datetime.now(UTC).date())]


@router.post("/admin/mlb/sync", dependencies=[Depends(require_editor_identity)])
def sync_mlb_schedule(
    game_date: date | None = Query(default=None, alias="date"),
    force: bool = Query(default=False),
    db: Session = Depends(get_db),
) -> dict:
    try:
        return sync_mlb(db, game_date or datetime.now(UTC).date(), force=force)
    except (MLBProviderError, ValueError, OSError) as exc:
        db.rollback()
        raise HTTPException(status_code=502, detail=f"MLB schedule sync failed: {exc}") from exc
