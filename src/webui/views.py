import logging
from datetime import date

from babel.dates import format_date
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi_babel import _

from config.requirements import RequirementsConfig
from services.candidates import CandidatesService, get_candidates_service
from services.cycles import CyclesService, get_cycles_service
from services.tracking import TrackingService, get_tracking_service


logger = logging.getLogger(__name__)

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


@router.get("/tracking", response_class=HTMLResponse)
async def about(
        request: Request,
        # -- Dependencies --
        candidates_service: CandidatesService = Depends(get_candidates_service),
        cycles_service: CyclesService = Depends(get_cycles_service),
        tracking_service: TrackingService = Depends(get_tracking_service),
):
    if candidate := candidates_service.find_by_id(627):
        if cycle := cycles_service.find_by_id(candidate.cycle_id):
            tracking_data = tracking_service.find_all_by_candidate_id_and_date_range(627, date(2025, 8, 10), date(2025, 8, 16))
            tracking_names = RequirementsConfig.PHYSICAL + RequirementsConfig.CLASS + RequirementsConfig.OTHER
            tracking_day = cycle.cycle_day(date(2025, 8, 10))
            cycle_days = list(range(tracking_day, tracking_day + 7))
            logger.info("tracking data: %s", tracking_data)
            return templates.TemplateResponse("tracking.html", {"request": request, "tracking_data": tracking_data, "tracking_names": tracking_names, "cycle_days": cycle_days})
