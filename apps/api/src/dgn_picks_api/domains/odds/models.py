from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from dgn_picks_api.db.base import Base

if TYPE_CHECKING:
    from dgn_picks_api.domains.markets.models import Selection


class SportsbookSource(Base):
    __tablename__ = "sportsbook_sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    source_type: Mapped[str] = mapped_column(String(32))
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class OddsSnapshot(Base):
    __tablename__ = "odds_snapshots"
    __table_args__ = (UniqueConstraint("selection_id", "sportsbook_id", "observed_at", "source_event_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    selection_id: Mapped[int] = mapped_column(ForeignKey("selections.id"), index=True)
    sportsbook_id: Mapped[int] = mapped_column(ForeignKey("sportsbook_sources.id"))
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    line_value: Mapped[Decimal | None] = mapped_column(Numeric(10, 3))
    american_odds: Mapped[int | None] = mapped_column(Integer)
    decimal_odds: Mapped[Decimal] = mapped_column(Numeric(10, 5))
    implied_probability: Mapped[Decimal | None] = mapped_column(Numeric(10, 8))
    source_event_id: Mapped[str | None] = mapped_column(String(160))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    selection: Mapped["Selection"] = relationship(back_populates="snapshots")
