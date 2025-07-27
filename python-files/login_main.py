import tkinter as tk
from tkinter import messagebox
import re

# ትክክለኛ የusername እና password
USERNAME = "beni@beni.com"
PASSWORD = "1XVBENI72"

# የፓስወርዱ አስፈላጊ ቅድመ ሁኔታ
def is_strong_password(pw):
    pattern = r'^[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{};:"\\|,.<>/?]+$'
    return bool(re.match(pattern, pw))

# GUI መጀመሪያ
root = tk.Tk()
root.title("BENI WORLD USER Login")
root.geometry("400x300")
root.configure(bg="black")

tk.Label(root, text="BENI WORLD USER Login", font=("Arial", 16, "bold"), fg="white", bg="black").pack(pady=10)

tk.Label(root, text="Username:", fg="white", bg="black").pack()
entry_username = tk.Entry(root)
entry_username.pack(pady=5)

tk.Label(root, text="Password:", fg="white", bg="black").pack()
entry_password = tk.Entry(root, show="*")
entry_password.pack(pady=5)

def login():
    user = entry_username.get()
    pw = entry_password.get()

    if not is_strong_password(pw):
        messagebox.showerror("Weak Password", "ፓስወርዱ ከሚፈቀዱ ፊደላት እና ምልክቶች ውጭ ነው።")
        return

    if user == USERNAME and pw == PASSWORD:
        messagebox.showinfo("Success", "እንኳን ደህና መጡ!")
        root.destroy()
        open_dashboard()
    else:
        messagebox.showerror("Login Failed", "የተሳሳተ መረጃ።")

btn_login = tk.Button(root, text="Login", command=login)
btn_login.pack(pady=10)

def open_dashboard():
    dash = tk.Tk()
    dash.title("BENI WORLD USER - Dashboard")
    dash.geometry("400x200")
    dash.configure(bg="navy")
    tk.Label(dash, text="Welcome to BENI WORLD USER", font=("Arial", 14), fg="white", bg="navy").pack(pady=50)
    dash.mainloop()

root.mainloop()
