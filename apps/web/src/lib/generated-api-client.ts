/*
 * GENERATED FILE — do not edit by hand.
 * Source: packages/api-client/openapi.json
 * Regenerate: PYTHONPATH=apps/api/src .venv/bin/python scripts/generate_api_client.py
 */

export type Components = {
  schemas: {
      "AccountResponse": { "username" : string; "role" : string; "display_name" : string; "email"?: string | null; "country"?: string | null };
      "AnalyticsSummary": { "wins" : number; "losses" : number; "pushes" : number; "pending" : number; "void" : number; "total_units_risked" : string; "profit_units" : string | null; "roi" : string | null; "pending_units"?: string; "unpriced_settled_count"?: number };
      "AuthResponse": { "access_token" : string; "token_type"?: string; "username" : string; "role" : string };
      "GameCreate": { "external_ids"?: Record<string, unknown>; "season" : number; "week" : number; "kickoff_at" : string; "home_team_id" : number; "away_team_id" : number; "venue"?: string | null; "status"?: Components["schemas"]["GameStatus"]; "home_score"?: number | null; "away_score"?: number | null };
      "GameResponse": { "id" : number; "external_ids"?: Record<string, unknown>; "season" : number; "sport" : string; "league" : string; "week" : number; "kickoff_at" : string; "home_team_id" : number; "away_team_id" : number; "venue"?: string | null; "status" : Components["schemas"]["GameStatus"]; "home_score"?: number | null; "away_score"?: number | null };
      "GameStatus": "scheduled" | "live" | "final" | "postponed" | "cancelled";
      "GameUpdate": { "external_ids"?: Record<string, unknown> | null; "season"?: number | null; "week"?: number | null; "kickoff_at"?: string | null; "home_team_id"?: number | null; "away_team_id"?: number | null; "venue"?: string | null; "status"?: Components["schemas"]["GameStatus"] | null; "home_score"?: number | null; "away_score"?: number | null };
      "HTTPValidationError": { "detail"?: Array<Components["schemas"]["ValidationError"]> };
      "HealthResponse": { "status" : string; "service" : string };
      "ImportGame": { "key" : string; "kickoff_at" : string; "season" : number; "week" : number; "status" : Components["schemas"]["GameStatus"]; "home_team" : Components["schemas"]["ImportTeam"]; "away_team" : Components["schemas"]["ImportTeam"]; "source_urls" : Array<string> };
      "ImportPick": { "key" : string; "game_key" : string; "player_name" : string; "player_team" : "home" | "away"; "player_position" : string; "original_text" : string; "description" : string; "market_type" : "player_rushing_yards" | "player_passing_yards" | "player_receiving_yards"; "side" : "over" | "under"; "line_value" : number | string; "american_odds"?: number | null; "decimal_odds"?: number | string | null; "stake_units"?: number | string; "source_urls" : Array<string> };
      "ImportTeam": { "name" : string; "short_name" : string; "abbreviation" : string; "conference" : string };
      "LoginRequest": { "username" : string; "password" : string };
      "MarketCreate": { "game_id" : number; "market_type" : string; "period"?: string; "player_id"?: number | null; "team_id"?: number | null; "status"?: Components["schemas"]["MarketStatus"] };
      "MarketResponse": { "id" : number; "game_id" : number; "market_type" : string; "period" : string; "player_id"?: number | null; "team_id"?: number | null; "status" : Components["schemas"]["MarketStatus"]; "selections"?: Array<Components["schemas"]["SelectionResponse"]> };
      "MarketStatus": "open" | "suspended" | "closed";
      "MarketUpdate": { "market_type"?: string | null; "period"?: string | null; "player_id"?: number | null; "team_id"?: number | null; "status"?: Components["schemas"]["MarketStatus"] | null };
      "OddsSnapshotCreate": { "selection_id" : number; "sportsbook_id" : number; "observed_at" : string; "line_value"?: number | string | null; "american_odds"?: number | null; "decimal_odds" : number | string; "implied_probability"?: number | string | null; "source_event_id"?: string | null };
      "OddsSnapshotResponse": { "id" : number; "selection_id" : number; "sportsbook_id" : number; "observed_at" : string; "line_value"?: string | null; "american_odds"?: number | null; "decimal_odds" : string; "implied_probability"?: string | null; "source_event_id"?: string | null; "created_at" : string };
      "PickCreate": { "user" : string; "game_id" : number; "market_id" : number; "selection_id"?: number | null; "stake_units" : number | string; "notes"?: string | null };
      "PickGrade": { "result" : Components["schemas"]["PickResult"] };
      "PickImportManifest": { "batch_key" : string; "user" : string; "source_file" : string; "pick_date" : string; "games" : Array<Components["schemas"]["ImportGame"]>; "picks" : Array<Components["schemas"]["ImportPick"]> };
      "PickResponse": { "import_metadata"?: Record<string, unknown> | null; "id" : number; "user_id" : number; "game_id" : number; "market_id" : number; "selection_id"?: number | null; "picked_at" : string; "line_value"?: string | null; "american_odds"?: number | null; "decimal_odds"?: string | null; "stake_units" : string; "result" : Components["schemas"]["PickResult"]; "profit_units"?: string | null; "notes"?: string | null };
      "PickResult": "pending" | "win" | "loss" | "push" | "void";
      "PickUpdate": { "user" : string; "stake_units"?: number | string | null; "notes"?: string | null };
      "PlayerCreate": { "external_ids"?: Record<string, unknown>; "team_id" : number; "name" : string; "position" : string; "active"?: boolean };
      "PlayerResponse": { "id" : number; "external_ids"?: Record<string, unknown>; "team_id" : number; "name" : string; "position" : string; "active" : boolean };
      "PlayerUpdate": { "external_ids"?: Record<string, unknown> | null; "team_id"?: number | null; "name"?: string | null; "position"?: string | null; "active"?: boolean | null };
      "PublicUserResponse": { "id" : number; "username" : string; "display_name" : string; "active" : boolean; "created_at" : string };
      "RegistrationRequest": { "username" : string; "email" : string; "display_name" : string; "country"?: string | null; "password" : string };
      "RegistrationResponse": { "user" : Components["schemas"]["UserResponse"]; "access_token" : string; "token_type"?: string };
      "SeedPickDefinitionResponse": { "number" : number; "description" : string; "market_type" : string; "line_value" : string; "side"?: string | null; "team_or_player" : string; "state" : string };
      "SeedReportResponse": { "users_inserted" : number; "users_existing" : number; "games_inserted" : number; "markets_inserted" : number; "snapshots_inserted" : number; "picks_inserted" : number; "duplicate_snapshots" : number; "unresolved_definitions" : Array<string>; "unresolved_count" : number };
      "SelectionCreate": { "market_id" : number; "selection_key" : string; "team_id"?: number | null; "player_id"?: number | null; "side"?: string | null };
      "SelectionResponse": { "id" : number; "market_id" : number; "selection_key" : string; "team_id"?: number | null; "player_id"?: number | null; "side"?: string | null };
      "SelectionUpdate": { "selection_key"?: string | null; "team_id"?: number | null; "player_id"?: number | null; "side"?: string | null };
      "TeamCreate": { "external_ids"?: Record<string, unknown>; "name" : string; "short_name" : string; "abbreviation" : string; "conference" : string; "logo_url"?: string | null; "active"?: boolean };
      "TeamResponse": { "id" : number; "external_ids"?: Record<string, unknown>; "name" : string; "short_name" : string; "abbreviation" : string; "conference" : string; "logo_url"?: string | null; "active" : boolean };
      "TeamUpdate": { "external_ids"?: Record<string, unknown> | null; "name"?: string | null; "short_name"?: string | null; "abbreviation"?: string | null; "conference"?: string | null; "logo_url"?: string | null; "active"?: boolean | null };
      "UserCreate": { "username" : string; "email"?: string | null; "display_name" : string; "country"?: string | null; "password"?: string | null; "active"?: boolean };
      "UserResponse": { "id" : number; "username" : string; "email"?: string | null; "display_name" : string; "country"?: string | null; "active" : boolean; "created_at" : string };
      "UserUpdate": { "email"?: string | null; "display_name"?: string | null; "country"?: string | null; "password"?: string | null; "active"?: boolean | null };
      "ValidationError": { "loc" : Array<string | number>; "msg" : string; "type" : string };
  };
};

