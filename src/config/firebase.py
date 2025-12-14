import logging

from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth

logger = logging.getLogger(__name__)

bearer_scheme = HTTPBearer(auto_error=False)


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
