import tkinter as tk
from datetime import datetime
import pyperclip

def generar_cadena():
    dias = ['L', 'Ma', 'Mi', 'J', 'V', 'S', 'D']
    hoy = datetime.now()
    dia_semana = dias[hoy.weekday()]
    dia_mes = hoy.strftime('%d')
    mes = hoy.strftime('%b').lower()
    anio = hoy.strftime('%y')
    cadena = f"{dia_semana}{dia_mes}{mes}{anio}"
    resultado.set(cadena)

def copiar_al_portapapeles():
    pyperclip.copy(resultado.get())

# Crear ventana principal
ventana = tk.Tk()
ventana.title("Generador de Cadena de Fecha")
ventana.geometry("300x150")

resultado = tk.StringVar()

tk.Label(ventana, text="Cadena generada:").pack(pady=5)
tk.Entry(ventana, textvariable=resultado, font=("Arial", 14), justify="center").pack(pady=5)
tk.Button(ventana, text="Generar", command=generar_cadena).pack(pady=5)
tk.Button(ventana, text="Copiar", command=copiar_al_portapapeles).pack(pady=5)

ventana.mainloop()
