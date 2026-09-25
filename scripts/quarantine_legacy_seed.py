"""Report legacy fixture-derived seed picks; use --apply to archive strict matches."""
import argparse
import json
from dgn_picks_api.db.session import SessionLocal
from dgn_picks_api.seed.quarantine import quarantine_legacy_seed

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Archive eligible records; taken terms and history remain unchanged")
    args = parser.parse_args()
    with SessionLocal() as db:
        print(json.dumps(quarantine_legacy_seed(db, apply=args.apply), indent=2))
