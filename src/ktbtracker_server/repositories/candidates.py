from typing import Annotated, Sequence, Literal

from fastapi import Depends
from sqlmodel import Session, func, select

from ktbtracker_server.config.mysql import get_session
from ktbtracker_server.entities import entities


class CandidatesRepository:

    def __init__(self, session: Session):
        self.session = session

    def count_all(self) -> int:
        return self.session.exec(select(func.count())
                                 .select_from(entities.Candidate)
                                 ).first()

    def count_all_by_cycle_id(
            self,
            cycle_id: int
    ) -> int:
        return self.session.exec(select(func.count())
                                 .select_from(entities.Candidate)
                                 .where(entities.Candidate.cycle_id == cycle_id)
                                 ).first()

    def find_all(
            self,
            offset: int = 0,
            limit: int = 100,
            sort: Literal['asc', 'desc'] = 'asc'
    ) -> Sequence[entities.Candidate]:
        return self.session.exec(select(entities.Candidate)
                                 .offset(offset).limit(limit)
                                 .order_by(entities.Candidate.id if sort == 'asc' else entities.Candidate.id.desc())
                                 ).all()

    def find_all_by_cycle_id(
            self,
            cycle_id: int,
            offset: int = 0,
            limit: int = 100,
            sort: Literal['asc', 'desc'] = 'asc'
    ) -> Sequence[entities.Candidate]:
        return self.session.exec(select(entities.Candidate)
                                 .offset(offset).limit(limit)
                                 .where(entities.Candidate.cycle_id == cycle_id)
                                 .order_by(entities.Candidate.id if sort == 'asc' else entities.Candidate.id.desc())
                                 ).all()

    def find_by_id(
            self,
            id: int
    ) -> entities.Candidate:
        return self.session.exec(select(entities.Candidate)
                                 .where(entities.Candidate.id == id)
                                 ).first()


async def get_candidates_repository(session: Annotated[Session, Depends(get_session)]):
    return CandidatesRepository(session)
