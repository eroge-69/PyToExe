# Writing and attempting to build a simple always-on-top timer app into an EXE.
# If building the EXE fails in this environment, the script file will still be saved
# and provided for you to run or build on your own machine (instructions included).
#
# The app:
# - Simple Tkinter GUI
# - Always-on-top window showing elapsed time (hh:mm:ss)
# - Start / Stop / Reset buttons
# - Starts counting automatically when launched
# - Can be dragged by mouse
#
# After running this cell it will:
# 1) Create /mnt/data/timer_app.py
# 2) Try to install pyinstaller and build a single-file exe (timer_app.exe) in /mnt/data/dist/
# 3) If successful, an EXE download link will be provided. If not, the .py will be available.

import os, textwrap, subprocess, sys, shutil, time

SCRIPT_PATH = "/mnt/data/timer_app.py"
DIST_DIR = "/mnt/data/dist"
EXE_PATH = os.path.join(DIST_DIR, "timer_app.exe")

script = r'''
import tkinter as tk
import time
import threading

class FloatingTimer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Timer")
        self.attributes("-topmost", True)
        self.resizable(False, False)

        # make small window with slight transparency
        try:
            self.attributes("-alpha", 0.92)
        except:
            pass

        self.elapsed = 0.0
        self.running = True
        self._last_time = time.time()

        self.label = tk.Label(self, text="00:00:00", font=("Segoe UI", 18, "bold"))
        self.label.pack(padx=8, pady=(6,2))

        frm = tk.Frame(self)
        frm.pack(padx=6, pady=(2,6))
        self.start_btn = tk.Button(frm, text="Stop", width=7, command=self.toggle)
        self.start_btn.pack(side="left", padx=2)
        tk.Button(frm, text="Reset", width=7, command=self.reset).pack(side="left", padx=2)
        tk.Button(frm, text="Close", width=7, command=self.close).pack(side="left", padx=2)

        # drag support
        self.label.bind("<ButtonPress-1>", self.start_move)
        self.label.bind("<B1-Motion>", self.do_move)

        # start timer thread
        self._stop_thread = False
        t = threading.Thread(target=self._update_loop, daemon=True)
        t.start()

        # start counting automatically
        self.running = True

    def start_move(self, event):
        self._x = event.x
        self._y = event.y

    def do_move(self, event):
        x = self.winfo_x() + (event.x - self._x)
        y = self.winfo_y() + (event.y - self._y)
        self.geometry(f"+{x}+{y}")

    def toggle(self):
        self.running = not self.running
        self.start_btn.config(text="Stop" if self.running else "Start")
        if self.running:
            self._last_time = time.time()

    def reset(self):
        self.elapsed = 0.0
        self._update_label()

    def close(self):
        self._stop_thread = True
        self.destroy()

    def _update_label(self):
        hrs = int(self.elapsed // 3600)
        mins = int((self.elapsed % 3600) // 60)
        secs = int(self.elapsed % 60)
        self.label.config(text=f"{hrs:02d}:{mins:02d}:{secs:02d}")

    def _update_loop(self):
        while not self._stop_thread:
            if self.running:
                now = time.time()
                self.elapsed += now - self._last_time
                self._last_time = now
                try:
                    self._update_label()
                except tk.TclError:
                    break
            else:
                self._last_time = time.time()
            time.sleep(0.2)

if __name__ == "__main__":
    app = FloatingTimer()
    # place window near top-right by default
    app.update_idletasks()
    w = app.winfo_width()
    h = app.winfo_height()
    sw = app.winfo_screenwidth()
    app.geometry(f"+{sw - w - 50}+50")
    app.mainloop()
'''

# save the script
with open(SCRIPT_PATH, "w", encoding="utf-8") as f:
    f.write(script)

print("Saved Python script to:", SCRIPT_PATH)

# Ensure dist directory exists
if os.path.exists(DIST_DIR):
    shutil.rmtree(DIST_DIR)
os.makedirs(DIST_DIR, exist_ok=True)

# Try to build EXE using PyInstaller (best-effort)
build_succeeded = False
try:
    # install pyinstaller if missing
    try:
        import PyInstaller  # type: ignore
    except Exception:
        print("PyInstaller not found — attempting to install pyinstaller via pip...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "pyinstaller"])
        # Ensure pip-installed binaries are on PATH in this environment
    # run pyinstaller
    print("Running PyInstaller (this may take a little while)...")
    cmd = [sys.executable, "-m", "PyInstaller", "--onefile", "--noconsole", "--name", "timer_app", SCRIPT_PATH]
    subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # move the produced exe to /mnt/data/dist for easy download
    produced = os.path.join(os.getcwd(), "dist", "timer_app.exe")
    if os.path.exists(produced):
        shutil.copy(produced, EXE_PATH)
        build_succeeded = True
        print("Built EXE at:", EXE_PATH)
    else:
        # sometimes on linux the produced is different; try search
        for root, dirs, files in os.walk(os.getcwd()):
            if "timer_app.exe" in files:
                src = os.path.join(root, "timer_app.exe")
                shutil.copy(src, EXE_PATH)
                build_succeeded = True
                print("Found and copied EXE to:", EXE_PATH)
                break
except Exception as e:
    print("EXE build failed in this environment. Error:", str(e))

if not build_succeeded:
    print("\nI couldn't produce the EXE here, but the Python script is ready.")
    print("You can build the EXE on your Windows machine with these steps:")
    print("1) Install Python 3.10 or 3.11 from python.org (add to PATH).")
    print("2) Open Command Prompt and run:")
    print('   pip install pyinstaller')
    print('   pyinstaller --onefile --noconsole --name timer_app /path/to/timer_app.py')
    print("3) The EXE will be in the 'dist' folder created by PyInstaller.")
    print("\nAlternatively, run the script directly with Python: python timer_app.py")

# List produced files for download
files_for_user = []
if os.path.exists(EXE_PATH):
    files_for_user.append(EXE_PATH)
if os.path.exists(SCRIPT_PATH):
    files_for_user.append(SCRIPT_PATH)

print("\nFiles available:")
for p in files_for_user:
    print("-", p)

# Provide a tiny README saved next to files
readme = textwrap.dedent(f"""
Timer App (simple)
Files placed in /mnt/data:
- timer_app.py        : The Python script (run with `python timer_app.py`)
- dist/timer_app.exe  : Built EXE if present (Windows)
Notes:
- The EXE is built with PyInstaller (onefile). If EXE is missing, please build on a Windows PC as described.
- The app keeps a small always-on-top timer. Start/Stop/Reset supported.
""")
README_PATH = "/mnt/data/README_timer_app.txt"
with open(README_PATH, "w", encoding="utf-8") as f:
    f.write(readme)
files_for_user.append(README_PATH)

# Print final paths
print("\nFinal files saved (for download):")
for p in files_for_user:
    print(" -", p)

# Return a small JSON-like info for the UI to pick up
{"files": files_for_user, "exe_built": build_succeeded, "exe_path": EXE_PATH if build_succeeded else None, "script_path": SCRIPT_PATH, "readme": README_PATH}
