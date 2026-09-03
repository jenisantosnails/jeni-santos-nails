from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates


router = APIRouter(
    tags=["Area Publica"],
)


BASE_DIR = Path(__file__).resolve().parent.parent

templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)


@router.get("/agendamento")
def booking_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="booking.html",
    )
