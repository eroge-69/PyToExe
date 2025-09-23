import os
import json
import tkinter as tk
from tkinter import ttk, messagebox
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
from PIL import Image, ImageTk

# Network paths to monitor
network_paths = [
    r"\\192.168.29.78\Design\To Process New",
    r"\\192.168.29.134\Album 2\Album and banner\Online"
]

# JSON file path
save_file = r"\\192.168.29.134\Design\Backup\MISC\Unnatesh - Do Not Delete\DO NOT DELETE\folders.json"

# Ensure the directory for save_file exists
os.makedirs(os.path.dirname(save_file), exist_ok=True)

def load_folders(save_file):
    """Load existing folders from JSON"""
    try:
        if not os.path.exists(save_file):
            messagebox.showerror("Error", f"JSON file not found at {save_file}. Please run a full scan.")
            return []
        with open(save_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        messagebox.showerror("Error", f"Error loading JSON: {e}")
        return []

def save_folders(folders, save_file):
    """Save folders list to JSON"""
    try:
        with open(save_file, 'w') as f:
            json.dump(folders, f, indent=4)
        print(f"Saved {len(folders)} folders to {save_file}")
    except Exception as e:
        messagebox.showerror("Error", f"Error saving JSON: {e}")

def search_folders(query, folders):
    """Search folders by name, sort by path depth (outside first)"""
    if not query:
        return []
    query = query.lower()
    results = [item for item in folders if query in item['name'].lower()]
    results.sort(key=lambda x: x['path'].count('\\'))
    return results

class FolderEventHandler(FileSystemEventHandler):
    """Handle file system events for new and deleted folders"""
    def __init__(self, folders, save_file, listbox, entry):
        self.folders = folders
        self.save_file = save_file
        self.listbox = listbox
        self.entry = entry
        self.existing_paths = {item['path'] for item in folders}

    def on_created(self, event):
        """Handle folder creation events"""
        if not event.is_directory:
            return
        folder_path = event.src_path
        folder_name = os.path.basename(folder_path)
        if folder_path not in self.existing_paths:
            self.folders.append({'name': folder_name, 'path': folder_path})
            self.existing_paths.add(folder_path)
            print(f"New folder detected: {folder_name} -> {folder_path}")
            save_folders(self.folders, self.save_file)
            # Update listbox if there's an active search
            query = self.entry.get()
            if query:
                results = search_folders(query, self.folders)
                self.listbox.delete(*self.listbox.get_children())
                for i, item in enumerate(results):
                    display_text = self.format_display_text(item)
                    self.listbox.insert("", tk.END, values=display_text, tags=('even' if i % 2 == 0 else 'odd',))

    def on_deleted(self, event):
        """Handle folder deletion events"""
        if not event.is_directory:
            return
        folder_path = event.src_path
        if folder_path in self.existing_paths:
            self.folders[:] = [item for item in self.folders if item['path'] != folder_path]
            self.existing_paths.remove(folder_path)
            print(f"Folder deleted: {folder_path}")
            save_folders(self.folders, self.save_file)
            # Update listbox if there's an active search
            query = self.entry.get()
            if query:
                results = search_folders(query, self.folders)
                self.listbox.delete(*self.listbox.get_children())
                for i, item in enumerate(results):
                    display_text = self.format_display_text(item)
                    self.listbox.insert("", tk.END, values=display_text, tags=('even' if i % 2 == 0 else 'odd',))

    def format_display_text(self, item):
        """Format display text to show end of path"""
        path = item['path']
        max_length = 60  # Adjust based on column width
        if len(path) > max_length:
            path = "..." + path[-(max_length-3):]
        return ("", item['name'], path) if folder_icon is None else (folder_icon, item['name'], path)

def start_monitoring(folders, save_file, listbox, entry):
    """Start monitoring network paths for folder events"""
    event_handler = FolderEventHandler(folders, save_file, listbox, entry)
    observer = Observer()
    for path in network_paths:
        try:
            if os.path.exists(path):
                observer.schedule(event_handler, path, recursive=True)
                print(f"Monitoring {path}")
            else:
                messagebox.showwarning("Warning", f"Path inaccessible: {path}")
        except Exception as e:
            messagebox.showerror("Error", f"Error accessing {path}: {e}")
    observer.start()
    return observer

def full_scan(network_paths, save_file, listbox, entry):
    """Perform a full scan to rebuild the JSON file"""
    folders = []
    existing_paths = set()
    new_count = 0
    for base_path in network_paths:
        try:
            for root, dirs, files in os.walk(base_path):
                for d in dirs:
                    folder_path = os.path.join(root, d)
                    if folder_path not in existing_paths:
                        folders.append({'name': d, 'path': folder_path})
                        existing_paths.add(folder_path)
                        new_count += 1
                        print(f"Full scan - Adding: {d} -> {folder_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Error scanning {base_path}: {e}")
    save_folders(folders, save_file)
    print(f"Full scan added {new_count} new folders.")
    # Update listbox if there's an active search
    query = entry.get()
    if query:
        results = search_folders(query, folders)
        listbox.delete(*listbox.get_children())
        for i, item in enumerate(results):
            display_text = FolderEventHandler(folders, save_file, listbox, entry).format_display_text(item)
            listbox.insert("", tk.END, values=display_text, tags=('even' if i % 2 == 0 else 'odd',))
    return folders

# Tkinter app
root = tk.Tk()
root.title("Folder Search")
root.geometry("1000x600")
root.minsize(600, 400)  # Set minimum window size
root.configure(bg="#1a1a1a")

# Custom styles
style = ttk.Style()
style.theme_use('clam')
style.configure("TEntry", fieldbackground="#2e2e2e", foreground="#ffffff", padding=10, font=("Segoe UI", 12))
style.configure("TButton", background="#0078d7", foreground="#ffffff", font=("Segoe UI", 12, "bold"), padding=10)
style.map("TButton", background=[("active", "#005ea2")])
style.configure("TLabel", background="#1a1a1a", foreground="#ffffff", font=("Segoe UI", 14, "bold"))
style.configure("Treeview", background="#2e2e2e", fieldbackground="#2e2e2e", foreground="#ffffff", rowheight=30, font=("Segoe UI", 11))
style.configure("Treeview.Heading", background="#0078d7", foreground="#ffffff", font=("Segoe UI", 12, "bold"))

# Load folder icon
try:
    folder_img = Image.open("folder_icon.png")  # Ensure you have a 16x16 folder icon file
    folder_img = folder_img.resize((16, 16), Image.LANCZOS)
    folder_icon = ImageTk.PhotoImage(folder_img)
except Exception as e:
    print(f"Error loading icon: {e}")
    folder_icon = None

# Header
header = ttk.Label(root, text="Type your order - Unnatesh", style="TLabel")
header.pack(pady=10, fill=tk.X)

# Search entry
entry_frame = tk.Frame(root, bg="#1a1a1a")
entry_frame.pack(pady=10, padx=20, fill=tk.X)
entry = ttk.Entry(entry_frame, style="TEntry")
entry.pack(fill=tk.X, padx=(0, 10), side=tk.LEFT, expand=True)
clear_btn = ttk.Button(entry_frame, text="Clear", command=lambda: entry.delete(0, tk.END), style="TButton")
clear_btn.pack(side=tk.RIGHT)

# Listbox with scrollbar (using Treeview for better styling)
frame = tk.Frame(root, bg="#1a1a1a")
frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
scrollbar = ttk.Scrollbar(frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
listbox = ttk.Treeview(frame, columns=("Icon", "Folder", "Path"), show="headings", selectmode="extended", yscrollcommand=scrollbar.set)
listbox.heading("Icon", text="")
listbox.heading("Folder", text="Folder Name")
listbox.heading("Path", text="Path")
listbox.column("Icon", width=30, anchor="center")
listbox.column("Folder", width=300, stretch=True)
listbox.column("Path", width=600, anchor="e", stretch=True)  # Align path to right
listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.config(command=listbox.yview)
listbox.tag_configure('even', background='#2e2e2e')
listbox.tag_configure('odd', background='#3a3a3a')

# Adjust column widths on window resize
def resize_columns(event):
    total_width = listbox.winfo_width()
    icon_width = 30
    folder_width = int(total_width * 0.3)  # 30% for folder name
    path_width = total_width - icon_width - folder_width - 20  # Adjust for scrollbar
    listbox.column("Icon", width=icon_width)
    listbox.column("Folder", width=max(200, folder_width))
    listbox.column("Path", width=max(400, path_width))

root.bind("<Configure>", resize_columns)

# Load folders from JSON
folders = load_folders(save_file)

# Start monitoring
observer = start_monitoring(folders, save_file, listbox, entry)

# Debounce search
search_timer = None
def debounce_search():
    global search_timer
    if search_timer:
        search_timer.cancel()
    search_timer = threading.Timer(0.3, update_list)  # 300ms delay
    search_timer.start()

def update_list():
    query = entry.get()
    results = search_folders(query, folders)
    listbox.delete(*listbox.get_children())
    for i, item in enumerate(results):
        display_text = FolderEventHandler(folders, save_file, listbox, entry).format_display_text(item)
        listbox.insert("", tk.END, values=display_text, tags=('even' if i % 2 == 0 else 'odd',))

entry.bind("<KeyRelease>", lambda event: debounce_search())

# Open selected folders on double-click
def open_folder(event):
    selections = listbox.selection()
    if not selections:
        return
    # Confirm if opening many folders
    if len(selections) > 5:
        if not messagebox.askyesno("Confirm", f"You are about to open {len(selections)} folders. Continue?"):
            return
    errors = []
    for item in selections:
        path = listbox.item(item)['values'][2]  # Path is in the third column
        # If path is truncated, retrieve full path from folders list
        full_path = next((item['path'] for item in folders if item['path'].endswith(path.lstrip("..."))), path)
        try:
            os.startfile(full_path)
        except Exception as e:
            errors.append(f"{full_path}: {e}")
    if errors:
        messagebox.showerror("Error", "Could not open some folders:\n" + "\n".join(errors))

listbox.bind("<Double-Button-1>", open_folder)

# Buttons
button_frame = tk.Frame(root, bg="#1a1a1a")
button_frame.pack(pady=10, fill=tk.X)
rescan_btn = ttk.Button(button_frame, text="Force Full Rescan", command=lambda: globals().update(folders=full_scan(network_paths, save_file, listbox, entry)), style="TButton")
rescan_btn.pack(side=tk.LEFT, padx=5)
refresh_btn = ttk.Button(button_frame, text="Refresh List", command=update_list, style="TButton")
refresh_btn.pack(side=tk.LEFT, padx=5)

# Stop observer on window close
def on_closing():
    observer.stop()
    observer.join()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()