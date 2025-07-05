import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageOps, ImageDraw
from rembg import remove
import io
import os
import webbrowser
from tkinterdnd2 import TkinterDnD, DND_FILES

class AdvancedBGRemoverApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("Professional BG Remover Pro")
        self.geometry("1200x700")
        self.minsize(1000, 600)
        self.configure(bg="#2e2e2e")
        
        # App variables
        self.image_data = None
        self.full_res_output = None
        self.current_image_path = ""
        self.theme_mode = "dark"
        self.original_image = None
        self.processed_image = None
        
        # Setup UI
        self.setup_ui()
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.handle_drop)
        self.set_window_icon()
    
    def set_window_icon(self):
        try:
            self.iconbitmap(default='icon.ico')
        except:
            pass
    
    def setup_ui(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        
        # Main container
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Controls
        self.control_frame = ttk.LabelFrame(self.main_frame, text="Controls", padding=10)
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Right panel - Image display
        self.display_frame = ttk.Frame(self.main_frame)
        self.display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.create_control_buttons()
        self.create_settings_panel()
        self.create_image_display()
        self.create_status_bar()
    
    def configure_styles(self):
        bg = "#2e2e2e" if self.theme_mode == "dark" else "#f5f5f5"
        fg = "#ffffff" if self.theme_mode == "dark" else "#000000"
        accent = "#007acc" if self.theme_mode == "dark" else "#1e88e5"
        secondary = "#3e3e3e" if self.theme_mode == "dark" else "#e0e0e0"
        
        self.style.configure('.', background=bg, foreground=fg)
        self.style.configure('TFrame', background=bg)
        self.style.configure('TLabel', background=bg, foreground=fg)
        self.style.configure('TButton', background=accent, foreground="white", 
                           borderwidth=1, font=('Arial', 10))
        self.style.configure('TLabelFrame', background=bg, foreground=accent)
        self.style.configure('TEntry', fieldbackground=secondary)
        self.style.configure('TCombobox', fieldbackground=secondary)
        self.style.map('TButton', background=[('active', accent), ('disabled', '#666666')])
    
    def create_control_buttons(self):
        large_btn_style = ttk.Style()
        large_btn_style.configure('Large.TButton', font=('Arial', 12, 'bold'), padding=10)
        
        self.load_btn = ttk.Button(
            self.control_frame, 
            text="📁 Load Image", 
            command=self.load_image,
            style='Large.TButton'
        )
        self.load_btn.pack(fill=tk.X, pady=5)
        
        self.remove_btn = ttk.Button(
            self.control_frame, 
            text="✂️ Remove Background", 
            command=self.remove_bg,
            style='Large.TButton'
        )
        self.remove_btn.pack(fill=tk.X, pady=5)
        
        self.save_btn = ttk.Button(
            self.control_frame, 
            text="💾 Save Result", 
            command=self.save_image,
            style='Large.TButton',
            state=tk.DISABLED
        )
        self.save_btn.pack(fill=tk.X, pady=5)
        
        ttk.Separator(self.control_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        quick_frame = ttk.LabelFrame(self.control_frame, text="Quick Actions", padding=10)
        quick_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(quick_frame, text="🔄 Reset View", command=self.reset_view).pack(fill=tk.X, pady=2)
        ttk.Button(quick_frame, text="🎨 Change Theme", command=self.toggle_theme).pack(fill=tk.X, pady=2)
        ttk.Button(quick_frame, text="🌐 Visit Website", command=lambda: webbrowser.open("https://example.com")).pack(fill=tk.X, pady=2)
    
    def create_settings_panel(self):
        settings_frame = ttk.LabelFrame(self.control_frame, text="Settings", padding=10)
        settings_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(settings_frame, text="Output Quality:").pack(anchor=tk.W)
        self.quality_var = tk.StringVar(value="high")
        ttk.Combobox(
            settings_frame,
            textvariable=self.quality_var,
            values=["low", "medium", "high", "ultra"],
            state="readonly"
        ).pack(fill=tk.X, pady=2)
        
        ttk.Label(settings_frame, text="Preview Background:").pack(anchor=tk.W)
        self.bg_color_var = tk.StringVar(value="checkerboard")
        ttk.Combobox(
            settings_frame,
            textvariable=self.bg_color_var,
            values=["checkerboard", "white", "black", "transparent"],
            state="readonly"
        ).pack(fill=tk.X, pady=2)
        
        ttk.Label(settings_frame, text="Edge Refinement:").pack(anchor=tk.W)
        self.edge_var = tk.IntVar(value=1)
        ttk.Scale(
            settings_frame,
            from_=0,
            to=10,
            variable=self.edge_var,
            orient=tk.HORIZONTAL
        ).pack(fill=tk.X, pady=2)
    
    def create_image_display(self):
        # Main image display area
        self.img_frame = ttk.Frame(self.display_frame)
        self.img_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas with scrollbars
        self.canvas = tk.Canvas(
            self.img_frame,
            bg="#808080",
            highlightthickness=0
        )
        
        self.h_scroll = ttk.Scrollbar(
            self.img_frame,
            orient=tk.HORIZONTAL,
            command=self.canvas.xview
        )
        self.v_scroll = ttk.Scrollbar(
            self.img_frame,
            orient=tk.VERTICAL,
            command=self.canvas.yview
        )
        
        self.canvas.configure(
            xscrollcommand=self.h_scroll.set,
            yscrollcommand=self.v_scroll.set
        )
        
        # Grid layout for canvas and scrollbars
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scroll.grid(row=0, column=1, sticky="ns")
        self.h_scroll.grid(row=1, column=0, sticky="ew")
        
        self.img_frame.grid_rowconfigure(0, weight=1)
        self.img_frame.grid_columnconfigure(0, weight=1)
        
        # Info label
        self.image_info = ttk.Label(
            self.display_frame,
            text="No image loaded",
            anchor=tk.CENTER
        )
        self.image_info.pack(fill=tk.X, pady=5)
        
        # Preview label (smaller preview)
        self.preview_label = ttk.Label(
            self.display_frame,
            text="Preview",
            anchor=tk.CENTER
        )
        self.preview_label.pack(fill=tk.X, pady=5)
        
        self.preview_canvas = tk.Canvas(
            self.display_frame,
            width=300,
            height=200,
            bg="#808080",
            highlightthickness=0
        )
        self.preview_canvas.pack(pady=5)
        
        # Bind mouse events
        self.canvas.bind("<ButtonPress-1>", self.start_pan)
        self.canvas.bind("<B1-Motion>", self.pan_image)
        self.canvas.bind("<MouseWheel>", self.zoom_image)
        self.canvas.bind("<Button-4>", self.zoom_image)
        self.canvas.bind("<Button-5>", self.zoom_image)
        
        # Image references
        self.image_on_canvas = None
        self.image_tk = None
        self.preview_image_tk = None
        self.zoom_level = 1.0
    
    def create_status_bar(self):
        self.status_bar = ttk.Frame(self)
        self.status_bar.pack(fill=tk.X, padx=5, pady=2)
        
        self.status_label = ttk.Label(
            self.status_bar,
            text="Ready",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_label.pack(fill=tk.X)
    
    def update_status(self, message):
        self.status_label.config(text=message)
        self.update()
    
    def load_image(self, path=None):
        if not path:
            path = filedialog.askopenfilename(
                filetypes=[
                    ("Image Files", "*.jpg *.jpeg *.png *.bmp *.tiff"),
                    ("All Files", "*.*")
                ]
            )
        
        if path:
            try:
                self.current_image_path = path
                with open(path, "rb") as file:
                    self.image_data = file.read()
                
                self.original_image = Image.open(io.BytesIO(self.image_data))
                self.display_images()
                self.save_btn.config(state=tk.DISABLED)
                self.update_status(f"Loaded: {os.path.basename(path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image:\n{str(e)}")
    
    def handle_drop(self, event):
        files = self.tk.splitlist(event.data)
        if files and files[0].lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            self.load_image(files[0])
    
    def display_images(self):
        """Display both main and preview images"""
        if not self.original_image:
            return
            
        # Display main image (fit to canvas)
        self.display_main_image(self.original_image, "Original Image")
        
        # Display preview (fixed size)
        self.display_preview_image(self.original_image)
    
    def display_main_image(self, img, title=""):
        """Display image fitted to canvas size"""
        self.canvas.delete("all")
        
        # Get canvas dimensions
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:  # Canvas not yet visible
            canvas_width = 800
            canvas_height = 600
        
        # Calculate aspect ratio preserving dimensions
        img_width, img_height = img.size
        ratio = min(canvas_width/img_width, canvas_height/img_height)
        new_size = (int(img_width * ratio), int(img_height * ratio))
        
        # Resize image
        resized_img = img.resize(new_size, Image.LANCZOS)
        
        # Create background
        bg = self.create_background(new_size)
        if img.mode == 'RGBA':
            bg.paste(resized_img, (0, 0), resized_img)
            resized_img = bg
        
        # Convert to PhotoImage
        self.image_tk = ImageTk.PhotoImage(resized_img)
        
        # Center image on canvas
        x_pos = max(0, (canvas_width - new_size[0]) // 2)
        y_pos = max(0, (canvas_height - new_size[1]) // 2)
        
        # Display on canvas
        self.image_on_canvas = self.canvas.create_image(
            x_pos, y_pos,
            image=self.image_tk,
            anchor=tk.NW
        )
        
        # Update info and scroll region
        self.image_info.config(text=f"{title} | Size: {img.width}x{img.height} | Format: {img.format if hasattr(img, 'format') else 'Unknown'}")
        self.canvas.config(scrollregion=(0, 0, new_size[0], new_size[1]))
        self.zoom_level = 1.0
    
    def display_preview_image(self, img):
        """Display fixed-size preview image"""
        self.preview_canvas.delete("all")
        
        # Fixed preview size
        preview_size = (300, 200)
        
        # Create thumbnail
        img_copy = img.copy()
        img_copy.thumbnail(preview_size, Image.LANCZOS)
        
        # Create background
        bg = Image.new('RGB', preview_size, (128, 128, 128))
        bg.paste(img_copy, 
                ((preview_size[0] - img_copy.width) // 2, 
                 (preview_size[1] - img_copy.height) // 2))
        
        # Convert to PhotoImage
        self.preview_image_tk = ImageTk.PhotoImage(bg)
        
        # Display on preview canvas
        self.preview_canvas.create_image(
            preview_size[0]//2,
            preview_size[1]//2,
            image=self.preview_image_tk,
            anchor=tk.CENTER
        )
    
    def remove_bg(self):
        if not self.image_data:
            messagebox.showwarning("No Image", "Please load an image first.")
            return
        
        try:
            self.update_status("Removing background... (this may take a while)")
            self.update()
            
            output = remove(self.image_data)
            self.processed_image = Image.open(io.BytesIO(output))
            self.full_res_output = self.processed_image.copy()
            
            self.display_main_image(self.processed_image, "Background Removed")
            self.display_preview_image(self.processed_image)
            self.save_btn.config(state=tk.NORMAL)
            self.update_status("Background removed successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove background:\n{str(e)}")
            self.update_status("Error removing background")
    
    def save_image(self):
        if not self.full_res_output:
            messagebox.showwarning("No Result", "No processed image to save.")
            return
        
        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG Image", "*.png"),
                ("JPEG Image", "*.jpg"),
                ("All Files", "*.*")
            ]
        )
        
        if save_path:
            try:
                self.full_res_output.save(save_path)
                messagebox.showinfo("Saved", f"Image saved successfully to:\n{save_path}")
                self.update_status(f"Saved to: {save_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image:\n{str(e)}")
                self.update_status("Error saving image")
    
    def reset_view(self):
        if self.processed_image:
            self.display_main_image(self.processed_image, "Background Removed")
        elif self.original_image:
            self.display_main_image(self.original_image, "Original Image")
        self.zoom_level = 1.0
    
    def toggle_theme(self):
        self.theme_mode = "light" if self.theme_mode == "dark" else "dark"
        self.configure_styles()
        self.update_all_widgets()
    
    def update_all_widgets(self):
        for widget in self.winfo_children():
            widget.update()
    
    def start_pan(self, event):
        self.canvas.scan_mark(event.x, event.y)
    
    def pan_image(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)
    
    def zoom_image(self, event):
        scale = 1.0
        
        if event.num == 5 or event.delta < 0:  # Zoom out
            scale *= 0.9
        elif event.num == 4 or event.delta > 0:  # Zoom in
            scale *= 1.1
        
        self.zoom_level *= scale
        self.canvas.scale("all", event.x, event.y, scale, scale)
    
    def create_background(self, size):
        bg_type = self.bg_color_var.get()
        
        if bg_type == "checkerboard":
            tile_size = 20
            bg = Image.new('RGB', size, (240, 240, 240))
            draw = Image.new('RGB', (tile_size*2, tile_size*2), (255, 255, 255))
            ImageDraw.Draw(draw).rectangle([0, 0, tile_size, tile_size], fill=(220, 220, 220))
            ImageDraw.Draw(draw).rectangle([tile_size, tile_size, tile_size*2, tile_size*2], fill=(220, 220, 220))
            bg = Image.new('RGB', size)
            for y in range(0, size[1], tile_size*2):
                for x in range(0, size[0], tile_size*2):
                    bg.paste(draw, (x, y))
        elif bg_type == "white":
            bg = Image.new('RGB', size, (255, 255, 255))
        elif bg_type == "black":
            bg = Image.new('RGB', size, (0, 0, 0))
        else:  # transparent
            bg = Image.new('RGBA', size, (0, 0, 0, 0))
        
        return bg
    
    def run(self):
        self.mainloop()

if __name__ == "__main__":
    app = AdvancedBGRemoverApp()
    app.run()