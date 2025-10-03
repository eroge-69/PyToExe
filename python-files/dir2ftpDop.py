import os
import ftplib
import json
from datetime import datetime
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import queue
import time

class FTPUploader:
    def __init__(self, config_file="ftp_config.json"):
        self.config = self.load_config(config_file)
        self.lock = threading.Lock()
        self.created_dirs_cache = set()  # Кэш созданных папок
        self.connection_pool = queue.Queue()  # Пул соединений
        self.active_connections = 0
        
    def load_config(self, config_file):
        """Загружает конфигурацию из JSON файла"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # Устанавливаем значения по умолчанию
                config.setdefault("port", 21)
                config.setdefault("max_workers", 5)
                config.setdefault("max_connections", 10)
                config.setdefault("timeout", 30)
                return config
        except FileNotFoundError:
            raise Exception(f"Конфигурационный файл {config_file} не найден")
    
    def create_ftp_connection(self):
        """Создает новое FTP соединение"""
        try:
            ftp = ftplib.FTP()
            ftp.connect(self.config["host"], self.config["port"], timeout=self.config["timeout"])
            ftp.login(self.config["username"], self.config["password"])
            ftp.encoding = "utf-8"
            return ftp
        except Exception as e:
            raise Exception(f"Ошибка подключения к FTP: {e}")
    
    def get_ftp_connection(self):
        """Получает соединение из пула или создает новое"""
        try:
            # Пытаемся получить соединение из пула без блокировки
            return self.connection_pool.get_nowait()
        except queue.Empty:
            # Создаем новое соединение если в пуле нет
            with self.lock:
                if self.active_connections < self.config["max_connections"]:
                    self.active_connections += 1
                    return self.create_ftp_connection()
                else:
                    # Ждем освобождения соединения
                    return self.connection_pool.get()
    
    def return_ftp_connection(self, ftp):
        """Возвращает соединение в пул"""
        try:
            # Проверяем что соединение еще живо
            ftp.voidcmd("NOOP")
            self.connection_pool.put(ftp)
        except:
            # Соединение разорвано, создаем новое
            try:
                ftp.quit()
            except:
                pass
            with self.lock:
                self.active_connections -= 1
    
    def close_all_connections(self):
        """Закрывает все соединения в пуле"""
        while not self.connection_pool.empty():
            try:
                ftp = self.connection_pool.get_nowait()
                ftp.quit()
            except:
                pass
        self.active_connections = 0
    
    def get_all_files(self, local_folder):
        """Получает список всех файлов для загрузки с размерами"""
        all_files = []
        total_size = 0
        
        if not os.path.exists(local_folder):
            raise Exception(f"Локальная папка {local_folder} не существует")
        
        for root, dirs, files in os.walk(local_folder):
            for file in files:
                full_path = os.path.join(root, file)
                try:
                    file_size = os.path.getsize(full_path)
                    relative_path = os.path.relpath(full_path, local_folder).replace('\\', '/')
                    all_files.append((full_path, relative_path, file_size))
                    total_size += file_size
                except OSError as e:
                    print(f"Ошибка доступа к файлу {full_path}: {e}")
        
        return all_files, total_size
    
    def ensure_remote_dirs(self, ftp, remote_dir):
        """Создает папки на FTP сервере если их нет"""
        if not remote_dir or remote_dir in self.created_dirs_cache:
            return
            
        folders = remote_dir.split('/')
        current_path = []
        
        for folder in folders:
            if folder:
                current_path.append(folder)
                dir_path = '/'.join(current_path)
                
                # Проверяем в кэше
                if dir_path in self.created_dirs_cache:
                    continue
                
                # Проверяем существует ли папка на сервере
                try:
                    ftp.cwd(dir_path)
                    # Папка существует, добавляем в кэш
                    with self.lock:
                        self.created_dirs_cache.add(dir_path)
                    ftp.cwd('/')
                except ftplib.error_perm:
                    # Папка не существует, создаем
                    try:
                        ftp.mkd(dir_path)
                        with self.lock:
                            self.created_dirs_cache.add(dir_path)
                    except ftplib.error_perm as e:
                        # Возможно папка была создана другим потоком
                        if "550" not in str(e):
                            raise
    
    def upload_file(self, file_info, pbar):
        """Загружает один файл в отдельном потоке"""
        local_file, remote_file, file_size = file_info
        
        try:
            # Получаем соединение из пула
            ftp = self.get_ftp_connection()
            
            try:
                # Создаем необходимые папки
                remote_dir = os.path.dirname(remote_file)
                if remote_dir:
                    with self.lock:  # Блокируем для безопасного создания папок
                        self.ensure_remote_dirs(ftp, remote_dir)
                
                # Загружаем файл
                with open(local_file, 'rb') as f:
                    ftp.storbinary(f"STOR {remote_file}", f)
                
                # Обновляем прогресс-бар
                with self.lock:
                    pbar.update(1)
                    pbar.set_postfix(
                        file=os.path.basename(local_file)[:15],
                        size=f"{file_size / 1024 / 1024:.1f}MB"
                    )
                
                return True, local_file, file_size
                
            finally:
                # Всегда возвращаем соединение в пул
                self.return_ftp_connection(ftp)
            
        except Exception as e:
            # В случае ошибки тоже возвращаем соединение
            try:
                self.return_ftp_connection(ftp)
            except:
                pass
            return False, f"{local_file}: {e}", file_size
    
    def upload(self):
        """Основной метод загрузки с многопоточностью"""
        config = self.config
        
        try:
            print("=" * 50)
            print(f"FTP Загрузчик")
            print("=" * 50)
            print(f"Сервер: {config['host']}:{config['port']}")
            print(f"Локальная папка: {config['local_folder']}")
            print(f"Потоков: {config['max_workers']}")
            print(f"Макс. соединений: {config['max_connections']}")
            print("=" * 50)
            
            # Получаем список всех файлов
            all_files, total_size = self.get_all_files(config["local_folder"])
            
            if not all_files:
                print("Файлы для загрузки не найдены!")
                return
            
            print(f"Найдено файлов: {len(all_files)}")
            print(f"Общий размер: {total_size / 1024 / 1024:.2f} MB")
            print("=" * 50)
            
            start_time = time.time()
            
            # Создаем прогресс-бар
            with tqdm(
                total=len(all_files), 
                desc="Загрузка файлов", 
                unit="file",
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]"
            ) as pbar:
                
                # Многопоточная загрузка
                with ThreadPoolExecutor(max_workers=config["max_workers"]) as executor:
                    # Запускаем задачи для каждого файла
                    future_to_file = {
                        executor.submit(self.upload_file, file_info, pbar): file_info
                        for file_info in all_files
                    }
                    
                    # Обрабатываем завершенные задачи
                    successful_uploads = 0
                    failed_uploads = []
                    total_uploaded_size = 0
                    
                    for future in as_completed(future_to_file):
                        file_info = future_to_file[future]
                        local_file, remote_file, file_size = file_info
                        
                        try:
                            success, result, size = future.result()
                            if success:
                                successful_uploads += 1
                                total_uploaded_size += size
                            else:
                                failed_uploads.append(result)
                        except Exception as e:
                            failed_uploads.append(f"{local_file}: {e}")
            
            # Закрываем все соединения
            self.close_all_connections()
            
            # Вычисляем статистику
            end_time = time.time()
            total_time = end_time - start_time
            speed = total_uploaded_size / total_time / 1024 / 1024  # MB/s
            
            # Выводим итоги
            print("\n" + "=" * 50)
            print("ЗАГРУЗКА ЗАВЕРШЕНА!")
            print("=" * 50)
            print(f"Успешно загружено: {successful_uploads}/{len(all_files)} файлов")
            print(f"Общий размер: {total_uploaded_size / 1024 / 1024:.2f} MB")
            print(f"Время выполнения: {total_time:.2f} секунд")
            print(f"Средняя скорость: {speed:.2f} MB/сек")
            
            if failed_uploads:
                print(f"\nОшибки при загрузке ({len(failed_uploads)} файлов):")
                for i, error in enumerate(failed_uploads[:10], 1):
                    print(f"  {i:2d}. {error}")
                if len(failed_uploads) > 10:
                    print(f"  ... и еще {len(failed_uploads) - 10} ошибок")
            
            print("=" * 50)
            
        except Exception as e:
            # Всегда закрываем соединения при ошибке
            self.close_all_connections()
            print(f"\nКритическая ошибка: {e}")
    
    def test_connection(self):
        """Тестирует подключение к FTP серверу"""
        try:
            ftp = self.create_ftp_connection()
            welcome_msg = ftp.getwelcome()
            ftp.quit()
            print(f"✓ Подключение успешно: {welcome_msg}")
            return True
        except Exception as e:
            print(f"✗ Ошибка подключения: {e}")
            return False

# Использование
if __name__ == "__main__":
    try:
        uploader = FTPUploader("ftp_config.json")
        
        # Тестируем подключение
        print("Тестирование подключения...")
        if not uploader.test_connection():
            exit(1)
        
        # Запускаем загрузку
        uploader.upload()
        
    except KeyboardInterrupt:
        print("\nЗагрузка прервана пользователем")
    except Exception as e:
        print(f"Ошибка: {e}")