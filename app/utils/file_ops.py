import os
import uuid
from datetime import datetime
from fastapi import UploadFile, HTTPException, status
from app.config import UPLOAD_DIR, MAX_FILE_SIZE
from app.utils.metadata import read_metadata, write_metadata

async def save_uploaded_file(file: UploadFile):
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File exceeds 20 MB limit."
        )

    # Generate unique file ID
    file_id = str(uuid.uuid4())
    _, ext = os.path.splitext(file.filename)
    filename = f"{file_id}{ext}"
    path = os.path.join(UPLOAD_DIR, filename)

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
