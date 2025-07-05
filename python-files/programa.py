import tkinter as tk
from tkinter import filedialog, messagebox
import shutil
import os

def borrar_carpeta():
    carpeta = filedialog.askdirectory(title="Selecciona la carpeta a eliminar")
    if carpeta:
        if messagebox.askyesno("Confirmar eliminación", f"¿Estás seguro de eliminar:\n{carpeta}?"):
            try:
                shutil.rmtree(carpeta)
                messagebox.showinfo("Éxito", f"La carpeta\n{carpeta}\nha sido eliminada.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar la carpeta:\n{e}")

# Crear ventana
root = tk.Tk()
root.title("Eliminador de carpetas rápido")
root.geometry("400x150")

# Botón para seleccionar carpeta y borrar
btn_borrar = tk.Button(root, text="Seleccionar carpeta y borrar", command=borrar_carpeta, height=2, width=30)
btn_borrar.pack(pady=40)

root.mainloop()
