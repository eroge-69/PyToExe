import tkinter as tk
from tkinter import messagebox, ttk

def calcular():
    try:
        x = float(entry.get())
        factor = float(combo.get())
        resultado = (x * factor) * 2.3
        messagebox.showinfo("Resultado", f"El resultado es: {resultado}")
    except ValueError:
        messagebox.showerror("Error", "Por favor ingresa un número válido.")

# Ventana principal
ventana = tk.Tk()
ventana.title("Calculadora (x * factor) * 2.3")
ventana.geometry("320x200")

# Entrada de X
label_x = tk.Label(ventana, text="Ingresa el valor de x:")
label_x.pack(pady=5)

entry = tk.Entry(ventana, justify="center")
entry.pack(pady=5)

# Selección del factor
label_factor = tk.Label(ventana, text="Selecciona el factor:")
label_factor.pack(pady=5)

combo = ttk.Combobox(ventana, values=["0.9", "1.0", "1.1", "1.2"], state="readonly")
combo.current(0)  # valor inicial = 0.9
combo.pack(pady=5)

# Botón calcular
boton = tk.Button(ventana, text="Calcular", command=calcular)
boton.pack(pady=15)

ventana.mainloop()
