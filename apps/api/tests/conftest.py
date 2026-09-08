from __future__ import annotations

import sys
from pathlib import Path


SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Import all mapped models before tests create Base.metadata tables.
from dgn_picks_api.db import models as _models  # noqa: F401,E402
