#!/usr/bin/env python3
import argparse
import ebookmeta
import os
import platform


_FORBIDDEN_CHARS = None
_TRANSLATE_TABLE = None


def _init_translate_table():
    global _FORBIDDEN_CHARS, _TRANSLATE_TABLE
    if _TRANSLATE_TABLE is None:
        if platform.system() == 'Windows':
            _FORBIDDEN_CHARS = {'<', '>', ':', '"', '/', '\\', '|', '?', '*', '\x00'}
        else:
            _FORBIDDEN_CHARS = {'/', '\x00'}
        _TRANSLATE_TABLE = str.maketrans({char: None for char in _FORBIDDEN_CHARS})


def parse_arguments():
  parser = argparse.ArgumentParser(
    prog=os.path.basename(__file__),
    description="Rename .fb2, .epub2, .epub3 files in a specified directory according to books metadata")

  parser.add_argument("path", help="Path to an ebook file or to an directory with ebooks files to rename")

  arguments = parser.parse_args()

  if not os.path.exists(arguments.path):
    parser.error("The specified path does not exist")

  return arguments


def escape_forbidden_characters(filename):
  _init_translate_table()
  escaped = filename.translate(_TRANSLATE_TABLE)
  return escaped


def get_filename(authors, title, file_extension):
  filename = "{} - {}{}".format(authors, title, file_extension)
  filename = escape_forbidden_characters(filename)

  return filename


def rename_ebook(file):
  if not file.endswith(".fb2") and not file.endswith(".epub"):
    raise ValueError(f"'{file}' is unsupported ebook file format")

  meta = ebookmeta.get_metadata(file)
  authors = meta.author_list_to_string()
  title = meta.title

  parent_directory = os.path.dirname(file)
  file_extension = os.path.splitext(file)[-1]

  new_file = os.path.join(parent_directory, get_filename(authors, title, file_extension))

  os.rename(file, new_file)


def rename_ebooks(directory):
  for root, _, files in os.walk(directory):
    for file in files:
        if file.endswith(('.fb2', '.epub')):
            rename_ebook(os.path.join(root, file))


def main():
  arguments = parse_arguments()
  target_path = arguments.path

  if os.path.isdir(target_path):
    rename_ebooks(target_path)
  else:
    rename_ebook(target_path)


if __name__ == "__main__":
  main()