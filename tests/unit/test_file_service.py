import pytest
from unittest.mock import MagicMock
from app.services.file_service import FileService
import app.exceptions as ex

@pytest.mark.unit
def test_save_uploaded_file_success(monkeypatch):
    """Ensures a file is saved correctly and metadata is added."""

    # Arrange
    file_repo = MagicMock()
    metadata_repo = MagicMock()
    service = FileService(file_repo, metadata_repo, max_size_mb=5)

    filename = "test.txt"
    content = b"hello world"
    fake_file_id = "1234-uuid"

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
    file_repo = MagicMock()
    metadata_repo = MagicMock()
    service = FileService(file_repo, metadata_repo)

    monkeypatch.setattr("app.services.file_service.is_valid_filename", lambda _: False)

    with pytest.raises(ex.InvalidFilenameException):
        service.save_uploaded_file("bad|name.txt", b"content")

@pytest.mark.unit
def test_save_uploaded_file_too_large(monkeypatch):
    """Raises FileSizeExceededException when file too large."""
    file_repo = MagicMock()
    metadata_repo = MagicMock()
    service = FileService(file_repo, metadata_repo, max_size_mb=1)

    monkeypatch.setattr("app.services.file_service.is_valid_filename", lambda _: True)

    big_content = b"x" * (2 * 1024 * 1024)  # 2 MB
    with pytest.raises(ex.FileSizeExceededException):
        service.save_uploaded_file("bigfile.txt", big_content)

@pytest.mark.unit
def test_save_uploaded_file_dangerous_extension(monkeypatch):
    """Raises DangerousFileExtensionException for dangerous extension."""
    file_repo = MagicMock()
    metadata_repo = MagicMock()
    service = FileService(file_repo, metadata_repo)

    monkeypatch.setattr("app.services.file_service.is_valid_filename", lambda _: True)

    file_repo.get_file_extension.return_value = ".exe"

    with pytest.raises(ex.DangerousFileExtensionException):
        service.save_uploaded_file("virus.exe", b"evil")

@pytest.mark.unit
def test_get_all_files_metadata():
    """Ensures all metadata entries are returned."""
    file_repo = MagicMock()
    metadata_repo = MagicMock()
    metadata_repo.read_metadata.return_value = [{"file_id": "1"}]

    service = FileService(file_repo, metadata_repo)

    result = service.get_all_files_metadata()

    assert result == [{"file_id": "1"}]
    metadata_repo.read_metadata.assert_called_once()

@pytest.mark.unit
def test_fetch_downloadable_file_by_id_success():
    """Ensures fetch_downloadable_file_by_id returns path and filename."""
    file_repo = MagicMock()
    metadata_repo = MagicMock()
    service = FileService(file_repo, metadata_repo)

    file_id = "abc123"
    filename = "file.txt"
    path = "/uploads/file.txt"

    metadata_repo.get_metadata_by_id.return_value = {"file_id": file_id, "filename": filename}
    file_repo.get_file_path.return_value = path
    file_repo.file_exists.return_value = True

    result = service.fetch_downloadable_file_by_id(file_id)

    assert result == (path, filename)
    file_repo.get_file_path.assert_called_once_with(file_id, filename)
    file_repo.file_exists.assert_called_once_with(path)

@pytest.mark.unit
def test_fetch_downloadable_file_by_id_not_in_metadata():
    """Raises FileNotFoundError when metadata missing."""
    file_repo = MagicMock()
    metadata_repo = MagicMock()
    service = FileService(file_repo, metadata_repo)

    metadata_repo.get_metadata_by_id.return_value = None

    with pytest.raises(FileNotFoundError, match="metadata"):
        service.fetch_downloadable_file_by_id("missing-id")

@pytest.mark.unit
def test_fetch_downloadable_file_by_id_not_on_disk():
    """Raises FileNotFoundError when file not on disk."""
    file_repo = MagicMock()
    metadata_repo = MagicMock()
    service = FileService(file_repo, metadata_repo)

    metadata_repo.get_metadata_by_id.return_value = {"file_id": "id", "filename": "file.txt"}
    file_repo.get_file_path.return_value = "/fake/path/file.txt"
    file_repo.file_exists.return_value = False

    with pytest.raises(FileNotFoundError, match="disk"):
        service.fetch_downloadable_file_by_id("id")

@pytest.mark.unit
def test_is_file_size_above_max():
    """Checks file size threshold logic."""
    service = FileService(MagicMock(), MagicMock(), max_size_mb=1)
    below_limit = 1024 * 1024 - 1
    above_limit = 1024 * 1024 + 1

    assert service.is_file_size_above_max(below_limit) is False
    assert service.is_file_size_above_max(above_limit) is True

@pytest.mark.unit
def test_is_dangerous_extension_detection():
    """Ensures dangerous extensions are detected."""
    service = FileService(MagicMock(), MagicMock())

    for ext in [".exe", ".bat", ".sh"]:
        assert service.is_dangerous_extension(ext) is True

    for ext in [".txt", ".png", ".pdf"]:
        assert service.is_dangerous_extension(ext) is False
