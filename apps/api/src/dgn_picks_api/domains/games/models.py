from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from dgn_picks_api.db.base import Base
from dgn_picks_api.domains.common.enums import GameStatus

if TYPE_CHECKING:
    from dgn_picks_api.domains.markets.models import Market


class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(primary_key=True)
    external_ids: Mapped[dict] = mapped_column(JSON, default=dict)
    season: Mapped[int] = mapped_column(Integer, index=True)
    week: Mapped[int] = mapped_column(Integer)
    kickoff_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    home_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    away_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    venue: Mapped[str | None] = mapped_column(String(160))
    status: Mapped[GameStatus] = mapped_column(String(16), default=GameStatus.SCHEDULED, index=True)
    home_score: Mapped[int | None] = mapped_column()
    away_score: Mapped[int | None] = mapped_column()
    markets: Mapped[list["Market"]] = relationship(back_populates="game")
