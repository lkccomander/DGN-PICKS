"use client";

import Link from "next/link";
import { useState, type FormEvent } from "react";
import { API_URL } from "@/lib/dashboard-api";

const methods = [
  ["Bank transfer", "Secure account transfer", "BT"],
  ["Debit card", "Visa or Mastercard", "CARD"],
  ["Digital wallet", "Fast wallet processing", "WALLET"],
  ["Local payment", "Supported local methods", "LOCAL"],
  ["Wire transfer", "Manual review required", "WIRE"],
  ["USDC", "Digital asset deposit", "USDC"],
];

function authHeaders() {
  if (typeof window === "undefined") return {};
  const token = window.localStorage.getItem("dgn-admin-token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export default function DepositPage() {
  const [method, setMethod] = useState(methods[0][0]);
  const [amount, setAmount] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault(); setBusy(true); setMessage(null);
    try {
      const response = await fetch(`${API_URL}/api/v1/deposits`, { method: "POST", headers: { "Content-Type": "application/json", Accept: "application/json", ...authHeaders() }, body: JSON.stringify({ amount: Number(amount) }) });
      const body = await response.json().catch(() => ({})) as { detail?: string };
      if (!response.ok) throw new Error(body.detail || "Deposit could not be submitted.");
      setMessage(`USD ${Number(amount).toFixed(2)} submitted as pending for approval.`); setAmount("");
    } catch (error) { setMessage(error instanceof Error ? error.message : "Deposit could not be submitted."); }
    finally { setBusy(false); }
  };
  return <main className="deposit-page"><div className="stripe" /><header className="deposit-header"><Link className="deposit-brand" href="/">DGN-PICKS</Link><div className="deposit-account">✉ <span>USD 0.52</span><strong>AC254187</strong></div></header><div className="deposit-shell"><aside className="deposit-sidebar"><h2>MESSAGE CENTER</h2><Link href="/account">✉ Inbox</Link><h2>MY ACCOUNT</h2><Link href="/account">● Personal details</Link><Link href="/account">⚙ Preferences</Link><Link href="/account">▣ Statements</Link><h2>CASHIER</h2><Link className="selected" href="/deposit">▣ Deposit</Link><Link href="/account">▤ Payment history</Link><h2>MY PICKS</h2><Link href="/#picks">▣ Open picks</Link></aside><section className="deposit-content"><div className="deposit-content-head"><span className="section-kicker">ACCOUNT FUNDING</span><h1>Deposit</h1><p>Select a payment method and enter an amount. All deposits are reviewed manually.</p></div><form className="deposit-form-page" onSubmit={submit}><div className="deposit-method-heading">SELECT DEPOSIT METHOD</div><div className="deposit-method-grid">{methods.map(([name, detail, mark]) => <button type="button" key={name} className={`deposit-method ${method === name ? "selected" : ""}`} onClick={() => setMethod(name)}><span className="deposit-method-mark">{mark}</span><strong>{name}</strong><small>{detail}</small></button>)}</div><div className="deposit-entry"><label>Amount in USD<input type="number" min="0.01" max="1000" step="0.01" value={amount} onChange={(event) => setAmount(event.target.value)} placeholder="0.00" required /></label><span>Monthly limit: USD 1,000.00 · Selected: {method}</span></div>{message ? <p className="deposit-page-message" role="status">{message}</p> : null}<button className="deposit-submit" type="submit" disabled={busy}>{busy ? "SUBMITTING…" : "SUBMIT DEPOSIT"}</button></form><div className="deposit-notice">Deposits are created as <strong>pending</strong> and become available only after approval in the DGN-PICKS local operations tool.</div></section><aside className="deposit-aside"><strong>Your profile is verified.</strong><p>✓ ID<br />✓ Account</p><Link href="/account">Help &amp; support</Link></aside></div></main>;
}
