import os
import csv
import tkinter as tk
from tkinter import filedialog, messagebox

def rename_files():
    folder_path = filedialog.askdirectory(title="Select Folder with Original Files")
    if not folder_path:
        return

    csv_path = filedialog.askopenfilename(title="Select CSV File", filetypes=[("CSV files", "*.csv")])
    if not csv_path:
        return

    # Read CSV
    mapping = {}
    try:
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                original_name = row['filename']  # CSV column: filename
                new_name = row['title']          # CSV column: title
                mapping[original_name] = new_name
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read CSV file:\n{e}")
        return

    # Rename files
    renamed_count = 0
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path):
            name, ext = os.path.splitext(file)
            if name in mapping:
                new_file_name = mapping[name] + ext
                new_file_path = os.path.join(folder_path, new_file_name)
                try:
                    os.rename(file_path, new_file_path)
                    renamed_count += 1
                except Exception as e:
                    messagebox.showwarning("Warning", f"Could not rename {file}:\n{e}")

    messagebox.showinfo("Done", f"Renaming completed. {renamed_count} files renamed.")

# GUI setup
root = tk.Tk()
root.title("CSV File Renamer")
root.geometry("400x150")

label = tk.Label(root, text="Click the button to select folder and CSV file to rename files", wraplength=350)
label.pack(pady=20)

button = tk.Button(root, text="Select Folder & CSV", command=rename_files, width=30, height=2)
button.pack()

root.mainloop()
