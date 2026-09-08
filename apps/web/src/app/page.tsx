"use client";

import { useEffect, useMemo, useState } from "react";

const API_URL = (process.env.NEXT_PUBLIC_API_URL ?? "https://dgn-picks-production.up.railway.app").replace(/\/$/, "");
const ACTIVE_USER = "gato";

type Game = {
  id: number;
  week: number;
  kickoff_at: string;
  home_team_id: number;
  away_team_id: number;
  status: "scheduled" | "live" | "final" | "postponed" | "cancelled";
  home_score?: number | null;
  away_score?: number | null;
  venue?: string | null;
};

type Pick = {
  id: number;
  game_id: number;
  market_id: number;
  selection_id?: number | null;
  picked_at: string;
  line_value?: number | null;
  american_odds?: number | null;
  stake_units: number;
  result: "pending" | "win" | "loss" | "push" | "void";
  profit_units?: number | null;
  notes?: string | null;
};

type Summary = {
  wins: number;
  losses: number;
  pushes: number;
  pending: number;
  void: number;
  total_units_risked: number;
  profit_units: number;
  roi: number | null;
};

function normalizeSummary(summary: Summary): Summary {
  return {
    wins: Number(summary.wins),
    losses: Number(summary.losses),
    pushes: Number(summary.pushes),
    pending: Number(summary.pending),
    void: Number(summary.void),
    total_units_risked: Number(summary.total_units_risked),
    profit_units: Number(summary.profit_units),
    roi: summary.roi == null ? null : Number(summary.roi),
  };
}

type DashboardData = { games: Game[]; picks: Pick[]; summary: Summary };

const emptySummary: Summary = { wins: 0, losses: 0, pushes: 0, pending: 0, void: 0, total_units_risked: 0, profit_units: 0, roi: null };

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, { headers: { Accept: "application/json" } });
  if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
  return response.json() as Promise<T>;
}

function formatKickoff(value: string) {
  return new Intl.DateTimeFormat("en-US", { weekday: "short", month: "short", day: "numeric", hour: "numeric", minute: "2-digit" }).format(new Date(value));
}

function teamLabel(id: number) { return `Team ${id}`; }

function lineLabel(pick: Pick) {
  const line = pick.line_value == null ? "Line pending" : `${pick.line_value > 0 ? "+" : ""}${pick.line_value}`;
  const odds = pick.american_odds == null ? "" : ` · ${pick.american_odds > 0 ? "+" : ""}${pick.american_odds}`;
  return `${line}${odds}`;
}

