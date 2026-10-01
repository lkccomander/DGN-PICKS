const $ = (id) => document.getElementById(id);
let graphViewVersion = null;
let graphWasRunning = false;
let gitHistory = '';
let gitOperationOutput = '';

function renderGitConsole() {
  const console = $('git-output');
  console.textContent = [gitHistory.trimEnd(), gitOperationOutput].filter(Boolean).join('\n\n') || 'Sin consultas guardadas.';
  console.scrollTop = console.scrollHeight;
}

function showLastGitStatus(status) {
  $('git-last-status').textContent = status
    ? `Último estado: ${status.checked_at} · ${status.code === 0 ? 'Consulta correcta' : 'Error'} (exit ${status.code})`
    : 'Sin estado anterior guardado.';
}

async function loadGitLog() {
  try {
    const response = await desktopFetch('/api/git/log');
    const data = await response.json();
    if (!response.ok || !data.ok) throw new Error(data.message || 'No se pudo cargar el log.');
    gitHistory = data.output || '';
    showLastGitStatus(data.last_status);
  } catch (error) {
    $('git-last-status').textContent = error.message;
  }
  renderGitConsole();
}

function setDeployVisual(status, message) {
  const labels = { ready:'LISTO', failed:'FALLÓ', deploying:'EN PROGRESO', error:'ERROR', unlinked:'NO VINCULADO', unavailable:'NO DISPONIBLE', timeout:'TIMEOUT', idle:'SIN CONSULTAR' };
  const statusEl = $('deploy-status');
  statusEl.textContent = labels[status] || String(status || 'SIN CONSULTAR').toUpperCase();
  statusEl.className = 'deploy-status ' + (status || '');
  $('deploy-message').textContent = message || '';
  $('deploy-progress').style.width = status === 'ready' || status === 'failed' || status === 'error' ? '100%' : status === 'deploying' ? '62%' : '12%';
  if ($('menu-deploy-status')) $('menu-deploy-status').textContent = labels[status] || '—';
}

async function refreshState() {
  const response = await desktopFetch('/api/state');
  const data = await response.json();
  const git = data.git || {};
  const output = git.output || git.error || '';
  // Status checks are already in the history; polling must not duplicate them.
  if (!/^\[[^\]\n]+\] git status --short --branch \(exit -?\d+\)/.test(output)) {
    gitOperationOutput = output;
    renderGitConsole();
  }
  if (data.deploy) setDeployVisual(data.deploy.status, data.deploy.message);
  if (data.graph) {
    const running = Boolean(data.graph.running);
    $('graph-refresh').disabled = running;
    $('quick-graph-refresh').disabled = running;
    $('graph-operation').textContent = data.graph.message || '';
    if (graphWasRunning && !running) await loadGraph();
    graphWasRunning = running;
  }
}

async function gitStatus() {
  await gitLogReady;
  $('git-last-status').textContent = 'Consultando git…';
  try {
    const response = await desktopFetch('/api/git/status');
    const data = await response.json();
    if (!response.ok) throw new Error(data.message || 'No se pudo consultar Git.');
    gitHistory = gitHistory.trimEnd() + (gitHistory.trim() ? '\n\n' : '') + (data.output || data.message || 'Sin cambios.');
    showLastGitStatus({checked_at: data.checked_at, code: data.code});
  } catch (error) {
    $('git-last-status').textContent = error.message;
  }
  renderGitConsole();
}

async function pushChanges() {
  const button = $('git-push');
  button.disabled = true;
  gitOperationOutput = 'Iniciando commit y push…';
  renderGitConsole();
  const response = await desktopFetch('/api/git/push', {
    method: 'POST', headers: {'Content-Type':'application/json'},
    body: JSON.stringify({branch:$('branch').value, message:$('commit-message').value})
  });
  const data = await response.json();
  if (!data.ok) { gitOperationOutput = data.message; renderGitConsole(); }
  button.disabled = false;
}

async function refreshDeploy() {
  const response = await desktopFetch('/api/deploy/refresh', {method:'POST'});
  const data = await response.json();
  setDeployVisual(data.status, data.message);
}

async function loadGraph() {
  try {
    const response = await desktopFetch('/api/graph');
    const data = await response.json();
    const meta = data.meta || {};
    if (!response.ok || meta.error) throw new Error(meta.error || 'No se pudo cargar el grafo.');
    const nodes = (data.nodes || []).length;
    const edges = (data.links || data.edges || []).length;
    $('graph-meta').textContent = `${nodes} nodos · ${edges} relaciones · actualizado ${meta.updated_at || '—'}`;
    $('menu-graph-status').textContent = `${nodes} nodos`;
    const frame = $('graph-view');
    if (!meta.view_version) throw new Error('No existe la vista Graphify. Pulsa Actualizar grafo.');
    if (graphViewVersion !== meta.view_version) {
      frame.src = '/api/graph/view?v=' + encodeURIComponent(meta.view_version);
      graphViewVersion = meta.view_version;
    }
    frame.hidden = false;
    $('graph-empty').hidden = true;
  } catch (error) {
    $('graph-empty').textContent = error.message;
    $('graph-empty').hidden = false;
    $('graph-view').hidden = true;
  }
}

async function refreshGraph() {
  $('graph-refresh').disabled = true;
  $('quick-graph-refresh').disabled = true;
  $('graph-operation').textContent = 'Actualizando grafo…';
  try {
    const response = await desktopFetch('/api/graph/refresh', {method:'POST'});
    const data = await response.json();
    if (!response.ok || !data.ok) throw new Error(data.message || 'No se pudo actualizar el grafo.');
    graphWasRunning = true;
    await refreshState();
  } catch (error) {
    $('graph-operation').textContent = error.message;
    $('graph-refresh').disabled = false;
    $('quick-graph-refresh').disabled = false;
  }
}

$('git-status').addEventListener('click', gitStatus);
$('git-push').addEventListener('click', pushChanges);
$('deploy-refresh').addEventListener('click', refreshDeploy);
$('graph-refresh').addEventListener('click', refreshGraph);
$('quick-git-status').addEventListener('click', () => { document.querySelector('[data-coreui-target="#ship-pane"]').click(); gitStatus(); });
$('quick-deploy-refresh').addEventListener('click', () => { document.querySelector('[data-coreui-target="#ship-pane"]').click(); refreshDeploy(); });
$('quick-graph-refresh').addEventListener('click', () => { document.querySelector('[data-coreui-target="#graph-pane"]').click(); refreshGraph(); });
loadGraph();
const gitLogReady = loadGitLog();
gitLogReady.then(refreshState);
setInterval(refreshState, 2500);
setInterval(loadGraph, 8000);
