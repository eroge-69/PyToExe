import os
from pathlib import Path
import win32com.client

# === CONFIGURE THESE ===
dosbox_path = r"C:\dosbox-x\dosbox-x.exe"
life79_exe_path = r"C:\PROGRAMS.PGC\LIFE79.EXE"

# === CREATE SHORTCUT ON DESKTOP ===
desktop = Path(os.path.join(os.environ["USERPROFILE"], "Desktop"))
shortcut_path = desktop / "Run LIFE79 (Quickload).lnk"

shell = win32com.client.Dispatch("WScript.Shell")
shortcut = shell.CreateShortCut(str(shortcut_path))
shortcut.TargetPath = dosbox_path
shortcut.Arguments = f'"{life79_exe_path}"'  # this mimics drag-and-drop quickload
shortcut.WorkingDirectory = str(Path(life79_exe_path).parent)
shortcut.IconLocation = dosbox_path
shortcut.Save()

print(f"Shortcut created: {shortcut_path}")
