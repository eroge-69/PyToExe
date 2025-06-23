import tkinter as tk
from tkinter import messagebox
import threading
import time
from PIL import Image, ImageTk
from pynput import keyboard, mouse
import os
import sys

# === CONFIGURACIÓN ===
TIEMPO_ESPERA = 5 * 60  # 5 minutos en segundos
CUENTA_ATRAS = 10       # segundos del "formateo"
IMAGEN_PAYASO = "payaso.jpg"  # imagen en mismo directorio

# === CONTROL DE BLOQUEO ===
teclado_bloqueado = True
raton_bloqueado = True

def bloquear_entrada():
    def bloquear_teclado(tecla):
        return False if teclado_bloqueado else True

    def bloquear_raton(*args):
        return None if raton_bloqueado else True

    listener_teclado = keyboard.Listener(on_press=bloquear_teclado)
    listener_raton = mouse.Listener(on_click=bloquear_raton, on_move=bloquear_raton, on_scroll=bloquear_raton)

    listener_teclado.start()
    listener_raton.start()

    return listener_teclado, listener_raton

# === PANTALLAZO AZUL SIMULADO ===
def mostrar_pantalla_azul():
    ventana = tk.Tk()
    ventana.title("Pantallazo Azul")
    ventana.attributes('-fullscreen', True)
    ventana.configure(bg='blue')
    ventana.focus_force()

    etiqueta = tk.Label(
        ventana,
        text="Se ha producido un error y Windows debe reiniciarse.\n\nFormateando disco duro...",
        font=("Consolas", 20),
        fg='white',
        bg='blue',
        justify="center"
    )
    etiqueta.pack(expand=True)

    progreso = tk.Label(ventana, text="Formateo: 100%", font=("Consolas", 24), fg='white', bg='blue')
    progreso.pack()

    def cuenta_atras():
        for i in range(100, -1, -10):
            progreso.config(text=f"Formateo: {i}%")
            ventana.update()
            time.sleep(CUENTA_ATRAS / 10)
        ventana.destroy()
        mostrar_payaso()

    threading.Thread(target=cuenta_atras).start()
    ventana.mainloop()

# === PANTALLA FINAL CON PAYASO ===
def mostrar_payaso():
    global teclado_bloqueado, raton_bloqueado

    ventana = tk.Tk()
    ventana.title("¡Broma final!")
    ventana.attributes('-fullscreen', True)
    ventana.configure(bg='black')

    mensaje = tk.Label(
        ventana,
        text="¿Inocente! Eres tonto, Jesús",
        font=("Arial", 30, "bold"),
        fg='red',
        bg='black'
    )
    mensaje.pack(pady=50)

    imagen_path = recurso_relativo(IMAGEN_PAYASO)
    if os.path.exists(imagen_path):
        imagen = Image.open(imagen_path).resize((400, 400))
        imagen_tk = ImageTk.PhotoImage(imagen)
        imagen_label = tk.Label(ventana, image=imagen_tk, bg='black')
        imagen_label.image = imagen_tk
        imagen_label.pack()

    def cerrar():
        global teclado_bloqueado, raton_bloqueado
        teclado_bloqueado = False
        raton_bloqueado = False
        ventana.destroy()

    ventana.after(5000, cerrar)
    ventana.mainloop()

# === AYUDA PARA CARGAR IMÁGENES EN .EXE ===
def recurso_relativo(ruta):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, ruta)
    return os.path.join(os.path.abspath("."), ruta)

# === FUNCIÓN PRINCIPAL ===
def iniciar_simulacion():
    print("Simulación iniciada. Esperando 5 minutos...")
    time.sleep(TIEMPO_ESPERA)
    mostrar_pantalla_azul()

# === LANZAMIENTO ===
if __name__ == "__main__":
    listener_teclado, listener_raton = bloquear_entrada()
    threading.Thread(target=iniciar_simulacion).start()
