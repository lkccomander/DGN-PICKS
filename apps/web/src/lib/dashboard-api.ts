import { DgnPicksApiClient, type Components } from "./generated-api-client";

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

const client = new DgnPicksApiClient(API_URL);

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
  const [games, picks, summary, teams, definitions] = await Promise.all([
    client.get<Game[]>("/api/v1/games", signal),
    client.get<ApiPick[]>(`/api/v1/picks?user=${encodeURIComponent(user)}`, signal),
    client.get<ApiSummary>("/api/v1/analytics/summary", signal),
    client.get<Team[]>("/api/v1/teams", signal),
    client.get<ApiSeedPickDefinition[]>(`/api/v1/seed/pick-definitions?user=${encodeURIComponent(user)}`, signal),
  ]);
  const markets = (await Promise.all(
    games.map((game) => client.get<Market[]>(`/api/v1/games/${game.id}/markets`, signal)),
  )).flat();
  const history = (await Promise.all(
    markets.map((market) => client.get<ApiOddsSnapshot[]>(`/api/v1/markets/${market.id}/history`, signal)),
  )).flat().map(normalizeSnapshot);
  return { games, picks: picks.map(normalizePick), summary: normalizeSummary(summary), markets, history, teams, definitions: definitions.map(normalizeSeedPickDefinition) };
}
