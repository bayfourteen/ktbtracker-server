import logging

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse

from ktbtracker_server.config import get_locale

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def base_index(
        request: Request,
        # -- Dependencies --
        locale: str = Depends(get_locale()),
) ->RedirectResponse:
    return RedirectResponse(request.url_for("index", locale=locale), status_code=status.HTTP_303_SEE_OTHER)
