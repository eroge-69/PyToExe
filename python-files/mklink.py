import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

# Function to create symbolic link
def create_symlink(source_folder, dest_folder):
    try:
        # Run the mklink command
        command = f'mklink /D "{dest_folder}" "{source_folder}"'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        # Check if mklink command was successful
        if result.returncode == 0:
            log_message = f"mklink /D \"{dest_folder}\" \"{source_folder}\""
            log_to_file(log_message)
            messagebox.showinfo("Success", f"Symlink created:\n\n{source_folder}\n-> {dest_folder}")
        else:
            log_message = f"[ERROR] Failed to create symlink: {result.stderr}"
            log_to_file(log_message)
            messagebox.showerror("Error", f"Error: {result.stderr}")
    except Exception as e:
        log_message = f"[EXCEPTION] {str(e)}"
        log_to_file(log_message)
        messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

# Function to log the result to a text file
def log_to_file(message):
    log_file = "symlink_creation_log.bat"
    with open(log_file, "a") as log:
        log.write(message + "\n")

# Function to select the source folder
def select_source_folder():
    source_folder = filedialog.askdirectory(title="Select Source Folder")
    if source_folder:
        source_entry.delete(0, tk.END)
        source_entry.insert(0, source_folder)

# Function to select the destination folder
def select_dest_folder():
    dest_folder = filedialog.askdirectory(title="Select Destination Folder")
    if dest_folder:
        dest_entry.delete(0, tk.END)
        dest_entry.insert(0, dest_folder)

# Function to handle the 'Create Symlink' button click
def on_create_symlink():
    source_folder = source_entry.get()
    dest_folder = dest_entry.get()
    
    # Check if both source and destination folders are provided
    if not source_folder or not dest_folder:
        messagebox.showwarning("Input Error", "Please select both source and destination folders.")
        return
    
    # Create symlink
    create_symlink(source_folder, dest_folder)

# Create the main GUI window
root = tk.Tk()
root.title("Symlink Creator")

# Set window size
root.geometry("400x250")

# Source folder input
source_label = tk.Label(root, text="Source Folder:")
source_label.pack(pady=5)
source_entry = tk.Entry(root, width=40)
source_entry.pack(pady=5)
source_button = tk.Button(root, text="Browse", command=select_source_folder)
source_button.pack(pady=5)

# Destination folder input
dest_label = tk.Label(root, text="Destination Folder:")
dest_label.pack(pady=5)
dest_entry = tk.Entry(root, width=40)
dest_entry.pack(pady=5)
dest_button = tk.Button(root, text="Browse", command=select_dest_folder)
dest_button.pack(pady=5)

# Create Symlink button
create_button = tk.Button(root, text="Create Symlink", command=on_create_symlink)
create_button.pack(pady=20)

# Run the GUI application
root.mainloop()
