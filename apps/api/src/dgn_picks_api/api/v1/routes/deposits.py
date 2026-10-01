from calendar import monthrange
from datetime import UTC, datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from dgn_picks_api.api.v1.dependencies import get_db, require_editor_identity, require_identity
from dgn_picks_api.api.v1.schemas import DepositCreate, DepositDecision, DepositResponse
from dgn_picks_api.domains.deposits.models import Deposit
from dgn_picks_api.domains.users.models import User

router = APIRouter(prefix="/deposits", tags=["deposits"])
admin_router = APIRouter(prefix="/admin/deposits", tags=["admin-deposits"], dependencies=[Depends(require_editor_identity)])


def _month_bounds() -> tuple[datetime, datetime]:
    now = datetime.now(UTC)
    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last = monthrange(now.year, now.month)[1]
    return start, start.replace(day=last, hour=23, minute=59, second=59, microsecond=999999)


def _response(deposit: Deposit, username: str | None = None) -> DepositResponse:
    return DepositResponse(id=deposit.id, user_id=deposit.user_id, username=username,
                           amount=deposit.amount, status=deposit.status,
                           created_at=deposit.created_at, reviewed_at=deposit.reviewed_at)


@router.post("", response_model=DepositResponse, status_code=201)
def create_deposit(payload: DepositCreate, identity: dict[str, str] = Depends(require_identity), db: Session = Depends(get_db)) -> DepositResponse:
    if "user_id" not in identity:
        raise HTTPException(status_code=400, detail="A registered user account is required")
    user_id = int(identity["user_id"])
    start, end = _month_bounds()
    used = db.scalar(select(func.coalesce(func.sum(Deposit.amount), 0)).where(
        Deposit.user_id == user_id, Deposit.status.in_(["pending", "approved"]),
        Deposit.created_at >= start, Deposit.created_at <= end,
    )) or Decimal("0")
    if used + payload.amount > Decimal("1000.00"):
        raise HTTPException(status_code=409, detail="Monthly deposit limit is USD 1,000.00")
    deposit = Deposit(user_id=user_id, amount=payload.amount, status="pending")
    db.add(deposit)
    db.commit()
    db.refresh(deposit)
    return _response(deposit, identity["username"])


@router.get("", response_model=list[DepositResponse])
def list_my_deposits(identity: dict[str, str] = Depends(require_identity), db: Session = Depends(get_db)) -> list[DepositResponse]:
    if "user_id" not in identity:
        return []
    rows = db.scalars(select(Deposit).where(Deposit.user_id == int(identity["user_id"])).order_by(Deposit.created_at.desc())).all()
    return [_response(row, identity["username"]) for row in rows]


@admin_router.get("/pending", response_model=list[DepositResponse])
def list_pending_deposits(db: Session = Depends(get_db)) -> list[DepositResponse]:
    rows = db.execute(select(Deposit, User.username).join(User, User.id == Deposit.user_id).where(Deposit.status == "pending").order_by(Deposit.created_at)).all()
    return [_response(deposit, username) for deposit, username in rows]


@admin_router.patch("/{deposit_id}", response_model=DepositResponse)
def decide_deposit(deposit_id: int, payload: DepositDecision, identity: dict[str, str] = Depends(require_editor_identity), db: Session = Depends(get_db)) -> DepositResponse:
    deposit = db.get(Deposit, deposit_id)
    if deposit is None:
        raise HTTPException(status_code=404, detail="Deposit not found")
    if deposit.status != "pending":
        raise HTTPException(status_code=409, detail="Deposit has already been reviewed")
    deposit.status = payload.status
    deposit.reviewed_at = datetime.now(UTC)
    deposit.reviewer_id = int(identity["user_id"]) if "user_id" in identity else None
    db.commit()
    db.refresh(deposit)
    username = db.scalar(select(User.username).where(User.id == deposit.user_id))
    return _response(deposit, username)
