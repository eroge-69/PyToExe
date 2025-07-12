
import pandas as pd
from datetime import datetime
import os
import tkinter as tk
from tkinter import filedialog, messagebox

def calcular_dias_generales(df, fecha_inicio, fecha_termino):
    df = df.iloc[:, [3, 49, 50]].copy()  # D, AX, AY columnas
    df.columns = ['Nombre', 'Inicio', 'Termino']
    df['Inicio'] = pd.to_datetime(df['Inicio'], errors='coerce')
    df['Termino'] = pd.to_datetime(df['Termino'], errors='coerce')
    df['Termino'] = df['Termino'].fillna(fecha_termino)
    df['InicioEfectivo'] = df[['Inicio']].apply(lambda x: max(x[0], fecha_inicio), axis=1)
    df['TerminoEfectivo'] = df[['Termino']].apply(lambda x: min(x[0], fecha_termino), axis=1)
    df['DiasEfectivos'] = (df['TerminoEfectivo'] - df['InicioEfectivo']).dt.days + 1
    df['DiasEfectivos'] = df['DiasEfectivos'].apply(lambda x: x if x > 0 else 0)
    resumen = df.groupby('Nombre', as_index=False)['DiasEfectivos'].sum()
    return resumen

def main():
    root = tk.Tk()
    root.withdraw()
    archivo = filedialog.askopenfilename(
        title="Selecciona base de contratos",
        filetypes=[("Archivos Excel","*.xlsx *.xls")]
    )
    if not archivo:
        messagebox.showerror("Error","No seleccionaste un archivo.")
        return

    resp_ini = tk.simpledialog.askstring("Fecha inicio", "Formato YYYY-MM-DD", parent=root)
    resp_fin = tk.simpledialog.askstring("Fecha término", "Formato YYYY-MM-DD", parent=root)
    if not resp_ini or not resp_fin:
        messagebox.showerror("Error","Fechas no ingresadas.")
        return

    try:
        fi = datetime.strptime(resp_ini, "%Y-%m-%d")
        ft = datetime.strptime(resp_fin, "%Y-%m-%d")
    except:
        messagebox.showerror("Error","Formato de fecha incorrecto.")
        return

    df = pd.read_excel(archivo, sheet_name=0)
    resumen = calcular_dias_generales(df, fi, ft)

    carpeta = os.path.dirname(archivo)
    nombre_out = f"dias_efectivos_{fi.strftime('%Y%m%d')}_{ft.strftime('%Y%m%d')}.xlsx"
    ruta_out = os.path.join(carpeta, nombre_out)
    resumen.to_excel(ruta_out, index=False)

    os.startfile(ruta_out)
    messagebox.showinfo("Listo","Archivo generado:\n" + ruta_out)

if __name__ == "__main__":
    main()
