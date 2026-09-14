"use client";

import { useState, type FormEvent } from "react";

export default function JoinPage() {
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    const form = new FormData(event.currentTarget);
    if (form.get("password") !== form.get("confirmPassword")) {
      setError("Passwords do not match.");
      return;
    }
    setSubmitted(true);
  }

  return <main className="join-shell">
    <div className="stripe" aria-hidden="true" />
    <header className="join-topbar"><a className="join-brand" href="/">DGN<span>-</span>PICKS<small>college football intelligence</small></a><a className="join-back" href="/">← Back to board</a></header>
    <nav className="join-primary-nav" aria-label="Primary navigation"><a href="/">◉ <span>BOARD</span></a><a href="/#games">◌ <span>LIVE CENTRE</span></a><a href="/#markets">◆ <span>MARKETS</span></a><a href="/#picks">▣ <span>MY PICKS</span></a><a href="/#insights">◈ <span>INSIGHTS</span></a></nav>
    <div className="join-layout"><section className="join-card"><span className="section-kicker">DGN-PICKS ACCOUNT</span><h1>Create your account</h1><p className="join-lede">Keep your picks, lines, and results together. Join the board in a few quick steps.</p>{submitted ? <div className="join-success" role="status"><strong>Request received.</strong><p>Account creation is not connected to the production API yet. Your form passed local validation.</p><a href="/">Return to the board →</a></div> : <form onSubmit={submit} className="join-form"><div className="join-form-grid"><label>First name<input name="firstName" autoComplete="given-name" required /></label><label>Last name<input name="lastName" autoComplete="family-name" required /></label></div><label>Email address<input name="email" type="email" autoComplete="email" required /></label><label>Client ID<input name="clientId" autoComplete="username" placeholder="Choose a client ID" required /></label><div className="join-form-grid"><label>Password<input name="password" type="password" autoComplete="new-password" minLength={8} required /></label><label>Confirm password<input name="confirmPassword" type="password" autoComplete="new-password" minLength={8} required /></label></div><label>Country<select name="country" defaultValue="Costa Rica"><option>Costa Rica</option><option>Guatemala</option><option>United States</option><option>Other</option></select></label><label className="join-check"><input name="terms" type="checkbox" required /> <span>I agree to the DGN-PICKS terms and understand this is an analytics and tracking platform, not a sportsbook.</span></label>{error ? <p className="join-error" role="alert">{error}</p> : null}<button className="join-submit" type="submit">CREATE ACCOUNT <span>→</span></button><p className="join-login">Already have an account? <a href="/">Log in from the board</a></p></form>}</section><aside className="join-aside"><div className="join-aside-art" aria-hidden="true"><span>◉</span></div><h2>Track the call.<br /><em>Keep the receipt.</em></h2><p>One place for the slate, the movement, and every pick your group is watching.</p><div className="join-aside-rule" /><span className="join-aside-label">NCAA COLLEGE FOOTBALL · 2026</span></aside></div>
  </main>;
}
