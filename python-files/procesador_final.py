
# -*- coding: utf-8 -*-
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def procesar_excel():
    root = tk.Tk()
    root.wm_withdraw()
    
    # Configuración
    solo_empleados_1_4 = False
    
    try:
        # Seleccionar archivos
        archivos = filedialog.askopenfilenames(
            title="SELECCIONAR ARCHIVOS EXCEL",
            filetypes=[
                ("Archivos Excel", "*.xlsx *.xls"),
                ("Todos los archivos", "*.*")
            ]
        )
        
        if not archivos:
            messagebox.showinfo("Información", "No se seleccionaron archivos.")
            return
        
        datos = []
        
        for ruta_archivo in archivos:
            nombre_archivo = os.path.basename(ruta_archivo)
            print(f"Procesando: {nombre_archivo}")
            
            try:
                # Leer Excel
                xls = pd.ExcelFile(ruta_archivo)
                hojas = [h for h in xls.sheet_names if h.isdigit()]
                
                if solo_empleados_1_4:
                    hojas = [h for h in hojas if int(h) in (1, 2, 3, 4)]
                
                for hoja in hojas:
                    try:
                        # Leer datos de columna F (13-43)
                        df = xls.parse(
                            sheet_name=hoja,
                            header=None,
                            usecols=[5],  # Columna F
                            skiprows=12,
                            nrows=31
                        )
                        
                        if df.empty:
                            continue
                            
                        # Procesar valores
                        for valor in df.iloc[:, 0]:
                            if pd.notna(valor):
                                valor_str = str(valor).strip()
                                if valor_str:
                                    datos.append({
                                        'Archivo': nombre_archivo,
                                        'Empleado': f'Empleado {hoja}',
                                        'Locación': valor_str
                                    })
                                    
                    except Exception as e:
                        print(f"Error en hoja {hoja}: {e}")
                        continue
                        
            except Exception as e:
                print(f"Error con archivo {nombre_archivo}: {e}")
                continue
        
        # Generar resultado
        if datos:
            df_resultado = pd.DataFrame(datos)
            resumen = df_resultado.groupby(['Archivo', 'Empleado', 'Locación']).size().reset_index(name='Días trabajados')
            
            # Guardar
            archivo_salida = 'RESUMEN_LOCACIONES.csv'
            resumen.to_csv(archivo_salida, index=False, encoding='utf-8-sig')
            
            # Mostrar resultado
            mensaje = f'''
✅ PROCESAMIENTO COMPLETADO

📊 RESULTADOS:
• Archivos procesados: {len(archivos)}
• Registros encontrados: {len(resumen)}
• Archivo guardado: {archivo_salida}

📍 El archivo se guardó en la misma carpeta donde está este programa.
            '''
            messagebox.showinfo("ÉXITO", mensaje)
            
        else:
            messagebox.showinfo("SIN DATOS", 
                "No se encontraron locaciones en las celdas F13:F43 de las hojas procesadas.")
                
    except Exception as e:
        messagebox.showerror("ERROR", f"Error general: {str(e)}")
    
    finally:
        try:
            root.destroy()
        except:
            pass

if __name__ == "__main__":
    procesar_excel()
