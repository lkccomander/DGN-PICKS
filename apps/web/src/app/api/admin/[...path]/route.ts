import { NextRequest, NextResponse } from "next/server";

const DEFAULT_API_URL = "https://dgn-picks-production.up.railway.app";

function upstreamUrl(path: string[], request: NextRequest) {
  const base = (process.env.DGN_API_INTERNAL_URL ?? process.env.NEXT_PUBLIC_API_URL ?? DEFAULT_API_URL).replace(/\/$/, "");
  return `${base}/api/v1/${path.join("/")}${request.nextUrl.search}`;
}

export async function ALL(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params;
  const headers = new Headers(request.headers);
  headers.delete("host");
  headers.delete("content-length");
  const response = await fetch(upstreamUrl(path, request), {
    method: request.method,
    headers,
    body: request.method === "GET" || request.method === "HEAD" ? undefined : await request.arrayBuffer(),
    cache: "no-store",
  });
  return new NextResponse(response.body, { status: response.status, headers: { "Content-Type": response.headers.get("Content-Type") ?? "application/json" } });
}

export const GET = ALL;
export const POST = ALL;
export const PATCH = ALL;
export const DELETE = ALL;
