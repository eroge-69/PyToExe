import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox

def split_files():
    folder = folder_path.get()
    try:
        files_per_folder = int(count_entry.get())
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid number.")
        return

    if not os.path.isdir(folder):
        messagebox.showerror("Error", "Invalid folder path.")
        return

    files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    if not files:
        messagebox.showinfo("Info", "No files found.")
        return

    for i in range(0, len(files), files_per_folder):
        group = i // files_per_folder + 1
        group_folder = os.path.join(folder, str(group))
        os.makedirs(group_folder, exist_ok=True)

        for f in files[i:i+files_per_folder]:
            shutil.move(os.path.join(folder, f), os.path.join(group_folder, f))

    messagebox.showinfo("Success", "Done!")

def browse_folder():
    folder = filedialog.askdirectory()
    folder_path.set(folder)

# GUI setup
root = tk.Tk()
root.title("Split Files into Folders")
root.geometry("400x150")
root.resizable(False, False)

folder_path = tk.StringVar()

tk.Label(root, text="Folder Path:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
tk.Entry(root, textvariable=folder_path, width=30).grid(row=0, column=1, padx=5)
tk.Button(root, text="Browse", command=browse_folder).grid(row=0, column=2)

tk.Label(root, text="Files per folder:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
count_entry = tk.Entry(root, width=10)
count_entry.grid(row=1, column=1, sticky="w")

tk.Button(root, text="Start", command=split_files).grid(row=2, column=1, pady=20)

root.mainloop()