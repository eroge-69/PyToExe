import tkinter as tk
from tkinter import filedialog, messagebox
import pdfplumber
from pypdf import PdfReader, PdfWriter
import os
import re
import configparser

CONFIG_FILE = "config.ini"

# ----- Funciones de configuración -----
def cargar_config():
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
    if 'RUTAS' not in config:
        config['RUTAS'] = {'pdf': '', 'carpeta': ''}
    return config

def guardar_config(pdf='', carpeta=''):
    config = cargar_config()
    if pdf:
        config['RUTAS']['pdf'] = pdf
    if carpeta:
        config['RUTAS']['carpeta'] = carpeta
    with open(CONFIG_FILE, 'w') as f:
        config.write(f)

# ----- Funciones de selección -----
def seleccionar_pdf():
    # Usar la ruta guardada como carpeta inicial, pero no mostrarla en el campo
    config = cargar_config()
    ruta_inicial = config['RUTAS'].get('pdf', '')

    ruta = filedialog.askopenfilename(initialdir=os.path.dirname(ruta_inicial) if ruta_inicial else "",
                                      filetypes=[("PDF Files", "*.pdf")])
    if ruta:
        entrada_pdf.delete(0, tk.END)
        entrada_pdf.insert(0, ruta)
        guardar_config(pdf=ruta)


def seleccionar_carpeta():
    # Usar la carpeta guardada como inicial, sin mostrarla en el campo
    config = cargar_config()
    carpeta_inicial = config['RUTAS'].get('carpeta', '')

    carpeta = filedialog.askdirectory(initialdir=carpeta_inicial if carpeta_inicial else "")
    if carpeta:
        entrada_carpeta.delete(0, tk.END)
        entrada_carpeta.insert(0, carpeta)
        guardar_config(carpeta=carpeta)


# ----- Función principal -----
def procesar_pdf():
    ruta_pdf = entrada_pdf.get()
    carpeta_salida = entrada_carpeta.get()
    nombre_carpeta = entrada_nombre_carpeta.get().strip()
    prefijo = entrada_prefijo.get().strip()

    if not ruta_pdf or not carpeta_salida:
        messagebox.showerror("Error", "Por favor selecciona el PDF y la carpeta de salida.")
        return

    try:
        # Crear carpeta de salida con el nombre ingresado
        if nombre_carpeta:
            carpeta_salida = os.path.join(carpeta_salida, nombre_carpeta)
        os.makedirs(carpeta_salida, exist_ok=True)

        reader = PdfReader(ruta_pdf)

        # Diccionario para agrupar páginas por nombre
        empleados = {}

        with pdfplumber.open(ruta_pdf) as pdf:
            for i, page in enumerate(pdf.pages):
                texto = page.extract_text()
                nombre = None

                if texto:
                    lineas = texto.splitlines()
                    for idx, linea in enumerate(lineas):
                        if "TRABAJADOR/A" in linea.upper():
                            if idx + 1 < len(lineas):
                                nombre = lineas[idx + 1].strip()
                                nombre = nombre.replace(",", "")
                                partes = nombre.split()

                                # Excluir "GRUPO", "LIMPIADORA", "OFICIAL", "AYUDANTE" y lo que venga detrás
                                for palabra in ["GRUPO", "LIMPIADORA", "OFICIAL", "AYUDANTE"]:
                                    if palabra in partes:
                                        idx_palabra = partes.index(palabra)
                                        partes = partes[:idx_palabra]

                                # Mantener primer espacio, resto con guiones bajos
                                if len(partes) > 1:
                                    nombre = partes[0] + " " + "_".join(partes[1:])
                                else:
                                    nombre = partes[0]

                                # Eliminar caracteres no válidos
                                nombre = re.sub(r'[\\/*?:"<>|]', "_", nombre)

                                # Limitar a 30 caracteres
                                nombre = nombre[:30]
                            break

                if not nombre:
                    nombre = f"Empleado_{i+1}"

                # Guardar página en el diccionario
                if nombre not in empleados:
                    empleados[nombre] = []
                empleados[nombre].append(reader.pages[i])

        # Ahora escribir un PDF por cada empleado con todas sus páginas
        for nombre, paginas in empleados.items():
            writer = PdfWriter()
            for p in paginas:
                writer.add_page(p)

            nombre_archivo = f"{prefijo}_{nombre}.pdf" if prefijo else f"{nombre}.pdf"
            ruta_salida_pdf = os.path.join(carpeta_salida, nombre_archivo)

            with open(ruta_salida_pdf, "wb") as f:
                writer.write(f)

        messagebox.showinfo("Proceso completo", f"Las nóminas se han separado correctamente en '{carpeta_salida}'.")

    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")

# ----- Interfaz Gráfica -----
ventana = tk.Tk()
ventana.title("Separador de Nóminas PDF")
ventana.geometry("800x650")

config = cargar_config()

tk.Label(ventana, text="Selecciona el PDF con las nóminas:").pack(pady=5)
entrada_pdf = tk.Entry(ventana, width=60)
entrada_pdf.pack()
entrada_pdf.insert(0, config['RUTAS'].get('pdf', ''))
tk.Button(ventana, text="Buscar PDF", command=seleccionar_pdf).pack(pady=5)

tk.Label(ventana, text="Selecciona la carpeta de salida:").pack(pady=5)
entrada_carpeta = tk.Entry(ventana, width=60)
entrada_carpeta.pack()
entrada_carpeta.insert(0, config['RUTAS'].get('carpeta', ''))
tk.Button(ventana, text="Buscar Carpeta", command=seleccionar_carpeta).pack(pady=5)

tk.Label(ventana, text="Nombre de la carpeta que se creará dentro:").pack(pady=5)
entrada_nombre_carpeta = tk.Entry(ventana, width=60)
entrada_nombre_carpeta.pack(pady=5)

tk.Label(ventana, text="Prefijo para los archivos (opcional):").pack(pady=5)
entrada_prefijo = tk.Entry(ventana, width=60)
entrada_prefijo.pack(pady=5)

tk.Button(ventana, text="Separar Nóminas", command=procesar_pdf, bg="green", fg="white", height=2).pack(pady=15)

ventana.mainloop()