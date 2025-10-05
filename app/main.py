from fastapi import FastAPI, status, Request
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from app.routes import files, student, professor
from app.middleware import catch_exceptions_middleware  # Import the middleware
import app.exceptions as ex

app = FastAPI(title="ClassDrop API", description="API for Class File Sharing.")

# Include routers
app.include_router(files.router)
app.include_router(student.router)
app.include_router(professor.router)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Redirect root to /student
@app.get("/")
async def root():
    """Redirect root to /student page."""

    return RedirectResponse(url="/student")

# Register middleware
app.middleware('http')(catch_exceptions_middleware)

# Exception handlers
@app.exception_handler(ex.FileSizeExceededException)
async def file_size_exceeded_exception_handler(request: Request, exc: ex.FileSizeExceededException):
    return JSONResponse(
        status_code=status.HTTP_413_CONTENT_TOO_LARGE,
        content={"detail": exc.message},
    )

@app.exception_handler(FileNotFoundError)
async def file_not_found_exception_handler(request: Request, exc: FileNotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )

@app.exception_handler(ex.DangerousFileExtensionException)
async def dangerous_file_extension_exception_handler(request: Request, exc: ex.DangerousFileExtensionException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.message},
    )

@app.exception_handler(ex.InvalidFilenameException)
async def validation_exception_handler(request: Request, exc: ex.InvalidFilenameException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )