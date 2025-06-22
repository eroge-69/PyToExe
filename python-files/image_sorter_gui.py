
import os
import shutil
import random
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox

def sort_images():
    folder_selected = filedialog.askdirectory(title="Select Folder Containing Images")
    if not folder_selected:
        return

    try:
        images_per_folder = simpledialog.askinteger("Input", "How many images per folder?", minvalue=1, maxvalue=1000)
        if not images_per_folder:
            return
    except Exception:
        messagebox.showerror("Error", "Invalid number entered.")
        return

    output_folder = os.path.join(folder_selected, "sorted_output")
    os.makedirs(output_folder, exist_ok=True)

    valid_exts = ('.jpg', '.jpeg', '.png')
    images = [f for f in os.listdir(folder_selected) if f.lower().endswith(valid_exts)]
    random.shuffle(images)

    for i in range(0, len(images), images_per_folder):
        chunk = images[i:i+images_per_folder]
        folder_name = f"Set_{i//images_per_folder + 1}"
        folder_path = os.path.join(output_folder, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        for img in chunk:
            shutil.copy(os.path.join(folder_selected, img), os.path.join(folder_path, img))

    messagebox.showinfo("Done", f"Images sorted into {len(os.listdir(output_folder))} folders!")

root = tk.Tk()
root.withdraw()
sort_images()
