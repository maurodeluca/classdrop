import pytest
from unittest.mock import MagicMock
from app.services.file_service import FileService
import app.exceptions as ex
import uuid

@pytest.mark.unit
def test_save_uploaded_file_success(monkeypatch):
    """Ensures a file is saved correctly and metadata is added."""

    # Arrange
    file_repo = MagicMock()
    metadata_repo = MagicMock()
    service = FileService(file_repo, metadata_repo, max_size_mb=5)

    filename = "test.txt"
    content = b"hello world"
    fake_file_id = uuid.uuid4()

    file_repo.get_file_extension.return_value = ".txt"
    metadata_repo.add_metadata.return_value = fake_file_id

    # Act
    result = service.save_uploaded_file(filename, content)

    # Assert
    assert result == fake_file_id
    metadata_repo.add_metadata.assert_called_once_with(filename, len(content))
    file_repo.write_file.assert_called_once_with(fake_file_id, ".txt", content)

@pytest.mark.unit
def test_save_uploaded_file_invalid_filename(monkeypatch):
    """Raises InvalidFilenameException for invalid filename."""
    
    # Arrange
    file_repo = MagicMock()
    metadata_repo = MagicMock()
    service = FileService(file_repo, metadata_repo)

    monkeypatch.setattr("app.services.file_service.is_valid_filename", lambda _: False)

    # Act & Assert
    with pytest.raises(ex.InvalidFilenameException):
        service.save_uploaded_file("bad|name.txt", b"content")

@pytest.mark.unit
def test_save_uploaded_file_too_large(monkeypatch):
    """Raises FileSizeExceededException when file too large."""
    
    # Arrange
    file_repo = MagicMock()
    metadata_repo = MagicMock()
    service = FileService(file_repo, metadata_repo, max_size_mb=1)

    monkeypatch.setattr("app.services.file_service.is_valid_filename", lambda _: True)

    big_content = b"x" * (2 * 1024 * 1024)  # 2 MB

    # Act & Assert
    with pytest.raises(ex.FileSizeExceededException):
        service.save_uploaded_file("bigfile.txt", big_content)

@pytest.mark.unit
def test_save_uploaded_file_dangerous_extension(monkeypatch):
    """Raises DangerousFileExtensionException for dangerous extension."""
    
    # Arrange
    file_repo = MagicMock()
    metadata_repo = MagicMock()
    service = FileService(file_repo, metadata_repo)

    monkeypatch.setattr("app.services.file_service.is_valid_filename", lambda _: True)

    file_repo.get_file_extension.return_value = ".exe"

    # Act & Assert
    with pytest.raises(ex.DangerousFileExtensionException):
        service.save_uploaded_file("virus.exe", b"evil")

@pytest.mark.unit
def test_get_all_files_metadata():
    """Ensures all metadata entries are returned."""
    
    # Arrange
    file_repo = MagicMock()
    metadata_repo = MagicMock()
    metadata_repo.read_metadata.return_value = [{"file_id": "1"}]

    service = FileService(file_repo, metadata_repo)

    # Act
    result = service.get_all_files_metadata()

    # Assert
    assert result == [{"file_id": "1"}]
    metadata_repo.read_metadata.assert_called_once()

@pytest.mark.unit
def test_fetch_downloadable_file_by_id_success():
    """Ensures fetch_downloadable_file_by_id returns path and filename."""
    
    # Arrange
    file_repo = MagicMock()
    metadata_repo = MagicMock()
    service = FileService(file_repo, metadata_repo)

    file_id = uuid.uuid4()
    filename = "file.txt"
    path = "/uploads/file.txt"

    metadata_repo.get_metadata_by_id.return_value = {"file_id": str(file_id), "filename": filename}
    file_repo.get_file_path.return_value = path
    file_repo.file_exists.return_value = True

    # Act
    result = service.fetch_downloadable_file_by_id(file_id)

    # Assert
    assert result == (path, filename)
    file_repo.get_file_path.assert_called_once_with(file_id, filename)
    file_repo.file_exists.assert_called_once_with(path)

@pytest.mark.unit
def test_fetch_downloadable_file_by_id_not_in_metadata():
    """Raises FileNotFoundError when metadata missing."""
    
    # Arrange
    file_repo = MagicMock()
    metadata_repo = MagicMock()
    service = FileService(file_repo, metadata_repo)
    file_id = uuid.uuid4()
    
    metadata_repo.get_metadata_by_id.side_effect = ValueError("No metadata found for file_id: {file_id}")

    # Act & Assert
    with pytest.raises(FileNotFoundError, match="metadata"):
        service.fetch_downloadable_file_by_id(file_id)

@pytest.mark.unit
def test_fetch_downloadable_file_by_id_not_on_disk():
    """Raises FileNotFoundError when file not on disk."""
    
    # Arrange
    file_repo = MagicMock()
    metadata_repo = MagicMock()
    service = FileService(file_repo, metadata_repo)

    file_id = uuid.uuid4()
    metadata_repo.get_metadata_by_id.return_value = {"file_id": str(file_id), "filename": "file.txt"}
    file_repo.get_file_path.return_value = "/fake/path/file.txt"
    file_repo.file_exists.return_value = False

    # Act & Assert
    with pytest.raises(FileNotFoundError, match="disk"):
        service.fetch_downloadable_file_by_id(file_id)