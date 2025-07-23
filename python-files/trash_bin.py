import tkinter as tk
from tkinter import filedialog, messagebox
import shutil
import os

TRASH_DIR = os.path.expanduser("~/.trash_bin")

if not os.path.exists(TRASH_DIR):
    os.makedirs(TRASH_DIR)

def trash_file():
    files = filedialog.askopenfilenames(title="Select files to trash")
    for f in files:
        try:
            shutil.move(f, TRASH_DIR)
        except Exception as e:
            messagebox.showerror("Error", f"Could not trash {f}.\n{e}")
    update_file_list()

def restore_file():
    selected = listbox.get(tk.ACTIVE)
    if not selected:
        return
    full_path = os.path.join(TRASH_DIR, selected)
    original_path = filedialog.askdirectory(title="Select folder to restore to")
    if original_path:
        try:
            shutil.move(full_path, os.path.join(original_path, selected))
        except Exception as e:
            messagebox.showerror("Error", f"Could not restore {selected}.\n{e}")
        update_file_list()

def empty_trash():
    confirm = messagebox.askyesno("Confirm", "Are you sure you want to permanently delete all trashed files?")
    if confirm:
        for f in os.listdir(TRASH_DIR):
            try:
                os.remove(os.path.join(TRASH_DIR, f))
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete {f}.\n{e}")
        update_file_list()

def update_file_list():
    listbox.delete(0, tk.END)
    for file in os.listdir(TRASH_DIR):
        listbox.insert(tk.END, file)

root = tk.Tk()
root.title("Trash Bin")
root.geometry("300x400")
root.resizable(False, False)

tk.Label(root, text="🗑️ Trash Bin", font=("Arial", 16)).pack(pady=10)
tk.Button(root, text="🗑️ Trash File", command=trash_file).pack(pady=5)
tk.Button(root, text="♻️ Restore File", command=restore_file).pack(pady=5)
tk.Button(root, text="🔥 Empty Trash", command=empty_trash).pack(pady=5)

listbox = tk.Listbox(root, width=40)
listbox.pack(pady=10)

update_file_list()
root.mainloop()
