
import tkinter as tk
import time

# Configuración ventana
root = tk.Tk()
root.title("Reloj Digital")
root.geometry("400x150")
root.configure(bg="black")
root.resizable(False, False)

# Fuente y colores
font = ("Arial", 72, "bold")
color_num = "#FFB6C1"  # Rosa pastel

# Etiqueta para mostrar la hora
label = tk.Label(root, font=font, fg=color_num, bg="black")
label.pack(expand=True)

def actualizar_reloj():
    hora = time.strftime("%H:%M:%S")
    label.config(text=hora)
    label.after(1000, actualizar_reloj)

actualizar_reloj()
root.mainloop()
