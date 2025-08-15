import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import threading

# Try to import drag & drop support (optional)
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_DND = True
except ImportError:
    HAS_DND = False

class ImageToPNGConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("🎨 PNG Converter Pro")
        self.root.geometry("500x550")
        self.root.resizable(False, False)
        
        # Theme state
        self.dark_mode = False
        
        # Theme colors
        self.light_theme = {
            'bg': '#ffffff',
            'surface': '#f8f9fa',
            'text': '#333333',
            'text_muted': '#666666',
            'button_bg': '#007acc',
            'button_fg': 'white',
            'success': '#28a745',
            'warning': '#ffc107',
            'danger': '#dc3545',
            'creator_bg': '#e9ecef',
            'creator_text': '#495057'
        }
        
        self.dark_theme = {
            'bg': '#1a1a1a',
            'surface': '#2d2d2d',
            'text': '#ffffff',
            'text_muted': '#cccccc',
            'button_bg': '#0d7377',
            'button_fg': 'white',
            'success': '#20c997',
            'warning': '#ffc107',
            'danger': '#fd7e14',
            'creator_bg': '#343a40',
            'creator_text': '#adb5bd'
        }
        
        self.current_theme = self.light_theme
        
        # Supported formats
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp']
        
        self.counter = 1
        self.selected_files = []
        self.output_folder = None
        
        self.setup_ui()
        if HAS_DND:
            self.setup_drag_drop()
        self.apply_theme()
    
    def setup_ui(self):
        # Header with theme toggle
        header_frame = tk.Frame(self.root)
        header_frame.pack(fill=tk.X, pady=(10, 5))
        
        title_label = tk.Label(
            header_frame,
            text="🎨 PNG Converter Pro",
            font=("Arial", 17, "bold")
        )
        title_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # Dark mode toggle button
        self.theme_btn = tk.Button(
            header_frame,
            text="🌙",
            command=self.toggle_theme,
            font=("Arial", 12),
            width=3,
            cursor="hand2",
            relief="flat"
        )
        self.theme_btn.pack(side=tk.RIGHT, padx=(0, 20))
        
        # Subtitle
        subtitle_text = "Convert JPG, GIF, BMP, TIFF, WEBP to PNG"
        if HAS_DND:
            subtitle_text += " | Drag & Drop Files"
        
        subtitle_label = tk.Label(
            self.root,
            text=subtitle_text,
            font=("Arial", 8)
        )
        subtitle_label.pack()
        
        # Drag and Drop Zone (only if supported)
        if HAS_DND:
            self.drop_zone = tk.Frame(
                self.root,
                relief="ridge",
                bd=2,
                height=0
            )
            self.drop_zone.pack(pady=0, padx=0, fill=tk.X)
            self.drop_zone.pack_propagate(False)
            
            self.drop_label = tk.Label(
                self.drop_zone,
                text="📁 Drag & Drop Images Here or Use Buttons Below",
                font=("Arial", 0, "bold"),
                justify=tk.CENTER
            )
            self.drop_label.pack(expand=True)
        
        # Control buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        self.select_files_btn = tk.Button(
            button_frame,
            text="📄 Files",
            command=self.select_files,
            font=("Arial", 12, "bold"),
            width=13,
            pady=7,
            cursor="hand2",
            relief="flat"
        )
        self.select_files_btn.pack(side=tk.LEFT, padx=5)
        
        self.select_folder_btn = tk.Button(
            button_frame,
            text="📂 Folder",
            command=self.select_folder,
            font=("Arial", 12, "bold"),
            width=13,
            pady=7,
            cursor="hand2",
            relief="flat"
        )
        self.select_folder_btn.pack(side=tk.LEFT, padx=5)
        
        # Output folder section
        output_frame = tk.Frame(self.root)
        output_frame.pack(pady=5, padx=15, fill=tk.X)
        
        self.output_title = tk.Label(
            output_frame,
            text="Output:",
            font=("Arial", 8, "bold")
        )
        self.output_title.pack(anchor=tk.W)
        
        output_control = tk.Frame(output_frame)
        output_control.pack(fill=tk.X, pady=2)
        
        self.output_label = tk.Label(
            output_control,
            text="Same as input files",
            font=("Arial", 8),
            relief="solid",
            bd=1,
            padx=8,
            pady=3,
            anchor='w'
        )
        self.output_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.browse_btn = tk.Button(
            output_control,
            text="Browse",
            command=self.select_output_folder,
            font=("Arial", 9),
            padx=10,
            pady=3,
            cursor="hand2",
            relief="flat"
        )
        self.browse_btn.pack(side=tk.RIGHT)
        
        # File preview section
        self.list_frame = tk.LabelFrame(
            self.root,
            text="Selected Files",
            font=("Arial", 9, "bold"),
            padx=3,
            pady=3
        )
        self.list_frame.pack(pady=8, padx=15, fill=tk.BOTH, expand=True)
        
        # Scrollable preview
        self.canvas = tk.Canvas(self.list_frame, highlightthickness=0, height=150)
        self.scrollbar = ttk.Scrollbar(self.list_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Empty state
        self.empty_label = tk.Label(
            self.scrollable_frame,
            text="📷 No files selected\nDrag & Drop images or click 'Files'/'Folder'",
            font=("Arial", 9),
            justify=tk.CENTER
        )
        self.empty_label.pack(pady=30)
        
        # Status section
        status_frame = tk.Frame(self.root)
        status_frame.pack(fill=tk.X, padx=15, pady=(5, 0))
        
        self.status_label = tk.Label(
            status_frame,
            text="Ready - Select or drag images to convert",
            font=("Arial", 8)
        )
        self.status_label.pack()
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            status_frame,
            variable=self.progress_var,
            maximum=100,
            length=470
        )
        self.progress_bar.pack(pady=3)
        
        # Convert button
        self.convert_btn = tk.Button(
            self.root,
            text="🚀 Convert to PNG",
            command=self.start_conversion,
            font=("Arial", 11, "bold"),
            padx=25,
            pady=8,
            cursor="hand2",
            relief="flat",
            state=tk.DISABLED
        )
        self.convert_btn.pack(pady=10)
        
        # Creator information
        creator_frame = tk.Frame(self.root, relief="sunken", bd=1)
        creator_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        creator_info = tk.Frame(creator_frame)
        creator_info.pack(side=tk.LEFT, padx=10, pady=5)
        
        creator_label = tk.Label(
            creator_info,
            text="Created by: Rushi Digraskar",
            font=("Arial", 8, "bold")
        )
        creator_label.pack(anchor=tk.W)
        
        email_label = tk.Label(
            creator_info,
            text="rushi88300@gmail.com",
            font=("Arial", 7)
        )
        email_label.pack(anchor=tk.W)
        
        # Store all widgets for theme updates
        self.widgets = [
            self.root, header_frame, title_label, subtitle_label, button_frame,
            self.select_files_btn, self.select_folder_btn, output_frame,
            self.output_title, output_control, self.output_label, self.browse_btn,
            self.list_frame, self.canvas, self.scrollable_frame, self.empty_label,
            status_frame, self.status_label, self.convert_btn,
            creator_frame, creator_info, creator_label, email_label
        ]
        
        # Add drag zone widgets if available
        if HAS_DND:
            self.widgets.extend([self.drop_zone, self.drop_label])
    
    def setup_drag_drop(self):
        """Setup drag and drop functionality (only if supported)"""
        if not HAS_DND:
            return
            
        # Enable drag and drop for the entire window and drop zone
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.handle_drop)
        
        self.drop_zone.drop_target_register(DND_FILES)
        self.drop_zone.dnd_bind('<<Drop>>', self.handle_drop)
        
        # Visual feedback for drag over
        self.root.dnd_bind('<<DragEnter>>', self.on_drag_enter)
        self.root.dnd_bind('<<DragLeave>>', self.on_drag_leave)
        self.drop_zone.dnd_bind('<<DragEnter>>', self.on_drag_enter)
        self.drop_zone.dnd_bind('<<DragLeave>>', self.on_drag_leave)
    
    def on_drag_enter(self, event):
        """Visual feedback when drag enters"""
        if HAS_DND and hasattr(self, 'drop_zone'):
            self.drop_zone.configure(relief="solid", bd=3)
    
    def on_drag_leave(self, event):
        """Visual feedback when drag leaves"""
        if HAS_DND and hasattr(self, 'drop_zone'):
            self.drop_zone.configure(relief="ridge", bd=2)
    
    def handle_drop(self, event):
        """Handle dropped files"""
        if not HAS_DND:
            return
            
        if hasattr(self, 'drop_zone'):
            self.drop_zone.configure(relief="ridge", bd=2)  # Reset visual state
        
        try:
            # Get dropped files
            files = self.root.tk.splitlist(event.data)
            valid_files = []
            
            for file_path in files:
                if os.path.isfile(file_path):
                    ext = os.path.splitext(file_path)[1].lower()
                    if ext in self.supported_formats:
                        valid_files.append(file_path)
                elif os.path.isdir(file_path):
                    # If folder is dropped, scan for images
                    for filename in os.listdir(file_path):
                        ext = os.path.splitext(filename)[1].lower()
                        if ext in self.supported_formats:
                            valid_files.append(os.path.join(file_path, filename))
            
            if valid_files:
                self.selected_files = valid_files
                self.update_file_list()
                self.status_label.config(text=f"Dropped {len(valid_files)} files ready for conversion")
            else:
                messagebox.showwarning("No Valid Files", "No supported image files found in dropped items!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error processing dropped files: {str(e)}")
    
    def toggle_theme(self):
        """Toggle between light and dark theme"""
        self.dark_mode = not self.dark_mode
        self.current_theme = self.dark_theme if self.dark_mode else self.light_theme
        self.theme_btn.config(text="☀️" if self.dark_mode else "🌙")
        self.apply_theme()
    
    def apply_theme(self):
        """Apply current theme to all widgets"""
        theme = self.current_theme
        
        # Main window
        self.root.configure(bg=theme['bg'])
        
        # Configure all frames and labels
        for widget in self.root.winfo_children():
            self.configure_widget_theme(widget, theme)
        
        # Special configurations
        if HAS_DND and hasattr(self, 'drop_zone'):
            self.drop_zone.configure(bg=theme['surface'])
            if hasattr(self, 'drop_label'):
                self.drop_label.configure(bg=theme['surface'], fg=theme['text'])
        
        # Button configurations
        self.select_files_btn.configure(
            bg=theme['button_bg'], fg=theme['button_fg'],
            activebackground=theme['surface']
        )
        self.select_folder_btn.configure(
            bg=theme['success'], fg=theme['button_fg'],
            activebackground=theme['surface']
        )
        self.browse_btn.configure(
            bg=theme['warning'], fg='black',
            activebackground=theme['surface']
        )
        self.convert_btn.configure(
            bg=theme['success'], fg='white',
            activebackground=theme['surface']
        )
        self.theme_btn.configure(
            bg=theme['surface'], fg=theme['text'],
            activebackground=theme['bg']
        )
        
        # Creator section
        creator_frame = None
        creator_info = None
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame) and widget.cget('relief') == 'sunken':
                creator_frame = widget
                break
        
        if creator_frame:
            creator_frame.configure(bg=theme['creator_bg'])
            for child in creator_frame.winfo_children():
                if isinstance(child, tk.Frame):
                    child.configure(bg=theme['creator_bg'])
                    for grandchild in child.winfo_children():
                        if isinstance(grandchild, tk.Label):
                            grandchild.configure(bg=theme['creator_bg'], fg=theme['creator_text'])
        
        # Update file list if files are selected
        if self.selected_files:
            self.update_file_list()
    
    def configure_widget_theme(self, widget, theme):
        """Recursively configure widget theme"""
        try:
            widget_type = widget.winfo_class()
            
            if widget_type in ['Frame', 'Toplevel']:
                if widget.cget('relief') != 'sunken':  # Don't change creator frame
                    widget.configure(bg=theme['bg'])
            elif widget_type == 'Label':
                widget.configure(bg=theme['bg'], fg=theme['text'])
            elif widget_type == 'LabelFrame':
                widget.configure(bg=theme['bg'], fg=theme['text'])
            elif widget_type == 'Canvas':
                widget.configure(bg=theme['surface'])
            
            # Configure children recursively
            for child in widget.winfo_children():
                self.configure_widget_theme(child, theme)
                
        except tk.TclError:
            pass
    
    def select_files(self):
        """Select individual files"""
        try:
            file_types = [
                ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff *.tif *.webp"),
                ("All files", "*.*")
            ]
            
            files = filedialog.askopenfilenames(
                title="Select Image Files",
                filetypes=file_types
            )
            
            if files:
                valid_files = []
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext in self.supported_formats:
                        valid_files.append(file)
                
                if valid_files:
                    self.selected_files = valid_files
                    self.update_file_list()
                else:
                    messagebox.showwarning("No Valid Files", "No supported image files selected!")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error selecting files: {str(e)}")
    
    def select_folder(self):
        """Select folder containing images"""
        try:
            folder = filedialog.askdirectory(title="Select Folder with Images")
            
            if folder:
                files = []
                for filename in os.listdir(folder):
                    ext = os.path.splitext(filename)[1].lower()
                    if ext in self.supported_formats:
                        files.append(os.path.join(folder, filename))
                
                if files:
                    self.selected_files = files
                    self.update_file_list()
                else:
                    messagebox.showinfo("No Images", "No supported images found in folder!")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error selecting folder: {str(e)}")
    
    def select_output_folder(self):
        """Select output folder"""
        try:
            folder = filedialog.askdirectory(title="Select Output Folder")
            if folder:
                self.output_folder = folder
                folder_name = os.path.basename(folder) or "Selected Folder"
                self.output_label.config(text=f"📁 {folder_name}")
        except Exception as e:
            messagebox.showerror("Error", f"Error selecting output folder: {str(e)}")
    
    def create_thumbnail(self, image_path):
        """Create thumbnail for preview"""
        try:
            img = Image.open(image_path)
            img.thumbnail((35, 35), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        except:
            return None
    
    def update_file_list(self):
        """Update the file list display"""
        # Clear existing items
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        theme = self.current_theme
        
        if not self.selected_files:
            self.empty_label = tk.Label(
                self.scrollable_frame,
                text="📷 No files selected\nDrag & Drop images or click 'Files'/'Folder'",
                font=("Arial", 9),
                bg=theme['surface'],
                fg=theme['text_muted'],
                justify=tk.CENTER
            )
            self.empty_label.pack(pady=30)
            self.convert_btn.config(state=tk.DISABLED)
            return
        
        # Add each file to the list
        for i, file_path in enumerate(self.selected_files):
            try:
                file_frame = tk.Frame(
                    self.scrollable_frame, 
                    bg=theme['bg'], 
                    relief="solid", 
                    bd=1
                )
                file_frame.pack(fill=tk.X, padx=3, pady=1)
                
                # Thumbnail
                thumbnail = self.create_thumbnail(file_path)
                if thumbnail:
                    img_label = tk.Label(file_frame, image=thumbnail, bg=theme['bg'])
                    img_label.image = thumbnail
                    img_label.pack(side=tk.LEFT, padx=3, pady=3)
                else:
                    icon_label = tk.Label(
                        file_frame,
                        text="🖼️",
                        font=("Arial", 16),
                        bg=theme['bg'],
                        fg=theme['text']
                    )
                    icon_label.pack(side=tk.LEFT, padx=3, pady=3)
                
                # File info
                info_frame = tk.Frame(file_frame, bg=theme['bg'])
                info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=3)
                
                # Filename
                filename = os.path.basename(file_path)
                if len(filename) > 30:
                    filename = filename[:27] + "..."
                
                name_label = tk.Label(
                    info_frame,
                    text=filename,
                    font=("Arial", 8, "bold"),
                    bg=theme['bg'],
                    fg=theme['text'],
                    anchor='w'
                )
                name_label.pack(anchor=tk.W, fill=tk.X)
                
                # File details
                try:
                    size = os.path.getsize(file_path)
                    size_text = f"{size/1024:.1f} KB" if size < 1024*1024 else f"{size/(1024*1024):.1f} MB"
                    ext = os.path.splitext(file_path)[1].upper()
                    
                    detail_label = tk.Label(
                        info_frame,
                        text=f"{ext} • {size_text}",
                        font=("Arial", 7),
                        bg=theme['bg'],
                        fg=theme['text_muted'],
                        anchor='w'
                    )
                    detail_label.pack(anchor=tk.W)
                    
                    # Output preview
                    output_name = f"{os.path.splitext(os.path.basename(file_path))[0]}_conv_{self.counter + i:03d}.png"
                    if len(output_name) > 35:
                        output_name = output_name[:32] + "..."
                    
                    output_label = tk.Label(
                        info_frame,
                        text=f"→ {output_name}",
                        font=("Arial", 7),
                        bg=theme['bg'],
                        fg=theme['success'],
                        anchor='w'
                    )
                    output_label.pack(anchor=tk.W)
                    
                except:
                    pass
                    
            except Exception as e:
                print(f"Error creating preview for {file_path}: {e}")
        
        # Update status and enable convert button
        self.status_label.config(text=f"{len(self.selected_files)} files ready for conversion")
        self.convert_btn.config(state=tk.NORMAL)
    
    def start_conversion(self):
        """Start the conversion process"""
        if not self.selected_files:
            return
        
        # Disable buttons during conversion
        self.convert_btn.config(state=tk.DISABLED)
        self.select_files_btn.config(state=tk.DISABLED)
        self.select_folder_btn.config(state=tk.DISABLED)
        
        # Start conversion in background thread
        threading.Thread(target=self.convert_images, daemon=True).start()
    
    def convert_images(self):
        """Convert images to PNG"""
        total = len(self.selected_files)
        converted = 0
        errors = []
        
        for i, file_path in enumerate(self.selected_files):
            try:
                # Update progress
                progress = (i / total) * 100
                self.progress_var.set(progress)
                
                filename = os.path.basename(file_path)
                self.status_label.config(text=f"Converting: {filename}")
                self.root.update_idletasks()
                
                # Load and convert image
                with Image.open(file_path) as img:
                    # Handle transparency
                    if img.mode in ('RGBA', 'LA', 'P'):
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        if img.mode in ('RGBA', 'LA'):
                            background.paste(img, mask=img.split()[-1])
                        else:
                            background.paste(img)
                        img = background
                    elif img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # Generate output filename
                    base_name = os.path.splitext(os.path.basename(file_path))[0]
                    output_filename = f"{base_name}_converted_{self.counter:04d}.png"
                    
                    # Determine output path
                    if self.output_folder:
                        output_path = os.path.join(self.output_folder, output_filename)
                    else:
                        output_path = os.path.join(os.path.dirname(file_path), output_filename)
                    
                    # Save as PNG
                    img.save(output_path, 'PNG', optimize=True)
                    converted += 1
                    self.counter += 1
                    
            except Exception as e:
                errors.append(f"{os.path.basename(file_path)}: {str(e)}")
        
        # Complete progress
        self.progress_var.set(100)
        
        # Show results
        if errors:
            error_msg = f"Converted {converted}/{total} files.\n\nErrors:\n" + "\n".join(errors[:3])
            messagebox.showwarning("Conversion Complete", error_msg)
        else:
            messagebox.showinfo("Success! 🎉", f"Successfully converted all {converted} files to PNG!")
        
        # Re-enable buttons
        self.convert_btn.config(state=tk.NORMAL)
        self.select_files_btn.config(state=tk.NORMAL)
        self.select_folder_btn.config(state=tk.NORMAL)
        self.status_label.config(text=f"Complete: {converted}/{total} files converted")
        
        # Reset progress after 2 seconds
        self.root.after(2000, lambda: self.progress_var.set(0))

def main():
    """Main function"""
    global HAS_DND
    
    # Create root window
    if HAS_DND:
        try:
            root = TkinterDnD.Tk()  # Use TkinterDnD root for drag & drop support
        except:
            root = tk.Tk()
            HAS_DND = False
    else:
        root = tk.Tk()
        # Show info about drag & drop being unavailable
        def show_dnd_info():
            messagebox.showinfo("Drag & Drop Info", 
                              "Drag & Drop feature is not available.\n\n"
                              "To enable it, install: pip install tkinterdnd2\n"
                              "You can still use 'Files' and 'Folder' buttons.")
        root.after(1000, show_dnd_info)  # Show after 1 second
    
    app = ImageToPNGConverter(root)
    
    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (250)
    y = (root.winfo_screenheight() // 2) - (275)
    root.geometry(f"500x550+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()