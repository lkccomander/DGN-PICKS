import { NextRequest, NextResponse } from "next/server";

const DEFAULT_API_URL = "https://dgn-picks-production.up.railway.app";

function upstreamUrl(path: string[], request: NextRequest) {
  const base = (process.env.DGN_API_INTERNAL_URL ?? process.env.NEXT_PUBLIC_API_URL ?? DEFAULT_API_URL).replace(/\/$/, "");
  return `${base}/api/v1/auth/${path.join("/")}${request.nextUrl.search}`;
}

async function forward(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params;
  const response = await fetch(upstreamUrl(path, request), {
    method: request.method,
    headers: { "Content-Type": "application/json", ...(request.headers.get("authorization") ? { Authorization: request.headers.get("authorization")! } : {}) },
    body: request.method === "GET" ? undefined : await request.arrayBuffer(),
    cache: "no-store",
    signal: AbortSignal.timeout(15000),
    redirect: "error",
  });
  return new NextResponse(response.body, {
    status: response.status,
    headers: { "Content-Type": response.headers.get("Content-Type") ?? "application/json" },
  });
}

export const GET = forward;
export const POST = forward;
