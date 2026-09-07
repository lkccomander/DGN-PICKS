from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from dgn_picks_api.db.base import Base
from dgn_picks_api.domains.common.enums import PickResult

if TYPE_CHECKING:
    from dgn_picks_api.domains.users.models import User


class Pick(Base):
    __tablename__ = "picks"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"))
    market_id: Mapped[int] = mapped_column(ForeignKey("markets.id"))
    selection_id: Mapped[int | None] = mapped_column(ForeignKey("selections.id"))
    picked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    line_value: Mapped[Decimal | None] = mapped_column(Numeric(10, 3))
    american_odds: Mapped[int | None] = mapped_column()
    decimal_odds: Mapped[Decimal | None] = mapped_column(Numeric(10, 5))
    stake_units: Mapped[Decimal] = mapped_column(Numeric(10, 3), default=Decimal("1.0"))
    result: Mapped[PickResult] = mapped_column(String(16), default=PickResult.PENDING, index=True)
    profit_units: Mapped[Decimal | None] = mapped_column(Numeric(10, 5))
    notes: Mapped[str | None] = mapped_column(String(1000))
    user: Mapped["User"] = relationship(back_populates="picks")
    legs: Mapped[list["PickLeg"]] = relationship(back_populates="pick", cascade="all, delete-orphan")


class PickLeg(Base):
    __tablename__ = "pick_legs"

    id: Mapped[int] = mapped_column(primary_key=True)
    pick_id: Mapped[int] = mapped_column(ForeignKey("picks.id"), index=True)
    market_id: Mapped[int] = mapped_column(ForeignKey("markets.id"))
    selection_id: Mapped[int | None] = mapped_column(ForeignKey("selections.id"))
    odds_snapshot_id: Mapped[int | None] = mapped_column(ForeignKey("odds_snapshots.id"))
    pick: Mapped["Pick"] = relationship(back_populates="legs")
