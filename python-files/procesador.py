import pandas as pd
import os
import re
from concurrent.futures import ProcessPoolExecutor
from functools import partial
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

# Funciones de procesamiento
def transformar_periodo_mmaa(valor):
    if isinstance(valor, str) and ' - ' in valor:
        parte = valor.split(' - ')[0].strip()
        mes = parte[:3]
        if mes == 'Set':
            mes = 'Sep'
        año = parte[-2:]
        return f"{mes}{año}"
    return None

def detectar_encabezado(df):
    for i in range(min(10, len(df))):
        fila = df.iloc[i]
        if 'Markets' in fila.values and 'Periods' in fila.values:
            return i
    return None

def detectar_fin_data(df):
    vacias = df.isnull().all(axis=1)
    consecutivas = vacias.rolling(2).sum()
    fin = consecutivas[consecutivas == 2].first_valid_index()
    return fin if fin else len(df)

def obtener_columnas_jerarquia(df):
    try:
        idx_ini = df.columns.get_loc('Periods') + 1
        idx_fin = df.columns.get_loc('Vtas Valor')
        if idx_ini < idx_fin:
            return df.columns[idx_ini:idx_fin]
    except:
        pass
    return []

def poblar_jerarquia(row, columnas):
    for col in reversed(columnas):
        if pd.notna(row[col]):
            return col
    return None

def procesar_hoja(ruta, hoja):
    df_raw = pd.read_excel(ruta, sheet_name=hoja, header=None, engine='openpyxl')
    idx = detectar_encabezado(df_raw)
    if idx is None:
        return None, hoja

    df_full = pd.read_excel(ruta, sheet_name=hoja, skiprows=idx, engine='openpyxl')
    fin_idx = detectar_fin_data(df_full)
    df = df_full.iloc[:fin_idx].copy()
    return df, hoja

def transformar_hoja(df, hoja):
    if 'Periods' in df.columns:
        df['Periodo_MMAA'] = df['Periods'].apply(transformar_periodo_mmaa)

    columnas_jerarquia = obtener_columnas_jerarquia(df)
    if len(columnas_jerarquia) > 0:
        df['Jerarquia'] = df.apply(lambda row: poblar_jerarquia(row, columnas_jerarquia), axis=1)
    else:
        df['Jerarquia'] = None

    df['Origen'] = hoja
    return df

# Interfaz gráfica
class ProcesadorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Procesador de Reportes Excel")
        self.root.geometry("600x400")
        self.root.configure(bg="#f0f4f7")

        self.input_folder = tk.StringVar()
        self.output_folder = tk.StringVar()

        self.crear_interfaz()

    def crear_interfaz(self):
        tk.Label(self.root, text="Carpeta de entrada:", bg="#f0f4f7", font=("Segoe UI", 10)).pack(pady=5)
        tk.Entry(self.root, textvariable=self.input_folder, width=60).pack()
        tk.Button(self.root, text="Seleccionar carpeta", command=self.seleccionar_entrada).pack(pady=5)

        tk.Label(self.root, text="Carpeta de salida:", bg="#f0f4f7", font=("Segoe UI", 10)).pack(pady=5)
        tk.Entry(self.root, textvariable=self.output_folder, width=60).pack()
        tk.Button(self.root, text="Seleccionar carpeta", command=self.seleccionar_salida).pack(pady=5)

        tk.Button(self.root, text="Procesar", command=self.procesar, bg="#4caf50", fg="white", font=("Segoe UI", 10, "bold")).pack(pady=15)

        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=10)

        self.mensaje = tk.Label(self.root, text="", bg="#f0f4f7", font=("Segoe UI", 10, "italic"))
        self.mensaje.pack(pady=10)

    def seleccionar_entrada(self):
        carpeta = filedialog.askdirectory()
        if carpeta:
            self.input_folder.set(carpeta)

    def seleccionar_salida(self):
        carpeta = filedialog.askdirectory()
        if carpeta:
            self.output_folder.set(carpeta)

    def procesar(self):
        entrada = self.input_folder.get()
        salida = self.output_folder.get()
        if not entrada or not salida:
            messagebox.showerror("Error", "Selecciona ambas carpetas.")
            return

        archivos = [f for f in os.listdir(entrada) if f.endswith('.xlsx')]
        grupos = {}
        for archivo in archivos:
            base = re.match(r"^(.*?)(?:\s\d+)?\.xlsx$", archivo)
            if base:
                nombre_base = base.group(1).strip()
                grupos.setdefault(nombre_base, []).append(archivo)

        total_grupos = len(grupos)
        self.progress["maximum"] = total_grupos
        self.progress["value"] = 0

        for nombre_base, archivos_grupo in grupos.items():
            dfs = []
            for archivo in archivos_grupo:
                ruta = os.path.join(entrada, archivo)
                xls = pd.ExcelFile(ruta, engine='openpyxl')
                hojas = [s for s in xls.sheet_names if s.lower() != 'index']

                resultados = []
                with ProcessPoolExecutor() as executor:
                    resultados = list(executor.map(partial(procesar_hoja, ruta), hojas))

                for df, hoja in resultados:
                    if df is not None:
                        df_transformado = transformar_hoja(df, hoja)
                        dfs.append(df_transformado)

            if dfs:
                df_final = pd.concat(dfs, ignore_index=True)
                columnas_relevantes = [col for col in df_final.columns if col != 'Origen']
                df_final = df_final[~(df_final[columnas_relevantes].isnull().all(axis=1) & df_final['Origen'].notnull())]

                salida_archivo = os.path.join(salida, f"{nombre_base}_Procesado.xlsx")
                df_final.to_excel(salida)