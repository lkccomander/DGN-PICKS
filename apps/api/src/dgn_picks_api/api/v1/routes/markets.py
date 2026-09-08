from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from dgn_picks_api.api.v1.dependencies import get_db
from dgn_picks_api.api.v1.schemas import OddsSnapshotResponse
from dgn_picks_api.domains.markets.models import Market, Selection
from dgn_picks_api.domains.odds.models import OddsSnapshot

router = APIRouter(prefix="/markets", tags=["markets"])


@router.get("/{market_id}/history", response_model=list[OddsSnapshotResponse])
def market_history(market_id: int, db: Session = Depends(get_db)) -> list[OddsSnapshot]:
    market_exists = db.scalars(select(Market.id).where(Market.id == market_id)).one_or_none()
    if market_exists is None:
        raise HTTPException(status_code=404, detail="Market not found")
    statement = (
        select(OddsSnapshot)
        .join(Selection, OddsSnapshot.selection_id == Selection.id)
        .where(Selection.market_id == market_id)
        .order_by(OddsSnapshot.observed_at, OddsSnapshot.id)
    )
    return list(db.scalars(statement).all())
