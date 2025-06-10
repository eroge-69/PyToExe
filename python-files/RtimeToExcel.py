import pandas as pd
import sys

# Command line arguments: file_path, output_name, is_rod


# File to convert to excel
file_path = sys.argv[1]

# Output file name
output_name = sys.argv[2]

# Boolean to determine if the file is rod data
try:
  is_rod = eval(sys.argv[3])
except:
  is_rod = False # Default to False

# Figure out the header situation (a function)
def find_header_length(file_path: str) -> int:
    """
    Method to find the length of the file's header. +2 removes some additional white space

    Args:
        file_path (str): Path to the text file

    Returns:
        int: The number of lines in the header, or -1 if no data is found
    """

    try:
        with open(file_path, 'r') as file:
            for count, line in enumerate(file):
                # First 5 lines don't follow the format, but is header
                if count > 5:
                  parts = line.split()
                  # Check if it follows 'Point #' format
                  try:
                    if parts[0] == "Point":
                      continue
                    else:
                      return count

                  # The line is blank. Not part of the header
                  except IndexError:
                    return count + 2

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return -1

    return -1

# Function to remove header
def remove_header(file_path: str, header_length: int) -> None:
    """
    Removes header of a given R*Time file

    Args:
        file_path (str): Path to the text file

    Returns:
        None
    """

    lines = []
    # Reads in the lines of the file
    with open(file_path) as file:
      lines = file.readlines()

    with open(file_path, "w") as file:
      for line_num, line in enumerate(lines):
        if line_num <= header_length:
          continue
        else:
          file.write(line)

# Function to remove dashed lines
def remove_dashes(file_path: str) -> None:
    """
    Removes the random dashes in the R*Time file

    Args:
        file_path (str): Path to the text file

    Returns:
        None
    """
    with open(file_path, "r+") as file:
      lines = file.readlines()
      file.seek(0)
      file.truncate()
      for number, line in enumerate(lines):
        if number not in [1]:
          file.write(line)

# Cleaning up the file before making dataframes
header_length = find_header_length(file_path)
remove_header(file_path, header_length)
remove_dashes(file_path)

# Make Dataframe
df = pd.read_fwf(file_path)

# Additional cleaning for rod data
if is_rod:
  df.drop(df.columns[df.columns.str.contains('unnamed',case = False)],axis = 1, inplace = True)

# dataframe to excel
df.to_excel(output_name, index=False)