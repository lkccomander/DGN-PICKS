# Ops Console Configuration Design

## Purpose

Add a Configuration tab to the DGN-PICKS desktop Ops Console so the local
operator can inspect, validate, save, and apply the desktop and local API
environment variables required to operate user administration.

## Scope

The tab manages these desktop variables:

- `DGN_OPS_API_URL`
- `DGN_OPS_PORT`
- `DGN_OPS_DEBUG`
- `GRAPHIFY_COMMAND`

It also manages the local API variables:

- `DATABASE_URL`
- `DGN_AUTH_SECRET`
- `DGN_AUTH_USERNAME`
- `DGN_AUTH_PASSWORD`
- `DGN_AUTH_ROLE`
- `DGN_CORS_ORIGINS`
- `DGN_API_WRITE_MODE`
- `DGN_API_WRITE_KEY`

It provides an explicit API health check and explicit actions to start and stop
the local FastAPI process. It does not read, alter, or expose Railway variables,
database records, Git credentials, or the desktop user-management token.

## Storage and security

Values persist as user-scoped Windows environment variables. The app never
writes a `.env` file and never stores configuration in source control.

Secret variables are `DGN_AUTH_SECRET`, `DGN_AUTH_PASSWORD`, and
`DGN_API_WRITE_KEY`. The desktop backend returns only a `configured` boolean
for these values. The browser UI uses password fields and sends a secret only
when an operator supplies a replacement. Empty secret input retains the
existing persisted value. There is no UI operation to reveal a stored secret.

`DATABASE_URL` is also rendered as an obscured password field because it may
contain database credentials. It follows the same replace-only rule.

## Interaction model

The new tab shows two forms.

**Desktop connection** shows the effective API URL, console port, debug flag,
and Graphify command. Saving makes a new desktop process inherit the values;
the current web server keeps its current port until the desktop application is
restarted. The URL must be a credential-free `http` or `https` origin.

**Local API** shows non-secret values and a configured/not-configured state for
secret values. A local API is configured only when it has an absolute
`DATABASE_URL`, a signing secret, an operator username/password, and an allowed
role (`admin` or `editor`). Development write mode requires a write key.

The operator can choose **Test connection** to call `<DGN_OPS_API_URL>/api/health`.
The response reports the exact target and whether its network/HTTP check passed.
The operator can choose **Start local API** only when the configuration validates;
the desktop launches `python -m uvicorn dgn_picks_api.main:app --app-dir
apps/api/src --port <port>` without a shell. The configuration is injected only
into that child process. The application tracks the child PID, reports output,
and allows **Stop local API** for that exact owned process. It never terminates an
arbitrary process that happens to use the API port.

## Error handling

Validation errors identify the field and leave unsaved form contents intact.
Saving environment variables returns a restart notice. A failed health check
returns connection-refused, timeout, TLS, invalid response, or non-success HTTP
status detail. Starting an API when another listener owns the requested port is
rejected with a readable explanation.

## Tests

Flask tests cover redacted secret status, replacement-only secrets, validation,
health-check success/failure, child command construction, start/stop ownership,
and no shell invocation. Browser tests cover the Configuration tab, saving a
non-secret variable, redacted secret state, invalid URL display, and health check
feedback. Tests never write user environment variables, start real API processes,
or contact Railway.

## Decision log

- 2026-09-17: configuration is user-scoped Windows environment state, not a
  project `.env` file, because this desktop tool is intended for a local
  operator and must not put credentials in the repository.
- 2026-09-17: secrets are replace-only and are never returned to the renderer.
- 2026-09-17: API lifecycle controls manage only a process spawned by the Ops
  Console; they do not control external deployments or unknown local processes.
