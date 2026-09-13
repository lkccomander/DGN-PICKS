from datetime import UTC, date, datetime, time, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.params import Query as QueryParam
from sqlalchemy import select
from sqlalchemy.orm import Session

from dgn_picks_api.api.v1.dependencies import get_db, require_authenticated_write_access
from dgn_picks_api.api.v1.schemas import PickCreate, PickGrade, PickResponse, PickUpdate
from dgn_picks_api.domains.picks.models import Pick
from dgn_picks_api.domains.picks.service import delete_pending_pick, create_pick, grade_pick, update_pending_pick
from dgn_picks_api.domains.users.models import User

router = APIRouter(prefix="/picks", tags=["picks"])


@router.get("", response_model=list[PickResponse])
def list_picks(
    user: str | None = Query(default=None),
    pick_date: date | None = Query(default=None, alias="date"),
    db: Session = Depends(get_db),
) -> list[Pick]:
    # Direct unit calls do not receive FastAPI's injected defaults.
    if isinstance(user, QueryParam):
        user = None
    if isinstance(pick_date, QueryParam):
        pick_date = None
    statement = select(Pick)
    if user is not None:
        statement = statement.join(User, Pick.user_id == User.id).where(User.username == user)
    if pick_date is not None:
        start = datetime.combine(pick_date, time.min, tzinfo=UTC)
        statement = statement.where(Pick.picked_at >= start, Pick.picked_at < start + timedelta(days=1))
    statement = statement.order_by(Pick.picked_at, Pick.id)
    return list(db.scalars(statement).all())


@router.post("", response_model=PickResponse, status_code=status.HTTP_201_CREATED,
            dependencies=[Depends(require_authenticated_write_access)])
def post_pick(payload: PickCreate, db: Session = Depends(get_db)) -> Pick:
    try:
        return create_pick(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/{pick_id}", response_model=PickResponse)
def get_pick(pick_id: int, db: Session = Depends(get_db)) -> Pick:
    pick = db.get(Pick, pick_id)
    if pick is None:
        raise HTTPException(status_code=404, detail="Pick not found")
    return pick


@router.patch("/{pick_id}", response_model=PickResponse,
             dependencies=[Depends(require_authenticated_write_access)])
def patch_pick(pick_id: int, payload: PickUpdate, db: Session = Depends(get_db)) -> Pick:
    try:
        return update_pending_pick(db, pick_id, payload)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if message == "Unknown pick" else 409
        raise HTTPException(status_code=status_code, detail=message) from exc


@router.delete("/{pick_id}", status_code=status.HTTP_204_NO_CONTENT,
              dependencies=[Depends(require_authenticated_write_access)])
def remove_pick(pick_id: int, user: str = Query(..., min_length=1, max_length=32), db: Session = Depends(get_db)) -> None:
    try:
        delete_pending_pick(db, pick_id, user)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if message == "Unknown pick" else 409
        raise HTTPException(status_code=status_code, detail=message) from exc


@router.patch("/{pick_id}/grade", response_model=PickResponse,
             dependencies=[Depends(require_authenticated_write_access)])
def patch_grade(pick_id: int, payload: PickGrade, db: Session = Depends(get_db)) -> Pick:
    try:
        return grade_pick(db, pick_id, payload.result)
    except ValueError as exc:
        status_code = 404 if str(exc) == "Unknown pick" else 409
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
