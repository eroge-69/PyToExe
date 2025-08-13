import os
import socket
import threading
import time
from datetime import datetime
import zipfile
import io

# Конфигурация
BUFFER_SIZE = 65536
SEPARATOR = "<SEPARATOR>"
TIMEOUT = 30

class FileExchange:
    def __init__(self):
        self.current_dir = os.getcwd()
        self.selected_path = None
        self.running = True
    
    def clear_screen(self):
        """Очистка экрана с учетом ОС"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def get_local_ip(self):
        """Получение локального IP адреса"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except:
            return "127.0.0.1"
    
    def human_readable_size(self, size):
        """Форматирование размера файла"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"
    
    def display_files(self):
        """Отображение файлов в текущей директории"""
        self.clear_screen()
        print(f"\nТекущая папка: {self.current_dir}\n")
        print(f"{'№':<4} {'Тип':<5} {'Имя':<40} {'Размер':>15} {'Дата изменения':>20}")
        print("-"*90)
        
        items = []
        # Добавляем родительскую директорию
        if os.path.dirname(self.current_dir) != self.current_dir:
            items.append(("..", "DIR", "UP-DIR", "", ""))
        
        # Получаем список файлов и папок
        for item in os.listdir(self.current_dir):
            full_path = os.path.join(self.current_dir, item)
            if os.path.isdir(full_path):
                items.append((item, "DIR", "Папка", "", ""))
            else:
                size = os.path.getsize(full_path)
                mtime = datetime.fromtimestamp(os.path.getmtime(full_path)).strftime('%Y-%m-%d %H:%M')
                items.append((item, "FILE", "Файл", self.human_readable_size(size), mtime))
        
        # Выводим список с нумерацией
        for idx, (name, typ, desc, size, mtime) in enumerate(items, 1):
            print(f"{idx:<4} {typ:<5} {name[:38]:<40} {size:>15} {mtime:>20}")
        
        print("-"*90)
        return items
    
    def navigate_files(self):
        """Навигация по файловой системе"""
        while True:
            items = self.display_files()
            if self.selected_path:
                print(f"\nВыбрано: {self.selected_path}")
            
            print("\nКоманды:")
            print("[1-{0}] Выбрать файл/папку | [s] Выбрать для отправки".format(len(items)))
            print("[b] Назад в меню | [q] Выход")
            
            choice = input("Ваш выбор: ").lower()
            
            if choice == 'q':
                return "exit"
            elif choice == 'b':
                return "back"
            elif choice == 's':
                if self.selected_path:
                    if os.path.isdir(self.selected_path):
                        confirm = input(f"Отправить всю папку {os.path.basename(self.selected_path)}? (y/n): ").lower()
                        if confirm == 'y':
                            return self.selected_path
                    else:
                        return self.selected_path
                else:
                    print("Сначала выберите файл или папку!")
                    time.sleep(1)
            elif choice.isdigit():
                index = int(choice) - 1
                if 0 <= index < len(items):
                    selected = items[index][0]
                    full_path = os.path.join(self.current_dir, selected)
                    
                    if selected == "..":
                        self.current_dir = os.path.dirname(self.current_dir)
                        self.selected_path = None
                    elif os.path.isdir(full_path):
                        self.current_dir = full_path
                        self.selected_path = None
                    else:
                        self.selected_path = full_path
                        print(f"\nВыбран файл: {full_path}")
                        input("Нажмите Enter чтобы продолжить...")
                else:
                    print("Неверный номер!")
                    time.sleep(1)
    
    def zip_folder(self, folder_path):
        """Создание zip-архива папки в памяти"""
        mem_zip = io.BytesIO()
        with zipfile.ZipFile(mem_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, folder_path)
                    zf.write(file_path, arcname)
        mem_zip.seek(0)
        return mem_zip
    
    def send_file_or_folder(self, host, port, path):
        """Отправка файла или папки"""
        try:
            if os.path.isdir(path):
                # Если это папка - создаем zip в памяти
                print(f"\nПодготовка папки к отправке: {os.path.basename(path)}")
                zip_data = self.zip_folder(path)
                filesize = zip_data.getbuffer().nbytes
                filename = os.path.basename(path) + ".zip"
            else:
                # Если это файл - открываем его
                with open(path, 'rb') as f:
                    zip_data = io.BytesIO(f.read())
                filesize = os.path.getsize(path)
                filename = os.path.basename(path)
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, port))
                print(f"\nПодключено к {host}:{port}")
                
                # Отправляем информацию о файле
                s.sendall(f"{filename}{SEPARATOR}{filesize}".encode())
                
                # Ожидаем подтверждения
                if s.recv(2) != b'OK':
                    print("Сервер не готов к приему")
                    return False
                
                # Отправляем данные
                print(f"Отправка: {filename} ({self.human_readable_size(filesize)})")
                start_time = time.time()
                sent = 0
                zip_data.seek(0)
                
                while sent < filesize:
                    data = zip_data.read(min(BUFFER_SIZE, filesize - sent))
                    s.sendall(data)
                    sent += len(data)
                    
                    # Вывод прогресса
                    progress = (sent / filesize) * 100
                    speed = sent / (time.time() - start_time)
                    print(f"\rОтправлено: {progress:.1f}% | {self.human_readable_size(sent)}/{self.human_readable_size(filesize)} | {self.human_readable_size(speed)}/s", end='')
                
                print("\nПередача завершена успешно!")
                return True
        except Exception as e:
            print(f"\nОшибка отправки: {e}")
            return False
    
    def start_server(self, port):
        """Запуск сервера для приема файлов"""
        host = '0.0.0.0'
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind((host, port))
                s.listen(1)
                
                print(f"\nСервер запущен на {self.get_local_ip()}:{port}")
                print("Ожидаем подключения... (Ctrl+C для остановки)\n")
                
                conn, addr = s.accept()
                print(f"Подключен клиент: {addr}")
                
                # Получаем информацию о файле
                file_info = conn.recv(BUFFER_SIZE).decode()
                filename, filesize = file_info.split(SEPARATOR)
                filesize = int(filesize)
                
                # Подтверждаем готовность
                conn.sendall(b'OK')
                
                # Принимаем файл
                print(f"\nПрием файла: {filename} ({self.human_readable_size(filesize)})")
                self.receive_file(conn, filename, filesize)
                
            except KeyboardInterrupt:
                print("\nСервер остановлен")
            except Exception as e:
                print(f"\nОшибка сервера: {e}")
            finally:
                input("\nНажмите Enter для возврата в меню...")
    
    def receive_file(self, conn, filename, filesize):
        """Прием файла с отображением прогресса"""
        try:
            start_time = time.time()
            received = 0
            
            with open(filename, 'wb') as f:
                while received < filesize:
                    data = conn.recv(min(BUFFER_SIZE, filesize - received))
                    if not data:
                        break
                    f.write(data)
                    received += len(data)
                    
                    # Вывод прогресса
                    progress = (received / filesize) * 100
                    speed = received / (time.time() - start_time)
                    print(f"\rПолучено: {progress:.1f}% | {self.human_readable_size(received)}/{self.human_readable_size(filesize)} | {self.human_readable_size(speed)}/s", end='')
            
            print(f"\nФайл {filename} успешно получен!")
            
            # Если это zip-архив, предлагаем распаковать
            if filename.endswith('.zip'):
                choice = input("Распаковать полученный архив? (y/n): ").lower()
                if choice == 'y':
                    with zipfile.ZipFile(filename, 'r') as zip_ref:
                        zip_ref.extractall()
                    print("Архив распакован!")
            
            return True
        except Exception as e:
            print(f"\nОшибка приема: {e}")
            return False
    
    def main_menu(self):
        """Главное меню программы"""
        while self.running:
            self.clear_screen()
            print("=== УНИВЕРСАЛЬНЫЙ ФАЙЛООБМЕННИК ===")
            print(f"Ваш IP: {self.get_local_ip()}")
            print("\n1. Принимать файлы (сервер)")
            print("2. Отправить файл/папку (клиент)")
            print("3. Просмотреть файлы")
            print("4. Выход")
            
            choice = input("\nВыберите действие: ")
            
            if choice == '1':
                try:
                    port = int(input("Введите порт для сервера (по умолчанию 5000): ") or 5000)
                    self.start_server(port)
                except ValueError:
                    print("Некорректный номер порта!")
                    time.sleep(1)
            
            elif choice == '2':
                self.clear_screen()
                print("=== РЕЖИМ ОТПРАВКИ ===")
                
                host = input("Введите IP сервера: ")
                port = int(input("Введите порт сервера: "))
                
                # Навигация по файлам
                result = self.navigate_files()
                if result and result not in ["back", "exit"]:
                    self.send_file_or_folder(host, port, result)
                    input("\nНажмите Enter для продолжения...")
            
            elif choice == '3':
                self.navigate_files()
            
            elif choice == '4':
                self.running = False
            
            else:
                print("Неверный выбор!")
                time.sleep(1)

if __name__ == "__main__":
    try:
        app = FileExchange()
        app.main_menu()
    except KeyboardInterrupt:
        print("\nПрограмма завершена")
    except Exception as e:
        print(f"\nКритическая ошибка: {e}")
        input("Нажмите Enter для выхода...")
