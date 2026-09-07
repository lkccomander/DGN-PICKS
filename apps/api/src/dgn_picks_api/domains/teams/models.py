from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from dgn_picks_api.db.base import Base

if TYPE_CHECKING:
    from dgn_picks_api.domains.games.models import Game


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True)
    external_ids: Mapped[dict] = mapped_column(JSON, default=dict)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    short_name: Mapped[str] = mapped_column(String(80))
    abbreviation: Mapped[str] = mapped_column(String(8), unique=True)
    conference: Mapped[str] = mapped_column(String(64), index=True)
    logo_url: Mapped[str | None] = mapped_column(String(500))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    players: Mapped[list["Player"]] = relationship(back_populates="team")


class Player(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(primary_key=True)
    external_ids: Mapped[dict] = mapped_column(JSON, default=dict)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    name: Mapped[str] = mapped_column(String(120), index=True)
    position: Mapped[str] = mapped_column(String(16))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    team: Mapped["Team"] = relationship(back_populates="players")
