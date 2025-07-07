
import os
import time
import json
import threading
from tkinter import Tk, Label, Button, filedialog, Spinbox, IntVar, Checkbutton, messagebox

CONFIG_FILE = "config.json"
LOG_DIR = "logs"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {
        "folder": "",
        "days": 7,
        "interval": 60,
        "autostart": True,
        "logging": True
    }

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

def log_deletion(file_path):
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    log_file = os.path.join(LOG_DIR, "deleted_files.log")
    with open(log_file, "a") as f:
        f.write(f"{time.ctime()} - Deleted: {file_path}\n")

def delete_old_files(config):
    folder = config["folder"]
    days = config["days"]
    logging_enabled = config.get("logging", True)

    if not os.path.isdir(folder):
        return

    cutoff = time.time() - (days * 86400)
    for filename in os.listdir(folder):
        path = os.path.join(folder, filename)
        if os.path.isfile(path) and os.path.getmtime(path) < cutoff:
            try:
                os.remove(path)
                if logging_enabled:
                    log_deletion(path)
            except Exception as e:
                print(f"Error deleting {path}: {e}")

def start_deletion_thread(config):
    def run():
        while True:
            delete_old_files(config)
            time.sleep(config["interval"] * 60)
    threading.Thread(target=run, daemon=True).start()

class AutoDataWipeApp:
    def __init__(self, root):
        self.config = load_config()
        self.root = root
        root.title("Auto Data Wipe")

        Label(root, text="Folder to clean:").pack()
        self.folder_label = Label(root, text=self.config["folder"], wraplength=400)
        self.folder_label.pack()

        Button(root, text="Select Folder", command=self.select_folder).pack()

        Label(root, text="Delete files older than (days):").pack()
        self.days_spin = Spinbox(root, from_=1, to=365, width=5)
        self.days_spin.pack()
        self.days_spin.delete(0, "end")
        self.days_spin.insert(0, self.config["days"])

        Label(root, text="Check interval (minutes):").pack()
        self.interval_spin = Spinbox(root, from_=5, to=1440, width=5)
        self.interval_spin.pack()
        self.interval_spin.delete(0, "end")
        self.interval_spin.insert(0, self.config["interval"])

        self.autostart_var = IntVar(value=int(self.config.get("autostart", 1)))
        Checkbutton(root, text="Start with Windows", variable=self.autostart_var).pack()

        self.logging_var = IntVar(value=int(self.config.get("logging", 1)))
        Checkbutton(root, text="Enable Logging", variable=self.logging_var).pack()

        Button(root, text="Save & Start", command=self.save_and_start).pack()
        Button(root, text="Exit", command=root.quit).pack()

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_label.config(text=folder)
            self.config["folder"] = folder

    def save_and_start(self):
        self.config["days"] = int(self.days_spin.get())
        self.config["interval"] = int(self.interval_spin.get())
        self.config["autostart"] = bool(self.autostart_var.get())
        self.config["logging"] = bool(self.logging_var.get())
        save_config(self.config)
        start_deletion_thread(self.config)
        messagebox.showinfo("Started", "Auto deletion started in background.")

if __name__ == "__main__":
    root = Tk()
    app = AutoDataWipeApp(root)
    root.mainloop()


