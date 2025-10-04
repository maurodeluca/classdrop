from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.utils.metadata import read_metadata
from datetime import datetime

router = APIRouter(prefix="/student", tags=["Students"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def student_page(request: Request):
    """Render the student page with list of uploaded files."""
    
    files = read_metadata()
    
    # Format timestamps for display
    for i in range(len(files)):
        dt = datetime.fromisoformat(files[i]["upload_timestamp"])
        files[i]["upload_timestamp"] = dt.strftime("%d %b %Y %H:%M")

    return templates.TemplateResponse(
        "student_files.html",
        {
            "request": request,
              "files": files
        }
    )
