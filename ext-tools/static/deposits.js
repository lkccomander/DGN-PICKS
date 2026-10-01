(() => {
  const el = (id) => document.getElementById(id);
  let rows = [], busy = false;
  const token = () => window.localStorage.getItem('dgn-ops-token') || '';
  const message = (text, error = false) => { el('deposits-message').textContent = text; el('deposits-message').className = error ? 'text-danger' : 'text-success'; };
  const statusLabel = (status) => ({ pending: 'Pendiente', approved: 'Aprobado', rejected: 'Rechazado' }[status] || status);
  const dateLabel = (value) => value ? new Date(value).toISOString().replace('T', ' ').replace(/\.\d{3}Z$/, ' UTC') : '—';
  async function api(path, method = 'GET', body) {
    const response = await desktopFetch('/api/deposits' + path, { method, cache: 'no-store', headers: { Accept: 'application/json', Authorization: 'Bearer ' + token(), ...(body ? {'Content-Type':'application/json'} : {}) }, ...(body ? {body: JSON.stringify(body)} : {}) });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.detail || 'No se pudo consultar depósitos.');
    return data;
  }
  function detailCell(row) {
    const cell = document.createElement('td'), details = document.createElement('details'), summary = document.createElement('summary');
    summary.textContent = row.status === 'pending' ? 'Revisar' : 'Ver detalle'; details.append(summary);
    const text = document.createElement('small'); text.className = 'd-block mt-2 text-medium-emphasis';
    text.textContent = `Solicitud #${row.id} · Usuario ${row.user_id} · Revisado: ${dateLabel(row.reviewed_at)} · Revisor: ${row.reviewer_id || '—'}`; details.append(text);
    if (row.status === 'pending') for (const [label, status, danger] of [['Aprobar', 'approved', false], ['Rechazar', 'rejected', true]]) { const button = document.createElement('button'); button.type = 'button'; button.textContent = label; button.className = 'btn btn-sm ' + (danger ? 'btn-outline-danger' : 'btn-outline-success') + ' m-1'; button.disabled = busy; button.onclick = () => decide(row.id, status); details.append(button); }
    cell.append(details); return cell;
  }
  function render() {
    const filter = el('deposits-filter').value, visible = filter === 'all' ? rows : rows.filter((row) => row.status === filter);
    el('deposits-rows').replaceChildren();
    for (const row of visible) { const tr = document.createElement('tr'); for (const value of [String(row.id), '@' + (row.username || row.user_id), 'USD ' + Number(row.amount).toFixed(2), dateLabel(row.created_at), statusLabel(row.status), dateLabel(row.reviewed_at)]) { const td = document.createElement('td'); td.textContent = value; tr.append(td); } tr.append(detailCell(row)); el('deposits-rows').append(tr); }
    if (!visible.length) { const tr = document.createElement('tr'), td = document.createElement('td'); td.colSpan = 7; td.className = 'text-center py-4'; td.textContent = filter === 'all' ? 'No hay depósitos registrados.' : `No hay depósitos ${statusLabel(filter).toLowerCase()}s.`; tr.append(td); el('deposits-rows').append(tr); }
    el('deposits-count').textContent = `${visible.length} visible(s) · ${rows.length} total(es)`;
  }
  async function load() { if (!token()) { message('Inicia sesión en Usuarios para consultar depósitos.', true); return; } try { rows = await api('/history'); render(); message('Historial actualizado.'); } catch (error) { message(error.message, true); } }
  async function decide(id, status) { if (busy) return; busy = true; try { await api('/' + id, 'PATCH', { status }); await load(); message(status === 'approved' ? 'Depósito aprobado.' : 'Depósito rechazado.'); } catch (error) { message(error.message, true); } finally { busy = false; render(); } }
  el('deposits-refresh').addEventListener('click', () => void load()); el('deposits-filter').addEventListener('change', render);
  document.querySelector('[data-coreui-target="#deposits-pane"]').addEventListener('click', () => void load()); render();
})();
