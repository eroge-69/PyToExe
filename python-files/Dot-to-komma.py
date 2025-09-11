import os
import tkinter as tk
from tkinter import filedialog, messagebox

def replace_dots_in_files(folder_path):
    updated_files = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
            
            new_content = content.replace(".", ",")
            
            # Save as a new file with "_modified"
            new_filename = os.path.splitext(filename)[0] + "_modified.txt"
            new_file_path = os.path.join(folder_path, new_filename)
            
            with open(new_file_path, "w", encoding="utf-8") as file:
                file.write(new_content)
            
            updated_files.append(new_filename)
    return updated_files

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    folder = filedialog.askdirectory(title="Select a folder with .txt files")

    if folder:
        updated = replace_dots_in_files(folder)
        if updated:
            messagebox.showinfo("Done", f"Created {len(updated)} new file(s):\n\n" + "\n".join(updated))
        else:
            messagebox.showwarning("No files", "No .txt files found in the selected folder.")
    else:
        messagebox.showwarning("No folder selected", "No folder was chosen. Exiting...")
