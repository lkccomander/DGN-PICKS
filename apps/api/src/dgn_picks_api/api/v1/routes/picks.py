from datetime import UTC, date, datetime, time, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from dgn_picks_api.api.v1.dependencies import get_db
from dgn_picks_api.api.v1.schemas import PickCreate, PickResponse
from dgn_picks_api.domains.picks.models import Pick
from dgn_picks_api.domains.picks.service import create_pick
from dgn_picks_api.domains.users.models import User

router = APIRouter(prefix="/picks", tags=["picks"])


@router.get("", response_model=list[PickResponse])
def list_picks(
    user: str | None = Query(default=None),
    pick_date: date | None = Query(default=None, alias="date"),
    db: Session = Depends(get_db),
) -> list[Pick]:
    statement = select(Pick)
    if user is not None:
        statement = statement.join(User, Pick.user_id == User.id).where(User.username == user)
    if pick_date is not None:
        start = datetime.combine(pick_date, time.min, tzinfo=UTC)
        statement = statement.where(Pick.picked_at >= start, Pick.picked_at < start + timedelta(days=1))
    statement = statement.order_by(Pick.picked_at, Pick.id)
    return list(db.scalars(statement).all())


@router.post("", response_model=PickResponse, status_code=status.HTTP_201_CREATED)
def post_pick(payload: PickCreate, db: Session = Depends(get_db)) -> Pick:
    try:
        return create_pick(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
