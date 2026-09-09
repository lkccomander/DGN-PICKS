# Milestone 1 Bootstrap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a runnable local DGN-PICKS monorepo foundation with web, API, PostgreSQL, migrations, health checks, and baseline developer commands.

**Status:** Complete for the current GitHub → Railway workflow. API tests pass (`39 passed`) and frontend lint/build pass through Windows Node. Local Compose migration verification is deferred because a separate local runtime is not required.

**Architecture:** A modular monorepo contains a Next.js App Router frontend in `apps/web` and a FastAPI backend in `apps/api`. PostgreSQL runs as a local Docker Compose dependency; the first migration establishes the shared database schema foundation without connecting a live odds provider.

**Tech Stack:** Next.js, TypeScript, React, FastAPI, Python, PostgreSQL, Docker Compose, Alembic, pytest, ESLint.

## Global Constraints

- Build milestone by milestone and keep the repo runnable after each milestone.
- Use a modular monorepo; no microservices in MVP.
- Brand name is `DGN-PICKS`; use the existing stripe assets and dark navy visual direction.
- Use deterministic local fixtures before any live odds provider.
- Store timestamps in UTC and keep secrets out of source control.

### Task 1: Repository tooling and local services

**Files:**
- Create: `package.json`
- Create: `docker-compose.yml`
- Create: `.env.example`
- Create: `.gitignore`
- Create: `Makefile`

    - [x] Add workspace scripts for web, API, checks, and database services.
    - [x] Add PostgreSQL health-gated Compose service with a non-secret local default.
    - [x] Add environment examples and ignore local secrets/build output.
    - [ ] Run Compose configuration validation (blocked only by Docker Desktop WSL integration in this distro).

### Task 2: FastAPI shell

**Files:**
- Create: `apps/api/pyproject.toml`
- Create: `apps/api/src/dgn_picks_api/main.py`
- Create: `apps/api/src/dgn_picks_api/api/routes/health.py`
- Create: `apps/api/tests/test_health.py`

    - [x] Define a typed FastAPI app and `/health` route returning service status.
    - [x] Add pytest coverage through an ASGI test client.
    - [x] Run the API test suite and import check.

### Task 3: Next.js shell

**Files:**
- Create: `apps/web/package.json`
- Create: `apps/web/tsconfig.json`
- Create: `apps/web/next.config.ts`
- Create: `apps/web/eslint.config.mjs`
- Create: `apps/web/src/app/layout.tsx`
- Create: `apps/web/src/app/page.tsx`
- Create: `apps/web/src/app/globals.css`

    - [x] Add App Router root layout and branded starter page.
    - [x] Reuse existing brand assets without introducing provider-specific UI.
    - [x] Run lint and production build.

### Task 4: Database migration foundation

**Files:**
- Create: `apps/api/alembic.ini`
- Create: `apps/api/migrations/env.py`
- Create: `apps/api/migrations/versions/0001_initial_schema.py`
- Create: `apps/api/src/dgn_picks_api/db.py`

    - [x] Add Alembic configuration driven by `DATABASE_URL`.
    - [x] Add initial tables for users, sports, events, markets, odds snapshots, picks, and pick legs.
    - [~] Verify migration upgrade and downgrade against local PostgreSQL — deferred; local PostgreSQL is not required for the current workflow.

### Task 5: Documentation and verification

**Files:**
- Modify: `README.md`
- Modify: `PLANS.md`

    - [x] Document install, run, test, lint, migration, and health commands.
    - [x] Record that Milestone 1 intentionally has no live odds provider.
    - [x] Run all available checks and report unavailable external prerequisites explicitly.
