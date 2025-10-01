import os
import shutil

# --- Input paths ---
source_folder = input("Enter full path of Source Folder: ")
destination_folder = input("Enter full path of Destination Folder: ")
text_file = input("Enter full path of Text File with file names: ")

# --- Check paths ---
if not os.path.exists(source_folder):
    print("Source folder does not exist!")
    exit()
if not os.path.exists(destination_folder):
    print("Destination folder does not exist!")
    exit()
if not os.path.exists(text_file):
    print("Text file does not exist!")
    exit()

# --- Read file names ---
with open(text_file, "r") as f:
    file_names = [line.strip() for line in f if line.strip()]

if not file_names:
    print("No file names found in text file!")
    exit()

# --- Copy files ---
copied = 0
for fname in file_names:
    src_file = os.path.join(source_folder, fname)
    if os.path.exists(src_file):
        shutil.copy(src_file, destination_folder)
        print(f"Copied: {fname}")
        copied += 1
    else:
        print(f"Not found: {fname}")

print(f"\nDone! Total files copied: {copied}")