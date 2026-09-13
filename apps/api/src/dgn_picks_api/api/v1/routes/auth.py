import os

from fastapi import APIRouter, Header

from dgn_picks_api.api.v1.auth import authenticate, current_identity
from dgn_picks_api.api.v1.schemas import AuthResponse, LoginRequest

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest) -> AuthResponse:
    token = authenticate(payload.username, payload.password)
    return AuthResponse(access_token=token, username=payload.username, role=os.getenv("DGN_AUTH_ROLE", "admin"))


@router.get("/me", response_model=AuthResponse)
def me(authorization: str | None = Header(default=None)) -> AuthResponse:
    identity = current_identity(authorization)
    return AuthResponse(access_token="", username=identity["username"], role=identity["role"])
