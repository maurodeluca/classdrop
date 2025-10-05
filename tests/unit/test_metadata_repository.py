import json
import uuid
from datetime import datetime
import pytest
from app.repositories.metadata_repository import MetadataRepository

@pytest.mark.unit
def test_initializes_metadata_file(tmp_path):
    """Ensures metadata.json is created on initialization if missing."""
    metadata_file = tmp_path / "metadata.json"

    # Act
    repo = MetadataRepository(metadata_file=str(metadata_file))

    # Assert
    assert metadata_file.exists()
    assert repo.METADATA_FILE == str(metadata_file)

    # Should contain an empty list initially
    with open(metadata_file, "r") as f:
        data = json.load(f)
    assert data == []

@pytest.mark.unit
def test_write_and_read_metadata(tmp_path):
    """Verifies that metadata can be written and read correctly."""
    metadata_file = tmp_path / "metadata.json"
    repo = MetadataRepository(metadata_file=str(metadata_file))

    sample_metadata = [
        {"file_id": "123", "filename": "a.txt", "upload_timestamp": "now", "size_in_bytes": 10}
    ]

    # Act
    repo.write_metadata(sample_metadata)
    result = repo.read_metadata()

    # Assert
    assert result == sample_metadata

@pytest.mark.unit
def test_add_metadata_creates_new_entry(tmp_path, monkeypatch):
    """Ensures add_metadata adds a new entry and returns a valid UUID."""
    metadata_file = tmp_path / "metadata.json"
    repo = MetadataRepository(metadata_file=str(metadata_file))

    # Mock uuid4 to return a known value
    fake_uuid = uuid.UUID("12345678-1234-5678-1234-567812345678")
    monkeypatch.setattr(uuid, "uuid4", lambda: fake_uuid)

    # Act
    file_id = repo.add_metadata("file.txt", 1024)

    # Assert
    assert file_id == fake_uuid

    with open(metadata_file, "r") as f:
        data = json.load(f)

    assert len(data) == 1
    entry = data[0]
    assert entry["file_id"] == str(fake_uuid)
    assert entry["filename"] == "file.txt"
    assert entry["size_in_bytes"] == 1024
    # Validate timestamp format
    datetime.fromisoformat(entry["upload_timestamp"])

@pytest.mark.unit
def test_get_metadata_by_id_returns_entry(tmp_path, monkeypatch):
    """Ensures get_metadata_by_id finds the correct entry."""
    metadata_file = tmp_path / "metadata.json"
    repo = MetadataRepository(metadata_file=str(metadata_file))

    # Prepare test data
    known_id = str(uuid.uuid4())
    sample_metadata = [
        {"file_id": known_id, "filename": "pic.png", "upload_timestamp": "now", "size_in_bytes": 200}
    ]
    repo.write_metadata(sample_metadata)

    # Act
    result = repo.get_metadata_by_id(known_id)

    # Assert
    assert result == sample_metadata[0]

@pytest.mark.unit
def test_get_metadata_by_id_returns_none_for_missing_id(tmp_path):
    """Ensures get_metadata_by_id returns None when no match found."""
    metadata_file = tmp_path / "metadata.json"
    repo = MetadataRepository(metadata_file=str(metadata_file))

    repo.write_metadata([])

    result = repo.get_metadata_by_id("nonexistent-id")

    assert result is None
