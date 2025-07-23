
import os
from tkinter import filedialog, messagebox, ttk
from tkinter import *
from PIL import Image, ImageTk

class WebPImgConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("WebPImgConverter")
        self.root.geometry("800x600")

        self.images = []
        self.output_dir = ""
        self.current_image = None
        self.tk_img = None
        self.crop_start = None
        self.crop_rect = None
        self.cropped_img = None
        self.quality = IntVar(value=80)
        self.output_format = StringVar(value=".webp")

        # UI Layout
        frame = Frame(root)
        frame.pack(pady=10)

        Button(frame, text="Select Images", command=self.select_images).grid(row=0, column=0, padx=5)
        Button(frame, text="Output Folder", command=self.select_output_folder).grid(row=0, column=1, padx=5)

        Label(frame, text="Quality:").grid(row=0, column=2, padx=5)
        Scale(frame, from_=1, to=100, orient=HORIZONTAL, variable=self.quality).grid(row=0, column=3, padx=5)

        Label(frame, text="Format:").grid(row=0, column=4, padx=5)
        ttk.Combobox(frame, values=[".webp", ".jpg", ".png"], textvariable=self.output_format, width=6).grid(row=0, column=5)

        Button(frame, text="Convert", command=self.convert_all).grid(row=0, column=6, padx=5)

        # Canvas for preview
        self.canvas = Canvas(root, width=600, height=400, bg='gray')
        self.canvas.pack(pady=10)
        self.canvas.bind("<Button-1>", self.start_crop)
        self.canvas.bind("<B1-Motion>", self.update_crop)
        self.canvas.bind("<ButtonRelease-1>", self.end_crop)

        Button(root, text="Next Image", command=self.next_image).pack(pady=5)

    def select_images(self):
        files = filedialog.askopenfilenames(filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.tiff")])
        if files:
            self.images = list(files)
            self.load_image(0)

    def select_output_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_dir = folder

    def load_image(self, index):
        if not self.images:
            return
        path = self.images[index]
        self.current_image = Image.open(path)
        self.show_image(self.current_image)

    def show_image(self, img):
        img.thumbnail((600, 400))
        self.tk_img = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(300, 200, image=self.tk_img)

    def start_crop(self, event):
        self.crop_start = (event.x, event.y)
        self.crop_rect = self.canvas.create_rectangle(event.x, event.y, event.x, event.y, outline="red")

    def update_crop(self, event):
        if self.crop_rect:
            self.canvas.coords(self.crop_rect, self.crop_start[0], self.crop_start[1], event.x, event.y)

    def end_crop(self, event):
        if not self.crop_start or not self.current_image:
            return

        x0, y0 = self.crop_start
        x1, y1 = event.x, event.y
        x0, x1 = sorted((x0, x1))
        y0, y1 = sorted((y0, y1))

        # Convert canvas coords to image coords
        ratio = min(600 / self.current_image.width, 400 / self.current_image.height)
        ix0 = int(x0 / ratio)
        iy0 = int(y0 / ratio)
        ix1 = int(x1 / ratio)
        iy1 = int(y1 / ratio)

        self.cropped_img = self.current_image.crop((ix0, iy0, ix1, iy1))
        self.show_image(self.cropped_img)

    def convert_all(self):
        if not self.images or not self.output_dir:
            messagebox.showwarning("Missing", "Please select images and output folder.")
            return

        for path in self.images:
            img = Image.open(path)

            # Use cropped version if available
            if self.cropped_img:
                img = self.cropped_img

            filename = os.path.splitext(os.path.basename(path))[0]
            save_path = os.path.join(self.output_dir, filename + self.output_format.get())

            try:
                if self.output_format.get() == ".webp":
                    img.save(save_path, "WEBP", quality=self.quality.get())
                elif self.output_format.get() == ".jpg":
                    img = img.convert("RGB")
                    img.save(save_path, "JPEG", quality=self.quality.get())
                elif self.output_format.get() == ".png":
                    img.save(save_path, "PNG")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save {save_path}\n{e}")

        messagebox.showinfo("Done", f"Images saved to {self.output_dir}")

    def next_image(self):
        if not self.images:
            return
        current_index = self.images.index(self.images[0])
        self.images = self.images[1:] + [self.images[0]]  # Rotate list
        self.cropped_img = None
        self.load_image(0)

if __name__ == "__main__":
    root = Tk()
    app = WebPImgConverter(root)
    root.mainloop()
