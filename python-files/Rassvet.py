import os
import sys
import time
import requests
import webbrowser
import math

def display_header():
    header = """
██████╗  █████╗ ███████╗███████╗██╗   ██╗███████╗████████╗
██╔══██╗██╔══██╗██╔════╝██╔════╝██║   ██║██╔════╝╚══██╔══╝
██████╔╝███████║███████╗███████╗██║   ██║█████╗     ██║   
██╔══██╗██╔══██║╚════██║╚════██║╚██╗ ██╔╝██╔══╝     ██║   
██║  ██║██║  ██║███████║███████║ ╚████╔╝ ███████╗   ██║   
╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝  ╚═══╝  ╚══════╝   ╚═╝   Client<3
    """
    print(header)

def download_with_progress(url, destination):
    try:
        session = requests.Session()
        response = session.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024 * 1024  # 1MB
        downloaded = 0
        
        if "confirm=" in response.url:
            confirm_key = response.url.split("confirm=")[1].split("&")[0]
            new_url = f"{url}&confirm={confirm_key}"
            response = session.get(new_url, stream=True)
            total_size = int(response.headers.get('content-length', 0))

        with open(destination, 'wb') as f:
            start_time = time.time()
            for chunk in response.iter_content(block_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    # Расчет прогресса
                    percent = downloaded / total_size * 100
                    speed = downloaded / (time.time() - start_time) / (1024 * 1024)  # MB/s
                    eta = (total_size - downloaded) / (speed * 1024 * 1024) if speed > 0 else 0
                    
                    # Рисуем прогресс-бар
                    bar_length = 50
                    filled_length = int(bar_length * downloaded // total_size)
                    bar = '█' * filled_length + '-' * (bar_length - filled_length)
                    
                    # Выводим информацию
                    sys.stdout.write(
                        f"\r[{bar}] {percent:.1f}% "
                        f"| {downloaded/(1024*1024):.1f}MB/{total_size/(1024*1024):.1f}MB "
                        f"| {speed:.2f}MB/s | ETA: {math.ceil(eta)}s "
                    )
                    sys.stdout.flush()
        
        print("\n[УСПЕХ] Файл успешно скачан!")
        return True
    except Exception as e:
        print(f"\n[ОШИБКА] При скачивании: {e}")
        return False

def get_download_path():
    if os.name == 'posix':
        return "/tmp/" if os.access("/tmp/", os.W_OK) else os.path.expanduser("~/Downloads/")
    else:
        return os.path.expanduser("~\\Downloads\\")

def show_guide():
    guide = """
=== ГАЙД ПО УСТАНОВКЕ ===
1. Скачайте архив с клиентом (кнопка "1")
2. Распакуйте ZIP-архив в любое удобное место
3. Переместите папку с клиентом в папку 'Versions' в Legacy Launcher
4. Запустите Legacy Launcher и выберите ваш клиент

Открыть ссылку на Legacy Launcher в браузере? (Y/N)
"""
    print(guide)
    choice = input().lower()
    if choice == 'y':
        try:
            webbrowser.get('chrome').open_new_tab('https://llaun.ch/ru')
        except:
            webbrowser.open_new_tab('https://llaun.ch/ru')

def main():
    display_header()
    
    download_dir = get_download_path()
    os.makedirs(download_dir, exist_ok=True)
    
    while True:
        print("\n=== МЕНЮ ===")
        print("1. Скачать клиент")
        print("2. Гайд по установке")
        print("0. Выход с позором")
        
        choice = input("Ваш выбор: ")
        
        if choice == '1':
            file_url = "https://drive.google.com/uc?export=download&id=1RQFnwCn0bkibrYYUqcYLICBHvChOfMvu"
            zip_filename = os.path.join(download_dir, "client_files.zip")
            
            print(f"Файл будет сохранён в: {zip_filename}")
            
            if download_with_progress(file_url, zip_filename):
                print("Загрузка завершена! Программа закроется через 5 секунд...")
                time.sleep(5)
                sys.exit(0)
        elif choice == '2':
            show_guide()
        elif choice == '0':
            print("Выход из программы...")
            time.sleep(1)
            sys.exit(0)
        else:
            print("Неверный ввод. Попробуйте снова.")

if __name__ == "__main__":
    main()