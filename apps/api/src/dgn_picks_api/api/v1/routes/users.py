from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from dgn_picks_api.api.v1.dependencies import get_db
from dgn_picks_api.api.v1.schemas import UserResponse
from dgn_picks_api.domains.users.models import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserResponse])
def list_users(user: str | None = Query(default=None), db: Session = Depends(get_db)) -> list[User]:
    statement = select(User)
    if user is not None:
        statement = statement.where(User.username == user)
    statement = statement.order_by(User.username, User.id)
    return list(db.scalars(statement).all())
