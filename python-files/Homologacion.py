import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import os
from datetime import datetime

class HomologadorSAP:
    def __init__(self):
        self.archivo_sap = None
        self.archivo_maestro = os.path.join(os.path.dirname(__file__), "maestro.xlsx")
        self.df_sap = None
        self.df_maestro = None
        self.df_resultado = None
        self.df_no_homologadas = None

    def seleccionar_archivo_sap(self):
        """Permite al usuario seleccionar el archivo SAP (balance)."""
        root = tk.Tk()
        root.withdraw()

        messagebox.showinfo("Selección de archivo", "Selecciona el archivo SAP (balance).")
        self.archivo_sap = filedialog.askopenfilename(filetypes=[("Archivos Excel", "*.xlsx")])

        if not self.archivo_sap:
            messagebox.showerror("Error", "No seleccionaste el archivo SAP. Proceso cancelado.")
            return False
        return True

    def cargar_archivos(self):
        """Carga SAP y Maestro, forzando todas las columnas como texto."""
        try:
            # ✅ Leer todo como texto para evitar problemas de formato
            self.df_sap = pd.read_excel(self.archivo_sap, dtype=str)
            self.df_maestro = pd.read_excel(self.archivo_maestro, dtype=str)

            # Normalizar nombres de columnas
            self.df_sap.columns = self.df_sap.columns.str.strip()
            self.df_maestro.columns = self.df_maestro.columns.str.strip()

            print("✅ Archivos cargados correctamente.")
        except FileNotFoundError:
            messagebox.showerror("Error", f"No se encontró maestro.xlsx en:\n{os.path.dirname(__file__)}")
            raise
        except Exception as e:
            messagebox.showerror("Error", f"Hubo un problema al cargar los archivos:\n{e}")
            raise

    def homologar_cuentas(self):
        """Realiza la homologación de cuentas asegurando formatos."""

        if 'Cuentas' not in self.df_sap.columns or 'Balance' not in self.df_sap.columns:
            raise KeyError("❌ El archivo SAP debe contener las columnas 'Cuentas' y 'Balance'.")
        if 'COSI' not in self.df_maestro.columns or 'CMF' not in self.df_maestro.columns:
            raise KeyError("❌ El archivo maestro debe contener las columnas 'COSI' y 'CMF'.")

        # Normalizar valores (como texto y sin espacios)
        self.df_sap['Cuentas'] = self.df_sap['Cuentas'].astype(str).str.strip()
        self.df_maestro['COSI'] = self.df_maestro['COSI'].astype(str).str.strip()

        # Convertir Balance a numérico (aunque lo leímos como texto)
        self.df_sap['Balance'] = pd.to_numeric(self.df_sap['Balance'], errors='coerce').fillna(0)

        # Merge
        self.df_resultado = self.df_sap.merge(
            self.df_maestro[['COSI', 'CMF']],
            left_on='Cuentas',
            right_on='COSI',
            how='left'
        )

        self.df_resultado['Homologación CMF'] = self.df_resultado['CMF']
        print("🔄 Homologación completada.")

    def filtrar_no_homologadas(self):
        """Filtra las cuentas sin homologación y con balance distinto de 0."""
        self.df_no_homologadas = self.df_resultado[
            self.df_resultado['Homologación CMF'].isna() &
            (self.df_resultado['Balance'] != 0)
        ]

        print(f"⚠️ Se encontraron {len(self.df_no_homologadas)} cuentas sin homologación con Balance ≠ 0.")

    def guardar_archivos(self):
        """Guarda copia del SAP homologado y archivo de cuentas no homologadas con fecha."""

        carpeta_sap = os.path.dirname(self.archivo_sap)

        # ✅ Crear copia homologada sin sobrescribir el original
        nombre_base = os.path.splitext(os.path.basename(self.archivo_sap))[0]
        archivo_homologado = os.path.join(carpeta_sap, f"{nombre_base}_homologado.xlsx")
        self.df_resultado.to_excel(archivo_homologado, index=False)

        # ✅ Crear archivo de cuentas no homologadas con fecha
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        archivo_no_homologadas = os.path.join(carpeta_sap, f"cuentas_no_homologadas_{fecha_actual}.xlsx")
        self.df_no_homologadas.to_excel(archivo_no_homologadas, index=False)

        messagebox.showinfo(
            "Proceso finalizado",
            f"✅ ¡Proceso completado!\n\n"
            f"✔ Archivo homologado creado en:\n{archivo_homologado}\n\n"
            f"✔ Cuentas no homologadas creadas en:\n{archivo_no_homologadas}"
        )

def main():
    app = HomologadorSAP()

    if not app.seleccionar_archivo_sap():
        return

    try:
        app.cargar_archivos()
        app.homologar_cuentas()
        app.filtrar_no_homologadas()
        app.guardar_archivos()
    except Exception as e:
        messagebox.showerror("Error crítico", f"Ocurrió un problema:\n{e}")

if __name__ == "__main__":
    main()