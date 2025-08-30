import os
import random
import re
import string
import tempfile
import shutil
import time
import threading
import requests
import customtkinter as ctk
from tkinter import messagebox

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

# ===================== CONFIG =====================
DOMINIO = "@sapo.pt"
SENHA_FIXA = "Instaconta1@"
URL_INSTAGRAM = "https://www.instagram.com/"
EXT_CRX = "webrtc_control.crx"
EXT_CAP = "extension_cap"

# ===================== UTILS =====================
def normalize_str(s: str) -> str:
    import unicodedata
    nfkd = unicodedata.normalize("NFD", s)
    return re.sub(r"[^a-zA-Z]", "", nfkd).lower()

def random_letters(n=3):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(n))

def gerar_usuario(nome1, nome2):
    return f"{normalize_str(nome1)}{random_letters()}{normalize_str(nome2)}{random_letters()}"

def pegar_nome():
    try:
        r = requests.get("https://gerador-nomes.wolan.net/nomes/2", timeout=10)
        nomes = r.json()
        return nomes[0], nomes[1]
    except:
        return "ana", "silva"

def pegar_frase_aleatoria():
    try:
        r = requests.get("https://zenquotes.io/api/random", timeout=10)
        data = r.json()
        frase = f"{data[0]['q']} — {data[0]['a']}"
        return frase[:150]
    except:
        return "Vivendo um dia de cada vez."

def pegar_foto_pessoa():
    try:
        r = requests.get("https://randomuser.me/api/", timeout=10)
        data = r.json()
        return data["results"][0]["picture"]["large"]
    except:
        return "https://picsum.photos/600"

def js_click(driver, el):
    driver.execute_script("arguments[0].click();", el)

# ===================== SELENIUM =====================
def criar_chrome_com_extensoes(headless):
    temp_profile_dir = os.path.join(tempfile.gettempdir(), "chrome_profile_TEMP")
    if os.path.exists(temp_profile_dir):
        shutil.rmtree(temp_profile_dir)
    os.makedirs(temp_profile_dir, exist_ok=True)

    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f"--user-data-dir={temp_profile_dir}")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
    )

    if os.path.exists(EXT_CRX):
        chrome_options.add_extension(EXT_CRX)
    if os.path.exists(EXT_CAP):
        chrome_options.add_argument(f"--load-extension={os.path.abspath(EXT_CAP)}")

    driver = webdriver.Chrome(options=chrome_options)
    return driver, temp_profile_dir

