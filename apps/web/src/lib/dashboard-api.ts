import { type Components } from "./generated-api-client";

export const API_URL = (process.env.NEXT_PUBLIC_API_URL ?? "https://dgn-picks-production.up.railway.app").replace(/\/$/, "");

type ApiGame = Components["schemas"]["GameResponse"];
type ApiMarket = Components["schemas"]["MarketResponse"];
type ApiOddsSnapshot = Components["schemas"]["OddsSnapshotResponse"];
type ApiPick = Components["schemas"]["PickResponse"];
type ApiSummary = Components["schemas"]["AnalyticsSummary"];
type ApiSeedPickDefinition = Components["schemas"]["SeedPickDefinitionResponse"];

export type Game = ApiGame;
export type Team = Components["schemas"]["TeamResponse"];
export type Selection = Components["schemas"]["SelectionResponse"];
export type Market = ApiMarket;
export type OddsSnapshot = Omit<ApiOddsSnapshot, "line_value" | "american_odds" | "decimal_odds"> & {
  line_value?: number | null;
  american_odds?: number | null;
  decimal_odds: number;
};
export type Pick = Omit<ApiPick, "line_value" | "american_odds" | "decimal_odds" | "stake_units" | "profit_units"> & {
  line_value?: number | null;
  american_odds?: number | null;
  decimal_odds?: number | null;
  stake_units: number;
  profit_units?: number | null;
};
export type Summary = Omit<ApiSummary, "total_units_risked" | "profit_units" | "roi"> & {
  total_units_risked: number;
  profit_units: number;
  roi: number | null;
};
export type SeedPickDefinition = Omit<ApiSeedPickDefinition, "state"> & {
  state: "tracked" | "unmatched" | "unresolved";
};

export type DashboardData = {
  games: Game[];
  picks: Pick[];
  summary: Summary;
  markets: Market[];
  history: OddsSnapshot[];
  teams: Team[];
  definitions: SeedPickDefinition[];
};

function normalizeSummary(summary: ApiSummary): Summary {
  return {
    ...summary,
    total_units_risked: Number(summary.total_units_risked),
    profit_units: Number(summary.profit_units),
    roi: summary.roi == null ? null : Number(summary.roi),
  };
}

function normalizePick(pick: ApiPick): Pick {
  return {
    ...pick,
    line_value: pick.line_value == null ? null : Number(pick.line_value),
    american_odds: pick.american_odds == null ? null : Number(pick.american_odds),
    decimal_odds: pick.decimal_odds == null ? null : Number(pick.decimal_odds),
    stake_units: Number(pick.stake_units),
    profit_units: pick.profit_units == null ? null : Number(pick.profit_units),
  };
}

function normalizeSnapshot(snapshot: ApiOddsSnapshot): OddsSnapshot {
  return {
    ...snapshot,
    line_value: snapshot.line_value == null ? null : Number(snapshot.line_value),
    american_odds: snapshot.american_odds == null ? null : Number(snapshot.american_odds),
    decimal_odds: Number(snapshot.decimal_odds),
  };
}

function normalizeSeedPickDefinition(definition: ApiSeedPickDefinition): SeedPickDefinition {
  const state = ["tracked", "unmatched", "unresolved"].includes(definition.state)
    ? definition.state as SeedPickDefinition["state"]
    : "unmatched";
  return { ...definition, state };
}

export async function fetchDashboardData(user: string, signal?: AbortSignal): Promise<DashboardData> {
  const response = await fetch(`/api/dashboard?user=${encodeURIComponent(user)}`, {
    cache: "no-store",
    headers: { Accept: "application/json" },
    signal,
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Dashboard API returned ${response.status}`);
  }
  const { games, picks, summary, teams, definitions, markets, history } = await response.json() as {
    games: Game[];
    picks: ApiPick[];
    summary: ApiSummary;
    teams: Team[];
    definitions: ApiSeedPickDefinition[];
    markets: Market[];
    history: ApiOddsSnapshot[];
  };
  return { games, picks: picks.map(normalizePick), summary: normalizeSummary(summary), markets, history: history.map(normalizeSnapshot), teams, definitions: definitions.map(normalizeSeedPickDefinition) };
}
