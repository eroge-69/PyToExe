#!/usr/bin/python
# Command-line tool to decompress mozLz4 files used for example by Firefox to store various kinds of session backup information.
# Works in both Python 2.7.15 and 3.6.7, as of version 2.1.6 of the LZ4 Python bindings at pypi.org/project/lz4.
# To use in another script, simply cut and paste the import statement and the mozlz4_to_text() function (lines 8 to 17).

import lz4.block  # pip install lz4 --user


def mozlz4_to_text(filepath):
    # Given the path to a "mozlz4", "jsonlz4", "baklz4" etc. file, 
    # return the uncompressed text.
    bytestream = open(filepath, "rb")
    bytestream.read(8)  # skip past the b"mozLz40\0" header
    valid_bytes = bytestream.read()
    text = lz4.block.decompress(valid_bytes)
    return text


def main(args):
  # Given command-line arguments of an input filepath for a ".mozlz4" file
  # and optionally an output filepath, write the decompressed text to the
  # output filepath.
  # Default output filepath is the input filepath minus the last three characters
  # (e.g. "foo.jsonlz4" becomes "foo.json")
  filepath_in = args[0]
  if len(args) < 2:
    filepath_out = filepath_in[:-3]
  else:
    filepath_out = args[1]
  text = mozlz4_to_text(filepath_in)
  with open(filepath_out, "wb") as outfile:
    outfile.write(text)
  print("Wrote decompressed text to {}".format(filepath_out))


if __name__ == "__main__":
  import sys
  args = sys.argv[1:]
  if args and not args[0] in ("--help", "-h"):
    main(args)
  else:
    print("Usage: mozlz4.py <mozlz4 file to read> <location to write>")
