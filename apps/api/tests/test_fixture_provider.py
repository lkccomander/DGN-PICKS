from datetime import UTC, datetime

from dgn_picks_api.domains.common.enums import GameStatus
from dgn_picks_api.domains.providers.fixture import FixtureProvider


def test_fixture_provider_has_deterministic_game_coverage() -> None:
    provider = FixtureProvider()
    games = provider.list_games((datetime(2026, 1, 1, tzinfo=UTC), datetime(2026, 12, 31, tzinfo=UTC)))
    assert len(games) == 4
    assert {game.status for game in games} == {GameStatus.SCHEDULED, GameStatus.FINAL}


def test_fixture_provider_exposes_movement_and_props() -> None:
    provider = FixtureProvider()
    markets = provider.list_markets("fixture-stanford-duke")
    props = provider.list_props("fixture-ucla-washington")
    assert len(markets[0].snapshots) == 2
    assert {market.market_type for market in props} == {"player_receiving_yards"}
    assert props[0].side is None


def test_complete_fixture_market_coverage():
    provider = FixtureProvider()
    games = provider.list_games((datetime(2026, 1, 1, tzinfo=UTC), datetime(2027, 1, 1, tzinfo=UTC)))
    markets = [market for game in games for market in provider.list_markets(game.external_id) + provider.list_props(game.external_id)]
    assert len({market.market_type for market in markets if market.market_type.startswith("player_")}) >= 3
    for kind in ("game_moneyline", "game_spread", "game_total"):
        movement = next(m for m in markets if m.market_type == kind and len(m.snapshots) > 1)
        assert movement.snapshots[0] != movement.snapshots[-1]
    assert games == FixtureProvider().list_games((datetime(2026, 1, 1, tzinfo=UTC), datetime(2027, 1, 1, tzinfo=UTC)))
