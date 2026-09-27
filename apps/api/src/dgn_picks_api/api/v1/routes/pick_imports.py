"""Strictly authenticated operator workflows for manual imports and legacy review."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from dgn_picks_api.api.v1.dependencies import get_db, require_editor_identity
from dgn_picks_api.domains.picks.imports import PickImportManifest, import_pick_manifest
from dgn_picks_api.seed.quarantine import quarantine_legacy_seed

router = APIRouter(prefix="/admin/pick-imports", tags=["pick imports"],
                   dependencies=[Depends(require_editor_identity)])


@router.post("")
def post_pick_import(manifest: PickImportManifest, apply: bool = Query(default=False), db: Session = Depends(get_db)) -> dict:
    """Plan by default. Explicit apply commits the complete manifest atomically."""
    try:
        return import_pick_manifest(db, manifest, apply=apply)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except IntegrityError as exc:
        raise HTTPException(status_code=409, detail="Import conflicts with existing records") from exc


@router.post("/legacy-seed-quarantine")
def post_legacy_seed_quarantine(apply: bool = Query(default=False), db: Session = Depends(get_db)) -> dict[str, list[int]]:
    """Review the fixed legacy fixture manifest; explicit apply archives strict matches."""
    return quarantine_legacy_seed(db, apply=apply)
