from decimal import Decimal
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from dgn_picks_api.api.v1.dependencies import get_db
from dgn_picks_api.api.v1.schemas import AnalyticsSummary
from dgn_picks_api.domains.common.enums import PickResult
from dgn_picks_api.domains.picks.calculations import profit_units, roi
from dgn_picks_api.domains.picks.models import Pick
from dgn_picks_api.domains.users.models import User

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsSummary)
def get_summary(db: Session = Depends(get_db), user: str | None = None) -> AnalyticsSummary:
    statement = select(Pick).where(Pick.archived_at.is_(None))
    if user is not None:
        statement = statement.join(User, Pick.user_id == User.id).where(User.username == user)
    picks = db.scalars(statement.order_by(Pick.id)).all()
    counts = {result: 0 for result in PickResult}
    settled_stake = Decimal(0)
    pending_stake = Decimal(0)
    profit = Decimal(0)
    priced_count = 0
    unpriced_count = 0
    for pick in picks:
        result = PickResult(pick.result)
        counts[result] += 1
        if result is PickResult.PENDING:
            pending_stake += pick.stake_units
            continue
        value = profit_units(pick.stake_units, pick.decimal_odds, result)
        if value is None:
            unpriced_count += 1
            continue
        priced_count += 1
        settled_stake += pick.stake_units
        profit += value
    complete = priced_count > 0 and unpriced_count == 0
    return AnalyticsSummary(
        wins=counts[PickResult.WIN], losses=counts[PickResult.LOSS],
        pushes=counts[PickResult.PUSH], pending=counts[PickResult.PENDING], void=counts[PickResult.VOID],
        total_units_risked=settled_stake, pending_units=pending_stake,
        unpriced_settled_count=unpriced_count, profit_units=profit if complete else None,
        roi=roi(profit, settled_stake) if complete else None,
    )
