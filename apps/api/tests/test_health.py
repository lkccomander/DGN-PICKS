from fastapi.testclient import TestClient

from dgn_picks_api.main import app


def test_health_returns_service_status() -> None:
    response = TestClient(app).get("/api/health")
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
