from fastapi.testclient import TestClient
from main import app
import pytest
import uuid

client = TestClient(app)

@pytest.mark.e2e
def test_upload_file_success(tmp_path):
    # Setup
    test_file_path = tmp_path / "test.txt"
    test_file_content = "This is a test file."
    test_file_path.write_text(test_file_content)

    # Act
    with test_file_path.open("rb") as file:
        response = client.post(
            "/files/",
            files={"file": ("test.txt", file, "text/plain")}
        )

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert "file_id" in data
    assert data["message"] == "File uploaded successfully!"

    # Validate file_id is a valid UUID
    try:
        uuid_obj = uuid.UUID(data["file_id"], version=4)
        assert str(uuid_obj) == data["file_id"]  # Ensure it's a properly formatted UUID
    except ValueError:
        pytest.fail("file_id is not a valid UUID")