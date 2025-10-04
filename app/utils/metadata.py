import json
from filelock import FileLock, Timeout
from fastapi import HTTPException, status
from functools import wraps
from app.config import METADATA_FILE

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
def read_metadata() -> list:
    """Read metadata from the JSON file with file locking."""

    with FileLock(f"{METADATA_FILE}.lock", timeout=5):
        with open(METADATA_FILE, "r") as f:
            return json.load(f)

@handle_file_errors
def write_metadata(metadata: list):
    """Write metadata to the JSON file with file locking."""

    with FileLock(f"{METADATA_FILE}.lock", timeout=5):
        with open(METADATA_FILE, "w") as f:         
            json.dump(metadata, f, indent=4)

def update_metadata(new_entry: dict):
    """Add a new entry to the metadata file."""

    metadata = read_metadata()
    metadata.append(new_entry)
    write_metadata(metadata)