"""Compatibility entry point: schema changes belong to versioned migrations."""
from railway_migrate import main

if __name__ == "__main__":
    raise SystemExit(main())
