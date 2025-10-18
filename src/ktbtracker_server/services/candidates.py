from typing import Annotated, Sequence

from fastapi import Depends

from ktbtracker_server.models import models
from ktbtracker_server.repositories.candidates import CandidatesRepository, get_candidates_repository


class CandidatesService:

    def __init__(self, repository):
        self.repository = repository

    def count_all(self) -> int:
        return self.repository.count_all()

    def find_all(self, offset: int = 0, limit: int = 100) -> Sequence[models.Cycle]:
        return self.repository.find_all(offset=offset, limit=limit)

    def find_all_by_cycle_id(self, cycle_id: int, offset: int = 0, limit: int = 100) -> Sequence[models.Cycle]:
        return self.repository.find_all_by_cycle_id(cycle_id, offset=offset, limit=limit)


async def get_candidates_service(repository: Annotated[CandidatesRepository, Depends(get_candidates_repository)]):
    return CandidatesService(repository)
