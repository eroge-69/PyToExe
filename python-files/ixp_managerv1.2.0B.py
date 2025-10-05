import shutil
import os
import json
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, scrolledtext, colorchooser

# --- Define paths dynamically ---
home_dir = Path.home()
roblox_dir = home_dir / "AppData" / "Local" / "Roblox" / "ClientSettings"
fishstrap_dir = home_dir / "AppData" / "Local" / "Fishstrap" / "Modifications" / "ClientSettings"
filename = "IxpSettings.json"

roblox_path = roblox_dir / filename
fishstrap_path = fishstrap_dir / filename
client_settings_path = fishstrap_dir / "ClientAppSettings.json"

# --- Themes ---
themes = {
    "Light": {
        "bg": "#f0f0f0", "fg": "#000000",
        "text_bg": "#ffffff", "text_fg": "#000000",
        "button_bg": "#e0e0e0", "button_fg": "#000000",
    },
    "Dark": {
        "bg": "#212326", "fg": "#ffffff",
        "text_bg": "#2c2f33", "text_fg": "#f8f8f8",
        "button_bg": "#444444", "button_fg": "#ffffff",
    },
    "Blue": {
        "bg": "#dce9f9", "fg": "#000033",
        "text_bg": "#eaf2fc", "text_fg": "#001144",
        "button_bg": "#a7c7f2", "button_fg": "#000033",
    },
    "Green": {
        "bg": "#e5f5e0", "fg": "#003300",
        "text_bg": "#f0fff0", "text_fg": "#003300",
        "button_bg": "#a7e9af", "button_fg": "#003300",
    }
}
current_theme = "Light"

# --- File management functions ---
def get_current_file_path():
    if fishstrap_path.exists():
        return fishstrap_path
    elif roblox_path.exists():
        return roblox_path
    return None

def load_file_content():
    """Loads IxpSettings.json into editor."""
    current_path = get_current_file_path()
    text_widget.delete('1.0', tk.END)
    if current_path:
        try:
            with open(current_path, 'r', encoding='utf-8') as f:
                content = f.read()
                text_widget.insert('1.0', content)
            messagebox.showinfo("Loaded", f"Loaded content from {current_path.name}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not load file: {e}")
    else:
        messagebox.showwarning("File Not Found", f"{filename} not found in either location.")

def save_file_content():
    """Saves editor content to active IxpSettings.json."""
    current_path = get_current_file_path()
    if current_path:
        try:
            content = text_widget.get('1.0', tk.END)
            with open(current_path, 'w', encoding='utf-8') as f:
                f.write(content)
            messagebox.showinfo("Saved", f"Changes saved to {current_path.name} successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {e}")
    else:
        messagebox.showwarning("File Not Found", "No file is active to save changes to.")

def move_file():
    """Moves IxpSettings.json from Roblox to Fishstrap."""
    fishstrap_dir.mkdir(parents=True, exist_ok=True)
    if roblox_path.exists():
        try:
            os.chmod(roblox_path, 0o666)  # remove read-only if set
            shutil.move(roblox_path, fishstrap_path)
            messagebox.showinfo("Success", "IxpSettings.json moved to Fishstrap successfully!")
            load_file_content()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to move file: {e}")
    else:
        messagebox.showwarning("File Not Found", "File not found in Roblox folder.")

def restore_file():
    """Restores IxpSettings.json back to Roblox (keeps current read-only state)."""
    if fishstrap_path.exists():
        try:
            shutil.move(fishstrap_path, roblox_path)
            messagebox.showinfo("Success", "IxpSettings.json restored to Roblox successfully!")
            load_file_content()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to restore file: {e}")
    else:
        messagebox.showwarning("File Not Found", "File not found in Fishstrap folder.")

def toggle_read_only():
    """Toggle read-only attribute on Roblox IxpSettings.json."""
    if roblox_path.exists():
        try:
            if os.access(roblox_path, os.W_OK):  # currently writable
                os.chmod(roblox_path, 0o444)     # make read-only
                messagebox.showinfo("Read-Only", "IxpSettings.json set to READ-ONLY.")
            else:
                os.chmod(roblox_path, 0o666)     # make writable
                messagebox.showinfo("Read-Only", "IxpSettings.json set to WRITABLE.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to toggle read-only: {e}")
    else:
        messagebox.showwarning("File Not Found", "Roblox IxpSettings.json not found.")

