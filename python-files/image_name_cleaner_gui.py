import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

def rename_images_with_preview():
    folder_path = filedialog.askdirectory(title="Select Folder with Images")

    if not folder_path:
        messagebox.showinfo("No Folder", "No folder was selected.")
        return

    image_files = [
        f for f in os.listdir(folder_path)
        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))
    ]

    if not image_files:
        messagebox.showinfo("No Images", "No image files found in the selected folder.")
        return

    preview_window = tk.Toplevel(root)
    preview_window.title("Rename Preview")
    preview_window.geometry("650x450")
    preview_window.resizable(False, False)

    # Frame for scrollable text area
    frame = tk.Frame(preview_window)
    frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    text_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD, font=("Consolas", 10), height=20)
    text_area.pack(fill=tk.BOTH, expand=True)

    rename_pairs = []

    for filename in image_files:
        name, ext = os.path.splitext(filename)
        new_name = name.replace('-', ' ').replace('_', ' ').title()
        new_filename = new_name + ext
        rename_pairs.append((filename, new_filename))

        # Display preview in a clean way
        text_area.insert(tk.END, f"Old🔹 {filename}\n")
        text_area.insert(tk.END, f"New ⮕ {new_filename}\n\n")

    def confirm_rename():
        backup_folder = os.path.join(folder_path, "backup_originals")
        os.makedirs(backup_folder, exist_ok=True)

        renamed_count = 0

        for old_name, new_name in rename_pairs:
            old_path = os.path.join(folder_path, old_name)
            new_path = os.path.join(folder_path, new_name)

            if old_name != new_name:
                backup_path = os.path.join(backup_folder, old_name)
                shutil.copy2(old_path, backup_path)
                os.rename(old_path, new_path)
                renamed_count += 1

        messagebox.showinfo("Rename Completed", f"✅ Renamed {renamed_count} files.\n🗂️ Backup saved in: backup_originals/")
        preview_window.destroy()

    confirm_btn = tk.Button(preview_window, text="✅ Confirm Rename", command=confirm_rename,
                            bg="#2196F3", fg="white", padx=10, pady=5)
    confirm_btn.pack(pady=10)


# --- Main GUI Window ---
root = tk.Tk()
root.title("Image Name Cleaner")
root.geometry("500x250")
root.resizable(False, False)

content_frame = tk.Frame(root)
content_frame.pack(expand=True)

title_label = tk.Label(content_frame,
                       text="Click below to select a folder and preview image name cleanup.",
                       font=("Arial", 12), pady=20)
title_label.pack()

select_btn = tk.Button(content_frame, text="📁 Select Image Folder",
                       command=rename_images_with_preview, font=("Arial", 12),
                       bg="#4CAF50", fg="white", padx=10, pady=5)
select_btn.pack()

# Footer credit
credit_label = tk.Label(root, text="By MD Nayeem Islam", font=("Arial", 9), fg="gray")
credit_label.pack(side=tk.BOTTOM, pady=5)

root.mainloop()