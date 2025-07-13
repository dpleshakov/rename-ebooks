# pylint: disable=missing-module-docstring

import os
import sys
from unittest.mock import patch, MagicMock

import pytest # type: ignore[import-untyped] # pylint: disable=import-error

# pylint: disable=line-too-long
# pylint: disable=missing-function-docstring
# pylint: disable=redefined-outer-name

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import rename_ebooks  # pylint: disable=wrong-import-position


@pytest.fixture
def mock_metadata():
    """Fixture for creating a book metadata mock"""
    meta = MagicMock()
    meta.author_list_to_string.return_value = "Author Name"
    meta.title = "Book Title"
    return meta


@pytest.fixture
def temp_ebook(tmp_path):
    """Fixture for creating a temporary ebook file"""
    ebook_path = tmp_path / "test_book.epub"
    ebook_path.touch()
    return str(ebook_path)


@pytest.fixture(autouse=True)
def reset_module_state():
    """Resets the module state before each test"""
    rename_ebooks._TRANSLATE_TABLE = None  # pylint: disable=protected-access
    yield


@pytest.mark.parametrize("os_name, input_name, expected", [
    ("Windows", "file:name?.txt", "filename.txt"),
    ("Windows", "<book|title>", "booktitle"),
    ("Windows", "a/b\\c*d", "abcd"),
    ("Windows", "valid_name.txt", "valid_name.txt"),
    ("Windows", '"quote"', "quote"),
    ("Windows", "file/name", "filename"),
    ("Windows", "file\\name", "filename"),
    ("Windows", "file|name", "filename"),
    ("Windows", "file?name", "filename"),
    ("Windows", "file*name", "filename"),
    ("Windows", "", ""),
    ("Windows", "no_changes", "no_changes"),
    ("Windows", "file\x00name.txt", "filename.txt"),

    ("Linux", "file:name?.txt", "file:name?.txt"),
    ("Linux", "<book|title>", "<book|title>"),
    ("Linux", "a/b\\c*d", "ab\\c*d"),
    ("Linux", "valid_name.txt", "valid_name.txt"),
    ("Linux", '"quote"', '"quote"'),
    ("Linux", "file/name", "filename"),
    ("Linux", "file\\name", "file\\name"),
    ("Linux", "file|name", "file|name"),
    ("Linux", "file?name", "file?name"),
    ("Linux", "file*name", "file*name"),
    ("Linux", "", ""),
    ("Linux", "no_changes", "no_changes"),
    ("Linux", "file\x00name.txt", "filename.txt"),

    ("Darwin", "file/name", "filename"),
    ("Darwin", "file\\name", "file\\name"),
    ("Darwin", "file:name", "file:name"),
])
def test_escape_forbidden_characters(os_name, input_name, expected):
    with patch('rename_ebooks.platform.system', return_value=os_name):
        result = rename_ebooks.escape_forbidden_characters(input_name)
        assert result == expected


@pytest.mark.parametrize("authors, title, ext, expected", [
    ("Author", "Title", ".epub", "Author - Title.epub"),
    ("Auth:or?", "Tit>le*", ".fb2", "Author - Title.fb2"),
    ("", "", ".epub", " - .epub"),
    ("Author", "Title", "", "Author - Title"),
])
def test_get_filename_basic_cases(authors, title, ext, expected):
    result = rename_ebooks.get_filename(authors, title, ext)
    assert result == expected


@pytest.mark.parametrize("existing_files, expected", [
    ([], "Author - Title.epub"),
    (["Author - Title.epub"], "Author - Title-1.epub"),
    (["Author - Title.epub", "Author - Title-1.epub"], "Author - Title-2.epub"),
])
def test_get_filename_unique_name_generation(existing_files, expected):
    with patch("os.path.exists", side_effect=lambda x: x in existing_files):
        result = rename_ebooks.get_filename("Author", "Title", ".epub")
        assert result == expected


def test_get_filename_exceeds_max_attempts():
    with patch("os.path.exists", return_value=True):
        with pytest.raises(RuntimeError, match="Cannot find unique name after 100 attempts: A - B.txt"):
            rename_ebooks.get_filename("A", "B", ".txt")


