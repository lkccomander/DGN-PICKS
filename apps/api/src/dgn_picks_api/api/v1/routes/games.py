from datetime import UTC, date, datetime, time, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from dgn_picks_api.api.v1.dependencies import get_db
from dgn_picks_api.api.v1.schemas import GameResponse, MarketResponse
from dgn_picks_api.domains.games.models import Game
from dgn_picks_api.domains.markets.models import Market
from dgn_picks_api.domains.teams.models import Team

router = APIRouter(prefix="/games", tags=["games"])


@router.get("", response_model=list[GameResponse])
def list_games(
    game_date: date | None = Query(default=None, alias="date"),
    conference: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[Game]:
    statement = select(Game)
    if game_date is not None:
        start = datetime.combine(game_date, time.min, tzinfo=UTC)
        statement = statement.where(Game.kickoff_at >= start, Game.kickoff_at < start + timedelta(days=1))
    if conference is not None:
        home_team = Team.__table__.alias("home_team")
        away_team = Team.__table__.alias("away_team")
        statement = (
            statement.join(home_team, Game.home_team_id == home_team.c.id)
            .join(away_team, Game.away_team_id == away_team.c.id)
            .where(or_(home_team.c.conference == conference, away_team.c.conference == conference))
        )
    statement = statement.order_by(Game.kickoff_at, Game.id)
    return list(db.scalars(statement).all())


@router.get("/{game_id}", response_model=GameResponse)
def get_game(game_id: int, db: Session = Depends(get_db)) -> Game:
    game = db.scalars(select(Game).where(Game.id == game_id)).one_or_none()
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")
    return game


@router.get("/{game_id}/markets", response_model=list[MarketResponse])
def list_game_markets(game_id: int, db: Session = Depends(get_db)) -> list[Market]:
    game_exists = db.scalars(select(Game.id).where(Game.id == game_id)).one_or_none()
    if game_exists is None:
        raise HTTPException(status_code=404, detail="Game not found")
    statement = (
        select(Market)
        .where(Market.game_id == game_id)
        .options(selectinload(Market.selections))
        .order_by(Market.market_type, Market.period, Market.id)
    )
    return list(db.scalars(statement).all())
