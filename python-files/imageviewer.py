import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

class ImageViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Smooth Image Viewer")
        self.root.geometry("1200x800")
        self.root.configure(bg="#1e1e1e")

        # Canvas setup
        self.canvas = tk.Canvas(root, bg="#1e1e1e", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Bindings
        self.canvas.bind("<Button-1>", self.start_pan)
        self.canvas.bind("<B1-Motion>", self.do_pan)
        self.canvas.bind("<MouseWheel>", self.zoom)  # Windows
        self.canvas.bind("<Button-4>", self.zoom)    # Linux scroll up
        self.canvas.bind("<Button-5>", self.zoom)    # Linux scroll down

        # Menu
        menubar = tk.Menu(root, bg="#2d2d2d", fg="white", tearoff=0)
        file_menu = tk.Menu(menubar, tearoff=0, bg="#2d2d2d", fg="white")
        file_menu.add_command(label="Open Image", command=self.open_image)
        file_menu.add_command(label="Exit", command=root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        root.config(menu=menubar)

        # Image variables
        self.img = None
        self.tk_img = None
        self.image_id = None
        self.scale = 1.0
        self.pan_start = None

    def open_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        if path:
            self.img = Image.open(path)
            self.scale = 1.0
            self.show_image()

    def show_image(self):
        if self.img:
            # Resize image for current scale
            w, h = self.img.size
            w_scaled, h_scaled = int(w * self.scale), int(h * self.scale)
            resized = self.img.resize((w_scaled, h_scaled), Image.LANCZOS)
            self.tk_img = ImageTk.PhotoImage(resized)

            if self.image_id:
                self.canvas.itemconfig(self.image_id, image=self.tk_img)
            else:
                self.image_id = self.canvas.create_image(
                    self.canvas.winfo_width()//2, 
                    self.canvas.winfo_height()//2, 
                    image=self.tk_img
                )
            self.canvas.tag_raise(self.image_id)

    def zoom(self, event):
        # Determine zoom direction
        if event.delta > 0 or event.num == 4:
            factor = 1.1
        else:
            factor = 0.9

        self.scale *= factor
        self.show_image()

    def start_pan(self, event):
        self.pan_start = (event.x, event.y)

    def do_pan(self, event):
        if self.pan_start:
            dx = event.x - self.pan_start[0]
            dy = event.y - self.pan_start[1]
            self.canvas.move(self.image_id, dx, dy)
            self.pan_start = (event.x, event.y)

if __name__ == "__main__":
    root = tk.Tk()
    viewer = ImageViewer(root)
    root.mainloop()
