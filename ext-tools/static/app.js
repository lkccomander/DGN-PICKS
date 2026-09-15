const $ = (id) => document.getElementById(id);
let graphInstance = null;

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
  const response = await fetch('/api/state');
  const data = await response.json();
  const git = data.git || {};
  $('git-output').textContent = git.output || git.error || 'Esperando una operación…';
  if (data.deploy) setDeployVisual(data.deploy.status, data.deploy.message);
  if (data.graph && data.graph.message) $('graph-meta').textContent = data.graph.message;
}

async function gitStatus() {
  $('git-output').textContent = 'Consultando git…';
  const response = await fetch('/api/git/status');
  const data = await response.json();
  $('git-output').textContent = data.output || data.message || 'Sin cambios.';
}

async function pushChanges() {
  const button = $('git-push');
  button.disabled = true;
  $('git-output').textContent = 'Iniciando commit y push…';
  const response = await fetch('/api/git/push', {
    method: 'POST', headers: {'Content-Type':'application/json'},
    body: JSON.stringify({branch:$('branch').value, message:$('commit-message').value})
  });
  const data = await response.json();
  if (!data.ok) $('git-output').textContent = data.message;
  button.disabled = false;
}

async function refreshDeploy() {
  const response = await fetch('/api/deploy/refresh', {method:'POST'});
  const data = await response.json();
  setDeployVisual(data.status, data.message);
}

function drawGraph(payload) {
  const rawNodes = payload.nodes || [];
  const rawEdges = payload.edges || [];
  if (graphInstance) graphInstance.destroy();
  graphInstance = cytoscape({
    container: $('graph-canvas'),
    elements: {
      nodes: rawNodes.map((n, i) => ({data:{id:String(n.id), label:n.label || n.id, type:n.file_type || 'concept'}, position:{x:80+(i%12)*105,y:80+Math.floor(i/12)*82}})),
      edges: rawEdges.map((e, i) => ({data:{id:'e'+i, source:String(e.source), target:String(e.target), label:e.relation || ''}}))
    },
    style: [
      {selector:'node',style:{'background-color':'#168cff','label':'data(label)','color':'#eaf5ff','font-size':8,'text-wrap':'ellipsis','text-max-width':90,'text-valign':'bottom','text-margin-y':6,'width':14,'height':14,'border-width':1,'border-color':'#a9d8ff'}},
      {selector:'node[type="image"]',style:{'background-color':'#e3222e','shape':'round-rectangle'}},
      {selector:'node[type="document"]',style:{'background-color':'#e7f2ff','color':'#071a2f'}},
      {selector:'edge',style:{'line-color':'#426683','target-arrow-color':'#426683','target-arrow-shape':'triangle','curve-style':'bezier','width':1,'opacity':.55}},
      {selector:':selected',style:{'background-color':'#ffd166','line-color':'#ffd166','target-arrow-color':'#ffd166','z-index':99}}
    ],
    layout:{name:'cose', animate:true, padding:35, idealEdgeLength:100, nodeRepulsion:8000, gravity:.25}
  });
  const meta = payload.meta || {};
  $('graph-meta').textContent = rawNodes.length + ' nodos · ' + rawEdges.length + ' relaciones · actualizado ' + (meta.updated_at || 'ahora');
}

async function loadGraph() {
  const response = await fetch('/api/graph');
  const data = await response.json();
  drawGraph(data);
  if ($('menu-graph-status')) $('menu-graph-status').textContent = (data.nodes || []).length + ' nodos';
}

async function refreshGraph() {
  const button = $('graph-refresh');
  button.disabled = true;
  await fetch('/api/graph/refresh', {method:'POST'});
  setTimeout(async () => { await loadGraph(); button.disabled = false; }, 1200);
}

$('git-status').addEventListener('click', gitStatus);
$('git-push').addEventListener('click', pushChanges);
$('deploy-refresh').addEventListener('click', refreshDeploy);
$('graph-refresh').addEventListener('click', refreshGraph);
$('quick-git-status').addEventListener('click', () => { document.querySelector('[data-coreui-target="#ship-pane"]').click(); gitStatus(); });
$('quick-deploy-refresh').addEventListener('click', () => { document.querySelector('[data-coreui-target="#ship-pane"]').click(); refreshDeploy(); });
$('quick-graph-refresh').addEventListener('click', () => { document.querySelector('[data-coreui-target="#graph-pane"]').click(); refreshGraph(); });
loadGraph();
refreshState();
setInterval(refreshState, 2500);
setInterval(loadGraph, 8000);
