import json
from filelock import FileLock, Timeout
from fastapi import HTTPException, status
from functools import wraps
from app.models import FileMetadata

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

@handle_file_errors
def read_metadata() -> list[FileMetadata]:
    """Read metadata from the JSON file with file locking."""

    with FileLock("metadata.json.lock", timeout=5):
        with open("metadata.json", "r") as f:
            raw = json.load(f)
    return [FileMetadata(**item) for item in raw]

@handle_file_errors
def write_metadata(metadata: list[FileMetadata]):
    """Write metadata to the JSON file with file locking."""

    d = [json.loads(m.model_dump_json()) for m in metadata]

    with FileLock("metadata.json.lock", timeout=5):
        with open("metadata.json", "w") as f:         
            json.dump(d, f, indent=4)

def update_metadata(new_entry: FileMetadata):
    """Add a new entry to the metadata file."""

    metadata = read_metadata()
    metadata.append(new_entry)
    write_metadata(metadata)