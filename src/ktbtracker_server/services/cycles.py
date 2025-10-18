import logging
from typing import Annotated, Sequence

from fastapi import Depends

from ktbtracker_server.models import models
from ktbtracker_server.repositories.cycles import CyclesRepository, get_cycles_repository


logger = logging.getLogger(__name__)


class CyclesService:
    def __init__(self, repository: CyclesRepository):
        self.repository = repository

    def count_all(self) -> int:
        return self.repository.count_all()

    def find_all(self, offset: int = 0, limit: int = 100) -> Sequence[models.Cycle]:
        return self.repository.find_all(offset, limit)

    def find_by_id(self, id: int) -> models.Cycle:
        return self.repository.find_by_id(id)


async def get_cycles_service(repository: Annotated[CyclesRepository, Depends(get_cycles_repository)]):
    logger.info(f"Creating CyclesService with repository {repository}...")
    return CyclesService(repository)
