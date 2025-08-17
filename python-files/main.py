#!/usr/bin/env python3
"""
MacOS Disk Image Manager - PowerISO alternative for Mac
Handles .img and .iso files for floppy disks, hard disk images, and CD/DVD images
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import threading

class DiskImageManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Disk Image Manager")
        self.root.geometry("800x600")
        
        self.current_image = None
        self.mount_point = None
        self.image_contents = []
        self.unsaved_changes = False
        
        self.setup_ui()
        
    def setup_ui(self):
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Image...", command=self.new_image)
        file_menu.add_command(label="Open Image...", command=self.open_image)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Toolbar
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar, text="New", command=self.new_image).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Open", command=self.open_image).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Add Files", command=self.add_files).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Add Folder", command=self.add_folder).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Extract", command=self.extract_files).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Delete", command=self.delete_selected).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="New Folder", command=self.create_folder).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Format", command=self.format_image).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Save", command=self.save_image).pack(side=tk.LEFT, padx=2)
        
        # Main content area
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Image info
        info_frame = ttk.LabelFrame(main_frame, text="Image Information")
        info_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.info_label = ttk.Label(info_frame, text="No image loaded")
        self.info_label.pack(padx=10, pady=5)
        
        # File tree
        tree_frame = ttk.LabelFrame(main_frame, text="Contents")
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview with scrollbars
        tree_container = ttk.Frame(tree_frame)
        tree_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.tree = ttk.Treeview(tree_container, columns=('Size', 'Type'), show='tree headings')
        self.tree.heading('#0', text='Name')
        self.tree.heading('Size', text='Size')
        self.tree.heading('Type', text='Type')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_container, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack tree and scrollbars
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        
        # Context menu for tree
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Create Folder", command=self.create_folder)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Delete", command=self.delete_selected)
        
        self.tree.bind("<Button-2>", self.show_context_menu)  # Right click on Mac
        self.tree.bind("<Control-Button-1>", self.show_context_menu)  # Ctrl+click on Mac
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
    def update_status(self, message):
        self.status_var.set(message)
        self.root.update_idletasks()
        
    def new_image(self):
        dialog = ImageCreationDialog(self.root)
        if dialog.result:
            image_path, image_type, size_mb = dialog.result
            self.create_image(image_path, image_type, size_mb)
            
    def create_image(self, image_path, image_type, size_mb):
        try:
            self.update_status("Creating image...")
            
            if image_type == "Floppy (1.44MB)":
                # Create 1.44MB floppy disk image
                subprocess.run(['hdiutil', 'create', '-size', '1440k', '-fs', 'MS-DOS FAT12', 
                              '-volname', 'FLOPPY', '-type', 'UDIF', image_path], check=True)
            elif image_type == "Floppy (2.88MB)":
                # Create 2.88MB floppy disk image
                subprocess.run(['hdiutil', 'create', '-size', '2880k', '-fs', 'MS-DOS FAT12', 
                              '-volname', 'FLOPPY', '-type', 'UDIF', image_path], check=True)
            elif image_type == "Hard Disk":
                # Create hard disk image
                subprocess.run(['hdiutil', 'create', '-size', f'{size_mb}m', '-fs', 'HFS+', 
                              '-volname', 'DISK', '-type', 'UDIF', image_path], check=True)
            elif image_type == "CD/DVD (ISO)":
                # Create empty ISO - we'll use a different approach
                self.create_empty_iso(image_path, size_mb)
            
            self.open_image_file(image_path)
            self.update_status("Image created successfully")
            
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to create image: {e}")
            self.update_status("Ready")
        except Exception as e:
            messagebox.showerror("Error", f"Error creating image: {e}")
            self.update_status("Ready")
            
    def create_empty_iso(self, image_path, size_mb):
        # Create a temporary directory structure and build ISO
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create empty directory structure
            os.makedirs(os.path.join(temp_dir, "empty_folder"), exist_ok=True)
            
            # Use hdiutil to create ISO
            subprocess.run(['hdiutil', 'makehybrid', '-iso', '-joliet', '-o', 
                          image_path.replace('.iso', ''), temp_dir], check=True)
            
            # Rename to .iso if needed
            if not image_path.endswith('.iso'):
                shutil.move(image_path.replace('.iso', '') + '.iso', image_path)
    
    def open_image(self):
        file_path = filedialog.askopenfilename(
            title="Open Disk Image",
            filetypes=[
                ("Disk Images", "*.img *.iso *.dmg"),
                ("IMG files", "*.img"),
                ("ISO files", "*.iso"),
                ("DMG files", "*.dmg"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.open_image_file(file_path)
    
    def open_image_file(self, file_path):
        try:
            self.update_status("Opening image...")
            
            # Unmount previous image if any
            if self.mount_point:
                self.unmount_image()
            
            self.current_image = file_path
            self.mount_image()
            self.refresh_contents()
            
            # Update info
            file_size = os.path.getsize(file_path)
            size_str = self.format_size(file_size)
            image_name = os.path.basename(file_path)
            self.info_label.config(text=f"Image: {image_name} ({size_str})")
            
            self.update_status("Image opened successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open image: {e}")
            self.update_status("Ready")
    
    def mount_image(self):
        if not self.current_image:
            return
            
        try:
            # Mount the image
            result = subprocess.run(['hdiutil', 'attach', '-nobrowse', '-mountpoint', 
                                   f'/tmp/diskimg_{os.getpid()}', self.current_image], 
                                  capture_output=True, text=True, check=True)
            
            # Find mount point
            for line in result.stdout.split('\n'):
                if '/tmp/diskimg_' in line:
                    self.mount_point = line.split()[-1]
                    break
                    
        except subprocess.CalledProcessError:
            # If mounting fails, try read-only
            try:
                result = subprocess.run(['hdiutil', 'attach', '-readonly', '-nobrowse', 
                                       '-mountpoint', f'/tmp/diskimg_{os.getpid()}', 
                                       self.current_image], 
                                      capture_output=True, text=True, check=True)
                
                for line in result.stdout.split('\n'):
                    if '/tmp/diskimg_' in line:
                        self.mount_point = line.split()[-1]
                        break
            except subprocess.CalledProcessError as e:
                raise Exception(f"Could not mount image: {e}")
    
    def unmount_image(self):
        if self.mount_point:
            try:
                subprocess.run(['hdiutil', 'detach', self.mount_point], 
                             capture_output=True, check=True)
            except subprocess.CalledProcessError:
                pass
            self.mount_point = None
    
    def refresh_contents(self):
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        if not self.mount_point or not os.path.exists(self.mount_point):
            return
            
        try:
            self.populate_tree(self.mount_point, "")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read image contents: {e}")
    
    def populate_tree(self, path, parent_id):
        try:
            items = os.listdir(path)
            items.sort()
            
            for item in items:
                if item.startswith('.'):
                    continue
                    
                item_path = os.path.join(path, item)
                
                if os.path.isdir(item_path):
                    # Directory
                    item_id = self.tree.insert(parent_id, tk.END, text=item, 
                                             values=("", "Folder"))
                    # Recursively populate subdirectories
                    self.populate_tree(item_path, item_id)
                else:
                    # File
                    size = os.path.getsize(item_path)
                    size_str = self.format_size(size)
                    self.tree.insert(parent_id, tk.END, text=item, 
                                   values=(size_str, "File"))
                                   
        except PermissionError:
            pass
    
    def show_context_menu(self, event):
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def create_folder(self):
        if not self.mount_point:
            messagebox.showwarning("Warning", "No image loaded")
            return
            
        folder_name = simpledialog.askstring("Create Folder", "Enter folder name:")
        if folder_name:
            try:
                folder_path = os.path.join(self.mount_point, folder_name)
                os.makedirs(folder_path, exist_ok=True)
                self.refresh_contents()
                self.unsaved_changes = True
                self.update_title()
                self.update_status("Folder created")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create folder: {e}")
    
    def update_title(self):
        title = "Disk Image Manager"
        if self.current_image:
            title += f" - {os.path.basename(self.current_image)}"
            if self.unsaved_changes:
                title += " *"
        self.root.title(title)
    
    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    def add_files(self):
        if not self.mount_point:
            messagebox.showwarning("Warning", "No image loaded")
            return
            
        files = filedialog.askopenfilenames(title="Select files to add")
        if files:
            self.copy_files_to_image(files)
    
    def add_folder(self):
        if not self.mount_point:
            messagebox.showwarning("Warning", "No image loaded")
            return
            
        folder = filedialog.askdirectory(title="Select folder to add")
        if folder:
            self.copy_folder_to_image(folder)
    
    def copy_files_to_image(self, files):
        try:
            self.update_status("Adding files...")
            for file_path in files:
                dest_path = os.path.join(self.mount_point, os.path.basename(file_path))
                shutil.copy2(file_path, dest_path)
            
            self.refresh_contents()
            self.unsaved_changes = True
            self.update_title()
            self.update_status("Files added successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add files: {e}")
            self.update_status("Ready")
    
    def copy_folder_to_image(self, folder_path):
        try:
            self.update_status("Adding folder...")
            dest_path = os.path.join(self.mount_point, os.path.basename(folder_path))
            shutil.copytree(folder_path, dest_path)
            
            self.refresh_contents()
            self.update_status("Folder added successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add folder: {e}")
            self.update_status("Ready")
    
    def extract_files(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "No files selected")
            return
            
        dest_folder = filedialog.askdirectory(title="Select destination folder")
        if dest_folder:
            self.extract_selected_files(selected_items, dest_folder)
    
    def extract_selected_files(self, selected_items, dest_folder):
        try:
            self.update_status("Extracting files...")
            
            for item_id in selected_items:
                item_name = self.tree.item(item_id, 'text')
                source_path = os.path.join(self.mount_point, item_name)
                dest_path = os.path.join(dest_folder, item_name)
                
                if os.path.isdir(source_path):
                    shutil.copytree(source_path, dest_path)
                else:
                    shutil.copy2(source_path, dest_path)
            
            self.update_status("Files extracted successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to extract files: {e}")
            self.update_status("Ready")
    
    def delete_selected(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "No files selected")
            return
            
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected items?"):
            self.delete_files(selected_items)
    
    def delete_files(self, selected_items):
        try:
            self.update_status("Deleting files...")
            
            for item_id in selected_items:
                item_name = self.tree.item(item_id, 'text')
                file_path = os.path.join(self.mount_point, item_name)
                
                if os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                else:
                    os.remove(file_path)
            
            self.refresh_contents()
            self.unsaved_changes = True
            self.update_title()
            self.update_status("Files deleted successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete files: {e}")
            self.update_status("Ready")
    
    def format_image(self):
        if not self.current_image:
            messagebox.showwarning("Warning", "No image loaded")
            return
            
        if messagebox.askyesno("Confirm Format", 
                              "Are you sure you want to format this image? All data will be lost!"):
            self.format_current_image()
    
    def format_current_image(self):
        try:
            self.update_status("Formatting image...")
            
            # Unmount first
            self.unmount_image()
            
            # Determine format based on image type
            if self.current_image.lower().endswith('.iso'):
                # For ISO, we need to recreate it
                size_mb = os.path.getsize(self.current_image) // (1024 * 1024)
                self.create_empty_iso(self.current_image, size_mb)
            else:
                # Get current image info to determine proper format
                image_info = subprocess.run(['hdiutil', 'imageinfo', self.current_image], 
                                          capture_output=True, text=True)
                
                # Determine if it's a floppy based on size
                file_size = os.path.getsize(self.current_image)
                if file_size <= 1474560:  # 1.44MB floppy
                    # Recreate as floppy
                    temp_path = self.current_image + ".temp"
                    subprocess.run(['hdiutil', 'create', '-size', '1440k', '-fs', 'MS-DOS FAT12', 
                                  '-volname', 'FLOPPY', '-type', 'UDIF', temp_path], check=True)
                    os.replace(temp_path, self.current_image)
                elif file_size <= 2949120:  # 2.88MB floppy
                    # Recreate as 2.88MB floppy
                    temp_path = self.current_image + ".temp"
                    subprocess.run(['hdiutil', 'create', '-size', '2880k', '-fs', 'MS-DOS FAT12', 
                                  '-volname', 'FLOPPY', '-type', 'UDIF', temp_path], check=True)
                    os.replace(temp_path, self.current_image)
                else:
                    # Hard disk - use erase
                    subprocess.run(['hdiutil', 'erase', '-format', 'HFS+', 
                                  self.current_image], check=True)
            
            # Remount
            self.mount_image()
            self.refresh_contents()
            self.unsaved_changes = False
            self.update_title()
            
            self.update_status("Image formatted successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to format image: {e}")
            self.update_status("Ready")
    
    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        if self.mount_point:
            self.unmount_image()
        self.root.destroy()


class ImageCreationDialog:
    def __init__(self, parent):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Create New Image")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (300 // 2)
        self.dialog.geometry(f"400x300+{x}+{y}")
        
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Image type
        ttk.Label(main_frame, text="Image Type:").pack(anchor=tk.W)
        self.image_type = tk.StringVar(value="Floppy (1.44MB)")
        type_frame = ttk.Frame(main_frame)
        type_frame.pack(fill=tk.X, pady=(5, 15))
        
        ttk.Radiobutton(type_frame, text="Floppy Disk (1.44MB)", 
                       variable=self.image_type, value="Floppy (1.44MB)").pack(anchor=tk.W)
        ttk.Radiobutton(type_frame, text="Floppy Disk (2.88MB)", 
                       variable=self.image_type, value="Floppy (2.88MB)").pack(anchor=tk.W)
        ttk.Radiobutton(type_frame, text="Hard Disk Image", 
                       variable=self.image_type, value="Hard Disk").pack(anchor=tk.W)
        ttk.Radiobutton(type_frame, text="CD/DVD (ISO)", 
                       variable=self.image_type, value="CD/DVD (ISO)").pack(anchor=tk.W)
        
        # Size (for hard disk and ISO)
        size_frame = ttk.Frame(main_frame)
        size_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(size_frame, text="Size (MB):").pack(anchor=tk.W)
        self.size_var = tk.StringVar(value="100")
        size_entry = ttk.Entry(size_frame, textvariable=self.size_var)
        size_entry.pack(fill=tk.X, pady=(5, 0))
        
        # File path
        ttk.Label(main_frame, text="Save As:").pack(anchor=tk.W)
        path_frame = ttk.Frame(main_frame)
        path_frame.pack(fill=tk.X, pady=(5, 15))
        
        self.path_var = tk.StringVar()
        path_entry = ttk.Entry(path_frame, textvariable=self.path_var)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(path_frame, text="Browse...", 
                  command=self.browse_file).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="Create", 
                  command=self.create).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="Cancel", 
                  command=self.cancel).pack(side=tk.RIGHT, padx=(5, 0))
        
    def browse_file(self):
        image_type = self.image_type.get()
        
        if "ISO" in image_type:
            filetypes = [("ISO files", "*.iso"), ("All files", "*.*")]
            default_ext = ".iso"
        else:
            filetypes = [("IMG files", "*.img"), ("All files", "*.*")]
            default_ext = ".img"
        
        file_path = filedialog.asksaveasfilename(
            title="Save Image As",
            filetypes=filetypes,
            defaultextension=default_ext
        )
        
        if file_path:
            self.path_var.set(file_path)
    
    def create(self):
        image_path = self.path_var.get().strip()
        if not image_path:
            messagebox.showerror("Error", "Please specify a file path")
            return
        
        image_type = self.image_type.get()
        
        # For floppy disks, size is fixed
        if "Floppy" in image_type:
            size_mb = 1.44 if "1.44MB" in image_type else 2.88
        else:
            # For hard disk and ISO, validate size input
            try:
                size_mb = float(self.size_var.get())
                if size_mb <= 0:
                    raise ValueError()
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid size in MB")
                return
        
        self.result = (image_path, image_type, size_mb)
        self.dialog.destroy()
    
    def cancel(self):
        self.dialog.destroy()


if __name__ == "__main__":
    # Check if running on macOS
    if sys.platform != "darwin":
        print("This application is designed for macOS and requires hdiutil.")
        sys.exit(1)
    
    app = DiskImageManager()
    app.run()
