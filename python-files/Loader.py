  #loader by zmei
    #loader by zmei
      #loader by zmei
        #loader by zmei161  
          #loader by zmei
            #loader by zmei
              #loader by zmei161
                #loader by zmei161
                #loader by zmei161
                #loader by zmei161
                #loader by zmei161
                
import ctypes
import functools
import hashlib
import inspect
import json
import os
import os.path
import subprocess
import sys
import time
import zipfile
  #loader by zmei
  #loader by zmei
  #loader by zmei
  #loader by zmei
import requests
from colorama import init, Fore
from tqdm import tqdm

ctypes.windll.kernel32.SetConsoleTitleA(b"Loader")
init(autoreset=True)
  #loader by zmei
logo = [

    " ██╗  ██╗ █████╗ ██████╗ ████████╗ █████╗    █████╗ ██╗     ██╗███████╗███╗  ██╗████████╗",
    " ██║ ██╔╝██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗  ██╔══██╗██║     ██║██╔════╝████╗ ██║╚══██╔══╝",
    " █████═╝ ██║  ██║██████╔╝   ██║   ███████║  ██║  ╚═╝██║     ██║█████╗  ██╔██╗██║   ██║",
    " ██╔═██╗ ██║  ██║██╔══██╗   ██║   ██╔══██║  ██║  ██╗██║     ██║██╔══╝  ██║╚████║   ██║",
    " ██║ ╚██╗╚█████╔╝██║  ██║   ██║   ██║  ██║  ╚█████╔╝███████╗██║███████╗██║ ╚███║   ██║",
    " ╚═╝  ╚═╝ ╚════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝   ╚════╝ ╚══════╝╚═╝╚══════╝╚═╝  ╚══╝   ╚═╝"
]
  #loader by zmei
username = "Free User"
till = "31.01.2999"
build = "Free 1.16.5"
last_update_date = "27.10.2024"
loader_ver = "1.2"
  #loader by zmei
  #loader by zmei
IGNORED_MODULES = []
class MODULEENTRY32(ctypes.Structure):
    _fields_ = [
        ("dwSize", ctypes.c_ulong),
        ("th32ModuleID", ctypes.c_ulong),
        ("th32ProcessID", ctypes.c_ulong),
        ("GlblcntUsage", ctypes.c_ulong),
        ("ProccntUsage", ctypes.c_ulong),
        ("modBaseAddr", ctypes.POINTER(ctypes.c_byte)),
        ("modBaseSize", ctypes.c_ulong),
        ("hModule", ctypes.c_void_p),
        ("szModule", ctypes.c_char * 256),
        ("szExePath", ctypes.c_char * 260)
    ]
  #loader by zmei
def check_for_injection():
    previous_modules = get_loaded_modules()
  #loader by zmei
    while True:
        current_modules = get_loaded_modules()
        new_modules = [module for module in current_modules if
                       module not in previous_modules and module not in IGNORED_MODULES]
        if new_modules:
            print(" [!] Обнаружена попытка инжекта кода")
            os.kill(os.getpid(), 9)
        previous_modules = current_modules
        time.sleep(0.001)
  #loader by zmei
def get_loaded_modules():
    module_list = []
    snapshot = ctypes.windll.kernel32.CreateToolhelp32Snapshot(0x00000008, 0)  # TH32CS_SNAPMODULE
    if snapshot == -1:
        return []
  #loader by zmei
    me32 = MODULEENTRY32()
    me32.dwSize = ctypes.sizeof(MODULEENTRY32)
  #loader by zmei
    ret = ctypes.windll.kernel32.Module32First(snapshot, ctypes.byref(me32))
    while ret != 0:
        if me32.szExePath.endswith(b".dll"):
            module_list.append(me32.szModule)
        ret = ctypes.windll.kernel32.Module32Next(snapshot, ctypes.byref(me32))
  #loader by zmei
    ctypes.windll.kernel32.CloseHandle(snapshot)
    return module_list
  #loader by zmei
