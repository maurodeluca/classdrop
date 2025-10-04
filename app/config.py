import os

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB
UPLOAD_DIR = "uploads"
METADATA_FILE = "metadata.json"
LOCK_FILE = "metadata.json.lock"
DANGEROUS_EXTENSIONS = {".exe", ".bat", ".sh", ".js", ".py", ".php", ".com", ".vbs", ".msi", ".cmd"}

# Ensure upload dir and metadata file exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
if not os.path.exists(METADATA_FILE):
    with open(METADATA_FILE, "w") as f:
        f.write("[]")
