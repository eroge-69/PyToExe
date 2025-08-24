import tkinter as tk
from tkinter import ttk
import psutil
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import time

# Precio estimado de la luz en €/kWh (puedes ajustarlo)
PRECIO_LUZ_ESTIMADO = 0.30  # €/kWh

# Función para obtener consumo aproximado del PC
def consumo_pc():
    cpu = psutil.cpu_percent()  # %
    ram = psutil.virtual_memory().percent  # %
    # Aproximación de consumo en W: CPU y RAM ponderados
    consumo = cpu * 0.5 + ram * 0.3
    return round(consumo, 2)

# Función para actualizar datos y gráfico
def actualizar():
    while True:
        consumo = consumo_pc()
        # Convertimos W a kWh por hora y multiplicamos por precio estimado
        coste = round(consumo / 1000 * PRECIO_LUZ_ESTIMADO, 4)
        
        precio_label.config(text=f"Precio estimado luz: {PRECIO_LUZ_ESTIMADO} €/kWh")
        consumo_label.config(text=f"Consumo PC: {consumo} W")
        coste_label.config(text=f"Coste aproximado por hora: {coste} €")
        
        # Actualizar gráfico
        ax.clear()
        ax.bar(["Consumo (W)", "Coste (€)"], [consumo, coste], color=['skyblue', 'orange'])
        canvas.draw()
        
        time.sleep(600)  # Actualizar cada 10 minutos (600 segundos)

# Configuración de ventana
root = tk.Tk()
root.title("Monitor Energía PC")
root.geometry("400x400")

precio_label = ttk.Label(root, text="Precio luz: -- €/kWh")
precio_label.pack(pady=5)

consumo_label = ttk.Label(root, text="Consumo PC: -- W")
consumo_label.pack(pady=5)

coste_label = ttk.Label(root, text="Coste aproximado por hora: -- €")
coste_label.pack(pady=5)

# Gráfico
fig, ax = plt.subplots(figsize=(4,3))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

# Hilo para actualizar datos sin bloquear la ventana
threading.Thread(target=actualizar, daemon=True).start()

root.mainloop()
