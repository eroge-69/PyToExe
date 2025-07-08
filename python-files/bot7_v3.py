import os
import time
import glob
import shutil
import tkinter as tk
from tkinter import simpledialog
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta

def obtener_rango_fechas():
    """Solicita al usuario un rango de fechas y devuelve una lista de fechas."""
    root = tk.Tk()
    root.withdraw()

    fecha_inicio_str = simpledialog.askstring("Input", "Ingrese la fecha de inicio (DD/MM/AAAA):")
    fecha_fin_str = simpledialog.askstring("Input", "Ingrese la fecha de fin (DD/MM/AAAA):")

    if not fecha_inicio_str or not fecha_fin_str:
        return []

    try:
        fecha_inicio = datetime.strptime(fecha_inicio_str, "%d/%m/%Y").date()
        fecha_fin = datetime.strptime(fecha_fin_str, "%d/%m/%Y").date()
    except ValueError:
        return []

    fechas = []
    fecha_actual = fecha_inicio
    while fecha_actual <= fecha_fin:
        fechas.append(fecha_actual.strftime("%d/%m/%Y"))
        fecha_actual += timedelta(days=1)
    return fechas

# ---------------------- SOLICITAR DATOS AL USUARIO ----------------------
root = tk.Tk()
root.withdraw()

usuario = simpledialog.askstring("Input", "Ingrese su usuario:")
if not usuario:
    print("No se ingresó un usuario válido.")
    exit()

password = simpledialog.askstring("Input", "Ingrese su contraseña:", show="*")
if not password:
    print("No se ingresó una contraseña válida.")
    exit()

fechas = obtener_rango_fechas()
if not fechas:
    print("No se ingresó un rango de fechas válido.")
    exit()

# ---------------------- CONFIGURAR SELENIUM ----------------------
carpeta_descargas = os.path.join(os.getcwd(), "Descargas_Temporales")
os.makedirs(carpeta_descargas, exist_ok=True)

opciones = webdriver.ChromeOptions()
#opciones.add_argument("--headless")
opciones.add_experimental_option("prefs", {
    "download.default_directory": carpeta_descargas,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
})

driver = webdriver.Chrome(options=opciones)
wait = WebDriverWait(driver, 10)

try:
    driver.get("https://appet2.dreamtec.pe/login")
    time.sleep(2)

    # Iniciar sesión
    driver.find_element(By.NAME, "usuario").send_keys(usuario)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.XPATH, "//button//span[contains(text(), 'Iniciar Sesión')]").click()
    time.sleep(2)

    # Ir a seguimiento
    driver.get("https://appet2.dreamtec.pe/seguimiento")
    time.sleep(2)

    for fecha_fija in fechas:
        # fecha_fija está en "DD/MM/YYYY"
        dd, mm, yyyy = fecha_fija.split('/')
        fecha_para_carpeta = f"{yyyy}{mm}{dd}" 
        carpeta_fecha = os.path.join(os.getcwd(), "Descargas", fecha_para_carpeta)
        os.makedirs(carpeta_fecha, exist_ok=True)

        # Abrir el menú de filtros y asegurarse de que se mantenga abierto
        filtro_boton = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@data-kt-menu-trigger='click' and contains(., 'Filtros')]") ))
        try:
            filtro_boton.click()
        except:
            driver.execute_script("arguments[0].click();", filtro_boton)
        time.sleep(2)

        # Aplicar filtro de fecha
        fecha_filtro = wait.until(EC.presence_of_element_located((By.ID, "filtro_fecha")))
        fecha_filtro.clear()
        fecha_filtro.send_keys(fecha_fija)
        time.sleep(1)

        # Seleccionar CEDI
        cedi_dropdown_element = wait.until(EC.presence_of_element_located((By.ID, "filtro_cedi")))
        cedi_dropdown = Select(cedi_dropdown_element)
        opciones_cedi = [option.get_attribute("value") for option in cedi_dropdown.options if option.get_attribute("value")]

        for cedi_value in opciones_cedi:
            try:
                cedi_dropdown.select_by_value(cedi_value)
            except:
                driver.execute_script("arguments[0].value=arguments[1];", cedi_dropdown_element, cedi_value)
            time.sleep(1)

            # Cerrar y volver a abrir menú de filtros para asegurar la selección
            try:
                filtro_boton.click()
            except:
                driver.execute_script("arguments[0].click();", filtro_boton)
            time.sleep(1)
            try:
                filtro_boton.click()
            except:
                driver.execute_script("arguments[0].click();", filtro_boton)
            time.sleep(1)

            boton_descargar = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[@onclick='descargarExcelDetalle()' and contains(., 'Excel Detalle')]")
            ))
            boton_descargar.click()

            # Esperar hasta que los archivos se descarguen
            tiempo_espera = 0
            archivos_previos = set(glob.glob(os.path.join(carpeta_descargas, "Detalle*.xlsx")))
            while tiempo_espera < 60:
                archivos_actuales = set(glob.glob(os.path.join(carpeta_descargas, "Detalle*.xlsx")))
                nuevos_archivos = archivos_actuales - archivos_previos
                if nuevos_archivos:
                    break
                time.sleep(1)
                tiempo_espera += 1

            # Mover archivos descargados a su carpeta correspondiente con nombres únicos
            archivos_movidos_csv = []
            archivos_movidos = []
            for i, archivo in enumerate(sorted(nuevos_archivos), start=1):
                df = pd.read_excel(archivo, engine='openpyxl')
                csv_temp = archivo.replace(".xlsx", ".csv")
                df.to_csv(csv_temp, sep = '|',index=False, encoding='utf-8-sig')
                dest_csv = os.path.join(carpeta_fecha, f"{cedi_value}_{i}_detalle.csv")
                shutil.move(csv_temp, dest_csv)
                archivos_movidos_csv.append(dest_csv)
                nuevo_nombre = os.path.join(carpeta_fecha, f"{cedi_value}_{i}_detalle.xlsx")
                shutil.move(archivo, nuevo_nombre)
                archivos_movidos.append(nuevo_nombre)

        # Combinar los archivos Excel en un solo archivo consolidado
        archivos_excel = glob.glob(os.path.join(carpeta_fecha, "*.xlsx"))
        dataframes = [pd.read_excel(archivo) for archivo in archivos_excel]
        if dataframes:
            df_consolidado = pd.concat(dataframes, ignore_index=True)
            df_consolidado.to_excel(os.path.join(carpeta_fecha, f"Consolidado_{fecha_fija.replace('/', '-')}.xlsx"), index=False)

finally:
    driver.quit()

# ------------------ORDENAR ARCHIVOS -----------------------------------
# Crear la carpeta base de consolidados
consolidados_dir = os.path.join(os.getcwd(), "Consolidados")
os.makedirs(consolidados_dir, exist_ok=True)

# 1. Mover todos los archivos consolidado*.xlsx
for filepath in glob.glob(os.path.join(os.getcwd(), "Descargas", "*", "Consolidado_*.xlsx")):
    shutil.move(filepath, consolidados_dir)

# 2. Eliminar los archivos detalle.xlsx en todas las subcarpetas
for detalle in glob.glob(os.path.join(os.getcwd(), "Descargas", "*", "*_detalle.xlsx")):
    os.remove(detalle)


# ---------------------- LIMPIAR CARPETA TEMPORAL ----------------------
if os.path.exists(carpeta_descargas):
    shutil.rmtree(carpeta_descargas)
    print("🗑️ Carpeta de descargas temporales eliminada.")
