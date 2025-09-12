import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageFilter
import os
import sys
from pathlib import Path

class ImageExplorer:
    def __init__(self, root):
        self.root = root
        self.root.title("Windows 11 Image Explorer")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Set application icon (if available)
        try:
            if getattr(sys, 'frozen', False):
                application_path = sys._MEIPASS
            else:
                application_path = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(application_path, "icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass
        
        # Configure style to mimic Windows 11
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        
        # Variables
        self.current_folder = os.path.expanduser("~")
        self.images = []
        self.current_index = 0
        self.thumb_size = 128
        self.view_mode = 'thumbnails'
        
        # Create UI
        self.create_menu()
        self.create_toolbar()
        self.create_main_frame()
        self.create_statusbar()
        
        # Bind shortcuts
        self.bind_shortcuts()
        
        # Load initial directory
        self.load_directory(self.current_folder)
    
    def configure_styles(self):
        # Configure styles to resemble Windows 11
        self.style.configure('TFrame', background='#f5f5f5')
        self.style.configure('TLabel', background='#f5f5f5', foreground='#000000')
        self.style.configure('TButton', background='#ffffff', foreground='#000000')
        self.style.configure('Treeview', background='#ffffff', fieldbackground='#ffffff')
        self.style.configure('Treeview.Heading', background='#e5e5e5', foreground='#000000')
        self.style.map('Treeview', background=[('selected', '#0078d4')], 
                      foreground=[('selected', 'white')])
        self.style.configure('TScrollbar', background='#e5e5e5')
        self.style.configure('TMenubutton', background='#ffffff')
        self.style.configure('TMenu', background='#ffffff')
        self.style.configure('Title.TLabel', font=('Segoe UI', 10, 'bold'))
    
    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open Folder", command=self.open_folder, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Alt+F4")
        menubar.add_cascade(label="File", menu=file_menu)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Thumbnails", command=lambda: self.set_view_mode('thumbnails'))
        view_menu.add_command(label="Details", command=lambda: self.set_view_mode('details'))
        view_menu.add_separator()
        view_menu.add_command(label="Increase Thumbnails", command=self.increase_thumb_size, accelerator="Ctrl++")
        view_menu.add_command(label="Decrease Thumbnails", command=self.decrease_thumb_size, accelerator="Ctrl+-")
        menubar.add_cascade(label="View", menu=view_menu)
        
        # Go menu (like ACDSee)
        go_menu = tk.Menu(menubar, tearoff=0)
        go_menu.add_command(label="Previous Image", command=self.prev_image, accelerator="Left")
        go_menu.add_command(label="Next Image", command=self.next_image, accelerator="Right")
        go_menu.add_separator()
        go_menu.add_command(label="First Image", command=self.first_image, accelerator="Home")
        go_menu.add_command(label="Last Image", command=self.last_image, accelerator="End")
        menubar.add_cascade(label="Go", menu=go_menu)
        
        self.root.config(menu=menubar)
    
    def create_toolbar(self):
        toolbar = ttk.Frame(self.root, style='Toolbar.TFrame')
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        # Navigation buttons
        ttk.Button(toolbar, text="↑", command=self.go_up, width=3).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(toolbar, text="←", command=self.prev_image, width=3).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(toolbar, text="→", command=self.next_image, width=3).pack(side=tk.LEFT, padx=2, pady=2)
        
        # Address bar
        self.address_var = tk.StringVar()
        self.address_entry = ttk.Entry(toolbar, textvariable=self.address_var, width=50)
        self.address_entry.pack(side=tk.LEFT, padx=10, pady=2, fill=tk.X, expand=True)
        self.address_entry.bind('<Return>', self.navigate_to_address)
        
        # View buttons
        ttk.Button(toolbar, text="Thumbnails", command=lambda: self.set_view_mode('thumbnails')).pack(side=tk.RIGHT, padx=2, pady=2)
        ttk.Button(toolbar, text="Details", command=lambda: self.set_view_mode('details')).pack(side=tk.RIGHT, padx=2, pady=2)
        
        self.style.configure('Toolbar.TFrame', background='#e5e5e5')
    
    def create_main_frame(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Split view - left for folder tree, right for content
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Folder tree
        tree_frame = ttk.Frame(paned_window, width=200)
        self.tree = ttk.Treeview(tree_frame)
        tree_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Image/content area
        content_frame = ttk.Frame(paned_window)
        
        # Thumbnail view (default)
        self.thumb_frame = ttk.Frame(content_frame)
        self.thumb_canvas = tk.Canvas(self.thumb_frame, bg='white')
        thumb_scroll = ttk.Scrollbar(self.thumb_frame, orient=tk.VERTICAL, command=self.thumb_canvas.yview)
        self.thumb_canvas.configure(yscrollcommand=thumb_scroll.set)
        thumb_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.thumb_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Detail view (hidden initially)
        self.detail_frame = ttk.Frame(content_frame)
        columns = ('name', 'size', 'type', 'modified')
        self.detail_tree = ttk.Treeview(self.detail_frame, columns=columns, show='tree headings')
        self.detail_tree.heading('name', text='Name', anchor=tk.W)
        self.detail_tree.heading('size', text='Size', anchor=tk.W)
        self.detail_tree.heading('type', text='Type', anchor=tk.W)
        self.detail_tree.heading('modified', text='Modified', anchor=tk.W)
        
        detail_scroll = ttk.Scrollbar(self.detail_frame, orient=tk.VERTICAL, command=self.detail_tree.yview)
        self.detail_tree.configure(yscrollcommand=detail_scroll.set)
        detail_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.detail_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Preview frame (hidden initially)
        self.preview_frame = ttk.Frame(content_frame)
        self.preview_label = ttk.Label(self.preview_frame, text="Image Preview")
        self.preview_label.pack(fill=tk.BOTH, expand=True)
        
        # Pack the default view
        self.thumb_frame.pack(fill=tk.BOTH, expand=True)
        self.detail_frame.pack_forget()
        self.preview_frame.pack_forget()
        
        paned_window.add(tree_frame)
        paned_window.add(content_frame)
        
        # Configure tree
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        self.detail_tree.bind('<Double-1>', self.on_detail_double_click)
        
        # Populate tree with drives/directories
        self.populate_tree()
    
    def create_statusbar(self):
        self.statusbar = ttk.Frame(self.root)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_left = ttk.Label(self.statusbar, text="Ready")
        self.status_left.pack(side=tk.LEFT, padx=5)
        
        self.status_right = ttk.Label(self.statusbar, text="0 items")
        self.status_right.pack(side=tk.RIGHT, padx=5)
    
    def bind_shortcuts(self):
        # Navigation shortcuts
        self.root.bind('<Left>', lambda e: self.prev_image())
        self.root.bind('<Right>', lambda e: self.next_image())
        self.root.bind('<Home>', lambda e: self.first_image())
        self.root.bind('<End>', lambda e: self.last_image())
        
        # Zoom shortcuts
        self.root.bind('<Control-plus>', lambda e: self.increase_thumb_size())
        self.root.bind('<Control-minus>', lambda e: self.decrease_thumb_size())
        
        # Open folder shortcut
        self.root.bind('<Control-o>', lambda e: self.open_folder())
        
        # View mode shortcuts
        self.root.bind('<F5>', lambda e: self.refresh())
    
    def populate_tree(self):
        # Add drives to the tree
        self.tree.delete(*self.tree.get_children())
        if os.name == 'nt':  # Windows
            import string
            drives = ['%s:' % d for d in string.ascii_uppercase if os.path.exists('%s:' % d)]
            for drive in drives:
                self.tree.insert('', 'end', drive, text=drive, values=[drive])
        else:  # Linux/Mac
            self.tree.insert('', 'end', '/', text='/', values=['/'])
        
        # Set the initial selection to the user's home directory
        self.tree.selection_set(os.path.expanduser("~"))
        self.load_directory(os.path.expanduser("~"))
    
    def on_tree_select(self, event):
        if self.tree.selection():
            item = self.tree.selection()[0]
            path = self.tree.item(item, 'values')[0]
            if os.path.isdir(path):
                self.load_directory(path)
    
    def on_detail_double_click(self, event):
        if self.detail_tree.selection():
            item = self.detail_tree.selection()[0]
            values = self.detail_tree.item(item, 'values')
            if values:
                filename = values[0]
                path = os.path.join(self.current_folder, filename)
                if os.path.isdir(path):
                    self.load_directory(path)
                else:
                    self.open_image(path)
    
    def load_directory(self, path):
        try:
            self.current_folder = path
            self.address_var.set(path)
            
            # Clear current images
            self.images = []
            
            # List directory contents
            items = os.listdir(path)
            
            # Filter images and folders
            image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp')
            folders = [item for item in items if os.path.isdir(os.path.join(path, item))]
            images = [item for item in items if item.lower().endswith(image_extensions)]
            
            # Update status bar
            self.status_right.config(text=f"{len(items)} items")
            
            # Update views
            if self.view_mode == 'details':
                self.update_detail_view(folders + images)
            else:
                self.update_thumb_view(folders + images)
                
        except PermissionError:
            messagebox.showerror("Permission Denied", f"Cannot access {path}")
        except Exception as e:
            messagebox.showerror("Error", f"Error loading directory: {str(e)}")
    
    def update_thumb_view(self, items):
        # Clear the canvas
        self.thumb_canvas.delete("all")
        
        # Calculate layout
        canvas_width = self.thumb_canvas.winfo_width()
        if canvas_width < 10:  # Canvas not yet visible
            self.root.after(100, lambda: self.update_thumb_view(items))
            return
            
        cols = max(1, canvas_width // (self.thumb_size + 20))
        x, y = 10, 10
        
        for i, item in enumerate(items):
            item_path = os.path.join(self.current_folder, item)
            
            # Create thumbnail frame
            frame = ttk.Frame(self.thumb_canvas)
            
            # Check if it's a directory or image
            if os.path.isdir(item_path):
                # Folder icon
                img_label = ttk.Label(frame, text="📁", font=("Arial", 24))
            else:
                # Try to create thumbnail for image
                try:
                    img = Image.open(item_path)
                    img.thumbnail((self.thumb_size, self.thumb_size))
                    photo = ImageTk.PhotoImage(img)
                    img_label = ttk.Label(frame, image=photo)
                    img_label.image = photo  # Keep a reference
                    self.images.append(item_path)  # Add to image list for navigation
                except:
                    img_label = ttk.Label(frame, text="📄", font=("Arial", 24))
            
            img_label.pack()
            text_label = ttk.Label(frame, text=item, wraplength=self.thumb_size)
            text_label.pack()
            
            # Add to canvas
            self.thumb_canvas.create_window(x, y, window=frame, anchor=tk.NW)
            
            # Bind click event
            frame.bind('<Button-1>', lambda e, path=item_path: self.on_thumb_click(e, path))
            
            # Update position
            if (i + 1) % cols == 0:
                x = 10
                y += self.thumb_size + 50
            else:
                x += self.thumb_size + 20
        
        # Update scroll region
        rows = (len(items) + cols - 1) // cols
        height = rows * (self.thumb_size + 50) + 10
        self.thumb_canvas.configure(scrollregion=(0, 0, canvas_width, height))
    
    def update_detail_view(self, items):
        # Clear the tree
        self.detail_tree.delete(*self.detail_tree.get_children())
        
        # Add items to detail view
        for item in items:
            item_path = os.path.join(self.current_folder, item)
            if os.path.isdir(item_path):
                self.detail_tree.insert('', 'end', values=(item, "", "Folder", ""))
            else:
                try:
                    size = os.path.getsize(item_path)
                    file_type = "Image"
                    modified = os.path.getmtime(item_path)
                    self.detail_tree.insert('', 'end', values=(item, self.format_size(size), file_type, modified))
                    self.images.append(item_path)  # Add to image list for navigation
                except:
                    self.detail_tree.insert('', 'end', values=(item, "N/A", "File", "N/A"))
    
    def on_thumb_click(self, event, path):
        if os.path.isdir(path):
            self.load_directory(path)
        else:
            self.open_image(path)
    
    def open_image(self, path):
        # Switch to preview mode
        self.thumb_frame.pack_forget()
        self.detail_frame.pack_forget()
        self.preview_frame.pack(fill=tk.BOTH, expand=True)
        
        try:
            img = Image.open(path)
            # Resize to fit window but maintain aspect ratio
            window_width = self.preview_frame.winfo_width() - 20
            window_height = self.preview_frame.winfo_height() - 20
            
            if window_width < 10:  # Not yet visible
                self.root.after(100, lambda: self.open_image(path))
                return
                
            img.thumbnail((window_width, window_height))
            photo = ImageTk.PhotoImage(img)
            self.preview_label.configure(image=photo)
            self.preview_label.image = photo
            
            # Set current index for navigation
            if path in self.images:
                self.current_index = self.images.index(path)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open image: {e}")
    
    def set_view_mode(self, mode):
        self.view_mode = mode
        if mode == 'details':
            self.thumb_frame.pack_forget()
            self.preview_frame.pack_forget()
            self.detail_frame.pack(fill=tk.BOTH, expand=True)
            self.load_directory(self.current_folder)
        else:  # thumbnails
            self.detail_frame.pack_forget()
            self.preview_frame.pack_forget()
            self.thumb_frame.pack(fill=tk.BOTH, expand=True)
            self.load_directory(self.current_folder)
    
    def increase_thumb_size(self):
        self.thumb_size = min(256, self.thumb_size + 32)
        self.load_directory(self.current_folder)
    
    def decrease_thumb_size(self):
        self.thumb_size = max(64, self.thumb_size - 32)
        self.load_directory(self.current_folder)
    
    def open_folder(self):
        folder = filedialog.askdirectory(initialdir=self.current_folder)
        if folder:
            self.load_directory(folder)
    
    def navigate_to_address(self, event):
        path = self.address_var.get()
        if os.path.exists(path):
            self.load_directory(path)
        else:
            messagebox.showerror("Error", "Path does not exist")
    
    def go_up(self):
        parent = os.path.dirname(self.current_folder)
        if os.path.exists(parent):
            self.load_directory(parent)
    
    def prev_image(self):
        if self.images and self.current_index > 0:
            self.current_index -= 1
            self.open_image(self.images[self.current_index])
    
    def next_image(self):
        if self.images and self.current_index < len(self.images) - 1:
            self.current_index += 1
            self.open_image(self.images[self.current_index])
    
    def first_image(self):
        if self.images:
            self.current_index = 0
            self.open_image(self.images[self.current_index])
    
    def last_image(self):
        if self.images:
            self.current_index = len(self.images) - 1
            self.open_image(self.images[self.current_index])
    
    def refresh(self):
        self.load_directory(self.current_folder)
    
    def format_size(self, size):
        # Format file size in human-readable format
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageExplorer(root)
    root.mainloop()