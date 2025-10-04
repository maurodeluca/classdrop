from fastapi import APIRouter, UploadFile, HTTPException
from fastapi.responses import FileResponse
from app.utils.file_ops import save_uploaded_file
from app.utils.metadata import read_metadata
from app.config import UPLOAD_DIR
import os
import uuid

router = APIRouter(prefix="/files", tags=["Files"])

# Upload a file
@router.post("/", status_code=201)
async def upload_file(file: UploadFile):
    return await save_uploaded_file(file)

# List all files
@router.get("/")
async def list_files():
    return {"files": read_metadata()}

# Download a file by file_id
@router.get("/{file_id}")
async def download_file(file_id: uuid.UUID):
    metadata = read_metadata()

    # Check if file_id exists in metadata
    entry = next((m for m in metadata if m["file_id"] == str(file_id)), None)
    if not entry:
        raise HTTPException(status_code=404, detail="File not found in metadata")

    # Check if file exists on disk
    _, ext = os.path.splitext(entry["filename"])
    path = os.path.join(UPLOAD_DIR, f"{file_id}{ext}")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    return FileResponse(path=path, filename=entry["filename"], media_type="application/octet-stream")
