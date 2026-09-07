from dgn_picks_api.seed.data import GATO_PICK_DEFINITIONS, SEEDED_USERS


def test_seed_users_are_exactly_the_approved_users() -> None:
    assert {user.username for user in SEEDED_USERS} == {"gato", "daran", "noch"}
    assert "noche" not in {user.username for user in SEEDED_USERS}


def test_all_thirteen_gato_definitions_are_distinct_and_malakai_is_unresolved() -> None:
    assert len(GATO_PICK_DEFINITIONS) == 13
    assert [definition.number for definition in GATO_PICK_DEFINITIONS] == list(range(1, 14))
    malakai = next(definition for definition in GATO_PICK_DEFINITIONS if "Malakai" in definition.description)
    assert malakai.side is None
