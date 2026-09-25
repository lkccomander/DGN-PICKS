# Audit remediation — 2026-09-24

## Purpose
Resolve A1–A15 in PROJECT-RECAP.md and make the supported MVP flows testable.

## Scope / Non-scope
Includes API/account privacy, session invalidation, accurate seed definitions,
fixture coverage, pick authorization/eligibility, settled analytics, web/desktop
integration, dependencies, migrations, regression tests, CI, and documentation.
Production deployment and data writes are not part of this local remediation.
Token accounting, live providers, CLV, and email verification remain future scope.

## Progress
- [x] Read the audit and source-of-truth documents; reproduce baseline failures.
- [x] Phase 1: account privacy, sessions, authenticated picks, domain regression tests.
- [x] Phase 2: seed/QA separation, reversible legacy quarantine, fixture coverage, analytics.
- [ ] Phase 3: desktop boundary, truthful account UI, lint, dependencies, contract/CI.
- [ ] Phase 4: validation, documentation, remaining deployment checklist.

## Implementation plan
1. Separate public user projections from protected admin/account reads.
2. Bind user tokens to persisted account IDs and a revocable session version.
3. Require bearer sessions for pick writes; keep explicit development keys for
   local catalog/seed setup only when auth is unconfigured.
4. Make prediction creation match the board: open markets on scheduled/live games.
   Historical import is a separate future operation; preserve existing history.
5. Keep all 13 original definitions unresolved until authoritative event and price
   metadata is supplied. Archive strict legacy demo matches without changing terms.
6. Complete deterministic fixtures and separate QA result examples from product users.
7. Report priced settled ROI separately from pending exposure and missing prices.
8. Apply a localhost/Origin/session-token boundary to desktop mutations.
9. Fix UI claims/lint, regenerate clients, upgrade dependencies, add checks and CI.
10. Run focused and integrated tests; update handoff and acceptance evidence.

## Validation
API pytest; HTTP auth/privacy/ownership tests; seed idempotency/quarantine tests;
desktop unit and boundary tests; OpenAPI generation check; frontend lint/types/build;
dependency audit; isolated browser flows and migration validation where available.

## Surprises & Discoveries
The execution sandbox cannot start due to a host mount alias. Commands use the
approved escalation path. Existing .claude/skills changes are unrelated.

## Decision Log
- Public user selectors expose no email/country. Account and admin reads are protected.
- Deactivation/password changes revoke existing user sessions via session_version.
- New predictions require an open market and scheduled/live game; no implicit retrospective entry.
- Incomplete original seed definitions are never resolved from QA fixture names.
- Settled priced stake is the ROI denominator; pending exposure is separate.

## Outcomes & Retrospective
Paused at the user’s request on 2026-09-24. Phases 1–2 are implemented and covered by API tests. Phase 3 implementation is present; final browser acceptance and the last small edits need verification. See [checkpoint](../../checkpoints/2026-09-24-remediation.md) for exact results and ordered next steps. Deployment acceptance remains separate.