def generate_hash(func):
    source_code = inspect.getsource(func)
    lines = source_code.splitlines()
    non_decorator_lines = [line for line in lines if not line.strip().startswith('@')]
    return hashlib.sha256('\n'.join(non_decorator_lines).encode("utf-8")).hexdigest()
  #loader by zmei
def verify_hash(original_hash):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_hash = generate_hash(func)
            if current_hash != original_hash:
                raise ValueError("Integrity check failed.")
            return func(*args, **kwargs)
  #loader by zmei
        return wrapper
  #loader by zmei
    return decorator
  #loader by zmei
def execute_command(command, ram):
    try:
        subprocess.run(command)
    except subprocess.CalledProcessError as e:
        print(f" [!] Процесс не запустился, ошибка: {e}")
  #loader by zmei
def download_and_extract(url: str, extract_dir: str):
    target_folder = os.path.join(extract_dir)
    response = requests.get(url, stream=True)
    filename = url.split('/')[-1].split(".zip")[0] + ".zip"
    target_path = os.path.join(target_folder, filename)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024
    t = tqdm(total=total_size, unit='B', unit_scale=True, desc=filename, leave=True)
    with open(target_path, 'wb') as file:
        for data in response.iter_content(block_size):
            t.update(len(data))
            file.write(data)
    t.close()
  #loader by zmei
    with zipfile.ZipFile(target_path, 'r') as zip_ref:
        zip_ref.extractall(target_folder)
        try:
            os.remove(target_path)
        except OSError:
            pass
  #loader by zmei
config_path = "C:\\KortaClient\\config\\memory_config.json"
def load_memory_config():
    if os.path.exists(config_path):
        with open(config_path, 'r') as file:
            config = json.load(file)
            return config.get("memory", "2048")
    return "2048"
  #loader by zmei
def save_memory_config(memory):
    config = {"memory": memory}
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, 'w') as file:
        json.dump(config, file)
  #loader by zmei
def ram_select():
    default_memory = load_memory_config()
    print(f" Текущее количество памяти: {default_memory} MB")
    user_input = input(" Введите количество памяти в MB (по умолчанию 2048): ").strip()
    if user_input.isdigit():
        memory = user_input
    else:
        memory = default_memory
    save_memory_config(memory)
    print(f" Выбранное количество памяти: {memory} MB")
    return memory
  #loader by zmei
  #loader by zmei
  #loader by zmei
def build_select():
    print(Fore.RED + "╔════════════════════════╗")
    print(Fore.RED + "║ Будет доступно позже...║")
    print(Fore.RED + "╚════════════════════════╝")
  #loader by zmei
# ФУНКЦИЯ СТАРТА КЛИЕНТА
def start():
    if not os.path.isdir("C:\\KortaClient"):
        os.mkdir("C:\\KortaClient")
        print(" [!] Stage 1: Created main directory")
        print(" [!] Stage 2: Downloading & extracting required files...")
        download_and_extract(
            "https://www.dropbox.com/scl/fi/39axga73lk4gzmo9g8ssm/client.zip?rlkey=dtr4wwmlv1w7e43ryv3dk9pyo&st=ak5do8re&dl=1",
            "C:\\KortaClient\\")
  #loader by zmei
    while True:
  #loader by zmei
        memory_input = input(Fore.LIGHTGREEN_EX +" [>] Введите кол-во оперативной памяти (В гб): ")
        print(f" Приятной Игры!")
  #loader by zmei
        try:
            memory = int(memory_input)
            print("[!] Stage 3: Launching client...")
            launch_command = [
                "C:\\KortaClient\\client\\jre-21.0.2\\bin\\java.exe",
                f"-Xmx{memory}G",
                "-Djava.library.path=C:\\KortaClient\\client\\natives",
                "-cp",
                "C:\\KortaClient\\client\\libraries\\*;C:\\KortaClient\\client\\Korta.jar",
                "net.minecraft.client.main.Main",
                "--username",
                "korta",
                "--width",
                "854",
                "--height",
                "480",
                "--version",
                "xyipenis141",
                "--gameDir",
                "C:\\KortaClient\\game",
                "--assetsDir",
                "C:\\KortaClient\\client\\assets",
                "--assetIndex",
                "1.16",
                "--accessToken",
                "0"
            ]
            execute_command(launch_command, ram=memory)
            break
        except ValueError:
            print(" [!] Введенное значение не является целым числом. Пожалуйста, попробуйте снова.")

            execute_command(launch_command, ram=memory)
            break
        except ValueError:
            print(" [!] Введенное значение не является целым числом. Пожалуйста, попробуйте снова.")
  #loader by zmei
