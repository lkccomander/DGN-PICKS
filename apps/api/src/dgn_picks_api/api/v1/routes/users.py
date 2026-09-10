from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from sqlalchemy.orm import Session

from dgn_picks_api.api.v1.dependencies import get_db, require_development_write_access
from dgn_picks_api.api.v1.schemas import UserCreate, UserResponse, UserUpdate
from dgn_picks_api.domains.picks.models import Pick
from dgn_picks_api.domains.users.models import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserResponse])
def list_users(user: str | None = Query(default=None), db: Session = Depends(get_db)) -> list[User]:
    statement = select(User)
    if user is not None:
        statement = statement.where(User.username == user)
    statement = statement.order_by(User.username, User.id)
    return list(db.scalars(statement).all())


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_development_write_access)],
)
def create_user(payload: UserCreate, db: Session = Depends(get_db)) -> User:
    user = User(**payload.model_dump())
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Username already exists") from exc
    db.refresh(user)
    return user


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(require_development_write_access)],
)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    dependencies=[Depends(require_development_write_access)],
)
def delete_user(user_id: int, db: Session = Depends(get_db)) -> Response:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if db.scalar(select(Pick.id).where(Pick.user_id == user_id).limit(1)) is not None:
        raise HTTPException(status_code=409, detail="User owns picks; deactivate instead")
    db.delete(user)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
