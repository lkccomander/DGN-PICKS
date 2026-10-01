"""Public MLB schedule adapter used for the live schedule preview."""

from __future__ import annotations

import json
from datetime import UTC, date, datetime
from typing import Any, Callable
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from dgn_picks_api.domains.common.enums import GameStatus
from dgn_picks_api.domains.providers.contracts import NormalizedGame


class MLBProviderError(RuntimeError):
    pass


def _fetch(url: str, headers: dict[str, str]) -> Any:
    try:
        with urlopen(Request(url, headers=headers), timeout=15) as response:  # noqa: S310 - fixed MLB HTTPS URL
            return json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        raise MLBProviderError(f"MLB schedule request failed: {exc}") from exc


class MLBProvider:
    base_url = "https://statsapi.mlb.com/api/v1/schedule"

    def __init__(self, fetcher: Callable[[str, dict[str, str]], Any] | None = None) -> None:
        self._fetcher = fetcher or _fetch

    def fetch_schedule_payload(self, game_date: date) -> dict[str, Any]:
        query = urlencode({"sportId": 1, "date": game_date.isoformat(), "hydrate": "venue"})
        payload = self._fetcher(f"{self.base_url}?{query}", {"Accept": "application/json"})
        if not isinstance(payload, dict) or not isinstance(payload.get("dates"), list):
            raise MLBProviderError("MLB schedule response is missing dates")
        return payload

    @staticmethod
    def _status(game: dict[str, Any]) -> GameStatus:
        code = str((game.get("status") or {}).get("codedGameState", "")).upper()
        abstract = str((game.get("status") or {}).get("abstractGameState", "")).lower()
        if code in {"F", "O"} or abstract == "final":
            return GameStatus.FINAL
        if code in {"I", "M", "N"} or abstract == "live":
            return GameStatus.LIVE
        if code in {"D", "C"} or abstract in {"postponed", "cancelled"}:
            return GameStatus.POSTPONED if code == "D" or abstract == "postponed" else GameStatus.CANCELLED
        return GameStatus.SCHEDULED

    @staticmethod
    def _team(game: dict[str, Any], side: str) -> str:
        value = ((game.get("teams") or {}).get(side) or {}).get("team") or {}
        name = value.get("name")
        if not isinstance(name, str) or not name:
            raise MLBProviderError("MLB game is missing a team name")
        return name

    def list_games(self, game_date: date) -> list[NormalizedGame]:
        return self.normalize_payload(self.fetch_schedule_payload(game_date), game_date)

    def normalize_payload(self, payload: dict[str, Any], game_date: date) -> list[NormalizedGame]:
        dates = payload["dates"]
        games: list[NormalizedGame] = []
        for day in dates:
            for item in day.get("games", []) if isinstance(day, dict) else []:
                if not isinstance(item, dict) or not item.get("gamePk"):
                    raise MLBProviderError("MLB schedule contains an invalid game")
                starts = item.get("gameDate")
                if not isinstance(starts, str):
                    raise MLBProviderError(f"MLB game {item['gamePk']} is missing gameDate")
                kickoff = datetime.fromisoformat(starts.replace("Z", "+00:00")).astimezone(UTC)
                games.append(NormalizedGame(
                    external_id=f"mlb:{item['gamePk']}", season=game_date.year, week=1,
                    kickoff_at=kickoff, away_team=self._team(item, "away"),
                    home_team=self._team(item, "home"), conference="MLB",
                    status=self._status(item), away_score=((item.get("teams") or {}).get("away") or {}).get("score"),
                    home_score=((item.get("teams") or {}).get("home") or {}).get("score"),
                    sport="baseball", league="MLB",
                ))
        return sorted(games, key=lambda game: game.kickoff_at)
