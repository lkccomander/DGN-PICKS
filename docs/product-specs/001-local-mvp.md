# DGN-PICKS — Local MVP Product Specification

Status: implementation-ready initial spec  
Phase: Local MVP  
Primary sport: NCAA College Football

## 1. Vision
DGN-PICKS is a sportsbook-style analytics and tracking site for NCAA College Football. It tracks games, game lines, props, line movement, user picks, results, units, ROI, and later closing-line value.

It is **not** a sportsbook and does not accept wagers, deposits, withdrawals, or payments.

## 2. Branding / UI direction
- Brand: `DGN-PICKS`
- Dark sportsbook-style UI.
- Dense, compact market presentation.
- Approved logo uses subtle interlocking/overlapping wordmark treatment.
- Stripe below logo: **blue → white → red → white → blue**.
- Pinnacle is a visual reference only; do not copy code, assets, trademarks, proprietary text, odds, or exact layouts.

## 3. MVP capabilities
1. Browse NCAA games by date.
2. Filter by conference, team, status, and market availability.
3. Show moneyline, spread, total.
4. Show team/player props when available.
5. Preserve multiple odds snapshots over time.
6. Show opening / prior / current line observations.
7. Plot line movement from stored observations.
8. Track picks by user.
9. Grade pending / win / loss / push / void.
10. Show wins, losses, pushes, win rate, units, P/L, ROI.
11. Preserve enough history for future CLV.

## 4. Non-goals
- No real-money wagering.
- No production auth in phase 1.
- No deployment in phase 1.
- No ML picks engine.
- No live provider required initially.
- No scraping Pinnacle.
- No microservices.

## 5. Stack
- Frontend: Next.js + TypeScript
- Backend: FastAPI
- DB: PostgreSQL
- ORM: SQLAlchemy
- Migrations: Alembic
- API contract: OpenAPI
- Frontend API client: generated from OpenAPI
- Backend tests: pytest
- E2E: Playwright
- Local DB: Docker Compose preferred
- Config: environment variables + `.env.example`

## 6. Repo structure
```text
dgn-picks/
├── AGENTS.md
├── ARCHITECTURE.md
├── PLANS.md
├── README.md
├── .env.example
├── apps/
│   ├── web/
│   │   ├── public/brand/
│   │   └── src/
│   └── api/
│       ├── app/
│       │   ├── api/
│       │   ├── core/
│       │   ├── db/
│       │   ├── domains/
│       │   │   ├── users/
│       │   │   ├── teams/
│       │   │   ├── players/
│       │   │   ├── games/
│       │   │   ├── markets/
│       │   │   ├── odds/
│       │   │   ├── props/
│       │   │   ├── picks/
│       │   │   └── providers/
│       │   └── ingestion/
│       ├── migrations/
│       └── tests/
├── packages/api-client/
├── data/fixtures/
├── data/seeds/
├── docs/
│   ├── product-specs/
│   ├── design-docs/
│   ├── exec-plans/active/
│   ├── exec-plans/completed/
│   └── generated/
├── scripts/
├── tests/e2e/
└── infra/local/
```

## 7. Domain model

### User
- id
- username (unique)
- display_name
- active
- created_at

Seed users:
- `gato`
- `daran`
- `noch`

Do **not** create `noche`.

### Team
- id
- external_ids
- name
- short_name
- abbreviation
- conference
- logo_url optional
- active

### Player
- id
- external_ids
- team_id
- name
- position
- active

### Game
- id
- external_ids
- season
- week
- kickoff_at
- home_team_id
- away_team_id
- venue optional
- status
- home_score optional
- away_score optional

Normalized statuses: scheduled, live, final, postponed, cancelled.

### SportsbookSource
- id
- name
- source_type
- active

MVP source: `local-fixture`.

### Market
- id
- game_id
- market_type
- period
- player_id optional
- team_id optional
- status

Examples:
- game_moneyline
- game_spread
- game_total
- team_total
- player_passing_yards
- player_receiving_yards
- player_rushing_yards
- player_receptions
- player_passing_touchdowns
- player_anytime_touchdown

### Selection
- id
- market_id
- selection_key
- team_id optional
- player_id optional
- side optional

### OddsSnapshot
Append-oriented historical observation:
- id
- selection_id
- sportsbook_id
- observed_at
- line_value optional
- american_odds optional
- decimal_odds
- implied_probability optional
- source_event_id optional

