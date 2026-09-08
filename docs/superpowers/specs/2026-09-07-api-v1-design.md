# DGN-PICKS API v1 Design

## Scope

Implement the approved M2 API v1 contract for the Railway-hosted FastAPI service. This milestone has no authentication. It exposes deterministic local fixture data through the persisted domain and provides a development-only seed endpoint.

## Architecture

Routes remain thin and delegate database work to focused application/query helpers. A shared SQLAlchemy session dependency obtains a session from `DATABASE_URL` and closes it after each request. Pydantic v2 schemas define request validation and stable response shapes.

The API is mounted under `/api/v1` while the existing `/api/health` endpoint remains available for Railway health checks.

## Endpoints

- `GET /api/v1/users`: list users, optionally filtered by `user`.
- `GET /api/v1/games`: list games, optionally filtered by `date` and `conference`.
- `GET /api/v1/games/{game_id}`: return one game or `404`.
- `GET /api/v1/games/{game_id}/markets`: list markets and current odds for a game.
- `GET /api/v1/markets/{market_id}/history`: return append-only odds snapshots.
- `GET /api/v1/picks`: list picks, optionally filtered by `user` and `date`.
- `POST /api/v1/picks`: create a pick after validating its game, market, selection, and user references.
- `GET /api/v1/analytics/summary`: return aggregate pick performance and ROI.
- `POST /api/v1/dev/seed`: run the idempotent local seed service and return its `SeedReport`.

Unknown resource identifiers return `404`. Malformed request bodies and invalid foreign-key references return `422`. The API does not invent unresolved provider data and does not create a playable pick for an unresolved selection.

## Pick and Odds Semantics

When a pick is created, its line and odds are copied from the selected current snapshot. Later odds snapshots are append-only and cannot alter the pick's taken price. Duplicate snapshot observations are ignored using the domain uniqueness key.

## Testing

API tests use the existing test client and an isolated database/session boundary. They cover health, seed idempotency, user and game listing, filters, market history, pick creation, taken-price preservation, unknown references, and invalid request bodies. Tests remain network-free and use deterministic fixture data.