def info():
    print("  Информация:")
    print("  ╔══════════════════════════════════════════╗")
    print( f"  ║  Версия клиента: {build}             ║ ")
    print( f"  ║  Имя пользователя: {username}             ║   ")
    print( f"  ║  Подписка до: {till}                 ║  ")
    print( f"  ║  Дата последнего обновления: {last_update_date}  ║   ")
    print( f"  ║  Версия лоадера: {loader_ver}                     ║ ")
    print( "  ╚══════════════════════════════════════════╝")
  #loader by zmei
def inform():
    print(Fore.LIGHTGREEN_EX + f"╔══════════════════════════════════════════╗")
    print(Fore.LIGHTGREEN_EX + f"║   Кодер & Создатель чита: zmei161        ║"),
    print(Fore.LIGHTGREEN_EX + "║   Zmei ушел в запой.                     ║")
    print(Fore.LIGHTGREEN_EX +"║   t.me/kortaclient                       ║")
    print(Fore.LIGHTGREEN_EX + f"╚══════════════════════════════════════════╝")
  #loader by zmei
def sosal():
    print(Fore.LIGHTWHITE_EX + " ╔══════════════════════════════════════════════╗")
    print(Fore.LIGHTWHITE_EX + " ║ Change Log:                                  ║")
    print(Fore.LIGHTWHITE_EX + " ║ 1.Изменен Дизайн.                            ║")
    print(Fore.LIGHTWHITE_EX + " ║ 2.Изменен Функционал                         ║")
    print(Fore.LIGHTWHITE_EX + " ║ 3.Изменен Код                                ║")
    print(Fore.LIGHTWHITE_EX + " ╚══════════════════════════════════════════════╝")
  #loader by zmei

def selector():
    while True:
        enter = input(Fore.CYAN + " [>] Выберите пункт: ")
        if enter == "1":
            start()
  #loader by zmei
        elif enter == "0":
            ram_select()
            print(" Изменения сохранены...\nПерезапустите лоадер...\nЛоадер будет закрыт через 5 секунд...")
            time.sleep(5)
            sys.exit()

        elif enter == "2":
            build_select()
  #loader by zmei
        elif enter == "3":
            info()
  #loader by zmei
        elif enter == "4":
            inform()
  #loader by zmei
        elif enter == "5":
            sosal()
  #loader by zmei
        else:
            print(" Неккоректный выбор!")
            print(f" [>] Выберите пункт: {enter}")
  #loader by zmei
  #loader by zmei
  #loader by zmei
  #loader by zmei
# ФУНКЦИЯ АВТОРИЗАЦИИ AKA ИНИЦИЛИЗАЦИИ
def auth():
    for line in logo:
        print(Fore.CYAN + line)
    print(" Загрузка...")
    time.sleep(3)
    main_func()
  #loader by zmei
# MAIN ФУНКЦИЯ
def main_func():
    print("\n [>] Добро пожаловать!")
    print(" ╔══════════════════════════════╗")
    print(" ║ [1] Запуск клиента           ║  ")
    print(" ║ [2] Выбор версии клиента     ║")
    print(" ║ [3] Информация               ║")
    print(" ║ [4] Разработчик              ║   ")
    print(" ║ [5] Change Log               ║   ")
    print(" ╚══════════════════════════════╝\n")
    selector()
  #loader by zmei
if __name__ == '__main__':
    auth()
    while True:
        pass
        
        #loader by zmei