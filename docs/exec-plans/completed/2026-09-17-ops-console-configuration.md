# Ops Console Configuration

## Purpose

Let the desktop Ops Console configure its API connection and local API runtime
without leaving connection details hidden in a PowerShell session.

## Scope / Non-scope

Implemented a desktop Configuration tab for the documented desktop and local
API environment variables, connection health checks, and lifecycle controls for
the API process started by the console. Railway configuration, database records,
Git credentials, and unowned local processes remain out of scope.

## Progress

- [x] Define settings storage, redaction, validation, and lifecycle boundaries.
- [x] Add Flask configuration routes and user-scoped Windows persistence.
- [x] Add the desktop tab, forms, connection test, process controls, and styles.
- [x] Add focused configuration tests and documentation.
- [x] Verify remote API health without submitting credentials.

## Implementation plan

1. Persist non-secret and replace-only secret fields under the current Windows
   user environment registry key.
2. Return only configured-state metadata for database and authentication secrets.
3. Validate URL, port, role, write mode, and development write-key dependencies.
4. Restrict local API startup to a local API URL and track the child process in
   memory so only the console-owned process can be stopped.
5. Use the Windows Python launcher for Uvicorn because the desktop virtual
   environment intentionally contains only desktop dependencies.

## Validation

- `ext-tools` configuration and user bridge tests: 14 passed.
- Python syntax compilation passed.
- The configuration page rendered with its tab, pane, and script.
- The configured DGN-PICKS Railway health endpoint returned HTTP 200 through
  the new desktop connection test.
- `git diff --check` passed after normalizing edited file endings.

## Surprises & Discoveries

- The desktop virtual environment does not include Uvicorn; Windows `py -m
  uvicorn` is available and is used only to start the local API child process.
- The existing desktop instance requires restart before loading the new tab or a
  changed console port.

## Decision Log

- Keep secrets replace-only and never return them to the renderer.
- A local API cannot be started when `DGN_OPS_API_URL` targets Railway or another
  remote host, because it would not serve the selected desktop target.

## Outcomes & Retrospective

The desktop can now configure the variables needed for local and remote API
operation while keeping credentials out of the repository and UI responses.
