import os

class FileRepository:
    """Repository for managing file storage and retrieval."""

    UPLOAD_DIR: str = "uploads"

    def __init__(self, upload_dir: str = None):
        if upload_dir:
            self.UPLOAD_DIR = upload_dir

        # Ensure upload dir and metadata file exist
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)

    def write_file(self, file_id: str, ext: str, content: bytes):
        """Write file content to the upload directory."""

        path = os.path.join(self.UPLOAD_DIR, f"{file_id}{ext}")
        with open(path, "wb") as f:
            f.write(content)

    def file_exists(self, path: str) -> bool:
        """
        Check if a file exists at the given path.
        Returns True if the file exists, False otherwise.
        """

        return os.path.exists(path)
    
    def get_file_path(self, file_id: str, filename: str) -> str:
        """
        Get the full file path for a given file ID and original filename.
        Returns the path where the file is stored.
        """
        
        _, ext = os.path.splitext(filename)
        return os.path.join(self.UPLOAD_DIR, f"{file_id}{ext}")
    
    def get_file_extension(self, filename: str) -> str:
        """
        Get the file extension from the filename.
        Returns the file extension including the dot (e.g., '.txt').
        """
        
        _, ext = os.path.splitext(filename)
        return ext