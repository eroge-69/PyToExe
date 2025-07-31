import os
import subprocess
import shutil
from datetime import datetime
import pandas as pd

# === CONFIGURATION ===
target_folder = r'D:\OneDrive\งานป่าน'
destination_folder = r'H:\@Backup all data zip'
seven_zip_path = r'C:\Program Files\7-Zip\7z.exe'  # Make sure this path is correct!

# === FILENAME BASED ON CURRENT DATETIME ===
now = datetime.now()
timestamp = now.strftime('%Y-%m-%d_%H-%M-%S')
zip_filename = f'backup_{timestamp}.7z'
zip_full_path = os.path.join(destination_folder, zip_filename)

# === CREATE ZIP WITH MAX COMPRESSION ===
subprocess.run([
    seven_zip_path, 'a', '-t7z', '-mx=9', zip_full_path, target_folder
], check=True)

# === COPY TO DESTINATION (already saved there by zip path) ===

# === GENERATE FILE LIST FOR LOG ===
file_list = []
for root, dirs, files in os.walk(target_folder):
    for name in dirs:
        file_list.append({'Type': 'Folder', 'Path': os.path.join(root, name)})
    for name in files:
        file_list.append({'Type': 'File', 'Path': os.path.join(root, name)})

# === WRITE TO XLSX LOG FILE ===
log_filename = f'log_{timestamp}.xlsx'
log_path = os.path.join(destination_folder, log_filename)

df = pd.DataFrame(file_list)
df.to_excel(log_path, index=False)

print(f'ZIP created: {zip_full_path}')
print(f'Log saved: {log_path}')