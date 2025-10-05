import pytest
from app.repositories.file_repository import FileRepository  # adjust this import as needed

@pytest.mark.unit
def test_initializes_upload_dir(tmp_path):
    """Ensures the upload directory is created properly."""
    upload_dir = tmp_path / "uploads"

    # Act
    repo = FileRepository(upload_dir=str(upload_dir))

    # Assert
    assert upload_dir.exists()
    assert repo.UPLOAD_DIR == str(upload_dir)

@pytest.mark.unit
def test_write_file_creates_file(tmp_path):
    """Verifies that writing a file saves the correct bytes."""
    upload_dir = tmp_path / "uploads"
    repo = FileRepository(upload_dir=str(upload_dir))

    file_id = "test1"
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
    upload_dir = tmp_path / "uploads"
    repo = FileRepository(upload_dir=str(upload_dir))

    existing_path = upload_dir / "exists.txt"
    existing_path.write_text("data")

    missing_path = upload_dir / "missing.txt"

    assert repo.file_exists(str(existing_path)) is True
    assert repo.file_exists(str(missing_path)) is False

@pytest.mark.unit
def test_get_file_path_returns_correct_path(tmp_path):
    """Checks that get_file_path builds the correct file path with extension."""
    upload_dir = tmp_path / "uploads"
    repo = FileRepository(upload_dir=str(upload_dir))

    file_id = "abc123"
    filename = "photo.png"

    expected = upload_dir / f"{file_id}.png"
    result = repo.get_file_path(file_id, filename)

    assert result == str(expected)

@pytest.mark.unit
def test_get_file_extension_returns_extension(tmp_path):
    """Ensures get_file_extension correctly extracts the file extension."""
    repo = FileRepository(upload_dir=str(tmp_path / "uploads"))

    assert repo.get_file_extension("image.jpg") == ".jpg"
    assert repo.get_file_extension("archive.tar.gz") == ".gz"
    assert repo.get_file_extension("no_extension") == ""

@pytest.mark.unit
def test_custom_upload_dir_is_created(tmp_path):
    """Verifies that a custom upload directory is created automatically."""
    custom_dir = tmp_path / "custom_uploads"
    assert not custom_dir.exists()

    repo = FileRepository(upload_dir=str(custom_dir))

    assert custom_dir.exists()
    assert repo.UPLOAD_DIR == str(custom_dir)
