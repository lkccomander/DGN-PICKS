from typing import TypedDict

from fastapi import APIRouter

router = APIRouter(tags=["health"])


class HealthResponse(TypedDict):
    status: str
    service: str


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return {"status": "ok", "service": "dgn-picks-api"}
