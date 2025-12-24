import logging.config
import logging.config
import os
import secrets

import firebase_admin
import sqlalchemy
import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from api.v1.candidates import router as api_candidates_router
from api.v1.cycles import router as api_cycles_router
from config.observability import CustomLogger
from config.settings import LOGGING_CONFIG
from src.webui import errors
from webui.admin.views import router as webui_admin_router
from webui.auth.views import router as webui_auth_router
from webui.tracking.views import router as webui_tracking_router
from webui.views import router as webui_router

logging.setLoggerClass(CustomLogger)
logging.config.dictConfig(LOGGING_CONFIG)

logger = logging.getLogger(__name__)


def locale_selector(request: Request) -> str:
    return request.cookies.get("locale") or "en" # Fallback to "en" if no cookie is set


def create_app():
    app = FastAPI()

    #
    # Initialize Google Firebase Administration SDK
    #
    cert_creds = firebase_admin.credentials.Certificate(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))
    firebase_admin.initialize_app(cert_creds)
    logger.info("Google Firebase Administration SDK successfully initialized for project"
                f" '{firebase_admin.get_app().project_id}'.")

    app.add_exception_handler(sqlalchemy.exc.OperationalError, errors.operational_error_handler)

    #
    # Load any middleware
    #
    #app.add_middleware(
    #    BabelMiddleware,
    #    babel_configs=configs,
    #    jinja2_templates=get_templates(),
    #    locale_selector=locale_selector,
    #)

    # app.add_middleware(FastAPICSRFJinjaMiddleware, secret=secrets.token_urlsafe(32))

    # app.add_middleware(RequestLoggerMiddleware, logger=logger)
    # app.add_middleware(I18nMiddleware, templates=get_templates())
    app.add_middleware(SessionMiddleware, secret_key=secrets.token_urlsafe(32))

    app.mount("/static", StaticFiles(directory="static"), name="static")
    #templates.env.install_gettext_translations(Translations.load("locale", ["en"]))

    app.include_router(webui_router)
    app.include_router(webui_auth_router)
    app.include_router(webui_tracking_router)
    app.include_router(webui_admin_router, prefix="/admin")

    app.include_router(api_cycles_router, prefix="/ktbtracker/v1")
    app.include_router(api_candidates_router, prefix="/ktbtracker/v1")

    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True, log_config="logging.json")
