"""Read-only smoke check for a deployed DGN-PICKS API."""

from __future__ import annotations

import argparse
import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def get_json(base_url: str, path: str) -> object:
    request = Request(f"{base_url.rstrip('/')}{path}", headers={"Accept": "application/json"})
    with urlopen(request, timeout=15) as response:  # noqa: S310 - URL is user-provided CLI input.
        if response.status != 200:
            raise RuntimeError(f"{path}: HTTP {response.status}")
        return json.load(response)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base-url",
        default=os.getenv("DGN_API_URL", "https://dgn-picks-production.up.railway.app"),
        help="API origin without /api (default: DGN_API_URL or Railway API)",
    )
    args = parser.parse_args()
    checks = {
        "health": "/api/health",
        "teams": "/api/v1/teams",
        "games": "/api/v1/games",
        "summary": "/api/v1/analytics/summary",
    }
    try:
        results = {name: get_json(args.base_url, path) for name, path in checks.items()}
    except (HTTPError, URLError, TimeoutError, RuntimeError) as exc:
        print(f"smoke check failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"base_url": args.base_url.rstrip("/"), "checks": results}, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
