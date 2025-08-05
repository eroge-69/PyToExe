import os
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
import shutil

# Ruta compartida
RUTA_BASE = r"\\192.168.100.254\Testigo"

class DescargadorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Descargador de Archivos")
        self.root.geometry("500x400")

        self.frame_inicio = tk.Frame(root)
        self.frame_archivos = tk.Frame(root)

        self.subcarpeta_actual = ""

        self.crear_inicio()

    def crear_inicio(self):
        self.frame_inicio.pack(fill=tk.BOTH, expand=True)

        lbl = tk.Label(self.frame_inicio, text="Selecciona una carpeta:", font=("Arial", 16))
        lbl.pack(pady=30)

        btn_am = tk.Button(self.frame_inicio, text="AM", font=("Arial", 14), width=15, command=lambda: self.mostrar_archivos("am"))
        btn_am.pack(pady=10)

        btn_fm = tk.Button(self.frame_inicio, text="FM", font=("Arial", 14), width=15, command=lambda: self.mostrar_archivos("fm"))
        btn_fm.pack(pady=10)

    def mostrar_archivos(self, subcarpeta):
        self.subcarpeta_actual = subcarpeta
        ruta_completa = os.path.join(RUTA_BASE, subcarpeta)

        try:
            archivos = [os.path.join(ruta_completa, f) for f in os.listdir(ruta_completa) if os.path.isfile(os.path.join(ruta_completa, f))]
            archivos.sort(key=lambda f: os.path.getmtime(f), reverse=True)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo acceder a la carpeta: {e}")
            return

        self.frame_inicio.pack_forget()
        self.frame_archivos.pack(fill=tk.BOTH, expand=True)

        lbl = tk.Label(self.frame_archivos, text=f"Archivos en: {subcarpeta.upper()}", font=("Arial", 14))
        lbl.pack(pady=10)

        self.lista = tk.Listbox(self.frame_archivos, width=60, height=15)
        self.lista.pack(pady=10)
        for f in archivos:
            nombre = os.path.basename(f)
            fecha = datetime.fromtimestamp(os.path.getmtime(f)).strftime('%Y-%m-%d %H:%M')
            self.lista.insert(tk.END, f"{nombre} (modificado: {fecha})")

        btn_descargar = tk.Button(self.frame_archivos, text="Descargar archivo seleccionado", command=self.descargar_archivo)
        btn_descargar.pack(pady=5)

        btn_volver = tk.Button(self.frame_archivos, text="Volver", command=self.volver_inicio)
        btn_volver.pack(pady=5)

        self.archivos_actuales = archivos

    def descargar_archivo(self):
        seleccion = self.lista.curselection()
        if not seleccion:
            messagebox.showwarning("Atención", "Seleccioná un archivo primero.")
            return

        indice = seleccion[0]
        ruta_origen = self.archivos_actuales[indice]
        nombre_archivo = os.path.basename(ruta_origen)

        destino = filedialog.asksaveasfilename(initialfile=nombre_archivo, title="Guardar como")
        if destino:
            try:
                shutil.copy2(ruta_origen, destino)
                messagebox.showinfo("Éxito", f"Archivo guardado en:\n{destino}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo copiar el archivo: {e}")

    def volver_inicio(self):
        self.frame_archivos.pack_forget()
        self.lista.delete(0, tk.END)
        self.frame_inicio.pack(fill=tk.BOTH, expand=True)


if __name__ == "__main__":
    root = tk.Tk()
    app = DescargadorApp(root)
    root.mainloop()