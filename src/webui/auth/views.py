import logging
from datetime import datetime, UTC
from types import NoneType
from typing import Annotated
from urllib.parse import quote

import pyrebase

import pyrebase
from fastapi import APIRouter, Depends, FastAPI, Form, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from firebase_admin import auth

from src.config import firebase
from src.config.jinja2 import get_templates
from src.config.observability import debug

logger = logging.getLogger(__name__)

firebase_app = pyrebase.initialize_app(firebase.FIREBASE_CONFIG)
pyrebase_auth = firebase_app.auth()

router = APIRouter()


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
    if session_cookie := request.cookies.get(firebase.COOKIE):
        try:
            decoded_claims = auth.verify_session_cookie(session_cookie, check_revoked=True)

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
@debug
async def login_post(

        request: Request,
        email: Annotated[str, Form(...)],
        password: Annotated[str, Form(...)],
        error: Annotated[str | None, Form(...)] = None,
        next_url: Annotated[str | None, Form(...)] = None,
        # -- Dependencies --
        templates: Jinja2Templates = Depends(get_templates),
):
    # If the user is currently logged-in, simply redirect to return URL (or "/")
    if session_cookie := request.cookies.get(firebase.COOKIE):
        try:
            decoded_claims = auth.verify_session_cookie(session_cookie, check_revoked=True)
            logging.info(f"Already logged in as {decoded_claims=}")
            logging.info(f"Redirecting {'/' if next_url == 'None' else next_url}")

            return RedirectResponse(url="/" if next_url == 'None' else next_url, status_code=status.HTTP_303_SEE_OTHER)

        except auth.InvalidSessionCookieError:
            return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    logging.info(f"No session cookie found!")
    # Ensure that both a "username" and "password" were provided
    if email is None or password is None:
        return RedirectResponse(url=f'/login?error={quote('Missing email or password')}{'' if next_url == 'None' else '&next_url=' + next_url}',
                                status_code=status.HTTP_302_FOUND)

    try:
        user = pyrebase_auth.sign_in_with_email_and_password(email, password)
        logging.info(f"Logged in as {user=}")
        session_cookie = auth.create_session_cookie(user.get("idToken"), expires_in=firebase.COOKIE_TTL)

        response = RedirectResponse(url="/" if next_url == 'None' else next_url, status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(firebase.COOKIE, session_cookie, expires=datetime.now(UTC) + firebase.COOKIE_TTL, secure=request.url.is_secure, httponly=True)

        return response

    except Exception as e:
        logger.error(e, exc_info=True)
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

    if session_cookie := request.cookies.get(firebase.COOKIE):
        logging.info(f"Logged in... {session_cookie=}")
        try:
            decoded_claims = auth.verify_session_cookie(session_cookie, check_revoked=True)
            logging.info(f"Logged out from {decoded_claims=}")
            auth.revoke_refresh_tokens(decoded_claims.get("sub"))
            response.set_cookie(firebase.COOKIE, expires=0, secure=request.url.is_secure, httponly=True)

        except auth.RevokedSessionCookieError | auth.InvalidSessionCookieError as e:
            logging.info(f"Logged out from {e}")
            response.set_cookie(firebase.COOKIE, expires=0, secure=request.url.is_secure, httponly=True)

    else:
        logging.info(f"No session cookie found!")

    response.set_cookie("current_user", expires=0, secure=request.url.is_secure, httponly=True)
    response.set_cookie("current_candidate", expires=0, secure=request.url.is_secure, httponly=True)

    return response
