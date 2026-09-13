import { NextResponse } from "next/server";

type PickRequest = {
  user?: unknown;
  game_id?: unknown;
  market_id?: unknown;
  selection_id?: unknown;
  stake_units?: unknown;
  notes?: unknown;
};

function writesEnabled(request: Request) {
  return Boolean(request.headers.get("authorization")) || (process.env.DGN_WEB_WRITE_MODE === "development" && Boolean(process.env.DGN_API_WRITE_KEY));
}

function validPickRequest(value: PickRequest) {
  return typeof value.user === "string"
    && typeof value.game_id === "number"
    && typeof value.market_id === "number"
    && typeof value.selection_id === "number"
    && typeof value.stake_units === "number"
    && value.game_id > 0
    && value.market_id > 0
    && value.selection_id > 0
    && value.stake_units > 0
    && (value.notes == null || typeof value.notes === "string");
}

export async function POST(request: Request) {
  if (!writesEnabled(request)) {
    return NextResponse.json({ detail: "Development pick writes are disabled" }, { status: 404 });
  }

  let payload: PickRequest;
  try {
    payload = await request.json() as PickRequest;
  } catch {
    return NextResponse.json({ detail: "Invalid JSON body" }, { status: 400 });
  }
  if (!validPickRequest(payload)) {
    return NextResponse.json({ detail: "A resolved selection and positive stake are required" }, { status: 400 });
  }

  const apiUrl = (process.env.DGN_API_INTERNAL_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");
  const authorization = request.headers.get("authorization");
  const response = await fetch(`${apiUrl}/api/v1/picks`, {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
      ...(authorization ? { Authorization: authorization } : { "X-DGN-Write-Key": process.env.DGN_API_WRITE_KEY as string }),
    },
    body: JSON.stringify(payload),
    cache: "no-store",
  });
  const body = await response.text();
  return new NextResponse(body, {
    status: response.status,
    headers: { "Content-Type": response.headers.get("Content-Type") ?? "application/json" },
  });
}
