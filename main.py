from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from app.routes import files, student, professor
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="ClassDrop API", description="API for Class File Sharing.")

# Include routers
app.include_router(files.router)
app.include_router(student.router)
app.include_router(professor.router)

# Mout static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Redirect root to /student
@app.get("/")
async def root():
    return RedirectResponse(url="/student")

