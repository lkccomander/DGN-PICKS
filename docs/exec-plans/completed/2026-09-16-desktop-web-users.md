# Desktop and web user CRUD

## Purpose
Complete user management in the desktop Ops Console and web admin, as approved by the user.

## Scope / Non-scope
Reuse `/api/v1/users` and operator authentication. List/search, create, edit profile/password, activate/deactivate and confirmed deletion. Preserve pick ownership and reject deletion of users with picks. No new account roles, database access from desktop, deployment or changes to other catalog semantics.

## Design
Desktop gains a Users tab matching its existing dark CoreUI layout, with an authenticated form and searchable table. A narrow Flask proxy forwards only login and user endpoints to `DGN_OPS_API_URL` (local API by default), with timeouts and structured errors. The operator token stays in memory in the desktop window. Web completes its existing authenticated admin rather than adding a competing screen. Blank password on edit preserves credentials; blank optional profile fields clear them; username stays immutable on edit.

## Progress
- [x] Inspect API, desktop and existing web administration.
- [x] User approved the design and explicitly included web.
- [x] Implement and test the desktop API bridge and interface.
- [x] Complete web CRUD and error handling.
- [x] Verify API rules, desktop flows and web build; document configuration.

## Implementation plan
1. Add `ext-tools/users_api.py`, register its blueprint in `app.py`, and test with Flask's test client and mocked HTTP transport. Cover authorization forwarding, CRUD methods, conflicts, validation and unavailable upstream.
2. Add the Users tab/template and isolated `static/users.js`: login/logout, list/search, create/edit, activation, deletion confirmation and persistent inline errors. Render user text through `textContent`.
3. Complete `apps/web/src/app/admin/page.tsx` with the isolated `users-panel.tsx` component: searchable Users entry, immutable username, nullable profile updates, password preservation, operation locks, loading and error states. Keep failed deletes visible.
4. Handle duplicate email on API update with rollback/409 and test CRUD integrity; reject explicit null for non-nullable update fields.
5. Run isolated desktop tests, API tests and web build; exercise both interfaces with deterministic fixtures, without mutating live users.

## Validation
Desktop unittest tests mock the remote API; API tests use an in-memory database. Web browser checks use intercepted deterministic responses. Build checks TypeScript and integration.

## Surprises & Discoveries
The working tree already contains account authentication and a generic web Users tab. Preserve those changes. The current web delete handler clears errors by reloading immediately. Empty profile fields are omitted from PATCH; duplicate email updates currently escape as database errors.

## Decision Log
Reuse existing admin/editor authorization and backend deletion rules. Desktop uses a configured API origin, never direct database writes or a new credential store. Username remains fixed after creation, matching UserUpdate.

## Outcomes & Retrospective
Completed 2026-09-17. Desktop and web share user operations through the existing API; no deployment or live user mutations were performed.

- Desktop bridge: 8 unittest tests passed.
- Users/authentication API: 14 pytest tests passed, including regression tests first observed failing for duplicate email and explicit null updates.
- Browser: full deterministic CRUD workflow passed independently for desktop and web, including search, nullable profile fields, password preservation, deactivation, deletion cancellation/confirmation, pick conflict and network failure recovery. Web screenshot inspected.
- Web production build passed; git diff --check passed.
- Full API suite: 66 passed, 5 failed outside the changed user flow. Four older pick tests call route functions without the newly introduced identity dependency from the pre-existing account work. The health test assumes every app.routes entry has a path; the installed FastAPI includes _IncludedRouter entries.
- Environment: the API .venv is configured for WSL; Windows py has the API test dependencies. Desktop uses its own Windows .venv. Sandbox file operations failed repeatedly, so authorized elevated commands were used. The missing Playwright Chromium shell was installed; installed Edge could not launch in automation.
- Temporary browser reports are ignored by Git; the optional E2E_BROWSER_CHANNEL supports installed browsers.

