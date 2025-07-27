
import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os
from datetime import datetime, timedelta

DATA_FILE = "id_timers.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            for id_, value in data.items():
                if value["start_time"]:
                    value["start_time"] = datetime.strptime(value["start_time"], "%Y-%m-%d %H:%M:%S")
            return data
    return {}

def save_data(data):
    serializable_data = {
        k: {
            "start_time": v["start_time"].strftime("%Y-%m-%d %H:%M:%S") if v["start_time"] else None
        }
        for k, v in data.items()
    }
    with open(DATA_FILE, "w") as f:
        json.dump(serializable_data, f)

class IDTimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ID Timer Tracker")
        self.data = load_data()

        self.frame = tk.Frame(root)
        self.frame.pack(padx=10, pady=10)

        self.add_button = tk.Button(root, text="➕ Add New ID", command=self.add_id)
        self.add_button.pack(pady=(0, 10))

        self.refresh_ui()
        self.root.after(60000, self.check_timers)

    def add_id(self):
        id_name = simpledialog.askstring("Add ID", "Enter ID name or number:")
        if id_name:
            if id_name in self.data:
                messagebox.showwarning("Exists", "This ID already exists.")
                return
            self.data[id_name] = {"start_time": None}
            save_data(self.data)
            self.refresh_ui()

    def refresh_ui(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

        for idx, (id_name, info) in enumerate(self.data.items()):
            frame = tk.Frame(self.frame, bd=1, relief="solid", padx=10, pady=5)
            frame.grid(row=idx, column=0, sticky="we", pady=5)

            tk.Label(frame, text=f"ID: {id_name}", width=20, anchor="w").grid(row=0, column=0)

            if info["start_time"]:
                elapsed = datetime.now() - info["start_time"]
                remaining = timedelta(hours=24) - elapsed
                if remaining.total_seconds() > 0:
                    status = f"Running - {str(remaining).split('.')[0]}"
                    color = "green"
                else:
                    status = "Expired"
                    color = "red"
            else:
                status = "Not started"
                color = "gray"

            tk.Label(frame, text=status, fg=color, width=25).grid(row=0, column=1)

            btn_text = "Start Timer" if not info["start_time"] or status == "Expired" else "Reset Timer"
            action_btn = tk.Button(frame, text=btn_text, command=lambda id_name=id_name: self.start_timer(id_name))
            action_btn.grid(row=0, column=2, padx=10)

    def start_timer(self, id_name):
        self.data[id_name]["start_time"] = datetime.now()
        save_data(self.data)
        self.refresh_ui()

    def check_timers(self):
        self.refresh_ui()
        self.root.after(60000, self.check_timers)

if __name__ == "__main__":
    root = tk.Tk()
    app = IDTimerApp(root)
    root.mainloop()
