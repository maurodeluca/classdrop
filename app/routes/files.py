from fastapi import APIRouter, UploadFile, HTTPException, status, Depends
from fastapi.responses import FileResponse
from app.services.file_service import FileService
from app.dependencies import get_file_service
from uuid import UUID

router = APIRouter(prefix="/files", tags=["Files"])

# Upload a file
@router.post("/", status_code=status.HTTP_201_CREATED)
async def upload_file(file: UploadFile, fs: FileService = Depends(get_file_service)):
    """Upload a file with metadata handling and file locking."""

    content = await file.read()
    file_id = fs.save_uploaded_file(filename=file.filename, content=content)
    return {"file_id": file_id, "message": "File uploaded successfully!"}


# List all files
@router.get("/")
async def list_files(fs: FileService = Depends(get_file_service)):
    """List all uploaded files with metadata."""

    return {"files": fs.get_all_files_metadata()}

# Download a file by file_id
@router.get("/{file_id}")
async def download_file(file_id: UUID, fs: FileService = Depends(get_file_service)):
    """Download a file by its unique file_id."""

    try:
        path, filename = fs.fetch_downloadable_file_by_id(str(file_id))
        return FileResponse(path, filename=filename, media_type="application/octet-stream")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    
