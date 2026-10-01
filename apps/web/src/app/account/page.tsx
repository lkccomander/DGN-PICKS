"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useStoredValue } from "@/lib/use-stored-value";
import type { Components } from "@/lib/generated-api-client";

type Account = Components["schemas"]["AccountResponse"] & { balance?: number | string };

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
  const account = current?.account;
  return <main className="deposit-page"><div className="stripe" aria-hidden="true" />
    <header className="deposit-header"><Link className="deposit-brand" href="/">DGN-PICKS</Link><div className="deposit-account"><span aria-hidden="true">✉</span><span>USD {Number(account?.balance ?? 0).toFixed(2)}</span><Link className="account-deposit" href="/deposit">DEPOSIT</Link><strong>{account?.username || "ACCOUNT"}</strong></div></header>
    <div className="deposit-shell"><aside className="deposit-sidebar"><h2>MESSAGE CENTER</h2><Link href="/account">✉ Inbox</Link><h2>MY ACCOUNT</h2><Link className="selected" href="/account">● Personal details</Link><Link href="/account">⚙ Preferences</Link><Link href="/account">▣ Statements</Link><h2>CASHIER</h2><Link href="/deposit">▣ Deposit</Link><Link href="/account">▤ Payment history</Link><h2>MY PICKS</h2><Link href="/#picks">▣ Open picks</Link></aside>
      <section className="deposit-content"><div className="deposit-content-head"><span className="section-kicker">MY ACCOUNT</span><h1>Personal details</h1><p>Your account information and current balance.</p></div>
        {!token ? <div className="deposit-notice">Sign in from the <Link href="/">main board</Link> to view your account.</div> : current?.error ? <p className="deposit-page-message" role="alert">{current.error}</p> : account ? <div className="profile-fields"><label className="profile-field">Client ID<input value={account.username} readOnly /></label><label className="profile-field">Display name<input value={account.display_name} readOnly /></label><label className="profile-field">Email<input value={account.email || "Not provided"} readOnly /></label><label className="profile-field">Country<input value={account.country || "Not provided"} readOnly /></label><label className="profile-field">Balance<input value={`USD ${Number(account.balance ?? 0).toFixed(2)}`} readOnly /></label><label className="profile-field">Role<input value={account.role} readOnly /></label></div> : <p role="status">Loading your account…</p>}
        <div className="deposit-notice">Deposits remain pending until an administrator approves them. Monthly limit: USD 1,000.00.</div>
      </section><aside className="deposit-aside"><strong>Your profile is verified.</strong><p>✓ ID<br />✓ Account</p><Link href="/deposit">Manage deposits</Link></aside>
    </div></main>;
}
