import os
import json
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

CONFIG_FILE = "config.json"

# Danh sách nút
BUTTONS = ["Notepad", "Calculator", "Paint"]

# Hàm load config
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {btn: "" for btn in BUTTONS}

# Hàm lưu config
def save_config():
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

# Hàm mở chương trình
def open_program(key):
    path = config.get(key, "")
    if path and os.path.exists(path):
        try:
            subprocess.Popen(path)
        except Exception as e:
            messagebox.showerror("Error", f"Không thể mở {key}\n{e}")
    else:
        messagebox.showwarning("Chưa cài đặt", f"Đường dẫn cho '{key}' chưa được cài đặt!")

# Hàm chọn đường dẫn cho từng app
def select_path(key, entry):
    filepath = filedialog.askopenfilename(title=f"Chọn file cho {key}")
    if filepath:
        entry.delete(0, tk.END)
        entry.insert(0, filepath)
        config[key] = filepath

# Cửa sổ cài đặt đường dẫn
def open_settings():
    settings_win = ttk.Toplevel(root)
    settings_win.title("Cài đặt đường dẫn")
    settings_win.geometry("400x300")

    frame = ttk.Frame(settings_win, padding=10)
    frame.pack(fill=BOTH, expand=True)

    for key in BUTTONS:
        row = ttk.Frame(frame)
        row.pack(fill=X, pady=5)

        ttk.Label(row, text=key, width=12).pack(side=LEFT)
        entry = ttk.Entry(row)
        entry.pack(side=LEFT, fill=X, expand=True, padx=5)
        entry.insert(0, config.get(key, ""))

        btn_browse = ttk.Button(row, text="Chọn", command=lambda k=key, e=entry: select_path(k, e))
        btn_browse.pack(side=RIGHT)

    ttk.Button(frame, text="Lưu", bootstyle=SUCCESS, command=lambda: [save_config(), settings_win.destroy()]).pack(pady=10)

# Load cấu hình
config = load_config()

# Giao diện chính
root = ttk.Window(themename="superhero")
root.title("Ứng dụng Launcher")
root.geometry("400x250")

# Menu
menubar = tk.Menu(root)
root.config(menu=menubar)
settings_menu = tk.Menu(menubar, tearoff=0)
settings_menu.add_command(label="Cài đặt", command=open_settings)
menubar.add_cascade(label="Setting", menu=settings_menu)

# Tiêu đề
ttk.Label(root, text="Chọn ứng dụng để mở", font=("Segoe UI", 14)).pack(pady=20)

# Nút mở ứng dụng
for key in BUTTONS:
    ttk.Button(root, text=key, bootstyle=PRIMARY, command=lambda k=key: open_program(k)).pack(pady=5, fill=X, padx=50)

root.mainloop()
