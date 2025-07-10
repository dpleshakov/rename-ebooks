import argparse
import ebookmeta
import os


def parse_arguments():
  parser = argparse.ArgumentParser(
    prog=os.path.basename(__file__),
    description="Rename .fb2, .epub2, .epub3 files in a specified directory according with books metadata")

  parser.add_argument("path", help="Path to an ebook file or to an directory with ebooks files to rename")

  arguments = parser.parse_args()

  if not os.path.exists(arguments.path):
    parser.error("'path' should be an exist file or directory")

  return arguments


def escape_windows_forbidden_characters(filename):
  forbidden_characters = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']

  for char in forbidden_characters:
    filename = filename.replace(char, '')

  return filename


def get_filename(authors, title, file_extension):
  filename = "{} - {}{}".format(authors, title, file_extension)
  filename = escape_windows_forbidden_characters(filename)

  return filename


def rename_ebook(file):
  if not file.endswith(".fb2") and not file.endswith(".epub"):
    raise Exception("'{}' is unsupported ebook file format".format(file))

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


if __name__ == "__main__":
  arguments = parse_arguments()
  target_path = arguments.path

  if os.path.isdir(target_path):
    rename_ebooks(target_path)
  else:
    rename_ebook(target_path)