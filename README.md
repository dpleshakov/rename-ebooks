# rename-ebooks

A simple Python script to rename `.fb2`, `.epub2`, and `.epub3` files using ebook metadata

## Requirements

- **Python 3.9 or higher**  
  *Script is tested with Python ≥3.9. Older versions (3.8 and below) might work but are not officially supported.*

## Features

- Renames files using author names and book titles from metadata
- Supports single files or entire directories

## Installation

```bash
# Verify Python version
python --version  # Should show 3.9.x or higher

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Rename a single file
python rename_ebooks.py path/to/book.epub

# Rename all ebooks in a directory
python rename_ebooks.py path/to/ebook-directory
```

## Example

Input: `random_book_name_12345.epub`  
Output: `Some Author - Insert Book Title Here.epub`

## Development and Testing

```bash
pip install -r requirements-dev.txt
```

### Code Quality Tools

#### Static Analysis with Pylint

```bash
# Basic check
pylint rename_ebooks.py
```

#### Static Type Checking with Mypy

```bash
mypy .
```

### Running Tests

- All tests with detailed output:

    ```bash
    pytest tests/
    pytest -v tests/
    ```

- Code coverage report:

    ```bash
    pytest --cov
    pytest --cov --cov-report=term-missing
    ```

#### Run All Checks

```bash
# Example for Unix-like systems
pylint rename_ebooks.py && mypy . && pytest tests/
```

## License

MIT License  
[View License](LICENSE)
