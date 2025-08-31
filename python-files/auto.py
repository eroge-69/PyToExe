import os
import subprocess

maps_dir = './assets'
 
for entry in os.listdir(maps_dir):
    entry_path = os.path.join(maps_dir, entry)
    
    if os.path.isdir(entry_path) or os.path.isfile(entry_path):
        subprocess.run(['python', 'escrow.py', '-d', entry_path])

os.system("python watermark.py -d ./out")