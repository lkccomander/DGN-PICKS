"use client";

import { useEffect, useMemo, useState, type FormEvent } from "react";

type Resource = "teams" | "players" | "games" | "markets" | "selections";
const resources: Resource[] = ["teams", "players", "games", "markets", "selections"];

export default function AdminPage() {
  const [token, setToken] = useState<string | null>(null);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [resource, setResource] = useState<Resource>("teams");
  const [rows, setRows] = useState<Record<string, unknown>[]>([]);
  const [draft, setDraft] = useState("{}");
  const [busy, setBusy] = useState(false);

  useEffect(() => setToken(window.localStorage.getItem("dgn-admin-token")), []);
  const endpoint = useMemo(() => `/api/admin/${resource}`, [resource]);

  async function login(event: FormEvent) {
    event.preventDefault();
    setError(null);
    const response = await fetch("/api/admin/auth/login", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ username, password }) });
    const body = await response.json().catch(() => ({}));
    if (!response.ok) { setError(body.detail ?? "Login failed"); return; }
    window.localStorage.setItem("dgn-admin-token", body.access_token);
    setToken(body.access_token);
  }

  async function load() {
    if (!token) return;
    setBusy(true); setError(null);
    const response = await fetch(endpoint, { headers: { Authorization: `Bearer ${token}` }, cache: "no-store" });
    const body = await response.json().catch(() => ({}));
    setBusy(false);
    if (!response.ok) { setError(body.detail ?? "Unable to load catalog"); return; }
    setRows(body);
  }

  useEffect(() => { void load(); }, [endpoint, token]);

  async function create() {
    let payload: unknown;
    try { payload = JSON.parse(draft); } catch { setError("Draft must be valid JSON"); return; }
    setBusy(true); setError(null);
    const response = await fetch(endpoint, { method: "POST", headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" }, body: JSON.stringify(payload) });
    if (!response.ok) { const body = await response.json().catch(() => ({})); setError(body.detail ?? "Create failed"); setBusy(false); return; }
    setDraft("{}"); await load();
  }

  async function remove(id: unknown) {
    if (!window.confirm(`Delete ${resource} ${id}?`)) return;
    setBusy(true); const response = await fetch(`${endpoint}/${id}`, { method: "DELETE", headers: { Authorization: `Bearer ${token}` } });
    if (!response.ok) { const body = await response.json().catch(() => ({})); setError(body.detail ?? "Delete failed"); }
    await load();
  }

  if (!token) return <main className="admin-shell"><div className="stripe" /><section className="admin-card"><span className="eyebrow">DGN-PICKS administration</span><h1>Sign in to catalog control</h1><form onSubmit={login}><label>Username<input value={username} onChange={(event) => setUsername(event.target.value)} required /></label><label>Password<input type="password" value={password} onChange={(event) => setPassword(event.target.value)} required /></label><button type="submit">Sign in</button></form>{error ? <p className="admin-error">{error}</p> : null}</section></main>;
  return <main className="admin-shell"><div className="stripe" /><header className="admin-header"><div><span className="eyebrow">Authenticated catalog</span><h1>Admin control</h1></div><button onClick={() => { window.localStorage.removeItem("dgn-admin-token"); setToken(null); }}>Sign out</button></header><section className="admin-card"><nav className="admin-tabs">{resources.map((item) => <button key={item} className={item === resource ? "selected" : ""} onClick={() => setResource(item)}>{item}</button>)}</nav><div className="admin-create"><h2>Add {resource.slice(0, -1)}</h2><p>Submit the API-shaped catalog object. References are validated by the API.</p><textarea value={draft} onChange={(event) => setDraft(event.target.value)} spellCheck={false} /><button onClick={() => void create()} disabled={busy}>Create {resource.slice(0, -1)}</button></div>{error ? <p className="admin-error">{error}</p> : null}<div className="admin-table"><div className="admin-table-head"><span>Record</span><span>Actions</span></div>{rows.map((row) => <article key={String(row.id)}><pre>{JSON.stringify(row, null, 2)}</pre><button onClick={() => void remove(row.id)}>Delete</button></article>)}{!rows.length && !busy ? <p className="admin-muted">No records.</p> : null}</div></section></main>;
}
