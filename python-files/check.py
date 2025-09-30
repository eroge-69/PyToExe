from pyreadmdb import read_mdb
import pandas as pd
import argparse

# -----------------------
# Parse command-line argument
# -----------------------
parser = argparse.ArgumentParser(description="Read an MDB file into Pandas")
parser.add_argument("filename", help="Path to the .mdb file")
args = parser.parse_args()
mdb_file = args.filename


output = ""

# -----------------------
# Read the MDB file using pyreadmdb
# -----------------------
# read_mdb returns a dict of DataFrames keyed by table name
tables = read_mdb(mdb_file)

# Check that the table 'List' exists
if "List" not in tables:
    raise ValueError(f"'List' table not found in {mdb_file}")

df = tables["List"]

# drop unnecessary columns
df = df.drop(columns=['Flag1', 'Flag2', 'Description', 'RefNum', 'AbsPosition'])
df.index += 1

#NULL Cue Column Check:
has_null_cue = df['Cue'].isnull().any()
if has_null_cue:
    output += "Cue NULL error\n:"
    output += df[df['Cue'].isnull()].to_string() + "\n"
    output += "--------------------------------\n"

df['Length'] = df['Length'].fillna('00:00')

# Convert all time lengths to total seconds
for i, row in df.iterrows():
  if len(row['Length']) > 5:
    hours = int(row['Length'][0:2])
    mins = int(row['Length'][3:5])
    secs = int(row['Length'][6:])
    totalTime = (hours * 3600) + (mins * 60) + secs
  else:
    mins = int(row['Length'][0:2])
    secs = int(row['Length'][3:])
    totalTime = (mins * 60) + secs
  df.loc[i, 'Length'] = totalTime

# Extract any row that doesn't have a '+' in the Cue column
df_commands = df[df['Cue'] != '+']

# Create a checkArray which contains the index and total time in seconds to check for each command
checkArray = []
for i, row in df_commands.iterrows():
  hours = int(row['Time'][0:2])
  mins = int(row['Time'][3:5])
  secs = int(row['Time'][6:])
  totalTime = (hours * 3600) + (mins * 60) + secs
  checkArray.append([i, totalTime])


lengthCheck = False
startTime = 0
startIndex = 1
for index, time in checkArray:
  lengthToCheck = time - startTime
  # Filter the DataFrame based on the indexes
  subset_df = df.loc[startIndex:index]
  # Sum the 'Length' column of the subset
  actualLength = subset_df['Length'].sum()

  
  if actualLength < lengthToCheck:
    if lengthCheck == False:
        output += "Length Check Error:\n"
    lengthCheck = True
    output += f"Error at command line {index}. Time is too short. ---- Missing {lengthToCheck - actualLength} seconds\n"

if output == "":
    output = "No errors found. All checks passed."
print(output)
