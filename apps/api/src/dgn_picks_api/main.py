from fastapi import FastAPI

from dgn_picks_api.api.routes.health import router as health_router
from dgn_picks_api.api.v1.routes.analytics import router as analytics_router
from dgn_picks_api.api.v1.routes.dev import router as dev_router
from dgn_picks_api.api.v1.routes.games import router as games_router
from dgn_picks_api.api.v1.routes.markets import router as markets_router
from dgn_picks_api.api.v1.routes.picks import router as picks_router
from dgn_picks_api.api.v1.routes.users import router as users_router

app = FastAPI(title="DGN-PICKS API", version="0.1.0")
app.include_router(health_router, prefix="/api")

for router in (
    users_router,
    games_router,
    markets_router,
    picks_router,
    analytics_router,
    dev_router,
):
    app.include_router(router, prefix="/api/v1")
