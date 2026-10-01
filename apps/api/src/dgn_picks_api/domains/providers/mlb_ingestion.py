"""Daily MLB snapshot storage and database import.

The public schedule API reads the local database. Only the admin sync operation
is allowed to contact MLB Stats API, at most once per date unless forced.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from dgn_picks_api.domains.games.models import Game
from dgn_picks_api.domains.providers.mlb import MLBProvider
from dgn_picks_api.domains.teams.models import Team


def snapshot_path(game_date: date) -> Path:
    root = Path(os.getenv("DGN_INGESTION_DIR", "data/ingestion"))
    return root / "mlb" / f"{game_date.isoformat()}.json"


def _write_snapshot(path: Path, payload: dict[str, Any], game_date: date) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    digest = hashlib.sha256(encoded).hexdigest()
    envelope = {
        "source": "statsapi.mlb.com",
        "league": "MLB",
        "date": game_date.isoformat(),
        "fetched_at": datetime.now(UTC).isoformat(),
        "sha256": digest,
        "payload": payload,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(envelope, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return digest


def _read_snapshot(path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    envelope = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(envelope, dict) or not isinstance(envelope.get("payload"), dict):
        raise ValueError("invalid MLB snapshot envelope")
    return envelope, envelope["payload"]


def _abbreviation(name: str, db: Session) -> str:
    base = re.sub(r"[^A-Z0-9]", "", name.upper())[:8] or "MLBTEAM"
    value = base
    suffix = 1
    while db.scalar(select(Team.id).where(Team.abbreviation == value)) is not None:
        tail = str(suffix)
        value = (base[: 8 - len(tail)] + tail)[:8]
        suffix += 1
    return value


def _team(db: Session, name: str) -> Team:
    team = db.scalar(select(Team).where(Team.name == name))
    if team is None:
        team = Team(
            external_ids={"mlb_name": name}, name=name, short_name=name,
            abbreviation=_abbreviation(name, db), conference="MLB", active=True,
        )
        db.add(team)
        db.flush()
    return team


def import_games(db: Session, games: list[Any]) -> int:
    count = 0
    for normalized in games:
        game = db.scalar(select(Game).where(Game.external_ids["mlb"].as_string() == normalized.external_id))
        if game is None:
            game = Game(external_ids={"mlb": normalized.external_id})
            db.add(game)
        home = _team(db, normalized.home_team)
        away = _team(db, normalized.away_team)
        game.season = normalized.season
        game.sport = normalized.sport
        game.league = normalized.league
        game.week = normalized.week
        game.kickoff_at = normalized.kickoff_at
        game.home_team_id = home.id
        game.away_team_id = away.id
        game.status = normalized.status
        game.home_score = normalized.home_score
        game.away_score = normalized.away_score
        count += 1
    return count


def sync_mlb(db: Session, game_date: date, *, force: bool = False) -> dict[str, Any]:
    path = snapshot_path(game_date)
    used_external = force or not path.exists()
    if used_external:
        payload = MLBProvider().fetch_schedule_payload(game_date)
        digest = _write_snapshot(path, payload, game_date)
        envelope, payload = _read_snapshot(path)
    else:
        envelope, payload = _read_snapshot(path)
        digest = str(envelope.get("sha256", ""))
    provider = MLBProvider()
    games = provider.normalize_payload(payload, game_date)
    imported = import_games(db, games)
    db.commit()
    return {"date": game_date.isoformat(), "games": imported, "used_external": used_external,
            "path": str(path), "sha256": digest, "fetched_at": envelope.get("fetched_at")}


def list_local_games(db: Session, game_date: date) -> list[dict[str, Any]]:
    start = datetime.combine(game_date, time.min, tzinfo=UTC)
    end = start + timedelta(days=1)
    rows = db.scalars(select(Game).where(Game.league == "MLB", Game.kickoff_at >= start, Game.kickoff_at < end).order_by(Game.kickoff_at)).all()
    teams = {team.id: team.name for team in db.scalars(select(Team)).all()}
    return [{"external_id": game.external_ids.get("mlb", ""), "sport": game.sport, "league": game.league,
             "kickoff_at": game.kickoff_at.isoformat(), "away_team": teams.get(game.away_team_id, ""),
             "home_team": teams.get(game.home_team_id, ""), "status": str(game.status),
             "away_score": game.away_score, "home_score": game.home_score} for game in rows]
