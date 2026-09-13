"use client";

import { useCallback, useEffect, useMemo, useState, type FormEvent } from "react";
import {
  API_URL,
  fetchDashboardData,
  type DashboardData,
  type Game,
  type Market,
  type OddsSnapshot,
  type Pick,
  type SeedPickDefinition,
  type Summary,
  type Team,
} from "@/lib/dashboard-api";

const ACTIVE_USER = "gato";
const DEVELOPMENT_PICK_WRITES = process.env.NEXT_PUBLIC_ENABLE_DEV_PICK_WRITES === "true";

function browserAuthHeaders() {
  if (typeof window === "undefined") return {};
  const token = window.localStorage.getItem("dgn-admin-token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

type ResultFilter = "all" | Pick["result"];
type PickDraft = { gameId: number; marketId: number; selectionId: number; description: string };

const emptySummary: Summary = { wins: 0, losses: 0, pushes: 0, pending: 0, void: 0, total_units_risked: 0, profit_units: 0, roi: null };

function formatKickoff(value: string) {
  return new Intl.DateTimeFormat("en-US", { weekday: "short", month: "short", day: "numeric", hour: "numeric", minute: "2-digit" }).format(new Date(value));
}

function teamLabel(id: number, teamsById?: Map<number, Team>) { return teamsById?.get(id)?.short_name || `Team ${id}`; }

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
  const [teamFilter, setTeamFilter] = useState("all");
  const [conferenceFilter, setConferenceFilter] = useState("all");
  const [boardDate, setBoardDate] = useState("");
  const [marketStatusFilter, setMarketStatusFilter] = useState<"all" | Market["status"]>("all");
  const [selectedGameId, setSelectedGameId] = useState<number | null>(null);
  const [pickDraft, setPickDraft] = useState<PickDraft | null>(null);
  const [stakeUnits, setStakeUnits] = useState("1");
  const [pickNotes, setPickNotes] = useState("");
  const [pickError, setPickError] = useState<string | null>(null);
  const [savingPick, setSavingPick] = useState(false);
  const [hasAdminToken, setHasAdminToken] = useState(false);
  const [editingPick, setEditingPick] = useState<Pick | null>(null);
  const [editStake, setEditStake] = useState("1");
  const [editNotes, setEditNotes] = useState("");

  const loadDashboard = useCallback(async (signal?: AbortSignal) => {
    setLoading(true);
    setError(null);
    try {
      setData(await fetchDashboardData(ACTIVE_USER, signal));
    } catch (requestError) {
      if (requestError instanceof DOMException && requestError.name === "AbortError") return;
      setError(requestError instanceof Error ? requestError.message : "Unable to reach the picks API.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    setHasAdminToken(Boolean(window.localStorage.getItem("dgn-admin-token")));
    const controller = new AbortController();
    fetchDashboardData(ACTIVE_USER, controller.signal)
      .then(setData)
      .catch((requestError: unknown) => {
        if (requestError instanceof DOMException && requestError.name === "AbortError") return;
        setError(requestError instanceof Error ? requestError.message : "Unable to reach the picks API.");
      })
      .finally(() => setLoading(false));
    return () => controller.abort();
  }, []);

  const gamesById = useMemo(() => new Map((data?.games ?? []).map((game) => [game.id, game])), [data?.games]);
  const teamsById = useMemo(() => new Map((data?.teams ?? []).map((team) => [team.id, team])), [data?.teams]);
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
      const searchable = `${pick.notes ?? ""} ${pick.market_id} ${pick.selection_id ?? ""} ${game ? `${teamLabel(game.away_team_id, teamsById)} ${teamLabel(game.home_team_id, teamsById)}` : ""}`.toLowerCase();
      return (resultFilter === "all" || pick.result === resultFilter) && (!normalizedQuery || searchable.includes(normalizedQuery));
    });
  }, [data?.picks, gamesById, query, resultFilter, teamsById]);
  const visibleDefinitions = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    return (data?.definitions ?? []).filter((definition) => definition.state !== "tracked"
      && resultFilter === "all"
      && (!normalizedQuery || definition.description.toLowerCase().includes(normalizedQuery)));
  }, [data?.definitions, query, resultFilter]);
  const visibleGames = useMemo(() => (data?.games ?? []).filter((game) => {
    const home = teamsById.get(game.home_team_id);
    const away = teamsById.get(game.away_team_id);
    const gameDate = game.kickoff_at.slice(0, 10);
    return (gameFilter === "all" || game.status === gameFilter)
      && (!boardDate || gameDate === boardDate)
      && (teamFilter === "all" || game.home_team_id.toString() === teamFilter || game.away_team_id.toString() === teamFilter)
      && (conferenceFilter === "all" || home?.conference === conferenceFilter || away?.conference === conferenceFilter);
  }), [boardDate, conferenceFilter, data?.games, gameFilter, teamFilter, teamsById]);
  const visibleGameIds = useMemo(() => new Set(visibleGames.map((game) => game.id)), [visibleGames]);
  const visibleMarkets = useMemo(() => (data?.markets ?? []).filter((market) => visibleGameIds.has(market.game_id) && (marketStatusFilter === "all" || market.status === marketStatusFilter)), [data?.markets, marketStatusFilter, visibleGameIds]);
  const conferences = useMemo(() => [...new Set((data?.teams ?? []).map((team) => team.conference).filter(Boolean))].sort(), [data?.teams]);

  const beginPick = useCallback((market: Market, selection: { id: number; selection_key: string; side?: string | null }) => {
    setPickDraft({ gameId: market.game_id, marketId: market.id, selectionId: selection.id, description: `${marketLabel(market)} · ${selection.side || selection.selection_key}` });
    setPickError(null);
  }, []);

  const submitPick = useCallback(async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!pickDraft) return;
    const stake = Number(stakeUnits);
    if (!Number.isFinite(stake) || stake <= 0) {
      setPickError("Enter a positive stake in units.");
      return;
    }
    setSavingPick(true);
    setPickError(null);
    try {
      const response = await fetch("/api/development/picks", {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json", ...browserAuthHeaders() },
        body: JSON.stringify({
          user: ACTIVE_USER,
          game_id: pickDraft.gameId,
          market_id: pickDraft.marketId,
          selection_id: pickDraft.selectionId,
          stake_units: stake,
          notes: pickNotes.trim() || null,
        }),
      });
      if (!response.ok) {
        const failure = await response.json().catch(() => null) as { detail?: string } | null;
        throw new Error(failure?.detail || "The pick could not be saved.");
      }
      setPickDraft(null);
      setPickNotes("");
      await loadDashboard();
    } catch (submitError) {
      setPickError(submitError instanceof Error ? submitError.message : "The pick could not be saved.");
    } finally {
      setSavingPick(false);
    }
  }, [loadDashboard, pickDraft, pickNotes, stakeUnits]);
  const mutatePick = useCallback(async (pick: Pick, method: "PATCH" | "DELETE", body?: Record<string, unknown>) => {
    setPickError(null);
    setSavingPick(true);
    try {
      const response = await fetch(`/api/development/picks/${pick.id}${method === "DELETE" ? `?user=${ACTIVE_USER}` : ""}`, {
        method,
        headers: { "Content-Type": "application/json", Accept: "application/json", ...browserAuthHeaders() },
        ...(body ? { body: JSON.stringify({ user: ACTIVE_USER, ...body }) } : {}),
      });
      if (!response.ok) {
        const failure = await response.json().catch(() => null) as { detail?: string } | null;
        throw new Error(failure?.detail || "The pick could not be updated.");
      }
      setEditingPick(null);
      await loadDashboard();
    } catch (mutationError) {
      setPickError(mutationError instanceof Error ? mutationError.message : "The pick could not be updated.");
    } finally {
      setSavingPick(false);
    }
  }, [loadDashboard]);
  const submitEdit = useCallback(async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!editingPick) return;
    const stake = Number(editStake);
    if (!Number.isFinite(stake) || stake <= 0) {
      setPickError("Enter a positive stake in units.");
      return;
    }
    await mutatePick(editingPick, "PATCH", { stake_units: stake, notes: editNotes.trim() || null });
  }, [editNotes, editStake, editingPick, mutatePick]);
  const selectedGame = selectedGameId == null ? null : gamesById.get(selectedGameId) ?? null;
  const selectedGameMarkets = selectedGame == null ? [] : (data?.markets ?? []).filter((market) => market.game_id === selectedGame.id);

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
              <PanelHeading eyebrow="Your card · gato" title="Tracked picks" count={visiblePicks.length + visibleDefinitions.length} />
              <div className="panel-tools">
                <label className="search-box"><span className="sr-only">Search picks</span><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search picks" /></label>
                <label className="filter-box"><span className="sr-only">Filter result</span><select value={resultFilter} onChange={(event) => setResultFilter(event.target.value as ResultFilter)}><option value="all">All results</option><option value="pending">Pending</option><option value="win">Wins</option><option value="loss">Losses</option><option value="push">Pushes</option><option value="void">Voids</option></select></label>
              </div>
              <div className="table-head"><span>Selection</span><span>Line / price</span><span>Risk</span><span>Status</span></div>
              {visiblePicks.length || visibleDefinitions.length ? <div className="pick-list">{visiblePicks.map((pick) => <PickRow key={pick.id} pick={pick} game={gamesById.get(pick.game_id)} teamsById={teamsById} canManage={DEVELOPMENT_PICK_WRITES || hasAdminToken} onEdit={(value) => { setEditingPick(value); setEditStake(value.stake_units.toString()); setEditNotes(value.notes ?? ""); setPickError(null); }} onDelete={(value) => { if (window.confirm("Delete this pending pick?")) void mutatePick(value, "DELETE"); }} onGrade={(value, result) => void mutatePick(value, "PATCH", { result })} />)}{visibleDefinitions.map((definition) => <SeedDefinitionRow key={definition.number} definition={definition} />)}</div> : <PanelEmpty text={data.picks.length ? "No picks match the current filters." : "No picks have been recorded for this user yet."} />}
            </section>
            <aside id="games" className="panel games-panel">
              <PanelHeading eyebrow="The slate" title="Games" count={visibleGames.length} />
              <div className="game-controls"><label>Date<input type="date" value={boardDate} onChange={(event) => setBoardDate(event.target.value)} /></label><label>Conference<select value={conferenceFilter} onChange={(event) => setConferenceFilter(event.target.value)}><option value="all">All conferences</option>{conferences.map((conference) => <option key={conference} value={conference}>{conference}</option>)}</select></label><label>Team<select value={teamFilter} onChange={(event) => setTeamFilter(event.target.value)}><option value="all">All teams</option>{(data.teams ?? []).filter((team) => team.active).map((team) => <option key={team.id} value={team.id}>{team.short_name}</option>)}</select></label></div>
              <div className="game-filter" role="group" aria-label="Filter games"><button type="button" aria-pressed={gameFilter === "all"} className={gameFilter === "all" ? "selected" : ""} onClick={() => setGameFilter("all")}>All</button><button type="button" aria-pressed={gameFilter === "scheduled"} className={gameFilter === "scheduled" ? "selected" : ""} onClick={() => setGameFilter("scheduled")}>Scheduled</button><button type="button" aria-pressed={gameFilter === "live"} className={gameFilter === "live" ? "selected" : ""} onClick={() => setGameFilter("live")}>Live</button><button type="button" aria-pressed={gameFilter === "final"} className={gameFilter === "final" ? "selected" : ""} onClick={() => setGameFilter("final")}>Final</button></div>
              {visibleGames.length ? <div className="game-list">{visibleGames.slice(0, 6).map((game) => <GameRow key={game.id} game={game} teamsById={teamsById} onSelect={setSelectedGameId} />)}</div> : <PanelEmpty text={data.games.length ? "No games match this filter." : "No games are available for this board."} />}
              <div className="panel-foot">Source · Railway API <span>UTC timestamps</span></div>
            </aside>
          </div>
          {selectedGame ? <section id="game-detail" className="panel game-detail" aria-labelledby="game-detail-title">
            <PanelHeading eyebrow="Selected matchup" title="Game detail" count={selectedGameMarkets.length} />
            <div className="game-detail-grid"><div><h3 id="game-detail-title">{teamLabel(selectedGame.away_team_id, teamsById)} at {teamLabel(selectedGame.home_team_id, teamsById)}</h3><p>{formatKickoff(selectedGame.kickoff_at)} · {selectedGame.venue || "Venue pending"}</p></div><div><span>Status</span><strong>{selectedGame.status}</strong></div><div><span>Markets</span><strong>{selectedGameMarkets.length}</strong></div>{selectedGame.status === "final" ? <div><span>Score</span><strong>{selectedGame.away_score ?? "—"} – {selectedGame.home_score ?? "—"}</strong></div> : null}</div>
          </section> : null}
          <section id="markets" className="panel market-panel">
            <PanelHeading eyebrow="The board" title="Market movement" count={visibleMarkets.length} />
            <div className="market-tools"><label>Availability<select value={marketStatusFilter} onChange={(event) => setMarketStatusFilter(event.target.value as "all" | Market["status"])}><option value="all">All markets</option><option value="open">Open</option><option value="suspended">Suspended</option><option value="closed">Closed</option></select></label></div>
            {visibleMarkets.length ? <div className="market-list">{visibleMarkets.slice(0, 12).map((market) => <MarketRow key={market.id} market={market} game={gamesById.get(market.game_id)} teamsById={teamsById} snapshotsBySelection={snapshotsBySelection} canTrack={DEVELOPMENT_PICK_WRITES || hasAdminToken} onTrack={beginPick} />)}</div> : <PanelEmpty text="No market lines are available for the current slate." />}
            <div className="panel-foot">Opening → current <span>Persisted snapshots · local-fixture</span></div>
          </section>
          {pickDraft ? <section className="pick-dialog" role="dialog" aria-modal="true" aria-labelledby="pick-dialog-title">
            <form onSubmit={submitPick}>
              <div><span className="eyebrow">Development entry</span><h2 id="pick-dialog-title">Track {pickDraft.description}</h2><p>The API records the current stored line and price; the browser never receives the write key.</p></div>
              <label>Stake (units)<input name="stake" type="number" min="0.1" step="0.1" value={stakeUnits} onChange={(event) => setStakeUnits(event.target.value)} required /></label>
              <label>Note (optional)<input name="notes" maxLength={1000} value={pickNotes} onChange={(event) => setPickNotes(event.target.value)} placeholder="Why this play?" /></label>
              {pickError ? <p className="pick-form-error" role="alert">{pickError}</p> : null}
              <div className="pick-dialog-actions"><button type="button" onClick={() => setPickDraft(null)} disabled={savingPick}>Cancel</button><button type="submit" disabled={savingPick}>{savingPick ? "Saving…" : "Create pick"}</button></div>
            </form>
          </section> : null}
          {editingPick ? <section className="pick-dialog" role="dialog" aria-modal="true" aria-labelledby="edit-pick-dialog-title">
            <form onSubmit={submitEdit}>
              <div><span className="eyebrow">Development edit</span><h2 id="edit-pick-dialog-title">Edit pick</h2><p>The taken line and price remain locked. Only pending stake and notes can change.</p></div>
              <label>Stake (units)<input name="edit-stake" type="number" min="0.1" step="0.1" value={editStake} onChange={(event) => setEditStake(event.target.value)} required /></label>
              <label>Note (optional)<input name="edit-notes" maxLength={1000} value={editNotes} onChange={(event) => setEditNotes(event.target.value)} /></label>
              {pickError ? <p className="pick-form-error" role="alert">{pickError}</p> : null}
              <div className="pick-dialog-actions"><button type="button" onClick={() => setEditingPick(null)} disabled={savingPick}>Cancel</button><button type="submit" disabled={savingPick}>{savingPick ? "Saving…" : "Save changes"}</button></div>
            </form>
          </section> : null}
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

