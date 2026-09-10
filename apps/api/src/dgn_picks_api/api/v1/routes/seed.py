from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from dgn_picks_api.api.v1.dependencies import get_db
from dgn_picks_api.api.v1.schemas import SeedPickDefinitionResponse
from dgn_picks_api.domains.picks.models import Pick
from dgn_picks_api.domains.users.models import User
from dgn_picks_api.seed.data import GATO_PICK_DEFINITIONS, PickDefinition

router = APIRouter(prefix="/seed", tags=["seed"])


def definition_state(definition: PickDefinition, materialized_descriptions: set[str]) -> str:
    if definition.description in materialized_descriptions:
        return "tracked"
    if definition.side is None:
        return "unresolved"
    return "unmatched"


def gato_pick_definitions(materialized_descriptions: set[str]) -> list[SeedPickDefinitionResponse]:
    return [
        SeedPickDefinitionResponse(
            number=definition.number,
            description=definition.description,
            market_type=definition.market_type,
            line_value=definition.line_value,
            side=definition.side,
            team_or_player=definition.team_or_player,
            state=definition_state(definition, materialized_descriptions),
        )
        for definition in GATO_PICK_DEFINITIONS
    ]


@router.get("/pick-definitions", response_model=list[SeedPickDefinitionResponse])
def list_pick_definitions(
    user: str = Query(default="gato"),
    db: Session = Depends(get_db),
) -> list[SeedPickDefinitionResponse]:
    """Expose the supplied seed input without turning unmatched entries into picks."""
    if user != "gato":
        return []
    gato = db.scalars(select(User).where(User.username == "gato")).one_or_none()
    if gato is None:
        return gato_pick_definitions(set())
    materialized = set(
        db.scalars(
            select(Pick.notes).where(Pick.user_id == gato.id, Pick.notes.is_not(None))
        ).all()
    )
    return gato_pick_definitions(materialized)
