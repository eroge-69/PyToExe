import os
import tkinter as tk
from tkinter import filedialog, messagebox

def rename_images_in_folder():
    folder_path = filedialog.askdirectory(title="Select Folder with Images")

    if not folder_path:
        messagebox.showinfo("No Folder", "No folder was selected.")
        return

    renamed_count = 0

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            name, ext = os.path.splitext(filename)
            new_name = name.replace('-', ' ').replace('_', ' ')
            new_name = new_name.title()
            new_filename = new_name + ext

            old_path = os.path.join(folder_path, filename)
            new_path = os.path.join(folder_path, new_filename)

            if old_path != new_path:
                os.rename(old_path, new_path)
                renamed_count += 1

    messagebox.showinfo("Done ✅", f"Total renamed files: {renamed_count}")

# GUI window
root = tk.Tk()
root.title("Image Name Cleaner")
root.geometry("400x200")
root.resizable(False, False)

label = tk.Label(root, text="Click the button below to select a folder\nand clean up image names.", font=("Arial", 12), pady=20)
label.pack()

btn = tk.Button(root, text="Select Image Folder", command=rename_images_in_folder, font=("Arial", 12), bg="#4CAF50", fg="white", padx=10, pady=5)
btn.pack()

root.mainloop()