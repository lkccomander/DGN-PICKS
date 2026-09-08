# Picks Dashboard Design

## Scope

Add the first real frontend-to-API flow for the picks dashboard. The dashboard
will provide a user selector for `gato`, `daran`, and `noch`, with `gato`
selected by default. All initial demo picks remain owned by `gato`.

## API Contract

Expose `GET /api/picks?user=<username>` from the FastAPI application.

- Accepted users: `gato`, `daran`, `noch`.
- Unknown users return HTTP 400.
- The response returns an array of picks for the requested user.
- Picks are ordered newest first using their UTC pick timestamp.
- The API must not invent missing event, market, odds, or result data.

## Frontend Behavior

- Read the API base URL from `NEXT_PUBLIC_API_URL`.
- Load `gato` on the initial render.
- Request new data when the selected user changes.
- Show loading, error, and empty states.
- Render the available pick fields without replacing missing values with
  guessed data.

## Architecture

Keep the implementation inside the existing modular monolith. Add a focused
API route and response schema, a frontend API client, and dashboard rendering
logic. Database access remains behind the API boundary; the browser never
connects directly to PostgreSQL.

## Testing

- API tests cover each allowed user, unknown-user rejection, ownership
  filtering, and newest-first ordering.
- Frontend tests or build validation cover the default user, user changes,
  loading, error, and empty states.
- Run the existing API test suite and frontend build before deployment.

