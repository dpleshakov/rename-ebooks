#!/usr/bin/env python3
"""
Ebook File Renamer Tool

This script renames ebook files (.fb2, .epub) based on their metadata information.

Example usage:
    $ python rename_ebooks.py /path/to/ebooks
    $ python rename_ebooks.py single_file.epub
"""

import argparse
import os
import platform
from typing import Mapping, Optional

import ebookmeta  # type: ignore[import-untyped] # pylint: disable=import-error

# pylint: disable=line-too-long
_TRANSLATE_TABLE: Optional[Mapping[int, None]] = None


def _init_translate_table() -> None:
    """Initialize translation table for forbidden filename characters.
    
    Creates a translation table based on the operating system's filename restrictions.
    Windows has more restricted characters compared to Unix-based systems.
    """
    global _TRANSLATE_TABLE  # pylint: disable=global-statement
    if _TRANSLATE_TABLE is None:
        if platform.system() == 'Windows':
            forbidden_chars = {'<', '>', ':', '"', '/', '\\', '|', '?', '*', '\x00'}
        else:
            forbidden_chars = {'/', '\x00'}

        _TRANSLATE_TABLE = str.maketrans({char: None for char in forbidden_chars})


def parse_arguments() -> argparse.Namespace:
    """Parse and validate command-line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments with 'path' attribute
    
    Raises:
        argparse.ArgumentError: If the specified path doesn't exist
    """
    parser = argparse.ArgumentParser(
        prog=os.path.basename(__file__),
        description="Rename .fb2, .epub2, .epub3 files in a specified directory according to books metadata"
    )

    parser.add_argument("path", help="Path to an ebook file or to a directory with ebooks files to rename")
    arguments = parser.parse_args()

    if not os.path.exists(arguments.path):
        parser.error("The specified path does not exist")

    return arguments


def escape_forbidden_characters(filename: str) -> str:
    """Sanitize filename by removing forbidden characters.
    
    Args:
        filename: Original filename to sanitize
    
    Returns:
        str: Filename with forbidden characters removed
    """
    _init_translate_table()
    escaped = filename.translate(_TRANSLATE_TABLE)  # type: ignore[arg-type]
    return escaped


def get_filename(authors: str, title: str, file_extension: str, max_attempts: int = 100) -> str:
    """Generate a unique filename using author(s) and title.
    
    Args:
        authors: Comma-separated list of authors
        title: Book title
        file_extension: Original file extension (.fb2, .epub)
        max_attempts: Maximum number of attempts to find unique name
    
    Returns:
        str: Unique filename with format "Authors - Title[ - Counter].ext"
    
    Raises:
        RuntimeError: If unable to find unique name after max_attempts
    """
    filename = escape_forbidden_characters(f"{authors} - {title}")

    if not os.path.exists(f"{filename}{file_extension}"):
        return f"{filename}{file_extension}"

    for counter in range(1, max_attempts + 1):
        if not os.path.exists(f"{filename}-{counter}{file_extension}"):
            return f"{filename}-{counter}{file_extension}"

    raise RuntimeError(f"Cannot find unique name after {max_attempts} attempts: {filename}{file_extension}")


def rename_ebook(file: str) -> None:
    """Rename a single ebook file using its metadata.
    
    Args:
        file: Path to the ebook file
    
    Raises:
        ValueError: For unsupported file formats
    """
    if not file.endswith((".fb2", ".epub")):
        raise ValueError(f"'{file}' is unsupported ebook file format")

    meta = ebookmeta.get_metadata(file)
    authors = meta.author_list_to_string()
    title = meta.title

    parent_directory = os.path.dirname(file)
    file_extension = os.path.splitext(file)[-1]

    new_file = os.path.join(parent_directory, get_filename(authors, title, file_extension))
    os.rename(file, new_file)


def rename_ebooks(directory: str) -> None:
    """Process all ebook files in a directory recursively.
    
    Args:
        directory: Path to directory containing ebook files
    """
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(('.fb2', '.epub')):
                rename_ebook(os.path.join(root, file))


def main() -> None:
    """Main entry point for the script."""
    arguments = parse_arguments()
    target_path = arguments.path

    if os.path.isdir(target_path):
        rename_ebooks(target_path)
    else:
        rename_ebook(target_path)


if __name__ == "__main__":
    main()
