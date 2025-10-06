import pytest
import uuid
from app.repositories.file_repository import FileRepository  # adjust this import as needed

@pytest.mark.unit
def test_initializes_upload_dir(tmp_path):
    """Ensures the upload directory is created properly."""
    
    # Arrange
    upload_dir = tmp_path / "uploads"

    # Act
    repo = FileRepository(upload_dir=str(upload_dir))

    # Assert
    assert upload_dir.exists()
    assert repo.UPLOAD_DIR == str(upload_dir)

@pytest.mark.unit
def test_write_file_creates_file(tmp_path):
    """Verifies that writing a file saves the correct bytes."""
    
    # Arrange
    upload_dir = tmp_path / "uploads"
    repo = FileRepository(upload_dir=str(upload_dir))

    file_id = uuid.uuid4()
    ext = ".txt"
    content = b"hello world"

    # Act
    repo.write_file(file_id, ext, content)
    file_path = upload_dir / f"{file_id}{ext}"

    # Assert
    assert file_path.exists()
    assert file_path.read_bytes() == content

@pytest.mark.unit
def test_file_exists_true_and_false(tmp_path):
    """Checks file_exists returns True for existing files and False otherwise."""
    
    # Arrange
    upload_dir = tmp_path / "uploads"
    repo = FileRepository(upload_dir=str(upload_dir))

    existing_path = upload_dir / "exists.txt"
    existing_path.write_text("data")

    missing_path = upload_dir / "missing.txt"

    # Act & Assert
    assert repo.file_exists(str(existing_path)) is True
    assert repo.file_exists(str(missing_path)) is False

@pytest.mark.unit
def test_get_file_path_returns_correct_path(tmp_path):
    """Checks that get_file_path builds the correct file path with extension."""
    
    # Arrange
    upload_dir = tmp_path / "uploads"
    repo = FileRepository(upload_dir=str(upload_dir))

    file_id = uuid.uuid4()
    filename = "test.txt"
    ext = filename.split(".")[-1]
    # Act
    expected = upload_dir / f"{file_id}.{ext}"
    result = repo.get_file_path(file_id, filename)

    # Assert
    assert result == str(expected)

@pytest.mark.unit
def test_get_file_extension_returns_extension(tmp_path):
    """Ensures get_file_extension correctly extracts the file extension."""
    
    # Arrange
    repo = FileRepository(upload_dir=str(tmp_path / "uploads"))

    # Act & Assert
    assert repo.get_file_extension("test.txt") == ".txt"
    assert repo.get_file_extension("archive.tar.gz") == ".gz"
    assert repo.get_file_extension("no_extension") == ""

@pytest.mark.unit
def test_custom_upload_dir_is_created(tmp_path):
    """Verifies that a custom upload directory is created automatically."""
    
    # Arrange
    custom_dir = tmp_path / "custom_uploads"
    assert not custom_dir.exists()

    # Act
    repo = FileRepository(upload_dir=str(custom_dir))

    # Assert
    assert custom_dir.exists()
    assert repo.UPLOAD_DIR == str(custom_dir)
