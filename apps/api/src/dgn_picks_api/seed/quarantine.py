"""Reversible quarantine of pristine legacy product-to-fixture seed matches.

No provenance existed in the old schema. Require an explicit operator action;
report modified candidates for review instead of assuming they are seed data.
"""
from datetime import UTC, datetime
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.orm import Session
from dgn_picks_api.domains.games.models import Game
from dgn_picks_api.domains.markets.models import Market, Selection
from dgn_picks_api.domains.picks.models import Pick
from dgn_picks_api.domains.users.models import User

LEGACY = {
    "Stanford +24.5": ("fixture-stanford-duke", "game_spread", "stanford", "+", "24.5"),
    "Josh Hoover over 246.5 passing yards": ("fixture-stanford-duke", "player_passing_yards", "over", "over", "246.5"),
    "Over 51.5 Duke": ("fixture-stanford-duke", "game_total", "over", "over", "51.5"),
    "Over 56.5 Indiana": ("fixture-indiana-houston", "game_total", "over", "over", "56.5"),
    "Over 50.5 LSU": ("fixture-lsu-auburn", "game_total", "over", "over", "50.5"),
    "Over 50.5 Washington": ("fixture-ucla-washington", "game_total", "over", "over", "50.5"),
}


def quarantine_legacy_seed(db: Session, *, apply: bool = False) -> dict[str, list[int]]:
    report: dict[str, list[int]] = {"eligible": [], "review_required": [], "archived": []}
    candidates = db.scalars(select(Pick).join(User).where(User.username == "gato", Pick.notes.in_(LEGACY), Pick.archived_at.is_(None))).all()
    for pick in candidates:
        game, market, selection = db.get(Game, pick.game_id), db.get(Market, pick.market_id), db.get(Selection, pick.selection_id) if pick.selection_id else None
        event, market_type, key, side, line = LEGACY[pick.notes]
        matches = (game and market and selection and game.external_ids.get("fixture") == event
                   and market.game_id == game.id and market.market_type == market_type
                   and selection.market_id == market.id and selection.selection_key == key and selection.side == side
                   and pick.line_value == Decimal(line) and pick.american_odds == -110
                   and pick.decimal_odds == Decimal("1.90909") and pick.stake_units == Decimal(1)
                   and pick.result == "pending" and pick.profit_units is None and not pick.legs)
        if not matches:
            report["review_required"].append(pick.id)
            continue
        report["eligible"].append(pick.id)
        if apply:
            pick.archived_at = datetime.now(UTC)
            pick.archive_reason = "legacy_fixture_seed_terms_v1"
            report["archived"].append(pick.id)
    if apply:
        db.commit()
    return report
