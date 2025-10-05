from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.services.file_service import FileService
from app.dependencies import get_file_service

router = APIRouter(prefix="/professor", tags=["Professor"])
templates = Jinja2Templates(directory="app/templates")

# Render professor upload page
@router.get("/", response_class=HTMLResponse)
async def professor_page(request: Request, fs: FileService = Depends(get_file_service)):
    """Render the professor upload page with max file size info."""
    
    return templates.TemplateResponse(
        "upload_form.html",
        {
            "request": request,
            "max_file_size_mb": fs.max_size // (1024*1024)
        }
    )
