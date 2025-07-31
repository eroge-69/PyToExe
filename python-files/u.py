import base64
import os
import shutil
from pathlib import Path
import winshell
from win32com.client import Dispatch

# fake picture here
b64_string = "iVBORw0KGgoAAAANSUhEUgAAAAUA..."

# Decode and save image
image_path = Path.home() / "Pictures" / "startup_image.png"
image_path.parent.mkdir(parents=True, exist_ok=True)
with open(image_path, "wb") as f:
    f.write(base64.b64decode(b64_string))

# put in startup folder
startup_folder = Path(winshell.startup())
shortcut_path = startup_folder / "ImageFolderShortcut.lnk"

shell = Dispatch('WScript.Shell')
shortcut = shell.CreateShortCut(str(shortcut_path))
shortcut.Targetpath = str(image_path.parent)
shortcut.WorkingDirectory = str(image_path.parent)
shortcut.IconLocation = str(image_path)
shortcut.save()