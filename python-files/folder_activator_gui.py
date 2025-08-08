import os
import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime

def get_foldername_from_config(config_path):
    if not os.path.exists(config_path):
        return None
    with open(config_path, 'r') as f:
        for line in f:
            if line.startswith("foldername="):
                return line.strip().split("=", 1)[1]
    return None

def log_action(message):
    log_path = "C:/efts/folder_activator.log"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, 'a') as log_file:
        log_file.write(f"[{timestamp}] {message}\n")

def activate_folder():
    home_dir = "C:/efts/"
    hardcoded_folder_name = "atm"
    active_folder_path = os.path.join(home_dir, hardcoded_folder_name)

    # Step 1: If 'atm' exists, rename it back to its original name
    if os.path.exists(active_folder_path):
        active_config_path = os.path.join(active_folder_path, "atmirage_config.txt")
        original_name = get_foldername_from_config(active_config_path)
        if original_name:
            original_path = os.path.join(home_dir, original_name)
            try:
                os.rename(active_folder_path, original_path)
                log_action(f"Renamed existing 'atm' folder to '{original_name}'")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to rename existing 'atm' folder: {e}")
                log_action(f"Error renaming 'atm' folder: {e}")
                return

    # Step 2: Select new folder to activate
    selected_folder_path = filedialog.askdirectory(initialdir=home_dir, title="Select a folder to activate")
    if not selected_folder_path:
        return

    selected_config_path = os.path.join(selected_folder_path, "atmirage_config.txt")
    new_name = get_foldername_from_config(selected_config_path)
    if not new_name:
        messagebox.showerror("Error", f"'foldername=' not found in {selected_config_path}")
        log_action(f"Error: 'foldername=' not found in {selected_config_path}")
        return

    new_name_path = os.path.join(home_dir, new_name)

    try:
        # Rename selected folder to its configured name
        os.rename(selected_folder_path, new_name_path)
        log_action(f"Renamed selected folder to '{new_name}'")

        # Rename it again to 'atm' to activate
        os.rename(new_name_path, active_folder_path)
        log_action(f"Activated folder '{new_name}' as 'atm'")

        messagebox.showinfo("Success", f"Folder '{new_name}' activated successfully as '{hardcoded_folder_name}'")
    except Exception as e:
        messagebox.showerror("Error", str(e))
        log_action(f"Error during activation: {e}")

# Create GUI window
root = tk.Tk()
root.title("Folder Activator")
root.geometry("400x500")

label = tk.Label(root, text="Click the button to select folder for activation. \n it will\n 1. change the name of existing atm folder to the folder name specified in atmirage_config.txt foldername= \n 2. rename the selected folder to atm", wraplength=300)
label.pack(pady=20)

activate_button = tk.Button(root, text="Activate Folder", command=activate_folder)
activate_button.pack(pady=10)

root.mainloop()
