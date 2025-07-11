import os
import tkinter as tk
from tkinter import filedialog, messagebox

def rename_files(base_name, directory):
    """
    Renames all files in the specified directory by adding sequential numbers
    to the base name, preserving original extensions.
    """
    if not base_name:
        messagebox.showerror("Error", "Base name cannot be empty.")
        return

    if not os.path.isdir(directory):
        messagebox.showerror("Error", "Invalid directory.")
        return

    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    
    if not files:
        messagebox.showinfo("Info", "No files found in the directory.")
        return

    files.sort()
    
    renamed_count = 0
    for i, filename in enumerate(files, start=1):
        _, ext = os.path.splitext(filename)
        new_name = f"{base_name}{i}{ext}"
        old_path = os.path.join(directory, filename)
        new_path = os.path.join(directory, new_name)
        
        try:
            os.rename(old_path, new_path)
            renamed_count += 1
        except Exception as e:
            messagebox.showerror("Error", f"Failed to rename {filename}: {str(e)}")
    
    messagebox.showinfo("Success", f"Renamed {renamed_count} files successfully.")

def browse_directory():
    dir_path = filedialog.askdirectory()
    if dir_path:
        directory_var.set(dir_path)

def start_rename():
    base_name = base_name_entry.get().strip()
    directory = directory_var.get()
    rename_files(base_name, directory)

# Create the main window
root = tk.Tk()
root.title("File Renamer")
root.geometry("400x200")

# Base name input
tk.Label(root, text="Base Name:").pack(pady=5)
base_name_entry = tk.Entry(root, width=50)
base_name_entry.pack()

# Directory selection
tk.Label(root, text="Directory:").pack(pady=5)
directory_var = tk.StringVar()
directory_entry = tk.Entry(root, textvariable=directory_var, width=50)
directory_entry.pack()
browse_button = tk.Button(root, text="Browse", command=browse_directory)
browse_button.pack(pady=5)

# Rename button
rename_button = tk.Button(root, text="Rename Files", command=start_rename)
rename_button.pack(pady=10)

# Run the GUI
root.mainloop()