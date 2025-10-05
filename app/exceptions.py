import json
from filelock import Timeout
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

class FileSizeExceededException(Exception):
    """Exception raised when a file exceeds the maximum allowed size."""
    def __init__(self, message: str = "File size exceeds the allowed limit."):
        self.message = message
        super().__init__(self.message)


class DangerousFileExtensionException(Exception):
    """Exception raised when a file has a dangerous extension."""
    def __init__(self, message: str = "File type is not allowed for security reasons."):
        self.message = message
        super().__init__(self.message)
