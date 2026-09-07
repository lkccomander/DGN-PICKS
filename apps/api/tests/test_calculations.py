from decimal import Decimal

import pytest

from dgn_picks_api.domains.common.enums import PickResult
from dgn_picks_api.domains.odds.calculations import american_to_decimal, decimal_to_implied_probability
from dgn_picks_api.domains.picks.calculations import profit_units, roi


def test_american_odds_use_decimal_arithmetic() -> None:
    assert american_to_decimal(150) == Decimal("2.5")
    assert american_to_decimal(-200) == Decimal("1.5")


def test_implied_probability_requires_valid_decimal_odds() -> None:
    assert decimal_to_implied_probability(Decimal("2")) == Decimal("0.5")
    with pytest.raises(ValueError):
        decimal_to_implied_probability(Decimal("1"))


@pytest.mark.parametrize(
    ("result", "expected"),
    [(PickResult.WIN, Decimal("1.5")), (PickResult.LOSS, Decimal("-1")), (PickResult.PUSH, Decimal("0")), (PickResult.VOID, Decimal("0"))],
)
def test_profit_units(result: PickResult, expected: Decimal) -> None:
    assert profit_units(Decimal("1"), Decimal("2.5"), result) == expected


def test_profit_and_roi_skip_incomplete_values() -> None:
    assert profit_units(Decimal("1"), None, PickResult.WIN) is None
    assert profit_units(Decimal("1"), Decimal("2"), PickResult.PENDING) is None
    assert roi(Decimal("2"), Decimal("0")) is None
    assert roi(Decimal("2"), Decimal("4")) == Decimal("0.5")
