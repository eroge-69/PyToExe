import tkinter as tk
from PIL import Image, ImageTk
from tkinter import filedialog

class ImageEditor:
    def __init__(self, root, image_path):
        self.root = root
        self.image_path = image_path
        self.canvas = tk.Canvas(root, width=800, height=600, bg='white')
        self.canvas.pack()

        # Load image using Pillow
        self.image = Image.open(image_path)
        self.original_image = self.image.copy()  # Keep a copy for future reference
        self.image_tk = ImageTk.PhotoImage(self.image)

        # Display image on canvas
        self.image_id = self.canvas.create_image(400, 300, image=self.image_tk)

        # Variables for dragging
        self.drag_data = {"x": 0, "y": 0}

        # Bind mouse events to canvas
        self.canvas.tag_bind(self.image_id, "<ButtonPress-1>", self.on_press)
        self.canvas.tag_bind(self.image_id, "<B1-Motion>", self.on_drag)
        self.canvas.tag_bind(self.image_id, "<ButtonRelease-1>", self.on_release)

        # Zoom, Rotate, and Save buttons
        self.zoom_in_button = tk.Button(root, text="Zoom In", command=self.zoom_in)
        self.zoom_in_button.pack(side=tk.LEFT, padx=5)
        
        self.zoom_out_button = tk.Button(root, text="Zoom Out", command=self.zoom_out)
        self.zoom_out_button.pack(side=tk.LEFT, padx=5)

        self.rotate_button = tk.Button(root, text="Rotate 90°", command=self.rotate_image)
        self.rotate_button.pack(side=tk.LEFT, padx=5)

        self.save_button = tk.Button(root, text="Save Image", command=self.save_image)
        self.save_button.pack(side=tk.LEFT, padx=5)

    def on_press(self, event):
        """This function is called when the mouse button is pressed."""
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def on_drag(self, event):
        """This function is called while the mouse is being dragged."""
        delta_x = event.x - self.drag_data["x"]
        delta_y = event.y - self.drag_data["y"]

        # Move the image on the canvas
        self.canvas.move(self.image_id, delta_x, delta_y)

        # Update the drag data for the next move
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def on_release(self, event):
        """This function is called when the mouse button is released."""
        print("Image moved!")

    def zoom_in(self):
        """Zoom in the image by 1.2x."""
        self.image = self.image.resize((int(self.image.width * 1.2), int(self.image.height * 1.2)))
        self.update_image()

    def zoom_out(self):
        """Zoom out the image by 1.2x."""
        self.image = self.image.resize((int(self.image.width * 0.8), int(self.image.height * 0.8)))
        self.update_image()

    def rotate_image(self):
        """Rotate the image by 90 degrees."""
        self.image = self.image.rotate(90, expand=True)
        self.update_image()

    def update_image(self):
        """Update the image displayed on the canvas after modification."""
        self.image_tk = ImageTk.PhotoImage(self.image)
        self.canvas.itemconfig(self.image_id, image=self.image_tk)

    def save_image(self):
        """Save the current image to a file."""
        save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Files", "*.png"), ("JPEG Files", "*.jpg"), ("All Files", "*.*")])
        if save_path:
            self.image.save(save_path)
            print(f"Image saved to {save_path}")

# Create Tkinter window
root = tk.Tk()
root.title("Image Editor")

# Create an ImageEditor instance with the path to an image
editor = ImageEditor(root, "path_to_your_image.jpg")

# Start the Tkinter main loop
root.mainloop()
