import os

class FileRepository:
    UPLOAD_DIR: str = "uploads"

    def __init__(self, upload_dir: str = None):
        if upload_dir:
            self.UPLOAD_DIR = upload_dir

        # Ensure upload dir and metadata file exist
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)

    def write_file(self, file_id: str, ext: str, content: bytes):
        path = os.path.join(self.UPLOAD_DIR, f"{file_id}{ext}")
        with open(path, "wb") as f:
            f.write(content)

    def file_exists(self, path: str) -> bool:
        return os.path.exists(path)
    
    def get_file_path(self, file_id: str, filename: str) -> str:
        _, ext = os.path.splitext(filename)
        return os.path.join(self.UPLOAD_DIR, f"{file_id}{ext}")
    
    def get_file_extension(self, filename: str) -> str:
        _, ext = os.path.splitext(filename)
        return ext