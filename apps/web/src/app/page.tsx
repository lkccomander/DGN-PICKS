export default function Home() {
  return <main className="shell">
    <div className="stripe" aria-hidden="true" />
    <nav className="topbar"><span className="wordmark">DGN<span>-</span>PICKS</span><span className="status"><i /> Local MVP</span></nav>
    <section className="hero"><p className="eyebrow">Picks with a paper trail</p><h1>Make the read.<br /><em>Keep the receipt.</em></h1><p className="lede">Your sharpest calls, captured with the odds that made them worth taking.</p><div className="actions"><a href="#workspace" className="primary">Enter workspace</a><a href="#about" className="secondary">How it works</a></div></section>
    <section className="signal-grid" id="workspace"><div><strong>01</strong><span>Local first</span><p>Fast fixture-backed development, ready before live feeds.</p></div><div><strong>02</strong><span>Every pick owned</span><p>A clear record from user to leg to captured price.</p></div><div><strong>03</strong><span>History stays put</span><p>Odds snapshots are append-only, never silently replaced.</p></div></section>
    <footer id="about"><span>DGN-PICKS / 2026</span><span>Built for the group chat that takes receipts.</span></footer>
  </main>;
}
