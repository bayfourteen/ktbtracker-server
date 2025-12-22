import logging
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, select

from config.mysql import get_session
from entities import entities


class SiteUsersRepository:
    def __init__(self, session: Session):
        self.session = session

    def find_by_email(self, email: str) -> entities.SiteUser:
        return self.session.exec(select(entities.SiteUser)
                                 .where(entities.SiteUser.email == email)
                                 ).first()

    def find_by_id(self, id: int) -> entities.SiteUser:
        return self.session.exec(select(entities.SiteUser)
                                 .where(entities.SiteUser.id == id)
                                 ).first()

    def find_by_user_id(self, user_id: str) -> entities.SiteUser:
        return self.session.exec(select(entities.SiteUser)
                                 .where(entities.SiteUser.user_id == user_id)
                                 ).first()


async def get_site_users_repository(session: Annotated[Session, Depends(get_session)]):
    logging.info(f"Creating cycle repository with session {session}...")
    return SiteUsersRepository(session)
