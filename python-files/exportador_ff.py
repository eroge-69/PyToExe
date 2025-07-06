
import os
import configparser
import tkinter as tk
from tkinter import messagebox, filedialog
import pandas as pd
from datetime import datetime
import openpyxl

CONFIG_FILE = "config.ini"

def cargar_config():
    config = configparser.ConfigParser()
    if not os.path.exists(CONFIG_FILE):
        config["config"] = {
            "input_folder": "D:\\descargas",
            "output_folder": "D:\\descargas",
            "output_filename": "FF_UnionCriterios_YYYYMMDD.xlsx"
        }
        with open(CONFIG_FILE, "w") as f:
            config.write(f)
    else:
        config.read(CONFIG_FILE)
    return config

def guardar_config(ruta_csv, ruta_salida, nombre_archivo):
    config = configparser.ConfigParser()
    config["config"] = {
        "input_folder": ruta_csv,
        "output_folder": ruta_salida,
        "output_filename": nombre_archivo
    }
    with open(CONFIG_FILE, "w") as f:
        config.write(f)

def encontrar_csv_reciente(carpeta):
    archivos = [f for f in os.listdir(carpeta) if f.lower().startswith("callout-log") and f.endswith(".csv")]
    if not archivos:
        return None
    archivos = sorted(archivos, key=lambda x: os.path.getmtime(os.path.join(carpeta, x)), reverse=True)
    return os.path.join(carpeta, archivos[0])

def ejecutar_exportacion():
    config = cargar_config()
    carpeta = config["config"]["input_folder"]
    salida = config["config"]["output_folder"]
    nombre = config["config"]["output_filename"]
    if "YYYYMMDD" in nombre:
        nombre = nombre.replace("YYYYMMDD", datetime.now().strftime("%Y%m%d"))
    ruta_csv = encontrar_csv_reciente(carpeta)
    if not ruta_csv:
        messagebox.showerror("Error", "No se encontró ningún archivo CSV válido.")
        return
    try:
        df = pd.read_csv(ruta_csv)
    except:
        messagebox.showerror("Error", "No se pudo leer el archivo CSV.")
        return
    try:
        df["PTO PASS USED"] = df["PTO PASS USED"].astype(str)
        df["REQUEST DATE"] = pd.to_datetime(df["REQUEST DATE"], errors='coerce')
        df["RECEIVED DATE"] = pd.to_datetime(df["RECEIVED DATE"], errors='coerce')
        df["FROM TIME"] = pd.to_datetime(df["FROM TIME"], errors='coerce').dt.time
        df["TO TIME"] = pd.to_datetime(df["TO TIME"], errors='coerce').dt.time
        df["RECEIVED TIME"] = pd.to_datetime(df["RECEIVED TIME"], errors='coerce').dt.time
        df["PTO AVAILABLE"] = pd.to_numeric(df["PTO AVAILABLE"].astype(str).str.replace(",", "."), errors="coerce")

        seleccion = []
        for idx, row in df.iterrows():
            if row["PTO PASS USED"].strip().lower() == "yes":
                seleccion.append(True)
                continue
            try:
                req_dt = datetime.combine(row["REQUEST DATE"].date(), row["FROM TIME"])
                rec_dt = datetime.combine(row["RECEIVED DATE"].date(), row["RECEIVED TIME"])
                if abs((rec_dt - req_dt).total_seconds()) < 14400:
                    seleccion.append(True)
                    continue
            except:
                pass
            try:
                ft = datetime.combine(datetime.today(), row["FROM TIME"])
                tt = datetime.combine(datetime.today(), row["TO TIME"])
                diff_hours = (tt - ft).total_seconds() / 3600
                if diff_hours > row["PTO AVAILABLE"]:
                    seleccion.append(True)
                    continue
            except:
                pass
            seleccion.append(False)
        df_filtrado = df[seleccion]
        if df_filtrado.empty:
            messagebox.showinfo("Aviso", "No hay filas que cumplan los criterios.")
            return
        os.makedirs(salida, exist_ok=True)
        ruta_final = os.path.join(salida, nombre)
        df_filtrado.to_excel(ruta_final, index=False)
        messagebox.showinfo("Éxito", f"Archivo exportado exitosamente en:
{ruta_final}")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error al procesar:
{str(e)}")

def ventana_opciones():
    def guardar():
        guardar_config(e1.get(), e2.get(), e3.get())
        top.destroy()

    config = cargar_config()
    top = tk.Toplevel(root)
    top.title("Opciones")
    tk.Label(top, text="Ruta carpeta CSV:").grid(row=0, column=0)
    tk.Label(top, text="Ruta salida:").grid(row=1, column=0)
    tk.Label(top, text="Nombre archivo:").grid(row=2, column=0)
    e1 = tk.Entry(top, width=50)
    e1.insert(0, config["config"]["input_folder"])
    e2 = tk.Entry(top, width=50)
    e2.insert(0, config["config"]["output_folder"])
    e3 = tk.Entry(top, width=50)
    e3.insert(0, config["config"]["output_filename"])
    e1.grid(row=0, column=1)
    e2.grid(row=1, column=1)
    e3.grid(row=2, column=1)
    tk.Button(top, text="Guardar", command=guardar).grid(row=3, column=0, columnspan=2)

root = tk.Tk()
root.title("Exportador FF")
tk.Button(root, text="Ejecutar", width=20, command=ejecutar_exportacion).pack(pady=10)
tk.Button(root, text="Opciones", width=20, command=ventana_opciones).pack(pady=10)
tk.Button(root, text="Salir", width=20, command=root.quit).pack(pady=10)
root.mainloop()
