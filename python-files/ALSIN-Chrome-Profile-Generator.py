import os
import sys
import subprocess
import customtkinter as ctk
from tkinter import messagebox
from win32com.client import Dispatch

# === Runtime path ===
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

# === UI Setup ===
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("ALSIN Chrome Profile Generator")
app.geometry("700x600")
app.minsize(500, 500)
app.grid_rowconfigure(2, weight=1)
app.grid_columnconfigure(0, weight=1)

# === Variables ===
start_var = ctk.StringVar(value="1")
prefix_var = ctk.StringVar(value="Profile ")
digits_var = ctk.StringVar(value="3")
count_var = ctk.StringVar(value="10")

# === Functions ===
def update_preview(*args):
    try:
        preview.configure(text=f"Preview: {prefix_var.get()}{str(int(start_var.get())).zfill(int(digits_var.get()))}")
    except:
        preview.configure(text="Preview: ...")

def create_shortcut(name, target, args):
    path = os.path.join(BASE_DIR, f"{name}.lnk")
    shell = Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(path)
    shortcut.Targetpath = target
    shortcut.Arguments = args
    shortcut.WorkingDirectory = os.path.dirname(target)
    shortcut.save()
    return path

def launch_chrome(profile_path):
    try:
        subprocess.Popen([CHROME_PATH, f'--user-data-dir={profile_path}'])
    except Exception as e:
        messagebox.showerror("Error", str(e))

def generate_profiles():
    try:
        count = int(count_var.get())
        prefix = prefix_var.get()
        digits = int(digits_var.get())
        start = int(start_var.get())

        for widget in result_frame.winfo_children():
            widget.destroy()

        for i in range(count):
            profile_name = f"{prefix}{str(start + i).zfill(digits)}"

            # ✅ Create unique profile folder
            profile_path = os.path.join(BASE_DIR, "Profiles", profile_name)
            os.makedirs(profile_path, exist_ok=True)

            # ✅ Use user-data-dir for real saved profile
            args = f'--user-data-dir="{profile_path}"'

            # ✅ Create shortcut
            create_shortcut(profile_name, CHROME_PATH, args)

            # UI Row
            row = ctk.CTkFrame(result_frame)
            row.pack(fill="x", padx=10, pady=4)

            label = ctk.CTkLabel(row, text=profile_name, anchor="w")
            label.pack(side="left", padx=(5, 10), fill="x", expand=True)

            open_btn = ctk.CTkButton(row, text="▶", width=40, height=28,
                                     command=lambda p=profile_path: launch_chrome(p))
            open_btn.pack(side="right", padx=5)

        messagebox.showinfo("Done", f"{count} Chrome profiles created and saved in:\n{os.path.join(BASE_DIR, 'Profiles')}")

    except Exception as e:
        messagebox.showerror("Error", str(e))

# === Top Input Frame ===
input_frame = ctk.CTkFrame(app)
input_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
input_frame.grid_columnconfigure(1, weight=1)

fields = [
    ("Start Number", start_var),
    ("Prefix", prefix_var),
    ("Digits", digits_var),
    ("# of Profiles", count_var),
]

for i, (label_text, var) in enumerate(fields):
    label = ctk.CTkLabel(input_frame, text=label_text)
    label.grid(row=i, column=0, padx=5, pady=5, sticky="e")

    entry = ctk.CTkEntry(input_frame, textvariable=var)
    entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
    entry.bind("<KeyRelease>", update_preview)

# === Preview + Generate Button ===
preview = ctk.CTkLabel(app, text="Preview: Profile 001", font=("Segoe UI", 12, "italic"))
preview.grid(row=1, column=0, sticky="n", pady=(0, 10))

generate_btn = ctk.CTkButton(app, text="🚀 Generate Chrome Profiles", command=generate_profiles, height=40)
generate_btn.grid(row=1, column=0, sticky="s", pady=(40, 10))

# === Result Frame Scroll Area ===
result_label = ctk.CTkLabel(app, text="Profiles:", font=("Segoe UI", 13))
result_label.grid(row=2, column=0, sticky="n", pady=(10, 0))

result_frame = ctk.CTkScrollableFrame(app)
result_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 20))

update_preview()
app.mainloop()
