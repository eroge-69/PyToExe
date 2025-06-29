import tkinter as tk
from tkinter import ttk
from math import pi

def calcular_area():
    figura = combo_figuras.get()
    try:
        if figura == "Círculo":
            radio = float(entrada1.get())
            area = pi * radio ** 2
            resultado.set(f"Área del círculo: {area:.2f}")
        
        elif figura == "Triángulo":
            base = float(entrada1.get())
            altura = float(entrada2.get())
            area = (base * altura) / 2
            resultado.set(f"Área del triángulo: {area:.2f}")
        
        elif figura == "Rectángulo":
            largo = float(entrada1.get())
            ancho = float(entrada2.get())
            area = largo * ancho
            resultado.set(f"Área del rectángulo: {area:.2f}")
        
        elif figura == "Cuadrado":
            lado = float(entrada1.get())
            area = lado ** 2
            resultado.set(f"Área del cuadrado: {area:.2f}")
    
    except ValueError:
        resultado.set("¡Error! Ingresa valores numéricos válidos.")

def actualizar_campos(event=None):
    # Limpiar campos anteriores
    entrada1.delete(0, tk.END)
    entrada2.delete(0, tk.END)
    etiqueta2.pack_forget()
    entrada2.pack_forget()
    
    figura = combo_figuras.get()
    etiqueta1.config(text="Radio:" if figura == "Círculo" else 
                    "Base:" if figura == "Triángulo" else 
                    "Largo:" if figura == "Rectángulo" else "Lado:")
    
    if figura in ["Triángulo", "Rectángulo"]:
        etiqueta2.config(text="Altura:" if figura == "Triángulo" else "Ancho:")
        etiqueta2.pack(pady=5)
        entrada2.pack(pady=5)

# Configuración de la ventana
root = tk.Tk()
root.title("Calculadora de Áreas")
root.geometry("350x300")

# Variables
resultado = tk.StringVar()
figuras = ["Círculo", "Triángulo", "Rectángulo", "Cuadrado"]

# Widgets
combo_figuras = ttk.Combobox(root, values=figuras, state="readonly")
combo_figuras.set("Círculo")
combo_figuras.pack(pady=10)
combo_figuras.bind("<<ComboboxSelected>>", actualizar_campos)

frame_entradas = tk.Frame(root)
frame_entradas.pack(pady=10)

etiqueta1 = tk.Label(frame_entradas, text="Radio:")
etiqueta1.pack(pady=5)
entrada1 = tk.Entry(frame_entradas)
entrada1.pack(pady=5)

etiqueta2 = tk.Label(frame_entradas, text="Altura:")
entrada2 = tk.Entry(frame_entradas)

boton_calcular = tk.Button(root, text="Calcular Área", command=calcular_area)
boton_calcular.pack(pady=20)

etiqueta_resultado = tk.Label(root, textvariable=resultado, font=("Arial", 10, "bold"))
etiqueta_resultado.pack()

actualizar_campos()  # Inicializar campos
root.mainloop()
