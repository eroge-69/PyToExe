
import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox

FILE_CATEGORIES = {
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".odt", ".rtf", ".tex", ".wps"],
    "Spreadsheets": [".xls", ".xlsx", ".csv", ".ods", ".tsv"],
    "Presentations": [".ppt", ".pptx", ".odp", ".key"],
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".heic", ".svg"],
    "Videos": [".mp4", ".mkv", ".mov", ".avi", ".wmv", ".flv", ".webm", ".3gp"],
    "Music": [".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a", ".wma", ".aiff"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".iso"],
    "Executables": [".exe", ".msi", ".bat", ".cmd", ".jar", ".sh", ".apk", ".py", ".js"],
    "Fonts": [".ttf", ".otf", ".woff", ".woff2", ".fnt"],
    "Code Files": [".py", ".js", ".html", ".css", ".cpp", ".java", ".cs", ".php", ".rb", ".ipynb"],
    "Design Files": [".psd", ".ai", ".xd", ".sketch", ".fig", ".indd"]
}

def get_category(extension):
    extension = extension.lower()
    for category, extensions in FILE_CATEGORIES.items():
        if extension in extensions:
            return category
    return "Others"

def organize_files(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            _, ext = os.path.splitext(filename)
            category = get_category(ext)
            category_folder = os.path.join(folder_path, category)
            os.makedirs(category_folder, exist_ok=True)

            destination = os.path.join(category_folder, filename)
            base, extension = os.path.splitext(filename)
            counter = 1
            while os.path.exists(destination):
                destination = os.path.join(category_folder, f"{base} ({counter}){extension}")
                counter += 1

            shutil.move(file_path, destination)

def select_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        organize_files(folder_selected)
        messagebox.showinfo("Done", "🎉 Files have been organized!")

def create_gui():
    root = tk.Tk()
    root.title("Smart File Organizer")
    root.geometry("360x160")
    root.resizable(False, False)

    label = tk.Label(root, text="Select a folder to organize your files:", font=("Segoe UI", 11))
    label.pack(pady=15)

    organize_btn = tk.Button(root, text="📂 Select Folder & Organize", command=select_folder, font=("Segoe UI", 10, "bold"), bg="#4CAF50", fg="white", padx=12, pady=6)
    organize_btn.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
