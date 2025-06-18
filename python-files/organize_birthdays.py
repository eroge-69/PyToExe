import os
import shutil
from tqdm import tqdm
import time

# Opening progress bar
opening_text = "Dila Programming, where everything Automate"
for i in tqdm(range(100), desc=opening_text, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]'):
    time.sleep(0.01)

# Set the source directory to the current working directory
source_path = os.getcwd()
birthday_path = os.path.join(source_path, 'Birthday')

# Create Birthday folder if it doesn't exist
os.makedirs(birthday_path, exist_ok=True)

# List all folders in the current directory (excluding Birthday)
folders = [f for f in os.listdir(source_path) if os.path.isdir(os.path.join(source_path, f)) and f != 'Birthday']
total = len(folders)
done = 0

with tqdm(total=total, desc='Copying folders', unit='folder') as pbar:
    for folder_name in folders:
        folder_path = os.path.join(source_path, folder_name)
        if len(folder_name) >= 6 and folder_name[2:6].isdigit():
            month = folder_name[2:4]
            day = folder_name[4:6]
            target_path = os.path.join(birthday_path, month, day, folder_name)
            if not os.path.exists(target_path):
                shutil.copytree(folder_path, target_path)
        done += 1
        pbar.set_postfix({'done': done, 'pending': total - done})
        pbar.update(1)

print("Folders copied into Birthday/<MM>/<DD>/ structure.")
