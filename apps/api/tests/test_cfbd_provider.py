from datetime import UTC, datetime

import pytest

from dgn_picks_api.domains.common.enums import GameStatus
from dgn_picks_api.domains.providers.cfbd import CFBDProvider, CFBDProviderError


PAYLOAD = [
    {"id": 123, "season": 2026, "week": 4, "startDate": "2026-09-26T19:30:00Z",
     "awayTeam": "Texas", "homeTeam": "Oklahoma", "awayConference": "SEC",
     "homeConference": "SEC", "completed": False, "status": "scheduled"},
    {"id": 124, "season": 2026, "week": 4, "startDate": "2026-09-27T00:00:00-05:00",
     "awayTeam": "Auburn", "homeTeam": "LSU", "awayConference": "SEC",
     "homeConference": "SEC", "completed": True, "awayPoints": 14, "homePoints": 28},
]


def fetcher(url, headers):
    assert "year=2026" in url
    assert headers["Authorization"] == "Bearer test-key"
    return PAYLOAD


def test_normalizes_cfbd_games_to_utc_and_statuses():
    games = CFBDProvider(api_key="test-key", fetcher=fetcher).list_games(
        (datetime(2026, 9, 26, tzinfo=UTC), datetime(2026, 9, 27, 23, 59, tzinfo=UTC))
    )
    assert [game.external_id for game in games] == ["cfbd:123", "cfbd:124"]
    assert games[0].kickoff_at.tzinfo is UTC
    assert games[0].status == GameStatus.SCHEDULED
    assert games[1].status == GameStatus.FINAL
    assert games[1].home_score == 28


def test_requires_timezone_aware_range_and_key():
    with pytest.raises(CFBDProviderError, match="CFBD_API_KEY"):
        CFBDProvider(api_key="")
    provider = CFBDProvider(api_key="test-key", fetcher=fetcher)
    with pytest.raises(ValueError, match="timezone-aware"):
        provider.list_games((datetime(2026, 1, 1), datetime(2026, 1, 2)))


def test_rejects_malformed_payload():
    provider = CFBDProvider(api_key="test-key", fetcher=lambda *_: {"games": []})
    with pytest.raises(CFBDProviderError, match="JSON array"):
        provider.list_games((datetime(2026, 1, 1, tzinfo=UTC), datetime(2026, 1, 2, tzinfo=UTC)))


def test_deduplicates_provider_events():
    provider = CFBDProvider(api_key="test-key", fetcher=lambda *_: PAYLOAD + [PAYLOAD[0]])
    games = provider.list_games((datetime(2026, 9, 26, tzinfo=UTC), datetime(2026, 9, 27, 23, 59, tzinfo=UTC)))
    assert [game.external_id for game in games].count("cfbd:123") == 1
