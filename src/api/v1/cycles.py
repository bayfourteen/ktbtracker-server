
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Query, HTTPException, Path

from models import models, response
from services.candidates import CandidatesService, get_candidates_service
from services.cycles import CyclesService, get_cycles_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cycles", tags=["cycles"])


@router.get("/", response_model=response.PagedResponse[models.Cycle])
def get_cycles(
        page: Annotated[int, Query(ge=0)] = 0,
        page_size: Annotated[int, Query(le=100, alias="size")] = 100,
        # -- Dependencies --
        cycles_service: CandidatesService = Depends(get_cycles_service),
) -> response.PagedResponse[models.Cycle]:
    return response.PagedResponse[models.Cycle](
        content=cycles_service.find_all(page, page_size),
        pagination=response.Pagination(
            page=page,
            page_size=page_size,
            total_elements=cycles_service.count_all()
        )
    )


@router.get("/{cycle_id}", response_model=models.Cycle)
def get_cycle(
        cycle_id: Annotated[int, Path(gt=0)],
        # -- Dependencies --
        cycles_service: CyclesService = Depends(get_cycles_service),
) -> models.Cycle:
    cycle = cycles_service.find_by_id(cycle_id)

    if not cycle:
        raise HTTPException(status_code=404, detail="Cycle not found")

    return models.Cycle.model_validate(cycle) if cycle else None


@router.get("/{cycle_id}/candidates", response_model=response.PagedResponse[models.Candidate])
def get_cycle_candidates(
        cycle_id: Annotated[int, Path(gt=0)],
        page: Annotated[int, Query(ge=0)] = 0,
        page_size: Annotated[int, Query(le=100, alias="size")] = 100,
        # -- Dependencies --
        candidates_service: CandidatesService = Depends(get_candidates_service),
) -> response.PagedResponse[models.Candidate]:
     return response.PagedResponse[models.Candidate](
        content=candidates_service.find_all_by_cycle_id(cycle_id),
        pagination=response.Pagination(
            page=page,
            page_size=page_size,
            total_elements=candidates_service.count_all_by_cycle_id(cycle_id)
        )
    )
