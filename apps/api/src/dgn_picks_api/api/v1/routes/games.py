from datetime import UTC, date, datetime, time, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from dgn_picks_api.api.v1.dependencies import get_db, require_authenticated_write_access
from dgn_picks_api.api.v1.schemas import GameCreate, GameResponse, GameUpdate, MarketResponse
from dgn_picks_api.domains.games.models import Game
from dgn_picks_api.domains.picks.models import Pick
from dgn_picks_api.domains.markets.models import Market
from dgn_picks_api.domains.teams.models import Team

router = APIRouter(prefix="/games", tags=["games"])


def _require_team(team_id: int, db: Session) -> None:
    if db.get(Team, team_id) is None:
        raise HTTPException(status_code=422, detail="Team not found")


def _validate_game_teams(home_team_id: int, away_team_id: int, db: Session) -> None:
    _require_team(home_team_id, db)
    _require_team(away_team_id, db)
    if home_team_id == away_team_id:
        raise HTTPException(status_code=422, detail="Home and away teams must differ")


def _commit_game(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Game cannot be saved") from exc


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


@router.post("", response_model=GameResponse, status_code=status.HTTP_201_CREATED,
            dependencies=[Depends(require_authenticated_write_access)])
def create_game(payload: GameCreate, db: Session = Depends(get_db)) -> Game:
    _validate_game_teams(payload.home_team_id, payload.away_team_id, db)
    game = Game(**payload.model_dump())
    db.add(game)
    _commit_game(db)
    db.refresh(game)
    return game


@router.get("/{game_id}", response_model=GameResponse)
def get_game(game_id: int, db: Session = Depends(get_db)) -> Game:
    game = db.scalars(select(Game).where(Game.id == game_id)).one_or_none()
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")
    return game


@router.patch("/{game_id}", response_model=GameResponse,
             dependencies=[Depends(require_authenticated_write_access)])
def update_game(game_id: int, payload: GameUpdate, db: Session = Depends(get_db)) -> Game:
    game = db.get(Game, game_id)
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")
    values = payload.model_dump(exclude_unset=True)
    home_team_id = values.get("home_team_id", game.home_team_id)
    away_team_id = values.get("away_team_id", game.away_team_id)
    _validate_game_teams(home_team_id, away_team_id, db)
    for field, value in values.items():
        setattr(game, field, value)
    _commit_game(db)
    db.refresh(game)
    return game


@router.delete("/{game_id}", status_code=status.HTTP_204_NO_CONTENT,
              dependencies=[Depends(require_authenticated_write_access)])
def delete_game(game_id: int, db: Session = Depends(get_db)) -> None:
    game = db.get(Game, game_id)
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")
    if db.scalar(select(Pick.id).where(Pick.game_id == game_id).limit(1)) is not None:
        raise HTTPException(status_code=409, detail="Game has picks; cancel or archive instead")
    if db.scalar(select(Market.id).where(Market.game_id == game_id).limit(1)) is not None:
        raise HTTPException(status_code=409, detail="Game has markets; remove them first")
    db.delete(game)
    _commit_game(db)


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
