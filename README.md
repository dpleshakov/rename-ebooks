# rename-ebooks

A simple Python script to rename `.fb2`, `.epub2`, and `.epub3` files using ebook metadata

## Features

- Renames files using author names and book titles from metadata
- Supports single files or entire directories

## Installation

```bash
pip install ebookmeta
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

## Testing

To run the tests:

1. Install test dependencies:

    ```bash
    pip install pytest pytest-cov
    ```

2. Run all tests with detailed output:

    ```bash
    pytest -v tests/
    ```

3. To check code coverage:

    ```bash
    pytest --cov=rename_ebooks tests/
    ```

## License

MIT License  
[View License](LICENSE)
