import os
import json
import uuid
from datetime import datetime
from filelock import FileLock
from app.exceptions import handle_file_errors

class MetadataRepository:
    """Repository for managing file metadata in the database."""
    
    METADATA_FILE: str = "metadata.json"
    
    def __init__(self, metadata_file: str = None):
        if metadata_file:
            self.METADATA_FILE = metadata_file

        # Ensure metadata file exists
        if not os.path.exists(self.METADATA_FILE):
            with open(self.METADATA_FILE, "w") as f:
                json.dump([], f)

    @handle_file_errors
    def read_metadata(self) -> list:
        """
        Read metadata from the JSON file with file locking.
        Returns a list of metadata entries.
        """

        with FileLock(f"{self.METADATA_FILE}.lock", timeout=5):
            with open(self.METADATA_FILE, "r") as f:
                return json.load(f)

    @handle_file_errors
    def write_metadata(self, metadata: list):
        """Write metadata to the JSON file with file locking."""

        with FileLock(f"{self.METADATA_FILE}.lock", timeout=5):
            with open(self.METADATA_FILE, "w") as f:
                json.dump(metadata, f, indent=4)

    def add_metadata(self, filename: str, file_size: int) -> uuid.UUID:
        """
        Add a new entry to the metadata file.
        Returns the generated file_id.
        """
        file_id = uuid.uuid4()
        new_entry = {
            "file_id": str(file_id),
            "filename": filename,
            "upload_timestamp": datetime.now().isoformat(),
            "size_in_bytes": file_size
        }
        metadata = self.read_metadata()
        metadata.append(new_entry)
        self.write_metadata(metadata)

        return file_id

    
    def get_metadata_by_id(self, file_id: str) -> dict:
        """
        Retrieve metadata entry by file_id.
        Returns the metadata dictionary if found, else None.
        """
        metadata = self.read_metadata()
        for entry in metadata:
            if entry["file_id"] == str(file_id):
                return entry
        return None