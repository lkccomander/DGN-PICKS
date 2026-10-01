from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException

from dgn_picks_api.api.v1.dependencies import get_db, require_editor_identity
from dgn_picks_api.api.v1.schemas import BalanceAdjustmentCreate, BalanceTransactionResponse
from dgn_picks_api.domains.balances.models import BalanceTransaction
from dgn_picks_api.domains.users.models import User

admin_router = APIRouter(prefix="/admin/balances", tags=["admin-balances"], dependencies=[Depends(require_editor_identity)])


def _response(transaction: BalanceTransaction, username: str | None) -> BalanceTransactionResponse:
    return BalanceTransactionResponse(id=transaction.id, user_id=transaction.user_id, username=username,
                                      amount=transaction.amount, kind=transaction.kind, reason=transaction.reason,
                                      created_at=transaction.created_at, created_by=transaction.created_by)


@admin_router.get("", response_model=list[BalanceTransactionResponse])
def list_balance_history(db: Session = Depends(get_db)) -> list[BalanceTransactionResponse]:
    rows = db.execute(select(BalanceTransaction, User.username).join(User, User.id == BalanceTransaction.user_id).order_by(BalanceTransaction.created_at.desc())).all()
    return [_response(transaction, username) for transaction, username in rows]


@admin_router.post("/adjust", response_model=BalanceTransactionResponse, status_code=201)
def create_balance_adjustment(payload: BalanceAdjustmentCreate, identity: dict[str, str] = Depends(require_editor_identity), db: Session = Depends(get_db)) -> BalanceTransactionResponse:
    if db.get(User, payload.user_id) is None:
        raise HTTPException(status_code=404, detail="User not found")
    transaction = BalanceTransaction(user_id=payload.user_id, amount=payload.amount, kind="manual_adjustment",
                                     reason=payload.reason, created_by=int(identity["user_id"]) if "user_id" in identity else None)
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    username = db.scalar(select(User.username).where(User.id == payload.user_id))
    return _response(transaction, username)
