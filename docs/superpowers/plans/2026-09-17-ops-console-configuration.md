# Ops Console Configuration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a secure Configuration tab to the desktop Ops Console that manages desktop and local API environment variables, tests API connectivity, and controls only the local API process it starts.

**Architecture:** `ext-tools/configuration.py` owns user-environment access, validation, connection checks, and local API lifecycle behind a Flask blueprint. The renderer receives non-secret values and secret configured-state only through `/api/configuration` endpoints. A tracked `subprocess.Popen` instance is the only process that can be stopped.

**Tech Stack:** Python 3.14, Flask 3, pywebview, standard-library `subprocess` and `winreg`, CoreUI Bootstrap 5, vanilla JavaScript, `unittest`.

## Global Constraints

- Preserve the DGN-PICKS brand stripe and existing desktop visual language.
- Persist only user-scoped Windows environment variables; never write `.env` or source-controlled configuration.
- Never return, log, render, test-print, or persist secret values in browser storage.
- Manage desktop: `DGN_OPS_API_URL`, `DGN_OPS_PORT`, `DGN_OPS_DEBUG`, `GRAPHIFY_COMMAND`.
- Manage local API: `DATABASE_URL`, `DGN_AUTH_SECRET`, `DGN_AUTH_USERNAME`, `DGN_AUTH_PASSWORD`, `DGN_AUTH_ROLE`, `DGN_CORS_ORIGINS`, `DGN_API_WRITE_MODE`, `DGN_API_WRITE_KEY`.
- Use argument-list subprocesses with `shell=False`; terminate only the process created by this desktop session.

---

### Task 1: Secure configuration blueprint

**Files:**

- Create: `ext-tools/configuration.py`
- Create: `ext-tools/test_configuration.py`
- Modify: `ext-tools/app.py`

**Interfaces:**

- Produces: `GET/PATCH /api/configuration`.
- Returns non-secret values and `{ "configured": bool }` for `DATABASE_URL`, `DGN_AUTH_SECRET`, `DGN_AUTH_PASSWORD`, and `DGN_API_WRITE_KEY`.

- [ ] **Step 1: Write the failing read/redaction test**

```python
def test_configuration_redacts_all_secrets():
    with patch("configuration.read_user_environment", return_value={
        "DGN_OPS_API_URL": "https://api.example.test",
        "DATABASE_URL": "postgresql://operator:secret@db.example/test",
        "DGN_AUTH_SECRET": "signing-secret",
        "DGN_AUTH_PASSWORD": "operator-password",
        "DGN_API_WRITE_KEY": "write-key",
    }):
        response = app.test_client().get("/api/configuration")

    assert response.status_code == 200
    assert response.json["desktop"]["DGN_OPS_API_URL"] == "https://api.example.test"
    assert response.json["api"]["DATABASE_URL"] == {"configured": True}
    assert "secret" not in str(response.json)
    assert "operator-password" not in str(response.json)
```

- [ ] **Step 2: Run it to verify failure**

Run: `C:\Projects\DGN-PICKS\ext-tools\.venv\Scripts\python.exe -m unittest test_configuration.ConfigurationReadTests.test_configuration_redacts_all_secrets -v`

Expected: FAIL because `configuration.py` does not exist.

- [ ] **Step 3: Implement the read model**

Create `configuration.py` with `configuration_api = Blueprint("configuration_api", __name__)`. Define `DESKTOP_FIELDS`, `API_FIELDS`, and `SECRET_FIELDS`. Implement `read_user_environment()` via `winreg.HKEY_CURRENT_USER\Environment`; absent values return `None`. Implement `read_configuration()` with defaults `http://127.0.0.1:8000`, `5178`, `false`, and `graphify`; secrets return only configured booleans. Register the blueprint in `app.py` after `users_api`.

- [ ] **Step 4: Run the read tests**

Run: `C:\Projects\DGN-PICKS\ext-tools\.venv\Scripts\python.exe -m unittest test_configuration.ConfigurationReadTests -v`

Expected: PASS.

- [ ] **Step 5: Write failing validation and replace-only-secret tests**

```python
def test_save_rejects_credentialed_api_url():
    response = app.test_client().patch("/api/configuration", json={
        "desktop": {"DGN_OPS_API_URL": "https://operator:password@api.example.test"},
    })
    assert response.status_code == 422
    assert "DGN_OPS_API_URL" in response.json["detail"]


@patch("configuration.write_user_environment")
def test_save_replaces_only_nonblank_secrets(write_user_environment):
    response = app.test_client().patch("/api/configuration", json={
        "api": {"DGN_AUTH_SECRET": "", "DGN_AUTH_PASSWORD": "new-password"},
    })
    assert response.status_code == 200
    write_user_environment.assert_called_once_with({"DGN_AUTH_PASSWORD": "new-password"})
```

