import os
import shutil
import datetime
import fnmatch
import threading
import logging
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# --- Helper functions ---

def format_size(bytes_size):
    return f"{bytes_size / 1024:.2f} KB"

def format_mtime(epoch_time):
    dt = datetime.datetime.fromtimestamp(epoch_time)
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def get_non_conflicting_path(dest_folder, filename):
    base, ext = os.path.splitext(filename)
    candidate = filename
    i = 1
    while os.path.exists(os.path.join(dest_folder, candidate)):
        candidate = f"{base} ({i}){ext}"
        i += 1
    return os.path.join(dest_folder, candidate)

# --- Main Application ---

class FileFinderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Advanced Recursive File Finder and Copier")
        self.geometry("900x700")
        self.resizable(False, False)

        # Setup logger
        logging.basicConfig(filename="file_finder_copier.log",
                            level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')

        self.found_files = []  # List of dicts: {path, size, mtime, selected}
        self.folder_entries = []

        self._setup_ui()

    def _setup_ui(self):
        # Filename input
        tk.Label(self, text="Filename (supports wildcards, e.g., *.txt or report*):").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.filename_entry = tk.Entry(self, width=60)
        self.filename_entry.grid(row=0, column=1, columnspan=3, sticky="w", padx=5)

        # Dynamic folder inputs frame
        self.folder_frame = tk.Frame(self)
        self.folder_frame.grid(row=1, column=0, columnspan=4, padx=10, pady=5, sticky="w")

        tk.Label(self.folder_frame, text="Search Folders:").grid(row=0, column=0, sticky="w")
        # Add first folder input by default
        self._add_folder_input()

        # Add / Remove folder buttons
        self.add_folder_btn = tk.Button(self.folder_frame, text="+ Add Folder", command=self._add_folder_input)
        self.add_folder_btn.grid(row=99, column=0, sticky="w", pady=5)
        self.remove_folder_btn = tk.Button(self.folder_frame, text="- Remove Folder", command=self._remove_folder_input)
        self.remove_folder_btn.grid(row=99, column=1, sticky="w", padx=5, pady=5)

        # Destination folder input
        tk.Label(self, text="Destination Folder:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.destination_entry = tk.Entry(self, width=60)
        self.destination_entry.grid(row=2, column=1, columnspan=2, sticky="w", padx=5)
        tk.Button(self, text="Browse", command=self._browse_destination).grid(row=2, column=3, sticky="w")

        # Search and copy buttons
        self.search_btn = tk.Button(self, text="Search Files", command=self._start_search, bg="#1976D2", fg="white", width=20)
        self.search_btn.grid(row=3, column=1, pady=10, sticky="e")

        self.copy_btn = tk.Button(self, text="Copy Selected Files", command=self._start_copy, bg="#388E3C", fg="white", width=20, state="disabled")
        self.copy_btn.grid(row=3, column=2, pady=10, sticky="w")

        # Progress bar and status
        self.progress = ttk.Progressbar(self, orient="horizontal", length=600, mode="determinate")
        self.progress.grid(row=4, column=0, columnspan=4, padx=10, sticky="w")
        self.status_label = tk.Label(self, text="Status: Waiting to start")
        self.status_label.grid(row=5, column=0, columnspan=4, padx=10, pady=5, sticky="w")

        # Found files list with scrollbar
        columns = ("path", "size", "modified", "selected")
        self.tree_frame = tk.Frame(self)
        self.tree_frame.grid(row=6, column=0, columnspan=4, padx=10, pady=5, sticky="nsew")

        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings", height=20)
        self.tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky='ns')
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.heading("path", text="File Path")
        self.tree.heading("size", text="Size")
        self.tree.heading("modified", text="Last Modified")
        self.tree.heading("selected", text="Selected")

        self.tree.column("path", width=550)
        self.tree.column("size", width=80, anchor="center")
        self.tree.column("modified", width=130, anchor="center")
        self.tree.column("selected", width=80, anchor="center")

        # Bind double click to toggle selection
        self.tree.bind("<Double-1>", self._on_tree_double_click)

    def _add_folder_input(self):
        idx = len(self.folder_entries)
        if idx >= 10:
            messagebox.showinfo("Limit reached", "Maximum 10 search folders allowed.")
            return
        entry = tk.Entry(self.folder_frame, width=60)
        entry.grid(row=idx+1, column=0, sticky="w", pady=2)
        btn = tk.Button(self.folder_frame, text="Browse", command=lambda e=entry: self._browse_folder(e))
        btn.grid(row=idx+1, column=1, sticky="w", padx=5)
        self.folder_entries.append(entry)

    def _remove_folder_input(self):
        if len(self.folder_entries) <= 1:
            messagebox.showinfo("Minimum folders", "At least one search folder is required.")
            return
        entry = self.folder_entries.pop()
        entry.grid_forget()
        # Remove associated browse button too
        for widget in self.folder_frame.grid_slaves():
            row = int(widget.grid_info()["row"])
            if row == len(self.folder_entries)+1:
                widget.grid_forget()

    def _browse_folder(self, entry):
        folder = filedialog.askdirectory()
        if folder:
            entry.delete(0, tk.END)
            entry.insert(0, folder)

    def _browse_destination(self):
        folder = filedialog.askdirectory()
        if folder:
            self.destination_entry.delete(0, tk.END)
            self.destination_entry.insert(0, folder)

    def _start_search(self):
        filename_pattern = self.filename_entry.get().strip()
        if not filename_pattern:
            messagebox.showerror("Input Error", "Please enter a filename pattern to search for.")
            return
        search_folders = [e.get().strip() for e in self.folder_entries if e.get().strip()]
        if not search_folders:
            messagebox.showerror("Input Error", "Please enter at least one search folder.")
            return
        for folder in search_folders:
            if not os.path.isdir(folder):
                messagebox.showerror("Folder Error", f"Search folder does not exist:\n{folder}")
                return

        self.found_files.clear()
        self.tree.delete(*self.tree.get_children())
        self.progress["value"] = 0
        self.status_label.config(text="Status: Searching files...")
        self.copy_btn.config(state="disabled")

        # Run search in background thread to keep UI responsive
        threading.Thread(target=self._search_files_thread, args=(filename_pattern, search_folders), daemon=True).start()

    def _search_files_thread(self, filename_pattern, search_folders):
        try:
            total_dirs = 0
            for base_folder in search_folders:
                for _, dirs, _ in os.walk(base_folder):
                    total_dirs += 1
            if total_dirs == 0:
                total_dirs = 1  # prevent division by zero

            processed_dirs = 0
            found = []

            for base_folder in search_folders:
                for root, dirs, files in os.walk(base_folder):
                    processed_dirs += 1
                    progress_pct = int(processed_dirs / total_dirs * 100)
                    self._update_progress(progress_pct, f"Searching: {root}")

                    for file in files:
                        if fnmatch.fnmatch(file, filename_pattern):
                            full_path = os.path.join(root, file)
                            try:
                                size = os.path.getsize(full_path)
                                mtime = os.path.getmtime(full_path)
                            except Exception:
                                size = 0
                                mtime = 0
                            found.append({
                                "path": full_path,
                                "size": size,
                                "mtime": mtime,
                                "selected": True
                            })

            # Update UI treeview in main thread
            self.after(0, self._populate_file_list, found)

            logging.info(f"Search complete: found {len(found)} files matching '{filename_pattern}'")
            self._update_status(f"Search complete: {len(found)} files found.")

        except Exception as e:
            logging.error(f"Error during search: {e}")
            self._update_status(f"Error during search: {e}")
            messagebox.showerror("Search Error", f"An error occurred during search:\n{e}")

    def _populate_file_list(self, found_files):
        self.found_files = found_files
        self.tree.delete(*self.tree.get_children())
        for idx, fileinfo in enumerate(found_files):
            self.tree.insert("", "end", iid=idx, values=(
                fileinfo["path"],
                format_size(fileinfo["size"]),
                format_mtime(fileinfo["mtime"]),
                "Yes" if fileinfo["selected"] else "No"
            ))
        self.copy_btn.config(state="normal" if found_files else "disabled")

    def _on_tree_double_click(self, event):
        item_id = self.tree.focus()
        if not item_id:
            return
        idx = int(item_id)
        fileinfo = self.found_files[idx]
        # Toggle selection
        fileinfo["selected"] = not fileinfo["selected"]
        self.tree.set(item_id, "selected", "Yes" if fileinfo["selected"] else "No")

    def _start_copy(self):
        dest_folder = self.destination_entry.get().strip()
        if not dest_folder:
            messagebox.showerror("Input Error", "Please select a destination folder.")
            return
        if not os.path.isdir(dest_folder):
            messagebox.showerror("Folder Error", "Destination folder does not exist.")
            return

        selected_files = [f for f in self.found_files if f["selected"]]
        if not selected_files:
            messagebox.showinfo("No Files Selected", "No files selected to copy.")
            return

        self.progress["value"] = 0
        self.status_label.config(text="Status: Copying files...")
        self.copy_btn.config(state="disabled")
        self.search_btn.config(state="disabled")

        threading.Thread(target=self._copy_files_thread, args=(selected_files, dest_folder), daemon=True).start()

    def _copy_files_thread(self, files, dest_folder):
        try:
            total_files = len(files)
                    for idx, fileinfo in enumerate(files, start=1):
            src = fileinfo["path"]
            try:
                dest = get_non_conflicting_path(dest_folder, os.path.basename(src))
                shutil.copy2(src, dest)
                logging.info(f"Copied: {src} → {dest}")
            except Exception as e:
                logging.error(f"Failed to copy {src}: {e}")

            progress_pct = int((idx / total_files) * 100)
            self._update_progress(progress_pct, f"Copying ({idx}/{total_files}): {os.path.basename(src)}")

        self._update_status("Copy complete.")
        messagebox.showinfo("Success", f"Copied {len(files)} files to:\n{dest_folder}")
        self.search_btn.config(state="normal")

    except Exception as e:
        logging.error(f"Error during file copy: {e}")
        self._update_status(f"Error during copy: {e}")
        messagebox.showerror("Copy Error", f"An error occurred during copying:\n{e}")
        self.search_btn.config(state="normal")

def _update_progress(self, percent, message):
    self.progress["value"] = percent
    self.status_label.config(text=f"Status: {message}")

def _update_status(self, message):
    self.status_label.config(text=f"Status: {message}")

# --- Run the Application ---
if __name__ == "__main__":
    app = FileFinderApp()
    app.mainloop()

