import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import os
import shutil
from datetime import datetime

class FileExplorerApp(tk.Tk):
    """
    A simple file explorer application with a GUI.

    Features:
    - Navigate directories.
    - View files and folders.
    - Open files.
    - Delete files or folders.
    - Rename files or folders.
    - Copy and paste files/folders.
    - Create new files and folders.
    - Search for files by name.
    - View file/folder properties.
    - Sort files by name, size, or type.
    - Auto-organize files by type.
    """
    def __init__(self):
        super().__init__()
        self.title("File Explorer")
        self.geometry("800x600")

        self.current_path = tk.StringVar(value=os.getcwd())
        self.clipboard = None # Stores path for copy/paste operations
        
        # UI Elements
        # Path Bar and Search
        self.top_frame = tk.Frame(self)
        self.top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.path_label = tk.Label(self.top_frame, text="Current Path:", font=("Arial", 10, "bold"))
        self.path_label.pack(side=tk.LEFT)

        self.path_entry = tk.Entry(self.top_frame, textvariable=self.current_path, state='readonly', relief=tk.FLAT, bd=0)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        self.search_entry = tk.Entry(self.top_frame)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        
        self.search_button = tk.Button(self.top_frame, text="Search", command=self.search_files)
        self.search_button.pack(side=tk.LEFT)

        self.clear_search_button = tk.Button(self.top_frame, text="Clear Search", command=lambda: self.load_directory(self.current_path.get()))
        self.clear_search_button.pack(side=tk.LEFT)

        # File listbox with scrollbar
        self.listbox_frame = tk.Frame(self)
        self.listbox_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.listbox_scrollbar = tk.Scrollbar(self.listbox_frame)
        self.listbox_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_listbox = tk.Listbox(self.listbox_frame, yscrollcommand=self.listbox_scrollbar.set, font=("Courier", 10))
        self.file_listbox.pack(fill=tk.BOTH, expand=True)
        self.listbox_scrollbar.config(command=self.file_listbox.yview)
        
        # Bind double-click event to open/navigate
        self.file_listbox.bind("<Double-1>", self.on_double_click)

        # Button Frame
        self.button_frame = tk.Frame(self)
        self.button_frame.pack(fill=tk.X, padx=10, pady=5)

        self.up_button = tk.Button(self.button_frame, text="Up", command=self.go_up)
        self.up_button.pack(side=tk.LEFT, padx=5)

        self.open_button = tk.Button(self.button_frame, text="Open", command=self.open_selected)
        self.open_button.pack(side=tk.LEFT, padx=5)

        self.copy_button = tk.Button(self.button_frame, text="Copy", command=self.copy_selected)
        self.copy_button.pack(side=tk.LEFT, padx=5)

        self.paste_button = tk.Button(self.button_frame, text="Paste", command=self.paste_selected)
        self.paste_button.pack(side=tk.LEFT, padx=5)

        self.rename_button = tk.Button(self.button_frame, text="Rename", command=self.rename_selected)
        self.rename_button.pack(side=tk.LEFT, padx=5)
        
        self.delete_button = tk.Button(self.button_frame, text="Delete", command=self.delete_selected)
        self.delete_button.pack(side=tk.LEFT, padx=5)

        self.properties_button = tk.Button(self.button_frame, text="Properties", command=self.show_properties)
        self.properties_button.pack(side=tk.LEFT, padx=5)

        self.create_menu = tk.Menubutton(self.button_frame, text="Create", relief=tk.RAISED)
        self.create_menu.pack(side=tk.LEFT, padx=5)
        self.create_menu.menu = tk.Menu(self.create_menu, tearoff=0)
        self.create_menu["menu"] = self.create_menu.menu
        self.create_menu.menu.add_command(label="New Folder", command=self.create_folder)
        self.create_menu.menu.add_command(label="New File", command=self.create_file)

        self.auto_organize_button = tk.Button(self.button_frame, text="Auto-Organize", command=self.auto_organize_files)
        self.auto_organize_button.pack(side=tk.LEFT, padx=5)

        self.sort_menu = tk.Menubutton(self.button_frame, text="Sort By", relief=tk.RAISED)
        self.sort_menu.pack(side=tk.LEFT, padx=5)
        self.sort_menu.menu = tk.Menu(self.sort_menu, tearoff=0)
        self.sort_menu["menu"] = self.sort_menu.menu
        self.sort_menu.menu.add_command(label="Name", command=lambda: self.sort_files("name"))
        self.sort_menu.menu.add_command(label="Size", command=lambda: self.sort_files("size"))
        self.sort_menu.menu.add_command(label="Type", command=lambda: self.sort_files("type"))

        # Initial display
        self.load_directory(self.current_path.get())

    def load_directory(self, path):
        """Loads and displays the contents of a given directory path."""
        try:
            os.chdir(path)
            self.current_path.set(os.getcwd())
            self.file_listbox.delete(0, tk.END)
            
            # Get list of files and directories
            items = os.listdir(path)
            
            # Separate directories and files
            directories = sorted([item for item in items if os.path.isdir(item)])
            files = sorted([item for item in items if os.path.isfile(item)])

            # Display directories first, then files
            for item in directories:
                self.file_listbox.insert(tk.END, f"[DIR] {item}")
            for item in files:
                self.file_listbox.insert(tk.END, f"[FILE] {item}")
        except FileNotFoundError:
            messagebox.showerror("Error", f"Directory not found: {path}")
            os.chdir(os.path.expanduser("~")) # Go back to home directory on error
            self.current_path.set(os.getcwd())
            self.load_directory(self.current_path.get())
        except PermissionError:
            messagebox.showerror("Error", f"Permission denied to access: {path}")
            os.chdir(os.path.dirname(os.getcwd())) # Go back up a directory on error
            self.current_path.set(os.getcwd())
            self.load_directory(self.current_path.get())

    def on_double_click(self, event):
        """Handles double-clicking on a listbox item."""
        selection = self.file_listbox.curselection()
        if not selection:
            return

        item = self.file_listbox.get(selection[0])
        item_path = item.split("] ")[1] # Get item name after the prefix
        
        if item.startswith("[DIR]"):
            # It's a directory, so navigate into it
            new_path = os.path.join(self.current_path.get(), item_path)
            self.load_directory(new_path)
        else:
            # It's a file, so open it
            full_path = os.path.join(self.current_path.get(), item_path)
            self.open_file(full_path)

    def go_up(self):
        """Navigates to the parent directory."""
        parent_path = os.path.dirname(self.current_path.get())
        if parent_path != self.current_path.get():
            self.load_directory(parent_path)

    def open_selected(self):
        """Opens the selected file."""
        selection = self.file_listbox.curselection()
        if not selection:
            return
        
        item = self.file_listbox.get(selection[0])
        if item.startswith("[FILE]"):
            item_path = item.split("] ")[1]
            full_path = os.path.join(self.current_path.get(), item_path)
            self.open_file(full_path)
        else:
            # If it's a directory, navigate into it
            item_path = item.split("] ")[1]
            new_path = os.path.join(self.current_path.get(), item_path)
            self.load_directory(new_path)

    def open_file(self, path):
        """Cross-platform function to open a file."""
        try:
            if os.name == 'nt':  # For Windows
                os.startfile(path)
            elif os.uname()[0] == 'Darwin':  # For macOS
                os.system(f'open "{path}"')
            else:  # For Linux
                os.system(f'xdg-open "{path}"')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file: {e}")

    def delete_selected(self):
        """Deletes the selected file or directory."""
        selection = self.file_listbox.curselection()
        if not selection:
            return

        item = self.file_listbox.get(selection[0])
        item_path = item.split("] ")[1]
        full_path = os.path.join(self.current_path.get(), item_path)

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{item_path}'? This cannot be undone."):
            try:
                if os.path.isdir(full_path):
                    shutil.rmtree(full_path)
                else:
                    os.remove(full_path)
                self.load_directory(self.current_path.get())
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete '{item_path}': {e}")
    
    def rename_selected(self):
        """Renames the selected file or directory."""
        selection = self.file_listbox.curselection()
        if not selection:
            return

        item = self.file_listbox.get(selection[0])
        old_name = item.split("] ")[1]
        full_path = os.path.join(self.current_path.get(), old_name)

        new_name = simpledialog.askstring("Rename", f"Enter new name for '{old_name}':", parent=self)
        
        if new_name and new_name.strip() != "":
            try:
                new_path = os.path.join(self.current_path.get(), new_name)
                os.rename(full_path, new_path)
                self.load_directory(self.current_path.get())
            except FileExistsError:
                messagebox.showerror("Error", f"A file or folder with the name '{new_name}' already exists.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to rename '{old_name}': {e}")

    def copy_selected(self):
        """Copies the selected file or folder to the clipboard."""
        selection = self.file_listbox.curselection()
        if not selection:
            return
        
        item = self.file_listbox.get(selection[0])
        item_path = item.split("] ")[1]
        self.clipboard = os.path.join(self.current_path.get(), item_path)
        messagebox.showinfo("Copied", f"'{item_path}' copied to clipboard.")

    def paste_selected(self):
        """Pastes the item from the clipboard into the current directory."""
        if not self.clipboard:
            messagebox.showinfo("Paste", "Clipboard is empty. Please copy a file or folder first.")
            return

        item_name = os.path.basename(self.clipboard)
        dest_path = os.path.join(self.current_path.get(), item_name)

        if self.clipboard == dest_path or os.path.commonpath([self.clipboard, dest_path]) == self.clipboard:
            messagebox.showerror("Error", "Cannot paste a folder into itself or its subfolder.")
            return

        try:
            if os.path.isdir(self.clipboard):
                # Copy entire directory tree
                shutil.copytree(self.clipboard, dest_path)
            else:
                # Copy single file
                shutil.copy2(self.clipboard, dest_path)
            
            messagebox.showinfo("Success", f"'{item_name}' pasted successfully.")
            self.load_directory(self.current_path.get())
        except Exception as e:
            messagebox.showerror("Error", f"Failed to paste '{item_name}': {e}")
            
    def create_folder(self):
        """Creates a new folder in the current directory."""
        folder_name = simpledialog.askstring("Create Folder", "Enter the name for the new folder:", parent=self)
        if folder_name and folder_name.strip() != "":
            new_folder_path = os.path.join(self.current_path.get(), folder_name)
            try:
                os.mkdir(new_folder_path)
                self.load_directory(self.current_path.get())
            except FileExistsError:
                messagebox.showerror("Error", f"Folder '{folder_name}' already exists.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create folder: {e}")

    def create_file(self):
        """Creates a new empty file in the current directory."""
        file_name = simpledialog.askstring("Create File", "Enter the name for the new file:", parent=self)
        if file_name and file_name.strip() != "":
            new_file_path = os.path.join(self.current_path.get(), file_name)
            try:
                with open(new_file_path, 'a'):
                    os.utime(new_file_path, None)
                self.load_directory(self.current_path.get())
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create file: {e}")

    def auto_organize_files(self):
        """Automatically organizes files in a selected directory into subfolders by file type."""
        directory_to_organize = filedialog.askdirectory(title="Select a folder to organize")

        if not directory_to_organize:
            return

        # Mapping for file extensions to folder names
        file_type_map = {
            'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg'],
            'documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'],
            'videos': ['.mp4', '.mkv', '.mov', '.avi', '.wmv'],
            'audio': ['.mp3', '.wav', '.flac', '.aac'],
            'executables': ['.exe', '.dmg', '.app', '.bat'],
            'archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
            'spreadsheets': ['.xls', '.xlsx', '.csv'],
            'presentations': ['.ppt', '.pptx'],
        }

        organized_count = 0
        
        try:
            for filename in os.listdir(directory_to_organize):
                file_path = os.path.join(directory_to_organize, filename)
                
                # Skip directories and the main script file
                if os.path.isdir(file_path) or filename == os.path.basename(__file__):
                    continue

                # Get the file extension
                _, file_extension = os.path.splitext(filename)
                file_extension = file_extension.lower()

                # Find the destination folder
                destination_folder = None
                for folder_name, extensions in file_type_map.items():
                    if file_extension in extensions:
                        destination_folder = os.path.join(directory_to_organize, folder_name)
                        break
                
                # If no matching folder, put it in 'Others'
                if not destination_folder:
                    destination_folder = os.path.join(directory_to_organize, 'Others')

                # Create the destination folder if it doesn't exist
                if not os.path.exists(destination_folder):
                    os.makedirs(destination_folder)

                # Move the file
                shutil.move(file_path, destination_folder)
                organized_count += 1
            
            messagebox.showinfo("Auto-Organize", f"Successfully organized {organized_count} files in '{os.path.basename(directory_to_organize)}'.")
            self.load_directory(self.current_path.get())
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during organization: {e}")


    def search_files(self):
        """Searches for files and folders by name within the current directory and subdirectories."""
        query = self.search_entry.get().strip().lower()
        if not query:
            messagebox.showinfo("Search", "Please enter a search query.")
            return

        self.file_listbox.delete(0, tk.END)
        found_items = []
        
        # Walk through the directory tree
        for root, dirs, files in os.walk(self.current_path.get()):
            for name in dirs:
                if query in name.lower():
                    rel_path = os.path.relpath(os.path.join(root, name), self.current_path.get())
                    found_items.append(f"[DIR] {rel_path}")
            for name in files:
                if query in name.lower():
                    rel_path = os.path.relpath(os.path.join(root, name), self.current_path.get())
                    found_items.append(f"[FILE] {rel_path}")

        if found_items:
            for item in sorted(found_items):
                self.file_listbox.insert(tk.END, item)
        else:
            self.file_listbox.insert(tk.END, "No items found matching the search query.")

    def show_properties(self):
        """Displays properties of the selected file or folder."""
        selection = self.file_listbox.curselection()
        if not selection:
            messagebox.showinfo("Properties", "Please select a file or folder to view its properties.")
            return

        item = self.file_listbox.get(selection[0])
        item_path = item.split("] ")[1]
        full_path = os.path.join(self.current_path.get(), item_path)

        try:
            stat_info = os.stat(full_path)
            is_dir = os.path.isdir(full_path)
            
            size_kb = stat_info.st_size / 1024
            created = datetime.fromtimestamp(stat_info.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
            modified = datetime.fromtimestamp(stat_info.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            
            properties_text = (
                f"Properties for: {item_path}\n\n"
                f"Type: {'Folder' if is_dir else 'File'}\n"
                f"Size: {size_kb:.2f} KB\n"
                f"Created: {created}\n"
                f"Modified: {modified}\n"
                f"Full Path: {full_path}"
            )
            messagebox.showinfo("Properties", properties_text)
        except FileNotFoundError:
            messagebox.showerror("Error", "Item not found.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get properties: {e}")

    def sort_files(self, sort_by):
        """Sorts the files and folders based on the specified criteria."""
        items = os.listdir(self.current_path.get())
        
        if sort_by == "name":
            items.sort(key=lambda x: x.lower())
        elif sort_by == "size":
            # Sort by file size, directories first (with size 0)
            items.sort(key=lambda x: (os.path.isdir(x), os.stat(x).st_size))
        elif sort_by == "type":
            # Sort by file extension
            items.sort(key=lambda x: os.path.splitext(x)[1].lower())
            
        self.file_listbox.delete(0, tk.END)
        for item in items:
            if os.path.isdir(item):
                self.file_listbox.insert(tk.END, f"[DIR] {item}")
            else:
                self.file_listbox.insert(tk.END, f"[FILE] {item}")

if __name__ == "__main__":
    app = FileExplorerApp()
    app.mainloop()