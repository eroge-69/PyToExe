import os
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

def install_whl_files():
    folder_path = filedialog.askdirectory(title="Select folder with .whl files")
    if not folder_path:
        return

    whl_files = [f for f in os.listdir(folder_path) if f.endswith(".whl")]
    if not whl_files:
        messagebox.showinfo("Info", "No .whl files found in the selected folder.")
        return

    # ترتیب نصب: preshed → thinc → بقیه
    priority = ["preshed", "thinc"]
    whl_files.sort(key=lambda x: 0 if any(p in x for p in priority) else 1)

    for whl in whl_files:
        file_path = os.path.join(folder_path, whl)
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", file_path])
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to install {whl}\n{e}")
            return

    messagebox.showinfo("Success", "All .whl files installed successfully!")

# رابط کاربری ساده
root = tk.Tk()
root.title("WHL Installer")
root.geometry("400x150")

install_button = tk.Button(root, text="Select Folder and Install .whl Files",
                           command=install_whl_files, width=40, height=3)
install_button.pack(pady=30)

root.mainloop()
