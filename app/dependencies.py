from app.services.file_service import FileService
from app.repositories.file_repository import FileRepository
from app.repositories.metadata_repository import MetadataRepository

# Dependency factory for FileService
def get_file_service() -> FileService:
    """
    Creates and returns a FileService with its repositories wired up.
    FastAPI uses this with Depends(), and tests can override it easily.
    """
    file_repo = FileRepository()
    metadata_repo = MetadataRepository()
    return FileService(file_repo=file_repo, metadata_repo=metadata_repo)
