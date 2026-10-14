from calendar import monthrange
from datetime import UTC, datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from dgn_picks_api.api.v1.dependencies import get_db, require_editor_identity, require_identity
from dgn_picks_api.api.v1.schemas import DepositCreate, DepositDecision, DepositResponse
from dgn_picks_api.domains.deposits.models import Deposit
from dgn_picks_api.domains.balances.models import BalanceTransaction
from dgn_picks_api.domains.users.models import User

router = APIRouter(prefix="/deposits", tags=["virtual-credits"])
admin_router = APIRouter(prefix="/admin/deposits", tags=["admin-virtual-credits"], dependencies=[Depends(require_editor_identity)])


def _month_bounds() -> tuple[datetime, datetime]:
    now = datetime.now(UTC)
    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last = monthrange(now.year, now.month)[1]
    return start, start.replace(day=last, hour=23, minute=59, second=59, microsecond=999999)


def _response(deposit: Deposit, username: str | None = None) -> DepositResponse:
    return DepositResponse(id=deposit.id, user_id=deposit.user_id, username=username,
                           amount=deposit.amount, status=deposit.status,
                           created_at=deposit.created_at, reviewed_at=deposit.reviewed_at,
                           reviewer_id=deposit.reviewer_id)


@router.post("", response_model=DepositResponse, status_code=201, description="Request non-monetary, non-redeemable virtual credits. Legacy deposit path retained for compatibility.")
def create_deposit(payload: DepositCreate, identity: dict[str, str] = Depends(require_identity), db: Session = Depends(get_db)) -> DepositResponse:
    if "user_id" not in identity:
        raise HTTPException(status_code=400, detail="A registered user account is required")
    user_id = int(identity["user_id"])
    # Serialize requests for one owner before checking the monthly quota.
    db.scalar(select(User).where(User.id == user_id).with_for_update())
    start, end = _month_bounds()
    used = db.scalar(select(func.coalesce(func.sum(Deposit.amount), 0)).where(
        Deposit.user_id == user_id, Deposit.status.in_(["pending", "approved"]),
        Deposit.created_at >= start, Deposit.created_at <= end,
    )) or Decimal("0")
    if used + payload.amount > Decimal("1000.00"):
        raise HTTPException(status_code=409, detail="Monthly virtual-credit request limit is 1,000.00 credits")
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


@admin_router.get("", response_model=list[DepositResponse])
def list_all_deposits(db: Session = Depends(get_db)) -> list[DepositResponse]:
    rows = db.execute(select(Deposit, User.username).join(User, User.id == Deposit.user_id).order_by(Deposit.created_at.desc())).all()
    return [_response(deposit, username) for deposit, username in rows]


@admin_router.patch("/{deposit_id}", response_model=DepositResponse)
def decide_deposit(deposit_id: int, payload: DepositDecision, identity: dict[str, str] = Depends(require_editor_identity), db: Session = Depends(get_db)) -> DepositResponse:
    deposit = db.get(Deposit, deposit_id)
    if deposit is None:
        raise HTTPException(status_code=404, detail="Virtual-credit request not found")
    if deposit.status != "pending":
        raise HTTPException(status_code=409, detail="Virtual-credit request has already been reviewed")
    reviewer_id = int(identity["user_id"]) if "user_id" in identity else None
    # Claim the pending request atomically, so simultaneous reviews cannot credit it twice.
    reviewed = db.execute(update(Deposit).where(Deposit.id == deposit_id, Deposit.status == "pending").values(
        status=payload.status, reviewed_at=datetime.now(UTC), reviewer_id=reviewer_id,
    ))
    if reviewed.rowcount != 1:
        db.rollback()
        raise HTTPException(status_code=409, detail="Virtual-credit request has already been reviewed")
    if payload.status == "approved":
        db.add(BalanceTransaction(user_id=deposit.user_id, amount=deposit.amount, kind="virtual_credit",
                                  reason=f"Approved non-monetary virtual-credit request #{deposit.id}", created_by=reviewer_id))
    db.commit()
    db.refresh(deposit)
    username = db.scalar(select(User.username).where(User.id == deposit.user_id))
    return _response(deposit, username)
