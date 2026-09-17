(() => {
  const el = (id) => document.getElementById(id);
  const secretFields = [
    ['DATABASE_URL', 'config-database-url', 'config-database-url-state'],
    ['DGN_AUTH_SECRET', 'config-auth-secret', 'config-auth-secret-state'],
    ['DGN_AUTH_PASSWORD', 'config-auth-password', 'config-auth-password-state'],
    ['DGN_API_WRITE_KEY', 'config-write-key', 'config-write-key-state'],
  ];
  let busy = false;
  let poll = null;

  function message(text, error = false) {
    el('configuration-message').textContent = text;
    el('configuration-message').className = `configuration-notice ${error ? 'text-danger' : 'text-success'}`;
  }
  function setBusy(value) {
    busy = value;
    el('configuration-pane').querySelectorAll('button, input, select').forEach((node) => { node.disabled = value; });
  }
  async function requestConfig(path = '', method = 'GET', body) {
    const response = await fetch(`/api/configuration${path}`, { method, cache: 'no-store', signal: AbortSignal.timeout(20000), headers: body ? { 'Content-Type': 'application/json' } : {}, ...(body ? { body: JSON.stringify(body) } : {}) });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'No se pudo completar la operación.');
    return data;
  }
  function render(data) {
    const desktop = data.desktop || {};
    const api = data.api || {};
    el('config-api-url').value = desktop.DGN_OPS_API_URL || '';
    el('config-ops-port').value = desktop.DGN_OPS_PORT || '';
    el('config-ops-debug').checked = Boolean(desktop.DGN_OPS_DEBUG);
    el('config-graphify-command').value = desktop.GRAPHIFY_COMMAND || '';
    el('config-auth-username').value = api.DGN_AUTH_USERNAME || '';
    el('config-auth-role').value = api.DGN_AUTH_ROLE || 'admin';
    el('config-cors-origins').value = api.DGN_CORS_ORIGINS || '';
    el('config-write-mode').value = api.DGN_API_WRITE_MODE || 'disabled';
    secretFields.forEach(([name, field, state]) => {
      el(field).value = '';
      el(state).textContent = api[name]?.configured ? 'Configurada' : 'No configurada';
    });
    const local = data.local_api || {};
    el('local-api-status').textContent = local.running ? `API local activa · PID ${local.pid}` : 'Sin proceso administrado.';
    el('configuration-process-output').textContent = local.output || 'Sin salida de proceso.';
    el('local-api-start').disabled = busy || Boolean(local.running);
    el('local-api-stop').disabled = busy || !local.running;
    if (local.running && !poll) poll = window.setInterval(() => void load(), 2500);
    if (!local.running && poll) { window.clearInterval(poll); poll = null; }
  }
  async function load() {
    try { render(await requestConfig()); }
    catch (error) { message(error instanceof Error ? error.message : 'No se pudo cargar la configuración.', true); }
  }
  async function action(work) {
    if (busy) return;
    setBusy(true); message('');
    try { await work(); }
    catch (error) { message(error instanceof Error ? error.message : 'Error de conexión.', true); }
    finally { setBusy(false); }
  }
  function payload() {
    const api = {
      DGN_AUTH_USERNAME: el('config-auth-username').value.trim() || null,
      DGN_AUTH_ROLE: el('config-auth-role').value,
      DGN_CORS_ORIGINS: el('config-cors-origins').value.trim() || null,
      DGN_API_WRITE_MODE: el('config-write-mode').value,
    };
    secretFields.forEach(([name, field]) => { if (el(field).value) api[name] = el(field).value; });
    return { desktop: { DGN_OPS_API_URL: el('config-api-url').value.trim(), DGN_OPS_PORT: el('config-ops-port').value.trim(), DGN_OPS_DEBUG: el('config-ops-debug').checked, GRAPHIFY_COMMAND: el('config-graphify-command').value.trim() }, api };
  }
  el('desktop-settings-form').addEventListener('submit', (event) => {
    event.preventDefault();
    void action(async () => { const data = await requestConfig('', 'PATCH', payload()); render(data.configuration); message(data.message); });
  });
  el('configuration-test-connection').addEventListener('click', () => void action(async () => {
    const data = await requestConfig('/test-connection', 'POST', { url: el('config-api-url').value.trim() });
    message(`API disponible: ${data.target} (HTTP ${data.status}).`);
  }));
  el('local-api-start').addEventListener('click', () => void action(async () => { const data = await requestConfig('/local-api/start', 'POST', {}); message(`API local iniciada (PID ${data.pid}).`); await load(); }));
  el('local-api-stop').addEventListener('click', () => void action(async () => { const data = await requestConfig('/local-api/stop', 'POST', {}); message(data.message); await load(); }));
  load();
})();
