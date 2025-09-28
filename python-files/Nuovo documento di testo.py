import os
import sys
import tempfile
import subprocess
import atexit
import time
import tkinter as tk
from screeninfo import get_monitors

PIDFILE = os.path.join(tempfile.gettempdir(), "blackout_toggle123.pid")
MONITORS_TO_BLACKOUT = [1, 2, 3]

def is_process_running(pid):
    try:
        subprocess.check_output(["tasklist", "/FI", f"PID eq {pid}"], shell=False)
        return True
    except subprocess.CalledProcessError:
        return False

def kill_process(pid):
    try:
        subprocess.check_call(["taskkill", "/PID", str(pid), "/T", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False

def write_pidfile():
    with open(PIDFILE, "w") as f:
        f.write(str(os.getpid()))

def remove_pidfile():
    try:
        if os.path.exists(PIDFILE):
            os.remove(PIDFILE)
    except Exception:
        pass

def toggle_off_existing():
    if os.path.exists(PIDFILE):
        try:
            with open(PIDFILE, "r") as f:
                pid = int(f.read().strip())
        except Exception:
            pid = None
        if pid and pid != os.getpid():
            if is_process_running(pid):
                killed = kill_process(pid)
                for _ in range(10):
                    if not is_process_running(pid):
                        break
                    time.sleep(0.2)
                remove_pidfile()
                if killed:
                    print("Blackout disattivato (processo terminato).")
                    return True
                else:
                    print("Impossibile terminare il processo.")
                    return False
            else:
                remove_pidfile()
                return False
    return False

def create_blackout_windows():
    root = tk.Tk()
    root.withdraw()
    tops = []
    monitors = list(get_monitors())
    for idx, mon in enumerate(monitors, start=1):
        if idx in MONITORS_TO_BLACKOUT:
            top = tk.Toplevel(root)
            top.overrideredirect(True)
            try:
                top.attributes("-topmost", True)
            except Exception:
                pass
            top.configure(bg="black")
            geom = f"{mon.width}x{mon.height}+{mon.x}+{mon.y}"
            top.geometry(geom)
            top.focus_force()
            tops.append(top)

    def on_close():
        for t in tops:
            try:
                t.destroy()
            except:
                pass
        try:
            root.destroy()
        except:
            pass

    root.protocol("WM_DELETE_WINDOW", on_close)
    atexit.register(remove_pidfile)
    root.mainloop()

def main():
    toggled_off = toggle_off_existing()
    if toggled_off:
        return
    write_pidfile()
    try:
        create_blackout_windows()
    finally:
        remove_pidfile()

if __name__ == "__main__":
    main()
