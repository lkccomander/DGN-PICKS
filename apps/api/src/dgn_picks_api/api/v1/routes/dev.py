from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from dgn_picks_api.api.v1.dependencies import get_db
from dgn_picks_api.api.v1.schemas import SeedReportResponse

router = APIRouter(prefix="/dev", tags=["development"])


@router.post("/seed", response_model=SeedReportResponse)
def seed(db: Session = Depends(get_db)) -> SeedReportResponse:
    # Import lazily so ordinary API startup does not require the development seed path.
    from dgn_picks_api.seed.service import seed_local_data

    return SeedReportResponse.model_validate(seed_local_data(db))
