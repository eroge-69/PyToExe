
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import ctypes

def hide_folder(path):
    try:
        os.system(f'attrib +h +s "{path}"')
        messagebox.showinfo("Success", "Folder hidden successfully!")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def unhide_folder(path):
    try:
        os.system(f'attrib -h -s "{path}"')
        messagebox.showinfo("Success", "Folder unhidden successfully!")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def lock_folder(path):
    try:
        os.rename(path, path + ".locked")
        messagebox.showinfo("Success", "Folder locked (renamed)!")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def unlock_folder(path):
    try:
        if path.endswith(".locked"):
            os.rename(path, path.replace(".locked", ""))
            messagebox.showinfo("Success", "Folder unlocked!")
        else:
            messagebox.showwarning("Warning", "This folder does not appear to be locked.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def select_folder():
    folder_path = filedialog.askdirectory()
    folder_entry.delete(0, tk.END)
    folder_entry.insert(0, folder_path)

def hide():
    path = folder_entry.get()
    hide_folder(path)

def unhide():
    path = folder_entry.get()
    unhide_folder(path)

def lock():
    path = folder_entry.get()
    lock_folder(path)

def unlock():
    path = folder_entry.get()
    unlock_folder(path)

root = tk.Tk()
root.title("Sagar Folder Locker - GUI")

folder_entry = tk.Entry(root, width=50)
folder_entry.grid(row=0, column=0, padx=10, pady=10, columnspan=3)

browse_btn = tk.Button(root, text="Browse", command=select_folder)
browse_btn.grid(row=0, column=3, padx=10)

hide_btn = tk.Button(root, text="Hide", command=hide)
hide_btn.grid(row=1, column=0, padx=10, pady=10)

unhide_btn = tk.Button(root, text="Unhide", command=unhide)
unhide_btn.grid(row=1, column=1, padx=10, pady=10)

lock_btn = tk.Button(root, text="Lock", command=lock)
lock_btn.grid(row=1, column=2, padx=10, pady=10)

unlock_btn = tk.Button(root, text="Unlock", command=unlock)
unlock_btn.grid(row=1, column=3, padx=10, pady=10)

root.mainloop()
