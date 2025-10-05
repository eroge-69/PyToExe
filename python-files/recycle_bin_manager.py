import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import winshell
import shutil
import datetime

class RecycleBinManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Recycle Bin Manager")
        self.root.geometry("800x600")

        # Frame for statistics
        self.stats_frame = tk.Frame(self.root)
        self.stats_frame.pack(pady=10)

        self.total_files_label = tk.Label(self.stats_frame, text="Total Files: 0")
        self.total_files_label.grid(row=0, column=0, padx=10)

        self.total_size_label = tk.Label(self.stats_frame, text="Total Size: 0 bytes")
        self.total_size_label.grid(row=0, column=1, padx=10)

        self.file_types_label = tk.Label(self.stats_frame, text="File Types: {}")
        self.file_types_label.grid(row=0, column=2, padx=10)

        # Search entry
        self.search_frame = tk.Frame(self.root)
        self.search_frame.pack(pady=10)

        tk.Label(self.search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(self.search_frame, width=50)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<KeyRelease>", self.update_list)

        # Treeview for listing items with checkboxes
        self.tree = ttk.Treeview(self.root, columns=("Select", "Name", "Original Path", "Size", "Deleted Date"), show="headings")
        self.tree.heading("Select", text="Select")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Original Path", text="Original Path")
        self.tree.heading("Size", text="Size (bytes)")
        self.tree.heading("Deleted Date", text="Deleted Date")
        self.tree.pack(fill=tk.BOTH, expand=True, pady=10)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Buttons frame
        self.buttons_frame = tk.Frame(self.root)
        self.buttons_frame.pack(pady=10)

        self.refresh_button = tk.Button(self.buttons_frame, text="Refresh", command=self.load_recycle_bin)
        self.refresh_button.grid(row=0, column=0, padx=5)

        self.select_all_button = tk.Button(self.buttons_frame, text="Select All", command=self.select_all)
        self.select_all_button.grid(row=0, column=1, padx=5)

        self.deselect_all_button = tk.Button(self.buttons_frame, text="Deselect All", command=self.deselect_all)
        self.deselect_all_button.grid(row=0, column=2, padx=5)

        self.restore_button = tk.Button(self.buttons_frame, text="Restore Selected", command=self.restore_selected)
        self.restore_button.grid(row=0, column=3, padx=5)

        self.delete_button = tk.Button(self.buttons_frame, text="Delete Selected Permanently", command=self.delete_selected)
        self.delete_button.grid(row=0, column=4, padx=5)

        self.empty_bin_button = tk.Button(self.buttons_frame, text="Empty Recycle Bin", command=self.empty_bin)
        self.empty_bin_button.grid(row=0, column=5, padx=5)

        # Data storage
        self.recycle_items = []
        self.selected_items = {}  # iid -> item

        self.load_recycle_bin()

    def load_recycle_bin(self):
        self.tree.delete(*self.tree.get_children())
        self.recycle_items = []
        self.selected_items = {}

        try:
            bin = winshell.recycle_bin()
            total_size = 0
            file_count = 0
            file_types = {}

            for item in bin:
                self.recycle_items.append(item)
                name = item.original_filename()
                # Kiểm tra kiểu file an toàn hơn bằng phần mở rộng hoặc giả định
                ext = os.path.splitext(name)[1].lower() or "folder"  # Giả định là folder nếu không có extension
                file_types[ext] = file_types.get(ext, 0) + 1
                size = item.size()
                total_size += size
                file_count += 1

                # Thêm item vào treeview mà không cần is_folder
                iid = self.tree.insert("", "end", values=("☐", name, item.original_path(), size, item.delete_date()))
                self.tree.item(iid, tags=(iid,))
                self.selected_items[iid] = {"selected": False, "item": item}

            self.total_files_label.config(text=f"Total Items: {file_count}")
            self.total_size_label.config(text=f"Total Size: {total_size} bytes")
            self.file_types_label.config(text=f"File Types: {file_types}")

            # Bind click to toggle checkbox
            self.tree.bind("<Button-1>", self.toggle_checkbox)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load recycle bin: {str(e)}")

    def update_list(self, event=None):
        search_term = self.search_entry.get().lower()
        self.tree.delete(*self.tree.get_children())
        self.selected_items = {}

        for item in self.recycle_items:
            name = item.original_filename().lower()
            if search_term in name:
                iid = self.tree.insert("", "end", values=("☐", item.original_filename(), item.original_path(), item.size(), item.delete_date()))
                self.tree.item(iid, tags=(iid,))
                self.selected_items[iid] = {"selected": False, "item": item}

    def toggle_checkbox(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            col = self.tree.identify_column(event.x)
            if col == "#1":  # Select column
                current = self.tree.item(item, "values")[0]
                new_check = "☑" if current == "☐" else "☐"
                values = list(self.tree.item(item, "values"))
                values[0] = new_check
                self.tree.item(item, values=values)
                self.selected_items[item]["selected"] = (new_check == "☑")

    def select_all(self):
        for iid in self.tree.get_children():
            values = list(self.tree.item(iid, "values"))
            values[0] = "☑"
            self.tree.item(iid, values=values)
            self.selected_items[iid]["selected"] = True

    def deselect_all(self):
        for iid in self.tree.get_children():
            values = list(self.tree.item(iid, "values"))
            values[0] = "☐"
            self.tree.item(iid, values=values)
            self.selected_items[iid]["selected"] = False

    def get_selected_items(self):
        return [self.selected_items[iid]["item"] for iid in self.selected_items if self.selected_items[iid]["selected"]]

    def restore_selected(self):
        selected = self.get_selected_items()
        if not selected:
            messagebox.showinfo("Info", "No items selected.")
            return

        for item in selected:
            try:
                item.undelete()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to restore {item.original_filename()}: {str(e)}")

        self.load_recycle_bin()

    def delete_selected(self):
        selected = self.get_selected_items()
        if not selected:
            messagebox.showinfo("Info", "No items selected.")
            return

        confirm = messagebox.askyesno("Confirm", "Are you sure you want to permanently delete selected items?")
        if confirm:
            for item in selected:
                try:
                    # Permanently delete by moving to temp or using shutil
                    path = item.recycle_path()
                    shutil.rmtree(path) if os.path.isdir(path) else os.remove(path)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to delete {item.original_filename()}: {str(e)}")

            self.load_recycle_bin()

    def empty_bin(self):
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to empty the entire Recycle Bin?")
        if confirm:
            try:
                winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to empty recycle bin: {str(e)}")
            self.load_recycle_bin()

if __name__ == "__main__":
    root = tk.Tk()
    app = RecycleBinManager(root)
    root.mainloop()