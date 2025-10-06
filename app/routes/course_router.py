from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/course", tags=["Course"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def course_page(request: Request):
    """Render the course page."""
    
    return templates.TemplateResponse(
        "course_page.html",
        {"request": request}
    )
