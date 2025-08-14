#
# An advanced desktop photo editing application using only standard
# tkinter widgets. This minimizes the number of libraries you need to install
# for a simpler build process, while still providing all core features.
#
# It includes:
# - A simple, classic user interface with built-in tkinter widgets.
# - Image filters: Black & White, Line Art, Sepia, Sharpen.
# - A grid overlay with customizable size.
# - A4 Portrait and Landscape display modes based on user-input DPI.
# - Efficient image processing for low-end PCs.
#
# Author: Gemini
# Date: 2025-08-15
#

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFilter, ImageOps

class PhotoLineApp:
    def __init__(self, root):
        """Initializes the main application window and its components."""
        self.root = root
        self.root.title("Photo Line Desktop")
        self.root.geometry("1000x800")

        # Application state variables
        self.original_image = None
        self.processed_image = None
        self.display_image = None
        self.current_mode = "color"
        self.grid_lines_visible = False
        self.current_filename = ""
        
        # A4 paper dimensions in millimeters
        self.A4_WIDTH_MM = 210
        self.A4_HEIGHT_MM = 297

        # Create the main layout
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Canvas for image display
        self.canvas = tk.Canvas(self.main_frame, bg="white")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Control panel for buttons and inputs
        self.control_frame = tk.Frame(self.main_frame, width=280, padx=10, pady=10)
        self.control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=15, pady=15)
        self.control_frame.pack_propagate(False)

        # Create and pack control widgets with standard tkinter
        self.open_button = tk.Button(self.control_frame, text="Open Photo", command=self.open_photo, width=25)
        self.open_button.pack(pady=5)

        tk.Label(self.control_frame, text="Image Filters:", font=("Helvetica", 10, "bold")).pack(pady=(15, 0), anchor="w")
        self.mode_frame = tk.Frame(self.control_frame)
        self.mode_frame.pack(pady=5, fill="x")
        
        self.mode_var = tk.StringVar(value="color")
        self.color_radio = tk.Radiobutton(self.mode_frame, text="Color", variable=self.mode_var, value="color", command=self.update_image_mode)
        self.color_radio.pack(side=tk.LEFT, padx=5, fill="x", expand=True)
        self.bw_radio = tk.Radiobutton(self.mode_frame, text="B&W", variable=self.mode_var, value="bw", command=self.update_image_mode)
        self.bw_radio.pack(side=tk.LEFT, padx=5, fill="x", expand=True)
        self.line_art_radio = tk.Radiobutton(self.mode_frame, text="Line Art", variable=self.mode_var, value="line_art", command=self.update_image_mode)
        self.line_art_radio.pack(side=tk.LEFT, padx=5, fill="x", expand=True)

        self.sepia_radio = tk.Radiobutton(self.control_frame, text="Sepia", variable=self.mode_var, value="sepia", command=self.update_image_mode)
        self.sepia_radio.pack(pady=2, fill="x")
        self.sharpen_radio = tk.Radiobutton(self.control_frame, text="Sharpen", variable=self.mode_var, value="sharpen", command=self.update_image_mode)
        self.sharpen_radio.pack(pady=2, fill="x")
        
        tk.Frame(self.control_frame, height=2, bd=1, relief="sunken").pack(fill="x", pady=10)

        # UI for DPI and A4 view
        tk.Label(self.control_frame, text="Monitor DPI:", font=("Helvetica", 10, "bold")).pack(pady=(5, 0), anchor="w")
        self.dpi_entry = tk.Entry(self.control_frame)
        self.dpi_entry.insert(0, "96")
        self.dpi_entry.pack(pady=5, fill="x")
        
        tk.Label(self.control_frame, text="Display View:", font=("Helvetica", 10, "bold")).pack(pady=(10, 0), anchor="w")
        self.view_var = tk.StringVar(value="fit_to_window")
        self.fit_radio = tk.Radiobutton(self.control_frame, text="Fit to Window", variable=self.view_var, value="fit_to_window", command=self.update_image_display)
        self.fit_radio.pack(pady=2, fill="x")
        self.a4_portrait_radio = tk.Radiobutton(self.control_frame, text="A4 Portrait", variable=self.view_var, value="a4_portrait", command=self.update_image_display)
        self.a4_portrait_radio.pack(pady=2, fill="x")
        self.a4_landscape_radio = tk.Radiobutton(self.control_frame, text="A4 Landscape", variable=self.view_var, value="a4_landscape", command=self.update_image_display)
        self.a4_landscape_radio.pack(pady=2, fill="x")
        
        tk.Frame(self.control_frame, height=2, bd=1, relief="sunken").pack(fill="x", pady=10)

        tk.Label(self.control_frame, text="Grid Size (px):", font=("Helvetica", 10, "bold")).pack(pady=(5, 0), anchor="w")
        self.grid_size_entry = tk.Entry(self.control_frame)
        self.grid_size_entry.insert(0, "50")
        self.grid_size_entry.pack(pady=5, fill="x")

        self.grid_button = tk.Button(self.control_frame, text="Toggle Grid", command=self.toggle_grid)
        self.grid_button.pack(pady=5, fill="x")

        # Status bar at the bottom
        self.status_bar = tk.Label(root, text="Ready.", bd=1, relief="sunken", anchor="w")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Bind the resize event
        self.root.bind("<Configure>", self.on_window_resize)

    def open_photo(self):
        filepath = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")])
        if filepath:
            try:
                self.original_image = Image.open(filepath)
                self.current_filename = filepath.split('/')[-1]
                self.mode_var.set("color")
                self.view_var.set("fit_to_window")
                self.grid_lines_visible = False
                self.update_image_display()
                self.status_bar.config(text=f"Opened: {self.current_filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open image: {e}")

    def update_image_mode(self):
        if not self.original_image:
            messagebox.showinfo("Info", "Please open a photo first.")
            self.mode_var.set("color")
            return
        
        self.current_mode = self.mode_var.get()
        processed_image_temp = self.original_image.copy()

        if self.current_mode == "bw":
            processed_image_temp = processed_image_temp.convert('L').convert('RGB')
        elif self.current_mode == "line_art":
            processed_image_temp = self.create_line_art(processed_image_temp)
        elif self.current_mode == "sepia":
            processed_image_temp = self.create_sepia_filter(processed_image_temp)
        elif self.current_mode == "sharpen":
            processed_image_temp = processed_image_temp.filter(ImageFilter.SHARPEN)
        
        self.processed_image = processed_image_temp
        self.update_image_display()
        self.status_bar.config(text=f"Image mode: {self.current_mode}")

    def create_line_art(self, img):
        gray_img = img.convert('L')
        inverted_img = ImageOps.invert(gray_img)
        blurred_img = inverted_img.filter(ImageFilter.GaussianBlur(radius=2))
        
        final_img = Image.new('L', img.size)
        for x in range(img.width):
            for y in range(img.height):
                pixel_gray = gray_img.getpixel((x, y))
                pixel_blur = blurred_img.getpixel((x, y))
                if pixel_blur == 255:
                    final_img.putpixel((x, y), pixel_gray)
                else:
                    final_img.putpixel((x, y), int(min(255, pixel_gray * 256 / (255 - pixel_blur))))
        
        return final_img.convert('RGB')

    def create_sepia_filter(self, img):
        img = img.convert('RGB')
        sepia_filter = [
            0.393, 0.769, 0.189, 0,
            0.349, 0.686, 0.168, 0,
            0.272, 0.534, 0.131, 0,
        ]
        return img.convert('RGB', sepia_filter)

    def toggle_grid(self):
        if not self.original_image:
            messagebox.showinfo("Info", "Please open a photo first.")
            return

        self.grid_lines_visible = not self.grid_lines_visible
        self.update_image_display()
        self.status_bar.config(text=f"Grid: {'On' if self.grid_lines_visible else 'Off'}")

    def update_image_display(self, event=None):
        if not self.processed_image:
            return

        current_view = self.view_var.get()
        
        try:
            user_dpi = float(self.dpi_entry.get())
        except (ValueError, IndexError):
            user_dpi = 96.0
            self.dpi_entry.delete(0, tk.END)
            self.dpi_entry.insert(0, "96")
            messagebox.showerror("Error", "Invalid DPI value. Using default 96.")

        image_with_grid = self.processed_image.copy()

        if self.grid_lines_visible:
            self.draw_grid(image_with_grid)

        if current_view == "fit_to_window":
            self.canvas_width = self.canvas.winfo_width()
            self.canvas_height = self.canvas.winfo_height()
            aspect_ratio = image_with_grid.width / image_with_grid.height
            if self.canvas_width / self.canvas_height > aspect_ratio:
                new_height = self.canvas_height
                new_width = int(new_height * aspect_ratio)
            else:
                new_width = self.canvas_width
                new_height = int(new_width / aspect_ratio)
            
            resized_image = image_with_grid.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            self.display_image = ImageTk.PhotoImage(resized_image)
            self.canvas.delete("all")
            self.canvas.create_image(self.canvas_width / 2, self.canvas_height / 2, image=self.display_image, anchor=tk.CENTER)
        
        else: # A4 Portrait or Landscape
            if current_view == "a4_portrait":
                target_width_px = int((self.A4_WIDTH_MM / 25.4) * user_dpi)
                target_height_px = int((self.A4_HEIGHT_MM / 25.4) * user_dpi)
            else: # a4_landscape
                target_width_px = int((self.A4_HEIGHT_MM / 25.4) * user_dpi)
                target_height_px = int((self.A4_WIDTH_MM / 25.4) * user_dpi)
            
            self.canvas.config(width=target_width_px, height=target_height_px)
            resized_image = image_with_grid.resize((target_width_px, target_height_px), Image.Resampling.LANCZOS)
            
            self.display_image = ImageTk.PhotoImage(resized_image)
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, image=self.display_image, anchor=tk.NW)

    def draw_grid(self, img):
        """Draws a grid on the image using the specified size."""
        try:
            grid_size = int(self.grid_size_entry.get())
            if grid_size <= 0:
                raise ValueError
        except (ValueError, IndexError):
            messagebox.showerror("Error", "Grid size must be a positive integer.")
            self.grid_lines_visible = False
            return
        
        draw = ImageDraw.Draw(img)
        img_width, img_height = img.size
        
        for x in range(0, img_width, grid_size):
            draw.line([(x, 0), (x, img_height)], fill="red", width=1)
        
        for y in range(0, img_height, grid_size):
            draw.line([(0, y), (img_width, y)], fill="red", width=1)

    def on_window_resize(self, event):
        """Handles window resizing, but only if 'Fit to Window' is selected."""
        if self.view_var.get() == "fit_to_window":
            self.update_image_display()

if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoLineApp(root)
    root.mainloop()