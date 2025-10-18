from typing import Annotated, Sequence

from fastapi import Depends
from sqlmodel import Session, func, select

from ktbtracker_server.config.mysql import get_session
from ktbtracker_server.entities import entities
from ktbtracker_server.models import models


class CandidatesRepository:

    def __init__(self, session: Session):
        self.session = session

    def count_all(self) -> int:
        return self.session.exec(select(func.count()).select_from(entities.Candidate)).first()

    def find_all(self, offset: int = 0, limit: int = 100) -> Sequence[models.Candidate]:
        candidates = self.session.exec(select(entities.Candidate).offset(offset).limit(limit)).all()
        return [models.Candidate.model_validate(e) for e in candidates]

    def find_all_by_cycle_id(self, cycle_id: int, offset: int = 0, limit: int = 100) -> Sequence[models.Candidate]:
        candidates = self.session.exec(
            select(entities.Candidate)
            .offset(offset).limit(limit)
            .where(entities.Candidate.cycle_id == cycle_id)
            .order_by(entities.Candidate.id.asc())
        ).all()
        return [models.Candidate.model_validate(e) for e in candidates]

    def find_by_id(self, id: int) -> models.Candidate:
        candidate = self.session.exec(select(entities.Candidate).where(entities.Candidate.id == id)).first()
        return models.Candidate.model_validate(candidate) if candidate else None


async def get_candidates_repository(session: Annotated[Session, Depends(get_session)]):
    return CandidatesRepository(session)
