import { NextResponse } from "next/server";

type PickRequest = { user?: unknown; stake_units?: unknown; notes?: unknown; result?: unknown };

function writesEnabled(request: Request) {
  return Boolean(request.headers.get("authorization")) || (process.env.DGN_WEB_WRITE_MODE === "development" && Boolean(process.env.DGN_API_WRITE_KEY));
}

function apiUrl() {
  return (process.env.DGN_API_INTERNAL_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");
}

async function forward(request: Request, pickId: string, method: "PATCH" | "DELETE") {
  if (!writesEnabled(request)) {
    return NextResponse.json({ detail: "Development pick writes are disabled" }, { status: 404 });
  }
  const url = new URL(request.url);
  let body: PickRequest = {};
  if (method === "PATCH") {
    try {
      body = await request.json() as PickRequest;
    } catch {
      return NextResponse.json({ detail: "Invalid JSON body" }, { status: 400 });
    }
    if (typeof body.user !== "string" || (body.stake_units !== undefined && (typeof body.stake_units !== "number" || body.stake_units <= 0)) || (body.notes !== undefined && body.notes !== null && typeof body.notes !== "string") || (body.result !== undefined && !["win", "loss", "push", "void"].includes(String(body.result)))) {
      return NextResponse.json({ detail: "A valid user, stake, or note is required" }, { status: 400 });
    }
  } else {
    const user = url.searchParams.get("user");
    if (!user) return NextResponse.json({ detail: "User is required" }, { status: 400 });
    body = { user };
  }

  const isGrade = method === "PATCH" && body.result !== undefined;
  const authorization = request.headers.get("authorization");
  const response = await fetch(`${apiUrl()}/api/v1/picks/${encodeURIComponent(pickId)}${isGrade ? "/grade" : method === "DELETE" ? `?user=${encodeURIComponent(String(body.user))}` : ""}`, {
    method,
    headers: {
      Accept: "application/json",
      ...(method === "PATCH" ? { "Content-Type": "application/json" } : {}),
      ...(authorization ? { Authorization: authorization } : { "X-DGN-Write-Key": process.env.DGN_API_WRITE_KEY as string }),
    },
    ...(method === "PATCH" ? { body: JSON.stringify(isGrade ? { result: body.result } : body) } : {}),
    cache: "no-store",
  });
  const responseBody = await response.text();
  return new NextResponse(responseBody, {
    status: response.status,
    headers: { "Content-Type": response.headers.get("Content-Type") ?? "application/json" },
  });
}

export async function PATCH(request: Request, context: { params: Promise<{ pickId: string }> }) {
  return forward(request, (await context.params).pickId, "PATCH");
}

export async function DELETE(request: Request, context: { params: Promise<{ pickId: string }> }) {
  return forward(request, (await context.params).pickId, "DELETE");
}
