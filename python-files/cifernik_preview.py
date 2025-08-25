import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageDraw

class WatchFaceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Náhled ciferníku Galaxy Watch4")

        self.canvas_size = 450
        self.canvas = tk.Canvas(root, width=self.canvas_size, height=self.canvas_size, bg="black")
        self.canvas.pack()

        self.img = None
        self.tk_img = None
        self.x, self.y = 0, 0
        self.scale = 1.0

        # Ovládací tlačítka
        btn_frame = tk.Frame(root)
        btn_frame.pack()

        tk.Button(btn_frame, text="Načíst fotku", command=self.load_image).pack(side="left")
        tk.Button(btn_frame, text="Uložit náhled", command=self.save_image).pack(side="left")

        # Bind ovládání myší
        self.canvas.bind("<B1-Motion>", self.drag)
        self.canvas.bind("<MouseWheel>", self.zoom)

    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[("Obrázky", "*.jpg *.jpeg *.png")])
        if not path:
            return
        self.img = Image.open(path).convert("RGBA")
        self.scale = 1.0
        self.x, self.y = 0, 0
        self.update_canvas()

    def update_canvas(self):
        if self.img is None:
            return

        # Úprava velikosti a posunu
        w, h = self.img.size
        resized = self.img.resize((int(w*self.scale), int(h*self.scale)), Image.LANCZOS)
        temp = Image.new("RGBA", (self.canvas_size, self.canvas_size), (0,0,0,0))
        temp.paste(resized, (self.x, self.y), resized)

        # Kruh (maska ciferníku)
        mask = Image.new("L", (self.canvas_size, self.canvas_size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, self.canvas_size, self.canvas_size), fill=255)
        circular = Image.new("RGBA", (self.canvas_size, self.canvas_size), (0,0,0,0))
        circular.paste(temp, (0,0), mask)

        self.tk_img = ImageTk.PhotoImage(circular)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)

    def drag(self, event):
        self.x += event.x - self.canvas_size//2
        self.y += event.y - self.canvas_size//2
        self.update_canvas()

    def zoom(self, event):
        if event.delta > 0:
            self.scale *= 1.1
        else:
            self.scale /= 1.1
        self.update_canvas()

    def save_image(self):
        if self.img is None:
            return
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
        if not path:
            return

        # Uloží aktuální stav
        w, h = self.img.size
        resized = self.img.resize((int(w*self.scale), int(h*self.scale)), Image.LANCZOS)
        temp = Image.new("RGBA", (self.canvas_size, self.canvas_size), (0,0,0,0))
        temp.paste(resized, (self.x, self.y), resized)

        mask = Image.new("L", (self.canvas_size, self.canvas_size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, self.canvas_size, self.canvas_size), fill=255)
        circular = Image.new("RGBA", (self.canvas_size, self.canvas_size), (0,0,0,0))
        circular.paste(temp, (0,0), mask)

        circular.save(path)

if __name__ == "__main__":
    root = tk.Tk()
    app = WatchFaceApp(root)
    root.mainloop()