def test_rename_ebook_unsupported_format(temp_ebook):
    invalid_file = temp_ebook.replace(".epub", ".txt")
    with pytest.raises(ValueError, match="unsupported ebook file format"):
        rename_ebooks.rename_ebook(invalid_file)


@patch('rename_ebooks.ebookmeta.get_metadata')
@patch('rename_ebooks.os.rename')
def test_rename_ebook_success(mock_rename, mock_get_metadata, mock_metadata, temp_ebook):
    mock_get_metadata.return_value = mock_metadata

    rename_ebooks.rename_ebook(temp_ebook)

    parent_dir = os.path.dirname(temp_ebook)
    expected_new_path = os.path.join(parent_dir, "Author Name - Book Title.epub")
    mock_rename.assert_called_once_with(temp_ebook, expected_new_path)


@patch('rename_ebooks.ebookmeta.get_metadata')
@patch('rename_ebooks.os.rename')
def test_rename_ebook_empty_metadata(mock_rename, mock_get_metadata, temp_ebook):
    mock_meta = MagicMock()
    mock_meta.author_list_to_string.return_value = ""
    mock_meta.title = ""
    mock_get_metadata.return_value = mock_meta

    rename_ebooks.rename_ebook(temp_ebook)

    parent_dir = os.path.dirname(temp_ebook)
    expected_new_path = os.path.join(parent_dir, " - .epub")
    mock_rename.assert_called_once_with(temp_ebook, expected_new_path)


@patch('rename_ebooks.ebookmeta.get_metadata')
@patch('rename_ebooks.os.rename')
def test_rename_ebook_partial_metadata(mock_rename, mock_get_metadata, temp_ebook):
    mock_meta = MagicMock()
    mock_meta.author_list_to_string.return_value = "Author Only"
    mock_meta.title = ""
    mock_get_metadata.return_value = mock_meta

    rename_ebooks.rename_ebook(temp_ebook)

    parent_dir = os.path.dirname(temp_ebook)
    expected_new_path = os.path.join(parent_dir, "Author Only - .epub")
    mock_rename.assert_called_once_with(temp_ebook, expected_new_path)


@patch('rename_ebooks.rename_ebook')
def test_rename_ebooks_directory(mock_rename_ebook, tmp_path):
    valid_ebook1 = tmp_path / "book1.fb2"
    valid_ebook2 = tmp_path / "book2.epub"
    invalid_file = tmp_path / "document.txt"
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    valid_ebook3 = subdir / "book3.epub"

    valid_ebook1.touch()
    valid_ebook2.touch()
    invalid_file.touch()
    valid_ebook3.touch()

    rename_ebooks.rename_ebooks(str(tmp_path))

    assert mock_rename_ebook.call_count == 3
    called_paths = {call.args[0] for call in mock_rename_ebook.call_args_list}
    assert str(valid_ebook1) in called_paths
    assert str(valid_ebook2) in called_paths
    assert str(valid_ebook3) in called_paths


@patch('rename_ebooks.rename_ebook')
def test_main_single_file(mock_rename_ebook, temp_ebook):
    with patch('sys.argv', ['script_name', temp_ebook]):
        rename_ebooks.main()
        mock_rename_ebook.assert_called_once_with(temp_ebook)


@patch('rename_ebooks.rename_ebooks')
def test_main_directory(mock_rename_ebooks, tmp_path):
    with patch('sys.argv', ['script_name', str(tmp_path)]):
        rename_ebooks.main()
        mock_rename_ebooks.assert_called_once_with(str(tmp_path))


def test_main_nonexistent_path(capsys):
    with patch('sys.argv', ['script_name', '/nonexistent/path']):
        with pytest.raises(SystemExit):
            rename_ebooks.main()
        captured = capsys.readouterr()
        assert "The specified path does not exist" in captured.err


@patch('rename_ebooks.ebookmeta.get_metadata')
def test_rename_ebook_metadata_error(mock_get_metadata, temp_ebook):
    mock_get_metadata.side_effect = Exception("Metadata error")

    with pytest.raises(Exception, match="Metadata error"):
        rename_ebooks.rename_ebook(temp_ebook)
