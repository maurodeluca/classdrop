import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.file_service import FileService
from app.repositories.file_repository import FileRepository
from app.repositories.metadata_repository import MetadataRepository
from app.dependencies import get_file_service
import uuid, json

@pytest.mark.e2e
def test_upload_file_success(tmp_path):
    # Setup: temporary isolated environment
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    metadata_file = tmp_path / "metadata.json"
    metadata_file.write_text("[]")

    # Create isolated repositories + service
    file_repo = FileRepository(upload_dir=upload_dir)
    metadata_repo = MetadataRepository(metadata_file=metadata_file)
    test_service = FileService(file_repo=file_repo, metadata_repo=metadata_repo)

    # Override dependency
    app.dependency_overrides[get_file_service] = lambda: test_service

    # Create test client
    client = TestClient(app)

    # Create fake file
    test_file_path = tmp_path / "test.txt"
    test_file_content = "This is a test file."
    test_file_path.write_text(test_file_content)

    # Act
    with test_file_path.open("rb") as f:
        response = client.post(
            "/files/",
            files={"file": ("test.txt", f, "text/plain")}
        )

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert "file_id" in data
    assert data["message"] == "File uploaded successfully!"

    # Validate file_id is valid UUID
    try:
        uuid_obj = uuid.UUID(data["file_id"], version=4)
        assert str(uuid_obj) == data["file_id"]
    except ValueError:
        pytest.fail("file_id is not a valid UUID")

    # Verify the file and metadata exist physically
    saved_file = upload_dir / f"{data['file_id']}.txt"
    assert saved_file.exists()
    saved_metadata = json.loads(metadata_file.read_text())
    assert len(saved_metadata) == 1
    assert saved_metadata[0]["filename"] == "test.txt"

    # Clean up overrides
    app.dependency_overrides.clear()
