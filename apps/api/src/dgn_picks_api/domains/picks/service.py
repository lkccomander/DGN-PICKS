from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from dgn_picks_api.api.v1.schemas import PickCreate
from dgn_picks_api.domains.markets.models import Market, Selection
from dgn_picks_api.domains.odds.models import OddsSnapshot
from dgn_picks_api.domains.picks.models import Pick
from dgn_picks_api.domains.picks.calculations import profit_units
from dgn_picks_api.domains.common.enums import PickResult
from dgn_picks_api.domains.users.models import User


def create_pick(session: Session, payload: PickCreate) -> Pick:
    """Validate and persist one single-leg pick at the current market price."""
    user = session.scalars(select(User).where(User.username == payload.user)).one_or_none()
    if user is None:
        raise ValueError("Unknown user")

    market = session.scalars(select(Market).where(Market.id == payload.market_id)).one_or_none()
    if market is None:
        raise ValueError("Unknown market")
    if market.game_id != payload.game_id:
        raise ValueError("Market does not belong to game")

    if payload.selection_id is None:
        raise ValueError("A resolved selection is required")
    selection = session.scalars(
        select(Selection).where(Selection.id == payload.selection_id)
    ).one_or_none()
    if selection is None:
        raise ValueError("Unknown selection")
    if selection.market_id != market.id:
        raise ValueError("Selection does not belong to market")
    if selection.side is None:
        raise ValueError("Selection is unresolved")

    snapshot = session.scalars(
        select(OddsSnapshot)
        .where(OddsSnapshot.selection_id == selection.id)
        .order_by(OddsSnapshot.observed_at.desc(), OddsSnapshot.id.desc())
        .limit(1)
    ).first()

    pick = Pick(
        user_id=user.id,
        game_id=payload.game_id,
        market_id=market.id,
        selection_id=selection.id,
        line_value=snapshot.line_value if snapshot else None,
        american_odds=snapshot.american_odds if snapshot else None,
        decimal_odds=snapshot.decimal_odds if snapshot else None,
        stake_units=payload.stake_units,
        notes=payload.notes,
    )
    session.add(pick)
    session.commit()
    session.refresh(pick)
    return pick


def grade_pick(session: Session, pick_id: int, result: PickResult) -> Pick:
    pick = session.get(Pick, pick_id)
    if pick is None:
        raise ValueError("Unknown pick")
    current_result = PickResult(pick.result)
    if current_result is not PickResult.PENDING:
        raise ValueError("Pick is already graded")
    pick.result = result
    pick.profit_units = profit_units(pick.stake_units, pick.decimal_odds, result)
    session.commit()
    session.refresh(pick)
    return pick
