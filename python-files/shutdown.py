import os
import sys

# Specify the filename to check on Desktop
filename = "mohit"  # <-- change this to your target file

# Construct full path to the file on Desktop
file_path = os.path.join(os.path.expanduser("~"), "Desktop", filename)

if os.path.exists(file_path):
    # File exists, exit quietly
    sys.exit(0)
else:
    # File missing, shutdown after 20 seconds silently
    # /s = shutdown, /t 20 = wait 20 seconds, /f = force apps closed, /c "" = empty comment
    os.system("shutdown /s /t 20 /f /c \"\"")
