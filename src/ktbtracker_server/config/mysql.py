import logging
from contextlib import contextmanager
from typing import Annotated, Generator, AsyncGenerator, Any

from fastapi import Depends
from sqlmodel import Session, create_engine

from ktbtracker_server.config.settings import Settings, get_settings

logger = logging.getLogger(__name__)


def create_database(self) -> None:
    pass

async def get_session(settings: Annotated[Settings, Depends(get_settings)]) -> AsyncGenerator[Session, Any]:
    logger.info(f"Creating session for {settings.database_url}...")
    engine = create_engine(str(settings.database_url), echo=True)

    with Session(engine, autocommit=False, autoflush=settings.auto_flush) as _session:
        try:
            yield _session
        finally:
            _session.close()
