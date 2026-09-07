# M2 Domain and Seed Design

**Status:** Approved for specification, awaiting implementation-plan review

## Goal

Add the domain foundation that turns the DGN-PICKS bootstrap into a deterministic local NCAA College Football picks application: normalized games and markets, immutable odds history, user-owned picks, and repeatable seed data.

## Scope

M2 includes:

- SQLAlchemy models and Alembic migration updates for users, teams, players, games, sportsbook sources, markets, selections, odds snapshots, and picks.
- A provider boundary with a deterministic `FixtureProvider`.
- Idempotent seed operations for the three approved users and the 13 Gato pick definitions.
- API v1 routes for users, games, markets, picks, and development seeding.
- Domain and API tests for ownership, normalization, snapshot history, calculations, idempotence, and unresolved seed input.

M2 does not include live providers, authentication, deployment, betting, payments, a full market-board UI, line-movement charts, or production-grade authorization.

## Architecture

The API remains a modular monolith. Domain modules own their schemas and rules, while route handlers translate HTTP requests into application-service calls. Provider adapters return normalized internal DTOs; persistence happens after provider validation, so future live providers cannot leak vendor-specific payload shapes into the rest of the system.

The fixture provider is deterministic and has no network dependency. Seed commands use stable external IDs and upserts where identity is defined, while odds snapshots remain append-oriented and are deduplicated by selection, sportsbook, observed timestamp, and source event ID. Picks copy the taken line and price at creation time and never derive historical values from later snapshots.

## Domain decisions

- User usernames are unique and limited to `gato`, `daran`, and `noch` in the initial seed. `noche` must not be created.
- All 13 supplied pick definitions belong to `gato`.
- Missing opponent, date, odds, or pick side data is represented as unresolved input or rejected with a clear validation error. It is never invented.
- `Malakai Toney 72.5 rec yards` remains unresolved because its Over/Under side is absent.
- Timestamps are timezone-aware UTC values.
- Decimal odds are canonical. American odds are optional source/display data.
- Snapshot history is immutable and append-oriented.
- Pick results are `pending`, `win`, `loss`, `push`, or `void`.

## Components

### Models and persistence

`domains/*/models.py` contains SQLAlchemy 2 typed models. Foreign keys enforce ownership and relationships. The migration creates the complete M2 schema and indexes stable external IDs, event start time, market lookup fields, and snapshot ordering fields.

### Provider boundary

`domains/providers/contracts.py` defines normalized provider protocols for listing games, retrieving a game, listing markets, and listing props. `domains/providers/fixture.py` implements the contract with fixed data covering at least four games, upcoming and completed statuses, main markets, three prop categories, multiple snapshots, one push, one win, one loss, and pending examples.

### Seed service

`seed.py` runs in a transaction and is safe to repeat. It creates or updates fixture reference data by stable identifiers, inserts missing snapshots only, and creates the 13 Gato picks as distinct records. The unresolved Malakai input is retained in a validation report and is not converted into a pick with a guessed side.

### API v1

Routes are grouped under `/api/v1`:

```text
GET    /users
GET    /users/{user_id}
GET    /games
GET    /games/{game_id}
GET    /games/{game_id}/markets
GET    /markets/{market_id}/history
GET    /picks
POST   /picks
PATCH  /picks/{pick_id}
DELETE /picks/{pick_id}
GET    /analytics/picks-summary
POST   /dev/seed
```

Handlers return validated Pydantic response models. The frontend is not allowed to hardcode domain data; M2 only needs a stable API contract for the later market board and tracker.

## Calculations

For a settled pick with required values:

- win: `stake_units * (decimal_odds - 1)`
- loss: `-stake_units`
- push or void: `0`
- ROI: `total_profit_units / total_units_risked`

Picks without odds or results remain excluded from profit and ROI totals.

## Error handling

- Invalid provider records fail validation before persistence and identify the offending fixture/provider field.
- Duplicate snapshots are ignored deterministically.
- Unknown users, games, markets, or selections return HTTP 404.
- Invalid pick payloads return HTTP 422.
- A pick cannot be created without a user and a valid market reference.
- Unresolved seed definitions are reported explicitly and cannot silently become playable picks.

## Testing

Tests must cover:

- stable fixture normalization;
- odds conversion, implied probability, and win/loss/push/void calculations;
- snapshot ordering, latest selection, and duplicate prevention;
- seed repeatability and the absence of `noche`;
- all 13 Gato definitions and no fabricated Daran/Noch picks;
- unresolved Malakai side validation;
- pick ownership and taken line/price preservation;
- API filtering, validation, and CRUD behavior.

## Acceptance criteria

- `POST /api/v1/dev/seed` is safe to call repeatedly.
- Users `gato`, `daran`, and `noch` exist; `noche` does not.
- The supplied 13 Gato definitions remain distinct and no missing sports data is guessed.
- Fixture games and markets are available through the API.
- Historical odds snapshots remain queryable in insertion order.
- Pick creation preserves the taken line and price.
- Domain and API tests pass when dependencies are installed.