function PickRow({ pick, game, teamsById, canManage, onEdit, onDelete, onGrade }: { pick: Pick; game?: Game; teamsById: Map<number, Team>; canManage: boolean; onEdit: (pick: Pick) => void; onDelete: (pick: Pick) => void; onGrade: (pick: Pick, result: "win" | "loss" | "push" | "void") => void }) {
  return <article className="pick-row"><div className="pick-main"><span className={`result-dot ${pick.result}`} /><div><strong>{pick.notes || `Market ${pick.market_id} · Selection ${pick.selection_id ?? "—"}`}</strong><span>{game ? `${teamLabel(game.away_team_id, teamsById)} at ${teamLabel(game.home_team_id, teamsById)}` : `Game ${pick.game_id}`}</span></div></div><span className="pick-line">{lineLabel(pick)}</span><span className="pick-stake">{pick.stake_units.toFixed(1)}u</span><span className={`status-pill ${pick.result}`}>{pick.result}</span>{canManage ? <div className="pick-actions">{pick.result === "pending" ? <><button type="button" onClick={() => onEdit(pick)}>Edit</button><button type="button" onClick={() => onDelete(pick)}>Delete</button><button type="button" onClick={() => onGrade(pick, "win")}>Win</button><button type="button" onClick={() => onGrade(pick, "loss")}>Loss</button></> : null}</div> : null}</article>;
}

