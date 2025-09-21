import turtle
import tkinter as tk
from threading import Thread
import random

# ========================
# CONFIGURACIÓN DEL MENSAJE
# ========================

nombre = "Amnelis"

mensaje_final = f"""Para {nombre}

Quiero que sepas que para mí eres una chica genial, eres muy alegre y energética.
Sé que esto no es una disculpa y puede que aún me odies, pero que sepas que me alegra
el haber podido hablar contigo, aunque sea por este corto periodo.
Quiero desearte un feliz inicio de primavera.
No te rindas y mantente determinada, te amo mucho... cuídate 💖
"""

# ========================
# FLOR PRINCIPAL
# ========================

def dibujar_flor(t, x, y, tamaño=1.0):
    t.penup()
    t.goto(x, y)
    t.pendown()
    t.color("gold", "yellow")
    t.pensize(2)

    def petalo():
        t.begin_fill()
        for _ in range(2):
            t.circle(60 * tamaño, 60)
            t.left(120)
        t.end_fill()

    for _ in range(12):
        petalo()
        t.left(360 / 12)

    # Centro
    t.penup()
    t.goto(x, y - 20 * tamaño)
    t.pendown()
    t.color("orange", "orange")
    t.begin_fill()
    t.circle(20 * tamaño)
    t.end_fill()


# ========================
# RAMO DE TULIPANES
# ========================

def dibujar_tulipan(t, x, y, color_petalos="red"):
    t.penup()
    t.goto(x, y)
    t.pendown()
    t.color("green")
    t.setheading(-90)
    t.pensize(3)
    t.forward(80)

    t.color(color_petalos)
    t.setheading(0)
    t.begin_fill()
    for _ in range(3):
        t.circle(10, 180)
        t.right(120)
    t.end_fill()


def dibujar_ramo(t):
    colores = ["red", "pink", "purple", "orange"]
    posiciones = [(-120, -100), (-90, -90), (-60, -110), (-30, -100), (0, -90), (30, -105)]

    for i, pos in enumerate(posiciones):
        dibujar_tulipan(t, pos[0], pos[1], random.choice(colores))


# ========================
# ESCENA COMPLETA
# ========================

def mostrar_dibujo():
    t = turtle.Turtle()
    turtle.bgcolor("white")
    turtle.title("🌷 Regalo de Primavera para Amnelis")
    t.speed(0)
    t.hideturtle()

    # Dibujar múltiples flores grandes
    coords_flores = [(-200, 150), (0, 100), (200, 140), (-150, -50), (150, -70)]
    for x, y in coords_flores:
        dibujar_flor(t, x, y, tamaño=1.2)

    # Dibujar ramo de tulipanes
    dibujar_ramo(t)

    turtle.done()


def lanzar_dibujo():
    Thread(target=mostrar_dibujo).start()


# ========================
# INTERFAZ TKINTER
# ========================

ventana = tk.Tk()
ventana.title("🌼 Regalo de Primavera")
ventana.geometry("700x500")
ventana.configure(bg="white")

# Botón para abrir regalo
boton = tk.Button(
    ventana,
    text="🎁 Abrir regalo",
    font=("Arial", 16, "bold"),
    bg="#ffcc00",
    fg="black",
    padx=20,
    pady=10,
    command=lanzar_dibujo
)
boton.pack(pady=30)

# Mostrar mensaje
mensaje_label = tk.Label(
    ventana,
    text=mensaje_final,
    font=("Helvetica", 13),
    wraplength=600,
    justify="left",
    bg="white"
)
mensaje_label.pack(pady=10)

ventana.mainloop()