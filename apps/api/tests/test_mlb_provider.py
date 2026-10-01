from datetime import UTC, date

from dgn_picks_api.domains.common.enums import GameStatus
from dgn_picks_api.domains.providers.mlb import MLBProvider


def test_mlb_schedule_normalizes_matchups():
    payload = {"dates": [{"games": [{
        "gamePk": 20261001, "gameDate": "2026-10-01T18:00:00Z",
        "status": {"codedGameState": "S", "abstractGameState": "Preview"},
        "teams": {"away": {"team": {"name": "Atlanta Braves"}}, "home": {"team": {"name": "Philadelphia Phillies"}}},
    }]}]}
    requested = []
    games = MLBProvider(lambda url, headers: requested.append(url) or payload).list_games(date(2026, 10, 1))
    assert games[0].external_id == "mlb:20261001"
    assert games[0].away_team == "Atlanta Braves"
    assert games[0].home_team == "Philadelphia Phillies"
    assert games[0].status == GameStatus.SCHEDULED
    assert games[0].kickoff_at.tzinfo is UTC
    assert "date=2026-10-01" in requested[0]
