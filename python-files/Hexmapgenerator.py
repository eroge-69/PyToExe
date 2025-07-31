import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os

def convert_bitmap_to_hexmap(bitmap, width, height, min_height=-10, max_height=10):
    if len(bitmap) != width * height:
        raise ValueError("Bitmap size does not match provided dimensions.")

    min_val = min(bitmap)
    max_val = max(bitmap)
    range_val = max_val - min_val if max_val != min_val else 1

    def scale_brightness(val):
        return round(((val - min_val) / range_val) * (max_height - min_height) + min_height)

    output = [f"size {width} {height}"]
    for row in range(1, height + 1):
        for col in range(1, width + 1):
            idx = (row - 1) * width + (col - 1)
            brightness = scale_brightness(bitmap[idx])
            coord = f"{col:02d}{row:02d}"
            output.append(f"hex {coord} {brightness:+d} \"\" \"\"")
    output.append("end")
    output = [line.replace("+", "") if line.startswith("hex ") else line for line in output]
    return "\n".join(output)

def jpeg_to_bitmap(input_path, output_width, output_height):
    img = Image.open(input_path).convert("L")
    img_resized = img.resize((output_width, output_height), Image.LANCZOS)
    pixels = list(img_resized.getdata())
    return pixels

class HexmapApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hexmap Generator")

        self.image_path = None

        # File load button
        tk.Button(root, text="Select Image", command=self.load_image).grid(row=0, column=0, columnspan=2, pady=5)

        # Inputs
        tk.Label(root, text="Width:").grid(row=1, column=0, sticky="e")
        self.width_entry = tk.Entry(root)
        self.width_entry.grid(row=1, column=1)

        tk.Label(root, text="Height:").grid(row=2, column=0, sticky="e")
        self.height_entry = tk.Entry(root)
        self.height_entry.grid(row=2, column=1)

        tk.Label(root, text="Min Height:").grid(row=3, column=0, sticky="e")
        self.min_height_entry = tk.Entry(root)
        self.min_height_entry.insert(0, "-10")
        self.min_height_entry.grid(row=3, column=1)

        tk.Label(root, text="Max Height:").grid(row=4, column=0, sticky="e")
        self.max_height_entry = tk.Entry(root)
        self.max_height_entry.insert(0, "10")
        self.max_height_entry.grid(row=4, column=1)

        # Preview label title
        tk.Label(root, text="Image Preview:").grid(row=5, column=0, columnspan=2)

        # Image preview display
        self.preview_label = tk.Label(root)
        self.preview_label.grid(row=6, column=0, columnspan=2, pady=10)

        # Export button
        tk.Button(root, text="Generate Hexmap", command=self.generate_hexmap).grid(row=7, column=0, columnspan=2, pady=10)

    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")])
        if path:
            self.image_path = path
            messagebox.showinfo("Image Loaded", f"Loaded: {os.path.basename(path)}")

            # Load and display preview (grayscale)
            img = Image.open(path).convert("L")
            img.thumbnail((200, 200))
            self.tk_image = ImageTk.PhotoImage(img)
            self.preview_label.config(image=self.tk_image)

    def generate_hexmap(self):
        if not self.image_path:
            messagebox.showerror("Error", "No image selected.")
            return

        try:
            width = int(self.width_entry.get())
            height = int(self.height_entry.get())
            min_h = int(self.min_height_entry.get())
            max_h = int(self.max_height_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter valid integers.")
            return

        if min_h >= max_h:
            messagebox.showerror("Error", "Minimum height must be less than maximum height.")
            return

        try:
            bitmap = jpeg_to_bitmap(self.image_path, width, height)
            hexmap = convert_bitmap_to_hexmap(bitmap, width, height, min_h, max_h)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to convert image:\n{e}")
            return

        save_path = filedialog.asksaveasfilename(defaultextension=".board", filetypes=[("Board File", "*.board")])
        if save_path:
            with open(save_path, "w") as f:
                f.write(hexmap)
            messagebox.showinfo("Saved", f"Board saved to: {save_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = HexmapApp(root)
    root.mainloop()
