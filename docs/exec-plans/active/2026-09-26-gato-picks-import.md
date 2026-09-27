# Gato picks import and prior-card review — 2026-09-26

## Purpose
Add all ten entries supplied in picks09262026.md to gato and show them publicly; evaluate previous picks only where real event and result evidence can support grading.

## Scope / Non-scope
Import verified event/player associations with user-supplied lines and unknown odds. Preserve original input and citations. Use the existing 1u tracking default when stake is not supplied. No sportsbook connection or fictional historical prices/results. Publishing these requested picks is authorized by the user.

## Progress
- [x] Read source file and source-of-truth docs; inspect public API state.
- [x] Resolve ten player identities and eight events against official team sources.
- [x] Add idempotent manual-import service, provenance, and forward migration.
- [ ] Restore reliable deployment migrations and public pick reads.
- [ ] Import new picks for gato and verify public dashboard display.
- [ ] Evaluate all prior picks; request event/date/side facts where absent.

## Implementation plan
1. Version the normalized manifest beside the original source; preserve original spelling.
2. Import into normal owned picks through a dedicated operator CLI with explicit apply and uniqueness guard. Preserve supplied taken lines, leave odds null, create no odds history.
3. Display imported dates/provenance and accurate missing-price labels on the public board; scope summary to selected user.
4. Verify critical domain rules, repeatability and browser visibility on isolated fixtures, then apply targeted production changes and verify.
5. Record what was imported/graded and why any earlier pick cannot yet be graded.

## Validation
105 API tests passed. Actual ten-entry manifest rehearsal produced ten Gato picks across eight games with null odds and no new snapshots; repeat created zero. Full upgrade SQL executed on disposable PostgreSQL 18 through 0011. Frontend lint/types/build passed. Public API and browser acceptance pending publication.

## Surprises & Discoveries
Public /picks?user=gato returned HTTP500 while health and games worked. Existing deployed events are synthetic fixtures and cannot establish real prior pick outcomes. The previous migration wrapper drops a historical column on repeated deployments and needs a forward repair.

## Decision Log
- Manual imports represent user-supplied historical/external picks; they preserve lines directly and do not relax eligibility for new predictions.
- Normalized names are source-backed matches to misspellings; retain original text and source URLs.
- Missing price data remains null; settled result evidence is required before grading.
- Earlier original definitions have no authoritative event date/opponent. Await these facts instead of grading against QA fixture scores.

## Outcomes & Retrospective
In progress.
