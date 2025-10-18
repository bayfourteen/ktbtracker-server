import json
import logging
import os
from pathlib import Path

import firebase_admin
import uvicorn
from fastapi import FastAPI

from ktbtracker_server.config.settings import LOGGING_CONFIG
from ktbtracker_server.controllers.candidates import router as candidates_router
from ktbtracker_server.controllers.cycles import router as cycles_router


#logging.basicConfig(format="[%(asctime)s] [%(levelname)-8s] %(name)s: %(message)s",level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app():
    app = FastAPI()

    #
    # Initialize Google Firebase Administration SDK
    #
    cert_creds = firebase_admin.credentials.Certificate(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))
    firebase_admin.initialize_app(cert_creds)
    logger.info("Google Firebase Administration SDK successfully initialized for project"
                f" '{firebase_admin.get_app().project_id}'.")

    app.include_router(cycles_router, prefix="/ktbtracker/v1")
    app.include_router(candidates_router, prefix="/ktbtracker/v1")

    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True, log_config="logging.json")
