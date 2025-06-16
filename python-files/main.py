import sys
import os

# ====== CEK PYTHON & INSTALL MODULE ======
try:
    import requests
    import chromedriver_autoinstaller
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
except ImportError:
    print("\033[93m[INFO]\033[0m Required modules not found. Installing dependencies...")
    os.system(f"{sys.executable} -m pip install --quiet requests selenium chromedriver-autoinstaller")
    print("\033[92m[INFO]\033[0m Modules installed. Please re-run the script.")
    sys.exit()

import time
import subprocess

# Hilangkan semua log DevTools/Chrome ke terminal
sys.stderr = open(os.devnull, 'w')

# Auto install Chrome driver
chromedriver_autoinstaller.install()

# === DISCORD SETUP ===
DISCORD_WEBHOOK_URL = input("Enter your Discord Webhook URL: ").strip()
if not DISCORD_WEBHOOK_URL.startswith("https://discord.com/api/webhooks/"):
    print("\033[91m[ERROR]\033[0m Invalid Discord webhook URL.")
    sys.exit(1)

def send_discord_message(message):
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": message})
    except:
        pass

def send_file_to_discord(file_path, caption):
    try:
        with open(file_path, 'rb') as f:
            files = {"file": (os.path.basename(file_path), f)}
            payload = {"content": caption}
            requests.post(DISCORD_WEBHOOK_URL, data=payload, files=files)
    except:
        pass

print("\033[92m  _   _ ________   __             _____ _____  ________          __")
print("\033[92m | \\ | |  ____\\ \\ / /    /\\      / ____|  __ \\|  ____\\ \\        / /")
print("\033[92m |  \\| | |__   \\ V /    /  \\    | |    | |__) | |__   \\ \\  /\\  / /")
print("\033[92m | . ` |  __|   > <    / /\\ \\   | |    |  _  /|  __|   \\ \\/  \\/ /")
print("\033[92m | |\\  | |____ / . \\  / ____ \\  | |____| | \\ \\| |____   \\  /\\  /")
print("\033[92m |_| \\_|______/_/ \\_\\/_/    \\_\\  \\_____|_|  \\_\\______|   \\/  \\/")
print("\033[92m==============================================================")
print("                  BSU CHECKER - Powered by NEXACREW")
print("==============================================================\033[0m")

# Chrome options
options = Options()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
options.add_argument("--log-level=3")
options.add_argument("--silent")
options.add_argument("--disable-logging")
options.add_argument('--headless=new')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# Service setup
service = Service()
service.creationflags = subprocess.CREATE_NO_WINDOW

# Prepare result files
open("live.txt", "w", encoding="utf-8").close()
open("dead.txt", "w", encoding="utf-8").close()
open("verifikasi_result.txt", "w", encoding="utf-8").close()

# Read input data
input_file = input("Enter the name of the input file (e.g. data.txt): ").strip()
if not os.path.exists(input_file):
    print(f"\033[91m[ERROR]\033[0m File '{input_file}' not found. Please make sure the file exists.")
    sys.exit(1)

with open(input_file, "r", encoding="utf-8") as f:
    lines = [line.strip() for line in f if line.strip()]
    rows = lines[1:]

print(f"Total data entries: {len(rows)}")

def input_js(driver, wait, selector, value):
    el = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
    driver.execute_script("arguments[0].scrollIntoView({behavior:'smooth',block:'center'});", el)
    time.sleep(0.1)
    driver.execute_script("""
        arguments[0].focus();
        arguments[0].value = arguments[1];
        arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
        arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
        arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
    """, el, value)
    time.sleep(0.1)

