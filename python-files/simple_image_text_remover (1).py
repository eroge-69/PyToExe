
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw

class SimpleEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Image Text Remover")
        self.root.geometry("800x600")

        self.image = None
        self.tk_image = None
        self.draw = None
        self.rect_start = None
        self.rect = None

        self.canvas = tk.Canvas(root, bg="gray")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        menubar = tk.Menu(root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open Image", command=self.open_image)
        filemenu.add_command(label="Save Image", command=self.save_image)
        menubar.add_cascade(label="File", menu=filemenu)

        root.config(menu=menubar)

        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)

    def open_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        if not file_path:
            return
        self.image = Image.open(file_path).convert("RGBA")
        self.draw = ImageDraw.Draw(self.image)
        self.display_image()

    def display_image(self):
        max_w, max_h = 780, 560
        img_w, img_h = self.image.size
        ratio = min(max_w / img_w, max_h / img_h, 1)
        display_size = (int(img_w * ratio), int(img_h * ratio))
        resized = self.image.resize(display_size, Image.ANTIALIAS)
        self.tk_image = ImageTk.PhotoImage(resized)
        self.canvas.config(width=display_size[0], height=display_size[1])
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

    def on_mouse_down(self, event):
        if not self.image:
            return
        self.rect_start = (event.x, event.y)
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(
            event.x, event.y, event.x, event.y, outline="red", width=2
        )

    def on_mouse_drag(self, event):
        if not self.image or not self.rect_start:
            return
        self.canvas.coords(self.rect, self.rect_start[0], self.rect_start[1], event.x, event.y)

    def on_mouse_up(self, event):
        if not self.image or not self.rect_start:
            return
        x1, y1 = self.rect_start
        x2, y2 = event.x, event.y
        if x1 == x2 or y1 == y2:
            self.canvas.delete(self.rect)
            self.rect = None
            return

        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        img_w, img_h = self.image.size
        ratio = min(canvas_w / img_w, canvas_h / img_h, 1)

        def canvas_to_img(c):
            return int(c / ratio)

        ix1, iy1 = canvas_to_img(min(x1, x2)), canvas_to_img(min(y1, y2))
        ix2, iy2 = canvas_to_img(max(x1, x2)), canvas_to_img(max(y1, y2))

        self.draw.rectangle([ix1, iy1, ix2, iy2], fill=(255, 255, 255, 255))

        self.display_image()
        self.canvas.delete(self.rect)
        self.rect = None

    def save_image(self):
        if not self.image:
            messagebox.showwarning("Warning", "No image to save!")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg;*.jpeg")],
        )
        if not file_path:
            return
        self.image.save(file_path)
        messagebox.showinfo("Saved", f"Image saved to {file_path}")

root = tk.Tk()
app = SimpleEditor(root)
root.mainloop()
