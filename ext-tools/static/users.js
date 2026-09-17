(() => {
  const el = (id) => document.getElementById(id);
  let token = null, rows = [], editingId = null, busy = false;
  const message = (text, error = false) => {
    el('users-message').textContent = text;
    el('users-message').className = error ? 'text-danger' : 'text-success';
  };
  function session(value) {
    token = value;
    el('users-login').hidden = Boolean(token);
    el('users-workspace').hidden = !token;
    el('users-logout').hidden = !token;
    if (!token) { rows = []; resetForm(); render(); }
  }
  function setBusy(value) {
    busy = value;
    el('users-pane').querySelectorAll('button, input').forEach((node) => { node.disabled = value; });
    el('user-username').disabled = value || editingId !== null;
  }
  async function api(path, method = 'GET', body) {
    const response = await fetch('/api/users' + path, {
      method, cache: 'no-store', signal: AbortSignal.timeout(20000),
      headers: { ...(token ? { Authorization: 'Bearer ' + token } : {}), ...(body ? { 'Content-Type': 'application/json' } : {}) },
      ...(body ? { body: JSON.stringify(body) } : {}),
    });
    const data = response.status === 204 ? null : await response.json();
    if (!response.ok) {
      if (response.status === 401 && path !== '/login') session(null);
      const detail = data?.detail;
      throw new Error(Array.isArray(detail) ? detail.map((item) => (item.loc?.at(-1) || 'Campo') + ': ' + item.msg).join(' · ') : typeof detail === 'string' ? detail : 'No se pudo completar la operación.');
    }
    return data;
  }
  async function action(work) {
    if (busy) return;
    setBusy(true); message('');
    try { await work(); }
    catch (error) { message(error instanceof Error ? error.message : 'Error de conexión.', true); }
    finally { setBusy(false); }
  }
  function resetForm() {
    editingId = null; el('user-form').reset(); el('user-username').disabled = false;
    el('user-form-title').textContent = 'Crear usuario'; el('user-save').textContent = 'Crear usuario'; el('user-cancel').hidden = true;
  }
  function edit(row) {
    editingId = row.id;
    for (const [id, key] of [['username', 'username'], ['display-name', 'display_name'], ['email', 'email'], ['country', 'country']]) el('user-' + id).value = row[key] || '';
    el('user-password').value = ''; el('user-active').checked = row.active;
    el('user-username').disabled = true; el('user-form-title').textContent = 'Editar @' + row.username;
    el('user-save').textContent = 'Guardar cambios'; el('user-cancel').hidden = false;
    el('user-display-name').focus();
  }
  async function load() {
    const data = await api('');
    if (!Array.isArray(data)) throw new Error('La API no devolvió una lista de usuarios.');
    rows = data; render();
  }
  function render() {
    const query = el('users-search').value.trim().toLowerCase();
    const visible = rows.filter((row) => [row.username, row.display_name, row.email].some((value) => String(value || '').toLowerCase().includes(query)));
    el('users-rows').replaceChildren();
    for (const row of visible) {
      const tr = document.createElement('tr');
      for (const text of ['@' + row.username + ' · #' + row.id, row.display_name + ' · ' + (row.email || 'Sin email') + ' · ' + (row.country || 'Sin país'), row.active ? 'Activo' : 'Inactivo']) {
        const td = document.createElement('td'); td.textContent = text; tr.append(td);
      }
      const actions = document.createElement('td');
      function button(label, callback, danger = false) {
        const node = document.createElement('button'); node.type = 'button'; node.textContent = label;
        node.className = 'btn btn-sm ' + (danger ? 'btn-outline-danger' : 'btn-outline-light') + ' m-1'; node.disabled = busy;
        node.addEventListener('click', callback); actions.append(node);
      }
      button('Editar', () => edit(row));
      button(row.active ? 'Desactivar' : 'Activar', () => action(async () => {
        await api('/' + row.id, 'PATCH', { active: !row.active });
        if (editingId === row.id) el('user-active').checked = !row.active;
        await load(); message('Estado actualizado.');
      }));
      button('Eliminar', () => {
        if (!window.confirm('¿Eliminar a @' + row.username + '? Si tiene picks, debes desactivarlo para conservar su historial.')) return;
        void action(async () => {
          await api('/' + row.id, 'DELETE'); if (editingId === row.id) resetForm();
          await load(); message('Usuario eliminado.');
        });
      }, true);
      tr.append(actions); el('users-rows').append(tr);
    }
    el('users-count').textContent = visible.length ? visible.length + ' de ' + rows.length + ' usuarios' : rows.length ? 'Sin coincidencias.' : 'No hay usuarios.';
  }
  el('users-login').addEventListener('submit', (event) => {
    event.preventDefault();
    void action(async () => {
      const data = await api('/login', 'POST', { username: el('operator-name').value.trim(), password: el('operator-password').value });
      el('operator-password').value = '';
      if (!['admin', 'editor'].includes(data.role)) throw new Error('Se requiere una cuenta de administrador o editor.');
      session(data.access_token); await load();
    });
  });
  el('users-logout').addEventListener('click', () => { session(null); message('Sesión cerrada.'); });
  el('user-cancel').addEventListener('click', resetForm);
  el('users-search').addEventListener('input', render);
  el('users-refresh').addEventListener('click', () => action(load));
  el('user-form').addEventListener('submit', (event) => {
    event.preventDefault();
    const payload = { display_name: el('user-display-name').value.trim(), email: el('user-email').value.trim() || null, country: el('user-country').value.trim() || null, active: el('user-active').checked };
    if (editingId === null) payload.username = el('user-username').value.trim();
    if (!payload.display_name || (editingId === null && !payload.username)) { message('Usuario y nombre visible son obligatorios.', true); return; }
    if (el('user-password').value) payload.password = el('user-password').value;
    void action(async () => {
      await api(editingId === null ? '' : '/' + editingId, editingId === null ? 'POST' : 'PATCH', payload);
      resetForm(); await load(); message('Usuario guardado.');
    });
  });
})();
