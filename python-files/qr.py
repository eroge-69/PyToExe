# filepath: qr-excel-app/src/qr.py
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import qrcode
import os
from PIL import Image, ImageTk

def generar_qr_desde_excel():
    archivo = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
    if not archivo:
        return

    try:
        df = pd.read_excel(archivo)
        columnas = df.columns.tolist()
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo leer el archivo:\n{str(e)}")
        return

    def generar_codigos_qr(columna):
        carpeta_salida = filedialog.askdirectory(title="Selecciona carpeta de destino")
        if not carpeta_salida:
            return

        for i, valor in enumerate(df[columna]):
            if pd.notna(valor):
                img = qrcode.make(str(valor))
                img.save(os.path.join(carpeta_salida, f"qr_{i+1}.png"))

        messagebox.showinfo("Éxito", "Códigos QR generados exitosamente.")

    seleccion_ventana = tk.Toplevel()
    seleccion_ventana.title("Selecciona la columna")

    tk.Label(seleccion_ventana, text="Selecciona la columna para generar los QR:").pack()

    for col in columnas:
        tk.Button(seleccion_ventana, text=col, command=lambda c=col: [generar_codigos_qr(c), seleccion_ventana.destroy()]).pack(pady=2)

def main():
    ventana = tk.Tk()
    ventana.title("Generador de Códigos QR desde Excel")
    ventana.geometry("400x300")  # Aumenta el alto para el logo

    # Cargar y mostrar el logo
    logo_img = Image.open("logo.png")  # Cambia el nombre si es necesario
    logo_img = logo_img.resize((100, 120))  # Ajusta el tamaño si lo deseas
    logo_tk = ImageTk.PhotoImage(logo_img)
    logo_label = tk.Label(ventana, image=logo_tk)
    logo_label.image = logo_tk  # Evita que la imagen se elimine por el recolector de basura
    logo_label.pack(pady=10)

    tk.Label(ventana, text="Haz clic en el botón para cargar tu archivo Excel").pack(pady=10)
    tk.Button(ventana, text="Cargar archivo Excel", command=generar_qr_desde_excel).pack()

    ventana.mainloop()

if __name__ == "__main__":
    main()