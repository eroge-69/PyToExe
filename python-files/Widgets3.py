import tkinter as tk
from datetime import datetime

# Fechas objetivo
FECHA_ALGEBRA = datetime(2025, 8, 11, 8, 0, 0)
FECHA_ANALISIS = datetime(2025, 8, 14, 8, 0, 0)

def crear_widget(raiz, nombre, fecha_objetivo, posicion):
    ventana = tk.Toplevel(raiz)
    ventana.overrideredirect(True)
    ventana.wm_attributes("-topmost", True)
    ventana.wm_attributes("-toolwindow", True)  # Oculta de alt-tab y barra
    ventana.configure(bg="black")
    ventana.geometry(posicion)

    # Título visual
    titulo = tk.Label(ventana, text=nombre, font=("Consolas", 16, "bold"), fg="white", bg="black")
    titulo.pack()

    label = tk.Label(ventana, font=("Consolas", 22), fg="lime", bg="black")
    label.pack(padx=10, pady=5)

    def actualizar():
        ahora = datetime.now()
        restante = fecha_objetivo - ahora

        if restante.total_seconds() <= 0:
            label.config(text="¡Llegó el día!")
        else:
            dias = restante.days
            horas, resto = divmod(restante.seconds, 3600)
            minutos, segundos = divmod(resto, 60)
            texto = f"{dias}d {horas}h {minutos}m {segundos}s"
            label.config(text=texto)
            ventana.after(1000, actualizar)

    actualizar()
    return ventana

# Crear raíz oculta
root = tk.Tk()
root.withdraw()  # Oculta la ventana principal

# Crear widgets reales como ventanas flotantes
crear_widget(root, "Álgebra", FECHA_ALGEBRA, "+20+20")
crear_widget(root, "Análisis", FECHA_ANALISIS, "+20+130")

# Ejecutar
root.mainloop()
