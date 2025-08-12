import os
import threading
import time
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
try:
    import psutil
except Exception:
    raise SystemExit("psutil is required. Install via: pip install psutil")

# -------------------------
# Configuration / defaults
# -------------------------
DEFAULTS = {
    "osu": r"C:\Path\To\osu.exe",
    "mcosu": r"C:\Path\To\McOsu.exe",
    "osulazer": r"C:\Path\To\osulazer.exe",
    "opentablet": r"C:\Program Files\OpenTabletDriver\OpenTabletDriver.UX.Wpf.exe"
}

# Monitor interval (seconds)
MONITOR_INTERVAL = 2.0

# -------------------------
# Helpers
# -------------------------
def is_process_running_by_name(name):
    """Return True if any running process name contains `name` (case-insensitive)."""
    name = name.lower()
    for p in psutil.process_iter(['name', 'exe', 'cmdline']):
        try:
            pname = (p.info.get('name') or "").lower()
            pexe = (p.info.get('exe') or "").lower()
            pcmd = " ".join(p.info.get('cmdline') or []).lower()
            if name in pname or name in pexe or name in pcmd:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False

def launch_exe(path):
    """Launch an executable path and return the Popen or raise."""
    if not path or not os.path.isfile(path):
        raise FileNotFoundError(f"File not found: {path}")
    # Start without waiting; creationflags to avoid console for GUI exes
    if os.name == 'nt':
        CREATE_NO_WINDOW = 0x08000000
        return subprocess.Popen([path], creationflags=CREATE_NO_WINDOW)
    else:
        return subprocess.Popen([path])

# -------------------------
# Background monitor thread
# -------------------------
class MonitorThread(threading.Thread):
    def __init__(self, get_paths_func, ensure_open_tablet_always):
        super().__init__(daemon=True)
        self.get_paths = get_paths_func
        self.ensure_flag = ensure_open_tablet_always
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def run(self):
        while not self._stop_event.is_set():
            osu_path, mcosu_path, osulazer_path, tablet_path, ensure_flag = self.get_paths()
            # If ensure_flag True -> keep OpenTabletDriver running
            try:
                if ensure_flag:
                    if not is_process_running_by_name("opentabletdriver.ux.wpf"):
                        # try by exe name fallback
                        if os.path.isfile(tablet_path):
                            try:
                                launch_exe(tablet_path)
                                print("Started OpenTabletDriver (monitor)")
                            except Exception as e:
                                print("Failed to start OpenTabletDriver:", e)
                        else:
                            print("OpenTabletDriver path missing or invalid:", tablet_path)
                else:
                    # If not always-ensure, still watch if any osu process launched — then ensure tablet runs
                    any_osu_running = (
                        is_process_running_by_name("osu") or
                        is_process_running_by_name("mcosu") or
                        is_process_running_by_name("osulazer")
                    )
                    if any_osu_running:
                        if not is_process_running_by_name("opentabletdriver.ux.wpf"):
                            if os.path.isfile(tablet_path):
                                try:
                                    launch_exe(tablet_path)
                                    print("Started OpenTabletDriver because osu detected")
                                except Exception as e:
                                    print("Failed to start OpenTabletDriver:", e)
                            else:
                                print("OpenTabletDriver path missing or invalid:", tablet_path)
            except Exception as e:
                print("Monitor error:", e)
            time.sleep(MONITOR_INTERVAL)

