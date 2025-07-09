import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from jinja2 import Environment, FileSystemLoader
import pdfkit
import os

# Configuración del ejecutable de wkhtmltopdf (ajústalo si es necesario)
#PDFKIT_CONFIG = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')

# Crear carpeta de salida si no existe
os.makedirs('output', exist_ok=True)

def generar_pdf(csv_path, titulo):
    df = pd.read_csv(csv_path)

    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('report_template.html')
    html = template.render(
        titulo=titulo,
        columnas=df.columns.tolist(),
        filas=df.values.tolist()
    )

    output_path = os.path.join('output', 'reporte.pdf')
    pdfkit.from_string(html, output_path)#, configuration=PDFKIT_CONFIG
    return output_path

def seleccionar_csv():
    filepath = filedialog.askopenfilename(filetypes=[('CSV files', '*.csv')])
    if filepath:
        entry_csv.delete(0, tk.END)
        entry_csv.insert(0, filepath)

def ejecutar():
    csv_file = entry_csv.get()
    titulo = entry_titulo.get()
    if not csv_file or not os.path.exists(csv_file):
        messagebox.showerror('Error', 'Selecciona un archivo CSV válido.')
        return
    if not titulo:
        titulo = 'Reporte generado'
    try:
        output = generar_pdf(csv_file, titulo)
        messagebox.showinfo('Éxito', f'PDF generado:\n{output}')
    except Exception as e:
        messagebox.showerror('Error', str(e))

# GUI
root = tk.Tk()
root.title('Generador de PDF desde CSV')
root.geometry('500x200')

tk.Label(root, text='Archivo CSV:').pack(pady=5)
entry_csv = tk.Entry(root, width=60)
entry_csv.pack()
tk.Button(root, text='Seleccionar CSV', command=seleccionar_csv).pack(pady=5)

tk.Label(root, text='Título del reporte:').pack(pady=5)
entry_titulo = tk.Entry(root, width=60)
entry_titulo.pack()

tk.Button(root, text='Generar PDF', command=ejecutar, bg='green', fg='white').pack(pady=15)

root.mainloop()
