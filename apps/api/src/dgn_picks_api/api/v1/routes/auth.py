import os

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from dgn_picks_api.api.v1.auth import authenticate, authenticate_user, current_identity, issue_token, signing_configured
from dgn_picks_api.api.v1.dependencies import get_db
from dgn_picks_api.api.v1.schemas import AuthResponse, LoginRequest, RegistrationRequest, RegistrationResponse, UserResponse
from dgn_picks_api.domains.users.models import User
from dgn_picks_api.domains.users.passwords import hash_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    if os.getenv("DGN_AUTH_USERNAME") == payload.username and os.getenv("DGN_AUTH_PASSWORD") is not None:
        token = authenticate(payload.username, payload.password)
        return AuthResponse(access_token=token, username=payload.username, role=os.getenv("DGN_AUTH_ROLE", "admin"))
    user = authenticate_user(db, payload.username, payload.password)
    return AuthResponse(access_token=issue_token(user.username, "user", user.id), username=user.username, role="user")


@router.post("/register", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegistrationRequest, db: Session = Depends(get_db)) -> RegistrationResponse:
    if not signing_configured():
        raise HTTPException(status_code=503, detail="Authentication is not configured")
    user = User(
        username=payload.username,
        email=payload.email.lower(),
        display_name=payload.display_name,
        country=payload.country,
        password_hash=hash_password(payload.password),
        active=True,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Username or email already exists") from exc
    db.refresh(user)
    return RegistrationResponse(
        user=UserResponse.model_validate(user),
        access_token=issue_token(user.username, "user", user.id),
    )


@router.get("/me", response_model=AuthResponse)
def me(authorization: str | None = Header(default=None)) -> AuthResponse:
    identity = current_identity(authorization)
    return AuthResponse(access_token="", username=identity["username"], role=identity["role"])
