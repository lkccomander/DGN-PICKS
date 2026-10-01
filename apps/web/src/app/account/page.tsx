"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { useStoredValue } from "@/lib/use-stored-value";
import type { Components } from "@/lib/generated-api-client";
type Account = Components["schemas"]["AccountResponse"];
export default function AccountPage() {
  const [token, setToken] = useStoredValue("dgn-admin-token");
  const [result, setResult] = useState<{ token: string; account?: Account; error?: string } | null>(null);
  useEffect(() => {
    if (!token) return;
    const controller = new AbortController();
    fetch("/api/auth/account", { headers: { Authorization: `Bearer ${token}` }, signal: controller.signal, cache: "no-store" })
      .then(async response => {
        if (response.status === 401 || response.status === 403) { setToken(""); return; }
        if (!response.ok) throw new Error("Unable to load your account. Please try again.");
        const account = await response.json() as Account;
        if (!controller.signal.aborted) setResult({ token, account });
      }).catch(error => { if (!controller.signal.aborted) setResult({ token, error: error instanceof Error ? error.message : "Unable to load account" }); });
    return () => controller.abort();
  }, [token, setToken]);
  const current = result?.token === token ? result : null;
  return <main className="account-shell"><div className="stripe" aria-hidden="true" />
    <header className="account-topbar"><Link className="account-brand" href="/">DGN-PICKS</Link><Link href="/#picks-detail">My picks</Link></header>
    <section className="admin-card"><h1>My account</h1>
      {!token ? <p>Sign in from the <Link href="/">board</Link> to view your account.</p> : current?.error ? <p role="alert">{current.error}</p> : current?.account ? <dl className="profile-fields">
        <dt>Client ID</dt><dd>{current.account.username}</dd><dt>Display name</dt><dd>{current.account.display_name}</dd>
        <dt>Email</dt><dd>{current.account.email || "Not provided"}</dd><dt>Country</dt><dd>{current.account.country || "Not provided"}</dd>
        <dt>Role</dt><dd>{current.account.role}</dd></dl> : <p role="status">Loading your account…</p>}
      <p>Deposits are reviewed manually and remain pending until an administrator approves them. Monthly limit: USD 1,000.00.</p>
    </section></main>;
}
