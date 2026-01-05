import logging
from typing import Annotated

from fastapi import Depends

from ktbtracker_server.models import models
from ktbtracker_server.repositories.site_users import get_site_users_repository, SiteUsersRepository


class SiteUsersService:
    def __init__(self, repository: SiteUsersRepository):
        self.repository = repository

    def find_by_email(self, email: str) -> models.SiteUser | None:
        if site_user := self.repository.find_by_email(email):
            return models.SiteUser.model_validate(site_user)
        return None

    def find_by_id(self, id: int) -> models.SiteUser | None:
        if site_user := self.repository.find_by_id(id):
            return models.SiteUser.model_validate(site_user)
        return None

    def find_by_user_id(self, user_id: str) -> models.SiteUser | None:
        if site_user := self.repository.find_by_user_id(user_id):
            return models.SiteUser.model_validate(site_user)
        return None


async def get_site_users_service(repository: Annotated[SiteUsersRepository, Depends(get_site_users_repository)]):
    logging.info(f"Creating CyclesService with repository {repository}...")
    return SiteUsersService(repository)
