from app.repositories.metadata_repository import MetadataRepository
from app.repositories.file_repository import FileRepository
import app.exceptions as ex

class FileService:
    """Service for handling file operations and metadata management."""

    def __init__(self, file_repo: FileRepository, metadata_repo: MetadataRepository, max_size_mb: float = 20):
        self.max_size = max_size_mb * 1024 * 1024  # Convert MB to bytes
        self.file_repo = file_repo
        self.metadata_repo = metadata_repo

    def save_uploaded_file(self, filename: str, content: bytes) -> str:
        """
        Save uploaded file and update metadata.       
        Returns the file_id as a string.
        """

        # Validate file size
        if self.is_file_size_above_max(len(content)):
            raise ex.FileSizeExceededException(f"File exceeds {self.max_size // (1024 * 1024)} MB limit.")
        
        # Validate file extension
        ext = self.file_repo.get_file_extension(filename)
        if self.is_dangerous_extension(ext):
            raise ex.DangerousFileExtensionException(f"File type '{ext}' is not allowed for security reasons.")
        
        file_id = self.metadata_repo.add_metadata(filename, len(content))
        self.file_repo.write_file(file_id, ext, content)

        return str(file_id)

    def get_all_files_metadata(self) -> list:
        """
        Retrieve all file metadata entries.
        Returns a list of metadata dictionaries.
        """

        return self.metadata_repo.read_metadata()

    def fetch_downloadable_file_by_id(self, file_id: str) -> tuple[str, str]:
        """
        Fetch downloadable file by file_id, raises ValueError if not found.      
        Returns a tuple of (file_path, filename).
        """

        # Check if file_id exists in metadata
        if not (entry := self.metadata_repo.get_metadata_by_id(file_id)):
            raise FileNotFoundError("File not found in metadata")
        
        # Check if file exists on disk
        path = self.file_repo.get_file_path(file_id, entry["filename"])
        if not self.file_repo.file_exists(path):
            raise FileNotFoundError("File not found on disk")
        
        return path, entry["filename"]

    def is_file_size_above_max(self, size: int) -> bool:
        """
        Check if file size exceeds the maximum allowed size.       
        Returns True if size exceeds max_size, else False.
        """

        if size > self.max_size:
            return True
        return False

    def is_dangerous_extension(self, ext: str) -> bool:
        """
        Check if the file extension is considered dangerous.     
        Returns True if extension is dangerous, else False.
        """

        DANGEROUS_EXTENSIONS = {".exe", ".bat", ".cmd", ".sh", ".js", ".msi", ".com", ".scr", ".pif", ".cpl"}
        if ext in DANGEROUS_EXTENSIONS:
            return True
        return False