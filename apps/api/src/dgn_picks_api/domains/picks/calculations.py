from decimal import Decimal

from dgn_picks_api.domains.common.enums import PickResult


def profit_units(
    stake_units: Decimal,
    decimal_odds: Decimal | None,
    result: PickResult,
) -> Decimal | None:
    if result in {PickResult.PENDING} or decimal_odds is None:
        return None
    if result in {PickResult.PUSH, PickResult.VOID}:
        return Decimal("0")
    if result is PickResult.WIN:
        return stake_units * (decimal_odds - Decimal(1))
    if result is PickResult.LOSS:
        return -stake_units
    raise ValueError(f"Unsupported pick result: {result}")


def roi(total_profit_units: Decimal, total_units_risked: Decimal) -> Decimal | None:
    if total_units_risked == 0:
        return None
    return total_profit_units / total_units_risked