# ===================== FLUXO IG =====================
def criar_conta(driver, usuario, email, nome_completo, log_callback, codigo_entry, btn_confirmar, confirm_event):
    try:
        driver.get(URL_INSTAGRAM)
        time.sleep(3)

        try:
            allow_btn = driver.find_element(By.XPATH, "//button[text()='Allow all cookies']")
            allow_btn.click()
            log_callback("🍪 Cookies aceitos")
        except:
            pass

        driver.get("https://www.instagram.com/accounts/emailsignup/")
        time.sleep(3)

        WebDriverWait(driver, 12).until(EC.presence_of_element_located((By.NAME, "emailOrPhone"))).send_keys(email)
        driver.find_element(By.NAME, "fullName").send_keys(nome_completo)
        driver.find_element(By.NAME, "username").send_keys(usuario)
        driver.find_element(By.NAME, "password").send_keys(SENHA_FIXA)
        log_callback("📝 Formulário preenchido.")

        driver.find_element(By.XPATH, "//button[contains(.,'Sign up')]").click()
        log_callback("✅ Enviado 'Sign up'.")

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//select[@title='Month:']"))
            )
        except:
            log_callback("❌ Erro: tela de data de nascimento não carregou.")
            return False

        Select(driver.find_element(By.XPATH, "//select[@title='Month:']")).select_by_value(str(random.randint(1, 12)))
        Select(driver.find_element(By.XPATH, "//select[@title='Day:']")).select_by_value(str(random.randint(1, 28)))
        Select(driver.find_element(By.XPATH, "//select[@title='Year:']")).select_by_value(str(random.randint(1970, 2005)))
        driver.find_element(By.XPATH, "//button[text()='Next']").click()
        log_callback("📅 Data de nascimento enviada.")

        # Verificar se apareceu o captcha
        try:
            body_text = driver.find_element(By.TAG_NAME, "body").text
            if "This helps us to combat harmful conduct, detect and prevent spam and maintain the integrity of our Products." in body_text:
                log_callback("⚠️ Captcha detectado! Por favor, resolva e pressione ENTER.")
                return False
        except:
            pass

        # Mostrar campo de código somente aqui
        codigo_entry.pack(pady=5)
        btn_confirmar.pack(pady=5)
        codigo_entry.configure(state="normal")
        btn_confirmar.configure(state="normal")
        log_callback(f"📨 Código enviado para {email}")

        confirm_event.wait()
        codigo = codigo_entry.get().replace(" ", "")
        confirm_event.clear()

        codigo_entry.delete(0, "end")
        codigo_entry.configure(state="disabled")
        btn_confirmar.configure(state="disabled")
        codigo_entry.pack_forget()
        btn_confirmar.pack_forget()

        code_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "email_confirmation_code"))
        )
        code_input.send_keys(codigo)
        time.sleep(1)
        code_input.send_keys(Keys.ENTER)
        log_callback("✅ Código inserido, aguardando confirmação...")

        time.sleep(20)

        suspensa = False
        try:
            body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
            if ("your account has been disabled" in body_text or 
                "we suspended your account" in body_text or 
                "sorry, something went wrong creating your account" in body_text):
                log_callback("❌ Conta não criada (erro ou suspensa).")
                suspensa = True
        except:
            pass

        conta_criada = False
        profile_url = f"https://www.instagram.com/{usuario}/"
        driver.get(profile_url)
        time.sleep(5)
        if "login" in driver.current_url.lower():
            log_callback("❌ Voltou para login → conta não criada.")
        else:
            body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
            sinais_nao_existe = [
                "página não disponível", "not available", "não foi possível encontrar",
                "sorry, this page isn't available", "something went wrong creating your account"
            ]
            if any(s in body_text for s in sinais_nao_existe) or suspensa:
                log_callback("❌ Conta não foi criada ou suspensa.")
            else:
                conta_criada = True
                log_callback("✅ Conta criada com sucesso!")

        if conta_criada:
            try:
                bio_texto = pegar_frase_aleatoria()
                foto_url = pegar_foto_pessoa()
                driver.get("https://www.instagram.com/accounts/edit/")
                time.sleep(3)

                try:
                    bio_field = WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.ID, "pepBio"))
                    )
                    bio_field.clear()
                    bio_field.send_keys(bio_texto)
                    save_btn = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
                    )
                    js_click(driver, save_btn)
                    log_callback("✍️ Bio alterada.")
                except:
                    log_callback("⚠️ Erro alterando bio.")

                img_bytes = requests.get(foto_url, timeout=15).content
                temp_img_path = os.path.join(tempfile.gettempdir(), f"pfp_{usuario}.jpg")
                with open(temp_img_path, "wb") as f:
                    f.write(img_bytes)

                try:
                    file_input = WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
                    )
                    file_input.send_keys(temp_img_path)
                    log_callback("🖼️ Foto de perfil alterada.")
                except:
                    log_callback("⚠️ Erro alterando foto de perfil.")

                with open("contas_criadas.txt", "a", encoding="utf-8") as f:
                    f.write(f"{usuario} | {email}\n")
                log_callback("💾 Conta salva em 'contas_criadas.txt'.")

                os.remove(temp_img_path)

            except Exception as e:
                log_callback(f"⚠️ Erro personalizando conta: {e}")

        return conta_criada
    except Exception as e:
        log_callback(f"⚠️ Erro: {e}")
        return False


# ===================== MAIN =====================
ctk.set_appearance_mode("dark")
root = ctk.CTk()
root.title("Criador de Contas Instagram")
root.geometry("850x700")

# Frame superior para inputs
frame_top = ctk.CTkFrame(root)
frame_top.pack(side="top", fill="x", pady=10)

ctk.CTkLabel(frame_top, text="Quantas contas deseja criar?").pack(pady=5)
entry_qtd = ctk.CTkEntry(frame_top, width=120)
entry_qtd.pack(pady=5)

var_headless = ctk.BooleanVar()
ctk.CTkCheckBox(frame_top, text="Rodar em modo headless", variable=var_headless).pack(pady=5)

btn_iniciar = ctk.CTkButton(frame_top, text="Iniciar Criação", command=iniciar_processo)
btn_iniciar.pack(pady=10)

lbl_status = ctk.CTkLabel(frame_top, text="Aguardando início...")
lbl_status.pack(pady=5)

# Campo de código logo abaixo
codigo_entry = ctk.CTkEntry(frame_top, placeholder_text="Digite o código do email", state="disabled", width=200)
btn_confirmar = ctk.CTkButton(frame_top, text="Confirmar Código", command=confirmar_codigo, state="disabled")

# Logs fixos no rodapé
frame_logs = ctk.CTkFrame(root)
frame_logs.pack(side="bottom", fill="both", expand=True, pady=10)

log_text = ctk.CTkTextbox(frame_logs, height=20, width=800)
log_text.pack(fill="both", expand=True, padx=10, pady=10)

confirm_event = threading.Event()

root.mainloop()
