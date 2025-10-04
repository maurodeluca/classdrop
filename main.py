from fastapi import FastAPI, UploadFile, status, HTTPException
from fastapi.responses import HTMLResponse
import os
import uuid
import json
from datetime import datetime

app = FastAPI(debug=True, 
              title="ClassDrop API",
              description="API for Class File Sharing.")

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB
UPLOAD_DIR = "uploads"
METADATA_FILE = os.path.join(UPLOAD_DIR, "metadata.json")

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize metadata file if it doesn't exist
if not os.path.exists(METADATA_FILE):
    with open(METADATA_FILE, "w") as f:
        f.write("[]")

# Helper to read metadata
def read_metadata():
    with open(METADATA_FILE, "r") as f:
        return json.load(f)

# Helper to write metadata
def write_metadata(data):
    with open(METADATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Upload endpoint
@app.post("/files/", status_code=status.HTTP_201_CREATED)
async def upload_file(file: UploadFile):
    if file.size > MAX_FILE_SIZE:  # 20 MB limit
        raise HTTPException(status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                            detail="File size exceeds 20 MB limit.")
    
    # Generate unique filename to avoid collisions
    _, ext = os.path.splitext(file.filename)
    file_id = uuid.uuid4().hex
    unique_filename = f"{file_id}.{ext}" 
    file_location = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Save file on disk
    with open(file_location, "wb") as f:
        f.write(await file.read())

    # Save metadata
    metadata = read_metadata()
    metadata.append({
        "file_id": file_id,
        "filename": unique_filename,
        "upload_timestamp": datetime.now().isoformat(),
        "size_in_bytes": file.size
    })
    write_metadata(metadata)

    return {"file_id": file_id, "message": "File uploaded successfully!"}

# TODO: Implement file download logic
# @app.get("/files/{id}")
# async def download_file():
#     return {"message": "File downloaded successfully!"}

# TODO: Implement file listing logic
# @app.get("/files/")
# async def list_files():
#     return {"files": ["file1.txt", "file2.txt", "file3.txt"]}

# Root endpoint with HTML form
@app.get("/")
async def root():
    content = """    
<!DOCTYPE html>
<html>
<head>
    <title>ClassDrop File Upload</title>
</head>
<body>
    <h1>ClassDrop File Upload</h1>
    <p>Welcome! Use this form to upload a single resource file for your class. Only one file can be uploaded at a time.</p>

    <form action="/files/" enctype="multipart/form-data" method="post">
        <input name="file" type="file">
        <input type="submit" value="Upload">
    </form>
</body>
</html>
    """
    return HTMLResponse(content=content)