from pyembroidery import read
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw

class PESViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Visor PES - Zoom + PNG Export")

        self.scale = 3
        self.offset_x = 20
        self.offset_y = 20

        # Botones
        btn_frame = tk.Frame(root)
        btn_frame.pack()
        tk.Button(btn_frame, text="Abrir archivo PES", command=self.abrir_y_dibujar).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Exportar PNG", command=self.exportar_png).pack(side=tk.LEFT, padx=5)

        # Canvas desplazable
        self.canvas = tk.Canvas(root, width=800, height=600, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<MouseWheel>", self.zoom)
        self.pattern = None
        self.zoom_factor = 1.0

    def abrir_y_dibujar(self):
        archivo = filedialog.askopenfilename(filetypes=[("Archivos PES", "*.pes")])
        if not archivo:
            return

        try:
            self.pattern = read(archivo)
            self.zoom_factor = 1.0
            self.dibujar()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def dibujar(self):
        self.canvas.delete("all")
        if not self.pattern:
            return

        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')

        for stitch in self.pattern.stitches:
            x, y = stitch[0], stitch[1]
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x)
            max_y = max(max_y, y)

        prev = None
        for stitch in self.pattern.stitches:
            x = (stitch[0] - min_x) * self.scale * self.zoom_factor + self.offset_x
            y = (stitch[1] - min_y) * self.scale * self.zoom_factor + self.offset_y

            if prev:
                self.canvas.create_line(prev[0], prev[1], x, y, fill="black")
            prev = (x, y)

        # Ajusta el tamaño del canvas según el zoom
        width = (max_x - min_x) * self.scale * self.zoom_factor + self.offset_x * 2
        height = (max_y - min_y) * self.scale * self.zoom_factor + self.offset_y * 2
        self.canvas.config(scrollregion=(0, 0, width, height))

    def zoom(self, event):
        # Zoom con la rueda del ratón
        if event.delta > 0:
            self.zoom_factor *= 1.1
        else:
            self.zoom_factor /= 1.1
        self.dibujar()

    def exportar_png(self):
        if not self.pattern:
            messagebox.showwarning("Advertencia", "Primero carga un archivo PES.")
            return

        archivo = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
        if not archivo:
            return

        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')
        for stitch in self.pattern.stitches:
            x, y = stitch[0], stitch[1]
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x)
            max_y = max(max_y, y)

        width = int((max_x - min_x) * self.scale * self.zoom_factor + self.offset_x * 2)
        height = int((max_y - min_y) * self.scale * self.zoom_factor + self.offset_y * 2)

        img = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(img)

        prev = None
        for stitch in self.pattern.stitches:
            x = (stitch[0] - min_x) * self.scale * self.zoom_factor + self.offset_x
            y = (stitch[1] - min_y) * self.scale * self.zoom_factor + self.offset_y

            if prev:
                draw.line([prev, (x, y)], fill="black", width=1)
            prev = (x, y)

        try:
            img.save(archivo)
            messagebox.showinfo("Éxito", "Imagen guardada correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la imagen:\n{e}")

# Iniciar app
if __name__ == "__main__":
    root = tk.Tk()
    app = PESViewerApp(root)
    root.mainloop()
