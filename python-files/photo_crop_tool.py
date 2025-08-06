import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

# 轉成像素大小（12cm x 9cm）@ 300dpi
CROP_WIDTH_PX = int(12 / 2.54 * 300)
CROP_HEIGHT_PX = int(9 / 2.54 * 300)

class PhotoCropApp:
    def __init__(self, root):
        self.root = root
        self.root.title("照片裁切工具")

        self.canvas = tk.Canvas(root, width=CROP_WIDTH_PX, height=CROP_HEIGHT_PX)
        self.canvas.pack()

        self.btn_load = tk.Button(root, text="選擇照片", command=self.load_image)
        self.btn_load.pack()

        self.btn_crop = tk.Button(root, text="裁切並另存", command=self.crop_and_save)
        self.btn_crop.pack()

        self.image = None
        self.tk_image = None
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.drag_start = None

        self.canvas.bind("<B1-Motion>", self.drag_image)
        self.canvas.bind("<Button-1>", self.start_drag)

    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if not path:
            return
        self.image = Image.open(path).convert("RGB")

        self.scale = min(CROP_WIDTH_PX / self.image.width, CROP_HEIGHT_PX / self.image.height)
        self.offset_x = (CROP_WIDTH_PX - self.image.width * self.scale) / 2
        self.offset_y = (CROP_HEIGHT_PX - self.image.height * self.scale) / 2

        self.redraw()

    def redraw(self):
        if self.image:
            resized = self.image.resize((int(self.image.width * self.scale), int(self.image.height * self.scale)))
            self.tk_image = ImageTk.PhotoImage(resized)
            self.canvas.delete("all")
            self.canvas.create_image(self.offset_x, self.offset_y, anchor="nw", image=self.tk_image)
            self.canvas.create_rectangle(0, 0, CROP_WIDTH_PX, CROP_HEIGHT_PX, outline="red", width=2)

    def start_drag(self, event):
        self.drag_start = (event.x, event.y)

    def drag_image(self, event):
        if self.drag_start:
            dx = event.x - self.drag_start[0]
            dy = event.y - self.drag_start[1]
            self.offset_x += dx
            self.offset_y += dy
            self.drag_start = (event.x, event.y)
            self.redraw()

    def crop_and_save(self):
        if not self.image:
            return

        # 計算原圖中要裁切的區域
        left = max(0, int(-self.offset_x / self.scale))
        top = max(0, int(-self.offset_y / self.scale))
        right = int(left + CROP_WIDTH_PX / self.scale)
        bottom = int(top + CROP_HEIGHT_PX / self.scale)

        cropped = self.image.crop((left, top, right, bottom))
        cropped = cropped.resize((CROP_WIDTH_PX, CROP_HEIGHT_PX))

        path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG", "*.jpg")])
        if path:
            cropped.save(path)
            print("已儲存：", path)

# 啟動程式
if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoCropApp(root)
    root.mainloop()
