from dgn_picks_api.api.v1.routes.seed import gato_pick_definitions, list_pick_definitions


def test_gato_seed_definitions_expose_all_inputs_without_guessing() -> None:
    definitions = gato_pick_definitions({"Stanford +24.5"})

    assert len(definitions) == 13
    assert definitions[0].state == "tracked"
    malakai = next(item for item in definitions if "Malakai Toney" in item.description)
    assert malakai.side is None
    assert malakai.state == "unresolved"
    assert all(item.state in {"tracked", "unresolved", "unmatched"} for item in definitions)


def test_seed_definition_route_only_returns_gato_input_and_marks_materialized_entries() -> None:
    class Result:
        def __init__(self, value):
            self.value = value

        def one_or_none(self):
            return self.value

        def all(self):
            return self.value

    class Session:
        def __init__(self):
            self.results = [Result(type("User", (), {"id": 1})()), Result(["Stanford +24.5"])]

        def scalars(self, statement):
            return self.results.pop(0)

    definitions = list_pick_definitions(user="gato", db=Session())

    assert len(definitions) == 13
    assert definitions[0].state == "tracked"
    assert list_pick_definitions(user="daran", db=Session()) == []
