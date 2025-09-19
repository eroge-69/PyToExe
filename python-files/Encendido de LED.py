import tkinter as tk
from tkinter import filedialog, messagebox

class LedCalibradorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Calibrador de LED")

        self.img_led_off = None
        self.img_led_on = None
        self.mostrando_on = False

        self.dx = 0  # desplazamiento X imagen encendida
        self.dy = 0  # desplazamiento Y imagen encendida

        self.canvas = tk.Canvas(root, width=200, height=200)
        self.canvas.pack(pady=10)

        self.info_label = tk.Label(root, text="Desplazamiento: (0, 0)")
        self.info_label.pack()

        self.boton_toggle = tk.Button(root, text="Alternar LED", command=self.toggle_led, state="disabled")
        self.boton_toggle.pack(pady=5)

        # --- Mejora: control manual para espacio y enter ---
        self.boton_toggle.bind("<KeyPress-space>", lambda e: self.boton_toggle.config(relief="sunken"))
        self.boton_toggle.bind("<KeyRelease-space>", lambda e: (self.boton_toggle.invoke(), self.boton_toggle.config(relief="raised")))
        self.boton_toggle.bind("<Return>", lambda e: self.boton_toggle.invoke())

        self.boton_reset = tk.Button(root, text="Resetear desplazamiento", command=self.reset_desplazamiento, state="disabled")
        self.boton_reset.pack(pady=5)

        self.boton_cargar = tk.Button(root, text="Seleccionar imágenes", command=self.cargar_imagenes)
        self.boton_cargar.pack(pady=5)

        self.root.bind("<Up>", self.mover_arriba)
        self.root.bind("<Down>", self.mover_abajo)
        self.root.bind("<Left>", self.mover_izquierda)
        self.root.bind("<Right>", self.mover_derecha)

    def cargar_imagenes(self):
        archivos = filedialog.askopenfilenames(
            title="Selecciona dos imágenes (apagado y encendido)",
            filetypes=[("Imágenes PPM o GIF", "*.ppm *.gif")],
        )

        if len(archivos) != 2:
            messagebox.showerror("Error", "Debes seleccionar exactamente dos imágenes.")
            return

        try:
            self.img_led_off = tk.PhotoImage(file=archivos[0])
            self.img_led_on = tk.PhotoImage(file=archivos[1])
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las imágenes:\n{e}")
            return

        ancho = max(self.img_led_off.width(), self.img_led_on.width())
        alto = max(self.img_led_off.height(), self.img_led_on.height())

        self.canvas.config(width=ancho, height=alto)
        self.canvas.delete("all")

        self.dx = 0
        self.dy = 0

        self.x = ancho / 2
        self.y = alto / 2

        self.img_id_off = self.canvas.create_image(self.x, self.y - 1, image=self.img_led_off)
        self.img_id_on = self.canvas.create_image(self.x + self.dx, self.y + self.dy, image=self.img_led_on)
        self.canvas.itemconfigure(self.img_id_on, state="hidden")

        self.mostrando_on = False
        self.boton_toggle.config(state="normal")
        self.boton_reset.config(state="normal")

        # Dar foco al botón "Alternar LED"
        self.boton_toggle.focus_set()

        self.actualizar_info()

    def toggle_led(self):
        if self.mostrando_on:
            self.canvas.itemconfigure(self.img_id_on, state="hidden")
            self.canvas.itemconfigure(self.img_id_off, state="normal")
        else:
            self.canvas.itemconfigure(self.img_id_on, state="normal")
            self.canvas.itemconfigure(self.img_id_off, state="hidden")
        self.mostrando_on = not self.mostrando_on

    def actualizar_info(self):
        self.info_label.config(text=f"Desplazamiento: (dx={self.dx}, dy={self.dy})")
        # Actualizar posición imagen encendida
        self.canvas.coords(self.img_id_on, self.x + self.dx, self.y + self.dy)

    def mover_arriba(self, event):
        if self.img_led_on:
            self.dy -= 1
            self.actualizar_info()

    def mover_abajo(self, event):
        if self.img_led_on:
            self.dy += 1
            self.actualizar_info()

    def mover_izquierda(self, event):
        if self.img_led_on:
            self.dx -= 1
            self.actualizar_info()

    def mover_derecha(self, event):
        if self.img_led_on:
            self.dx += 1
            self.actualizar_info()

    def reset_desplazamiento(self):
        self.dx = 0
        self.dy = 0
        self.actualizar_info()

if __name__ == "__main__":
    root = tk.Tk()
    app = LedCalibradorApp(root)
    root.mainloop()
