
import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime
import pytz
import json
import os
import threading
import time

DATA_FILE = "utility_data.json"

data = {
    "reminders": [
        {"name": "John - Payment", "date": "2025-07-15"},
        {"name": "Anna - Invoice", "date": "2025-07-20"}
    ],
    "tasks": [
        "Edit video for Raj",
        "Website update for client"
    ]
}

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    else:
        return data

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def check_reminders():
    today = datetime.now().strftime("%Y-%m-%d")
    due_today = [r["name"] for r in data["reminders"] if r["date"] == today]
    if due_today:
        messagebox.showinfo("Reminder", "Reminders due today:\n" + "\n".join(due_today))

def start_reminder_check_loop():
    def loop():
        while True:
            time.sleep(1800)
            check_reminders()
    threading.Thread(target=loop, daemon=True).start()

def update_time():
    china_time = datetime.now(pytz.timezone("Asia/Shanghai")).strftime("%H:%M:%S")
    italy_time = datetime.now(pytz.timezone("Europe/Rome")).strftime("%H:%M:%S")
    china_label.config(text=f"🇨🇳 China Time: {china_time}")
    italy_label.config(text=f"🇮🇹 Italy Time: {italy_time}")
    root.after(1000, update_time)

def add_reminder():
    name = simpledialog.askstring("Add Reminder", "Enter name and reason:")
    date = simpledialog.askstring("Add Reminder", "Enter due date (YYYY-MM-DD):")
    if name and date:
        data["reminders"].append({"name": name, "date": date})
        update_lists()
        save_data()

def add_task():
    task = simpledialog.askstring("Add Task", "Enter task:")
    if task:
        data["tasks"].append(task)
        update_lists()
        save_data()

def update_lists():
    reminder_listbox.delete(0, tk.END)
    for r in data["reminders"]:
        reminder_listbox.insert(tk.END, f"{r['name']} - {r['date']}")
    task_listbox.delete(0, tk.END)
    for t in data["tasks"]:
        task_listbox.insert(tk.END, t)

def delete_selected(lb, data_key):
    selected = lb.curselection()
    if selected:
        index = selected[0]
        del data[data_key][index]
        update_lists()
        save_data()

def toggle_ontop():
    state = root.attributes("-topmost")
    root.attributes("-topmost", not state)

root = tk.Tk()
root.title("🧠 My Utility App")
root.geometry("400x600")
root.configure(bg="#1e1e1e")
root.attributes("-topmost", True)

fg_color = "#ffffff"
bg_color = "#1e1e1e"
btn_color = "#2d2d30"

china_label = tk.Label(root, text="", font=("Segoe UI", 12), fg=fg_color, bg=bg_color)
china_label.pack(pady=(10, 0))

italy_label = tk.Label(root, text="", font=("Segoe UI", 12), fg=fg_color, bg=bg_color)
italy_label.pack(pady=(0, 20))

tk.Label(root, text="💵 Payment Reminders:", font=("Segoe UI", 10, "bold"), fg=fg_color, bg=bg_color).pack()
reminder_listbox = tk.Listbox(root, height=6, width=40, bg=bg_color, fg=fg_color)
reminder_listbox.pack(pady=5)
tk.Button(root, text="Add Reminder", command=add_reminder, bg=btn_color, fg=fg_color).pack()
tk.Button(root, text="Delete Selected Reminder", command=lambda: delete_selected(reminder_listbox, "reminders"), bg=btn_color, fg=fg_color).pack(pady=(0, 20))

tk.Label(root, text="📋 Tasks:", font=("Segoe UI", 10, "bold"), fg=fg_color, bg=bg_color).pack()
task_listbox = tk.Listbox(root, height=6, width=40, bg=bg_color, fg=fg_color)
task_listbox.pack(pady=5)
tk.Button(root, text="Add Task", command=add_task, bg=btn_color, fg=fg_color).pack()
tk.Button(root, text="Delete Selected Task", command=lambda: delete_selected(task_listbox, "tasks"), bg=btn_color, fg=fg_color).pack(pady=(0, 20))

tk.Button(root, text="💾 Save", command=save_data, bg=btn_color, fg=fg_color).pack(pady=(0, 10))
tk.Button(root, text="📌 Toggle Always-On-Top", command=toggle_ontop, bg=btn_color, fg=fg_color).pack()

data = load_data()
update_lists()
update_time()
check_reminders()
start_reminder_check_loop()
root.mainloop()
