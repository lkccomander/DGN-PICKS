from datetime import UTC, datetime
from decimal import Decimal

from dgn_picks_api.domains.common.enums import GameStatus
from dgn_picks_api.domains.providers.contracts import NormalizedGame, NormalizedMarket, NormalizedSnapshot


def _snapshot(hour: int, line: str, odds: int = -110) -> NormalizedSnapshot:
    decimal = Decimal("1.90909") if odds == -110 else Decimal("2.5")
    return NormalizedSnapshot(datetime(2026, 9, 1, hour, tzinfo=UTC), Decimal(line) if line else None, odds, decimal, f"fixture-{hour}-{line}")


class FixtureProvider:
    def __init__(self) -> None:
        self._games = [
            NormalizedGame("fixture-stanford-duke", 2026, 3, datetime(2026, 9, 12, 19, tzinfo=UTC), "Stanford", "Duke", "ACC", GameStatus.SCHEDULED),
            NormalizedGame("fixture-indiana-houston", 2026, 3, datetime(2026, 9, 13, 16, tzinfo=UTC), "Houston", "Indiana", "Big Ten", GameStatus.SCHEDULED),
            NormalizedGame("fixture-lsu-auburn", 2026, 2, datetime(2026, 9, 5, 20, tzinfo=UTC), "Auburn", "LSU", "SEC", GameStatus.FINAL, 21, 28),
            NormalizedGame("fixture-ucla-washington", 2026, 2, datetime(2026, 9, 6, 22, tzinfo=UTC), "Washington", "UCLA", "Big Ten", GameStatus.FINAL, 31, 24),
        ]
        self._markets = {
            "fixture-stanford-duke": [
                NormalizedMarket("m-stanford-spread", "game_spread", "stanford", "+", "Stanford", None, (_snapshot(10, "+25.5"), _snapshot(14, "+24.5"))),
                NormalizedMarket("m-duke-total", "game_total", "over", "over", "Duke", None, (_snapshot(10, "51.5"), _snapshot(14, "52.5"))),
                NormalizedMarket("m-hoover-pass", "player_passing_yards", "over", "over", None, "Josh Hoover", (_snapshot(10, "246.5"),)),
            ],
            "fixture-indiana-houston": [NormalizedMarket("m-indiana-total", "game_total", "over", "over", "Indiana", None, (_snapshot(9, "55.5"), _snapshot(13, "56.5")))],
            "fixture-lsu-auburn": [NormalizedMarket("m-lsu-total", "game_total", "over", "over", "LSU", None, (_snapshot(8, "49.5"), _snapshot(12, "50.5")))],
            "fixture-ucla-washington": [
                NormalizedMarket("m-wash-total", "game_total", "over", "over", "Washington", None, (_snapshot(7, "49.5"), _snapshot(11, "50.5"))),
                NormalizedMarket("m-toney-rec", "player_receiving_yards", "unresolved", None, None, "Malakai Toney", (_snapshot(7, "72.5"),)),
            ],
        }

    def list_games(self, date_range: tuple[datetime, datetime]) -> list[NormalizedGame]:
        start, end = date_range
        return [game for game in self._games if start <= game.kickoff_at <= end]

    def get_game(self, external_game_id: str) -> NormalizedGame:
        for game in self._games:
            if game.external_id == external_game_id:
                return game
        raise KeyError(external_game_id)

    def list_markets(self, external_game_id: str) -> list[NormalizedMarket]:
        return [market for market in self._markets.get(external_game_id, []) if not market.market_type.startswith("player_")]

    def list_props(self, external_game_id: str) -> list[NormalizedMarket]:
        return [market for market in self._markets.get(external_game_id, []) if market.market_type.startswith("player_")]
