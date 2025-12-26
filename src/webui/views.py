import base64
import json
import logging
from datetime import date
from typing import Annotated, OrderedDict, Any

import sqlalchemy
from babel.dates import format_date
from fastapi import APIRouter, Request, Depends, Query, Form, Path, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from firebase_admin import auth
from pymysql import OperationalError
from sqlalchemy.exc import SQLAlchemyError

from src.config import firebase
from src.config.firebase import get_current_session
from src.config.i18n import _
from src.config.jinja2 import get_templates
from src.config.observability import debug
from src.config.requirements import RequirementsConfig
from src.models.models import TrackingForm
from src.models.session import SessionData
from src.services.candidates import CandidatesService, get_candidates_service
from src.services.cycles import CyclesService, get_cycles_service
from src.services.site_users import SiteUsersService, get_site_users_service
from src.services.tracking import TrackingService, get_tracking_service

TRACKING_NAMES = OrderedDict({e: _(e) for e in (RequirementsConfig.PHYSICAL + RequirementsConfig.CLASS + RequirementsConfig.OTHER)})

logger = logging.getLogger('uvicorn')

router = APIRouter()

@debug
async def get_session_data(
        request: Request,
        # -- Dependencies --
        candidates_service: CandidatesService = Depends(get_candidates_service),
        cycles_service: CyclesService = Depends(get_cycles_service),
        site_users_service: SiteUsersService = Depends(get_site_users_service),
) -> SessionData | None:
    decoded_claims, decoded_query = {}, {}
    if session_cookie := request.cookies.get(firebase.COOKIE):
        try:
            decoded_claims = auth.verify_session_cookie(session_cookie, check_revoked=True)

        except auth.InvalidSessionCookieError:
            pass

    if query_cookie := request.cookies.get("q"):
        try:
            decoded_query = json.loads(base64.b64decode(query_cookie.encode("utf-8")))

        except json.JSONDecodeError:
            pass

    if decoded_claims and decoded_query.get("candidate_id") is None:
        try:
            if current_user := site_users_service.find_by_user_id(decoded_claims.get("user_id")):
                if candidates := candidates_service.find_all_by_user_id(current_user.id):
                    decoded_query["candidate_id"] = candidates[0].id
        except sqlalchemy.exc.OperationalError as e:
            pass

    if decoded_claims and decoded_query.get("week") is None:
        try:
            if decoded_query.get("candidate_id") and (candidate := candidates_service.find_by_id(decoded_query.get("candidate_id"))):
                cycle = cycles_service.find_by_id(candidate.cycle_id)
                decoded_query["week"] = cycle.cycle_week_of(decoded_query.get("tracking_date") or date.today()).week
        except sqlalchemy.exc.OperationalError as e:
            pass

    return SessionData(**decoded_claims, **decoded_query)



@router.get("/", response_class=HTMLResponse)
async def index(
        request: Request,
        # -- Dependencies --
        templates: Jinja2Templates = Depends(get_templates),
        cycles_service: CyclesService = Depends(get_cycles_service),
):
    try:
        cycles = cycles_service.find_all()
        return templates.TemplateResponse("index.html", {"request": request, "cycles": cycles})

    except sqlalchemy.exc.OperationalError as e:
        # Inform users if database is unavailable...
        if "Connection refused" in str(e):
            return templates.TemplateResponse("sysdown.html", {"request": request, "error": str(e)})

        return templates.TemplateResponse("error.html", {"request": request, "error": str(e)})



@router.get("/tracking", response_class=HTMLResponse, response_model=None)
@debug
async def get_tracking(
        request: Request,
        candidate_id: Annotated[int | None, Query(gt=0, alias="canid")] = None,
        tracking_date: Annotated[date | None, Query(alias="trackingDate")] = None,
        week: Annotated[int | None, Query(alias="week")] = None,
        # -- Dependencies --
        session_data: SessionData = Depends(get_session_data),
        user: dict[str, Any] = Depends(get_current_session),
        templates: Jinja2Templates = Depends(get_templates),
        candidates_service: CandidatesService = Depends(get_candidates_service),
        cycles_service: CyclesService = Depends(get_cycles_service),
        site_users_service: SiteUsersService = Depends(get_site_users_service),
        tracking_service: TrackingService = Depends(get_tracking_service),
):
    logging.info(f"**** {candidate_id=} {week=} {user=} ")
    candidate_cookie = request.cookies.get("current_candidate")
    candidate = candidates_service.find_by_id(candidate_id or session_data.candidate_id)
    logging.info(f"**** {candidate=}")
    if candidate:
        if cycle := cycles_service.find_by_id(candidate.cycle_id):
            tracking_week = cycle.cycle_week(week) if week else cycle.cycle_week_of(tracking_date or date.today())
            # tracking_week = cycle.cycle_week_of(tracking_date) if tracking_date else cycle.cycle_week(week or 0)
            tracking_data = tracking_service.find_all_by_candidate_id_and_date_range(candidate.id, tracking_week.start, tracking_week.end)
            tracking_stats = tracking_service.calculate_full_statistics(candidate.id)
            tracking_day = cycle.cycle_day(tracking_week.start)
            context = {
                "tracking_date": format_date(tracking_date, format="Y-M-d"),
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
            logging.info("**** Tracking data: %d %s", len(tracking_data), tracking_data)
            return templates.TemplateResponse("tracking/index.html", context)
    return HTMLResponse()


@router.post("/tracking", response_class=HTMLResponse, response_model=None)
@debug
async def create_tracking(
        tracking_date: Annotated[date, Form(alias="trackingDate")],
        candidate_id: Annotated[int, Form(alias="candidateId")],
        miles: Annotated[int, Form(alias="miles")],
        # -- Dependencies --
        templates: Jinja2Templates = Depends(get_templates),
        candidates_service: CandidatesService = Depends(get_candidates_service),
        cycles_service: CyclesService = Depends(get_cycles_service),
        tracking_service: TrackingService = Depends(get_tracking_service),
):
    pass


@router.post("/tracking/{tracking_date}", response_class=HTMLResponse, response_model=None)
@debug
async def update_tracking(
        tracking_date: Annotated[date, Path()],
        form: Annotated[TrackingForm, Form()],
        # -- Dependencies --
        request: Request,
        templates: Jinja2Templates = Depends(get_templates),
        candidates_service: CandidatesService = Depends(get_candidates_service),
        cycles_service: CyclesService = Depends(get_cycles_service),
        tracking_service: TrackingService = Depends(get_tracking_service),
):
    logger.info(f"**** {tracking_date=} {form=}")
    return RedirectResponse(request.url_for('get_tracking'), status_code=status.HTTP_303_SEE_OTHER)
