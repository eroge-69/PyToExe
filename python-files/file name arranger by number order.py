import os
import tkinter as tk
from tkinter import filedialog, messagebox

def rename_files():
    folder_path = path_var.get()

    if not folder_path or not os.path.exists(folder_path):
        messagebox.showerror("Error", "please select folder direction.")
        return

    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    files.sort()

    # مرحله 1: تغییر نام موقت
    for index, filename in enumerate(files, start=1):
        ext = os.path.splitext(filename)[1]
        temp_name = f"temp_{index}{ext}"
        os.rename(
            os.path.join(folder_path, filename),
            os.path.join(folder_path, temp_name)
        )

    # مرحله 2: تغییر نام نهایی
    temp_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    temp_files.sort()

    for index, filename in enumerate(temp_files, start=1):
        ext = os.path.splitext(filename)[1]
        new_name = f"{index}{ext}"
        os.rename(
            os.path.join(folder_path, filename),
            os.path.join(folder_path, new_name)
        )

    messagebox.showinfo("Succeeded", "Arranging succeeded.")

def select_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        path_var.set(folder_selected)

# ساخت پنجره
root = tk.Tk()
root.title("File Name Arranger By Number Order Program")
root.geometry("400x150")

path_var = tk.StringVar()

tk.Label(root, text="Folder direction:").pack(pady=5)
tk.Entry(root, textvariable=path_var, width=40).pack(pady=5)
tk.Button(root, text="Select folder", command=select_folder).pack(pady=5)
tk.Button(root, text="Start numbering", command=rename_files).pack(pady=10)

root.mainloop()
