from fastapi import APIRouter, Request, status, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from config.jinja2 import get_templates
from config.observability import AsyncIteratorWrapper, debug
from services.cycles import CyclesService, get_cycles_service

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
@debug
async def admin_index(
        request: Request,
        # -- Dependencies --
        templates: Jinja2Templates = Depends(get_templates),
        cycles_service: CyclesService = Depends(get_cycles_service)
):
    cycles = cycles_service.find_all()
    return templates.TemplateResponse("admin/index.html", {"request": request, "cycles": cycles})


@router.get("/cycles", response_class=HTMLResponse)
@debug
async def admin_cycles(
        request: Request,
        # -- Dependencies --
        templates: Jinja2Templates = Depends(get_templates),
        cycles_service: CyclesService = Depends(get_cycles_service)
):
    cycles = cycles_service.find_all()
    return templates.TemplateResponse("admin/cycles/index.html", {"request": request, "cycles": cycles})
