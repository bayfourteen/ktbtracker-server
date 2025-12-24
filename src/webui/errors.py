from http.client import HTTPException

import sqlalchemy
from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic_core._pydantic_core import ValidationError
from sqlalchemy.exc import OperationalError, SQLAlchemyError

from src.config.jinja2 import get_templates
from src.config.observability import debug

app = FastAPI()


@app.exception_handler(sqlalchemy.exc.OperationalError)
@debug
async def operational_error_handler(
        request: Request,
        exc: sqlalchemy.exc.OperationalError,
        # -- Dependencies --
        templates: Jinja2Templates = Depends(get_templates),
) -> HTMLResponse:
    return templates.TemplateResponse("sysdown.html", {"request": request, "error": str(exc), "page_background": "bg-danger"})