def import_client_settings():
    """Load ClientAppSettings.json into editor."""
    if client_settings_path.exists():
        try:
            with open(client_settings_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            formatted = json.dumps(data, indent=4)
            text_widget.delete('1.0', tk.END)
            text_widget.insert('1.0', formatted)
            messagebox.showinfo("Imported", "ClientAppSettings.json loaded into editor.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not load ClientAppSettings.json: {e}")
    else:
        messagebox.showwarning("Not Found", "ClientAppSettings.json not found in Fishstrap.")

# --- Theme functions ---
def apply_theme(theme_name, custom_data=None):
    global current_theme
    current_theme = theme_name
    theme = custom_data if custom_data else themes[theme_name]

    root.config(bg=theme["bg"])
    top_frame.config(bg=theme["bg"])
    bottom_frame.config(bg=theme["bg"])
    edit_frame.config(bg=theme["bg"])

    text_widget.config(bg=theme["text_bg"], fg=theme["text_fg"], insertbackground=theme["fg"])
    for btn in (move_button, restore_button, toggle_button, import_button, load_button, save_button):
        btn.config(bg=theme["button_bg"], fg=theme["button_fg"], activebackground=theme["bg"])

def open_custom_theme_editor():
    editor = tk.Toplevel(root)
    editor.title("Custom Theme Editor")

    labels = ["Background", "Foreground", "Text BG", "Text FG", "Button BG", "Button FG"]
    keys = ["bg", "fg", "text_bg", "text_fg", "button_bg", "button_fg"]
    entries = {}

    def pick_color(key):
        color = colorchooser.askcolor()[1]
        if color:
            entries[key].delete(0, tk.END)
            entries[key].insert(0, color)

    for i, (label, key) in enumerate(zip(labels, keys)):
        tk.Label(editor, text=label).grid(row=i, column=0, padx=5, pady=5, sticky="w")
        entry = tk.Entry(editor, width=10)
        entry.grid(row=i, column=1, padx=5, pady=5)
        entries[key] = entry
        tk.Button(editor, text="Pick", command=lambda k=key: pick_color(k)).grid(row=i, column=2, padx=5, pady=5)

    def apply_custom():
        custom = {k: entries[k].get() or "#ffffff" for k in keys}
        apply_theme("Custom", custom)
        editor.destroy()

    tk.Button(editor, text="Apply Custom Theme", command=apply_custom).grid(row=len(labels), columnspan=3, pady=10)

# --- GUI setup ---
root = tk.Tk()
root.title("IxpSettings Manager and Editor")
root.geometry("750x550")

# Menu bar with Themes
menubar = tk.Menu(root)
theme_menu = tk.Menu(menubar, tearoff=0)
for t in themes.keys():
    theme_menu.add_command(label=t, command=lambda name=t: apply_theme(name))
theme_menu.add_separator()
theme_menu.add_command(label="Custom Theme...", command=open_custom_theme_editor)
menubar.add_cascade(label="Themes", menu=theme_menu)
root.config(menu=menubar)

# --- Top Frame for file manipulation buttons ---
top_frame = tk.Frame(root)
top_frame.pack(pady=10)

move_button = tk.Button(top_frame, text="Move to Fishstrap", command=move_file)
move_button.pack(side=tk.LEFT, padx=10)

restore_button = tk.Button(top_frame, text="Restore to Roblox", command=restore_file)
restore_button.pack(side=tk.LEFT, padx=10)

toggle_button = tk.Button(top_frame, text="Toggle Read-Only", command=toggle_read_only)
toggle_button.pack(side=tk.LEFT, padx=10)

import_button = tk.Button(top_frame, text="Import JSON", command=import_client_settings)
import_button.pack(side=tk.LEFT, padx=10)

# --- Text Editing Frame ---
edit_frame = tk.Frame(root)
edit_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

text_widget = scrolledtext.ScrolledText(edit_frame, wrap=tk.WORD, width=85, height=22, font=("Courier New", 10))
text_widget.pack(fill=tk.BOTH, expand=True)

# --- Bottom Frame ---
bottom_frame = tk.Frame(root)
bottom_frame.pack(pady=10)

load_button = tk.Button(bottom_frame, text="Load File", command=load_file_content)
load_button.pack(side=tk.LEFT, padx=10)

save_button = tk.Button(bottom_frame, text="Save Changes", command=save_file_content)
save_button.pack(side=tk.LEFT, padx=10)

# Apply initial theme + load
apply_theme(current_theme)
load_file_content()

# Start GUI
root.mainloop()
