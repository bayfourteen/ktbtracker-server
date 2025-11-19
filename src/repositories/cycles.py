import logging
from typing import Annotated, Sequence, Literal

from fastapi import Depends
from sqlmodel import Session, func, select

from config.mysql import get_session
from entities import entities

logger = logging.getLogger(__name__)


class CyclesRepository:
    def __init__(self, session: Session):
        self.session = session

    def count_all(self) -> int:
        return self.session.exec(select(func.count()).select_from(entities.Cycle)).first()

    def find_all(
            self,
            offset: int = 0,
            limit: int = 100,
            sort: Literal['asc', 'desc'] = 'desc'
    ) -> Sequence[entities.Cycle]:
        return self.session.exec(select(entities.Cycle)
                                 .offset(offset).limit(limit)
                                 .order_by(entities.Cycle.id if sort == 'asc' else entities.Cycle.id.desc())
                                 ).all()

    def find_by_id(self, id: int) -> entities.Cycle:
        return self.session.exec(select(entities.Cycle)
                                 .where(entities.Cycle.id == id)
                                 ).first()


async def get_cycles_repository(session: Annotated[Session, Depends(get_session)]):
    logger.info(f"Creating cycle repository with session {session}...")
    return CyclesRepository(session)
