from dataclasses import dataclass


@dataclass(frozen=True)
class SeedUser:
    username: str
    display_name: str


@dataclass(frozen=True)
class PickDefinition:
    number: int
    description: str
    market_type: str
    line_value: str
    side: str | None
    team_or_player: str


SEEDED_USERS = (SeedUser("gato", "Gato"), SeedUser("daran", "Daran"), SeedUser("noch", "Noch"))

GATO_PICK_DEFINITIONS = (
    PickDefinition(1, "Stanford +24.5", "game_spread", "+24.5", "+", "Stanford"),
    PickDefinition(2, "Malakai Toney 72.5 rec yards", "player_receiving_yards", "72.5", None, "Malakai Toney"),
    PickDefinition(3, "Josh Hoover over 246.5 passing yards", "player_passing_yards", "246.5", "over", "Josh Hoover"),
    PickDefinition(4, "Over 56.5 Indiana", "game_total", "56.5", "over", "Indiana"),
    PickDefinition(5, "Over 51.5 Duke", "game_total", "51.5", "over", "Duke"),
    PickDefinition(6, "Over 58.5 Auburn", "game_total", "58.5", "over", "Auburn"),
    PickDefinition(7, "Over 50.5 LSU", "game_total", "50.5", "over", "LSU"),
    PickDefinition(8, "Over 54.5 UCLA", "game_total", "54.5", "over", "UCLA"),
    PickDefinition(9, "Over 50.5 Washington", "game_total", "50.5", "over", "Washington"),
    PickDefinition(10, "Notre Dame -20.5", "game_spread", "-20.5", "-", "Notre Dame"),
    PickDefinition(11, "Ole Miss -6.5", "game_spread", "-6.5", "-", "Ole Miss"),
    PickDefinition(12, "Over 52.5 Houston", "game_total", "52.5", "over", "Houston"),
    PickDefinition(13, "Over 53.5 SMU", "game_total", "53.5", "over", "SMU"),
)
