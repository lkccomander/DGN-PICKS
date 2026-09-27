# DGN-PICKS — session handoff

Updated: 2026-09-26 (America/Guatemala; verified 2026-09-27 UTC). **The ten requested Gato picks are published and verified anonymously on desktop and mobile.**

See the [publication checkpoint](docs/checkpoints/2026-09-26-gato-publication.md) for deployment and import evidence, and the [source/evaluation review](docs/data-reviews/2026-09-26-gato-picks.md) for every new and prior pick. The [project recap](PROJECT-RECAP.md) retains the original audit beneath its current progress checklist.

## Completed phases

- [x] Phase 1: API privacy, revocable sessions, ownership, and new-pick eligibility fixes.
- [x] Phase 2: unresolved seed definitions, reversible legacy quarantine, and accurate settled analytics.
- [x] Phase 3 implementation: desktop request boundary, protected account UI, dependency updates, generated clients, and CI definition.
- [x] Current validation: 105 API tests; web lint, TypeScript, build, and generated-client check passed. Desktop: 18 tests passed at the prior checkpoint; unchanged in this import.
- [x] Migration SQL through `0011_restore_pick_leg_snapshot` executed on disposable PostgreSQL 18; forward repair deployed with the API.
- [x] Publication: tested commit `53c75c5` deployed directly to Railway API and web.
- [x] Import: ten picks (IDs 8–17) assigned to `gato` (ID 7); supplied lines/date retained, odds unknown, default stake 1u each. Repeat preview creates zero duplicates.
- [x] Integrity cleanup: six strict legacy fixture records (1, 3, 4, 5, 6, 7) archived reversibly. All 13 original definitions preserved.
- [x] Public acceptance: Playwright passed on 1440px and 390px viewports without authentication. API summary confirms ten pending picks and 10u pending exposure.

## Next steps

- [ ] Obtain the date/jornada or opponent of the original 13 picks, plus Over/Under for Malakai Toney 72.5 receiving yards; then verify official results and grade each. All were reviewed; none can yet be graded from the supplied facts.
- [ ] Verify final statistics and participation for the new card before grading; missing taken odds must stay unknown.
- [ ] Run the wider isolated browser journeys (registration, protected account, pick creation/editing, stored-price history, desktop console) and close the [remediation plan](docs/exec-plans/active/2026-09-24-audit-remediation.md).
- [ ] Sync local `main` to GitHub using authentication permitted to update workflow files. The existing OAuth token rejected the push because it lacks `workflow` scope; local commits and the tested Railway deployment are intact.
- [ ] Run and verify GitHub CI after synchronization. Remote CI has not run for these commits.
- [ ] Later milestones: virtual-token ledger; live provider and CLV. No live odds provider is connected.

## Deployment context

Frontend: https://dgnweb-production.up.railway.app/
API: https://dgn-picks-production.up.railway.app

The usual workflow is GitHub → Railway. This release used a clean Git archive uploaded directly to Railway because the GitHub push was rejected. Reconcile GitHub before the next Git-triggered release.
Preserve unrelated `.claude/skills` worktree changes and the original untracked `picks09262026.md`.
