(() => {
  const el = (id) => document.getElementById(id);
  let rows = [], busy = false;
  const token = () => window.localStorage.getItem('dgn-ops-token') || '';
  const message = (text, error = false) => { el('deposits-message').textContent = text; el('deposits-message').className = error ? 'text-danger' : 'text-success'; };
  async function api(path, method = 'GET', body) {
    const response = await desktopFetch('/api/deposits' + path, { method, cache: 'no-store', headers: { Accept: 'application/json', Authorization: 'Bearer ' + token(), ...(body ? {'Content-Type':'application/json'} : {}) }, ...(body ? {body: JSON.stringify(body)} : {}) });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.detail || 'No se pudo consultar depósitos.');
    return data;
  }
  function render() {
    el('deposits-rows').replaceChildren();
    for (const row of rows) {
      const tr = document.createElement('tr');
      for (const value of [String(row.id), '@' + (row.username || row.user_id), 'USD ' + Number(row.amount).toFixed(2), new Date(row.created_at).toISOString().replace('T',' ').replace(/\.\d{3}Z$/,' UTC'), row.status]) { const td = document.createElement('td'); td.textContent = value; tr.append(td); }
      const actions = document.createElement('td');
      for (const [label, status, danger] of [['Aprobar','approved',false],['Rechazar','rejected',true]]) { const button = document.createElement('button'); button.type='button'; button.textContent=label; button.className='btn btn-sm ' + (danger ? 'btn-outline-danger' : 'btn-outline-success') + ' m-1'; button.disabled=busy; button.onclick=()=>decide(row.id,status); actions.append(button); }
      tr.append(actions); el('deposits-rows').append(tr);
    }
    if (!rows.length) { const tr=document.createElement('tr'), td=document.createElement('td'); td.colSpan=6; td.className='text-center py-4'; td.textContent='No hay depósitos pendientes.'; tr.append(td); el('deposits-rows').append(tr); }
    el('deposits-count').textContent = rows.length + ' depósito(s) pendiente(s)';
  }
  async function load() { if (!token()) { message('Inicia sesión en Usuarios para administrar depósitos.', true); return; } try { rows = await api('/pending'); render(); } catch (error) { message(error.message, true); } }
  async function decide(id, status) { if (busy) return; busy=true; try { await api('/' + id, 'PATCH', {status}); rows = rows.filter(row => row.id !== id); render(); message(status === 'approved' ? 'Depósito aprobado.' : 'Depósito rechazado.'); } catch(error) { message(error.message, true); } finally { busy=false; } }
  el('deposits-refresh').addEventListener('click', () => void load());
  document.querySelector('[data-coreui-target="#deposits-pane"]').addEventListener('click', () => void load());
  render();
})();
