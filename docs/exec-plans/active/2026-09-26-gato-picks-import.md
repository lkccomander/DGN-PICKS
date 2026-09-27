# Gato picks import and prior-card review — 2026-09-26

## Purpose
Add all ten entries supplied in picks09262026.md to gato and show them publicly; evaluate previous picks only where real event and result evidence can support grading.

## Scope / Non-scope
Import verified event/player associations with user-supplied lines and unknown odds. Preserve original input and citations. Use the existing 1u tracking default when stake is not supplied. No sportsbook connection or fictional historical prices/results. Publishing these requested picks is authorized by the user.

## Progress
- [x] Read source file and source-of-truth docs; inspect public API state.
- [x] Resolve ten player identities and eight events against official team sources.
- [x] Add idempotent manual-import service, provenance, and forward migration.
- [x] Restore deployment migrations and public pick reads.
- [x] Import ten picks for gato and verify the public dashboard on desktop/mobile.
- [x] Review all 13 prior definitions, request missing facts, and archive six strict synthetic legacy matches.
- [ ] Grade the prior card once event/date/side facts and official final statistics are available.

## Implementation plan
1. Version the normalized manifest beside the original source; preserve original spelling.
2. Import into normal owned picks through a dedicated operator CLI with explicit apply and uniqueness guard. Preserve supplied taken lines, leave odds null, create no odds history.
3. Display imported dates/provenance and accurate missing-price labels on the public board; scope summary to selected user.
4. Verify critical domain rules, repeatability and browser visibility on isolated fixtures, then apply targeted production changes and verify.
5. Record what was imported/graded and why any earlier pick cannot yet be graded.

## Validation
105 API tests passed. Actual ten-entry manifest rehearsal produced ten Gato picks across eight games with null odds and no new snapshots; repeat created zero. Full upgrade SQL executed on disposable PostgreSQL 18 through 0011. Frontend lint/types/build passed. Production API verification and anonymous desktop/mobile browser acceptance passed (one read-only Playwright test). Repeat production preview found zero new records.

## Surprises & Discoveries
Public /picks?user=gato returned HTTP500 while health and games worked. Existing deployed events are synthetic fixtures and cannot establish real prior pick outcomes. The previous migration wrapper drops a historical column on repeated deployments and needs a forward repair.

## Decision Log
- Manual imports represent user-supplied historical/external picks; they preserve lines directly and do not relax eligibility for new predictions.
- Normalized names are source-backed matches to misspellings; retain original text and source URLs.
- Missing price data remains null; settled result evidence is required before grading.
- Earlier original definitions have no authoritative event date/opponent. Await these facts instead of grading against QA fixture scores.

## Outcomes & Retrospective
Published commit `53c75c5` directly to Railway after GitHub rejected the push for missing workflow scope. Gato owns ten imported picks (IDs 8–17); six synthetic records are reversibly archived and all 13 prior definitions remain. Public summary is ten pending picks / 10u. New-card publication is complete; prior-card grading awaits missing user facts. See the [publication checkpoint](../../checkpoints/2026-09-26-gato-publication.md) for exact evidence and remaining acceptance/synchronization tasks.
