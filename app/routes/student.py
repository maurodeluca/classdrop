from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/student", tags=["Students"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def student_page(request: Request):
    """Render the student page."""
    
    return templates.TemplateResponse(
        "student_files.html",
        {"request": request}
    )
