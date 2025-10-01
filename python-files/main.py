import os
import pandas as pd

# -------------------------
# USER INPUTS
# -------------------------
folder_path = input("Enter the folder path containing .jpg files: ").strip()
file_extension = ".jpg"

name_file = input("Enter the path to your names file (.txt, .csv, .xlsx): ").strip()

# Optional: for CSV/XLSX
name_column = input("Enter the column name containing names (if applicable, else leave blank): ").strip()

# Optional settings
add_number = input("Add numbering? (yes/no) [default: yes]: ").strip().lower() != "no"
number_before = input("Number before name? (yes/no) [default: yes]: ").strip().lower() != "no"
prefix = input("Optional prefix (leave blank if none): ").strip()
suffix = input("Optional suffix (leave blank if none): ").strip()

# -------------------------
# LOAD NAMES
# -------------------------
if name_file.endswith(".txt"):
    with open(name_file, "r", encoding="utf-8") as f:
        names = [line.strip() for line in f.readlines()]
elif name_file.endswith(".csv"):
    df = pd.read_csv(name_file)
    if name_column:
        names = df[name_column].tolist()
    else:
        names = df.iloc[:, 0].tolist()
elif name_file.endswith(".xlsx"):
    df = pd.read_excel(name_file)
    if name_column:
        names = df[name_column].tolist()
    else:
        names = df.iloc[:, 0].tolist()
else:
    raise ValueError("Unsupported file type. Use .txt, .csv, or .xlsx.")

# -------------------------
# GET IMAGE FILES
# -------------------------
files = [f for f in os.listdir(folder_path) if f.endswith(file_extension)]
files.sort()  # optional: sort alphabetically

if len(names) > len(files):
    raise ValueError("More names than image files. Please check your input.")

# -------------------------
# RENAME FILES
# -------------------------
for i, file in enumerate(files):
    old_path = os.path.join(folder_path, file)
    
    new_name = names[i]
    
    # Apply prefix/suffix
    new_name = f"{prefix}{new_name}{suffix}"
    
    # Apply numbering if selected
    if add_number:
        num = str(i + 1).zfill(3)  # zero-padded numbers, e.g., 001
        if number_before:
            new_name = f"{num}_{new_name}"
        else:
            new_name = f"{new_name}_{num}"
    
    new_path = os.path.join(folder_path, f"{new_name}{file_extension}")
    os.rename(old_path, new_path)
    print(f"Renamed {file} -> {new_name}{file_extension}")

print("Renaming complete!")
