from re import S
import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox
from PIL import Image, ImageTk
import random
import colorsys
import numpy as np

def random_hue(img: Image.Image) -> Image.Image:
    img = img.convert("RGBA")
    pixels = img.load()
    width, height = img.size

    unique_colours = set()
    for y in range(height):
        for x in range(width):
            unique_colours.add(pixels[x, y])

    colour_map = {}
    for colour in unique_colours:
        r, g, b, a = colour
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        new_h = random.random()
        new_r, new_g, new_b = colorsys.hsv_to_rgb(new_h, s, v)
        colour_map[colour] = (
            int(new_r * 255),
            int(new_g * 255),
            int(new_b * 255),
            a
        )

    for y in range(height):
        for x in range(width):
            orig = pixels[x, y]
            pixels[x, y] = colour_map[orig]
    
    return img

class ColourPickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Super Ultimate Colour Picker")
        self.root.geometry("300x450")
        self.root.iconbitmap("icon.ico")
        self.img = None
        self.tk_img = None
        self.tk_img_out = None
        self.out_img = None
        self.dark_mode = True  # Always dark mode

        self.load_btn = tk.Button(root, text="Load Image", command=self.load_image, font=("Arial", 8))
        self.load_btn.pack(pady=(10, 5))  # Top margin for first button

        self.random_btn = tk.Button(root, text="Randomize Hue", command=self.randomize_hue, font=("Arial", 8))
        self.random_btn.pack(pady=5)

        self.save_btn = tk.Button(root, text="Save Output", command=self.save_output, font=("Arial", 8))
        self.save_btn.pack(pady=5)

        self.status = tk.Label(root, text="")
        self.status.pack(pady=(10, 5))

        self.canvas = tk.Label(root)
        self.canvas.pack()

        self.canvas_out = tk.Label(root)
        self.canvas_out.pack()

        self.footer = tk.Label(root, text="Super Ultimate Colour Picker, for Braxton", font=("Arial", 8))
        self.footer.pack(side="bottom", pady=4)

        self.set_dark_mode(True)

    def set_dark_mode(self, enable):
        bg = "#222222" if enable else "#f0f0f0"
        fg = "#f0f0f0" if enable else "#000000"
        btn_bg = "#333333" if enable else "#f0f0f0"
        btn_fg = "#f0f0f0" if enable else "#000000"
        self.root.configure(bg=bg)
        widgets = [
            self.load_btn, self.random_btn, self.save_btn,
            self.status, self.canvas, self.canvas_out, self.footer
        ]
        for w in widgets:
            if isinstance(w, tk.Button):
                w.configure(bg=btn_bg, fg=btn_fg, activebackground=bg, activeforeground=fg)
            else:
                w.configure(bg=bg, fg=fg)
    
    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if not file_path:
            return
        self.img = Image.open(file_path).resize((128, 128))
        self.tk_img = ImageTk.PhotoImage(self.img)
        self.canvas.config(image=self.tk_img)
        self.status.config(text=f"Loaded: {file_path}")

    def randomize_hue(self):
        if self.img is None:
            messagebox.showerror("Error", "No image loaded.")
            return
        self.out_img = random_hue(self.img.copy())
        self.tk_img_out = ImageTk.PhotoImage(self.out_img)
        self.canvas_out.config(image=self.tk_img_out)
        self.status.config(text="Hue randomized and image updated.")

    def save_output(self):
        if self.out_img is None:
            messagebox.showerror("Error", "No randomized image to save.")
            return
        filetypes = [
            ("PNG files", "*.png"),
            ("JPEG files", "*.jpg;*.jpeg"),
            ("BMP files", "*.bmp"),
            ("All files", "*.*"),
        ]
        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=filetypes,
            title="Save Randomized Image"
        )
        if not save_path:
            return  # User cancelled
        try:
            # Determine format from extension
            ext = save_path.split('.')[-1].upper()
            fmt = "PNG" if ext == "PNG" else "JPEG" if ext in ("JPG", "JPEG") else ext
            self.out_img.save(save_path, format=fmt)
            self.status.config(text=f'Saved as "{save_path}"')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save image: {e}")

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = ColourPickerApp(root)
        root.mainloop()
    except Exception as e:
        import traceback
        print("An error occurred:", e)
        traceback.print_exc()
        input("Press Enter to exit...")