export type ApiPath =
  | `/api/health`
  | `/api/v1/admin/pick-imports`
  | `/api/v1/admin/pick-imports/legacy-seed-quarantine`
  | `/api/v1/admin/users`
  | `/api/v1/admin/users/${number}`
  | `/api/v1/analytics/summary`
  | `/api/v1/auth/account`
  | `/api/v1/auth/login`
  | `/api/v1/auth/me`
  | `/api/v1/auth/register`
  | `/api/v1/dev/seed`
  | `/api/v1/games`
  | `/api/v1/games/${number}`
  | `/api/v1/games/${number}/markets`
  | `/api/v1/markets`
  | `/api/v1/markets/${number}`
  | `/api/v1/markets/${number}/history`
  | `/api/v1/markets/${number}/selections`
  | `/api/v1/picks`
  | `/api/v1/picks/${number}`
  | `/api/v1/picks/${number}/grade`
  | `/api/v1/players`
  | `/api/v1/players/${number}`
  | `/api/v1/seed/pick-definitions`
  | `/api/v1/selections`
  | `/api/v1/selections/${number}`
  | `/api/v1/teams`
  | `/api/v1/teams/${number}`
  | `/api/v1/users`
  | `/api/v1/users/${number}`;

export type ApiPathWithQuery = ApiPath | `${ApiPath}?${string}`;

export class ApiError extends Error {
  constructor(public readonly status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

export class DgnPicksApiClient {
  constructor(
    private readonly baseUrl: string,
    private readonly fetchImpl: typeof fetch = fetch,
  ) {}

  async request<T>(path: ApiPathWithQuery, options: RequestInit = {}): Promise<T> {
    const response = await this.fetchImpl(`${this.baseUrl}${path}`, {
      ...options,
      headers: { Accept: "application/json", ...options.headers },
    });
    if (!response.ok) {
      const detail = await response.text();
      throw new ApiError(response.status, detail || response.statusText);
    }
    if (response.status === 204) return undefined as T;
    return response.json() as Promise<T>;
  }

  get<T>(path: ApiPathWithQuery, signal?: AbortSignal): Promise<T> {
    return this.request<T>(path, { signal });
  }

  post<T>(path: ApiPathWithQuery, body: unknown, options: RequestInit = {}): Promise<T> {
    return this.request<T>(path, {
      ...options,
      method: "POST",
      body: JSON.stringify(body),
      headers: { "Content-Type": "application/json", ...options.headers },
    });
  }
}
