import json
from filelock import FileLock
from app.config import METADATA_FILE, LOCK_FILE

def read_metadata():
    with FileLock(LOCK_FILE, timeout=5):
        with open(METADATA_FILE, "r") as f:
            return json.load(f)
    
def write_metadata(data):
    with FileLock(LOCK_FILE, timeout=5):
        with open(METADATA_FILE, "w") as f:
            json.dump(data, f, indent=4)
