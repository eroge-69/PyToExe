import json
import time
import re
import unicodedata
import os
from difflib import get_close_matches, SequenceMatcher
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tkinter import Tk, Button, Label, StringVar, OptionMenu
import threading

TOTAL_PREGUNTAS = 40

json_categoria_map = {
    "clase a - categoría i.json": "Categoría A-I",
    "clase a - categoría iia.json": "Categoría AII-A",
    "clase a - categoría_iib.json": "Categoría AII-B",
    "clase a - categoría_iiia.json": "Categoría AIII-A",
    "clase a - categoría_iiib.json": "Categoría AIII-B",
    "clase a - categoria_iiic.json": "Categoría AIII-C",
    "clase_b - categoría_iic.json": "Categoría BII-C",
    "clase_b_categoría_iia.json": "Categoría BII-A",
    "clase_b_categoría_iib.json": "Categoría BII-B"
}

json_folder_path = "./"
json_files = [f for f in os.listdir(json_folder_path) if f.lower() in json_categoria_map]


def normalizar(texto):
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("utf-8")


def limpiar_pregunta(texto):
    texto = str(texto).strip().lower()
    texto = normalizar(texto)
    texto = re.sub(r"_+", "___", texto)
    texto = re.sub(r"\s+", " ", texto)
    texto = texto.replace("\u00bf", "").replace(":", "").replace("\u201c", "\"").replace("\u201d", "\"")
    return texto


def coincide_opcion(resp, texto_opcion):
    def limpiar(texto):
        texto = texto.lower().strip()
        texto = normalizar(texto)
        texto = re.sub(r"^[a-d]\)", "", texto)
        texto = re.sub(r"[^a-z0-9 ]", "", texto)
        return texto.strip()

    r = limpiar(resp)
    o = limpiar(texto_opcion)
    ratio = SequenceMatcher(None, r, o).ratio()
    return ratio > 0.8


def ejecutar_simulacro(archivo_json):
    try:
        nombre_json = os.path.basename(archivo_json).lower()
        categoria_asociada = json_categoria_map.get(nombre_json)
        if not categoria_asociada:
            print("No se encontró una categoría para el JSON seleccionado.")
            return

        with open(archivo_json, "r", encoding="utf-8") as f:
            respuestas = json.load(f)

        respuestas_limpias = {limpiar_pregunta(k): v for k, v in respuestas.items()}

        def buscar_respuesta(pregunta_web):
            pregunta_web_limpia = limpiar_pregunta(pregunta_web)
            if pregunta_web_limpia in respuestas_limpias:
                return respuestas_limpias[pregunta_web_limpia]
            coincidencias = get_close_matches(pregunta_web_limpia, respuestas_limpias.keys(), n=1, cutoff=0.85)
            if coincidencias:
                print(f"Coincidencia aproximada encontrada: {coincidencias[0]}")
                return respuestas_limpias[coincidencias[0]]
            return None

        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-infobars")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")

        driver = webdriver.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        driver.get("https://sierdgtt.mtc.gob.pe/")
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "btn-primary")))

        botones = driver.find_elements(By.CLASS_NAME, "btn-primary")
        for boton in botones:
            if categoria_asociada in boton.text:
                boton.click()
                break

        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Comenzar') or contains(., 'Simulacro')]"))).click()
        time.sleep(5)

        contador_pregunta = 0
        while True:
            try:
                pregunta_element = driver.find_element(By.XPATH, "//div[contains(@class,'card-box') and not(ancestor::*[@style='display: none;'])]//p[@class='text-muted font-15 m-b-15']")
                pregunta_texto = pregunta_element.text.strip()
                print(f"Pregunta: {pregunta_texto}")

                respuesta_correcta = buscar_respuesta(pregunta_texto)
                respuesta_marcada = False

                if respuesta_correcta:
                    respuestas_esperadas = respuesta_correcta if isinstance(respuesta_correcta, list) else [respuesta_correcta]
                    print(f"Respuestas esperadas: {respuestas_esperadas}")

                    opciones = driver.find_elements(By.TAG_NAME, "label")
                    for opcion in opciones:
                        texto_visible = opcion.text.strip().lower()
                        for respuesta in respuestas_esperadas:
                            respuesta_limpia = respuesta.strip().lower()
                            if len(respuesta_limpia) == 2 and re.match(r"^[a-d]\)$", respuesta_limpia):
                                if texto_visible.startswith(respuesta_limpia):
                                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", opcion)
                                    time.sleep(0.3)
                                    try:
                                        opcion.click()
                                    except:
                                        driver.execute_script("arguments[0].click();", opcion)
                                    respuesta_marcada = True
                                    break
                                continue

                            match_letra = re.match(r"^([a-dA-D])\)", respuesta.strip())
                            letra_correcta = match_letra.group(1).lower() if match_letra else None

                            if letra_correcta:
                                if texto_visible.startswith(f"{letra_correcta})") and coincide_opcion(respuesta, texto_visible):
                                    driver.execute_script("arguments[0].scrollIntoView(true);", opcion)
                                    opcion.click()
                                    respuesta_marcada = True
                                    break
                        if respuesta_marcada:
                            break

                print("respuesta marcada")
                time.sleep(2)

                if respuesta_marcada:
                    contador_pregunta += 1
                    print(f"Pregunta #{contador_pregunta} completada")

                    try:
                        btn_final = driver.find_element(By.XPATH, "//button[contains(., 'Simulacro Completo')]")
                        if btn_final.is_displayed() and btn_final.is_enabled():
                            driver.execute_script("arguments[0].scrollIntoView(true);", btn_final)
                            btn_final.click()
                            break
                    except:
                        pass

                    try:
                        wait.until(EC.element_to_be_clickable((By.ID, "btnSiguientePregunta"))).click()
                        time.sleep(2)
                    except Exception as e:
                        print("No se encontró botón para continuar:", repr(e))
                        break
                else:
                    print("No se seleccionó ninguna opción, no se puede continuar.")
                    break

            except Exception as e:
                print("Examen terminado o error:", repr(e))
                break

        try:
            terminar_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Terminar Simulacro')]")))
            driver.execute_script("arguments[0].scrollIntoView(true);", terminar_btn)
            time.sleep(1)
            terminar_btn.click()
            print("Simulacro finalizado correctamente.")
        except Exception as e:
            print("No se pudo finalizar correctamente el simulacro:", repr(e))

        # input("Presiona ENTER para cerrar el navegador...")
        time.sleep(6)
        driver.quit()

    except Exception as e:
        print("Error en la ejecución del simulacro:", repr(e))
        try:
            driver.quit()
        except:
            pass


root = Tk()
root.title("Simulacro de Licencias")
root.attributes("-topmost", True)

Label(root, text="Selecciona un archivo JSON de preguntas").pack(pady=5)
selected_json = StringVar(value=json_files[0] if json_files else "")
OptionMenu(root, selected_json, *json_files).pack(pady=5)

Button(root, text="Iniciar Simulacro", command=lambda: threading.Thread(target=iniciar_simulacro).start()).pack(pady=5)
Button(root, text="Salir", command=root.destroy).pack(pady=10)


def iniciar_simulacro():
    archivo_json = os.path.join(json_folder_path, selected_json.get())
    ejecutar_simulacro(archivo_json)

root.mainloop()
