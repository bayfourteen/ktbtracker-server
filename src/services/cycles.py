import logging
from typing import Annotated, Sequence, Literal

from fastapi import Depends

from models import models
from repositories.cycles import CyclesRepository, get_cycles_repository


logger = logging.getLogger(__name__)


class CyclesService:
    def __init__(self, repository: CyclesRepository):
        self.repository = repository

    def count_all(self) -> int:
        return self.repository.count_all()

    def find_all(
            self,
            offset: int = 0,
            limit: int = 100,
            sort: Literal['asc', 'desc'] = 'desc'
    ) -> Sequence[models.Cycle]:
        return [models.Cycle.model_validate(e)
                for e in self.repository.find_all(offset=offset, limit=limit, sort=sort)]

    def find_by_id(self, id: int) -> models.Cycle | None:
        if cycle := self.repository.find_by_id(id):
            return models.Cycle.model_validate(cycle)
        return None


async def get_cycles_service(repository: Annotated[CyclesRepository, Depends(get_cycles_repository)]):
    logger.info(f"Creating CyclesService with repository {repository}...")
    return CyclesService(repository)
