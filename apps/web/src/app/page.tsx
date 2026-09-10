"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

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

type Selection = {
  id: number;
  market_id: number;
  selection_key: string;
  team_id?: number | null;
  player_id?: number | null;
  side?: string | null;
};

type Market = {
  id: number;
  game_id: number;
  market_type: string;
  period: string;
  status: "open" | "suspended" | "closed";
  selections: Selection[];
};

type OddsSnapshot = {
  id: number;
  selection_id: number;
  sportsbook_id: number;
  observed_at: string;
  line_value?: number | null;
  american_odds?: number | null;
  decimal_odds: number;
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

function normalizePick(pick: Pick): Pick {
  return {
    ...pick,
    line_value: pick.line_value == null ? null : Number(pick.line_value),
    american_odds: pick.american_odds == null ? null : Number(pick.american_odds),
    stake_units: Number(pick.stake_units),
    profit_units: pick.profit_units == null ? null : Number(pick.profit_units),
  };
}

type DashboardData = { games: Game[]; picks: Pick[]; summary: Summary; markets: Market[]; history: OddsSnapshot[] };
type ResultFilter = "all" | Pick["result"];

const emptySummary: Summary = { wins: 0, losses: 0, pushes: 0, pending: 0, void: 0, total_units_risked: 0, profit_units: 0, roi: null };

async function fetchJson<T>(path: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, { headers: { Accept: "application/json" }, signal });
  if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
  return response.json() as Promise<T>;
}

