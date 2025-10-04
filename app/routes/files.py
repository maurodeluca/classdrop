from fastapi import APIRouter, UploadFile, HTTPException, status
from fastapi.responses import FileResponse
from app.utils.metadata import read_metadata, write_metadata
from app.config import UPLOAD_DIR, MAX_FILE_SIZE, DANGEROUS_EXTENSIONS
import os
import uuid
from datetime import datetime

router = APIRouter(prefix="/files", tags=["Files"])

# Upload a file
@router.post("/", status_code=status.HTTP_201_CREATED)
async def upload_file(file: UploadFile):
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds {MAX_FILE_SIZE} MB limit."
        )

    # Generate unique file ID
    file_id = str(uuid.uuid4())
    _, ext = os.path.splitext(file.filename)
    filename = f"{file_id}{ext}"
    path = os.path.join(UPLOAD_DIR, filename)

    # Check for dangerous file types
    if ext in DANGEROUS_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{ext}' is not allowed for security reasons."
        )

    # save file
    with open(path, "wb") as f:
        f.write(await file.read())

    # Update metadata
    metadata = read_metadata()
    metadata.append({
        "file_id": file_id,
        "filename": file.filename,
        "upload_timestamp": datetime.now().isoformat(),
        "size_in_bytes": file.size
    })
    write_metadata(metadata)

    return {"file_id": file_id, "detail": "File uploaded successfully!"}

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
