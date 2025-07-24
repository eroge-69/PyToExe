import os
import subprocess
import zipfile
import requests
import json
import uuid
import sys

# 🔐 Список ключей
VALID_KEYS = [
    "A1B2-C3D4-E5F6-G7H8", "I9J0-K1L2-M3N4-O5P6", "Q7R8-S9T0-U1V2-W3X4",
    "Y5Z6-A7B8-C9D0-E1F2", "G3H4-I5J6-K7L8-M9N0", "O1P2-Q3R4-S5T6-U7V8",
    "W9X0-Y1Z2-A3B4-C5D6", "E7F8-G9H0-I1J2-K3L4", "M5N6-O7P8-Q9R0-S1T2", "U3V4-W5X6-Y7Z8-A9B0"
]

# Пути к файлам
CLIENT_DIR = r"C:\litka client"
BETA_JAR = os.path.join(CLIENT_DIR, "LitkaClient.jar")
NATIVES_ZIP = os.path.join(CLIENT_DIR, "natives.zip")
NATIVES_DIR = os.path.join(CLIENT_DIR, "natives")
KEYS_DB = os.path.join(CLIENT_DIR, "keys_db.json")

# 🔗 Обновлённые прямые ссылки:
BETA_JAR_URL = "https://github.com/Ivban472/LitkaClient/releases/download/LitkaClient/LitkaClient.jar"
NATIVES_ZIP_URL = "https://github.com/Ivban472/LitkaClient/releases/download/LITKANATIVE/natives.zip"


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_banner():
    print("   ###       ##       ##     ###                                  ###       ##                         ##")
    print("   ##                ##      ##                                   ##                                  ##")
    print("   ##      ###      #####    ##  ##   ####              ####      ##      ###      ####    #####     #####")
    print("   ##       ##       ##      ## ##       ##            ##  ##     ##       ##     ##  ##   ##  ##     ##")
    print("   ##       ##       ##      ####     #####            ##         ##       ##     ######   ##  ##     ##")
    print("   ##       ##       ## ##   ## ##   ##  ##            ##  ##     ##       ##     ##       ##  ##     ## ##")
    print("  ####     ####       ###    ##  ##   #####             ####     ####     ####     #####   ##  ##      ###")
    print("=" * 100)

def validate_key(key):
    return key.strip().upper() in VALID_KEYS

def get_hwid():
    return str(uuid.getnode())

def load_keys_db():
    if not os.path.exists(KEYS_DB):
        return {}
    try:
        with open(KEYS_DB, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def save_keys_db(db):
    with open(KEYS_DB, "w") as f:
        json.dump(db, f)

def check_and_bind_key(key):
    db = load_keys_db()
    hwid = get_hwid()
    key = key.strip().upper()

    if key not in db:
        db[key] = hwid
        save_keys_db(db)
        return True

    if db[key] == hwid:
        return True
    else:
        print("❌ Этот ключ уже привязан к другому устройству.")
        return False

def ensure_client_dir():
    if not os.path.exists(CLIENT_DIR):
        os.makedirs(CLIENT_DIR)

def download_file(url, destination):
    try:
        print(f"⬇️ Скачивание: {url}")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(destination, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f"✅ Скачано: {destination}")
    except Exception as e:
        print(f"❌ Ошибка при скачивании {url}: {e}")
        sys.exit(1)

def extract_natives():
    if os.path.exists(NATIVES_ZIP):
        with zipfile.ZipFile(NATIVES_ZIP, 'r') as zip_ref:
            zip_ref.extractall(NATIVES_DIR)
        os.remove(NATIVES_ZIP)
        print(f"✅ Распаковано в: {NATIVES_DIR}")
    else:
        print("❌ Архив natives.zip не найден.")
        sys.exit(1)

def launch_client():
    if not os.path.exists(BETA_JAR):
        print(f"❌ Файл {BETA_JAR} не найден.")
        return
    if not os.path.exists(NATIVES_DIR):
        print(f"❌ Папка {NATIVES_DIR} не найдена.")
        return
    print(f"🚀 Запуск клиента...")
    try:
        subprocess.run([
            "java",
            f"-Djava.library.path={NATIVES_DIR}",
            "-jar",
            BETA_JAR
        ])
    except Exception as e:
        print(f"⚠️ Ошибка запуска: {e}")

def install_package(package_name):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"✅ Установлен пакет: {package_name}")
    except subprocess.CalledProcessError:
        print(f"❌ Не удалось установить пакет: {package_name}")

def check_and_install_requirements():
    required_packages = ["requests"]
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ Пакет {package} уже установлен.")
        except ImportError:
            print(f"❌ Пакет {package} не найден. Устанавливаю...")
            install_package(package)

def main():
    clear_screen()
    show_banner()

    ensure_client_dir()

    check_and_install_requirements()

    key = input("\n🔑 Введите ключ: ").strip().upper()

    if not validate_key(key):
        print("❌ Неверный ключ.")
        return

    if not check_and_bind_key(key):
        return

    download_file(BETA_JAR_URL, BETA_JAR)
    download_file(NATIVES_ZIP_URL, NATIVES_ZIP)
    extract_natives()
    launch_client()

if __name__ == "__main__":
    main()
