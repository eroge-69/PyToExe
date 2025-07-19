
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd

def sanitize_filename(name):
    invalid_chars = '<>:"/\\|?*'
    for ch in invalid_chars:
        name = name.replace(ch, '')
    return name.strip()

def rename_files_and_update_csv(folder):
    csv_path = os.path.join(folder, "rename_list.csv")
    if not os.path.exists(csv_path):
        messagebox.showerror("Error", "rename_list.csv not found in the folder.")
        return

    df = pd.read_csv(csv_path)

    renamed_files = []
    for index, row in df.iterrows():
        original = row['Filename']
        title = sanitize_filename(row['Title'])
        ext = os.path.splitext(original)[1]
        new_name = f"{title}{ext}"
        src = os.path.join(folder, original)
        dst = os.path.join(folder, new_name)

        counter = 1
        while os.path.exists(dst) and os.path.abspath(src) != os.path.abspath(dst):
            new_name = f"{title}_{counter}{ext}"
            dst = os.path.join(folder, new_name)
            counter += 1

        if os.path.exists(src):
            os.rename(src, dst)
            df.at[index, 'Filename'] = os.path.basename(dst)
            renamed_files.append((original, os.path.basename(dst)))

    df.to_csv(csv_path, index=False)
    messagebox.showinfo("Success", f"Renamed {len(renamed_files)} files and updated the CSV.")

def main():
    root = tk.Tk()
    root.withdraw()
    folder = filedialog.askdirectory(title="Select Folder with Images and rename_list.csv")
    if folder:
        rename_files_and_update_csv(folder)

if __name__ == "__main__":
    main()
