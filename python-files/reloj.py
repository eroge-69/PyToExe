import tkinter as tk
import time
import math

class RelojAnalogico:
    def __init__(self, root):
        self.root = root
        self.root.title("Reloj de Manecillas con Números")
        self.canvas = tk.Canvas(root, width=400, height=400, bg='white')
        self.canvas.pack()
        self.radio = 150
        self.centro = (200, 200)

        self.actualizar_reloj()

    def dibujar_esfera(self):
        x, y = self.centro
        self.canvas.create_oval(x - self.radio, y - self.radio, x + self.radio, y + self.radio, outline='black', width=3)

        # Dibujar marcas de horas y números
        for i in range(1, 13):
            angulo = math.radians(i * 30)
            # Marcas de hora
            x1 = x + math.sin(angulo) * (self.radio - 10)
            y1 = y - math.cos(angulo) * (self.radio - 10)
            x2 = x + math.sin(angulo) * (self.radio - 20)
            y2 = y - math.cos(angulo) * (self.radio - 20)
            self.canvas.create_line(x1, y1, x2, y2, fill='black', width=2)

            # Números
            xn = x + math.sin(angulo) * (self.radio - 30)
            yn = y - math.cos(angulo) * (self.radio - 30)
            self.canvas.create_text(xn, yn, text=str(i), font=("Arial", 12, "bold"))

    def dibujar_manecilla(self, angulo, largo, color, ancho):
        x, y = self.centro
        rad = math.radians(angulo)
        x2 = x + math.sin(rad) * largo
        y2 = y - math.cos(rad) * largo
        self.canvas.create_line(x, y, x2, y2, fill=color, width=ancho)

    def actualizar_reloj(self):
        self.canvas.delete("all")
        self.dibujar_esfera()

        ahora = time.localtime()
        hora = ahora.tm_hour % 12
        minuto = ahora.tm_min
        segundo = ahora.tm_sec

        # Calcular ángulos
        angulo_hora = (hora + minuto / 60) * 30
        angulo_minuto = (minuto + segundo / 60) * 6
        angulo_segundo = segundo * 6

        # Dibujar manecillas
        self.dibujar_manecilla(angulo_hora, self.radio * 0.5, 'black', 6)
        self.dibujar_manecilla(angulo_minuto, self.radio * 0.75, 'blue', 4)
        self.dibujar_manecilla(angulo_segundo, self.radio * 0.9, 'red', 2)

        self.root.after(1000, self.actualizar_reloj)

# Ejecutar la app
if __name__ == "__main__":
    root = tk.Tk()
    app = RelojAnalogico(root)
    root.mainloop()
