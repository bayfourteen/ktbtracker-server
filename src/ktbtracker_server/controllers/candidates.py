import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi_utils.cbv import cbv

from ktbtracker_server.models import response, models
from ktbtracker_server.models.query import PaginationParams
from ktbtracker_server.services.candidates import CandidatesService, get_candidates_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/candidates", tags=["candidates"])


@cbv(router)
class CandidatesController:
    candidates_service: CandidatesService = Depends(get_candidates_service)

    @router.get("/", response_model=response.PagedResponse[models.Candidate])
    async def get_candidates(
            self,
            page: Annotated[int, Query(ge=0)] = 0,
            page_size: Annotated[int, Query(le=100, alias="size")] = 100,
            cycle_id: Annotated[int | None, Query(ge=0, alias="cycle")] = None,
    ) -> response.PagedResponse[models.Candidate]:
        return response.PagedResponse[models.Candidate](
            content=self.candidates_service.find_all(page, page_size),
            pagination=response.Pagination(
                page=page,
                page_size=page_size,
                total_elements=self.candidates_service.count_all()
            )
        )