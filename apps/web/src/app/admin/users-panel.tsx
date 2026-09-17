"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";

type User = { id: number; username: string; display_name: string; email: string | null; country: string | null; active: boolean };
type Profile = { username: string; display_name: string; email: string; country: string; password: string; active: boolean };
const emptyProfile = (): Profile => ({ username: "", display_name: "", email: "", country: "", password: "", active: true });

function errorText(body: { detail?: unknown }) {
  if (typeof body.detail === "string") return body.detail === "User owns picks; deactivate instead" ? "Este usuario tiene picks. Desactívalo para conservar su historial." : body.detail;
  if (Array.isArray(body.detail)) return body.detail.map((item) => `${item.loc?.at(-1) ?? "Campo"}: ${item.msg ?? "Valor inválido"}`).join(" · ");
  return "No se pudo completar la operación.";
}

async function userRequest(token: string, path = "", method = "GET", body?: unknown, signal?: AbortSignal): Promise<User[] | User | null> {
  const response = await fetch(`/api/admin/users${path}`, {
    method, cache: "no-store", signal: signal ? AbortSignal.any([signal, AbortSignal.timeout(20000)]) : AbortSignal.timeout(20000),
    headers: { Authorization: `Bearer ${token}`, ...(body ? { "Content-Type": "application/json" } : {}) },
    ...(body ? { body: JSON.stringify(body) } : {}),
  });
  const result = response.status === 204 ? null : await response.json().catch(() => ({ detail: "Respuesta inválida de la API." }));
  if (!response.ok) throw new Error(response.status === 401 ? "La sesión expiró. Cierra sesión e ingresa nuevamente." : errorText(result ?? {}));
  return result;
}

