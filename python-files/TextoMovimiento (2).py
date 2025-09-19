import tkinter as tk
from tkinter import messagebox, simpledialog
import os

# Mapa 5x7 para caracteres (A-Z, espacio y algunos símbolos)
# Cada elemento es una lista de 7 números, cada número es un byte donde
# los 5 bits menos significativos representan una fila (5 columnas)
FONT_5x7 = {
    ' ': [0x00,0x00,0x00,0x00,0x00,0x00,0x00],
    'A': [0x0E,0x11,0x11,0x1F,0x11,0x11,0x11],
    'B': [0x1E,0x11,0x11,0x1E,0x11,0x11,0x1E],
    'C': [0x0E,0x11,0x10,0x10,0x10,0x11,0x0E],
    'D': [0x1E,0x11,0x11,0x11,0x11,0x11,0x1E],
    'E': [0x1F,0x10,0x10,0x1E,0x10,0x10,0x1F],
    'F': [0x1F,0x10,0x10,0x1E,0x10,0x10,0x10],
    'G': [0x0F,0x10,0x10,0x17,0x11,0x11,0x0F],
    'H': [0x11,0x11,0x11,0x1F,0x11,0x11,0x11],
    'I': [0x0E,0x04,0x04,0x04,0x04,0x04,0x0E],
    'J': [0x07,0x02,0x02,0x02,0x12,0x12,0x0C],
    'K': [0x11,0x12,0x14,0x18,0x14,0x12,0x11],
    'L': [0x10,0x10,0x10,0x10,0x10,0x10,0x1F],
    'M': [0x11,0x1B,0x15,0x15,0x11,0x11,0x11],
    'N': [0x11,0x19,0x15,0x13,0x11,0x11,0x11],
    'O': [0x0E,0x11,0x11,0x11,0x11,0x11,0x0E],
    'P': [0x1E,0x11,0x11,0x1E,0x10,0x10,0x10],
    'Q': [0x0E,0x11,0x11,0x11,0x15,0x12,0x0D],
    'R': [0x1E,0x11,0x11,0x1E,0x14,0x12,0x11],
    'S': [0x0F,0x10,0x10,0x0E,0x01,0x01,0x1E],
    'T': [0x1F,0x04,0x04,0x04,0x04,0x04,0x04],
    'U': [0x11,0x11,0x11,0x11,0x11,0x11,0x0E],
    'V': [0x11,0x11,0x11,0x11,0x0A,0x0A,0x04],
    'W': [0x11,0x11,0x11,0x15,0x15,0x15,0x0A],
    'X': [0x11,0x11,0x0A,0x04,0x0A,0x11,0x11],
    'Y': [0x11,0x11,0x11,0x0A,0x04,0x04,0x04],
    'Z': [0x1F,0x01,0x02,0x04,0x08,0x10,0x1F],
    '0': [0x0E,0x11,0x13,0x15,0x19,0x11,0x0E],
    '1': [0x04,0x0C,0x14,0x04,0x04,0x04,0x1F],
    '2': [0x0E,0x11,0x01,0x06,0x08,0x10,0x1F],
    '3': [0x1F,0x02,0x04,0x02,0x01,0x11,0x0E],
    '4': [0x02,0x06,0x0A,0x12,0x1F,0x02,0x02],
    '5': [0x1F,0x10,0x1E,0x01,0x01,0x11,0x0E],
    '6': [0x06,0x08,0x10,0x1E,0x11,0x11,0x0E],
    '7': [0x1F,0x01,0x02,0x04,0x08,0x08,0x08],
    '8': [0x0E,0x11,0x11,0x0E,0x11,0x11,0x0E],
    '9': [0x0E,0x11,0x11,0x0F,0x01,0x02,0x0C],
    '!': [0x04,0x04,0x04,0x04,0x00,0x00,0x04],
    '?': [0x0E,0x11,0x01,0x06,0x04,0x00,0x04],
    '.': [0x00,0x00,0x00,0x00,0x00,0x0C,0x0C],
    ',': [0x00,0x00,0x00,0x00,0x00,0x0C,0x04],
    ':': [0x00,0x0C,0x0C,0x00,0x0C,0x0C,0x00],
    '-': [0x00,0x00,0x00,0x1F,0x00,0x00,0x00],
}

class LedCalibradorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Matriz LED 7x60 con Texto Animado")

        self.rows = 7
        self.cols = 60

        self.img_led_off = None
        self.img_led_on = None
        self.leds = []      # Matriz de objetos de imagen
        self.estados = []   # Matriz de estados

        self.animacion_id = None
        self.text_to_show = ""
        self.text_matriz = []
        self.text_pos = 0

        # Canvas
        self.canvas = tk.Canvas(root)
        self.canvas.pack(padx=10, pady=10)

        # Info
        self.info_label = tk.Label(root, text="Cargando imágenes...")
        self.info_label.pack()

        # Botones
        self.boton_cargar = tk.Button(root, text="Iniciar Animación de Texto", command=self.iniciar)
        self.boton_cargar.pack(pady=5)

        self.boton_stop = tk.Button(root, text="Detener Animación", command=self.detener_animacion, state="disabled")
        self.boton_stop.pack(pady=5)

        # Cargar imágenes y dibujar matriz
        if self.cargar_imagenes():
            self.dibujar_matriz()
            self.info_label.config(text="Presiona 'Iniciar Animación de Texto' para comenzar.")

    def cargar_imagenes(self):
        ruta_img_off = "C:/Users/fk303464/Desktop/Green_OFF.ppm"
        ruta_img_on = "C:/Users/fk303464/Desktop/Green_ON.ppm"

        if not os.path.exists(ruta_img_off) or not os.path.exists(ruta_img_on):
            messagebox.showerror("Error", "No se encontraron las imágenes necesarias.")
            return False

        try:
            # Reducir tamaño de LEDs para que quepan muchos
            self.img_led_off = tk.PhotoImage(file=ruta_img_off).subsample(10)
            self.img_led_on = tk.PhotoImage(file=ruta_img_on).subsample(10)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las imágenes:\n{e}")
            return False

    def dibujar_matriz(self):
        self.canvas.delete("all")
        self.leds = []
        self.estados = []

        spacing = 2
        img_w = self.img_led_off.width()
        img_h = self.img_led_off.height()

        total_w = self.cols * img_w + (self.cols - 1) * spacing
        total_h = self.rows * img_h + (self.rows - 1) * spacing

        self.canvas.config(width=total_w, height=total_h)

        for i in range(self.rows):
            fila_leds = []
            fila_estados = []
            for j in range(self.cols):
                x = j * (img_w + spacing) + img_w / 2
                y = i * (img_h + spacing) + img_h / 2
                led_id = self.canvas.create_image(x, y, image=self.img_led_off)
                fila_leds.append(led_id)
                fila_estados.append(False)
            self.leds.append(fila_leds)
            self.estados.append(fila_estados)

    def texto_a_matriz(self, texto):
        matriz = []
        for letra in texto:
            patron = FONT_5x7.get(letra, FONT_5x7[' '])  # espacio si no existe
            for col in range(5):
                columna_bits = 0
                for fila in range(7):
                    if patron[fila] & (1 << (4 - col)):
                        columna_bits |= (1 << fila)
                matriz.append(columna_bits)
            matriz.append(0)  # columna espacio entre letras
        return matriz

    def iniciar(self):
        if not self.img_led_off or not self.img_led_on:
            messagebox.showerror("Error", "Imágenes no cargadas.")
            return

        texto = simpledialog.askstring("Texto para animar", "Introduce el texto a mostrar en la matriz:")
        if not texto:
            self.info_label.config(text="No se introdujo texto. Animación cancelada.")
            return

        self.text_to_show = texto.upper()
        self.text_matriz = self.texto_a_matriz(self.text_to_show)
        self.text_pos = -self.cols

        self.info_label.config(text=f"Animando texto: {self.text_to_show}")

        self.boton_cargar.config(state="disabled")
        self.boton_stop.config(state="normal")

        self.animar_texto()

    def detener_animacion(self):
        if self.animacion_id:
            self.root.after_cancel(self.animacion_id)
            self.animacion_id = None
        self.info_label.config(text="Animación detenida.")
        self.boton_cargar.config(state="normal")
        self.boton_stop.config(state="disabled")
        self.reset_leds()

    def reset_leds(self):
        for i in range(self.rows):
            for j in range(self.cols):
                self.estados[i][j] = False
                self.canvas.itemconfig(self.leds[i][j], image=self.img_led_off)

    def animar_texto(self):
        self.reset_leds()

        for col in range(self.cols):
            matriz_col = self.text_pos + col
            if 0 <= matriz_col < len(self.text_matriz):
                columna_bits = self.text_matriz[matriz_col]
                for fila in range(self.rows):
                    encendido = (columna_bits >> fila) & 1
                    self.estados[fila][col] = bool(encendido)
                    img = self.img_led_on if encendido else self.img_led_off
                    self.canvas.itemconfig(self.leds[fila][col], image=img)

        self.text_pos += 1
        if self.text_pos > len(self.text_matriz):
            self.text_pos = -self.cols

        self.animacion_id = self.root.after(100, self.animar_texto)  # velocidad animación

if __name__ == "__main__":
    root = tk.Tk()
    app = LedCalibradorApp(root)
    root.mainloop()
