import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import json
import os

CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"last_location": ""}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

def choose_folder():
    folder = filedialog.askdirectory()
    if folder:
        folder_var.set(folder)

def download_gallery():
    url = url_entry.get()
    folder = folder_var.get()

    if not url or not folder:
        messagebox.showerror("Error", "Please provide both URL and folder.")
        return

    # Save folder for next time
    config["last_location"] = folder
    save_config(config)

    try:
        subprocess.run(
            ["imagefap-dl", "-o", folder, url],
            check=True,
            shell=False  # Correct usage: shell=False when passing a list
        )
        messagebox.showinfo("Done", "Download completed successfully!")
    except FileNotFoundError:
        messagebox.showerror("Error", "imagefap-dl not found. Please install it.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Download failed:\n{e}")

# Load last config
config = load_config()

# GUI
root = tk.Tk()
root.title("ImageFap Downloader")

tk.Label(root, text="Gallery URL:").grid(row=0, column=0, sticky="w")
url_entry = tk.Entry(root, width=50)
url_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(root, text="Save Location:").grid(row=1, column=0, sticky="w")
folder_var = tk.StringVar(value=config.get("last_location", ""))
tk.Entry(root, textvariable=folder_var, width=50).grid(row=1, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=choose_folder).grid(row=1, column=2)

tk.Button(root, text="Download", command=download_gallery).grid(row=2, column=1, pady=10)

root.mainloop()