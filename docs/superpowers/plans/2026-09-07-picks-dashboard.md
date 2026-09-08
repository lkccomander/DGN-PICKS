# Picks Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a user-selectable picks dashboard backed by `GET /api/picks?user=<username>`.

**Architecture:** The FastAPI service owns validation, database access, and response shaping. The Next.js app reads `NEXT_PUBLIC_API_URL`, requests only the selected user's picks, and renders explicit loading, error, and empty states. PostgreSQL remains private behind the API.

**Tech Stack:** FastAPI, Pydantic, SQLAlchemy, PostgreSQL, Alembic, Next.js 16, React 19, TypeScript.

## Global Constraints

- Accepted users are exactly `gato`, `daran`, and `noch`.
- All initial demo picks belong to `gato`.
- Store and compare timestamps in UTC.
- Do not invent missing sports, odds, event, market, or result data.
- Preserve the modular monolith; do not add a microservice.
- Keep secrets out of source control.

---

### Task 1: Confirm Existing Data and Route Boundaries

**Files:**
- Read: `apps/api/src/dgn_picks_api`
- Read: `apps/api/migrations/versions/0001_initial_schema.py`
- Read: `apps/api/migrations/versions/0002_m2_domain_schema.py`
- Read: `apps/web/src/app/page.tsx`
- Read: `apps/web/src/app/layout.tsx`

**Interfaces:**
- Consumes: existing SQLAlchemy models, FastAPI router registration, and current Next.js page.
- Produces: verified model names and router location for Tasks 2 and 4.

- [ ] **Step 1: Locate the pick model and router registration**

Run:

```powershell
rg -n "class .*Pick|pick|include_router|APIRouter|export default|function Home" apps/api/src apps/web/src
```

Expected: identify the existing pick ORM model, API router module, and current home page without adding a duplicate model or router.

- [ ] **Step 2: Confirm the database columns used by the response**

Run:

```powershell
rg -n "CREATE TABLE|op\.create_table|user_id|picked_at|american_odds|decimal_odds|result|profit_units|notes" apps/api/migrations apps/api/src
```

Expected: map each response field to an existing column or explicitly mark it unavailable so the API returns `null` rather than guessing.

- [ ] **Step 3: Commit no code**

This task is a repository inspection checkpoint. Do not create a commit unless an existing mismatch must be documented.

### Task 2: Add the Picks API Contract

**Files:**
- Create or modify: `apps/api/src/dgn_picks_api/api/routes/picks.py`
- Modify: `apps/api/src/dgn_picks_api/api/router.py`
- Create or modify: `apps/api/tests/test_picks.py`

**Interfaces:**
- Consumes: existing SQLAlchemy session dependency and pick/user models.
- Produces: `GET /api/picks?user=<username>` returning a JSON array; invalid users return HTTP 400.

- [ ] **Step 1: Write failing route tests**

Add tests with the existing test client and fixture style:

```python
def test_picks_reject_unknown_user(client):
    response = client.get("/api/picks?user=noche")
    assert response.status_code == 400


def test_picks_filter_by_user_and_sort_newest_first(client, seeded_picks):
    response = client.get("/api/picks?user=gato")
    assert response.status_code == 200
    body = response.json()
    assert all(item["username"] == "gato" for item in body)
    assert [item["id"] for item in body] == [seeded_picks.latest.id, seeded_picks.earlier.id]


def test_picks_return_empty_array_for_allowed_user_without_picks(client):
    response = client.get("/api/picks?user=noch")
    assert response.status_code == 200
    assert response.json() == []
```

- [ ] **Step 2: Run the focused tests and verify failure**

Run from `apps/api`:

```powershell
py -m pytest tests/test_picks.py -q
```

Expected: FAIL because `/api/picks` and its test fixtures do not yet exist.

- [ ] **Step 3: Define the response schema and allowed-user validation**

Implement a focused route module with this public shape:

```python
ALLOWED_USERS = {"gato", "daran", "noch"}

class PickResponse(BaseModel):
    id: int
    username: str
    game_id: int | None
    market_id: int | None
    selection_id: int | None
    picked_at: datetime | None
    line_value: Decimal | None
    american_odds: int | None
    decimal_odds: Decimal | None
    stake_units: Decimal
    result: str
    profit_units: Decimal | None
    notes: str | None
```

Reject a username not in `ALLOWED_USERS` with `HTTPException(status_code=400, detail="invalid user")`. Serialize ORM values through Pydantic; do not synthesize absent values.

