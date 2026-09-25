"use client";

import Link from "next/link";
import { useState, type FormEvent } from "react";

export default function JoinPage() {
  const [submitted, setSubmitted] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    const form = new FormData(event.currentTarget);
    if (form.get("password") !== form.get("confirmPassword")) {
      setError("Passwords do not match.");
      return;
    }
    setBusy(true);
    try {
    const response = await fetch("/api/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: form.get("clientId"),
        email: form.get("email"),
        display_name: `${form.get("firstName")} ${form.get("lastName")}`.trim(),
        country: form.get("country"),
        password: form.get("password"),
      }),
    });
    const body = await response.json().catch(() => ({}));
    if (!response.ok) {
      setError(typeof body.detail === "string" ? body.detail : "Check your account details and try again.");
      return;
    }
    window.localStorage.setItem("dgn-admin-token", body.access_token);
    window.localStorage.setItem("dgn-account-label", body.user.display_name);
    window.localStorage.setItem("dgn-active-user", body.user.username);
    setSubmitted(true);
    } catch {
      setError("Unable to connect. Please try again.");
    } finally {
      setBusy(false);
    }
  }

  return <main className="join-shell">
    <div className="stripe" aria-hidden="true" />
    <header className="join-topbar"><Link className="join-brand" href="/">DGN<span>-</span>PICKS<small>college football intelligence</small></Link><Link className="join-back" href="/">← Back to board</Link></header>
    <nav className="join-primary-nav" aria-label="Primary navigation"><Link href="/">◉ <span>BOARD</span></Link><Link href="/#games">◌ <span>LIVE CENTRE</span></Link><Link href="/#markets">◆ <span>MARKETS</span></Link><Link href="/#picks">▣ <span>MY PICKS</span></Link><Link href="/#insights">◈ <span>INSIGHTS</span></Link></nav>
    <div className="join-layout"><section className="join-card"><span className="section-kicker">DGN-PICKS ACCOUNT</span><h1>Create your account</h1><p className="join-lede">Keep your picks, lines, and results together. Join the board in a few quick steps.</p>{submitted ? <div className="join-success" role="status"><strong>Account created.</strong><p>Your DGN-PICKS account is ready. You can now track picks on the board.</p><Link href="/">Go to the board →</Link></div> : <form onSubmit={submit} className="join-form"><div className="join-form-grid"><label>First name<input name="firstName" autoComplete="given-name" required /></label><label>Last name<input name="lastName" autoComplete="family-name" required /></label></div><label>Email address<input name="email" type="email" autoComplete="email" required /></label><label>Client ID<input name="clientId" autoComplete="username" pattern="[a-zA-Z0-9_-]+" minLength={3} maxLength={32} title="Use letters, numbers, underscores or hyphens" placeholder="Choose a client ID" required /></label><div className="join-form-grid"><label>Password<input name="password" type="password" autoComplete="new-password" minLength={8} required /></label><label>Confirm password<input name="confirmPassword" type="password" autoComplete="new-password" minLength={8} required /></label></div><label>Country<select name="country" defaultValue="Costa Rica"><option>Costa Rica</option><option>Guatemala</option><option>United States</option><option>Other</option></select></label><label className="join-check"><input name="terms" type="checkbox" required /> <span>I agree to the DGN-PICKS terms and understand this is an analytics and tracking platform, not a sportsbook.</span></label>{error ? <p className="join-error" role="alert">{error}</p> : null}<button className="join-submit" type="submit" disabled={busy}>{busy ? "CREATING ACCOUNT…" : <>CREATE ACCOUNT <span>→</span></>}</button><p className="join-login">Already have an account? <Link href="/">Log in from the board</Link></p></form>}</section><aside className="join-aside"><div className="join-aside-art" aria-hidden="true"><span>◉</span></div><h2>Track the call.<br /><em>Keep the receipt.</em></h2><p>One place for the slate, the movement, and every pick your group is watching.</p><div className="join-aside-rule" /><span className="join-aside-label">NCAA COLLEGE FOOTBALL · 2026</span></aside></div>
  </main>;
}
