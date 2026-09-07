from dataclasses import dataclass, field


@dataclass
class SeedReport:
    users_inserted: int = 0
    users_existing: int = 0
    games_inserted: int = 0
    markets_inserted: int = 0
    snapshots_inserted: int = 0
    picks_inserted: int = 0
    duplicate_snapshots: int = 0
    unresolved_definitions: list[str] = field(default_factory=list)

    @property
    def unresolved_count(self) -> int:
        return len(self.unresolved_definitions)
