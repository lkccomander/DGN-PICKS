# Ops Console user list

## Purpose
Make user management a list-first view with all available account fields and CRUD controls.

## Scope / Non-scope
Desktop user list, editor visibility, search/filter and existing CRUD browser checks.
No API or account semantics change. Secrets and password hashes remain excluded.

## Progress
- [x] Inspect user API and desktop controls.
- [x] Add separate columns, creation date, list toolbar and expandable editor.
- [x] Validate and document.

## Implementation plan
Display ID, username, display name, email, country, active state and creation time
in UTC. Open the editor from New/Edit and preserve existing CRUD behavior.
Search across profile fields and filter by active state. Provide empty-list feedback.

## Validation
Desktop unit suite, JavaScript syntax, and existing CRUD browser journey with
additional assertions for full columns, creation date, country search and state filter.

## Surprises & Discoveries
The previous table grouped profile fields together and omitted creation dates.
The admin API already supplies all required fields.

## Decision Log
Keep the same authenticated API and CRUD rules; present existing fields in a table.

## Outcomes & Retrospective
All 29 desktop unit tests passed. JavaScript syntax and whitespace checks passed.
The Chromium desktop browser test passed the complete create/search/edit/deactivate/
delete journey, including rejected deletion and connection failure recovery.
Additional checks verified all eight columns, UTC date, country search and state
filter. Reviewed the browser screenshot. API users were intercepted fixtures; no
real accounts were modified. The native Windows pywebview shell was not launched.
