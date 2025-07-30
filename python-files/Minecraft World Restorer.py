import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import shutil
import zipfile
import platform
import json

def get_minecraft_saves_dir():
    """Determine the Minecraft saves directory based on the operating system."""
    home = os.path.expanduser("~")
    if platform.system() == "Windows":
        return os.path.join(home, "AppData", "Roaming", ".minecraft", "saves")
    elif platform.system() == "Darwin":  # macOS
        return os.path.join(home, "Library", "Application Support", "minecraft", "saves")
    else:  # Linux
        return os.path.join(home, ".minecraft", "saves")

def load_saved_slots():
    """Load saved world and backup pairs from a JSON file."""
    try:
        with open("minecraft_restore_slots.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_slot(world_name, backup_path):
    """Save the world name and backup path to a JSON file."""
    slots = load_saved_slots()
    new_slot = {"world_name": world_name, "backup_path": backup_path}
    # Avoid duplicates
    if new_slot not in slots:
        slots.append(new_slot)
    with open("minecraft_restore_slots.json", "w") as f:
        json.dump(slots, f, indent=4)

def clear_slots():
    """Clear all saved slots by deleting the JSON file and updating the dropdown."""
    if os.path.exists("minecraft_restore_slots.json"):
        os.remove("minecraft_restore_slots.json")
    update_slot_dropdown()
    world_entry.delete(0, tk.END)
    backup_entry.delete(0, tk.END)
    messagebox.showinfo("Success", "All saved slots have been cleared.")

def restore_world():
    """Delete the current world and replace it with the backup from a zip file."""
    world_name = world_entry.get().strip()
    backup_zip = backup_entry.get().strip()

    if not world_name or not backup_zip:
        messagebox.showerror("Error", "Please provide both world name and backup zip path.")
        return

    saves_dir = get_minecraft_saves_dir()
    world_path = os.path.join(saves_dir, world_name)

    # Check if world exists
    if not os.path.exists(world_path):
        messagebox.showerror("Error", f"World folder '{world_name}' does not exist in {saves_dir}.")
        return

    # Check if backup zip exists
    if not os.path.exists(backup_zip) or not backup_zip.endswith(".zip"):
        messagebox.showerror("Error", "Please select a valid .zip backup file.")
        return

    try:
        # Delete current world folder
        shutil.rmtree(world_path)
        print(f"Deleted world folder: {world_path}")

        # Extract backup zip to saves directory
        with zipfile.ZipFile(backup_zip, 'r') as zip_ref:
            zip_ref.extractall(saves_dir)
        print(f"Restored world from: {backup_zip}")

        # Save the slot
        save_slot(world_name, backup_zip)
        update_slot_dropdown()
        messagebox.showinfo("Success", f"World '{world_name}' has been restored from backup.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to restore world: {str(e)}")

def browse_backup():
    """Open file dialog to select backup zip file."""
    file_path = filedialog.askopenfilename(filetypes=[("Zip files", "*.zip")])
    if file_path:
        backup_entry.delete(0, tk.END)
        backup_entry.insert(0, file_path)

def update_slot_dropdown():
    """Update the dropdown with saved slots, showing only world names."""
    slots = load_saved_slots()
    slot_dropdown['values'] = [slot['world_name'] for slot in slots]
    if slots:
        slot_dropdown.current(0)
        load_selected_slot()

def load_selected_slot(event=None):
    """Load the selected slot's world name and backup path into the entry fields."""
    selected = slot_dropdown.get()
    if selected:
        slots = load_saved_slots()
        for slot in slots:
            if slot['world_name'] == selected:
                world_entry.delete(0, tk.END)
                world_entry.insert(0, slot['world_name'])
                backup_entry.delete(0, tk.END)
                backup_entry.insert(0, slot['backup_path'])
                break

# Create GUI
root = tk.Tk()
root.title("Minecraft World Restorer")
root.geometry("400x280")

# Saved slots dropdown
tk.Label(root, text="Saved Slots:").pack(pady=5)
slot_dropdown = ttk.Combobox(root, width=50, state="readonly")
slot_dropdown.pack(pady=5)
slot_dropdown.bind("<<ComboboxSelected>>", load_selected_slot)

# Clear slots button
tk.Button(root, text="Clear All Slots", command=clear_slots).pack(pady=5)

# World name input
tk.Label(root, text="World Folder Name:").pack(pady=5)
world_entry = tk.Entry(root, width=40)
world_entry.pack(pady=5)

# Backup zip input
tk.Label(root, text="Backup Zip Path:").pack(pady=5)
backup_frame = tk.Frame(root)
backup_frame.pack(pady=5)
backup_entry = tk.Entry(backup_frame, width=30)
backup_entry.pack(side=tk.LEFT)
tk.Button(backup_frame, text="Browse", command=browse_backup).pack(side=tk.LEFT, padx=5)

# Restore button
tk.Button(root, text="Restore World", command=restore_world).pack(pady=20)

# Load saved slots and populate dropdown
update_slot_dropdown()

# Load last used slot if available
slots = load_saved_slots()
if slots:
    world_entry.insert(0, slots[-1]["world_name"])
    backup_entry.insert(0, slots[-1]["backup_path"])

# Start GUI
root.mainloop()