import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from ktbtracker_server.models import response, models
from ktbtracker_server.services.candidates import CandidatesService, get_candidates_service

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