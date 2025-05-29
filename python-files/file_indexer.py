import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os
import sqlite3
import pandas as pd
from datetime import datetime
from collections import defaultdict

class FileIndexerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Indexer")
        self.db_file = "file_index.db"
        self.file_data = []
        self.current_page = 0
        self.rows_per_page = 20
        self.filtered_data = []
        self.selected_folders = []

        # Column visibility state
        self.column_visibility = {
            "Row": tk.BooleanVar(value=True),
            "ID": tk.BooleanVar(value=True),
            "File Name": tk.BooleanVar(value=True),
            "Full Path": tk.BooleanVar(value=True)
        }

        # Initialize SQLite database
        self.init_db()

        # Apply modern theme
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()

        # Main container
        self.main_frame = ttk.Frame(self.root, padding=20)
        self.main_frame.pack(fill="both", expand=True)

        # Create notebook (tabs)
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(pady=10, fill="both", expand=True)

        # Index Tab
        self.index_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.index_frame, text="Index Files")

        # Search Tab
        self.search_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.search_frame, text="Search Files")

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(self.main_frame, textvariable=self.status_var, style="Status.TLabel")
        self.status_label.pack(side="bottom", fill="x", pady=5)

        self.setup_index_tab()
        self.setup_search_tab()

    def init_db(self):
        # Initialize SQLite database and create table if it doesn't exist
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS files (
                    file_id TEXT PRIMARY KEY,
                    full_path TEXT UNIQUE,
                    file_name TEXT
                )
            ''')
            conn.commit()

    def configure_styles(self):
        # Configure modern styles
        self.style.configure("TButton", font=("Helvetica", 10), padding=8)
        self.style.map("TButton", 
                      background=[('active', '#005f87'), ('!active', '#0078d4')],
                      foreground=[('active', '#ffffff'), ('!active', '#ffffff')])
        self.style.configure("TLabel", font=("Helvetica", 10))
        self.style.configure("Status.TLabel", font=("Helvetica", 9), background="#e0e0e0", padding=5)
        self.style.configure("TEntry", font=("Helvetica", 10))
        self.style.configure("TCombobox", font=("Helvetica", 10))
        self.style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))
        self.style.configure("Treeview", font=("Helvetica", 9), rowheight=25)

    def setup_index_tab(self):
        # Folder selection frame
        input_frame = ttk.Frame(self.index_frame)
        input_frame.pack(fill="x", pady=10)

        ttk.Label(input_frame, text="Selected Folders:", style="TLabel").pack(side="left", padx=5)
        self.folder_path_var = tk.StringVar()
        self.folder_entry = ttk.Entry(input_frame, textvariable=self.folder_path_var, width=50, state="readonly")
        self.folder_entry.pack(side="left", padx=5, fill="x", expand=True)
        ttk.Button(input_frame, text="Browse", command=self.browse_folders, style="TButton").pack(side="left", padx=5)

        # Index button
        ttk.Button(self.index_frame, text="Index Files", command=self.index_files, style="TButton").pack(pady=20)

    def setup_search_tab(self):
        # Search controls frame
        search_frame = ttk.Frame(self.search_frame)
        search_frame.pack(fill="x", pady=10)

        ttk.Label(search_frame, text="Search File Name:", style="TLabel").pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search_var, width=30).pack(side="left", padx=5)

        ttk.Label(search_frame, text="File Type:", style="TLabel").pack(side="left", padx=5)
        self.file_type_var = tk.StringVar()
        self.file_type_combo = ttk.Combobox(search_frame, textvariable=self.file_type_var, 
                                          values=["All", "pdf", "txt", "doc", "docx", "jpg", "png"], width=10)
        self.file_type_combo.set("All")
        self.file_type_combo.pack(side="left", padx=5)

        # Buttons
        button_frame = ttk.Frame(self.search_frame)
        button_frame.pack(fill="x", pady=5)
        ttk.Button(button_frame, text="Search", command=self.search_files, style="TButton").pack(side="left", padx=5)
        ttk.Button(button_frame, text="List All", command=self.list_all_files, style="TButton").pack(side="left", padx=5)
        ttk.Button(button_frame, text="Reset", command=self.reset_search, style="TButton").pack(side="left", padx=5)
        ttk.Button(button_frame, text="Find Duplicates (Path)", command=self.find_duplicates_by_path, style="TButton").pack(side="left", padx=5)
        ttk.Button(button_frame, text="Find Duplicates (Name)", command=self.find_duplicates_by_name, style="TButton").pack(side="left", padx=5)
        ttk.Button(button_frame, text="Columns", command=self.show_column_menu, style="TButton").pack(side="left", padx=5)
        ttk.Button(button_frame, text="Export to CSV", command=self.export_to_csv, style="TButton").pack(side="left", padx=5)

        # Treeview for results
        self.tree = ttk.Treeview(self.search_frame, 
                               columns=("Row", "ID", "File Name", "Full Path"), 
                               show="headings")
        self.tree.heading("Row", text="Row")
        self.tree.heading("ID", text="File ID")
        self.tree.heading("File Name", text="File Name")
        self.tree.heading("Full Path", text="Full Path")
        self.tree.column("Row", width=50)
        self.tree.column("ID", width=100)
        self.tree.column("File Name", width=200)
        self.tree.column("Full Path", width=400)
        self.tree.pack(pady=10, fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.search_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Context menu for right-click
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="Copy File Name", command=self.copy_file_name)
        self.context_menu.add_command(label="Copy File Path", command=self.copy_file_path)
        self.tree.bind("<Button-3>", self.show_context_menu)

        # Pagination controls
        pagination_frame = ttk.Frame(self.search_frame)
        pagination_frame.pack(pady=10)
        ttk.Button(pagination_frame, text="Previous", command=self.prev_page, style="TButton").pack(side="left", padx=5)
        self.page_label = ttk.Label(pagination_frame, text="Page 1", style="TLabel")
        self.page_label.pack(side="left", padx=10)
        ttk.Button(pagination_frame, text="Next", command=self.next_page, style="TButton").pack(side="left", padx=5)

        # Initialize column display
        self.update_column_display()

    def show_column_menu(self):
        # Create and show column toggle menu
        column_menu = tk.Menu(self.root, tearoff=0)
        for col in self.column_visibility:
            column_menu.add_checkbutton(label=col, variable=self.column_visibility[col], command=self.update_column_display)
        column_menu.post(self.root.winfo_pointerx(), self.root.winfo_pointery())

    def update_column_display(self):
        # Update Treeview to show only visible columns
        visible_columns = [col for col in ("Row", "ID", "File Name", "Full Path") if self.column_visibility[col].get()]
        self.tree["displaycolumns"] = visible_columns
        self.update_tree()  # Refresh Treeview with current data

    def show_context_menu(self, event):
        # Show context menu only if a row is selected
        selected_item = self.tree.identify_row(event.y)
        if selected_item:
            self.tree.selection_set(selected_item)
            self.context_menu.post(event.x_root, event.y_root)

    def copy_file_name(self):
        selected_item = self.tree.selection()
        if selected_item:
            values = self.tree.item(selected_item[0])['values']
            file_name = values[2]  # File Name is in column 2
            self.root.clipboard_clear()
            self.root.clipboard_append(file_name)
            self.root.update()  # Ensure clipboard is updated
            self.status_var.set(f"Copied file name: {file_name}")

    def copy_file_path(self):
        selected_item = self.tree.selection()
        if selected_item:
            values = self.tree.item(selected_item[0])['values']
            file_path = values[3]  # Full Path is in column 3
            self.root.clipboard_clear()
            self.root.clipboard_append(file_path)
            self.root.update()  # Ensure clipboard is updated
            self.status_var.set(f"Copied file path: {file_path}")

    def browse_folders(self):
        # Create a dialog for multiple folder selection
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Folders")
        dialog.geometry("600x400")
        dialog.transient(self.root)
        dialog.grab_set()

        # Listbox to display selected folders
        folder_listbox = tk.Listbox(dialog, height=15)
        folder_listbox.pack(pady=10, padx=10, fill="both", expand=True)

        # Buttons for adding folders and confirming
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=5)
        ttk.Button(button_frame, text="Add Folder", command=lambda: self.add_folder(folder_listbox), style="TButton").pack(side="left", padx=5)
        ttk.Button(button_frame, text="Done", command=lambda: self.finalize_folders(dialog, folder_listbox), style="TButton").pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy, style="TButton").pack(side="left", padx=5)

    def add_folder(self, folder_listbox):
        folder = filedialog.askdirectory()
        if folder and folder not in self.selected_folders:
            self.selected_folders.append(folder)
            folder_listbox.insert(tk.END, folder)

    def finalize_folders(self, dialog, folder_listbox):
        self.selected_folders = [folder_listbox.get(i) for i in range(folder_listbox.size())]
        if self.selected_folders:
            self.folder_path_var.set("; ".join(self.selected_folders))
            self.status_var.set(f"Selected {len(self.selected_folders)} folder(s)")
        else:
            self.folder_path_var.set("")
            self.status_var.set("No folders selected")
        dialog.destroy()

    def index_files(self):
        if not self.selected_folders:
            messagebox.showerror("Error", "Please select at least one folder")
            self.status_var.set("Error: No folders selected")
            return

        # Load existing file paths from database
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT full_path FROM files")
            existing_paths = {row[0] for row in cursor.fetchall()}

        # Collect new files from all selected folders
        new_files = []
        for folder_path in self.selected_folders:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    full_path = os.path.join(root, file)
                    if full_path not in existing_paths:
                        file_id = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(existing_paths) + len(new_files)}"
                        new_files.append({
                            "file_id": file_id,
                            "full_path": full_path,
                            "file_name": file
                        })
                        existing_paths.add(full_path)  # Prevent duplicates within this indexing

        # Insert new files into database
        if new_files:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.executemany(
                    "INSERT INTO files (file_id, full_path, file_name) VALUES (?, ?, ?)",
                    [(item["file_id"], item["full_path"], item["file_name"]) for item in new_files]
                )
                conn.commit()

        # Update file_data for in-memory use
        self.file_data = self.load_db()

        messagebox.showinfo("Success", f"Appended {len(new_files)} new files from {len(self.selected_folders)} folder(s). Total: {len(self.file_data)} files in database")
        self.status_var.set(f"Appended {len(new_files)} new files. Total: {len(self.file_data)} files")
        self.selected_folders = []  # Clear selected folders after indexing
        self.folder_path_var.set("")

    def load_db(self):
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT file_id, full_path, file_name FROM files")
                return [{"file_id": row[0], "full_path": row[1], "file_name": row[2]} for row in cursor.fetchall()]
        except sqlite3.Error:
            return []

    def update_tree(self):
        self.tree.delete(*self.tree.get_children())
        start_idx = self.current_page * self.rows_per_page
        end_idx = start_idx + self.rows_per_page
        page_data = self.filtered_data[start_idx:end_idx]
        
        for idx, item in enumerate(page_data, start=start_idx + 1):
            self.tree.insert("", "end", values=(idx, item["file_id"], item["file_name"], item["full_path"]))
        
        total_pages = (len(self.filtered_data) + self.rows_per_page - 1) // self.rows_per_page
        self.page_label.config(text=f"Page {self.current_page + 1} of {max(1, total_pages)}")
        self.status_var.set(f"Displaying {len(page_data)} of {len(self.filtered_data)} files")

    def search_files(self):
        search_term = self.search_var.get().lower()
        file_type = self.file_type_var.get().lower()
        
        file_data = self.load_db()
        self.filtered_data = []
        
        for item in file_data:
            matches_search = not search_term or search_term in item["file_name"].lower()
            matches_type = file_type == "all" or item["file_name"].lower().endswith(f".{file_type}")
            if matches_search and matches_type:
                self.filtered_data.append(item)
        
        self.current_page = 0
        self.update_tree()

    def find_duplicates_by_path(self):
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT file_id, full_path, file_name
                    FROM files
                    WHERE full_path IN (
                        SELECT full_path
                        FROM files
                        GROUP BY full_path
                        HAVING COUNT(*) > 1
                    )
                    ORDER BY full_path
                """)
                self.filtered_data = [{"file_id": row[0], "full_path": row[1], "file_name": row[2]} for row in cursor.fetchall()]
            
            self.current_page = 0
            self.update_tree()
            self.status_var.set(f"Found {len(self.filtered_data)} duplicate files by path")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Database error: {e}")
            self.status_var.set("Error: Failed to find duplicates")

    def find_duplicates_by_name(self):
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT file_id, full_path, file_name
                    FROM files
                    WHERE LOWER(file_name) IN (
                        SELECT LOWER(file_name)
                        FROM files
                        GROUP BY LOWER(file_name)
                        HAVING COUNT(*) > 1
                    )
                    ORDER BY LOWER(file_name)
                """)
                self.filtered_data = [{"file_id": row[0], "full_path": row[1], "file_name": row[2]} for row in cursor.fetchall()]
            
            self.current_page = 0
            self.update_tree()
            self.status_var.set(f"Found {len(self.filtered_data)} duplicate files by name")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Database error: {e}")
            self.status_var.set("Error: Failed to find duplicates")

    def reset_search(self):
        self.search_var.set("")
        self.file_type_combo.set("All")
        self.filtered_data = self.load_db()
        self.current_page = 0
        self.update_tree()
        self.status_var.set("Search reset")

    def list_all_files(self):
        self.reset_search()

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_tree()

    def next_page(self):
        total_pages = (len(self.filtered_data) + self.rows_per_page - 1) // self.rows_per_page
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.update_tree()

    def export_to_csv(self):
        if not self.filtered_data:
            messagebox.showinfo("Info", "No files to export")
            self.status_var.set("No files to export")
            return
        
        df = pd.DataFrame(self.filtered_data)
        df['row_number'] = range(1, len(self.filtered_data) + 1)
        df = df[['row_number', 'file_id', 'file_name', 'full_path']]
        
        output_file = f"file_index_export_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
        df.to_csv(output_file, index=False)
        messagebox.showinfo("Success", f"Exported to {output_file}")
        self.status_var.set(f"Exported to {output_file}")

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("900x700")
    app = FileIndexerApp(root)
    root.mainloop()