from fastapi import FastAPI

from dgn_picks_api.api.routes.health import router as health_router

app = FastAPI(title="DGN-PICKS API", version="0.1.0")
app.include_router(health_router, prefix="/api")
