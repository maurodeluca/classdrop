import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.file_service import FileService
from app.repositories.file_repository import FileRepository
from app.repositories.metadata_repository import MetadataRepository
from app.dependencies import get_file_service
import uuid, json

@pytest.mark.e2e
def test_upload_file_succeeds(tmp_path):
    """E2E test: verifies that a file can be uploaded successfully using dependency injection."""

    # Setup
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

    # Clean up
    app.dependency_overrides.clear()

@pytest.mark.e2e
def test_upload_file_with_bad_extension(tmp_path):
    """E2E test: verifies that a file with a bad extension is rejected."""

    # Setup
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

    # Create fake file with a bad extension
    test_file_path = tmp_path / "test.exe"
    test_file_content = "This is a test file with a bad extension."
    test_file_path.write_text(test_file_content)

    # Act
    with test_file_path.open("rb") as f:
        response = client.post(
            "/files/",
            files={"file": ("test.exe", f, "application/octet-stream")}
        )

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "File type '.exe' is not allowed for security reasons."

    # Clean up
    app.dependency_overrides.clear()

@pytest.mark.e2e
def test_upload_file_too_large(tmp_path):
    """E2E test: verifies that a file exceeding the maximum size is rejected."""

    # Setup
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    metadata_file = tmp_path / "metadata.json"
    metadata_file.write_text("[]")

    # Create isolated repositories + service
    file_repo = FileRepository(upload_dir=upload_dir)
    metadata_repo = MetadataRepository(metadata_file=metadata_file)
    test_service = FileService(file_repo=file_repo, metadata_repo=metadata_repo, max_size_mb=1)  # Set max size to 1 MB

    # Override dependency
    app.dependency_overrides[get_file_service] = lambda: test_service

    # Create test client
    client = TestClient(app)

    # Create fake file that exceeds the size limit
    test_file_path = tmp_path / "large_file.txt"
    test_file_content = "A" * (2 * 1024 * 1024)  # 2 MB file
    test_file_path.write_text(test_file_content)

    # Act
    with test_file_path.open("rb") as f:
        response = client.post(
            "/files/",
            files={"file": ("large_file.txt", f, "text/plain")}
        )

    # Assert
    assert response.status_code == 413
    data = response.json()
    assert data["detail"] == "File exceeds 1 MB limit."

    # Clean up
    app.dependency_overrides.clear()

@pytest.mark.e2e
def test_upload_file_with_bad_filename(tmp_path):
    """E2E test: verifies that a file with a bad filename is rejected."""

    # Setup
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

    # Create fake file with a bad filename
    test_file_path = tmp_path / "test.txt"  # Invalid filename on most systems
    test_file_content = "This is a test file with a bad filename."
    test_file_path.write_text(test_file_content)

    # Act
    with test_file_path.open("rb") as f:
        response = client.post(
            "/files/",
            files={"file": ("test<>.txt", f, "text/plain")}
        )

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Filename contains invalid characters."

    # Clean up
    app.dependency_overrides.clear()

