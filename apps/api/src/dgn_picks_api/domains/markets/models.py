from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from dgn_picks_api.db.base import Base
from dgn_picks_api.domains.common.enums import MarketStatus

if TYPE_CHECKING:
    from dgn_picks_api.domains.games.models import Game
    from dgn_picks_api.domains.odds.models import OddsSnapshot


class Market(Base):
    __tablename__ = "markets"

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"), index=True)
    market_type: Mapped[str] = mapped_column(String(48), index=True)
    period: Mapped[str] = mapped_column(String(24), default="game")
    player_id: Mapped[int | None] = mapped_column(ForeignKey("players.id"))
    team_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"))
    status: Mapped[MarketStatus] = mapped_column(String(16), default=MarketStatus.OPEN)
    game: Mapped["Game"] = relationship(back_populates="markets")
    selections: Mapped[list["Selection"]] = relationship(back_populates="market")


class Selection(Base):
    __tablename__ = "selections"
    __table_args__ = (UniqueConstraint("market_id", "selection_key"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    market_id: Mapped[int] = mapped_column(ForeignKey("markets.id"), index=True)
    selection_key: Mapped[str] = mapped_column(String(80))
    team_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"))
    player_id: Mapped[int | None] = mapped_column(ForeignKey("players.id"))
    side: Mapped[str | None] = mapped_column(String(16))
    market: Mapped["Market"] = relationship(back_populates="selections")
    snapshots: Mapped[list["OddsSnapshot"]] = relationship(back_populates="selection")
