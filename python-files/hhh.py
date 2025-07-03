import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import webbrowser
from PIL import Image, ImageTk
import datetime
import getpass


password = "security"


log_file_path = 'event_log.txt'

def log_event(action):
    """Log USB events to a file with timestamp and username."""
    username = getpass.getuser()
    time_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file_path, "a") as log_file:
        log_file.write(f"[{time_now}] Action: {action} | User: {username}\n")

def open_project_info():
    html_file_path = 'C:/Users/THAMARAI V/OneDrive/Documents/project_info.html'

    if os.path.isfile(html_file_path):
        webbrowser.open(f'file://{os.path.abspath(html_file_path)}')
    else:
        messagebox.showerror("Error", "Project Info file not found.")

def button1_clicked():
    password_window = tk.Toplevel(root)
    password_window.title("Enter Password")
    password_window.geometry("300x200")
    password_window.configure(bg="#ffffff")

    password_label = tk.Label(password_window, text="Enter Password:", bg="#ffffff")
    password_label.pack(pady=10)

    password_entry = tk.Entry(password_window, show="*")
    password_entry.pack(pady=5)

    def ok_button():
        if password_entry.get() == password:
            subprocess.run([r'C:/Users/THAMARAI V/OneDrive/Documents/block_usb.bat'], shell=True)
            password_window.destroy()
            success_label.config(text="USB Ports Disabled Successfully", fg="#008000")
            log_event("USB Ports Disabled")
        else:
            error_label.config(text="Incorrect password. Please try again.")
            password_entry.delete(0, tk.END)

    ok_button = tk.Button(password_window, text="OK", command=ok_button, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
    ok_button.pack(pady=10)

    error_label = tk.Label(password_window, text="", font=("Arial", 12), fg="#ff0000", bg="#ffffff")
    error_label.pack()

def button2_clicked():
    password_window = tk.Toplevel(root)
    password_window.title("Enter Password")
    password_window.geometry("300x200")
    password_window.configure(bg="#ffffff")

    password_label = tk.Label(password_window, text="Enter Password:", bg="#ffffff")
    password_label.pack(pady=10)

    password_entry = tk.Entry(password_window, show="*")
    password_entry.pack(pady=5)

    def ok_button():
        if password_entry.get() == password:
            subprocess.run([r'C:/Users/THAMARAI V/OneDrive/Documents/unblock_usb.bat'], shell=True)
            password_window.destroy()
            success_label.config(text="USB Ports Enabled Successfully", fg="#008000")
            log_event("USB Ports Enabled")
        else:
            error_label.config(text="Incorrect password. Please try again.")
            password_entry.delete(0, tk.END)

    ok_button = tk.Button(password_window, text="OK", command=ok_button, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
    ok_button.pack(pady=10)

    error_label = tk.Label(password_window, text="", font=("Arial", 12), fg="#ff0000", bg="#ffffff")
    error_label.pack()

def on_enter(e, btn):
    btn['background'] = '#555555'

def on_leave(e, btn):
    btn['background'] = e.widget.default_bg


root = tk.Tk()
root.title("USB Physical Security")
root.geometry("1440x800")


background_image_path = "C:/Users/THAMARAI V/OneDrive/Documents/wallpaper.png"
background_image = Image.open(background_image_path)
background_photo = ImageTk.PhotoImage(background_image)

background_label = tk.Label(root, image=background_photo)
background_label.place(relwidth=1, relheight=1)
title_label = tk.Label(root, text="*USB PHYSICAL SECURITY FOR SYSTEMS*", font=("Arial", 19, "bold"), bg="#ffffff", fg="#000000")
title_label.pack(pady=20)


project_info_button = tk.Button(root, text="Project Info", command=open_project_info, bg="#2196F3", fg="white", font=("Arial", 14, "bold"))
project_info_button.pack(pady=20)

enable_button = tk.Button(root, text="Enable USB Ports", command=button2_clicked, bg="#4CAF50", fg="white", font=("Arial", 14, "bold"))
enable_button.pack(pady=20)

disable_button = tk.Button(root, text="Disable USB Ports", command=button1_clicked, bg="#f44336", fg="white", font=("Arial", 14, "bold"))
disable_button.pack(pady=20)


for btn in [project_info_button, enable_button, disable_button]:
    btn.default_bg = btn['background']
    btn.bind("<Enter>", lambda e, b=btn: on_enter(e, b))
    btn.bind("<Leave>", lambda e, b=btn: on_leave(e, b))


success_label = tk.Label(root, text="", font=("Arial", 12), bg="#ffffff")
success_label.pack(pady=10)


root.mainloop()