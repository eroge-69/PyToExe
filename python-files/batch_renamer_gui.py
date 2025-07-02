import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

def rename_files():
    folder = folder_path.get()
    base = base_name.get()
    try:
        start = int(start_number.get())
    except ValueError:
        messagebox.showerror("Invalid Input", "Start number must be a number.")
        return

    if not folder or not base:
        messagebox.showerror("Missing Info", "Please fill in all fields.")
        return

    try:
        files = sorted([f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))])
        for i, filename in enumerate(files):
            ext = os.path.splitext(filename)[1]
            new_name = f"{base}{start + i}{ext}"
            os.rename(os.path.join(folder, filename), os.path.join(folder, new_name))
        messagebox.showinfo("Success", "Files renamed successfully!")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def browse_folder():
    selected = filedialog.askdirectory()
    folder_path.set(selected)

# GUI Setup
root = tk.Tk()
root.title("Batch File Renamer")

folder_path = tk.StringVar()
base_name = tk.StringVar()
start_number = tk.StringVar(value="1")

tk.Label(root, text="Selected Folder:").pack(pady=5)
tk.Entry(root, textvariable=folder_path, width=40).pack()

# If folder was passed from context menu
if len(sys.argv) > 1:
    folder_path.set(sys.argv[1])

tk.Button(root, text="Browse", command=browse_folder).pack(pady=5)

tk.Label(root, text="Base Name:").pack()
tk.Entry(root, textvariable=base_name).pack()

tk.Label(root, text="Start Number:").pack()
tk.Entry(root, textvariable=start_number).pack()

tk.Button(root, text="Rename Files", command=rename_files, bg="lightblue").pack(pady=10)

root.mainloop()
