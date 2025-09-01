import os
import subprocess
import datetime
import tkinter as tk
from tkinter import messagebox

# Carpetas fijas (ajusta según tu PC)
carpeta1 = r"\\srv5\Maquinas\OLANET\G02-13 MITUTOYO CRYSTA APEX\NGVLEAN\RECTIFICADO\INFORMES"
carpeta2 = r"\\srv5\Maquinas\OLANET\G02-13 MITUTOYO CRYSTA APEX\NGVLEAN\DMP\INFORMES"

# Diccionarios para mapear nombre mostrado -> ruta completa
mapa_rutas_1 = {}
mapa_rutas_2 = {}

def buscar_archivos(event=None):
    termino = entrada_busqueda.get().lower()
    lista1.delete(0, tk.END)
    lista2.delete(0, tk.END)
    mapa_rutas_1.clear()
    mapa_rutas_2.clear()

    # Buscar en carpeta1
    encontrados1 = []
    if os.path.isdir(carpeta1):
        for root, _, archivos in os.walk(carpeta1):
            for archivo in archivos:
                if termino in archivo.lower():
                    ruta = os.path.join(root, archivo)
                    try:
                        fecha = os.path.getmtime(ruta)
                        encontrados1.append((archivo, ruta, fecha))
                    except:
                        continue
        # Ordenar por fecha descendente
        encontrados1.sort(key=lambda x: x[2], reverse=True)

    if encontrados1:
        for nombre, ruta, fecha in encontrados1:
            fecha_str = datetime.datetime.fromtimestamp(fecha).strftime("%Y-%m-%d %H:%M")
            texto_mostrar = f"{nombre} ({fecha_str})"
            lista1.insert(tk.END, texto_mostrar)
            mapa_rutas_1[texto_mostrar] = ruta
    else:
        lista1.insert(tk.END, "No se encontró ningún archivo en esta carpeta.")

    # Buscar en carpeta2
    encontrados2 = []
    if os.path.isdir(carpeta2):
        for root, _, archivos in os.walk(carpeta2):
            for archivo in archivos:
                if termino in archivo.lower():
                    ruta = os.path.join(root, archivo)
                    try:
                        fecha = os.path.getmtime(ruta)
                        encontrados2.append((archivo, ruta, fecha))
                    except:
                        continue
        # Ordenar por fecha descendente
        encontrados2.sort(key=lambda x: x[2], reverse=True)

    if encontrados2:
        for nombre, ruta, fecha in encontrados2:
            fecha_str = datetime.datetime.fromtimestamp(fecha).strftime("%Y-%m-%d %H:%M")
            texto_mostrar = f"{nombre} ({fecha_str})"
            lista2.insert(tk.END, texto_mostrar)
            mapa_rutas_2[texto_mostrar] = ruta
    else:
        lista2.insert(tk.END, "No se encontró ningún archivo en esta carpeta.")

def abrir_archivo(event, lista, mapa_rutas):
    seleccion = lista.curselection()
    if seleccion:
        nombre = lista.get(seleccion[0])
        if nombre.lower().startswith("no se encontró"):
            return
        ruta_archivo = mapa_rutas.get(nombre)
        if ruta_archivo:
            try:
                subprocess.Popen(['notepad.exe', ruta_archivo])
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir el archivo:\n{e}")

# Crear ventana principal
ventana = tk.Tk()
ventana.title("Buscador Informes NGV")

# Validación: solo números y hasta 6 dígitos
def validar_entrada(dato):
    return dato == "" or (dato.isdigit() and len(dato) <= 6)

vcmd = (ventana.register(validar_entrada), '%P')

# Entrada de búsqueda
tk.Label(ventana, text="Buscar por OF:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
entrada_busqueda = tk.Entry(ventana, validate="key", validatecommand=vcmd, width=10)
entrada_busqueda.grid(row=0, column=0, padx=5, pady=5)
entrada_busqueda.bind("<Return>", buscar_archivos)
tk.Label(ventana, text="Pulsar ENTER para buscar").grid(row=0, column=1, sticky="w", padx=5, pady=5)

# Resultados carpeta 1
tk.Label(ventana, text="Resultados en:\n RECTIFICADO").grid(row=1, column=0, padx=5)
lista1 = tk.Listbox(ventana, width=70, height=10)
lista1.grid(row=2, column=0, padx=5)
lista1.bind("<Double-Button-1>", lambda event: abrir_archivo(event, lista1, mapa_rutas_1))

# Resultados carpeta 2
tk.Label(ventana, text="Resultados en:\n DMP").grid(row=1, column=1, padx=5)
lista2 = tk.Listbox(ventana, width=70, height=10)
lista2.grid(row=2, column=1, padx=5)
lista2.bind("<Double-Button-1>", lambda event: abrir_archivo(event, lista2, mapa_rutas_2))

ventana.mainloop()
