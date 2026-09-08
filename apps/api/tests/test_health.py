import anyio
import httpx

from dgn_picks_api.main import app


async def request_health() -> httpx.Response:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        return await client.get("/api/health")


def test_health_returns_service_status() -> None:
    response = anyio.run(request_health)
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "dgn-picks-api"}


def test_api_v1_routes_are_mounted() -> None:
    paths = {route.path for route in app.routes}

    assert "/api/health" in paths
    assert "/api/v1/users" in paths
    assert "/api/v1/games" in paths
    assert "/api/v1/markets/{market_id}/history" in paths
    assert "/api/v1/picks" in paths
    assert "/api/v1/analytics/summary" in paths
    assert "/api/v1/dev/seed" in paths
