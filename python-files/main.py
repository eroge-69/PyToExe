
import tkinter as tk
from tkinter import messagebox
import json
import os

def save_user(username, password, license_key):
    try:
        with open("keys.json", "r") as f:
            keys = json.load(f)
        if license_key not in keys:
            return False, "License key not found."
        if keys[license_key].get("user"):
            return False, "License key already used."
        keys[license_key]["user"] = username
        keys[license_key]["password"] = password
        with open("keys.json", "w") as f:
            json.dump(keys, f, indent=4)
        return True, "Registration successful."
    except Exception as e:
        return False, str(e)

def register_action():
    user = username_entry.get()
    pwd = password_entry.get()
    key = license_entry.get()
    if not all([user, pwd, key]):
        messagebox.showerror("Missing Info", "Please fill in all fields.")
        return
    ok, msg = save_user(user, pwd, key)
    if ok:
        if remember_var.get():
            with open("remember_me.txt", "w") as f:
                f.write(f"{user}\n{pwd}\n{key}")
        messagebox.showinfo("Success", msg)
        root.destroy()
        os.system("python login.py")
    else:
        messagebox.showerror("Failed", msg)

def cancel_action():
    root.destroy()

root = tk.Tk()
root.title("Register")
root.geometry("300x250")
root.configure(bg="black")

tk.Label(root, text="Username", fg="white", bg="black").pack(pady=(10,0))
username_entry = tk.Entry(root)
username_entry.pack()

tk.Label(root, text="Password", fg="white", bg="black").pack(pady=(10,0))
password_entry = tk.Entry(root, show="*")
password_entry.pack()

tk.Label(root, text="License Key", fg="white", bg="black").pack(pady=(10,0))
license_entry = tk.Entry(root)
license_entry.pack()

remember_var = tk.BooleanVar()
remember_check = tk.Checkbutton(root, text="Remember me", variable=remember_var, bg="black", fg="white", activebackground="black", activeforeground="white", selectcolor="black")
remember_check.pack(pady=5)

button_frame = tk.Frame(root, bg="black")
button_frame.pack(pady=10)

tk.Button(button_frame, text="OK", command=register_action, width=10).grid(row=0, column=0, padx=5)
tk.Button(button_frame, text="Cancel", command=cancel_action, width=10).grid(row=0, column=1, padx=5)

root.mainloop()


class MainLoaderUI:
    def __init__(self, username):
        self.root = tk.Tk()
        self.root.title("Decatur")
        self.root.geometry("700x500")

        # Menu bar
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        menubar.add_command(label="Help")
        self.root.config(menu=menubar)

        # Welcome and navigation
        tk.Label(self.root, text=f"Welcome {username}\nYou have 0 active subscriptions", anchor="w").pack(fill="x", padx=10, pady=5)

        container = tk.Frame(self.root)
        container.pack(fill="both", expand=True, padx=10, pady=5)

        # Left navigation
        nav_frame = tk.Frame(container, width=120)
        nav_frame.pack(side="left", fill="y")
        tk.Button(nav_frame, text="News", width=15).pack(pady=2)
        tk.Button(nav_frame, text="Cheats", width=15).pack(pady=2)
        tk.Button(nav_frame, text="Loaded", width=15).pack(pady=2)

        # News panel
        news_frame = tk.Frame(container)
        news_frame.pack(side="right", fill="both", expand=True)

        tk.Label(news_frame, text="News").pack(anchor="w")

        self.news_list = tk.Listbox(news_frame)
        self.news_list.pack(fill="both", expand=True)

        self.add_news_items()

        self.root.mainloop()

    def add_news_items(self):
        news_items = [
            "COD:BO6 re-enabled - Borderless or Windowed required",
            "Upgrade to Windows 11 when playing COD",
            "Hell Let Loose Update",
            "Framework Update",
            "Marvel Rivals Hack Available",
            "Artificial.Patchguard",
            "COD:BO6 available",
            "COD:BO6 Beta available",
            "COD:MWIII - Kernel Detection found and bypassed"
        ]
        for item in news_items:
            self.news_list.insert("end", item)

def launch_main_ui(username):
    MainLoaderUI(username)

if __name__ == "__main__":
    root = tk.Tk()
    app = LoginWindow(root, on_login=launch_main_ui)
    root.mainloop()
