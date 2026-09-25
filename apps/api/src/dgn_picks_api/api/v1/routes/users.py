from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from sqlalchemy.orm import Session

from dgn_picks_api.api.v1.dependencies import get_db, require_authenticated_write_access, require_editor_identity
from dgn_picks_api.api.v1.schemas import UserCreate, UserResponse, UserUpdate, PublicUserResponse
from dgn_picks_api.domains.picks.models import Pick
from dgn_picks_api.domains.users.models import User
from dgn_picks_api.domains.users.passwords import hash_password

router = APIRouter(prefix="/users", tags=["users"])
admin_router = APIRouter(prefix="/admin/users", tags=["admin"], dependencies=[Depends(require_editor_identity)])


@admin_router.get("", response_model=list[UserResponse])
@router.get("", response_model=list[PublicUserResponse])
def list_users(user: str | None = Query(default=None), db: Session = Depends(get_db)) -> list[User]:
    statement = select(User)
    if user is not None:
        statement = statement.where(User.username == user)
    statement = statement.order_by(User.username, User.id)
    return list(db.scalars(statement).all())


@admin_router.get("/{user_id}", response_model=UserResponse)
@router.get("/{user_id}", response_model=PublicUserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_authenticated_write_access)],
)
def create_user(payload: UserCreate, db: Session = Depends(get_db)) -> User:
    values = payload.model_dump(exclude={"password"})
    if values.get("email"):
        values["email"] = values["email"].lower()
    user = User(**values, password_hash=hash_password(payload.password) if payload.password else None)
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Username or email already exists") from exc
    db.refresh(user)
    return user


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(require_authenticated_write_access)],
)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    changes = payload.model_dump(exclude_unset=True)
    if any(changes.get(field) is None for field in ("display_name", "active") if field in changes):
        raise HTTPException(status_code=422, detail="Display name and active cannot be null")
    revoke = ("active" in changes and changes["active"] != user.active) or bool(changes.get("password"))
    if revoke:
        user.session_version += 1
    for field, value in changes.items():
        if field == "password":
            if value:
                user.password_hash = hash_password(value)
            continue
        if field == "email" and value:
            value = value.lower()
        setattr(user, field, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Username or email already exists") from exc
    db.refresh(user)
    return user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    dependencies=[Depends(require_authenticated_write_access)],
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