export default function Home() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  async function loadDashboard() {
    setLoading(true);
    setError(null);
    try {
      const [games, picks, summaryResponse] = await Promise.all([
        fetchJson<Game[]>("/api/v1/games"),
        fetchJson<Pick[]>(`/api/v1/picks?user=${ACTIVE_USER}`),
        fetchJson<Summary>("/api/v1/analytics/summary"),
      ]);
      setData({ games, picks, summary: normalizeSummary(summaryResponse) });
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to reach the picks API.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { void loadDashboard(); }, []);

  const gamesById = useMemo(() => new Map((data?.games ?? []).map((game) => [game.id, game])), [data?.games]);
  const activeGames = data?.games.filter((game) => game.status === "live" || game.status === "scheduled") ?? [];
  const summary = data?.summary ?? emptySummary;

  return (
    <main className="app-shell">
      <div className="stripe" aria-hidden="true" />
      <header className="topbar">
        <div className="brand-lockup">
          <span className="wordmark">DGN<span>-</span>PICKS</span>
          <span className="brand-caption">College football intelligence</span>
        </div>
        <div className="topbar-actions">
          <span className={`connection ${loading ? "is-loading" : error ? "is-error" : ""}`}><i /> {loading ? "Syncing" : error ? "Offline" : "Live API"}</span>
          <span className="user-chip"><b>G</b> {ACTIVE_USER}</span>
        </div>
      </header>

      <div className="page-wrap">
        <section className="intro-row">
          <div>
            <p className="eyebrow">Week {activeGames[0]?.week ?? "—"} · 2026 season</p>
            <h1>The board<br /><em>has receipts.</em></h1>
            <p className="intro-copy">A clean read on the games, lines, and calls your group is tracking.</p>
          </div>
          <div className="date-card">
            <span className="date-label">Today&apos;s board</span>
            <strong>{new Intl.DateTimeFormat("en-US", { month: "short", day: "numeric" }).format(new Date())}</strong>
            <span>{activeGames.length} active {activeGames.length === 1 ? "game" : "games"}</span>
          </div>
        </section>

        {error ? <section className="notice error-state"><div><span className="notice-kicker">Connection issue</span><h2>Couldn&apos;t load the board.</h2><p>Check the Railway API or try the sync again. The dashboard is configured for <code>{API_URL}</code>.</p></div><button onClick={() => void loadDashboard()}>Retry sync</button></section> : null}
        {loading ? <LoadingState /> : data && !data.picks.length && !data.games.length ? <EmptyState /> : null}

        {!loading && data && (data.picks.length || data.games.length) ? <>
          <section className="summary-grid" aria-label="Pick summary">
            <SummaryCard label="Record" value={`${summary.wins}-${summary.losses}`} detail={`${summary.pushes} push${summary.pushes === 1 ? "" : "es"}`} accent="blue" />
            <SummaryCard label="Pending" value={summary.pending.toString().padStart(2, "0")} detail={`${summary.total_units_risked.toFixed(1)}u risked`} accent="red" />
            <SummaryCard label="P/L" value={`${summary.profit_units >= 0 ? "+" : ""}${summary.profit_units.toFixed(2)}u`} detail={summary.roi == null ? "No settled ROI" : `${(summary.roi * 100).toFixed(1)}% ROI`} accent="white" />
          </section>

          <div className="content-grid">
            <section className="panel picks-panel">
              <PanelHeading eyebrow="Your card" title="Tracked picks" count={data.picks.length} />
              {data.picks.length ? <div className="pick-list">{data.picks.map((pick) => <PickRow key={pick.id} pick={pick} game={gamesById.get(pick.game_id)} />)}</div> : <PanelEmpty text="No picks have been recorded for this user yet." />}
            </section>
            <aside className="panel games-panel">
              <PanelHeading eyebrow="The slate" title="Games" count={data.games.length} />
              {data.games.length ? <div className="game-list">{data.games.slice(0, 6).map((game) => <GameRow key={game.id} game={game} />)}</div> : <PanelEmpty text="No games are available for this board." />}
              <div className="panel-foot">Source · Railway API <span>UTC timestamps</span></div>
            </aside>
          </div>
        </> : null}
      </div>
      <footer><span>DGN-PICKS / 2026</span><span>Track the call. Keep the receipt.</span></footer>
    </main>
  );
}

function SummaryCard({ label, value, detail, accent }: { label: string; value: string; detail: string; accent: string }) {
  return <article className={`summary-card ${accent}`}><span>{label}</span><strong>{value}</strong><small>{detail}</small></article>;
}

function PanelHeading({ eyebrow, title, count }: { eyebrow: string; title: string; count: number }) {
  return <div className="panel-heading"><div><span className="eyebrow">{eyebrow}</span><h2>{title}</h2></div><span className="count">{count.toString().padStart(2, "0")}</span></div>;
}

function PickRow({ pick, game }: { pick: Pick; game?: Game }) {
  return <article className="pick-row"><div className="pick-main"><span className={`result-dot ${pick.result}`} /><div><strong>{pick.notes || `Market ${pick.market_id} · Selection ${pick.selection_id ?? "—"}`}</strong><span>{game ? `${teamLabel(game.away_team_id)} at ${teamLabel(game.home_team_id)}` : `Game ${pick.game_id}`} · {lineLabel(pick)}</span></div></div><span className={`status-pill ${pick.result}`}>{pick.result}</span></article>;
}

function GameRow({ game }: { game: Game }) {
  const isFinal = game.status === "final";
  return <article className="game-row"><div className="game-time"><span className={game.status === "live" ? "live-label" : ""}>{game.status === "live" ? "Live" : isFinal ? "Final" : formatKickoff(game.kickoff_at)}</span><small>{game.venue || `Game ${game.id}`}</small></div><div className="matchup"><span>{teamLabel(game.away_team_id)} {isFinal && game.away_score != null ? <b>{game.away_score}</b> : null}</span><span>{teamLabel(game.home_team_id)} {isFinal && game.home_score != null ? <b>{game.home_score}</b> : null}</span></div><span className="chevron">›</span></article>;
}

function PanelEmpty({ text }: { text: string }) { return <div className="panel-empty"><span>—</span><p>{text}</p></div>; }

function LoadingState() { return <section className="loading-board" aria-label="Loading dashboard"><div className="loader-line" /><div className="loader-line short" /><p>Reading the board…</p></section>; }

function EmptyState() { return <section className="empty-state"><span className="eyebrow">Clear board</span><h2>No fixtures in the feed yet.</h2><p>When the Railway API has games or picks, they&apos;ll show up here automatically.</p></section>; }
