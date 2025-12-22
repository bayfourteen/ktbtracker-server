import logging
from datetime import timedelta
from typing import Any

from fastapi import HTTPException, Request, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth

from config.observability import debug

logger = logging.getLogger(__name__)

bearer_scheme = HTTPBearer(auto_error=False)

FIREBASE_CHECK_REVOKED = True
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

FIREBASE_COOKIE = "SESSION"
FIREBASE_COOKIE_TTL = timedelta(hours=5)
FIREBASE_HTTPONLY = True
FIREBASE_SECURE = False


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


async def get_current_session(request: Request) -> dict[str, Any] | None:
    if session_cookie := request.cookies.get("SESSION"):
        try:
            return auth.verify_session_cookie(session_cookie, check_revoked=True)

        except auth.ExpiredIdTokenError:
            return None

    return None