Never overwrite a prior observation to represent movement.

### Pick
- id
- user_id
- game_id
- market_id
- selection_id optional
- picked_at
- line_value optional
- american_odds optional
- decimal_odds optional
- stake_units
- status
- result
- profit_units
- notes optional

Results: pending, win, loss, push, void.

A pick preserves the number taken even if the market later moves.

## 8. Seed users
Seed idempotently:

| username | display_name | active |
|---|---|---|
| gato | Gato | true |
| daran | Daran | true |
| noch | Noch | true |

## 9. Initial Gato picks
All picks below belong to `gato`.

Defaults:
- `status = pending`
- `result = pending`
- `stake_units = 1.0` unless changed later
- odds unknown unless explicitly supplied; **do not invent odds**

| # | User | Pick | Normalized interpretation |
|---:|---|---|---|
| 1 | gato | Stanford +24.5 | Game spread: Stanford +24.5 |
| 2 | gato | Malakai Toney 72.5 rec yards | Player receiving yards 72.5; side unresolved |
| 3 | gato | Josh Hoover over 246.5 passing yards | Player passing yards: Over 246.5 |
| 4 | gato | Over 56.5 Indiana | Indiana game total: Over 56.5 |
| 5 | gato | Over 51.5 Duke | Duke game total: Over 51.5 |
| 6 | gato | Over 58.5 Auburn | Auburn game total: Over 58.5 |
| 7 | gato | Over 50.5 LSU | LSU game total: Over 50.5 |
| 8 | gato | Over 54.5 UCLA | UCLA game total: Over 54.5 |
| 9 | gato | Over 50.5 Washington | Washington game total: Over 50.5 |
| 10 | gato | Notre Dame -20.5 | Game spread: Notre Dame -20.5 |
| 11 | gato | Ole Miss -6.5 | Game spread: Ole Miss -6.5 |
| 12 | gato | Over 52.5 Houston | Houston game total: Over 52.5 |
| 13 | gato | Over 53.5 SMU | SMU game total: Over 53.5 |

### Important ambiguity
`Malakai Toney 72.5 rec yards` does not specify Over or Under. Codex must **not guess**. Preserve it as unresolved seed input or fail seed validation with a clear message until the side is provided.

Similarly, if exact opponent/date/odds metadata is missing for a pick, do not invent it.

## 10. Fixture requirements
Deterministic local fixtures should cover:
- at least 4 NCAA games;
- upcoming and completed games;
- spread, total, moneyline movement;
- at least 3 prop categories;
- multiple snapshots per selected market;
- a push example;
- one winning and one losing settled QA example;
- pending examples.

The 13 Gato picks are product seed data and should remain distinct from generic QA fixture examples.

## 11. API
Version under `/api/v1`.

```text
GET    /api/v1/users
GET    /api/v1/users/{user_id}
GET    /api/v1/games
GET    /api/v1/games/{game_id}
GET    /api/v1/games/{game_id}/markets
GET    /api/v1/markets/{market_id}/history
GET    /api/v1/picks
POST   /api/v1/picks
PATCH  /api/v1/picks/{pick_id}
DELETE /api/v1/picks/{pick_id}
GET    /api/v1/analytics/picks-summary
POST   /api/v1/dev/seed
```

Useful filters:
```text
GET /api/v1/picks?user=gato
GET /api/v1/games?date=YYYY-MM-DD
GET /api/v1/games?conference=SEC
```

## 12. UI screens

### Global shell
- top header with DGN-PICKS logo
- left sportsbook navigation
- central market board
- optional right context panel
- dark navy theme

### Market board
Show selected date, kickoff, away/home teams, spread, total, moneyline, availability, and expandable markets.

### Game detail
Show matchup, kickoff, status/score, main markets, props, opening/current observations, recent movement, and create-pick action.

### Line movement
Plot stored observations only; no fabricated sportsbook observations.

### Pick tracker
User filter plus:
- pick description
- line
- odds if known
- stake
- pending/settled
- result
- profit/loss
- summary metrics

Initial tracker must be able to show all 13 Gato seed definitions.

### User selector
Seed users available for filtering/comparison:
- Gato
- Daran
- Noch

Do not create artificial picks for Daran or Noch.

## 13. Calculations
Use decimal odds canonically.

Win:
`profit_units = stake_units * (decimal_odds - 1)`

