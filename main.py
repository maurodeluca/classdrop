from fastapi import FastAPI, UploadFile, status, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
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
    file_id = str(uuid.uuid4())
    unique_filename = f"{file_id}.{ext}" 
    file_location = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Save file on disk
    with open(file_location, "wb") as f:
        f.write(await file.read())

    # Save metadata
    metadata = read_metadata()
    metadata.append({
        "file_id": file_id,
        "filename": file.filename,
        "upload_timestamp": datetime.now().isoformat(),
        "size_in_bytes": file.size
    })
    write_metadata(metadata)

    return {"file_id": file_id, "message": "File uploaded successfully!"}

# List all uploaded files
@app.get("/files/")
async def list_files():
    metadata = read_metadata()
    return {"files": metadata}

# Download endpoint
@app.get("/files/{file_id}")
async def download_file(file_id: uuid.UUID):
    metadata = read_metadata()
    file_entry = next((item for item in metadata if item["file_id"] == str(file_id)), None)
    if not file_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found.")
    
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.{os.path.splitext(file_entry['filename'])[1]}")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found on server.")
    
    return FileResponse(path=file_path, filename=file_entry["filename"], media_type='application/octet-stream')
    

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