# -------------------------
# GUI
# -------------------------
class LauncherApp:
    def __init__(self, root):
        self.root = root
        root.title("osu / OpenTabletDriver Launcher")
        root.geometry("680x240")
        root.resizable(False, False)

        main = ttk.Frame(root, padding=12)
        main.pack(fill=tk.BOTH, expand=True)

        # Paths frame
        paths_frame = ttk.LabelFrame(main, text="Executable paths")
        paths_frame.pack(fill=tk.X, padx=4, pady=4)

        self.entries = {}
        row = 0
        for key, label in (("osu", "osu.exe (classic)"),
                           ("mcosu", "McOsu.exe"),
                           ("osulazer", "osulazer.exe"),
                           ("opentablet", "OpenTabletDriver.UX.Wpf.exe")):
            ttk.Label(paths_frame, text=label).grid(row=row, column=0, sticky=tk.W, padx=6, pady=6)
            e = ttk.Entry(paths_frame, width=60)
            e.grid(row=row, column=1, padx=6, pady=6, sticky=tk.W)
            e.insert(0, DEFAULTS.get(key, ""))
            self.entries[key] = e
            btn = ttk.Button(paths_frame, text="Browse", command=lambda k=key: self.browse_path(k))
            btn.grid(row=row, column=2, padx=6, pady=6)
            row += 1

        # options
        opts_frame = ttk.Frame(main)
        opts_frame.pack(fill=tk.X, padx=4, pady=6)

        self.ensure_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(opts_frame, text="Keep OpenTabletDriver running (auto-restart if it closes)",
                        variable=self.ensure_var).pack(anchor=tk.W, padx=6, pady=2)

        # launcher buttons
        btns_frame = ttk.Frame(main)
        btns_frame.pack(fill=tk.X, padx=4, pady=6)

        ttk.Button(btns_frame, text="Launch osu.exe", command=lambda: self.launch_and_ensure("osu")).grid(row=0, column=0, padx=6, pady=6)
        ttk.Button(btns_frame, text="Launch McOsu.exe", command=lambda: self.launch_and_ensure("mcosu")).grid(row=0, column=1, padx=6, pady=6)
        ttk.Button(btns_frame, text="Launch osulazer.exe", command=lambda: self.launch_and_ensure("osulazer")).grid(row=0, column=2, padx=6, pady=6)
        ttk.Button(btns_frame, text="Launch OpenTabletDriver only", command=lambda: self.launch_and_ensure("opentablet")).grid(row=0, column=3, padx=6, pady=6)

        # start monitor thread
        self.monitor = MonitorThread(self.get_paths_tuple, self.ensure_var.get)
        self.monitor.start()

        # make sure monitor sees the checkbox state by using a wrapper function
        def monitor_get_paths():
            return self.get_paths_tuple()
        # replace the thread's get_paths with a lambda that also reads checkbox each loop
        self.monitor.get_paths = self.get_paths_tuple

        # ensure proper shutdown
        root.protocol("WM_DELETE_WINDOW", self.on_close)

    def browse_path(self, key):
        p = filedialog.askopenfilename(title=f"Select {key} executable",
                                       filetypes=[("Executables", "*.exe"), ("All files", "*.*")])
        if p:
            self.entries[key].delete(0, tk.END)
            self.entries[key].insert(0, p)

    def get_paths_tuple(self):
        osu = self.entries["osu"].get().strip()
        mcosu = self.entries["mcosu"].get().strip()
        osulazer = self.entries["osulazer"].get().strip()
        tablet = self.entries["opentablet"].get().strip()
        ensure = self.ensure_var.get()
        return osu, mcosu, osulazer, tablet, ensure

    def launch_and_ensure(self, which):
        paths = {k: self.entries[k].get().strip() for k in self.entries}
        path = paths.get(which)
        if not path:
            messagebox.showerror("Path missing", f"Path for {which} is empty. Set the path first.")
            return
        if not os.path.isfile(path):
            messagebox.showerror("File not found", f"{path} not found. Check the path.")
            return
        try:
            launch_exe(path)
            self.log(f"Launched: {path}")
        except Exception as e:
            self.log(f"Failed to launch {path}: {e}")
            messagebox.showerror("Launch failed", str(e))
            return

        # ensure OpenTabletDriver immediately after launching
        tablet_path = paths.get("opentablet")
        if tablet_path and os.path.isfile(tablet_path):
            if not is_process_running_by_name("opentabletdriver.ux.wpf"):
                try:
                    launch_exe(tablet_path)
                    self.log(f"Started OpenTabletDriver: {tablet_path}")
                except Exception as e:
                    self.log(f"Failed to start OpenTabletDriver: {e}")
        else:
            # try to start even if path invalid by name (less reliable)
            if not is_process_running_by_name("opentabletdriver.ux.wpf"):
                self.log("OpenTabletDriver not running and path invalid/missing. Provide the correct path if needed.")

    def log(self, text):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.status_text.insert(tk.END, f"[{timestamp}] {text}\n")
        self.status_text.see(tk.END)

    def on_close(self):
        if messagebox.askokcancel("Quit", "Stop launcher and exit?"):
            try:
                self.monitor.stop()
            except Exception:
                pass
            self.root.destroy()

def main():
    root = tk.Tk()
    app = LauncherApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