- [ ] **Step 6: Implement save validation and persistence**

Implement `validate_configuration_patch(payload)`. Reject unknown fields, non-object sections, credentials/query/fragment in API URLs, ports outside `1024..65535`, non-booleans for debug, roles outside `admin`/`editor`, write modes outside `disabled`/`development`, and development mode without a current or replacement write key. Save only supplied non-empty secrets; explicit `null` clears non-secret fields. `write_user_environment()` uses `winreg.SetValueEx` and broadcasts `WM_SETTINGCHANGE` for `Environment`. Return redacted state and a restart notice.

- [ ] **Step 7: Run validation tests**

Run: `C:\Projects\DGN-PICKS\ext-tools\.venv\Scripts\python.exe -m unittest test_configuration.ConfigurationSaveTests -v`

Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add ext-tools/configuration.py ext-tools/test_configuration.py ext-tools/app.py
git commit -m "feat: add secure ops configuration backend"
```

### Task 2: Connection test and owned local API process

**Files:**

- Modify: `ext-tools/configuration.py`
- Modify: `ext-tools/test_configuration.py`

**Interfaces:**

- Produces: `POST /api/configuration/test-connection`, `POST /api/configuration/local-api/start`, and `POST /api/configuration/local-api/stop`.

- [ ] **Step 1: Write failing connection tests**

```python
@patch("configuration.urlopen")
def test_connection_check_reports_healthy_target(urlopen):
    urlopen.return_value.__enter__.return_value.status = 200
    urlopen.return_value.__enter__.return_value.read.return_value = b'{"status":"ok"}'
    response = app.test_client().post("/api/configuration/test-connection", json={"url": "https://api.example.test"})
    assert response.status_code == 200
    assert response.json == {"ok": True, "target": "https://api.example.test/api/health", "status": 200}


@patch("configuration.urlopen", side_effect=URLError("connection refused"))
def test_connection_check_reports_network_failure(_):
    response = app.test_client().post("/api/configuration/test-connection", json={"url": "http://127.0.0.1:8000"})
    assert response.status_code == 502
    assert response.json["ok"] is False
```

- [ ] **Step 2: Run connection tests to verify failure**

Run: `C:\Projects\DGN-PICKS\ext-tools\.venv\Scripts\python.exe -m unittest test_configuration.ConnectionTests -v`

Expected: FAIL because the connection route does not exist.

- [ ] **Step 3: Implement bounded health testing**

Use `urlopen(Request(f"{base}/api/health", headers={"Accept": "application/json"}), timeout=8)`. Return `ok`, credential-free `target`, and status only for a 2xx JSON response. Convert HTTP, connection, timeout, TLS, and malformed JSON failures into redacted JSON 502 responses.

- [ ] **Step 4: Write failing owned-process tests**

```python
@patch("configuration.subprocess.Popen")
def test_start_api_uses_argument_list_and_safe_environment(popen):
    popen.return_value.pid = 4242
    response = app.test_client().post("/api/configuration/local-api/start")
    assert response.status_code == 202
    assert popen.call_args.args[0] == [sys.executable, "-m", "uvicorn", "dgn_picks_api.main:app", "--app-dir", "apps/api/src", "--port", "8000"]
    assert popen.call_args.kwargs["shell"] is False
    assert response.json["pid"] == 4242


def test_stop_does_not_target_an_unowned_process():
    response = app.test_client().post("/api/configuration/local-api/stop")
    assert response.status_code == 409
```

- [ ] **Step 5: Implement lifecycle controller**

Track `local_api_process` behind a module lock. Validate all required local API variables before launching. Invoke `subprocess.Popen` with `sys.executable`, `cwd=ROOT`, merged child environment, `stdout=PIPE`, `stderr=STDOUT`, `text=True`, `shell=False`, and Windows `CREATE_NEW_PROCESS_GROUP`. Drain output in a daemon thread, keeping only 4,000 redacted characters. Stop only the tracked, still-running child with `terminate()`; never discover or kill processes by port/PID.

- [ ] **Step 6: Run lifecycle tests**

Run: `C:\Projects\DGN-PICKS\ext-tools\.venv\Scripts\python.exe -m unittest test_configuration.ConnectionTests test_configuration.LocalApiProcessTests -v`

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add ext-tools/configuration.py ext-tools/test_configuration.py
git commit -m "feat: manage local api from ops console"
```

### Task 3: Configuration tab