- [ ] **Step 4: Implement the query and register the router**

Query the requested user through the existing relationship, apply `order_by(Pick.picked_at.desc().nullslast(), Pick.id.desc())`, and register the router under the existing `/api` prefix. Use the project's current session dependency instead of opening a second engine.

- [ ] **Step 5: Run the focused tests and verify success**

Run:

```powershell
py -m pytest tests/test_picks.py -q
```

Expected: all picks route tests pass.

- [ ] **Step 6: Commit the backend contract**

```powershell
git add apps/api/src/dgn_picks_api apps/api/tests/test_picks.py
git commit -m "feat: add user-filtered picks endpoint"
```

### Task 3: Add Frontend API Client and Dashboard State

**Files:**
- Create: `apps/web/src/lib/api.ts`
- Create: `apps/web/src/lib/types.ts`
- Modify: `apps/web/src/app/page.tsx`

**Interfaces:**
- Consumes: `NEXT_PUBLIC_API_URL` and the backend `GET /api/picks` contract.
- Produces: `fetchPicks(username): Promise<PickResponse[]>` and a dashboard with a controlled user selector.

- [ ] **Step 1: Add a typed client and types**

Use this interface:

```ts
export const USERS = ["gato", "daran", "noch"] as const;
export type Username = (typeof USERS)[number];

export type PickResponse = {
  id: number;
  username: Username;
  game_id: number | null;
  market_id: number | null;
  selection_id: number | null;
  picked_at: string | null;
  line_value: string | number | null;
  american_odds: number | null;
  decimal_odds: string | number | null;
  stake_units: string | number;
  result: string;
  profit_units: string | number | null;
  notes: string | null;
};
```

`fetchPicks` must throw a descriptive error for non-2xx responses and use `${process.env.NEXT_PUBLIC_API_URL}/api/picks?user=${encodeURIComponent(username)}`.

- [ ] **Step 2: Add dashboard state**

Initialize `selectedUser` to `"gato"`, fetch on initial render and whenever it changes, and maintain `loading`, `error`, and `picks` state. Do not use a browser-side PostgreSQL connection or hardcode the Railway API domain in source.

- [ ] **Step 3: Render the selector and explicit states**

Render a native select with the three allowed usernames. Render loading text while fetching, an error message with a retry action on failure, an empty-state message when the array is empty, and cards for returned picks. Display `null` values as `N/A`; do not replace them with guessed teams, odds, or results.

- [ ] **Step 4: Run the frontend build**

Run from `apps/web`:

```powershell
npm run build
```

Expected: the Next.js production build completes successfully.

- [ ] **Step 5: Commit the frontend integration**

```powershell
git add apps/web/src/lib apps/web/src/app/page.tsx
git commit -m "feat: add user-selectable picks dashboard"
```

### Task 4: Verify Full Stack and Deploy

**Files:**
- Modify if needed: `apps/api/src/dgn_picks_api/api/routes/picks.py`
- Modify if needed: `apps/web/src/lib/api.ts`
- Read: Railway service variables and deployment logs

**Interfaces:**
- Consumes: the API and frontend commits from Tasks 2 and 3.
- Produces: a deployed dashboard using Railway API data.

- [ ] **Step 1: Run the complete API test suite**

Run from `apps/api`:

```powershell
py -m pytest -q
```

Expected: all existing health, domain, and picks tests pass.

- [ ] **Step 2: Verify the production API manually**

Open:

```text
https://dgn-picks-production.up.railway.app/api/health
https://dgn-picks-production.up.railway.app/api/picks?user=gato
https://dgn-picks-production.up.railway.app/api/picks?user=noche
```

Expected: health returns status `ok`, `gato` returns an array, and `noche` returns HTTP 400.

- [ ] **Step 3: Configure the frontend variable**

In the Railway frontend service, set:

```text
NEXT_PUBLIC_API_URL=https://dgn-picks-production.up.railway.app
```

Redeploy because `NEXT_PUBLIC_*` values are embedded during the Next.js build.

- [ ] **Step 4: Validate the production dashboard**

Open `https://dgnweb-production.up.railway.app`, confirm `gato` loads by default, switch to `daran` and `noch`, and verify that loading, empty, and error states do not break the page.

- [ ] **Step 5: Commit any only-when-needed deployment fix**

```powershell
git status --short
```

Commit only a demonstrated fix; never add `logs/` or environment files.

