import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import time
from datetime import datetime
import threading
import subprocess
import sys

# ---------- Config ----------
LOCKED_FILE_DEFAULT = "locked_document.txt"
SECRET_FILE_DEFAULT = "secret_pin.txt"
BACKUP_DIR = "pin_backups"
REFRESH_MS = 2000  # auto-refresh interval in milliseconds
MAX_LOG_LINES = 100
# ----------------------------

class TeacherGUI(tk.Tk):
    def __init__(self, locked_file=LOCKED_FILE_DEFAULT, secret_file=SECRET_FILE_DEFAULT):
        super().__init__()
        self.title("Teacher — Lock/Pin Manager")
        self.geometry("720x520")
        self.locked_file = locked_file
        self.secret_file = secret_file

        # Top frame: file selection / info
        top = ttk.Frame(self, padding=(6,6))
        top.pack(side="top", fill="x")

        ttk.Label(top, text="Locked file:").grid(row=0, column=0, sticky="w")
        self.locked_label = ttk.Label(top, text=self.locked_file)
        self.locked_label.grid(row=0, column=1, sticky="w", padx=(4,10))

        ttk.Button(top, text="Choose...", command=self.choose_locked_file).grid(row=0, column=2, padx=4)
        ttk.Label(top, text="PIN file:").grid(row=1, column=0, sticky="w", pady=(4,0))
        self.secret_label = ttk.Label(top, text=self.secret_file)
        self.secret_label.grid(row=1, column=1, sticky="w", padx=(4,10))
        ttk.Button(top, text="Choose...", command=self.choose_secret_file).grid(row=1, column=2, padx=4)

        # Middle: left - unlocked teams, right - controls
        mid = ttk.Frame(self, padding=(6,6))
        mid.pack(side="top", fill="both", expand=True)

        # Left pane: Unlocked list
        left = ttk.LabelFrame(mid, text="Unlocked Teams / Document")
        left.pack(side="left", fill="both", expand=True, padx=(0,6))

        self.listbox = tk.Listbox(left, height=20)
        self.listbox.pack(side="left", fill="both", expand=True, padx=(4,0), pady=4)
        self.listbox_scroll = ttk.Scrollbar(left, orient="vertical", command=self.listbox.yview)
        self.listbox_scroll.pack(side="left", fill="y", pady=4)
        self.listbox.config(yscrollcommand=self.listbox_scroll.set)

        # Right pane: controls
        right = ttk.LabelFrame(mid, text="Controls")
        right.pack(side="right", fill="y", padx=(6,0))

        ttk.Button(right, text="Refresh Now", command=self.refresh_now).pack(fill="x", padx=8, pady=(8,4))
        ttk.Button(right, text="Open Unlocked File", command=self.open_locked_file).pack(fill="x", padx=8, pady=4)
        ttk.Button(right, text="Clear Unlocked File", command=self.clear_locked_file).pack(fill="x", padx=8, pady=4)

        # PIN change area
        pinframe = ttk.LabelFrame(right, text="Change PIN")
        pinframe.pack(padx=8, pady=(12,8), fill="x")

        ttk.Label(pinframe, text="New PIN:").pack(anchor="w", padx=6, pady=(6,0))
        self.pin_var = tk.StringVar()
        self.pin_entry = ttk.Entry(pinframe, textvariable=self.pin_var)
        self.pin_entry.pack(fill="x", padx=6, pady=(0,6))
        ttk.Button(pinframe, text="Set PIN (overwrite)", command=self.set_pin).pack(fill="x", padx=6, pady=(0,6))
        ttk.Button(pinframe, text="Set PIN and clear unlocked file", command=self.set_pin_and_clear).pack(fill="x", padx=6, pady=(0,6))

        # Show file timestamps
        self.info_frame = ttk.Frame(right)
        self.info_frame.pack(fill="x", padx=8, pady=(6,0))
        self.locked_time_label = ttk.Label(self.info_frame, text="Locked file: —")
        self.locked_time_label.pack(anchor="w")
        self.secret_time_label = ttk.Label(self.info_frame, text="PIN file: —")
        self.secret_time_label.pack(anchor="w")

        # Bottom: status log
        bottom = ttk.LabelFrame(self, text="Status / Log")
        bottom.pack(side="bottom", fill="x", padx=6, pady=6)
        self.log_text = tk.Text(bottom, height=6, wrap="word", state="disabled")
        self.log_text.pack(fill="x", padx=6, pady=(6,6))

        # Start auto-refresh loop
        self._stop = False
        self._last_locked_mtime = None
        self._last_secret_mtime = None
        self.after(100, self.autorefresh_loop)

        self.log("Teacher GUI started.")
        # Ensure backup dir exists
        os.makedirs(BACKUP_DIR, exist_ok=True)

    # ---------- File selection ----------
    def choose_locked_file(self):
        path = filedialog.askopenfilename(title="Select locked document file", initialfile=self.locked_file)
        if path:
            self.locked_file = path
            self.locked_label.config(text=self.locked_file)
            self.refresh_now()

    def choose_secret_file(self):
        path = filedialog.asksaveasfilename(title="Select secret PIN file", initialfile=self.secret_file)
        if path:
            self.secret_file = path
            self.secret_label.config(text=self.secret_file)
            self.update_file_times()

    # ---------- Core actions ----------
    def refresh_now(self):
        try:
            lines = self.load_locked_lines()
            self.listbox.delete(0, tk.END)
            for ln in lines:
                self.listbox.insert(tk.END, ln.rstrip())
            self.log(f"Refreshed list ({len(lines)} lines).")
            self.update_file_times()
        except Exception as e:
            self.log(f"Error refreshing: {e}")
            messagebox.showerror("Refresh Error", str(e))

    def load_locked_lines(self):
        if not os.path.exists(self.locked_file):
            return ["(locked file not found)"]
        with open(self.locked_file, "r", encoding="utf-8") as f:
            return f.readlines()

    def open_locked_file(self):
        if not os.path.exists(self.locked_file):
            messagebox.showinfo("Open file", "Locked file does not exist yet.")
            return
        try:
            if sys.platform.startswith("win"):
                os.startfile(self.locked_file)
            elif sys.platform == "darwin":
                subprocess.call(["open", self.locked_file])
            else:
                subprocess.call(["xdg-open", self.locked_file])
            self.log("Opened locked file in default editor.")
        except Exception as e:
            self.log(f"Failed to open file: {e}")
            messagebox.showerror("Open Error", str(e))

    def clear_locked_file(self):
        if messagebox.askyesno("Clear unlocked file", "This will erase the unlocked file contents. Continue?"):
            with open(self.locked_file, "w", encoding="utf-8") as f:
                f.write("")  # clear
            self.refresh_now()
            self.log("Cleared locked file.")

    def set_pin(self):
        new_pin = self.pin_var.get().strip()
        if new_pin == "":
            messagebox.showwarning("Empty PIN", "Please enter a PIN value before pressing Set PIN.")
            return
        # Backup current secret file if exists
        if os.path.exists(self.secret_file):
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            bname = os.path.join(BACKUP_DIR, f"secret_backup_{ts}.txt")
            try:
                with open(self.secret_file, "r", encoding="utf-8") as src, open(bname, "w", encoding="utf-8") as dst:
                    dst.write(src.read())
                self.log(f"Backed up existing pin to {bname}")
            except Exception as e:
                self.log(f"Failed to backup pin: {e}")
        # Write new pin
        try:
            with open(self.secret_file, "w", encoding="utf-8") as f:
                f.write(new_pin + "\n")
            self.log("New PIN written.")
            self.update_file_times()
        except Exception as e:
            self.log(f"Failed to write new PIN: {e}")
            messagebox.showerror("Write Error", str(e))

    def set_pin_and_clear(self):
        self.set_pin()
        # small delay then clear unlocked file
        self.clear_locked_file()

    # ---------- Auto-refresh loop ----------
    def autorefresh_loop(self):
        if self._stop:
            return
        try:
            changed = False
            if os.path.exists(self.locked_file):
                m = os.path.getmtime(self.locked_file)
                if self._last_locked_mtime is None or m != self._last_locked_mtime:
                    self._last_locked_mtime = m
                    changed = True
            if os.path.exists(self.secret_file):
                m2 = os.path.getmtime(self.secret_file)
                if self._last_secret_mtime is None or m2 != self._last_secret_mtime:
                    self._last_secret_mtime = m2
                    # don't set changed for listbox, but update label
                    self.update_file_times()
            if changed:
                # Refresh listbox contents without blocking UI
                self.refresh_now()
        except Exception as e:
            self.log(f"Autorefresh error: {e}")
        finally:
            self.after(REFRESH_MS, self.autorefresh_loop)

    def update_file_times(self):
        if os.path.exists(self.locked_file):
            m = os.path.getmtime(self.locked_file)
            self.locked_time_label.config(text=f"Locked file: {datetime.fromtimestamp(m)}")
        else:
            self.locked_time_label.config(text="Locked file: (not found)")
        if os.path.exists(self.secret_file):
            m2 = os.path.getmtime(self.secret_file)
            # Optionally show masked current pin length
            try:
                with open(self.secret_file, "r", encoding="utf-8") as f:
                    current_pin = f.read().strip()
                masked = ("*" * len(current_pin)) if current_pin else "(empty)"
            except Exception:
                masked = "(error reading)"
            self.secret_time_label.config(text=f"PIN file: {datetime.fromtimestamp(m2)}  ({masked})")
        else:
            self.secret_time_label.config(text="PIN file: (not found)")

    # ---------- Logging ----------
    def log(self, message: str):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{ts}] {message}\n"
        # append to text widget in a thread-safe way
        self.log_text.config(state="normal")
        self.log_text.insert("end", line)
        # trim
        content = self.log_text.get("1.0", "end-1c").splitlines()
        if len(content) > MAX_LOG_LINES:
            # keep last MAX_LOG_LINES
            new_content = "\n".join(content[-MAX_LOG_LINES:]) + "\n"
            self.log_text.delete("1.0", "end")
            self.log_text.insert("1.0", new_content)
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def on_close(self):
        self._stop = True
        self.destroy()

def main():
    app = TeacherGUI()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()

if __name__ == "__main__":
    main()
