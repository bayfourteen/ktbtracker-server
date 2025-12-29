from typing import Literal

from pydantic import MySQLDsn
from pydantic_settings import BaseSettings

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '[%(asctime)s] [%(levelname)-8s] %(name)s: %(message)s'
        },
        'custom_formatter': {
            'format': "[%(asctime)s] [%(processName)s: %(process)d] [%(threadName)s: %(thread)d] [%(levelname)-8s] %(name)s: %(message)s"

        },
    },
    'handlers': {
        'default': {
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',  # Default is stderr
        },
        'stream_handler': {
            'formatter': 'custom_formatter',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',  # Default is stderr
        },
        'file_handler': {
            'formatter': 'custom_formatter',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'app.log',
            'maxBytes': 1024 * 1024 * 1,  # = 1MB
            'backupCount': 3,
        },
    },
    'loggers': {
        '': {
            'handlers': ['default', 'file_handler'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'uvicorn': {
            'handlers': ['file_handler'],
            'level': 'TRACE',
            'propagate': False
        },
        'uvicorn.access': {
            'handlers': ['file_handler'],
            'level': 'TRACE',
            'propagate': False
        },
        'uvicorn.error': {
            'handlers': ['file_handler'],
            'level': 'TRACE',
            'propagate': False
        },
        'uvicorn.asgi': {
            'handlers': ['file_handler'],
            'level': 'TRACE',
            'propagate': False
        },
    },
}


class Settings(BaseSettings):
    database_url: MySQLDsn
    auto_flush: bool = False
    google_application_credentials: str = None
    supported_locales: list[str] = ["en", "es", "ko"]


async def get_settings() -> Settings:
    return Settings()
