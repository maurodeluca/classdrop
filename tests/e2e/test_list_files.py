import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.file_service import FileService
from app.repositories.file_repository import FileRepository
from app.repositories.metadata_repository import MetadataRepository
from app.dependencies import get_file_service
import uuid, json

@pytest.mark.e2e
def test_list_files_success(tmp_path):
    """E2E test: verifies listing files returns correct metadata."""

    # --- Arrange: setup temporary repos + service ---
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    metadata_file = tmp_path / "metadata.json"
    metadata_file.write_text("[]")

    # Create repositories and service
    file_repo = FileRepository(upload_dir=upload_dir)
    metadata_repo = MetadataRepository(metadata_file=metadata_file)
    test_service = FileService(file_repo=file_repo, metadata_repo=metadata_repo)

    # Override FastAPI dependency
    app.dependency_overrides[get_file_service] = lambda: test_service

    client = TestClient(app)

    # Create fake metadata
    file_id = str(uuid.uuid4())
    filename = "test.txt"
    test_file = {
        "file_id": file_id,
        "filename": filename,
        "upload_timestamp": "2025-10-04T12:00:00",
        "size_in_bytes": 11
    }
    metadata_repo.write_metadata([test_file])

    # --- Act ---
    response = client.get("/files/")

    # --- Assert ---
    assert response.status_code == 200
    data = response.json()
    assert "files" in data
    assert len(data["files"]) == 1

    file = data["files"][0]
    assert file["file_id"] == test_file["file_id"]
    assert file["filename"] == test_file["filename"]
    assert file["upload_timestamp"] == test_file["upload_timestamp"]
    assert file["size_in_bytes"] == test_file["size_in_bytes"]

    # Clean up overrides
    app.dependency_overrides.clear()
