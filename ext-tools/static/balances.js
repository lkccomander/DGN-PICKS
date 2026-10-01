(() => {
  const el = (id) => document.getElementById(id);
  let rows = [], busy = false;
  const token = () => window.localStorage.getItem('dgn-ops-token') || '';
  const message = (text, error = false) => { el('balances-message').textContent = text; el('balances-message').className = error ? 'text-danger' : 'text-success'; };
  const dateLabel = (value) => value ? new Date(value).toISOString().replace('T', ' ').replace(/\.\d{3}Z$/, ' UTC') : '—';
  async function api(path, method = 'GET', body) {
    const response = await desktopFetch('/api/balances' + path, { method, cache: 'no-store', headers: { Accept: 'application/json', Authorization: 'Bearer ' + token(), ...(body ? {'Content-Type':'application/json'} : {}) }, ...(body ? {body: JSON.stringify(body)} : {}) });
    const data = await response.json().catch(() => ({})); if (!response.ok) throw new Error(data.detail || 'No se pudo consultar balances.'); return data;
  }
  function render() {
    el('balances-rows').replaceChildren();
    for (const row of rows) { const tr = document.createElement('tr'); for (const value of [row.id, '@' + (row.username || row.user_id), 'USD ' + Number(row.amount).toFixed(2), row.kind, row.reason, dateLabel(row.created_at), row.created_by || '—']) { const td = document.createElement('td'); td.textContent = String(value); tr.append(td); } el('balances-rows').append(tr); }
    if (!rows.length) { const tr = document.createElement('tr'), td = document.createElement('td'); td.colSpan = 7; td.className = 'text-center py-4'; td.textContent = 'No hay movimientos de balance.'; tr.append(td); el('balances-rows').append(tr); }
    el('balances-count').textContent = rows.length + ' movimiento(s)';
  }
  async function load() { if (!token()) { message('Inicia sesión en Usuarios para consultar balances.', true); return; } try { rows = await api('/history'); render(); } catch (error) { message(error.message, true); } }
  el('balance-adjustment-form').addEventListener('submit', async (event) => { event.preventDefault(); if (busy) return; busy = true; const payload = { user_id: Number(el('balance-user-id').value), amount: Number(el('balance-amount').value), reason: el('balance-reason').value.trim() }; try { await api('/adjust', 'POST', payload); event.target.reset(); await load(); message('Ajuste de balance registrado.'); } catch (error) { message(error.message, true); } finally { busy = false; } });
  el('balances-refresh').addEventListener('click', () => void load()); document.querySelector('[data-coreui-target="#balances-pane"]').addEventListener('click', () => void load()); render();
})();
