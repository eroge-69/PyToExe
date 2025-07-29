import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import threading

def seleccionar_y_procesar_excel():
    def procesar():
        try:
            df = pd.read_excel(ruta_archivo)
            total_filas = len(df)
            progreso["maximum"] = total_filas

            for i in range(total_filas):
                df.iloc[i] = df.iloc[i].replace('❌', 'NO').replace('✔', 'SI')
                progreso["value"] = i + 1
                root.update_idletasks()

            carpeta = os.path.dirname(ruta_archivo)
            salida = os.path.join(carpeta, "NodeEstatus_Modificado.xlsx")
            df.to_excel(salida, index=False)

            messagebox.showinfo("¡Éxito!", f"Archivo guardado como:\n{salida}")
            root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error:\n{str(e)}")
            root.destroy()

    # Ventana oculta para seleccionar archivo
    selector = tk.Tk()
    selector.withdraw()
    ruta_archivo = filedialog.askopenfilename(
        title="Selecciona el archivo NodeEstatus.xlsx",
        filetypes=[("Archivos Excel", "*.xlsx")]
    )
    selector.destroy()

    if not ruta_archivo:
        messagebox.showwarning("Cancelado", "No seleccionaste ningún archivo.")
        return

    # Ventana principal con barra de progreso
    root = tk.Tk()
    root.title("Procesando archivo...")
    root.geometry("400x100")
    root.resizable(False, False)

    ttk.Label(root, text="Procesando, por favor espera...").pack(pady=10)
    progreso = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
    progreso.pack(pady=5)

    # Lanzar procesamiento en segundo plano
    hilo = threading.Thread(target=procesar)
    hilo.start()

    root.mainloop()

# Ejecutar la función
seleccionar_y_procesar_excel()
