import os
import tempfile

# Create a temporary text file
path = tempfile.gettempdir() + "\\dubai_matcha_labubu.txt"

with open(path, "w", encoding="utf-8") as f:
    f.write("dubai matcha labubu")

# Open it in Notepad
os.system(f'notepad "{path}"')
