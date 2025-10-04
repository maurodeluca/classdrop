import os
import json
import uuid
from datetime import datetime
from filelock import FileLock, Timeout
from functools import wraps
from fastapi import UploadFile, HTTPException, status

class FileService:
    def __init__(self, upload_dir="uploads", metadata_file="metadata.json", max_size_mb=20):
        self.upload_dir = upload_dir
        self.metadata_file = metadata_file
        self.max_size = max_size_mb * 1024 * 1024  # convert to bytes
        self.lock_file = f"{metadata_file}.lock"

        os.makedirs(upload_dir, exist_ok=True)
        if not os.path.exists(metadata_file):
            with open(metadata_file, "w") as f:
                f.write("[]")

    @staticmethod
    def handle_file_errors(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Timeout:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Server busy, please try again shortly."
                )
            except FileNotFoundError:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Requested file not found."
                )
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Metadata corrupted. Please contact the administrator."
                )
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Unexpected server error: {str(e)}"
                )
        return wrapper

    def read_metadata(self):
        with FileLock(self.lock_file, timeout=5):
            with open(self.metadata_file, "r") as f:
                return json.load(f)

    def write_metadata(self, data):
        with FileLock(self.lock_file, timeout=5):
            with open(self.metadata_file, "w") as f:
                json.dump(data, f, indent=4)

    async def save_file(self, file: UploadFile):
        if file.spool_max_size > self.max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File exceeds maximum size of {self.max_size} bytes."
            )

        _, ext = os.path.splitext(file.filename)
        file_id = str(uuid.uuid4())
        unique_filename = f"{file_id}{ext}"
        file_path = os.path.join(self.upload_dir, unique_filename)

        with open(file_path, "wb") as f:
            f.write(await file.read())

        metadata = self.read_metadata()
        metadata.append({
            "file_id": file_id,
            "filename": file.filename,
            "upload_timestamp": datetime.now().isoformat(),
            "size_in_bytes": file.spool_max_size
        })
        self.write_metadata(metadata)
        return {"file_id": file_id, "message": "File uploaded successfully!"}
