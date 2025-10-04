from fastapi.testclient import TestClient
from main import app
import uuid
import json
import pytest

client = TestClient(app)

@pytest.mark.e2e
def test_list_files_success(tmp_path, monkeypatch):
    # Setup
    metadata_file = tmp_path / "metadata.json"
    metadata_file.write_text("[]")

    # Mock environment
    monkeypatch.setattr("app.utils.metadata.METADATA_FILE", str(metadata_file))

    # Create fake file + metadata
    file_id = str(uuid.uuid4())
    filename = "test.txt"
    test_file = {
        "file_id": file_id,
        "filename": filename,
        "upload_timestamp": "2025-10-04T12:00:00",
        "size_in_bytes": 11
    }
    metadata_file.write_text(json.dumps([test_file]))

    # Act
    response = client.get(f"/files/")
    breakpoint()

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "files" in data
    file = data["files"][0]
    assert file["file_id"] == test_file["file_id"]
    assert file["filename"] == test_file["filename"]
    assert file["upload_timestamp"] == test_file["upload_timestamp"]
    assert file["size_in_bytes"] == test_file["size_in_bytes"]