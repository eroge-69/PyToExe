import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import time
import os
import requests
import shutil
import hashlib
import traceback
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def solicitar_codigo_2fa(callback):
    def abrir_dialogo():
        codigo = simpledialog.askstring("Autenticação 2FA", "Digite o código do Google Authenticator:")
        callback(codigo)
    janela.after(0, abrir_dialogo)

def executar_script():
    codigo_event = threading.Event()
    codigo_armazenado = {}

    def receber_codigo(codigo):
        codigo_armazenado['valor'] = codigo
        codigo_event.set()

    try:
        # Configurações principais
        URL = "https://nubank.weduka.com.br/LogDocument/Access"
        PASTA_DOWNLOAD = os.path.join(os.getcwd(), "downloads")
        os.makedirs(PASTA_DOWNLOAD, exist_ok=True)
        PROXY = "192.168.239.9:8080"
        ORIGINAL = r"C:\Users\marcelo.mechi\AppData\Local\Google\Chrome\User Data\Profile 8"
        DESTINO = r"C:\Selenium\ProfileClone"
        if not os.path.exists(DESTINO):
            shutil.copytree(ORIGINAL, DESTINO)

        options = webdriver.ChromeOptions()
        options.add_argument(f"user-data-dir={DESTINO}")
        options.add_argument("profile-directory=Default")
        options.add_argument(f"--proxy-server=http://{PROXY}")
        options.add_argument("--window-size=1920x1080")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--remote-debugging-port=9222")
        options.add_argument("--headless")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        wait = WebDriverWait(driver, 30)
        session = requests.Session()

        driver.get(URL)
        wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Ir para site de autenticação"))).click()
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Próximo')]"))).click()

        campo_codigo = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input#credentials\\.passcode")))
        solicitar_codigo_2fa(receber_codigo)
        codigo_event.wait()
        codigo_2fa = codigo_armazenado.get("valor")
        if not codigo_2fa:
            messagebox.showerror("Erro", "Código 2FA não informado.")
            driver.quit()
            botao_iniciar.config(state="normal")
            return

        campo_codigo.clear()
        for digito in codigo_2fa.strip():
            campo_codigo.send_keys(digito)
            time.sleep(0.1)
        campo_codigo.send_keys(Keys.TAB)

        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and contains(., 'Verificar')]"))).click()
        time.sleep(1.5)

        campo_senha = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']")))
        campo_senha.clear()
        campo_senha.send_keys("Nubank1204861")
        time.sleep(1)

        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Verificar')]"))).click()

        try:
            while True:
                botao_modal = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Registrar depois')]"))
                )
                driver.execute_script("arguments[0].click();", botao_modal)
                time.sleep(1)
        except:
            pass

        if "LogDocument/Access" not in driver.current_url:
            driver.get(URL)

        wait.until(EC.presence_of_element_located((By.ID, "ID_Document_Repository")))
        combo_element = driver.find_element(By.ID, "ID_Document_Repository")
        combo = Select(combo_element)
        opcoes = [
            (opt.get_attribute("value"), opt.text.strip().replace("/", "-").replace(" ", "_"))
            for opt in combo.options
            if opt.get_attribute("value") and opt.is_enabled() and opt.is_displayed()
        ]

        total = len(opcoes)
        progresso["maximum"] = total
        progresso["value"] = 0

        for i, (valor, texto) in enumerate(opcoes, start=1):
            try:
                combo = Select(driver.find_element(By.ID, "ID_Document_Repository"))
                driver.execute_script("arguments[0].scrollIntoView(true);", combo._el)
                combo.select_by_value(valor)

                botao_filtro = wait.until(EC.element_to_be_clickable((By.ID, "submitFilter")))
                driver.execute_script("arguments[0].click();", botao_filtro)

                usar_botao_padrao = False
                try:
                    link_element = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((
                            By.XPATH,
                            "//a[contains(@href, '/LogDocument/Access?export=True') and not(ancestor::div[contains(@class,'alert-warning')])]"
                        ))
                    )
                    href = link_element.get_attribute("href")
                    usar_botao_padrao = True
                except:
                    try:
                        alerta = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((
                                By.CSS_SELECTOR,
                                "div.alert.alert-warning a[href*='export=True']"
                            ))
                        )
                        href = alerta.get_attribute("href")
                    except:
                        continue

                full_url = urljoin(URL, href)
                cookies = {c['name']: c['value'] for c in driver.get_cookies()}
                proxies = {"http": f"http://{PROXY}", "https": f"http://{PROXY}"}
                response = session.get(full_url, cookies=cookies, proxies=proxies)

                if response.status_code == 200:
                    content_disp = response.headers.get("Content-Disposition", "")
                    ext = ".bin"
                    if "filename=" in content_disp:
                        original_name = content_disp.split("filename=")[1].strip().strip('"')
                        _, ext = os.path.splitext(original_name)

                    hash_base = f"{href}{texto}".encode("utf-8")
                    nome_hash = hashlib.sha1(hash_base).hexdigest()
                    filename = f"{nome_hash}{ext}"
                    caminho_arquivo = os.path.join(PASTA_DOWNLOAD, filename)

                    with open(caminho_arquivo, "wb") as f:
                        f.write(response.content)

                progresso["value"] = i
                texto_status.set(f"{i}/{total} processados")
                janela.update_idletasks()
                time.sleep(1.5)

                if usar_botao_padrao:
                    try:
                        botao_abrir_filtro = wait.until(
                            EC.element_to_be_clickable((By.CLASS_NAME, "wdk-filter-advanced-trigger"))
                        )
                        driver.execute_script("arguments[0].click();", botao_abrir_filtro)
                        time.sleep(1)
                    except:
                        pass

            except Exception as e:
                print(f"Erro ao processar item '{texto}': {e}")
                traceback.print_exc()
                continue

        messagebox.showinfo("Concluído", "Todos os documentos foram processados.")
    except Exception as e:
        traceback.print_exc()
        messagebox.showerror("Erro", str(e))
    finally:
        botao_iniciar.config(state="normal")
        driver.quit()

def iniciar_processo():
    botao_iniciar.config(state="disabled")
    progresso["value"] = 0
    texto_status.set("Iniciando processo...")
    threading.Thread(target=executar_script, daemon=True).start()

# === INTERFACE GRÁFICA ===
janela = tk.Tk()
janela.title("Automatizador Weduka")
janela.geometry("400x200")
janela.resizable(False, False)

tk.Label(janela, text="Clique em Iniciar para extrair os documentos.").pack(pady=10)
botao_iniciar = tk.Button(janela, text="Iniciar", command=iniciar_processo)
botao_iniciar.pack(pady=5)

progresso = ttk.Progressbar(janela, orient="horizontal", length=300, mode="determinate")
progresso.pack(pady=10)

texto_status = tk.StringVar()
tk.Label(janela, textvariable=texto_status).pack(pady=5)

janela.mainloop()
