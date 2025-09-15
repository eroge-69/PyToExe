import os, glob
import win32com.client  # pip install pywin32

FLAG = "--touch-events"
DESKTOPS = [
    os.path.join(os.path.expandvars(r"%USERPROFILE%"), "Desktop"),
    r"C:\Users\Public\Desktop",  # shows on your desktop too
]

shell = win32com.client.Dispatch("WScript.Shell")
changed = 0

for desk in DESKTOPS:
    if not os.path.isdir(desk):
        continue
    for lnk in glob.glob(os.path.join(desk, "*.lnk")):
        sc = shell.CreateShortcut(lnk)
        exe = os.path.basename((sc.TargetPath or "")).lower()
        if exe != "chrome.exe":
            continue

        args = (sc.Arguments or "").strip()
        if FLAG.lower() in [t.lower() for t in args.split()]:
            print(f"Already had flag: {lnk}")
            continue

        sc.Arguments = (args + " " + FLAG).strip() if args else FLAG
        try:
            sc.Save()
            print(f"Updated: {lnk}")
            changed += 1
        except Exception as e:
            print(f"Can't update (likely needs admin): {lnk}\n{e}")

print(f"Done. Updated {changed} shortcut(s).")
print("Tip: Right-click the same shortcut → Properties. If Windows still only shows the EXE in 'Target',")
print("launch it and check chrome://version → Command Line (that is the real source of truth).")
