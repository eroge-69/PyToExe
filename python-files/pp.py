import requests
import subprocess
import os
import platform
import pkg_resources
import json
import re
import winreg
# Определим вспомогательные функции для различных платформ
def get_current_version_windows(app_name):
    """
    Чтение версии установленной программы из реестра Windows.
    Если приложение не зарегистрировано в реестре, возвращает None.
    """
    try:
        subkey = fr'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{app_name}'
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, subkey) as key:
            value, _ = winreg.QueryValueEx(key, 'DisplayVersion')
            return value
    except OSError:
        return None


def get_current_version_linux(app_name):
    """
    Определение версии установленного пакета на Linux с помощью dpkg/rpm.
    Возвращает None, если пакет не найден.
    """
    cmd = ['dpkg', '-l', app_name]
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
        lines = output.splitlines()
        for line in lines:
            parts = line.split()
            if len(parts) >= 3 and parts[1] == app_name:
                return parts[2]
    except subprocess.CalledProcessError:
        return None


def get_current_version_macos(app_name):
    """
    Определение версии приложения на macOS путем сканирования info.plist файлов.
    Работает только для приложений, упакованных стандартным способом.
    """
    cmd = ["mdfind", "-onlyin", "/", f"kMDItemCFBundleIdentifier=='com.{app_name}'"]
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
        path = output.strip()
        plist_file = os.path.join(path, "Contents", "Info.plist")
        data = subprocess.check_output(["plutil", "-convert", "json", "-o", "-", plist_file]).decode('utf-8')
        jdata = json.loads(data)
        return jdata.get("CFBundleShortVersionString")
    except Exception:
        return None


# Универсальная функция для проверки текущей версии
def get_current_version(app_name):
    os_type = platform.system()
    if os_type == "Windows":
        return get_current_version_windows(app_name)
    elif os_type == "Linux":
        return get_current_version_linux(app_name)
    elif os_type == "Darwin":  # macOS
        return get_current_version_macos(app_name)
    else:
        return None


# Список приложений и соответствующие им URL для скачивания
apps = [
    ("PDF24 Creator", "https://download.pdf24.org/pdf24-creator-installer.exe"),
    ("WinRAR", "https://www.win-rar.com/postdownload.html"),
    ("Bitrix24 Desktop", "https://repos.1c-bitrix.ru/b24/bitrix24_desktop_ru.exe"),
    ("VC++ Redistributable x64", "https://aka.ms/vs/17/release/vc_redist.x64.exe"),
    ("VC++ Redistributable x86", "https://aka.ms/vs/17/release/vc_redist.x86.exe")
]

# Функция для получения доступной версии (парсинг веб-страницы)
def fetch_available_version(url):
    try:
        response = requests.get(url)
        html = response.text
        # Здесь нужен уникальный шаблон для распознавания версии,
        # пока это условный пример
        match = re.search(r'version\s*(\d+\.\d+(?:\.\d+)?)', html)
        if match:
            return match.group(1)
        return None
    except Exception as e:
        print(f"Ошибка при определении версии: {e}")
        return None

# Основная функция для скачивания и установки
def download_and_install(url, app_name):
    """Загружает и устанавливает приложение"""
    filename = url.split("/")[-1]
    print(f"Скачиваю {app_name}...")
    response = requests.get(url, allow_redirects=True)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Файл {filename} сохранён.")
        
        # Запускаем установку
        print(f"Устанавливаем {app_name}...")
        result = subprocess.run([f"./{filename}", "/silent"], shell=True)
        if result.returncode == 0:
            print(f"{app_name} установлен успешно!")
        else:
            print(f"Ошибка при установке {app_name}.")
        
        # Очищаем временные файлы
        os.remove(filename)
    else:
        print(f"Ошибка при скачивании {app_name}, статус-код: {response.status_code}")

# Основной цикл обновления
for app_name, url in apps:
    current_version = get_current_version(app_name)
    available_version = fetch_available_version(url)
    
    if current_version is None or available_version is None:
        print(f"Не удалось определить текущую или доступную версию для {app_name}. Пропускаем.")
        continue
    
    if pkg_resources.parse_version(current_version) < pkg_resources.parse_version(available_version):
        print(f"Обнаружено новое обновление для {app_name} ({current_version} -> {available_version}). Начинаем обновление...")
        download_and_install(url, app_name)
    else:
        print(f"{app_name} уже актуален ({current_version}).")

print("Процесс обновления завершён.")