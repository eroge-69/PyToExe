import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

def prepare_for_xtool(input_path, output_path, width_mm=50, dpi=300, method="floyd-steinberg"):
    width_in = width_mm / 25.4
    pixel_width = int(width_in * dpi)

    img = Image.open(input_path).convert("L")

    w, h = img.size
    aspect = h / w
    pixel_height = int(pixel_width * aspect)
    img = img.resize((pixel_width, pixel_height), Image.LANCZOS)

    if method == "threshold":
        img = img.point(lambda x: 255 if x > 128 else 0, "1")
    else:
        img = img.convert("1")  # Floyd–Steinberg dithering

    img.save(output_path, "PNG")
    return output_path


class XToolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("xTool F1 Photo Preparer")

        tk.Label(root, text="Output Width (mm):").grid(row=0, column=0, sticky="e")
        self.width_entry = tk.Entry(root)
        self.width_entry.insert(0, "50")
        self.width_entry.grid(row=0, column=1)

        tk.Label(root, text="DPI:").grid(row=1, column=0, sticky="e")
        self.dpi_entry = tk.Entry(root)
        self.dpi_entry.insert(0, "300")
        self.dpi_entry.grid(row=1, column=1)

        tk.Label(root, text="Dithering:").grid(row=2, column=0, sticky="e")
        self.method_var = tk.StringVar(value="floyd-steinberg")
        tk.OptionMenu(root, self.method_var, "floyd-steinberg", "threshold").grid(row=2, column=1)

        self.preview_label = tk.Label(root)
        self.preview_label.grid(row=3, column=0, columnspan=2, pady=10)

        tk.Button(root, text="Choose Photo", command=self.load_image).grid(row=4, column=0, pady=5)
        tk.Button(root, text="Save Processed", command=self.save_image).grid(row=4, column=1, pady=5)

        self.img = None
        self.img_path = None

    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.png *.jpeg *.bmp")])
        if path:
            self.img_path = path
            preview = Image.open(path).resize((200, 200))
            self.img_preview = ImageTk.PhotoImage(preview)
            self.preview_label.config(image=self.img_preview)

    def save_image(self):
        if not self.img_path:
            messagebox.showerror("Error", "Please load an image first!")
            return

        try:
            width_mm = float(self.width_entry.get())
            dpi = int(self.dpi_entry.get())
            method = self.method_var.get()
        except ValueError:
            messagebox.showerror("Error", "Invalid width or DPI!")
            return

        save_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG files", "*.png")])
        if save_path:
            out = prepare_for_xtool(self.img_path, save_path, width_mm, dpi, method)
            messagebox.showinfo("Done", f"Saved processed image:\n{out}")


if __name__ == "__main__":
    root = tk.Tk()
    app = XToolApp(root)
    root.mainloop()
