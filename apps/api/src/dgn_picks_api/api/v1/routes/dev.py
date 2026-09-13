from dataclasses import asdict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from dgn_picks_api.api.v1.dependencies import get_db, require_authenticated_write_access
from dgn_picks_api.api.v1.schemas import SeedReportResponse

router = APIRouter(prefix="/dev", tags=["development"])


@router.post(
    "/seed",
    response_model=SeedReportResponse,
    dependencies=[Depends(require_authenticated_write_access)],
)
def seed(db: Session = Depends(get_db)) -> SeedReportResponse:
    # Import lazily so ordinary API startup does not require the development seed path.
    from dgn_picks_api.seed.service import seed_local_data

    report = seed_local_data(db)
    return SeedReportResponse.model_validate({**asdict(report), "unresolved_count": report.unresolved_count})