for idx, line in enumerate(rows, start=2):
    try:
        nik, nama, tgl_lahir, ibu, hp, email = [x.strip() for x in line.split("|")]

        if not nik.isdigit() or len(nik) != 16:
            print(f"[INVALID] Row {idx}: Invalid NIK ({nik}) – must be 16 digits.")
            with open("verifikasi_result.txt", "a", encoding="utf-8") as f:
                f.write(f"{nama} | {nik} | [Invalid NIK – must be 16 digits]\n")
            continue

        print(f"\n\033[92m[PROCESSING] Row {idx}: {nama}")

        service = Service(log_path='NUL')
        driver = webdriver.Chrome(service=service, options=options)
        wait = WebDriverWait(driver, 15)

        driver.get("https://bsu.bpjsketenagakerjaan.go.id")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(0.5)

        input_js(driver, wait, 'input[placeholder*="NIK"]', nik)
        input_js(driver, wait, 'input[placeholder*="Nama Lengkap"]', nama)
        input_js(driver, wait, 'input[placeholder*="Tanggal Lahir"]', tgl_lahir)
        input_js(driver, wait, 'input[placeholder*="Ibu Kandung"]', ibu)
        input_js(driver, wait, 'input[placeholder*="Ketik ulang Nama Ibu Kandung"]', ibu)
        input_js(driver, wait, 'input[placeholder*="Nomor Handphone Terkini"]', hp)
        input_js(driver, wait, 'input[placeholder*="Ketik ulang Nomor Handphone"]', hp)
        input_js(driver, wait, 'input[placeholder*="Email Terkini"]', email)
        input_js(driver, wait, 'input[placeholder*="Ketik ulang Email"]', email)

        print("\033[90mClicking 'Continue' button...\033[0m")
        submit_button = wait.until(EC.element_to_be_clickable((By.ID, "btn-cek-bsu")))
        time.sleep(0.2)
        submit_button.click()

        WebDriverWait(driver, 15).until(EC.url_contains("/cek-bsu-peserta"))
        print("\033[90mResult page loaded...\033[0m")

        time.sleep(0.5)
        hasil_text = driver.find_element(By.TAG_NAME, "body").text.lower().strip()
        hasil_text_clean = " ".join(hasil_text.split())
        reason = hasil_text_clean

        print(f"\033[90mDetected result text: {hasil_text_clean[:120]}...\033[0m")

        if "lolos verifikasi" in hasil_text_clean or "terdaftar sebagai calon penerima" in hasil_text_clean:
            status = f"\033[92m[LIVE]\033[0m {nama} ({nik})"
            print(status)
            send_discord_message(f"""**==========[ LIVE ]==========**
**Name**  : {nama}
**NIK**   : {nik}
**Reason**: {reason}
**==========[ NEXACREW ]==========**
""")
            with open("live.txt", "a", encoding="utf-8") as f:
                f.write(f"{nama} | {nik} | [{reason}]\n")

        elif "belum termasuk" in hasil_text_clean or "mohon maaf" in hasil_text_clean:
            status = f"\033[91m[DEAD]\033[0m {nama} ({nik})"
            print(status)
            with open("dead.txt", "a", encoding="utf-8") as f:
                f.write(f"{nama} | {nik} | [{reason}]\n")

        elif "dalam proses verifikasi" in hasil_text_clean or "cek secara berkala" in hasil_text_clean:
            print(f"\033[93m[VERIFICATION]\033[0m {nama} ({nik})")
            send_discord_message(f"""**==========[ VERIFIKASI ]==========**
**Name**  : {nama}
**NIK**   : {nik}
**Reason**: {reason}
**==========[ NEXACREW ]==========**
""")
            with open("verifikasi_result.txt", "a", encoding="utf-8") as f:
                f.write(f"{nama} | {nik} | [{reason}]\n")

        else:
            print("\033[90m[UNKNOWN] Unable to determine result.\033[0m")
            with open("verifikasi_result.txt", "a", encoding="utf-8") as f:
                f.write(f"{nama} | {nik} | [Unclear result: {reason}]\n")

        driver.quit()
        time.sleep(1)

    except Exception as e:
        short_error = str(e).split("\n")[0][:200]
        print(f"\033[90m[ERROR] Row {idx}: {short_error}\033[0m")
        send_discord_message(f"""**==========[ NEXACREW ERROR ]==========**
**Name**  : {nama}
**NIK**   : {nik}
**Error** : {short_error}
**==========[ NEXACREW ]==========**
""")
        try:
            driver.quit()
        except:
            pass
        continue

send_file_to_discord("live.txt", "[LIVE RESULTS]")
send_file_to_discord("dead.txt", "[DEAD RESULTS]")
send_file_to_discord("verifikasi_result.txt", "[VERIFICATION RESULTS]")

send_discord_message("[INFO] All data has been processed.")
print("Results saved and sent to Discord.")