function SeedDefinitionRow({ definition }: { definition: SeedPickDefinition }) {
  const status = definition.state === "unresolved" ? "side unresolved" : "fixture unmatched";
  return <article className="pick-row seed-definition"><div className="pick-main"><span className="result-dot" /><div><strong>{definition.description}</strong><span>Seed definition #{definition.number} · {definition.team_or_player}</span></div></div><span className="pick-line">{Number(definition.line_value) > 0 ? "+" : ""}{definition.line_value}</span><span className="pick-stake">—</span><span className="status-pill">{status}</span></article>;
}

function GameRow({ game, teamsById, onSelect }: { game: Game; teamsById: Map<number, Team>; onSelect: (gameId: number) => void }) {
  const isFinal = game.status === "final";
  return <button type="button" className="game-row game-select" onClick={() => onSelect(game.id)}><div className="game-time"><span className={game.status === "live" ? "live-label" : ""}>{game.status === "live" ? "Live" : isFinal ? "Final" : formatKickoff(game.kickoff_at)}</span><small>{game.venue || `Game ${game.id}`}</small></div><div className="matchup"><span>{teamLabel(game.away_team_id, teamsById)} {isFinal && game.away_score != null ? <b>{game.away_score}</b> : null}</span><span>{teamLabel(game.home_team_id, teamsById)} {isFinal && game.home_score != null ? <b>{game.home_score}</b> : null}</span></div><span className="chevron" aria-hidden="true">›</span></button>;
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

function MarketRow({ market, game, teamsById, snapshotsBySelection, canTrack, onTrack }: { market: Market; game?: Game; teamsById: Map<number, Team>; snapshotsBySelection: Map<number, OddsSnapshot[]>; canTrack: boolean; onTrack: (market: Market, selection: { id: number; selection_key: string; side?: string | null }) => void }) {
  const selections = market.selections ?? [];
  const selection = selections[0];
  const history = selection ? snapshotsBySelection.get(selection.id) ?? [] : [];
  const first = history[0];
  const current = history[history.length - 1];
  return <article className="market-row"><div className="market-ident"><strong>{marketLabel(market)}</strong><span>{game ? `${teamLabel(game.away_team_id, teamsById)} at ${teamLabel(game.home_team_id, teamsById)}` : `Game ${market.game_id}`} · {market.status}</span></div><div className="market-selections">{selections.slice(0, 3).map((item) => { const itemHistory = snapshotsBySelection.get(item.id) ?? []; return <span key={item.id}>{item.side || item.selection_key}<b>{snapshotLine(itemHistory[itemHistory.length - 1])}</b>{canTrack && market.status === "open" && item.side ? <button type="button" className="track-selection" onClick={() => onTrack(market, item)}>Track {item.side}</button> : null}</span>; })}</div><div className="movement"><MovementStrip history={history} /><small>{first ? snapshotLine(first) : "Opening —"} <i>→</i> {current ? snapshotLine(current) : "Current —"}</small></div></article>;
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
