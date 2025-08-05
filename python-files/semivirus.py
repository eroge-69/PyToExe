import tkinter as tk
from tkinter import messagebox
import threading
import random

def crear_ventana():
    ventana = tk.Toplevel()
    ventana.title("¡Atención!")
    ventana.geometry(f"200x100+{random.randint(0, 1000)}+{random.randint(0, 600)}")
    label = tk.Label(ventana, text="su pc acaba de ser infectada😃")
    label.pack(expand=True)

def generar_ventanas_multiples(cantidad):
    for _ in range(cantidad):
        threading.Thread(target=crear_ventana).start()

root = tk.Tk()
root.withdraw()  # Oculta ventana principal

# Crear muchas ventanas
generar_ventanas_multiples(10)  # Puedes cambiar a 50, 100, etc.

root.mainloop()
