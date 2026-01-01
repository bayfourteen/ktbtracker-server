import base64
import json
from datetime import date

import sqlalchemy
from fastapi import Depends, Request
from firebase_admin import auth

from config import firebase
from config.observability import debug
from models.session import SessionData
from services.candidates import CandidatesService, get_candidates_service
from services.cycles import CyclesService, get_cycles_service
from services.site_users import SiteUsersService, get_site_users_service


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

