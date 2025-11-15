from datetime import date, timedelta
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Path, HTTPException

from ktbtracker_server.entities.entities import Candidate
from ktbtracker_server.models import response, models
from ktbtracker_server.services.candidates import CandidatesService, get_candidates_service
from ktbtracker_server.services.tracking import TrackingService, get_tracking_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.get("/", response_model=response.PagedResponse[models.Candidate])
async def get_candidates(
        page: Annotated[int, Query(ge=0)] = 0,
        page_size: Annotated[int, Query(le=100, alias="size")] = 100,
        cycle_id: Annotated[int | None, Query(ge=0, alias="cycle")] = None,
        # -- Dependencies --
        candidates_service: CandidatesService = Depends(get_candidates_service),
) -> response.PagedResponse[models.Candidate]:
    return response.PagedResponse[models.Candidate](
        content=candidates_service.find_all(offset=page * page_size, limit=page_size)
        if cycle_id is None else candidates_service.find_all_by_cycle_id(cycle_id, offset=page * page_size, limit=page_size),
        pagination=response.Pagination(
            page=page,
            page_size=page_size,
            total_elements=candidates_service.count_all() if cycle_id is None else candidates_service.count_all_by_cycle_id(cycle_id)
        )
    )


@router.get("/{candidate_id}", response_model=models.Candidate)
async def get_candidate(
        candidate_id: Annotated[int, Path(
            gt=0,
            description="Candidate ID which uniquely identifies a user as a candidate for a testing cycle.")],
        # -- Dependencies --
        candidates_service: CandidatesService = Depends(get_candidates_service),
) -> Candidate:
    if candidate := candidates_service.find_by_id(candidate_id):
        return candidate
    raise HTTPException(status_code=404, detail="Not found")


@router.get("/{candidate_id}/full-statistics", response_model=models.FullStatistics)
async def get_full_statistics(
        candidate_id: Annotated[int, Path(
            gt=0,
            description="Candidate ID which uniquely identifies a user as a candidate for a testing cycle.")],
        candidates_service: CandidatesService = Depends(get_candidates_service),
        # -- Dependencies --
        tracking_service: TrackingService = Depends(get_tracking_service)
) -> models.FullStatistics:
    return tracking_service.calculate_full_statistics(candidate_id)


@router.get("/{candidate_id}/statistics", response_model=models.Statistics)
async def create_candidate(
        candidate_id: Annotated[int, Path(
            gt=0,
            description="Candidate ID which uniquely identifies a user as a candidate for a testing cycle.")],
        start_date: Annotated[date | None, Query(
            alias="startDate",
            description="The starting date to gather statistics for the candidate.")],
        end_date: Annotated[date | None, Query(
            alias="endDate",
            description="The ending date to gather statistics for the candidate.")],
        # -- Dependencies --
        tracking_service: TrackingService = Depends(get_tracking_service)
) -> models.Statistics:
    start_date: date = start_date or end_date or date.today()
    end_date: date = end_date or start_date or date.today()

    return tracking_service.calculate_statistics(candidate_id, start_date=start_date, end_date=end_date)
