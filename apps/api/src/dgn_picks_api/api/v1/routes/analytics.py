from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from dgn_picks_api.api.v1.dependencies import get_db
from dgn_picks_api.api.v1.schemas import AnalyticsSummary
from dgn_picks_api.domains.common.enums import PickResult
from dgn_picks_api.domains.picks.calculations import profit_units, roi
from dgn_picks_api.domains.picks.models import Pick

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsSummary)
def get_summary(db: Session = Depends(get_db)) -> AnalyticsSummary:
    picks = db.scalars(select(Pick).order_by(Pick.id)).all()
    counts = {result: 0 for result in PickResult}
    total_units_risked = Decimal("0")
    total_profit_units = Decimal("0")

    for pick in picks:
        result = PickResult(pick.result)
        counts[result] += 1
        total_units_risked += pick.stake_units or Decimal("0")
        settled_profit = profit_units(pick.stake_units, pick.decimal_odds, result)
        if settled_profit is not None:
            total_profit_units += settled_profit

    return AnalyticsSummary(
        wins=counts[PickResult.WIN],
        losses=counts[PickResult.LOSS],
        pushes=counts[PickResult.PUSH],
        pending=counts[PickResult.PENDING],
        void=counts[PickResult.VOID],
        total_units_risked=total_units_risked,
        profit_units=total_profit_units,
        roi=roi(total_profit_units, total_units_risked),
    )
