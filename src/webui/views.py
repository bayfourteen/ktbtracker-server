import base64
import json
import logging
from datetime import date, timedelta, datetime, UTC
from typing import Annotated, OrderedDict, Any
from urllib.parse import quote

import pyrebase
from babel.dates import format_date
from fastapi import APIRouter, Request, Response, Depends, Query, Form, Path, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from firebase_admin import auth

from src.config.firebase import get_current_user, FIREBASE_CHECK_REVOKED, FIREBASE_CONFIG, FIREBASE_COOKIE, FIREBASE_COOKIE_TTL, FIREBASE_SECURE, FIREBASE_HTTPONLY, \
    get_current_session
from src.config.i18n import _
from src.config.jinja2 import get_templates
from src.config.observability import debug
from src.config.requirements import RequirementsConfig
from src.models import models
from src.models.models import Tracking, TrackingForm, Candidate
from src.models.session import SessionData
from src.services.candidates import CandidatesService, get_candidates_service
from src.services.cycles import CyclesService, get_cycles_service
from src.services.site_users import SiteUsersService, get_site_users_service
from src.services.tracking import TrackingService, get_tracking_service


TRACKING_NAMES = OrderedDict({e: _(e) for e in (RequirementsConfig.PHYSICAL + RequirementsConfig.CLASS + RequirementsConfig.OTHER)})

logger = logging.getLogger('uvicorn')

firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
pyrebase_auth = firebase.auth()

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
    if session_cookie := request.cookies.get(FIREBASE_COOKIE):
        try:
            decoded_claims = auth.verify_session_cookie(session_cookie, check_revoked=FIREBASE_CHECK_REVOKED)

        except auth.InvalidSessionCookieError:
            pass

    if query_cookie := request.cookies.get("q"):
        try:
            decoded_query = json.loads(base64.b64decode(query_cookie.encode("utf-8")))

        except json.JSONDecodeError:
            pass

    if decoded_claims and decoded_query.get("candidate_id") is None:
        if current_user := site_users_service.find_by_user_id(decoded_claims.get("user_id")):
            if candidates := candidates_service.find_all_by_user_id(current_user.id):
                decoded_query["candidate_id"] = candidates[0].id

    if decoded_claims and decoded_query.get("week") is None:
        if decoded_query.get("candidate_id") and (candidate := candidates_service.find_by_id(decoded_query.get("candidate_id"))):
            cycle = cycles_service.find_by_id(candidate.cycle_id)
            decoded_query["week"] = cycle.cycle_week_of(decoded_query.get("tracking_date") or date.today()).week

    return SessionData(**decoded_claims, **decoded_query)



@router.get("/", response_class=HTMLResponse)
async def index(
        request: Request,
        # -- Dependencies --
        templates: Jinja2Templates = Depends(get_templates),
        cycles_service: CyclesService = Depends(get_cycles_service),
):
    cycles = cycles_service.find_all()
    return templates.TemplateResponse("index.html", {"request": request, "cycles": cycles})


@router.get("/login", response_class=HTMLResponse)
@debug
async def login(
        request: Request,
        error: Annotated[str | None, Query(...)] = None,
        return_url: Annotated[str | None, Query(alias="returnUrl")] = None,
        # -- Dependencies --
        templates: Jinja2Templates = Depends(get_templates),
):
    # If the user is currently logged-in, simply redirect to return URL (or "/")
    if session_cookie := request.cookies.get(FIREBASE_COOKIE):
        try:
            decoded_claims = auth.verify_session_cookie(session_cookie, check_revoked=FIREBASE_CHECK_REVOKED)

            return RedirectResponse(url=return_url or "/", status_code=status.HTTP_303_SEE_OTHER)

        except auth.InvalidSessionCookieError:
            pass

    return templates.TemplateResponse("login/index.html", context={
        "request": request,
        "next_url": return_url,
        "error": None,
        "page_background": "bg-primary"
    })


@router.post("/login", response_class=HTMLResponse)
async def login_post(

        request: Request,
        email: Annotated[str, Form(...)],
        password: Annotated[str, Form(...)],
        error: Annotated[str | None, Form(...)] = None,
        next_url: Annotated[str | None, Form(...)] = None,
        # -- Dependencies --
        templates: Jinja2Templates = Depends(get_templates),
        candidates_service: CandidatesService = Depends(get_candidates_service),
        cycles_service: CyclesService = Depends(get_cycles_service),
        site_users_service: SiteUsersService = Depends(get_site_users_service),
):
    # If the user is currently logged-in, simply redirect to return URL (or "/")
    if session_cookie := request.cookies.get(FIREBASE_COOKIE):
        try:
            decoded_claims = auth.verify_session_cookie(session_cookie, check_revoked=FIREBASE_CHECK_REVOKED)
            logging.info(f"Logged in from {decoded_claims=}")

            return RedirectResponse(url=next_url or "/", status_code=status.HTTP_303_SEE_OTHER)

        except auth.InvalidSessionCookieError:
            return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    logging.info(f"No session cookie found!")
    # Ensure that both a "username" and "password" were provided
    if email is None or password is None:
        return RedirectResponse(url=f'/login?error={quote('Missing email or password')}{'&next_url=' + next_url if next_url else ''}', status_code=status.HTTP_302_FOUND)

    try:
        user = pyrebase_auth.sign_in_with_email_and_password(email, password)
        logging.info(f"Logged in as {user=}")
        session_cookie = auth.create_session_cookie(user.get("idToken"), expires_in=FIREBASE_COOKIE_TTL)

        response = RedirectResponse(url=next_url or "/", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(FIREBASE_COOKIE, session_cookie, expires=datetime.now(UTC) + FIREBASE_COOKIE_TTL, secure=FIREBASE_SECURE, httponly=FIREBASE_HTTPONLY)

        return response

    except Exception as e:
        logging.error(e, exc_info=True)
        return RedirectResponse(url=f'/login?error={quote(e)}{'&next_url=' + next_url if next_url else ''}', status_code=status.HTTP_303_SEE_OTHER)

    return RedirectResponse(url=return_url or "/", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/logout", response_class=HTMLResponse)
@debug
async def logout(
        request: Request,
        return_url: Annotated[str | None, Query(alias="returnUrl")] = None,
        # -- Dependencies --
        templates: Jinja2Templates = Depends(get_templates)
):
    response = RedirectResponse(url=f'/login{'?next_url=' + return_url if return_url else ''}', status_code=status.HTTP_302_FOUND)

    if session_cookie := request.cookies.get(FIREBASE_COOKIE):
        logging.info(f"Logged in... {session_cookie=}")
        try:
            decoded_claims = auth.verify_session_cookie(session_cookie, check_revoked=FIREBASE_CHECK_REVOKED)
            logging.info(f"Logged out from {decoded_claims=}")
            auth.revoke_refresh_tokens(decoded_claims.get("sub"))
            response.set_cookie(FIREBASE_COOKIE, expires=0, secure=FIREBASE_SECURE, httponly=FIREBASE_HTTPONLY)

        except auth.RevokedSessionCookieError | auth.InvalidSessionCookieError as e:
            logging.info(f"Logged out from {e}")
            response.set_cookie(FIREBASE_COOKIE, expires=0, secure=FIREBASE_SECURE, httponly=FIREBASE_HTTPONLY)

    else:
        logging.info(f"No session cookie found!")

    response.set_cookie("current_user", expires=0, secure=FIREBASE_SECURE, httponly=FIREBASE_HTTPONLY)
    response.set_cookie("current_candidate", expires=0, secure=FIREBASE_SECURE, httponly=FIREBASE_HTTPONLY)

    return response


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
