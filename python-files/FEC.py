import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sys

if sys.platform.startswith("win"):
    import ctypes
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

def select_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        entry_file.delete(0, tk.END)
        entry_file.insert(0, file_path)

def rename_extension():
    file_path = entry_file.get()
    new_ext = entry_extension.get().strip()

    if not file_path or not new_ext:
        messagebox.showwarning("Missing Info", "Please select a file and enter a new extension.")
        return

    if not new_ext.startswith('.'):
        new_ext = '.' + new_ext

    base = os.path.splitext(file_path)[0]
    new_file_path = base + new_ext

    try:
        os.rename(file_path, new_file_path)
        messagebox.showinfo("Success", f"File renamed to:\n{new_file_path}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# GUI setup
root = tk.Tk()
root.title("FEC")
root.geometry("420x200")
root.resizable(False, False)

# Set custom icon (make sure 'icon.ico' exists in the same folder as the script)
root.iconphoto(False, tk.PhotoImage(file="icon.png"))  # can be PNG or GIF

style = ttk.Style(root)
style.theme_use("clam")

# Widgets
frame = ttk.Frame(root, padding=20)
frame.pack(fill='both', expand=True)

ttk.Label(frame, text="Selected File:").grid(row=0, column=0, sticky="w")
entry_file = ttk.Entry(frame, width=45)
entry_file.grid(row=1, column=0, pady=5, sticky="we")
ttk.Button(frame, text="Browse", command=select_file).grid(row=1, column=1, padx=5)

ttk.Label(frame, text="New Extension (e.g., .txt):").grid(row=2, column=0, columnspan=2, sticky="w", pady=(15, 0))
entry_extension = ttk.Entry(frame, width=20)
entry_extension.grid(row=3, column=0, pady=5, sticky="w")

ttk.Button(frame, text="Rename Extension", command=rename_extension).grid(row=4, column=0, columnspan=2, pady=15)

root.mainloop()

