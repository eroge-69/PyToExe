
import tkinter as tk
from tkinter import messagebox
import random

def no_se_puede(event):
    x = random.randint(0, 200)
    y = random.randint(0, 100)
    boton_no.place(x=x, y=y)

def si_presionado():
    ventana.destroy()
    messagebox.showinfo("¡Gracias!", "¡Gracias por ser mi amigo! 😄")

ventana = tk.Tk()
ventana.title("¿Quieres ser mi amigo? 🤝")
ventana.geometry("300x150")
ventana.resizable(False, False)

etiqueta = tk.Label(ventana, text="¿Quieres ser mi amigo?", font=("Arial", 14))
etiqueta.pack(pady=20)

boton_si = tk.Button(ventana, text="Sí", width=10, command=si_presionado)
boton_si.pack(side="left", padx=40, pady=20)

boton_no = tk.Button(ventana, text="No", width=10)
boton_no.place(x=180, y=80)
boton_no.bind("<Enter>", no_se_puede)

ventana.mainloop()
