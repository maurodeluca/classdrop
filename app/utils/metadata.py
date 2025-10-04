import json
from filelock import FileLock, Timeout
from fastapi import HTTPException, status
from functools import wraps

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
def read_metadata():
    """Read metadata from the JSON file with file locking."""

    with FileLock("metadata.json.lock", timeout=5):
        with open("metadata.json", "r") as f:
            return json.load(f)

@handle_file_errors
def write_metadata(data):
    """Write metadata to the JSON file with file locking."""
    
    with FileLock("metadata.json.lock", timeout=5):
        with open("metadata.json", "w") as f:
            json.dump(data, f, indent=4)