async function fetchDashboardData(signal?: AbortSignal): Promise<DashboardData> {
  const [games, picks, summaryResponse] = await Promise.all([
    fetchJson<Game[]>("/api/v1/games", signal),
    fetchJson<Pick[]>(`/api/v1/picks?user=${ACTIVE_USER}`, signal),
    fetchJson<Summary>("/api/v1/analytics/summary", signal),
  ]);
  const markets = (await Promise.all(
    games.map((game) => fetchJson<Market[]>(`/api/v1/games/${game.id}/markets`, signal)),
  )).flat();
  const histories = (await Promise.all(
    markets.map((market) => fetchJson<OddsSnapshot[]>(`/api/v1/markets/${market.id}/history`, signal)),
  )).flat().map((snapshot) => ({
    ...snapshot,
    line_value: snapshot.line_value == null ? null : Number(snapshot.line_value),
    american_odds: snapshot.american_odds == null ? null : Number(snapshot.american_odds),
    decimal_odds: Number(snapshot.decimal_odds),
  }));
  return { games, picks: picks.map(normalizePick), summary: normalizeSummary(summaryResponse), markets, history: histories };
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
  const [query, setQuery] = useState("");
  const [resultFilter, setResultFilter] = useState<ResultFilter>("all");
  const [gameFilter, setGameFilter] = useState<"all" | Game["status"]>("all");

  const loadDashboard = useCallback(async (signal?: AbortSignal) => {
    setLoading(true);
    setError(null);
    try {
      setData(await fetchDashboardData(signal));
    } catch (requestError) {
      if (requestError instanceof DOMException && requestError.name === "AbortError") return;
      setError(requestError instanceof Error ? requestError.message : "Unable to reach the picks API.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    fetchDashboardData(controller.signal)
      .then(setData)
      .catch((requestError: unknown) => {
        if (requestError instanceof DOMException && requestError.name === "AbortError") return;
        setError(requestError instanceof Error ? requestError.message : "Unable to reach the picks API.");
      })
      .finally(() => setLoading(false));
    return () => controller.abort();
  }, []);

  const gamesById = useMemo(() => new Map((data?.games ?? []).map((game) => [game.id, game])), [data?.games]);
  const snapshotsBySelection = useMemo(() => {
    const map = new Map<number, OddsSnapshot[]>();
    for (const snapshot of data?.history ?? []) {
      const history = map.get(snapshot.selection_id) ?? [];
      history.push(snapshot);
      map.set(snapshot.selection_id, history);
    }
    return map;
  }, [data?.history]);
  const activeGames = data?.games.filter((game) => game.status === "live" || game.status === "scheduled") ?? [];
  const summary = data?.summary ?? emptySummary;
  const visiblePicks = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    return (data?.picks ?? []).filter((pick) => {
      const game = gamesById.get(pick.game_id);
      const searchable = `${pick.notes ?? ""} ${pick.market_id} ${pick.selection_id ?? ""} ${game ? `${teamLabel(game.away_team_id)} ${teamLabel(game.home_team_id)}` : ""}`.toLowerCase();
      return (resultFilter === "all" || pick.result === resultFilter) && (!normalizedQuery || searchable.includes(normalizedQuery));
    });
  }, [data?.picks, gamesById, query, resultFilter]);
  const visibleGames = useMemo(() => (data?.games ?? []).filter((game) => gameFilter === "all" || game.status === gameFilter), [data?.games, gameFilter]);

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
        <nav className="section-nav" aria-label="Dashboard sections">
          <span className="nav-mark">D</span>
          <a className="active" href="#board">Board</a>
          <a href="#picks">Picks</a>
          <a href="#games">Games</a>
          <a href="#markets">Markets</a>
          <span className="nav-season">2026 / NCAA</span>
        </nav>
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
          <section id="board" className="summary-grid" aria-label="Pick summary">
            <p className="summary-scope">Performance summary · All users</p>
            <SummaryCard label="Record" value={`${summary.wins}-${summary.losses}`} detail={`${summary.pushes} push${summary.pushes === 1 ? "" : "es"}`} accent="blue" />
            <SummaryCard label="Pending" value={summary.pending.toString().padStart(2, "0")} detail={`${summary.total_units_risked.toFixed(1)}u risked`} accent="red" />
            <SummaryCard label="P/L" value={`${summary.profit_units >= 0 ? "+" : ""}${summary.profit_units.toFixed(2)}u`} detail={summary.roi == null ? "No settled ROI" : `${(summary.roi * 100).toFixed(1)}% ROI`} accent="white" />
          </section>

          <div className="content-grid">
            <section id="picks" className="panel picks-panel">
              <PanelHeading eyebrow="Your card · gato" title="Tracked picks" count={visiblePicks.length} />
              <div className="panel-tools">
                <label className="search-box"><span className="sr-only">Search picks</span><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search picks" /></label>
                <label className="filter-box"><span className="sr-only">Filter result</span><select value={resultFilter} onChange={(event) => setResultFilter(event.target.value as ResultFilter)}><option value="all">All results</option><option value="pending">Pending</option><option value="win">Wins</option><option value="loss">Losses</option><option value="push">Pushes</option><option value="void">Voids</option></select></label>
              </div>
              <div className="table-head"><span>Selection</span><span>Line / price</span><span>Risk</span><span>Status</span></div>
              {visiblePicks.length ? <div className="pick-list">{visiblePicks.map((pick) => <PickRow key={pick.id} pick={pick} game={gamesById.get(pick.game_id)} />)}</div> : <PanelEmpty text={data.picks.length ? "No picks match the current filters." : "No picks have been recorded for this user yet."} />}
            </section>
            <aside id="games" className="panel games-panel">
              <PanelHeading eyebrow="The slate" title="Games" count={visibleGames.length} />
              <div className="game-filter" role="group" aria-label="Filter games"><button type="button" aria-pressed={gameFilter === "all"} className={gameFilter === "all" ? "selected" : ""} onClick={() => setGameFilter("all")}>All</button><button type="button" aria-pressed={gameFilter === "scheduled"} className={gameFilter === "scheduled" ? "selected" : ""} onClick={() => setGameFilter("scheduled")}>Scheduled</button><button type="button" aria-pressed={gameFilter === "live"} className={gameFilter === "live" ? "selected" : ""} onClick={() => setGameFilter("live")}>Live</button><button type="button" aria-pressed={gameFilter === "final"} className={gameFilter === "final" ? "selected" : ""} onClick={() => setGameFilter("final")}>Final</button></div>
              {visibleGames.length ? <div className="game-list">{visibleGames.slice(0, 6).map((game) => <GameRow key={game.id} game={game} />)}</div> : <PanelEmpty text={data.games.length ? "No games match this filter." : "No games are available for this board."} />}
              <div className="panel-foot">Source · Railway API <span>UTC timestamps</span></div>
            </aside>
          </div>
          <section id="markets" className="panel market-panel">
            <PanelHeading eyebrow="The board" title="Market movement" count={data.markets.length} />
            {data.markets.length ? <div className="market-list">{data.markets.slice(0, 12).map((market) => <MarketRow key={market.id} market={market} game={gamesById.get(market.game_id)} snapshotsBySelection={snapshotsBySelection} />)}</div> : <PanelEmpty text="No market lines are available for the current slate." />}
            <div className="panel-foot">Opening → current <span>Persisted snapshots · local-fixture</span></div>
          </section>
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
  return <article className="pick-row"><div className="pick-main"><span className={`result-dot ${pick.result}`} /><div><strong>{pick.notes || `Market ${pick.market_id} · Selection ${pick.selection_id ?? "—"}`}</strong><span>{game ? `${teamLabel(game.away_team_id)} at ${teamLabel(game.home_team_id)}` : `Game ${pick.game_id}`}</span></div></div><span className="pick-line">{lineLabel(pick)}</span><span className="pick-stake">{pick.stake_units.toFixed(1)}u</span><span className={`status-pill ${pick.result}`}>{pick.result}</span></article>;
}

