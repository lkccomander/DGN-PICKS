"""College Football Data schedule adapter.

The adapter owns the provider payload shape. The rest of the application only
sees ``NormalizedGame`` values and UTC datetimes.
"""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from typing import Any, Callable
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from dgn_picks_api.domains.common.enums import GameStatus
from dgn_picks_api.domains.providers.contracts import NormalizedGame


class CFBDProviderError(RuntimeError):
    """Raised when CFBD cannot be queried or its payload is invalid."""


JsonFetcher = Callable[[str, dict[str, str]], Any]


def _default_fetcher(url: str, headers: dict[str, str]) -> Any:
    request = Request(url, headers=headers, method="GET")
    try:
        with urlopen(request, timeout=20) as response:  # noqa: S310 - fixed HTTPS base URL
            return json.loads(response.read().decode("utf-8"))
    except Exception as exc:  # urllib exposes several platform-specific errors
        raise CFBDProviderError(f"CFBD request failed: {exc}") from exc


def _parse_kickoff(value: Any) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise CFBDProviderError("CFBD game is missing startDate")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise CFBDProviderError(f"Invalid CFBD startDate: {value!r}") from exc
    return parsed.replace(tzinfo=UTC) if parsed.tzinfo is None else parsed.astimezone(UTC)


def _score(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise CFBDProviderError(f"Invalid CFBD score: {value!r}")
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise CFBDProviderError(f"Invalid CFBD score: {value!r}") from exc


class CFBDProvider:
    """Read NCAAFB schedules from the College Football Data API."""

    base_url = "https://api.collegefootballdata.com"

    def __init__(self, api_key: str | None = None, fetcher: JsonFetcher | None = None) -> None:
        self.api_key = api_key or os.environ.get("CFBD_API_KEY")
        if not self.api_key:
            raise CFBDProviderError("CFBD_API_KEY is required")
        self._fetcher = fetcher or _default_fetcher

    def _fetch_games(self, year: int) -> list[dict[str, Any]]:
        query = urlencode({"year": year})
        payload = self._fetcher(
            f"{self.base_url}/games?{query}",
            {"Accept": "application/json", "Authorization": f"Bearer {self.api_key}"},
        )
        if not isinstance(payload, list) or any(not isinstance(item, dict) for item in payload):
            raise CFBDProviderError("CFBD games response must be a JSON array of objects")
        return payload

    @staticmethod
    def _normalize(item: dict[str, Any]) -> NormalizedGame:
        external_id = item.get("id")
        away_team = item.get("awayTeam")
        home_team = item.get("homeTeam")
        if not isinstance(external_id, (int, str)) or not str(external_id):
            raise CFBDProviderError("CFBD game is missing id")
        if not isinstance(away_team, str) or not away_team or not isinstance(home_team, str) or not home_team:
            raise CFBDProviderError(f"CFBD game {external_id} is missing homeTeam or awayTeam")
        season = item.get("season")
        week = item.get("week")
        if not isinstance(season, int) or not isinstance(week, int):
            raise CFBDProviderError(f"CFBD game {external_id} has invalid season/week")
        status_value = str(item.get("status") or "").lower()
        if item.get("cancelled") or status_value == "cancelled":
            status = GameStatus.CANCELLED
        elif status_value == "postponed":
            status = GameStatus.POSTPONED
        elif item.get("completed"):
            status = GameStatus.FINAL
        elif status_value in {"in_progress", "live"}:
            status = GameStatus.LIVE
        else:
            status = GameStatus.SCHEDULED
        conference = item.get("homeConference") or item.get("awayConference") or "NCAA"
        if not isinstance(conference, str):
            conference = "NCAA"
        return NormalizedGame(
            external_id=f"cfbd:{external_id}", season=season, week=week,
            kickoff_at=_parse_kickoff(item.get("startDate")), away_team=away_team,
            home_team=home_team, conference=conference, status=status,
            away_score=_score(item.get("awayPoints")), home_score=_score(item.get("homePoints")),
            sport="ncaafb", league="NCAAFB",
        )

    def list_games(self, date_range: tuple[datetime, datetime]) -> list[NormalizedGame]:
        start, end = date_range
        if start.tzinfo is None or end.tzinfo is None:
            raise ValueError("CFBD date range must use timezone-aware datetimes")
        years = range(start.year, end.year + 1)
        games = [self._normalize(item) for year in years for item in self._fetch_games(year)]
        return sorted({game.external_id: game for game in games if start <= game.kickoff_at <= end}.values(), key=lambda game: game.kickoff_at)

    def get_game(self, external_game_id: str) -> NormalizedGame:
        if not external_game_id.startswith("cfbd:"):
            raise KeyError(external_game_id)
        game_id = external_game_id.removeprefix("cfbd:")
        for game in self.list_games((datetime(2000, 1, 1, tzinfo=UTC), datetime(2100, 1, 1, tzinfo=UTC))):
            if game.external_id == external_game_id or game.external_id == f"cfbd:{game_id}":
                return game
        raise KeyError(external_game_id)
