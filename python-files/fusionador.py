import os
from tkinter import Tk, Button, Label, filedialog, messagebox
from PyPDF2 import PdfMerger

class FusionadorApp:
    def __init__(self, master):
        self.master = master
        master.title("Fusionador de PDFs")

        self.label = Label(master, text="Selecciona las carpetas con PDFs:")
        self.label.pack(pady=5)

        self.btn_folder1 = Button(master, text="Elegir Carpeta 1", command=lambda: self.elegir_carpeta(1))
        self.btn_folder1.pack(pady=2)

        self.btn_folder2 = Button(master, text="Elegir Carpeta 2", command=lambda: self.elegir_carpeta(2))
        self.btn_folder2.pack(pady=2)

        self.btn_folder3 = Button(master, text="Elegir Carpeta 3", command=lambda: self.elegir_carpeta(3))
        self.btn_folder3.pack(pady=2)

        self.label_output = Label(master, text="Selecciona la carpeta de salida:")
        self.label_output.pack(pady=5)

        self.btn_output = Button(master, text="Elegir Carpeta de Salida", command=self.elegir_carpeta_salida)
        self.btn_output.pack(pady=2)

        self.btn_fusionar = Button(master, text="Fusionar PDFs", command=self.fusionar)
        self.btn_fusionar.pack(pady=10)

        self.folders = {1: None, 2: None, 3: None}
        self.output_folder = None

    def elegir_carpeta(self, num):
        carpeta = filedialog.askdirectory()
        if carpeta:
            self.folders[num] = carpeta
            messagebox.showinfo("Carpeta seleccionada", f"Carpeta {num} seleccionada:\n{carpeta}")

    def elegir_carpeta_salida(self):
        carpeta = filedialog.askdirectory()
        if carpeta:
            self.output_folder = carpeta
            messagebox.showinfo("Carpeta de salida", f"Carpeta de salida seleccionada:\n{carpeta}")

    def fusionar(self):
        if None in self.folders.values():
            messagebox.showerror("Error", "Por favor selecciona las tres carpetas con PDFs.")
            return
        if not self.output_folder:
            messagebox.showerror("Error", "Por favor selecciona la carpeta de salida.")
            return

        archivos_por_nombre = {}

        # Recopilar archivos PDF de cada carpeta
        for carpeta in self.folders.values():
            for archivo in os.listdir(carpeta):
                if archivo.lower().endswith('.pdf'):
                    ruta_completa = os.path.join(carpeta, archivo)
                    if archivo not in archivos_por_nombre:
                        archivos_por_nombre[archivo] = []
                    archivos_por_nombre[archivo].append(ruta_completa)

        # Fusionar archivos con mismo nombre
        for nombre, rutas in archivos_por_nombre.items():
            if len(rutas) > 1:
                merger = PdfMerger()
                for pdf in rutas:
                    merger.append(pdf)
                salida = os.path.join(self.output_folder, nombre)
                merger.write(salida)
                merger.close()
            else:
                # Si solo hay un archivo con ese nombre, lo copia directamente
                import shutil
                shutil.copy2(rutas[0], os.path.join(self.output_folder, nombre))

        messagebox.showinfo("Éxito", "¡Archivos PDF fusionados correctamente!")

if __name__ == "__main__":
    root = Tk()
    app = FusionadorApp(root)
    root.mainloop()
