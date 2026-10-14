"use client";

import Link from "next/link";
import { useEffect, useState, type FormEvent } from "react";
import { API_URL } from "@/lib/dashboard-api";
import { useStoredValue } from "@/lib/use-stored-value";
import type { Components } from "@/lib/generated-api-client";

type CreditRequest = Components["schemas"]["DepositResponse"];
type Account = Components["schemas"]["AccountResponse"];
type CreditState = { token: string; requests: CreditRequest[]; account: Account };

export default function CreditRequestsPage() {
  const [token, setToken] = useStoredValue("dgn-admin-token");
  const [amount, setAmount] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(false);
  const [refresh, setRefresh] = useState(0);
  const [state, setState] = useState<CreditState | null>(null);
  const current = state?.token === token ? state : null;

  useEffect(() => {
    if (!token) return;
    const controller = new AbortController();
    const headers = { Authorization: `Bearer ${token}`, Accept: "application/json" };
    async function load() {
      setLoading(true); setError(null);
      try {
        const responses = await Promise.all([
          fetch(`${API_URL}/api/v1/deposits`, { headers, cache: "no-store", signal: controller.signal }),
          fetch("/api/auth/account", { headers, cache: "no-store", signal: controller.signal }),
        ]);
        if (controller.signal.aborted) return;
        if (responses.some(response => response.status === 401 || response.status === 403)) {
          if (localStorage.getItem("dgn-admin-token") === token) setToken("");
          return;
        }
        if (responses.some(response => !response.ok)) throw new Error("Unable to load your credits. Please try again.");
        const [requests, account] = await Promise.all(responses.map(response => response.json()));
        if (!controller.signal.aborted) setState({ token, requests, account });
      } catch (cause) {
        if (!controller.signal.aborted) setError(cause instanceof Error ? cause.message : "Unable to load credits.");
      } finally {
        if (!controller.signal.aborted) setLoading(false);
      }
    }
    void load();
    return () => controller.abort();
  }, [token, setToken, refresh]);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || busy) return;
    setBusy(true); setMessage(null); setError(null);
    try {
      const response = await fetch(`${API_URL}/api/v1/deposits`, {
        method: "POST", headers: { "Content-Type": "application/json", Accept: "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ amount: Number(amount) }),
      });
      if (response.status === 401 || response.status === 403) {
        if (localStorage.getItem("dgn-admin-token") === token) setToken("");
        return;
      }
      const body = await response.json().catch(() => ({})) as { detail?: string };
      if (!response.ok) throw new Error(body.detail || "Credit request could not be submitted.");
      setMessage(`${Number(amount).toFixed(2)} virtual credits requested. Pending administrator approval.`);
      setAmount(""); setRefresh(value => value + 1);
    } catch (cause) { setError(cause instanceof Error ? cause.message : "Credit request could not be submitted."); }
    finally { setBusy(false); }
  }

  return <main className="deposit-page"><div className="stripe" aria-hidden="true" />
    <header className="deposit-header"><Link className="deposit-brand" href="/">DGN-PICKS</Link><div className="deposit-account"><span>{current ? `${Number(current.account.balance).toFixed(2)} credits` : "Virtual credits"}</span><strong>{current?.account.username || "ACCOUNT"}</strong></div></header>
    <div className="deposit-shell"><aside className="deposit-sidebar"><h2>MY ACCOUNT</h2><Link href="/account">Personal details</Link><h2>VIRTUAL CREDITS</h2><Link className="selected" href="/deposit">Request credits</Link><h2>MY PICKS</h2><Link href="/#picks">Open picks</Link></aside>
      <section className="deposit-content"><div className="deposit-content-head"><span className="section-kicker">VIRTUAL CREDITS</span><h1>Request credits</h1><p>Credits have no monetary value and cannot be purchased, transferred, withdrawn or redeemed. Picks are tracked separately in units.</p></div>
        {!token ? <div className="deposit-notice">Sign in from the <Link href="/">main board</Link> to request virtual credits.</div> : <>
          <form className="deposit-form-page" onSubmit={submit}><div className="deposit-entry"><label>Virtual credits<input type="number" min="0.01" max="1000" step="0.01" value={amount} onChange={event => setAmount(event.target.value)} placeholder="0.00" required /></label><span>Monthly request limit: 1,000.00 virtual credits. Pending and approved requests count toward the limit.</span></div>
            <button className="deposit-submit" type="submit" disabled={busy}>{busy ? "SUBMITTING…" : "REQUEST CREDITS"}</button>
          </form>
          <div className="deposit-notice">Requests remain pending until an administrator approves them. Approval adds virtual credits to your account history.</div>
          <section className="deposit-history"><div className="deposit-history-heading"><h2>Your credit requests</h2><button type="button" onClick={() => setRefresh(value => value + 1)} disabled={loading}>Refresh</button></div>
            {loading ? <p role="status">Loading credit requests…</p> : current?.requests.length ? <div className="deposit-list">{current.requests.map(request => <article className="deposit-row" key={request.id}><div><strong>Request #{request.id}</strong><small>{new Date(request.created_at).toLocaleString()}</small></div><b>{Number(request.amount).toFixed(2)} credits</b><span className={`deposit-status ${request.status}`}>{request.status === "approved" ? "Approved" : request.status === "rejected" ? "Rejected" : "Pending approval"}</span></article>)}</div> : !error ? <p className="deposit-history-empty">No credit requests yet.</p> : null}
          </section>
        </>}
        {message ? <p className="deposit-page-message" role="status">{message}</p> : null}
        {error && token ? <p className="deposit-page-message" role="alert">{error}</p> : null}
      </section><aside className="deposit-aside"><strong>Paper credits only</strong><p>No money or payment information is collected.</p><Link href="/account">My account</Link></aside>
    </div>
  </main>;
}
