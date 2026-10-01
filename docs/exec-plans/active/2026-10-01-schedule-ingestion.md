# Multi-sport schedule ingestion

## Purpose
Automate schedule ingestion for NFL, NCAAFB and MLB while preserving the
existing deterministic fixture workflow and provider boundary.

## Scope / Non-scope
Schedule discovery, normalization, validation, deduplication, UTC conversion,
raw-response audit metadata and a repeatable local ingestion command.
Odds, markets, props, standings, live scores and pick grading are out of scope
for the first schedule-ingestion milestone.

## Progress
- [x] Inspect the current provider contract and Game model.
- [x] Identify missing sport/league identity and ingestion audit fields.
- [x] Select CFBD as the first authorized API/source for NCAAFB.
- [x] Extend normalized contract and persistence schema for multiple sports.
- [x] Implement the first source adapter with injected HTTP transport.
- [x] Add CFBD tests for deduplication, validation, statuses and UTC handling.
- [x] Add a read-only MLB schedule adapter and market-board preview.
- [x] Add the daily MLB JSON snapshot and local database import workflow.

## Implementation plan
1. Use one normalized schedule contract with `sport`, `league`, stable provider
   event ID, season, week/series metadata, teams, kickoff UTC, status and scores.
2. Add sport/league identity to persisted games and namespace all external IDs.
3. Keep one adapter per source or league; adapters normalize at the boundary and
   never expose provider payload shapes to the domain/UI.
4. Store retrieval timestamp, source name, source URL/request key and a payload
   checksum for audit and safe replays. Upserts must be idempotent by source and
   external event ID; historical snapshots remain append-oriented where needed.
5. Start with a manual command and dry-run report, then add a scheduler after
   validation. Secrets stay in environment variables.

The first adapter is `CFBDProvider`. It reads `CFBD_API_KEY`, requests games by
season, filters the requested UTC range, namespaces IDs as `cfbd:<id>`, and
rejects malformed provider payloads before they reach the domain.

The `Game` model and API schemas now carry `sport` and `league`, with migration
`0012_add_game_sport_league`. Existing fixture rows default to `ncaafb` / `NCAAFB`
so the local seed remains compatible.

The admin endpoint `POST /api/v1/schedules/admin/mlb/sync?date=YYYY-MM-DD`
fetches Stats API once, writes `data/ingestion/mlb/YYYY-MM-DD.json`, and imports
normalized games and teams. Repeated calls reuse that snapshot unless
`force=true` is supplied. The public `GET /api/v1/schedules/mlb` endpoint reads
the local database and never calls the external provider.

## Validation
Each league needs deterministic sample payloads, timezone conversion tests,
duplicate-event tests, malformed-payload rejection and status mapping tests.
Live ingestion must be tested against a small date range before enabling a wider
schedule job.

## Surprises & Discoveries
The current `NormalizedGame` assumes a conference and integer week, which does
not fit MLB series/games. The current `Game` schema has no sport or league.

## Decision Log
2026-10-01: Preserve `FixtureProvider` as the local deterministic source until
an authorized external source is selected and validated.
2026-10-01: Pinnacle baseball matchups URL was rejected as an ingestion source.
Project rules explicitly prohibit scraping Pinnacle and copying its data, text,
assets, trademarks or exact layouts. The page is also client-rendered, so its
initial HTML does not expose the matchup data.
2026-10-01: MLB Stats API is acceptable for development/testing only until
commercial redistribution rights are confirmed. The live preview must identify
MLB as its source and must not be treated as licensed production data.

## Outcomes & Retrospective
CFBD adapter, sport/league identity, migration, and MLB daily persistence
ingestion are implemented. The NFL adapter remains pending; no MLB odds or
markets are fabricated.
