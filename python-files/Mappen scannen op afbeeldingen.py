import os
import shutil
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']

def find_image_files(directory):
    image_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if Path(file).suffix.lower() in IMAGE_EXTENSIONS:
                image_files.append(Path(root) / file)
    return image_files

def select_folder(title):
    return filedialog.askdirectory(title=title)

def copy_with_progress(image_files, destination, root):
    progress_window = tk.Toplevel(root)
    progress_window.title("Bezig met kopiëren...")

    label = tk.Label(progress_window, text="Kopiëren van afbeeldingen...")
    label.pack(padx=10, pady=(10, 0))

    progress = ttk.Progressbar(progress_window, length=300, mode='determinate', maximum=len(image_files))
    progress.pack(padx=10, pady=10)

    progress_window.update()

    for i, file in enumerate(image_files, start=1):
        shutil.copy(file, destination)
        progress["value"] = i
        progress_window.update_idletasks()

    messagebox.showinfo("Klaar", f"{len(image_files)} afbeeldingen gekopieerd naar:\n{destination}")
    progress_window.destroy()

def main():
    root = tk.Tk()
    root.withdraw()

    source_folder = select_folder("Selecteer de map om te scannen op afbeeldingen")
    if not source_folder:
        messagebox.showinfo("Geannuleerd", "Geen bronmap geselecteerd.")
        return

    image_files = find_image_files(source_folder)
    count = len(image_files)

    if count == 0:
        messagebox.showinfo("Geen afbeeldingen", "Er zijn geen afbeeldingsbestanden gevonden.")
        return

    answer = messagebox.askyesno("Afbeeldingen gevonden", f"Er zijn {count} afbeeldingen gevonden.\nWil je ze kopiëren?")
    if not answer:
        return

    dest_folder = select_folder("Selecteer de doelmap")
    if not dest_folder:
        messagebox.showinfo("Geannuleerd", "Geen doelmap geselecteerd.")
        return

    root.deiconify()
    copy_with_progress(image_files, dest_folder, root)

if __name__ == "__main__":
    main()