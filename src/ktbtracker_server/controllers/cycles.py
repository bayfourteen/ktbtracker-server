import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Query, HTTPException, Path
from fastapi_utils.cbv import cbv

from ktbtracker_server.models import models
from ktbtracker_server.models import response
from ktbtracker_server.services.cycles import CyclesService, get_cycles_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cycles", tags=["cycles"])


@cbv(router)
class CyclesController:
    cycles_service: CyclesService = Depends(get_cycles_service)

    def __init__(self, *args, **kwargs):
        logger.debug("CyclesController init")

    @router.get("/", response_model=response.PagedResponse[models.Cycle])
    async def get_cycles(
            self,
            page: Annotated[int, Query(ge=0)] = 0,
            page_size: Annotated[int, Query(le=100, alias="size")] = 100,
    ) -> response.PagedResponse[models.Cycle]:
        logger.info(f"CyclesController.get_cycles: {page} {page_size}")
        return response.PagedResponse[models.Cycle](
            content=self.cycles_service.find_all(page, page_size),
            pagination=response.Pagination(
                page=page,
                page_size=page_size,
                total_elements=self.cycles_service.count_all()
            )
        )

    @router.get("/{cycle_id}", response_model=models.Cycle)
    def get_cycle(
            self,
            cycle_id: Annotated[int, Path(gt=0)],
    ) -> models.Cycle:
        cycle = self.cycles_service.find_by_id(cycle_id)

        if not cycle:
            raise HTTPException(status_code=404, detail="Cycle not found")

        return models.Cycle.model_validate(cycle) if cycle else None
