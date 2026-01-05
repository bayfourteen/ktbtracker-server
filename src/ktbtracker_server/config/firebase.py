import json
from typing import Annotated

import httpx
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin.auth import verify_id_token
from sqlalchemy.testing.pickleable import User

from ktbtracker_server.config.i18n import get_locale
from ktbtracker_server.config.observability import debug

# use of a simple bearer scheme as auth is handled by firebase and not fastapi
# we set auto_error to False because fastapi incorrectly returns a 403 instead
# of a 401
# see: https://github.com/tiangolo/fastapi/pull/2120
bearer_scheme = HTTPBearer(auto_error=False)

...
def get_firebase_claims(
    token: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> dict | None:
    """Uses bearer token to identify firebase user id
    Args:
        token : the bearer token. Can be None as we set auto_error to False
    Returns:
        dict: the firebase user on success
    Raises:
        HTTPException 401 if user does not exist or token is invalid
    """
    try:
        if not token:
            # raise and catch to return 401, only needed because fastapi returns 403
            # by default instead of 401 so we set auto_error to False
            raise ValueError("No token")
        user = verify_id_token(token.credentials)
        return user
    # lots of possible exceptions, see firebase_admin.auth,
    # but most of the time it is a credentials issue
    except Exception:
        # we also set the header
        # see https://fastapi.tiangolo.com/tutorial/security/simple-oauth2/
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not logged in or Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
import logging
from datetime import timedelta
from typing import Any

from fastapi import HTTPException, Request, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth

logger = logging.getLogger(__name__)

bearer_scheme = HTTPBearer(auto_error=False)

FIREBASE_CHECK_REVOKED = True
FIREBASE_ACCOUNTS_API = "https://identitytoolkit.googleapis.com/v1/accounts"
FIREBASE_CONFIG = {
    "apiKey": "AIzaSyAJFZzjFujriTXa9Fzt0mKBMWzFz23Q8LQ",
    "authDomain": "ktbtracker.firebaseapp.com",
    "projectId": "ktbtracker",
    "storageBucket": "ktbtracker.firebasestorage.app",
    "messagingSenderId": "89203641216",
    "appId": "1:389203641216:web:412d016ea02a6b3cfaf765",
    "measurementId": "G-8P68YP45BK",
    "databaseURL": "https://kingtiger.firebaseio.com",
}

COOKIE = "session"
COOKIE_TTL = timedelta(hours=5)
HTTPONLY = True
SECURE = False


async def get_current_user(token: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    """Verifies the Firebase ID token and returns the user's UID."""
    if not token:
        logger.error(f"Missing Authorization header!")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        # Verify the token using Firebase Admin SDK
        decoded_token = auth.verify_id_token(token.credentials)
        logger.info(f"Successfully verified token: {decoded_token}")
        uid = decoded_token['uid']
        return uid
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def change_email(id_token: str, email: str):
    """Changes the email address of a user.
    Args:
    """
    request_url = "%s:update?key=%s" % (FIREBASE_ACCOUNTS_API, FIREBASE_CONFIG.get("apiKey"))
    headers = {"Content-Type": "application/json; charset=UTF-8", "X-Firebase-Locale": await get_locale()}
    data = {"idToken": id_token, "email": email, "returnSecureToken": True}

    try:
        response = httpx.post(request_url, headers=headers, json=data)
        return response.json()

    except httpx.HTTPStatusError as e:
        raise e


async def change_password(id_token: str, password: str):
    """Changes the email address of a user.
    Args:
    """
    request_url = "%s:update?key=%s" % (FIREBASE_ACCOUNTS_API, FIREBASE_CONFIG.get("apiKey"))
    headers = {"Content-Type": "application/json; charset=UTF-8", "X-Firebase-Locale": await get_locale()}
    data = {"idToken": id_token, "password": password, "returnSecureToken": True}

    try:
        response = httpx.post(request_url, headers=headers, json=data)
        return response.json()

    except httpx.HTTPStatusError as e:
        raise e


async def confirm_password_reset(email: str, password: str, oob_code: str) -> dict[str, Any]:
    request_url = "%s:resetPassword?key=%s" % (FIREBASE_ACCOUNTS_API, FIREBASE_CONFIG.get("apiKey"))
    headers = {"Content-Type": "application/json; charset=UTF-8", "X-Firebase-Locale": await get_locale()}
    data = {"oobCode": oob_code, "newPassword": password}

    try:
        response = httpx.post(request_url, headers=headers, json=data)
        return response.json()

    except httpx.HTTPStatusError as e:
        raise e


async def send_password_reset_email(email: str) -> dict[str, Any]:
    request_url = "%s:sendOobCode?key=%s" % (FIREBASE_ACCOUNTS_API, FIREBASE_CONFIG.get("apiKey"))
    headers = {"Content-Type": "application/json; charset=UTF-8", "X-Firebase-Locale": await get_locale()}
    data = {"requestType": "PASSWORD_RESET", "email": email}

    try:
        response = httpx.post(request_url, headers=headers, json=data)
        return response.json()

    except httpx.HTTPStatusError as e:
        raise e


@debug
async def signin_with_email_password(request: Request, email: str, password: str) -> dict[str, Any]:
    request_url = "%s:signInWithPassword?key=%s" % (FIREBASE_ACCOUNTS_API, FIREBASE_CONFIG.get("apiKey"))
    headers = {"Content-Type": "application/json; charset=UTF-8", "X-Firebase-Locale": await get_locale(request)}
    data = {"email": email, "password": password, "returnSecureToken": True}

    try:
        response = httpx.post(request_url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()

    except httpx.HTTPStatusError as e:
        raise e


async def signup_with_email_password(email: str, password: str) -> dict[str, Any]:
    request_url = "%s:signUp?key=%s" % (FIREBASE_ACCOUNTS_API, FIREBASE_CONFIG.get("apiKey"))
    headers = {"Content-Type": "application/json; charset=UTF-8", "X-Firebase-Locale": await get_locale()}
    data = {"email": email, "password": password, "returnSecureToken": True}

    try:
        response = httpx.post(request_url, headers=headers, json=data)
        return response.json()

    except httpx.HTTPStatusError as e:
        raise e


async def update_user_profile(id_token: str, display_name: str | None, photo_url: str | None) -> dict[str, Any]:
    request_url = "%s:update?key=%s" % (FIREBASE_ACCOUNTS_API, FIREBASE_CONFIG.get("apiKey"))
    headers = {"Content-Type": "application/json; charset=UTF-8", "X-Firebase-Locale": await get_locale()}
    update_display_name = {"displayName": display_name} if display_name else {}
    update_photo_url = {"photoUrl": photo_url} if photo_url else {}
    delete_attributes = {"deleteAttribute": ["DISPLAY_NAME"] if display_name else [] + ["PHOTO_URL"] if photo_url else []}

    data = dict({"idToken": id_token}, **update_display_name, **update_photo_url, **delete_attributes)

    try:
        response = httpx.post(request_url, headers=headers, json=data)
        return response.json()

    except httpx.HTTPStatusError as e:
        raise e


async def verify_reset_password_code(email: str, oob_code: str) -> dict[str, Any]:
    request_url = "%s:resetPassword?key=%s" % (FIREBASE_ACCOUNTS_API, FIREBASE_CONFIG.get("apiKey"))
    headers = {"Content-Type": "application/json; charset=UTF-8"}
    data = {"oobCode": oob_code}

    try:
        response = httpx.post(request_url, headers=headers, json=data)
        return response.json()

    except httpx.HTTPStatusError as e:
        raise e


async def get_current_session(request: Request) -> dict[str, Any] | None:
    if session_cookie := request.cookies.get("SESSION"):
        try:
            return auth.verify_session_cookie(session_cookie, check_revoked=True)

        except auth.ExpiredIdTokenError:
            return None

    return None
