import tkinter as tk
from tkinter import messagebox
import random

# Función para verificar si el número es par o impar
def verificar():
    try:
        numero = int(entrada.get())
        # 5% de probabilidad de mostrar el mensaje especial
        if random.random() < 0.05:
            messagebox.showinfo("¡Sorpresa!", "ERES UN DINOSAURIO: LOGRO 1/10 CONSEGUIDO")
            return
        if numero % 2 == 0:
            resultado = f"{numero} es PAR"
        else:
            resultado = f"{numero} es IMPAR"
        messagebox.showinfo("Resultado", resultado)
    except ValueError:
        messagebox.showerror("Error", "Por favor, ingrese un número válido.")

# Crear ventana principal
ventana = tk.Tk()
ventana.title("Verificador Par o Impar")
ventana.geometry("300x150")

# Etiqueta y campo de entrada
etiqueta = tk.Label(ventana, text="Ingrese un número:")
etiqueta.pack(pady=10)
entrada = tk.Entry(ventana)
entrada.pack(pady=5)

# Botón para verificar
boton = tk.Button(ventana, text="Verificar", command=verificar)
boton.pack(pady=10)

ventana.mainloop()
