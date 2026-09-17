import { NextRequest, NextResponse } from "next/server";

const DEFAULT_API_URL = "https://dgn-picks-production.up.railway.app";

function upstreamUrl(path: string[], request: NextRequest) {
  const base = (process.env.DGN_API_INTERNAL_URL ?? process.env.NEXT_PUBLIC_API_URL ?? DEFAULT_API_URL).replace(/\/$/, "");
  return `${base}/api/v1/auth/${path.join("/")}${request.nextUrl.search}`;
}

export async function POST(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params;
  const response = await fetch(upstreamUrl(path, request), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: await request.arrayBuffer(),
    cache: "no-store",
  });
  return new NextResponse(response.body, {
    status: response.status,
    headers: { "Content-Type": response.headers.get("Content-Type") ?? "application/json" },
  });
}
