from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from dgn_picks_api.api.v1.dependencies import get_db, require_development_write_access
from dgn_picks_api.api.v1.schemas import (
    MarketCreate,
    MarketResponse,
    MarketUpdate,
    OddsSnapshotResponse,
    SelectionCreate,
    SelectionResponse,
    SelectionUpdate,
)
from dgn_picks_api.domains.games.models import Game
from dgn_picks_api.domains.markets.models import Market, Selection
from dgn_picks_api.domains.odds.models import OddsSnapshot
from dgn_picks_api.domains.picks.models import Pick, PickLeg
from dgn_picks_api.domains.teams.models import Player, Team

router = APIRouter(prefix="/markets", tags=["markets"])
selections_router = APIRouter(prefix="/selections", tags=["selections"])


def _commit_or_conflict(db: Session, message: str) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=message) from exc


def _validate_market_refs(payload: MarketCreate | MarketUpdate, db: Session, game_id: int | None = None) -> None:
    values = payload.model_dump(exclude_unset=True)
    if game_id is not None and db.get(Game, game_id) is None:
        raise HTTPException(status_code=422, detail="Game not found")
    if "game_id" in values and db.get(Game, values["game_id"]) is None:
        raise HTTPException(status_code=422, detail="Game not found")
    if "team_id" in values and values["team_id"] is not None and db.get(Team, values["team_id"]) is None:
        raise HTTPException(status_code=422, detail="Team not found")
    if "player_id" in values and values["player_id"] is not None and db.get(Player, values["player_id"]) is None:
        raise HTTPException(status_code=422, detail="Player not found")


@router.get("", response_model=list[MarketResponse])
def list_markets(game_id: int | None = None, status_filter: str | None = None, db: Session = Depends(get_db)) -> list[Market]:
    statement = select(Market).order_by(Market.game_id, Market.market_type, Market.period, Market.id)
    if game_id is not None:
        statement = statement.where(Market.game_id == game_id)
    if status_filter is not None:
        statement = statement.where(Market.status == status_filter)
    return list(db.scalars(statement).all())


@router.get("/{market_id}", response_model=MarketResponse)
def get_market(market_id: int, db: Session = Depends(get_db)) -> Market:
    market = db.get(Market, market_id)
    if market is None:
        raise HTTPException(status_code=404, detail="Market not found")
    return market


@router.post("", response_model=MarketResponse, status_code=status.HTTP_201_CREATED,
            dependencies=[Depends(require_development_write_access)])
def create_market(payload: MarketCreate, db: Session = Depends(get_db)) -> Market:
    _validate_market_refs(payload, db)
    market = Market(**payload.model_dump())
    db.add(market)
    _commit_or_conflict(db, "Market cannot be created")
    db.refresh(market)
    return market


@router.patch("/{market_id}", response_model=MarketResponse,
             dependencies=[Depends(require_development_write_access)])
def update_market(market_id: int, payload: MarketUpdate, db: Session = Depends(get_db)) -> Market:
    market = db.get(Market, market_id)
    if market is None:
        raise HTTPException(status_code=404, detail="Market not found")
    _validate_market_refs(payload, db, market.game_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(market, field, value)
    _commit_or_conflict(db, "Market cannot be updated")
    db.refresh(market)
    return market


@router.delete("/{market_id}", status_code=status.HTTP_204_NO_CONTENT,
              dependencies=[Depends(require_development_write_access)])
def delete_market(market_id: int, db: Session = Depends(get_db)) -> None:
    market = db.get(Market, market_id)
    if market is None:
        raise HTTPException(status_code=404, detail="Market not found")
    if db.scalar(select(Pick.id).where(Pick.market_id == market_id).limit(1)) is not None:
        raise HTTPException(status_code=409, detail="Market has picks; close it instead")
    if db.scalar(select(Selection.id).where(Selection.market_id == market_id).limit(1)) is not None:
        raise HTTPException(status_code=409, detail="Market has selections; remove them first")
    db.delete(market)
    _commit_or_conflict(db, "Market cannot be deleted")


@router.post("/{market_id}/selections", response_model=SelectionResponse,
            status_code=status.HTTP_201_CREATED,
            dependencies=[Depends(require_development_write_access)])
def create_selection(market_id: int, payload: SelectionCreate, db: Session = Depends(get_db)) -> Selection:
    if payload.market_id != market_id:
        raise HTTPException(status_code=422, detail="Market path and payload must match")
    if db.get(Market, market_id) is None:
        raise HTTPException(status_code=422, detail="Market not found")
    if payload.team_id is not None and db.get(Team, payload.team_id) is None:
        raise HTTPException(status_code=422, detail="Team not found")
    if payload.player_id is not None and db.get(Player, payload.player_id) is None:
        raise HTTPException(status_code=422, detail="Player not found")
    selection = Selection(**payload.model_dump())
    db.add(selection)
    _commit_or_conflict(db, "Selection key already exists for this market")
    db.refresh(selection)
    return selection


@selections_router.get("/{selection_id}", response_model=SelectionResponse)
def get_selection(selection_id: int, db: Session = Depends(get_db)) -> Selection:
    selection = db.get(Selection, selection_id)
    if selection is None:
        raise HTTPException(status_code=404, detail="Selection not found")
    return selection


@selections_router.patch("/{selection_id}", response_model=SelectionResponse,
                        dependencies=[Depends(require_development_write_access)])
def update_selection(selection_id: int, payload: SelectionUpdate, db: Session = Depends(get_db)) -> Selection:
    selection = db.get(Selection, selection_id)
    if selection is None:
        raise HTTPException(status_code=404, detail="Selection not found")
    if payload.team_id is not None and db.get(Team, payload.team_id) is None:
        raise HTTPException(status_code=422, detail="Team not found")
    if payload.player_id is not None and db.get(Player, payload.player_id) is None:
        raise HTTPException(status_code=422, detail="Player not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(selection, field, value)
    _commit_or_conflict(db, "Selection key already exists for this market")
    db.refresh(selection)
    return selection


@selections_router.delete("/{selection_id}", status_code=status.HTTP_204_NO_CONTENT,
                         dependencies=[Depends(require_development_write_access)])
def delete_selection(selection_id: int, db: Session = Depends(get_db)) -> None:
    selection = db.get(Selection, selection_id)
    if selection is None:
        raise HTTPException(status_code=404, detail="Selection not found")
    if db.scalar(select(Pick.id).where(Pick.selection_id == selection_id).limit(1)) is not None or db.scalar(select(PickLeg.id).where(PickLeg.selection_id == selection_id).limit(1)) is not None:
        raise HTTPException(status_code=409, detail="Selection has picks; it cannot be deleted")
    if db.scalar(select(OddsSnapshot.id).where(OddsSnapshot.selection_id == selection_id).limit(1)) is not None:
        raise HTTPException(status_code=409, detail="Selection has odds history; it cannot be deleted")
    db.delete(selection)
    _commit_or_conflict(db, "Selection cannot be deleted")


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
