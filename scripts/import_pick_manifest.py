"""Plan an operator's manual pick import; --apply commits it."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps/api/src"))

from dgn_picks_api.db import models  # noqa: E402,F401 - register model relationships
from dgn_picks_api.db.session import SessionLocal  # noqa: E402
from dgn_picks_api.domains.picks.imports import PickImportManifest, import_pick_manifest  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--apply", action="store_true", help="Commit all new picks in one transaction")
    args = parser.parse_args()
    path = args.manifest
    if not path.is_absolute() and not path.exists():
        path = ROOT / path
    manifest = PickImportManifest.model_validate_json(path.read_text(encoding="utf-8"))
    with SessionLocal() as session:
        result = import_pick_manifest(session, manifest, apply=args.apply)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