**Files:**

- Create: `ext-tools/templates/configuration.html`
- Create: `ext-tools/static/configuration.js`
- Modify: `ext-tools/templates/index.html`
- Modify: `ext-tools/static/style.css`
- Modify: `ext-tools/test_users_api.py`

**Interfaces:**

- Consumes: all five routes from Tasks 1–2.
- Produces: `#configuration-tab` and `#configuration-pane`; no browser secret persistence.

- [ ] **Step 1: Write the failing page-integration test**

```python
def test_desktop_page_includes_configuration_assets():
    response = app.test_client().get("/")
    assert response.status_code == 200
    assert b'id="configuration-tab"' in response.data
    assert b'id="configuration-pane"' in response.data
    assert b"configuration.js" in response.data
```

- [ ] **Step 2: Run it to verify failure**

Run: `C:\Projects\DGN-PICKS\ext-tools\.venv\Scripts\python.exe -m unittest test_users_api.UsersBridgeTests.test_desktop_page_includes_configuration_assets -v`

Expected: FAIL because the tab and asset do not exist.

- [ ] **Step 3: Add accessible template markup**

Add the tab after Users and include `configuration.html`. The pane has desktop and API forms, visible labels for every variable, password inputs and configured-state labels for secrets, `#configuration-test-connection`, `#local-api-start`, `#local-api-stop`, `#configuration-message` with `role="status"`, and `#configuration-process-output`. Explain: “Los secretos guardados no se muestran. Déjalo vacío para conservarlo.”

- [ ] **Step 4: Implement browser behavior**

Load the redacted GET state; populate non-secret inputs only. PATCH sends desktop/API sections and omits blank secret fields. Use `textContent` for all feedback. Test the currently typed URL, not only saved state. Start/stop uses explicit endpoints and polls state each 2.5 seconds while an owned process runs. Do not use `localStorage`, `sessionStorage`, `innerHTML`, or dynamic script insertion.

- [ ] **Step 5: Style and verify the tab**

Add `.configuration-grid`, `.configuration-secret-state`, `.configuration-process-output`, and `.configuration-notice`, reusing navy/blue/red/muted values and responsive single-column behavior. Add visible `:focus-visible` states.

- [ ] **Step 6: Run interface and backend tests**

Run: `C:\Projects\DGN-PICKS\ext-tools\.venv\Scripts\python.exe -m unittest test_users_api test_configuration -v`

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add ext-tools/templates/configuration.html ext-tools/static/configuration.js ext-tools/templates/index.html ext-tools/static/style.css ext-tools/test_users_api.py
git commit -m "feat: add ops configuration tab"
```

### Task 4: Documentation and final validation

**Files:**

- Modify: `ext-tools/README.md`
- Modify: `docs/product-specs/001-local-mvp.md`

**Interfaces:**

- Produces: accurate operator setup and decision history.

- [ ] **Step 1: Document operator behavior**

Document user-scoped Windows persistence, restart requirement after desktop port/API URL change, replace-only secrets, API lifecycle ownership, and Railway exclusion.

- [ ] **Step 2: Update the product decision log**

Append:

```markdown
- 2026-09-17: Ops Console configuration persists only user-scoped desktop and local API environment variables; secrets are replace-only and never returned to the UI. Local API lifecycle controls manage only processes spawned by the console.
```

- [ ] **Step 3: Run complete verification**

Run: `C:\Projects\DGN-PICKS\ext-tools\.venv\Scripts\python.exe -m unittest discover -v`

Expected: PASS.

Run: `C:\Projects\DGN-PICKS\ext-tools\.venv\Scripts\python.exe -m compileall -q .`

Expected: exit code 0.

Run: `git diff --check`

Expected: exit code 0.

- [ ] **Step 4: Manually verify without changing a secret**

Run: `$env:DGN_OPS_BROWSER = "1"; C:\Projects\DGN-PICKS\ext-tools\.venv\Scripts\python.exe app.py`

Expected: the Configuration pane shows redacted secret state, invalid URL feedback, the active API URL, and an API health result. Do not save a real secret in this check.

- [ ] **Step 5: Commit**

```bash
git add ext-tools/README.md docs/product-specs/001-local-mvp.md
git commit -m "docs: explain ops configuration"
```

## Self-review

- Spec coverage: Tasks 1–2 cover persistence, redaction, validation, connectivity, and process ownership; Task 3 covers the tab; Task 4 covers docs and verification.
- Placeholder scan: no placeholders or unspecified route contracts remain.
- Type consistency: every browser operation maps to a defined route and secret names remain identical in validation, UI, tests, and docs.
