from babel.dates import format_date
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi_babel import _

from config.jinja2 import get_templates
from services.candidates import CandidatesService, get_candidates_service
from services.cycles import CyclesService, get_cycles_service

router = APIRouter()

templates = Jinja2Templates(directory="templates")
templates.env.globals.update(_=_)
templates.env.filters["format_date"] = \
        lambda dt, format='medium', locale='en_US': format_date(dt, format=format, locale=locale)


@router.get("/", response_class=HTMLResponse)
async def index(
        request: Request,
        # -- Dependencies --
        cycles_service: CyclesService = Depends(get_cycles_service),
):
    cycles = cycles_service.find_all()
    return templates.TemplateResponse("index.html", {"request": request, "cycles": cycles})
