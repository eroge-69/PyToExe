import tkinter as tk
from tkinter import messagebox

def calcular():
    try:
        peso = float(entry_peso.get())  # gramos
        costo_material_kg = float(entry_costo_material.get())
        horas = float(entry_horas.get())
        minutos = float(entry_minutos.get())
        consumo_w = float(entry_consumo.get())
        costo_kwh = float(entry_costo_kwh.get())
        margen = float(entry_margen.get())

        # Conversiones y cálculos
        peso_kg = peso / 1000
        tiempo_h = horas + (minutos / 60)

        costo_material = peso_kg * costo_material_kg
        costo_electricidad = (consumo_w / 1000) * tiempo_h * costo_kwh
        costo_total = costo_material + costo_electricidad
        precio_final = costo_total * (1 + margen / 100)

        # Mostrar resultados
        resultado.set(
            f"Costo material: ${costo_material:.2f}\n"
            f"Costo electricidad: ${costo_electricidad:.2f}\n"
            f"Costo total base: ${costo_total:.2f}\n"
            f"Precio final (con margen): ${precio_final:.2f}"
        )
    except ValueError:
        messagebox.showerror("Error", "Por favor ingresa solo números válidos.")

# --- Interfaz ---
root = tk.Tk()
root.title("Calculadora de Impresión 3D")
root.geometry("400x450")
root.resizable(False, False)

# Entradas
labels = [
    "Peso de la pieza (g):",
    "Costo material ($/kg):",
    "Horas de impresión:",
    "Minutos de impresión:",
    "Consumo máquina (W/h):",
    "Costo electricidad ($/kWh):",
    "Margen de ganancia (%):"
]

entries = []
for i, text in enumerate(labels):
    tk.Label(root, text=text, anchor="w").grid(row=i, column=0, padx=10, pady=5, sticky="w")
    e = tk.Entry(root, width=15)
    e.grid(row=i, column=1, padx=10, pady=5)
    entries.append(e)

entry_peso, entry_costo_material, entry_horas, entry_minutos, entry_consumo, entry_costo_kwh, entry_margen = entries

tk.Button(root, text="Calcular", command=calcular, bg="#4CAF50", fg="white", width=20).grid(row=8, column=0, columnspan=2, pady=15)

resultado = tk.StringVar()
tk.Label(root, textvariable=resultado, justify="left", font=("Arial", 10), fg="#333").grid(row=9, column=0, columnspan=2,
