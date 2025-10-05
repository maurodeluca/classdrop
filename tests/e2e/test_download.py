from fastapi.testclient import TestClient
from app.main import app
from app.services.file_service import FileService
from app.repositories.file_repository import FileRepository
from app.repositories.metadata_repository import MetadataRepository
from app.dependencies import get_file_service  # the one used in Depends()
import uuid
import pytest

client = TestClient(app)

@pytest.mark.e2e
def test_download_file(tmp_path):
    """E2E test: verifies that a file can be downloaded successfully using dependency injection."""

    # --- Arrange ---
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    metadata_file = tmp_path / "metadata.json"
    metadata_file.write_text("[]")

    # Build repositories and service (isolated for this test)
    file_repo = FileRepository(upload_dir=str(upload_dir))
    metadata_repo = MetadataRepository(metadata_file=str(metadata_file))
    test_service = FileService(file_repo=file_repo, metadata_repo=metadata_repo)

    # Inject this service into FastAPI using dependency override
    app.dependency_overrides[get_file_service] = lambda: test_service

    # Create a fake file and metadata entry
    file_id = str(uuid.uuid4())
    filename = "test.txt"
    content = "Hello from ClassDrop!"
    file_path = upload_dir / f"{file_id}.txt"
    file_path.write_text(content)

    metadata_repo.write_metadata([
        {
            "file_id": file_id,
            "filename": filename,
            "upload_timestamp": "2025-10-05T10:00:00",
            "size_in_bytes": len(content),
        }
    ])

    # --- Act ---
    response = client.get(f"/files/{file_id}")

    # --- Assert ---
    assert response.status_code == 200
    assert response.content == content.encode()
    assert "attachment;" in response.headers["content-disposition"]
    assert response.headers["content-disposition"].endswith(f'{filename}"')

    # --- Cleanup ---
    app.dependency_overrides.clear()
