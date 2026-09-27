# Checkpoint — Gato publication and previous-card review

Local date: 2026-09-26, America/Guatemala. Publication and verification occurred on 2026-09-27 UTC.

## Completed

- [x] Publish the ten entries from `picks09262026.md`, owned by `gato`.
- [x] Preserve original text, user-supplied lines and Over sides, source URLs, and card date `2026-09-26` in import metadata. Normalize misspelled names against official rosters/schedules.
- [x] Record missing odds as null and existing default stake as 1u, explicitly marked as defaulted. No invented historical odds snapshots.
- [x] Use ingestion time for `picked_at`; retain the supplied card date separately. All results remain pending until final statistics are verified.
- [x] Run production preview, apply, public verification, and repeated preview (zero new records).
- [x] Archive only six untouched legacy fixture matches, preserving their data and all original definitions.
- [x] Verify public visibility without login on desktop and mobile.

## Deployment evidence

Code commit: `53c75c5`, including remediation checkpoint `32104bb`.

| Service | Railway deployment | Public URL |
|---|---|---|
| API | `842e1573-9723-4068-b539-5389c8370de5` | https://dgn-picks-production.up.railway.app |
| Web | `c06c4b15-436b-4aef-a9f7-52582f60499d` | https://dgnweb-production.up.railway.app/ |

Both services built successfully from a clean archive of tracked files and served the new behavior. The repaired migration wrapper no longer drops `pick_legs.odds_snapshot_id`; forward revision `0011_restore_pick_leg_snapshot` repairs installations missing that column. This is not a claim of a completed production downgrade/restore rehearsal.

GitHub rejected `git push origin main`: the OAuth token lacks `workflow` scope for `.github/workflows/validate.yml`. The tested release was uploaded directly to Railway. GitHub synchronization and remote CI remain outstanding; do not treat GitHub's old revision as this deployed release.

## Data evidence

- Owner: `gato`, production user ID **7**.
- Batch: `gato-2026-09-26`; ten pick IDs **8–17**, in manifest order, across eight games.
- Public `/api/v1/picks?user=gato`: **10 active picks**, all belonging to Gato, all with unknown odds and the supplied card date.
- Public owner summary: **10 pending**, **10.000 pending units**, zero settled results; profit and ROI unavailable.
- Repeat import preview: ten existing matches, **zero would-create** entries.
- Legacy preview and apply: eligible/archived IDs **1, 3, 4, 5, 6, 7**; no ambiguous records. The original 13 definitions remain public and unresolved.
- A pre-quarantine public-record snapshot was saved outside the repository at `/tmp/dgn-gato-before-quarantine.json`; this temporary file is not a durable full-database backup. Archival retains the records in the database.

## Validation

- [x] API: **105 passed**, including import rules, operator authorization, owner analytics, and migration repair.
- [x] Actual-manifest isolated rehearsal: ten picks, eight games, unknown odds, no new snapshots, and repeatability.
- [x] Generated OpenAPI/client consistency check passed.
- [x] Complete migration SQL executed on disposable PostgreSQL 18 through revision `0011_restore_pick_leg_snapshot`.
- [x] Web lint, standalone TypeScript, and production build passed; both Railway builds succeeded.
- [x] Read-only Playwright `e2e/public-import.spec.ts`: **1 passed** against the deployed web; checks both 1440×1000 and 390×844 views, all ten rows, card date, unknown-odds labels, selected-owner summary, and absence of anonymous edit controls.
- [x] Screenshots saved locally under ignored `apps/web/test-results/gato-import-1440.png` and `gato-import-390.png`.
- [ ] Wider isolated authenticated/desktop browser acceptance remains open; the public test does not establish those flows.

## Next steps requiring additional facts

- [ ] Get original-card event dates/jornada or opponents and Malakai Toney's side, then grade from official final results. See the [per-pick review](../data-reviews/2026-09-26-gato-picks.md).
- [ ] Verify final statistics for the newly imported card before grading it; roster/schedule citations establish identity and event only.
- [ ] Complete the wider acceptance suite, restore GitHub synchronization, and verify remote CI.
