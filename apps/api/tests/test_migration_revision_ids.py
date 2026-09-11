from __future__ import annotations

import ast
from pathlib import Path


VERSIONS_DIRECTORY = Path(__file__).resolve().parents[1] / "migrations" / "versions"
MAX_ALEMBIC_REVISION_LENGTH = 32


def migration_revision(path: Path) -> str:
    module = ast.parse(path.read_text(encoding="utf-8"))
    for statement in module.body:
        if (
            isinstance(statement, ast.Assign)
            and len(statement.targets) == 1
            and isinstance(statement.targets[0], ast.Name)
            and statement.targets[0].id == "revision"
            and isinstance(statement.value, ast.Constant)
            and isinstance(statement.value.value, str)
        ):
            return statement.value.value
    raise AssertionError(f"{path} does not define a string revision")


def test_migration_revision_ids_fit_the_alembic_version_column() -> None:
    revisions = [migration_revision(path) for path in VERSIONS_DIRECTORY.glob("*.py")]
    assert len(revisions) == len(set(revisions))
    assert all(len(revision) <= MAX_ALEMBIC_REVISION_LENGTH for revision in revisions)