export default function UsersPanel({ token }: { token: string }) {
  const [users, setUsers] = useState<User[]>([]);
  const [form, setForm] = useState<Profile>(emptyProfile);
  const [editing, setEditing] = useState<number | null>(null);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const operation = useRef(false);
  const formRef = useRef<HTMLFormElement>(null);

  useEffect(() => {
    const controller = new AbortController();
    userRequest(token, "", "GET", undefined, controller.signal).then((rows) => {
      if (!Array.isArray(rows)) throw new Error("La API no devolvió una lista de usuarios.");
      if (!controller.signal.aborted) setUsers(rows);
    }).catch((reason) => {
      if (!controller.signal.aborted) setError(reason instanceof Error ? reason.message : "Error de conexión.");
    }).finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, [token]);

  async function reload() {
    const rows = await userRequest(token);
    if (!Array.isArray(rows)) throw new Error("La API no devolvió una lista de usuarios.");
    setUsers(rows);
  }
  async function run(work: () => Promise<void>) {
    if (operation.current) return;
    operation.current = true; setBusy(true); setError(""); setNotice("");
    try { await work(); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "No se pudo conectar con la API."); }
    finally { operation.current = false; setBusy(false); }
  }
  function reset() { setEditing(null); setForm(emptyProfile()); }
  function edit(user: User) {
    setEditing(user.id); setForm({ ...user, email: user.email ?? "", country: user.country ?? "", password: "" });
    setError(""); setNotice(""); formRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  }
  function save(event: FormEvent) {
    event.preventDefault();
    const body: Record<string, unknown> = {
      display_name: form.display_name.trim(), email: form.email.trim() || null,
      country: form.country.trim() || null, active: form.active,
    };
    if (!body.display_name || (editing === null && !form.username.trim())) { setError("Usuario y nombre visible son obligatorios."); return; }
    if (editing === null) body.username = form.username.trim();
    if (form.password) body.password = form.password;
    void run(async () => {
      await userRequest(token, editing === null ? "" : `/${editing}`, editing === null ? "POST" : "PATCH", body);
      reset(); setNotice("Usuario guardado."); await reload();
    });
  }
  function remove(user: User) {
    if (!window.confirm(`¿Eliminar a @${user.username}? Si tiene picks, debes desactivarlo para conservar su historial.`)) return;
    void run(async () => {
      await userRequest(token, `/${user.id}`, "DELETE");
      if (editing === user.id) reset();
      setNotice("Usuario eliminado."); await reload();
    });
  }
  function toggle(user: User) {
    void run(async () => {
      await userRequest(token, `/${user.id}`, "PATCH", { active: !user.active });
      if (editing === user.id) setForm((current) => ({ ...current, active: !user.active }));
      setNotice("Estado actualizado."); await reload();
    });
  }
  const query = search.trim().toLowerCase();
  const filtered = users.filter((user) => [user.username, user.display_name, user.email].some((value) => value?.toLowerCase().includes(query)));
  const disabled = busy || loading;

  return <section aria-label="Administración de usuarios">
    <form ref={formRef} className="admin-create" onSubmit={save}>
      <h2>{editing === null ? "Crear usuario" : `Editar @${form.username}`}</h2>
      <p>Gestiona perfiles y acceso. Desactiva cuentas con picks para conservar su historial.</p>
      <fieldset disabled={disabled} className="users-fieldset">
        <div className="admin-form-grid">
          <label>Usuario<input value={form.username} maxLength={32} required disabled={editing !== null} onChange={(event) => setForm({ ...form, username: event.target.value })} /></label>
          <label>Nombre visible<input value={form.display_name} maxLength={80} required onChange={(event) => setForm({ ...form, display_name: event.target.value })} /></label>
          <label>Email<input type="email" value={form.email} maxLength={320} onChange={(event) => setForm({ ...form, email: event.target.value })} /></label>
          <label>País<input value={form.country} maxLength={64} onChange={(event) => setForm({ ...form, country: event.target.value })} /></label>
          <label>Contraseña nueva (opcional)<input type="password" value={form.password} minLength={8} maxLength={256} autoComplete="new-password" aria-describedby="users-password-hint" onChange={(event) => setForm({ ...form, password: event.target.value })} /></label>
          <label>Cuenta activa<input type="checkbox" checked={form.active} onChange={(event) => setForm({ ...form, active: event.target.checked })} /></label>
        </div>
        <p id="users-password-hint" className="admin-muted">Al editar, deja la contraseña vacía para mantener la actual.</p>
        <div className="admin-form-actions">
          <button type="submit">{busy ? "Guardando…" : editing === null ? "Crear usuario" : "Guardar cambios"}</button>
          {editing !== null ? <button type="button" onClick={reset}>Cancelar edición</button> : null}
        </div>
      </fieldset>
    </form>
    {error ? <p role="alert" className="admin-error">{error}</p> : null}
    {notice ? <p role="status">{notice}</p> : null}
    <div className="admin-form-actions users-toolbar">
      <label>Buscar usuarios<input type="search" value={search} placeholder="Usuario, nombre o email" onChange={(event) => setSearch(event.target.value)} /></label>
      <button disabled={disabled} onClick={() => void run(reload)}>Actualizar</button>
    </div>
    <div className="admin-table" aria-busy={disabled}>
      <div className="admin-table-head"><span>Usuarios · {filtered.length} de {users.length}</span><span>Acciones</span></div>
      {loading ? <p role="status">Cargando usuarios…</p> : filtered.map((user) => <article key={user.id}>
        <div><strong>@{user.username} · #{user.id}</strong><span>{user.display_name} · {user.email || "Sin email"} · {user.country || "Sin país"} · {user.active ? "Activo" : "Inactivo"}</span></div>
        <div className="admin-row-actions">
          <button disabled={disabled} onClick={() => edit(user)}>Editar</button>
          <button disabled={disabled} onClick={() => toggle(user)}>{user.active ? "Desactivar" : "Activar"}</button>
          <button disabled={disabled} onClick={() => remove(user)}>Eliminar</button>
        </div>
      </article>)}
      {!loading && !filtered.length ? <p className="admin-muted">{query ? "Sin coincidencias." : "No hay usuarios."}</p> : null}
    </div>
  </section>;
}
