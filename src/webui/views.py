import logging
from datetime import date
from typing import Annotated, OrderedDict

from babel.dates import format_date
from fastapi import APIRouter, Request, Depends, Query, Form, Path
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from config.i18n import _
from config.jinja2 import get_templates
from config.requirements import RequirementsConfig
from models.models import Tracking
from services.candidates import CandidatesService, get_candidates_service
from services.cycles import CyclesService, get_cycles_service
from services.tracking import TrackingService, get_tracking_service


TRACKING_NAMES = OrderedDict({e: _(e) for e in (RequirementsConfig.PHYSICAL + RequirementsConfig.CLASS + RequirementsConfig.OTHER)})

logger = logging.getLogger('uvicorn')

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def index(
        request: Request,
        # -- Dependencies --
        templates: Jinja2Templates = Depends(get_templates),
        cycles_service: CyclesService = Depends(get_cycles_service),
):
    cycles = cycles_service.find_all()
    return templates.TemplateResponse("index.html", {"request": request, "cycles": cycles})


@router.get("/tracking", response_class=HTMLResponse, response_model=None)
async def get_tracking(
        request: Request,
        candidate_id: Annotated[int | None, Query(gt=0, alias="canid")] = 627,
        tracking_date: Annotated[date | None, Query(alias="trackingDate")] = date.today(),
        week: Annotated[int | None, Query(alias="week")] = 0,
        # -- Dependencies --
        templates: Jinja2Templates = Depends(get_templates),
        candidates_service: CandidatesService = Depends(get_candidates_service),
        cycles_service: CyclesService = Depends(get_cycles_service),
        tracking_service: TrackingService = Depends(get_tracking_service),
):
    logger.info(f"**** {candidate_id=} {week=}")
    if candidate := candidates_service.find_by_id(candidate_id):
        if cycle := cycles_service.find_by_id(candidate.cycle_id):
            tracking_week = cycle.cycle_week_of(tracking_date) if tracking_date else cycle.cycle_week(week or 0)
            tracking_data = tracking_service.find_all_by_candidate_id_and_date_range(candidate_id, tracking_week.start, tracking_week.end)
            tracking_stats = tracking_service.calculate_full_statistics(candidate_id)
            tracking_day = cycle.cycle_day(tracking_week.start)
            context = {
                "request": request,
                "candidate": candidate,
                "cycle": cycle.model_dump(),
                "tracking_data": [e.model_dump() for e in tracking_data],
                "totals": tracking_stats.model_dump()["totals"],
                "statistics": tracking_stats.model_dump()["statistics"],
                "TRACKING_NAMES": TRACKING_NAMES,
                "tracking_week": tracking_week,
                "today": date.today(),

            }
            cycle_days = list(range(tracking_day, tracking_day + 7))
            logger.info("**** Tracking data: %d %s", len(tracking_data), tracking_data)
            return templates.TemplateResponse("tracking/index.html", context)
    return HTMLResponse()


@router.post("/tracking", response_class=HTMLResponse, response_model=None)
async def create_tracking(
        form: Annotated[Tracking, Form] = Form({}),
        # -- Dependencies --
        templates: Jinja2Templates = Depends(get_templates),
        candidates_service: CandidatesService = Depends(get_candidates_service),
        cycles_service: CyclesService = Depends(get_cycles_service),
        tracking_service: TrackingService = Depends(get_tracking_service),
):
    pass


@router.post("/tracking/{tracking_date}", response_class=HTMLResponse, response_model=None)
async def update_tracking(
        tracking_date: Annotated[date, Path()],
        form: Annotated[Tracking, Form()],
        # -- Dependencies --
        templates: Jinja2Templates = Depends(get_templates),
        candidates_service: CandidatesService = Depends(get_candidates_service),
        cycles_service: CyclesService = Depends(get_cycles_service),
        tracking_service: TrackingService = Depends(get_tracking_service),
):
    logger.info(f"**** {tracking_date=} {form=}")
