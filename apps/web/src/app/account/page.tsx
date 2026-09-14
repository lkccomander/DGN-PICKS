"use client";

import { useEffect, useState } from "react";

const accountSections = ["Personal details", "Preferences", "Password and security", "Statements", "Verification"];
const cashierSections = ["Deposit", "Withdraw", "Payment methods"];
const betSections = ["Open picks", "Betting history"];
const casinoSections = ["Casino history", "My casino bonuses"];

export default function AccountPage() {
  const [accountId, setAccountId] = useState("AC254187");

  useEffect(() => {
    const token = window.localStorage.getItem("dgn-admin-token");
    if (!token) window.location.replace("/");
    setAccountId(window.localStorage.getItem("dgn-account-label") || "AC254187");
  }, []);

  return <main className="account-shell">
    <div className="stripe" aria-hidden="true" />
    <header className="account-topbar"><a className="account-brand" href="/">DGN<span>-</span>PICKS<small>college football intelligence</small></a><div className="account-top-actions"><span className="account-mail">✉</span><span>USD 0.93</span><button className="account-deposit" type="button">DEPOSIT</button><span className="account-avatar">●</span><strong>{accountId}</strong><span className="account-caret">▲</span></div></header>
    <nav className="account-primary-nav" aria-label="Primary navigation"><a className="active" href="/">◉ <span>BOARD</span></a><a href="/#games">◌ <span>LIVE CENTRE</span></a><a href="/#markets">◆ <span>MARKETS</span></a><a href="/#picks">▣ <span>MY PICKS</span></a><a href="/#insights">◈ <span>INSIGHTS</span></a></nav>
    <div className="account-layout">
      <aside className="account-sidebar"><AccountGroup title="MESSAGE CENTER" items={["Inbox"]} /><AccountGroup title="MY ACCOUNT" items={accountSections} selected="Personal details" /><AccountGroup title="CASHIER" items={cashierSections} /><AccountGroup title="MY PICKS" items={betSections} /><AccountGroup title="CASINO" items={casinoSections} /></aside>
      <section className="account-content"><div className="account-content-grid"><div><ProfileSection title="Personal details"><ProfileField label="Full Name" value="Not provided" /><ProfileField label="Email" value="Not provided" /><ProfileField label="Currency" value="USD" /><ProfileField label="Country" value="Not provided" /></ProfileSection><ProfileSection title="Address"><ProfileField label="Address 1" value="Not provided" /><ProfileField label="Address 2 (optional)" value="Not provided" /><ProfileField label="City" value="Not provided" /><ProfileField label="Postcode/Zip code" value="Not provided" /><ProfileField label="Phone" value="Not provided" /></ProfileSection><button className="account-save" type="button" disabled>SAVE</button></div><aside className="verification-card"><div className="verified-banner">Your profile is fully verified.</div><div className="verified-items"><p>✓ <span>ID</span></p><p>✓ <span>Address</span></p></div><a href="#help">? &nbsp; Help &amp; Support</a></aside></div></section>
    </div>
  </main>;
}

function AccountGroup({ title, items, selected }: { title: string; items: string[]; selected?: string }) {
  return <section className="account-group"><h2>{title}</h2>{items.map((item) => <a className={item === selected ? "selected" : ""} href={item === "Personal details" ? "/account" : item === "Open picks" ? "/#picks" : "/#help"} key={item}><span aria-hidden="true">{item === "Personal details" ? "●" : item === "Inbox" ? "✉" : "◆"}</span>{item}</a>)}</section>;
}

function ProfileSection({ title, children }: { title: string; children: React.ReactNode }) {
  return <section className="profile-section"><h2>{title}</h2><div className="profile-fields">{children}</div></section>;
}

function ProfileField({ label, value }: { label: string; value: string }) {
  return <label className="profile-field">{label}<input value={value} readOnly aria-label={label} /></label>;
}
