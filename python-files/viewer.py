import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

class ImageViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Vienkāršs attēlu skatītājs')
        self.geometry('800x600')
        self.configure(bg='black')
        self.resizable(True, True)
        self.canvas = tk.Canvas(self, bg='black', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.image = None
        self.imgtk = None
        self.zoom = 1.0
        self.pan_start = None
        self.offset_x = 0
        self.offset_y = 0
        self.canvas.bind('<MouseWheel>', self.on_zoom)
        self.canvas.bind('<ButtonPress-1>', self.on_pan_start)
        self.canvas.bind('<B1-Motion>', self.on_pan_move)
        self.bind('<Configure>', self.on_resize)
        self.open_image()

    def open_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[('Image Files', '*.png;*.jpg;*.jpeg;*.bmp;*.gif;*.tiff')])
        if not file_path:
            self.destroy()
            return
        self.image = Image.open(file_path)
        self.zoom = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.show_image()

    def show_image(self):
        if self.image is None:
            return
        w, h = self.image.size
        zoomed = self.image.resize((int(w * self.zoom), int(h * self.zoom)), Image.LANCZOS)
        self.imgtk = ImageTk.PhotoImage(zoomed)
        self.canvas.delete('all')
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        x = (cw - zoomed.width) // 2 + self.offset_x
        y = (ch - zoomed.height) // 2 + self.offset_y
        self.canvas.create_image(x, y, anchor='nw', image=self.imgtk)

    def on_zoom(self, event):
        if self.image is None:
            return
        old_zoom = self.zoom
        if event.delta > 0:
            self.zoom *= 1.1
        else:
            self.zoom /= 1.1
        self.zoom = max(0.1, min(self.zoom, 10))
        # Adjust offset so zoom is centered on mouse
        mouse_x = self.canvas.canvasx(event.x)
        mouse_y = self.canvas.canvasy(event.y)
        self.offset_x = int((self.offset_x + mouse_x) * (self.zoom / old_zoom) - mouse_x)
        self.offset_y = int((self.offset_y + mouse_y) * (self.zoom / old_zoom) - mouse_y)
        self.show_image()

    def on_pan_start(self, event):
        self.pan_start = (event.x, event.y)

    def on_pan_move(self, event):
        if self.pan_start:
            dx = event.x - self.pan_start[0]
            dy = event.y - self.pan_start[1]
            self.offset_x += dx
            self.offset_y += dy
            self.pan_start = (event.x, event.y)
            self.show_image()

    def on_resize(self, event):
        self.show_image()

if __name__ == '__main__':
    app = ImageViewer()
    app.mainloop()
