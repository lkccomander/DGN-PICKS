import os

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from dgn_picks_api.api.routes.health import router as health_router
from dgn_picks_api.api.v1.routes.analytics import router as analytics_router
from dgn_picks_api.api.v1.routes.auth import router as auth_router
from dgn_picks_api.api.v1.routes.dev import router as dev_router
from dgn_picks_api.api.v1.routes.games import router as games_router
from dgn_picks_api.api.v1.routes.markets import router as markets_router, selections_router
from dgn_picks_api.api.v1.routes.picks import router as picks_router
from dgn_picks_api.api.v1.routes.seed import router as seed_router
from dgn_picks_api.api.v1.routes.teams import players_router, router as teams_router
from dgn_picks_api.api.v1.routes.users import router as users_router

app = FastAPI(title="DGN-PICKS API", version="0.1.0")

cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "DGN_CORS_ORIGINS",
        "https://dgnweb-production.up.railway.app",
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Accept", "Content-Type", "X-DGN-Write-Key"],
)

app.include_router(health_router, prefix="/api")

for router in (
    users_router,
    auth_router,
    teams_router,
    players_router,
    games_router,
    markets_router,
    selections_router,
    picks_router,
    seed_router,
    analytics_router,
    dev_router,
):
    app.include_router(router, prefix="/api/v1")
