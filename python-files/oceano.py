import tkinter as tk
import random
import math

# Crear ventana
root = tk.Tk()
root.title("Océano Animado")
root.geometry("800x600")

# Crear canvas
canvas = tk.Canvas(root, width=800, height=600, bg="#006994")
canvas.pack()

# Lista de peces
peces = []
colores_peces = ["orange", "red", "yellow", "purple", "blue", "green", "pink", "white"]

for _ in range(12):  # Más peces pequeños
    x = random.randint(50, 750)
    y = random.randint(150, 500)
    tamaño = random.randint(15, 30)  # Pequeños
    color = random.choice(colores_peces)
    direccion = random.choice([-1, 1])
    velocidad = random.uniform(1, 3) * direccion

    cuerpo = canvas.create_oval(x, y, x + tamaño, y + tamaño // 2, fill=color, outline="black")
    cola = canvas.create_polygon(x + tamaño * direccion, y + tamaño // 4,
                                 x + tamaño * 1.2 * direccion, y,
                                 x + tamaño * 1.2 * direccion, y + tamaño // 2, fill=color)

    peces.append([cuerpo, cola, velocidad, direccion, 0])  # 0 = fase de animación

# Lista de burbujas
burbujas = []

# Función para crear burbujas
def crear_burbuja():
    if random.random() < 0.3:
        x = random.randint(100, 700)
        y = 600
        burbuja = canvas.create_oval(x, y, x + 10, y + 10, outline="white", fill="lightblue")
        burbujas.append(burbuja)

    root.after(random.randint(2000, 4000), crear_burbuja)

# Variables del barco
barco = None
caña = None
pescado = None

# Función para animar el barco de pesca
def barco_pesca():
    global barco, caña, pescado

    # Borrar barco anterior
    if barco:
        canvas.delete(barco)
    if caña:
        canvas.delete(caña)
    if pescado:
        canvas.delete(pescado)

    # Crear el barco
    x_inicial = -100
    y_barco = 50
    barco = canvas.create_rectangle(x_inicial, y_barco, x_inicial + 80, y_barco + 30, fill="brown")

    caña_x = x_inicial + 40
    caña_y = y_barco + 30
    caña = canvas.create_line(caña_x, caña_y, caña_x, 250, fill="black", width=2)

    def mover_barco(x):
        global pescado
        if x > 850:
            return  # El barco sale de la pantalla

        canvas.move(barco, 5, 0)
        canvas.move(caña, 5, 0)

        # Intentar atrapar un pez
        if 300 < x < 500 and random.random() < 0.05 and peces:
            pez_cazado = random.choice(peces)
            peces.remove(pez_cazado)
            pescado = pez_cazado[0]
            canvas.delete(pez_cazado[1])  # Eliminar cola del pez
            canvas.coords(pescado, caña_x - 10, 250, caña_x + 10, 270)

        # Subir el pez si fue atrapado
        if pescado:
            x1, y1, x2, y2 = canvas.coords(pescado)
            if y1 > 100:
                canvas.move(pescado, 0, -3)
            else:
                canvas.delete(pescado)
                pescado = None  # El pez es atrapado

        root.after(50, mover_barco, x + 5)

    mover_barco(x_inicial)
    root.after(120000, barco_pesca)  # Repetir cada 2 min

# Función para animar el océano
def animar(tiempo=0):
    # Mover peces con animación de la cola
    for pez in peces:
        cuerpo, cola, velocidad, direccion, fase = pez
        canvas.move(cuerpo, velocidad, 0)
        canvas.move(cola, velocidad, 0)

        # Animación oscilante de la cola
        desplazamiento_cola = math.sin(fase) * 3 * direccion
        x1, y1, x2, y2 = canvas.coords(cola)
        canvas.coords(cola, x1 + desplazamiento_cola, y1, x2, y2, x2, y2 - 5)
        pez[4] += 0.2  # Fase de animación

        # Si el pez se sale, reaparece en el otro lado
        x1, _, x2, _ = canvas.coords(cuerpo)
        if (direccion == 1 and x1 > 800) or (direccion == -1 and x2 < 0):
            nuevo_x = -50 if direccion == 1 else 850
            nuevo_y = random.randint(100, 500)
            tamaño = random.randint(15, 30)
            canvas.coords(cuerpo, nuevo_x, nuevo_y, nuevo_x + tamaño, nuevo_y + tamaño // 2)
            canvas.coords(cola, nuevo_x + tamaño * direccion, nuevo_y + tamaño // 4,
                          nuevo_x + tamaño * 1.2 * direccion, nuevo_y,
                          nuevo_x + tamaño * 1.2 * direccion, nuevo_y + tamaño // 2)
            pez[4] = 0  # Reiniciar animación de la cola

    # Mover burbujas
    for burbuja in burbujas:
        canvas.move(burbuja, 0, -2)
        if canvas.coords(burbuja)[1] < 0:
            canvas.delete(burbuja)
            burbujas.remove(burbuja)

    root.after(50, animar, tiempo + 1)

# Iniciar animación
animar()
crear_burbuja()
root.after(5000, barco_pesca)  # Espera 5s antes de la primera aparición del barco
root.mainloop()
