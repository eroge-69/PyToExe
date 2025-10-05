import os
import tkinter as tk
from tkinter import messagebox

# Ruta de los logs
LOGS_PATH = r"\\Jumpserver\TC\IT ROOM\App´s\SecureCRT\Logs"
# Carpeta y archivo de salida
RESULT_FOLDER = "resultado_logs"
OUTPUT_FILE = os.path.join(RESULT_FOLDER, "resultado_logs.txt")

def buscar_logs(nombre_maquina, cantidad=1):
    logs = []
    try:
        for root, dirs, files in os.walk(LOGS_PATH):
            for file in sorted(files, reverse=True):
                if nombre_maquina in file:
                    logs.append(os.path.join(root, file))
                    if len(logs) == cantidad:
                        break
        return logs
    except Exception as e:
        messagebox.showerror("Error", str(e))
        return []

def guardar_resultado(logs):
    try:
        os.makedirs(RESULT_FOLDER, exist_ok=True)
        with open(OUTPUT_FILE, 'w') as f:
            for log in logs:
                f.write(log + '\n')
        # Mensaje eliminado
    except Exception as e:
        messagebox.showerror("Error al guardar", str(e))

def mostrar_contenido(text_widget):
    try:
        with open(OUTPUT_FILE, 'r') as f:
            contenido = f.read()
        text_widget.delete(1.0, tk.END)
        text_widget.insert(tk.END, contenido)
    except Exception as e:
        messagebox.showerror("Error al abrir el archivo", str(e))

def crear_interfaz():
    ventana = tk.Tk()
    ventana.title("LogVisor")
    ventana.geometry("800x600")

    ventana.rowconfigure(3, weight=1)
    ventana.columnconfigure(0, weight=1)

    tk.Label(ventana, text="Nombre de la máquina:").grid(row=0, column=0, pady=5, padx=10, sticky="w")
    entrada = tk.Entry(ventana, width=50)
    entrada.grid(row=1, column=0, pady=5, padx=10, sticky="we")

    text_area = tk.Text(ventana)
    text_area.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

    def accion_buscar_1():
        nombre = entrada.get()
        logs = buscar_logs(nombre, 1)
        guardar_resultado(logs)
        mostrar_contenido(text_area)

    def accion_buscar_5():
        nombre = entrada.get()
        logs = buscar_logs(nombre, 5)
        guardar_resultado(logs)
        mostrar_contenido(text_area)

    frame_botones = tk.Frame(ventana)
    frame_botones.grid(row=2, column=0, pady=5)

    tk.Button(frame_botones, text="Último log", command=accion_buscar_1).pack(side="left", padx=10)
    tk.Button(frame_botones, text="Últimos 5 logs", command=accion_buscar_5).pack(side="left", padx=10)

    ventana.mainloop()

crear_interfaz()