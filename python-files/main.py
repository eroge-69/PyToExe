import sys
import time
import subprocess
import os
import requests
import zipfile
import hashlib
import inspect
import functools
from tqdm import tqdm
from time import sleep

# ======================== Настройки ========================
username = "test"
build = "Alpha 1.16.5"
loader_version = "1.0.3"
cheat_version = "1.5.0"

def getchecksum():
    md5_hash = hashlib.md5()
    file = open(''.join(sys.argv), "rb")
    md5_hash.update(file.read())
    digest = md5_hash.hexdigest()
    return digest

# ======================== Авторизация ========================
def auth():
    print("██╗░░░██╗████████╗██╗  ████████╗██╗██████╗░███████╗██╗░░██╗░██████╗")
    print("╚██╗░██╔╝╚══██╔══╝╚═╝  ╚══██╔══╝██║██╔══██╗██╔════╝╚██╗██╔╝██╔════╝")
    print("░╚████╔╝░░░░██║░░░░░░  ░░░██║░░░██║██║░░██║█████╗░░░╚███╔╝░╚█████╗░")
    print("░░╚██╔╝░░░░░██║░░░░░░  ░░░██║░░░██║██║░░██║██╔══╝░░░██╔██╗░░╚═══██╗")
    print("░░░██║░░░░░░██║░░░██╗  ░░░██║░░░██║██████╔╝███████╗██╔╝╚██╗██████╔╝")
    print("░░░╚═╝░░░░░░╚═╝░░░╚═╝  ░░░╚═╝░░░╚═╝╚═════╝░╚══════╝╚═╝░░╚═╝╚═════╝░")
    print("Лоадер сделан Tidexs, YT: Tidexs")
    sleep(2)

# ======================== Загрузка клиента ========================
def download_and_extract(url: str, extract_dir: str):
    target_folder = os.path.join(extract_dir)
    filename = url.split('/')[-1].split(".zip")[0] + ".zip"
    target_path = os.path.join(target_folder, filename)

    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    print("[Загрузка] Начинается загрузка клиента...")
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024
    t = tqdm(total=total_size, unit='B', unit_scale=True, desc=filename)

    with open(target_path, 'wb') as file:
        for data in response.iter_content(block_size):
            t.update(len(data))
            file.write(data)
    t.close()

    print("[Распаковка] Извлечение клиента...")
    with zipfile.ZipFile(target_path, mode='r') as zip_ref:
        zip_ref.extractall(target_folder)

    try:
        os.remove(target_path)
    except OSError:
        pass

# ======================== Запуск клиента ========================
def run_cheat():
    print("\n[Чит] Подготовка к запуску...")

    client_path = "C:\\scratchclient"
    if not os.path.isdir(client_path):
        os.mkdir(client_path)

    download_and_extract(
        url="https://www.dropbox.com/scl/fi/y1rvcgyaqnm9kizcpl5yj/client.zip?rlkey=2txjk1rhoif86mriynvhr7i9y&st=dnk5y405&dl=1",
        extract_dir=client_path
    )

    while True:
        memory_input = input("Введите объём оперативной памяти (в гигабайтах): ")
        try:
            memory = int(memory_input)
            break
        except ValueError:
            print("Ошибка: введите корректное число.")

    local_java = os.path.join(client_path, "Client\\jre-21.0.2\\bin\\java.exe")
    java_exe = local_java if os.path.exists(local_java) else "java"
    if java_exe == local_java:
        print("[Java] Используется встроенная Java")
    else:
        print("[Java] Встроенная Java не найдена, используется системная")

    print("[Запуск] Запускаю клиент...\n")

    launch_command = [
        java_exe,
        f"-Xmx{memory}G",
        f"-Djava.library.path={client_path}\\Client\\natives",
        "-cp",
        f"{client_path}\\Client\\libraries;{client_path}\\Client\\client.jar",
        "net.minecraft.client.main.Main",
        "--username", username,
        "--width", "854",
        "--height", "480",
        "--version", "1.16.5",
        "--gameDir", f"{client_path}\\game",
        "--assetsDir", f"{client_path}\\Client\\assets",
        "--assetIndex", "1.16",
        "--accessToken", "0"
    ]

    try:
        subprocess.run(launch_command)
    except subprocess.CalledProcessError as e:
        print(f"[Ошибка запуска]: {e}")
    except FileNotFoundError:
        print("[Ошибка]: Java не найдена.")

# ======================== Меню ========================
def menu():
    global username
    while True:
        print("\n=== Главное меню ===")
        print("1. Изменить ник")
        print("2. Показать версию лоадера")
        print("3. Показать версию чита")
        print("4. Запустить чит")
        print("5. Выход")

        choice = input("Выберите пункт (1-5): ")

        if choice == '1':
            new_nick = input("Введите новый ник: ")
            if new_nick.strip():
                username = new_nick.strip()
                print(f"Ник изменён на: {username}")
            else:
                print("Ник не может быть пустым.")
        elif choice == '2':
            print(f"Версия лоадера: {loader_version}")
        elif choice == '3':
            print(f"Версия чита: {cheat_version}")
        elif choice == '4':
            run_cheat()
        elif choice == '5':
            print("Выход из программы...")
            break
        else:
            print("Неверный выбор. Попробуйте снова.")

# ======================== Запуск ========================
if __name__ == "__main__":
    auth()
    menu()
