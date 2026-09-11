import { NextRequest, NextResponse } from "next/server";

const DEFAULT_API_URL = "https://dgn-picks-production.up.railway.app";
const USERNAME_PATTERN = /^[a-z0-9_-]{1,64}$/i;

type UpstreamError = Error & { status?: number };

function apiUrl() {
  return (process.env.DGN_API_INTERNAL_URL ?? process.env.NEXT_PUBLIC_API_URL ?? DEFAULT_API_URL).replace(/\/$/, "");
}

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${apiUrl()}${path}`, {
    cache: "no-store",
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    const error = new Error(`Upstream API returned ${response.status}`) as UpstreamError;
    error.status = response.status;
    throw error;
  }
  return response.json() as Promise<T>;
}

export async function GET(request: NextRequest) {
  const user = request.nextUrl.searchParams.get("user") ?? "gato";
  if (!USERNAME_PATTERN.test(user)) {
    return NextResponse.json({ detail: "Invalid user" }, { status: 400 });
  }

  try {
    const [games, picks, summary, teams, definitions] = await Promise.all([
      getJson<Array<{ id: number }>>("/api/v1/games"),
      getJson<unknown[]>(`/api/v1/picks?user=${encodeURIComponent(user)}`),
      getJson<unknown>("/api/v1/analytics/summary"),
      getJson<unknown[]>("/api/v1/teams"),
      getJson<unknown[]>(`/api/v1/seed/pick-definitions?user=${encodeURIComponent(user)}`),
    ]);
    const markets = (await Promise.all(
      games.map((game) => getJson<Array<{ id: number }>>(`/api/v1/games/${game.id}/markets`)),
    )).flat();
    const history = (await Promise.all(
      markets.map((market) => getJson<unknown[]>(`/api/v1/markets/${market.id}/history`)),
    )).flat();

    return NextResponse.json({ games, picks, summary, teams, definitions, markets, history });
  } catch (error) {
    const status = (error as UpstreamError).status;
    return NextResponse.json(
      { detail: "The DGN-PICKS API is temporarily unavailable", upstream_status: status ?? null },
      { status: 502 },
    );
  }
}
