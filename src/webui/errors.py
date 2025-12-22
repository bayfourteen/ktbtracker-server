from http.client import HTTPException

from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic_core._pydantic_core import ValidationError
from sqlalchemy.exc import OperationalError, SQLAlchemyError

from src.config.jinja2 import get_templates
from src.config.observability import debug

app = FastAPI()


@app.exception_handler(Exception)
@debug
async def http_exception_handler(
        request: Request,
        exc: Exception,
        # -- Dependencies --
        templates: Jinja2Templates = Depends(get_templates),
) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request, "page_background": "bg-danger"})


@app.exception_handler(OperationalError)
@debug
async def http_exception_handler(
        request: Request,
        exc: OperationalError,
        # -- Dependencies --
        templates: Jinja2Templates = Depends(get_templates),
) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request, "page_background": "bg-danger"})


@app.exception_handler(SQLAlchemyError)
@debug
async def http_exception_handler(
        request: Request,
        exc: SQLAlchemyError,
        # -- Dependencies --
        templates: Jinja2Templates = Depends(get_templates),
) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request, "page_background": "bg-danger"})


@app.exception_handler(ValidationError)
@debug
async def http_exception_handler(
        request: Request,
        exc: ValidationError,
        # -- Dependencies --
        templates: Jinja2Templates = Depends(get_templates),
) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request, "page_background": "bg-danger"})
