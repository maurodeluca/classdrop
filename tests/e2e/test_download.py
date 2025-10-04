from fastapi.testclient import TestClient
from main import app
import pytest
import uuid
import json

client = TestClient(app)

@pytest.mark.e2e
def test_download_file_success(tmp_path, monkeypatch):
    # Setup
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    metadata_file = tmp_path / "metadata.json"
    metadata_file.write_text("[]")

    # Mock environment
    monkeypatch.setattr("app.utils.metadata.METADATA_FILE", str(metadata_file))
    monkeypatch.setattr("app.routes.files.UPLOAD_DIR", str(upload_dir))

    # Create a test file and metadata entry
    file_id = str(uuid.uuid4())
    original_filename = "test_file.txt"
    test_file_path = upload_dir / f"{file_id}.txt"
    test_file_content = "This is a test file for download."
    test_file_path.write_text(test_file_content)

    metadata_entry = {
        "file_id": file_id,
        "filename": original_filename,
        "upload_timestamp": "2025-10-05T12:00:00",
        "size_in_bytes": len(test_file_content),
    }
    metadata_file.write_text(json.dumps([metadata_entry]))

    # Act
    response = client.get(f"/files/{file_id}")

    # Assert
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/octet-stream"
    assert response.headers["content-disposition"] == f'attachment; filename="{original_filename}"'
    assert response.headers["content-length"] == str(len(test_file_content))