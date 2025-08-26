import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox
import os

# Create a custom style for the app
class PaintApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Epic 2D Drawing App!")
        self.root.geometry("800x600")
        self.root.config(bg="#2F2F2F")  # Dark background color for contrast

        self.canvas_width = 600
        self.canvas_height = 400
        
        # Initial color and brush size
        self.current_color = "#FF5733"  # Default color is a vibrant red
        self.brush_size = 5
        
        # Creating the canvas for drawing
        self.canvas = tk.Canvas(self.root, width=self.canvas_width, height=self.canvas_height, bg="white")
        self.canvas.pack(pady=20)
        
        self.last_x, self.last_y = None, None
        self.canvas.bind("<B1-Motion>", self.paint)  # Left mouse button to draw
        self.canvas.bind("<ButtonRelease-1>", self.reset)  # When mouse button is released
        
        # Set up controls
        self.setup_controls()

    def setup_controls(self):
        # Color button
        self.color_button = self.create_button("Choose Color", self.choose_color, "#3498db", "#2980b9")
        self.color_button.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Brush size label and slider
        self.brush_size_label = self.create_label("Brush Size:")
        self.brush_size_label.pack(side=tk.LEFT, padx=10)
        
        self.brush_size_slider = self.create_slider(1, 20, self.change_brush_size)
        self.brush_size_slider.set(self.brush_size)
        self.brush_size_slider.pack(side=tk.LEFT, padx=10)

        # Clear canvas button
        self.clear_button = self.create_button("Clear Canvas", self.clear_canvas, "#e74c3c", "#c0392b")
        self.clear_button.pack(side=tk.LEFT, padx=10, pady=10)

        # Save drawing button
        self.save_button = self.create_button("Save Drawing", self.save_drawing, "#2ecc71", "#27ae60")
        self.save_button.pack(side=tk.LEFT, padx=10, pady=10)

    def create_button(self, text, command, bg_color, hover_color):
        """Creates a custom styled button with hover effects."""
        button = tk.Button(self.root, text=text, command=command, font=("Helvetica", 14, "bold"), bg=bg_color, fg="white", relief="flat", height=2, width=15)
        button.bind("<Enter>", lambda event, btn=button: self.on_hover(btn, hover_color))
        button.bind("<Leave>", lambda event, btn=button: self.on_leave(btn, bg_color))
        return button

    def on_hover(self, btn, hover_color):
        """Change button color on hover."""
        btn.config(bg=hover_color)

    def on_leave(self, btn, original_color):
        """Revert button color when hover is removed."""
        btn.config(bg=original_color)

    def create_label(self, text):
        """Creates a custom styled label."""
        return tk.Label(self.root, text=text, font=("Helvetica", 12, "bold"), fg="white", bg="#2F2F2F")

    def create_slider(self, min_val, max_val, command):
        """Creates a custom slider for brush size."""
        return tk.Scale(self.root, from_=min_val, to=max_val, orient=tk.HORIZONTAL, command=command, length=150)

    def paint(self, event):
        """Handles drawing on the canvas."""
        if self.last_x and self.last_y:
            x, y = event.x, event.y
            self.canvas.create_line(self.last_x, self.last_y, x, y, width=self.brush_size, fill=self.current_color, capstyle=tk.ROUND, smooth=tk.TRUE)
        self.last_x, self.last_y = event.x, event.y

    def reset(self, event):
        """Resets last_x and last_y after releasing the mouse button."""
        self.last_x, self.last_y = None, None

    def choose_color(self):
        """Opens a color picker dialog and updates the current drawing color."""
        color = colorchooser.askcolor()[1]
        if color:
            self.current_color = color

    def change_brush_size(self, val):
        """Changes the brush size based on the slider value."""
        self.brush_size = int(val)

    def clear_canvas(self):
        """Clears the canvas."""
        self.canvas.delete("all")

    def save_drawing(self):
        """Saves the drawing as a PNG file."""
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
        if file_path:
            self.canvas.postscript(file=file_path + ".eps")  # Save as EPS file first
            # Use PIL to convert EPS to PNG
            try:
                from PIL import Image
                img = Image.open(file_path + ".eps")
                img.save(file_path)
                os.remove(file_path + ".eps")  # Remove the EPS file
                messagebox.showinfo("Saved", f"Drawing saved as {file_path}")
            except ImportError:
                print("PIL library is required to save as PNG.")
                print("Please install it with: pip install pillow")

# Main window setup
root = tk.Tk()
app = PaintApp(root)
root.mainloop()
