from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from dgn_picks_api.api.v1.dependencies import get_db, require_authenticated_write_access
from dgn_picks_api.api.v1.schemas import (
    PlayerCreate,
    PlayerResponse,
    PlayerUpdate,
    TeamCreate,
    TeamResponse,
    TeamUpdate,
)
from dgn_picks_api.domains.games.models import Game
from dgn_picks_api.domains.markets.models import Market, Selection
from dgn_picks_api.domains.teams.models import Player, Team

router = APIRouter(prefix="/teams", tags=["teams"])
players_router = APIRouter(prefix="/players", tags=["players"])


def _commit_or_conflict(db: Session, message: str) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=message) from exc


@router.get("", response_model=list[TeamResponse])
def list_teams(
    conference: str | None = Query(default=None),
    active: bool | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[Team]:
    statement = select(Team).order_by(Team.name, Team.id)
    if conference is not None:
        statement = statement.where(Team.conference == conference)
    if active is not None:
        statement = statement.where(Team.active == active)
    return list(db.scalars(statement).all())


@router.get("/{team_id}", response_model=TeamResponse)
def get_team(team_id: int, db: Session = Depends(get_db)) -> Team:
    team = db.get(Team, team_id)
    if team is None:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@router.post("", response_model=TeamResponse, status_code=status.HTTP_201_CREATED,
            dependencies=[Depends(require_authenticated_write_access)])
def create_team(payload: TeamCreate, db: Session = Depends(get_db)) -> Team:
    team = Team(**payload.model_dump())
    db.add(team)
    _commit_or_conflict(db, "Team name or abbreviation already exists")
    db.refresh(team)
    return team


@router.patch("/{team_id}", response_model=TeamResponse,
             dependencies=[Depends(require_authenticated_write_access)])
def update_team(team_id: int, payload: TeamUpdate, db: Session = Depends(get_db)) -> Team:
    team = db.get(Team, team_id)
    if team is None:
        raise HTTPException(status_code=404, detail="Team not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(team, field, value)
    _commit_or_conflict(db, "Team name or abbreviation already exists")
    db.refresh(team)
    return team


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT,
              dependencies=[Depends(require_authenticated_write_access)])
def delete_team(team_id: int, db: Session = Depends(get_db)) -> None:
    team = db.get(Team, team_id)
    if team is None:
        raise HTTPException(status_code=404, detail="Team not found")
    if db.scalar(select(Player.id).where(Player.team_id == team_id).limit(1)) is not None:
        raise HTTPException(status_code=409, detail="Team has players; deactivate instead")
    if db.scalar(select(Game.id).where((Game.home_team_id == team_id) | (Game.away_team_id == team_id)).limit(1)) is not None:
        raise HTTPException(status_code=409, detail="Team has games; deactivate instead")
    db.delete(team)
    _commit_or_conflict(db, "Team cannot be deleted")


@players_router.get("", response_model=list[PlayerResponse])
def list_players(team_id: int | None = Query(default=None), active: bool | None = Query(default=None), db: Session = Depends(get_db)) -> list[Player]:
    statement = select(Player).order_by(Player.name, Player.id)
    if team_id is not None:
        statement = statement.where(Player.team_id == team_id)
    if active is not None:
        statement = statement.where(Player.active == active)
    return list(db.scalars(statement).all())


@players_router.get("/{player_id}", response_model=PlayerResponse)
def get_player(player_id: int, db: Session = Depends(get_db)) -> Player:
    player = db.get(Player, player_id)
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return player


def _require_team(team_id: int, db: Session) -> None:
    if db.get(Team, team_id) is None:
        raise HTTPException(status_code=422, detail="Team not found")


@players_router.post("", response_model=PlayerResponse, status_code=status.HTTP_201_CREATED,
                    dependencies=[Depends(require_authenticated_write_access)])
def create_player(payload: PlayerCreate, db: Session = Depends(get_db)) -> Player:
    _require_team(payload.team_id, db)
    player = Player(**payload.model_dump())
    db.add(player)
    _commit_or_conflict(db, "Player cannot be created")
    db.refresh(player)
    return player


@players_router.patch("/{player_id}", response_model=PlayerResponse,
                     dependencies=[Depends(require_authenticated_write_access)])
def update_player(player_id: int, payload: PlayerUpdate, db: Session = Depends(get_db)) -> Player:
    player = db.get(Player, player_id)
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    values = payload.model_dump(exclude_unset=True)
    if "team_id" in values:
        _require_team(values["team_id"], db)
    for field, value in values.items():
        setattr(player, field, value)
    _commit_or_conflict(db, "Player cannot be updated")
    db.refresh(player)
    return player


@players_router.delete("/{player_id}", status_code=status.HTTP_204_NO_CONTENT,
                      dependencies=[Depends(require_authenticated_write_access)])
def delete_player(player_id: int, db: Session = Depends(get_db)) -> None:
    player = db.get(Player, player_id)
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    if db.scalar(select(Market.id).where(Market.player_id == player_id).limit(1)) is not None or db.scalar(select(Selection.id).where(Selection.player_id == player_id).limit(1)) is not None:
        raise HTTPException(status_code=409, detail="Player is referenced by markets; deactivate instead")
    db.delete(player)
    _commit_or_conflict(db, "Player cannot be deleted")
