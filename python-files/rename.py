import os
import tkinter as tk
from tkinter import filedialog, messagebox
from customtkinter import *

# Supported file type filters
VIDEO_EXTS = ['.mp4', '.mkv', '.3gp', '.flv', '.avi', '.mov']
AUDIO_EXTS = ['.mp3', '.wav', '.aac', '.ogg']
DOC_EXTS = ['.pdf']
OFFICE_EXTS = ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']

# Set theme and appearance
set_appearance_mode("System")
set_default_color_theme("blue")

class FileRenamerApp(CTk):
    # --- FIX 1: The constructor method must be __init__ ---
    def __init__(self):
        super().__init__()
        self.title("Modern File Renamer")
        self.geometry("550x500")

        # --- Variables ---
        self.selected_path = tk.StringVar()
        self.target_text = tk.StringVar()
        self.replace_text = tk.StringVar()

        self.include_files = tk.BooleanVar(value=True)
        self.include_folders = tk.BooleanVar(value=False)
        self.filter_video = tk.BooleanVar(value=False)
        self.filter_audio = tk.BooleanVar(value=False)
        self.filter_docs = tk.BooleanVar(value=False)
        self.filter_office = tk.BooleanVar(value=False)

        self.create_widgets()

    def create_widgets(self):
        # --- Folder Selection ---
        CTkLabel(self, text="Select Folder to Rename Files In:").pack(pady=(15, 5))
        path_frame = CTkFrame(self)
        path_frame.pack(pady=5, fill="x", padx=20)
        CTkEntry(path_frame, textvariable=self.selected_path, width=400).pack(side="left", padx=5, fill="x", expand=True)
        CTkButton(path_frame, text="Browse", command=self.browse_folder).pack(side="left", padx=5)

        # --- Text Inputs ---
        CTkLabel(self, text="Text to Remove or Replace:").pack(pady=(15, 5))
        CTkEntry(self, textvariable=self.target_text, width=400).pack(pady=5, padx=20, fill="x")

        CTkLabel(self, text="Replacement Text (leave empty to remove):").pack(pady=(15, 5))
        CTkEntry(self, textvariable=self.replace_text, width=400).pack(pady=5, padx=20, fill="x")

        # --- Filter Options ---
        CTkLabel(self, text="Filter Options:").pack(pady=(15, 5))
        filter_frame = CTkFrame(self)
        filter_frame.pack(pady=5, padx=20, fill="x")
        
        # Create a grid layout for checkboxes for better alignment
        filter_frame.grid_columnconfigure((0, 1), weight=1)
        
        CTkCheckBox(filter_frame, text="All Files", variable=self.include_files).grid(row=0, column=0, sticky="w", padx=10, pady=5)
        CTkCheckBox(filter_frame, text="Folders Only", variable=self.include_folders).grid(row=0, column=1, sticky="w", padx=10, pady=5)
        CTkCheckBox(filter_frame, text="Movies (mp4, mkv, etc)", variable=self.filter_video).grid(row=1, column=0, sticky="w", padx=10, pady=5)
        CTkCheckBox(filter_frame, text="Music (mp3, wav, etc)", variable=self.filter_audio).grid(row=1, column=1, sticky="w", padx=10, pady=5)
        CTkCheckBox(filter_frame, text="Documents (PDF)", variable=self.filter_docs).grid(row=2, column=0, sticky="w", padx=10, pady=5)
        CTkCheckBox(filter_frame, text="Office Files (Word, Excel)", variable=self.filter_office).grid(row=2, column=1, sticky="w", padx=10, pady=5)

        # --- Action Button ---
        CTkButton(self, text="Start Renaming", command=self.rename_files, height=40).pack(pady=20)

    def browse_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.selected_path.set(path)

    def rename_files(self):
        folder = self.selected_path.get()
        target = self.target_text.get()
        replacement = self.replace_text.get()

        if not folder or not os.path.isdir(folder):
            messagebox.showerror("Error", "Please select a valid folder.")
            return

        if not target:
            messagebox.showerror("Error", "Please enter the target text to find.")
            return

        count = 0
        errors = []
        for entry in os.listdir(folder):
            full_path = os.path.join(folder, entry)
            
            # Skip if target text is not in the name
            if target not in entry:
                continue

            is_dir = os.path.isdir(full_path)
            
            # Folder filtering
            if is_dir and not self.include_folders.get():
                continue
            
            # File filtering
            if not is_dir:
                if not self.include_files.get():
                    continue

                _, ext = os.path.splitext(entry)
                ext = ext.lower()
                
                # If any filter is active, check against it
                any_filter_active = self.filter_video.get() or self.filter_audio.get() or self.filter_docs.get() or self.filter_office.get()
                if any_filter_active:
                    passes_filter = (
                        (self.filter_video.get() and ext in VIDEO_EXTS) or
                        (self.filter_audio.get() and ext in AUDIO_EXTS) or
                        (self.filter_docs.get() and ext in DOC_EXTS) or
                        (self.filter_office.get() and ext in OFFICE_EXTS)
                    )
                    if not passes_filter:
                        continue

            # Perform rename
            new_name = entry.replace(target, replacement)
            new_path = os.path.join(folder, new_name)
            try:
                os.rename(full_path, new_path)
                count += 1
            except Exception as e:
                errors.append(f"Failed to rename {entry}: {e}")
        
        if errors:
            messagebox.showwarning("Warning", f"{count} item(s) renamed.\nCould not rename some items:\n" + "\n".join(errors))
        else:
            messagebox.showinfo("Success", f"{count} item(s) renamed successfully.")

# --- FIX 2: The main execution block must be __name__ == "__main__" ---
if __name__ == "__main__":
    app = FileRenamerApp()
    app.mainloop()
