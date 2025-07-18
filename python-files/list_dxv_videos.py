
import os
import pandas as pd
from tkinter import Tk, filedialog
import subprocess

# Open folder dialog
Tk().withdraw()
folder_path = filedialog.askdirectory(title="Select folder containing .dxv/.dxv3/.mov files")

# Check for valid path
if not folder_path:
    print("No folder selected. Exiting.")
    exit()

# Supported extensions
valid_exts = [".dxv", ".dxv3", ".mov"]

# Collect file names
file_names = [f for f in os.listdir(folder_path) if os.path.splitext(f)[1].lower() in valid_exts]

# Save to Excel
df = pd.DataFrame(file_names, columns=["Video File Name"])
output_file = os.path.join(folder_path, "video_file_list.xlsx")
df.to_excel(output_file, index=False)

# Open the Excel file
subprocess.Popen(["start", "", output_file], shell=True)
