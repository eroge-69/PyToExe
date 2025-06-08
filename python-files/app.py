Python 3.11.0 (main, Oct 24 2022, 18:26:48) [MSC v.1933 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
import tkinter as tk
from tkinter import messagebox
import webbrowser
import subprocess
from keyauth import api  # pip install keyauth

# Initialize KeyAuth
keyauth_app = api(
    name="dont delete really important",
    ownerid="EdmsTKiuld",
    secret="b8d2d04cd87757003cbcfd57a991ce2127117ace8d69343d71727d5bb553f72d",
    version="1.0"
)

# ----------------- LOGIN WINDOW ----------------- #
def show_login_window():
    login_root = tk.Tk()
    login_root.title("KeyAuth Login")
    login_root.geometry("300x200")
    login_root.resizable(False, False)

    tk.Label(login_root, text="Username:").pack(pady=5)
    username_entry = tk.Entry(login_root)
    username_entry.pack()

    tk.Label(login_root, text="Password:").pack(pady=5)
    password_entry = tk.Entry(login_root, show="*")
    password_entry.pack()

    def attempt_login():
        username = username_entry.get()
        password = password_entry.get()
        keyauth_app.login(username, password)
        if not keyauth_app.response.get("success", False):
            messagebox.showerror("Login Failed", keyauth_app.response.get('message', 'Unknown error'))
        else:
            login_root.destroy()
            show_main_gui()

    tk.Button(login_root, text="Login", command=attempt_login).pack(pady=20)
    login_root.mainloop()

# ----------------- MAIN GUI ----------------- #
def normal_clean():
    subprocess.Popen(r"C:\Users\Ken Kaneki\Downloads\NormalCleaner.exe")

def deep_clean():
    subprocess.Popen(r"C:\Path\To\DeepCleaner.exe")  # Update path

def disk_cleaner():
    subprocess.Popen(r"C:\Path\To\DiskCleaner.exe")  # Update path

def reg_trace_cleaner():
    subprocess.Popen(r"C:\Path\To\RegTraceCleaner.exe")  # Update path

def open_discord():
...     webbrowser.open("https://discord.gg/eqKcUuumbu")
... 
... def show_main_gui():
...     root = tk.Tk()
...     root.title("Winterz")
...     root.geometry("350x400")
...     root.configure(bg="black")
...     root.resizable(False, False)
... 
...     title = tk.Label(root, text="Winterz!", font=("Arial", 24, "bold"), fg="blue", bg="black")
...     title.pack(pady=20)
... 
...     def create_button(text, command):
...         return tk.Button(
...             root,
...             text=text,
...             font=("Arial", 12, "bold"),
...             fg="blue",
...             bg="white",
...             width=25,
...             relief="raised",
...             command=command
...         )
... 
...     create_button("1. Normal Clean", normal_clean).pack(pady=5)
...     create_button("2. Deep Clean", deep_clean).pack(pady=5)
...     create_button("3. Disk Cleaner", disk_cleaner).pack(pady=5)
...     create_button("4. Reg Trace Cleaner", reg_trace_cleaner).pack(pady=5)
...     create_button("5. Discord", open_discord).pack(pady=15)
... 
...     footer = tk.Label(root, text="Made by 1337Tuno", fg="blue", bg="black", font=("Arial", 8))
...     footer.pack(side="left", anchor="s", padx=10, pady=10)
... 
...     root.mainloop()
... 
... # ----------------- START ----------------- #
... show_login_window()
