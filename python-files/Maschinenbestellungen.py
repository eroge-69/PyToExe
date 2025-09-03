import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox

# Function to copy files/folders and handle duplicates
def copy_with_overwrite(src, dst):
    if os.path.exists(dst):
        if os.path.isfile(dst):
            os.remove(dst)  # Remove the existing file
        elif os.path.isdir(dst):
            shutil.rmtree(dst)  # Remove the existing directory
    if os.path.isfile(src):
        shutil.copy2(src, dst)  # Copy file
    elif os.path.isdir(src):
        shutil.copytree(src, dst)  # Copy directory

# Function to reorganize folders
def reorganize_folders(source_folder, target_folder, text):
    # Define the main folder in the target directory
    main_folder = os.path.join(target_folder, text)
    categories = ["Laser", "Fertigung", "Rohrlaser", "Montage", "Schlosserei"]

    # Create the main folder if it doesn't exist
    if not os.path.exists(main_folder):
        os.makedirs(main_folder)

    # Create category folders inside the main folder with the input text appended
    for category in categories:
        category_folder_name = f"{category}-{text}"  # e.g., "Fertigung-IP - 2023 - 297 Powerjet 301-302"
        category_path = os.path.join(main_folder, category_folder_name)
        if not os.path.exists(category_path):
            os.makedirs(category_path)

    # Find all folders that match the pattern "<text> <group>"
    for folder_name in os.listdir(source_folder):
        if folder_name.startswith(text + " "):
            group_name = folder_name[len(text) + 1:]  # Extract the group name (e.g., "Bilderkennung")
            group_folder = os.path.join(source_folder, folder_name)
            if os.path.isdir(group_folder):
                # Copy contents from the group folder to the corresponding category folders
                for category in categories:
                    source_path = os.path.join(group_folder, category)
                    if os.path.exists(source_path):
                        category_folder_name = f"{category}-{text}"  # e.g., "Fertigung-IP - 2023 - 297 Powerjet 301-302"
                        destination_path = os.path.join(main_folder, category_folder_name, group_name)
                        # Create the group folder inside the category folder
                        if not os.path.exists(destination_path):
                            os.makedirs(destination_path)
                        # Copy all files and subdirectories from source to destination
                        for item in os.listdir(source_path):
                            item_path = os.path.join(source_path, item)
                            if os.path.isfile(item_path) or os.path.isdir(item_path):
                                try:
                                    copy_with_overwrite(item_path, os.path.join(destination_path, item))
                                except Exception as e:
                                    print(f"Error copying {item_path}: {e}")
                        print(f"Copied contents from {source_path} to {destination_path}")

    messagebox.showinfo("Success", "Folder reorganization completed! Source files were not deleted.")

# Function to handle the GUI button click
def on_submit():
    source_folder = source_folder_entry.get()
    target_folder = target_folder_entry.get()
    text = text_entry.get()

    if not source_folder or not target_folder or not text:
        messagebox.showerror("Error", "Please fill in all fields.")
        return

    reorganize_folders(source_folder, target_folder, text)

# Function to open a directory dialog for source folder
def browse_source_folder():
    folder = filedialog.askdirectory()
    source_folder_entry.delete(0, tk.END)
    source_folder_entry.insert(0, folder)

# Function to open a directory dialog for target folder
def browse_target_folder():
    folder = filedialog.askdirectory()
    target_folder_entry.delete(0, tk.END)
    target_folder_entry.insert(0, folder)

# Create the GUI
root = tk.Tk()
root.title("Folder Reorganizer")

# Source Folder
tk.Label(root, text="Source Folder:").grid(row=0, column=0, padx=10, pady=10)
source_folder_entry = tk.Entry(root, width=50)
source_folder_entry.grid(row=0, column=1, padx=10, pady=10)
tk.Button(root, text="Browse", command=browse_source_folder).grid(row=0, column=2, padx=10, pady=10)

# Target Folder
tk.Label(root, text="Target Folder:").grid(row=1, column=0, padx=10, pady=10)
target_folder_entry = tk.Entry(root, width=50)
target_folder_entry.grid(row=1, column=1, padx=10, pady=10)
tk.Button(root, text="Browse", command=browse_target_folder).grid(row=1, column=2, padx=10, pady=10)

# Text Input
tk.Label(root, text="Text (e.g., IP - 2023 - 297 Powerjet 301-302):").grid(row=2, column=0, padx=10, pady=10)
text_entry = tk.Entry(root, width=50)
text_entry.grid(row=2, column=1, padx=10, pady=10)

# Submit Button
tk.Button(root, text="Reorganize Folders", command=on_submit).grid(row=3, column=1, padx=10, pady=20)

# Run the GUI
root.mainloop()
