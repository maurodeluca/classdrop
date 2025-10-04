from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.config import MAX_FILE_SIZE

router = APIRouter(prefix="/professor", tags=["Professor"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def professor_page(request: Request):
    return templates.TemplateResponse(
        "upload_form.html",
        {
            "request": request,
            "max_file_size_mb": MAX_FILE_SIZE // (1024*1024)
        }
    )