function GameRow({ game }: { game: Game }) {
  const isFinal = game.status === "final";
  return <article className="game-row"><div className="game-time"><span className={game.status === "live" ? "live-label" : ""}>{game.status === "live" ? "Live" : isFinal ? "Final" : formatKickoff(game.kickoff_at)}</span><small>{game.venue || `Game ${game.id}`}</small></div><div className="matchup"><span>{teamLabel(game.away_team_id)} {isFinal && game.away_score != null ? <b>{game.away_score}</b> : null}</span><span>{teamLabel(game.home_team_id)} {isFinal && game.home_score != null ? <b>{game.home_score}</b> : null}</span></div><span className="chevron">›</span></article>;
}

function marketLabel(market: Market) {
  return market.market_type.replaceAll("_", " ");
}

function snapshotLine(snapshot?: OddsSnapshot) {
  if (!snapshot) return "—";
  const line = snapshot.line_value == null ? "—" : `${snapshot.line_value > 0 ? "+" : ""}${snapshot.line_value}`;
  const odds = snapshot.american_odds == null ? "" : ` / ${snapshot.american_odds > 0 ? "+" : ""}${snapshot.american_odds}`;
  return `${line}${odds}`;
}

function MarketRow({ market, game, snapshotsBySelection }: { market: Market; game?: Game; snapshotsBySelection: Map<number, OddsSnapshot[]> }) {
  const selection = market.selections[0];
  const history = selection ? snapshotsBySelection.get(selection.id) ?? [] : [];
  const first = history[0];
  const current = history[history.length - 1];
  return <article className="market-row"><div className="market-ident"><strong>{marketLabel(market)}</strong><span>{game ? `${teamLabel(game.away_team_id)} at ${teamLabel(game.home_team_id)}` : `Game ${market.game_id}`} · {market.status}</span></div><div className="market-selections">{market.selections.slice(0, 3).map((item) => { const itemHistory = snapshotsBySelection.get(item.id) ?? []; return <span key={item.id}>{item.side || item.selection_key}<b>{snapshotLine(itemHistory[itemHistory.length - 1])}</b></span>; })}</div><div className="movement"><MovementStrip history={history} /><small>{first ? snapshotLine(first) : "Opening —"} <i>→</i> {current ? snapshotLine(current) : "Current —"}</small></div></article>;
}

function MovementStrip({ history }: { history: OddsSnapshot[] }) {
  const values = history.map((snapshot) => snapshot.line_value).filter((value): value is number => value != null);
  if (values.length < 2) return <span className="movement-empty">No movement</span>;
  const minimum = Math.min(...values);
  const maximum = Math.max(...values);
  const spread = maximum - minimum || 1;
  const points = values.map((value, index) => `${(index / (values.length - 1)) * 96 + 2},${30 - ((value - minimum) / spread) * 24}`).join(" ");
  return <svg className="movement-chart" viewBox="0 0 100 32" role="img" aria-label={`${values.length} stored line observations`}><polyline points={points} fill="none" vectorEffect="non-scaling-stroke" /></svg>;
}

function PanelEmpty({ text }: { text: string }) { return <div className="panel-empty"><span>—</span><p>{text}</p></div>; }

function LoadingState() { return <section className="loading-board" aria-label="Loading dashboard"><div className="loader-line" /><div className="loader-line short" /><p>Reading the board…</p></section>; }

function EmptyState() { return <section className="empty-state"><span className="eyebrow">Clear board</span><h2>No fixtures in the feed yet.</h2><p>When the Railway API has games or picks, they&apos;ll show up here automatically.</p></section>; }
