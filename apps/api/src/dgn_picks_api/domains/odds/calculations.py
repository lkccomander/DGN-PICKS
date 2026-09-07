from decimal import Decimal


def american_to_decimal(american_odds: int) -> Decimal:
    if american_odds == 0:
        raise ValueError("American odds cannot be zero")
    if american_odds > 0:
        return (Decimal(american_odds) / Decimal(100)) + Decimal(1)
    return (Decimal(100) / Decimal(abs(american_odds))) + Decimal(1)


def decimal_to_implied_probability(decimal_odds: Decimal) -> Decimal:
    if decimal_odds <= 1:
        raise ValueError("Decimal odds must be greater than 1")
    return Decimal(1) / decimal_odds