Loss:
`profit_units = -stake_units`

Push/Void:
`profit_units = 0`

ROI:
`ROI = total_profit_units / total_units_risked`

Do not calculate profit/ROI for picks lacking required odds/results.

## 14. Provider boundary
Conceptual contract:
```text
list_games(date_range)
get_game(external_game_id)
list_markets(external_game_id)
list_props(external_game_id)
```

MVP: `FixtureProvider`.
Future real providers must normalize into the same internal domain.

## 15. Data integrity
- Namespaced external IDs.
- UTC timestamps.
- Decimal odds canonical.
- No invented odds, dates, opponents, or missing sides.
- Provider validation at ingestion boundary.
- Deterministic duplicate-snapshot prevention.
- Historical observations immutable.
- Pick taken line/price preserved.

## 16. Observability
Structured ingestion logs:
- provider
- start/finish
- games received
- markets received
- snapshots inserted
- duplicates ignored
- validation failures

Never log credentials.

## 17. Security baseline
- `.env` gitignored
- `.env.example` placeholders only
- validated request bodies
- no concatenated SQL from user input
- provider credentials server-side only
- explicit external timeouts
- no secrets in browser bundle

## 18. Testing
High-value tests:
- odds conversion
- implied probability
- win/loss/push/void math
- ROI
- snapshot ordering
- latest snapshot selection
- duplicate prevention
- provider normalization
- seed idempotence
- user/pick ownership
- unresolved seed validation
- API validation

Required E2E:
1. open board;
2. choose game;
3. inspect market;
4. create pick for user;
5. open tracker;
6. verify taken line/price remains unchanged after a later snapshot.

Seed acceptance:
- `gato`, `daran`, `noch` exist;
- `noche` does not exist;
- all 13 provided pick definitions belong to Gato;
- Daran/Noch have no fake picks;
- Malakai Toney side is not guessed.

## 19. Milestones

### M1 — Bootstrap
Repo structure, Next.js shell, FastAPI shell, PostgreSQL local setup, migrations, lint/format/test commands, health checks, docs.

### M2 — Domain + seed
Users, teams, players, games, markets, selections, snapshots, picks, FixtureProvider, seed users, Gato picks.

### M3 — Market board
Sportsbook-style shell, date navigation, main markets, filters, expansion.

### M4 — Game detail + movement
Props, history, movement chart.

### M5 — Pick tracker
CRUD, user ownership, results, units, ROI, Gato seed display.

### M6 — Validation
Clean bootstrap, automated tests, E2E, docs sync.

## 20. Acceptance criteria
- Clean local setup works from documented commands.
- Migrations succeed.
- Seed is repeatable/idempotent.
- Users Gato, Daran, Noch are present.
- No user `noche`.
- Gato's 13 supplied pick definitions are preserved.
- Malakai Toney side is not guessed.
- UI gets game/market data through API, not frontend hardcoding.
- Line movement comes from persisted snapshots.
- Pick taken values are preserved.
- Grading supports pending/win/loss/push/void.
- Branding follows DGN-PICKS rules.
- Lint/tests/E2E pass.

## 21. Decision Log
- 2026-09-07: modular monorepo; avoid microservices.
- 2026-09-07: FixtureProvider first; live vendor deferred.
- 2026-09-07: append-oriented odds history.
- 2026-09-07: every pick belongs to a user.
- 2026-09-07: seed users are `gato`, `daran`, `noch`; `noche` is incorrect.
- 2026-09-07: all 13 supplied initial picks belong to `gato`.
- 2026-09-07: missing sports data must remain unresolved rather than guessed.

## 22. Progress
- [x] Product concept
- [x] Branding direction
- [x] Architecture
- [x] Domain model
- [x] Seed users
- [x] Gato pick definitions
- [x] Repository bootstrap
- [x] Database implementation
- [x] FixtureProvider
- [x] UI shell
- [x] Market board
- [x] Line movement
- [x] Pick tracker
- [ ] MVP validation

## 23. Codex implementation rules
- Read `AGENTS.md` and this spec first.
- Work milestone by milestone.
- Do not silently change product semantics.
- Do not guess missing sports data.
- Do not connect a paid/live provider in M1.
- Prefer complete runnable changes.
- Keep migrations/seeds deterministic.
- Add tests for domain behavior.
- Record non-obvious decisions.
- If implementation conflicts with the spec, surface the conflict instead of improvising.
