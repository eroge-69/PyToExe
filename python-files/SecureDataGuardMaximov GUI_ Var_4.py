import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding, hashes
from cryptography.hazmat.backends import default_backend
import os
import threading
import json
import hashlib

class SecureDataGuard:
    def __init__(self, key=None, salt=None):
        self.key = key or os.urandom(32)
        self.salt = salt or os.urandom(16)

    def encrypt_binary(self, data: bytes) -> bytes:
        """Шифрование байтов (AES-256 CBC)"""
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()
        ct = encryptor.update(padded_data) + encryptor.finalize()
        return iv + ct

    def decrypt_binary(self, enc_data: bytes) -> bytes:
        """Дешифрование байтов"""
        iv, ct = enc_data[:16], enc_data[16:]
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        unpadder = padding.PKCS7(128).unpadder()
        padded_data = decryptor.update(ct) + decryptor.finalize()
        return unpadder.update(padded_data) + unpadder.finalize()

    def hash_binary(self, data: bytes) -> str:
        """Хеширование байтов с солью"""
        digest = hashes.Hash(hashes.SHA256())
        digest.update(self.salt + data)
        return digest.finalize().hex()
    
    def save_keys(self, key_dir: str):
        """Сохранить ключи в безопасном формате"""
        os.makedirs(key_dir, exist_ok=True)
        
        # Сохраняем ключ шифрования
        with open(os.path.join(key_dir, "encryption_key.bin"), "wb") as f:
            f.write(self.key)
        
        # Сохраняем соль для хеширования
        with open(os.path.join(key_dir, "hash_salt.bin"), "wb") as f:
            f.write(self.salt)
        
        # Создаем мета-файл с информацией
        meta = {
            "key_size": len(self.key) * 8,
            "salt_size": len(self.salt) * 8,
            "algorithm": "AES-256-CBC",
            "hash": "SHA-256"
        }
        with open(os.path.join(key_dir, "key_metadata.json"), "w") as f:
            json.dump(meta, f, indent=2)
    
    @classmethod
    def load_keys(cls, key_dir: str):
        """Загрузить ключи из указанной папки"""
        try:
            with open(os.path.join(key_dir, "encryption_key.bin"), "rb") as f:
                key = f.read()
            
            with open(os.path.join(key_dir, "hash_salt.bin"), "rb") as f:
                salt = f.read()
            
            return cls(key, salt)
        except FileNotFoundError:
            return None

class CryptoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SecureDataGuard - Полный цикл защиты")
        self.root.geometry("700x600")
        self.root.resizable(False, False)
        
        # Стилизация
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TButton", padding=6, font=("Arial", 10))
        self.style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))
        self.style.configure("Header.TLabel", background="#4b6cb7", 
                            foreground="white", font=("Arial", 14, "bold"))
        self.style.configure("KeyWarning.TLabel", background="#f0f0f0", 
                           foreground="red", font=("Arial", 9, "bold"))
        self.style.configure("TNotebook", background="#f0f0f0")
        self.style.configure("TNotebook.Tab", padding=(10, 5), font=("Arial", 10, "bold"))
        
        # Создаем вкладки
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Вкладка шифрования
        self.encrypt_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.encrypt_tab, text="Шифрование")
        
        # Вкладка дешифрования
        self.decrypt_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.decrypt_tab, text="Дешифрование")
        
        # Вкладка проверки целостности
        self.verify_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.verify_tab, text="Проверка целостности")
        
        # Инициализация вкладок
        self.setup_encryption_tab()
        self.setup_decryption_tab()
        self.setup_verification_tab()
        
        # Инициализация крипто-модуля
        self.crypto = None
        
        # Статус выполнения
        self.is_running = False
    
    def setup_encryption_tab(self):
        """Настройка вкладки шифрования"""
        tab = self.encrypt_tab
        
        # Заголовок
        header = ttk.Label(tab, text="Шифрование файлов", 
                          style="Header.TLabel", anchor="center")
        header.pack(fill=tk.X, pady=(0, 15), ipady=10)
        
        # Фрейм для полей ввода
        input_frame = ttk.Frame(tab)
        input_frame.pack(fill=tk.X, pady=5, padx=20)
        
        # Поле 1: Папка для шифрования
        ttk.Label(input_frame, text="Папка для шифрования:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.enc_source_entry = ttk.Entry(input_frame, width=50)
        self.enc_source_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(input_frame, text="Обзор...", command=lambda: self.browse_folder(self.enc_source_entry)).grid(row=0, column=2, padx=5, pady=5)
        
        # Поле 2: Папка для зашифрованных файлов
        ttk.Label(input_frame, text="Папка для зашифрованных файлов:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.enc_dest_entry = ttk.Entry(input_frame, width=50)
        self.enc_dest_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(input_frame, text="Обзор...", command=lambda: self.browse_folder(self.enc_dest_entry)).grid(row=1, column=2, padx=5, pady=5)
        
        # Поле 3: Папка для хэшей
        ttk.Label(input_frame, text="Папка для хранения хэшей:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.enc_hash_entry = ttk.Entry(input_frame, width=50)
        self.enc_hash_entry.grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(input_frame, text="Обзор...", command=lambda: self.browse_folder(self.enc_hash_entry)).grid(row=2, column=2, padx=5, pady=5)
        
        # Поле 4: Папка для ключей
        ttk.Label(input_frame, text="Папка для хранения ключей:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.enc_key_entry = ttk.Entry(input_frame, width=50)
        self.enc_key_entry.grid(row=3, column=1, padx=5, pady=5)
        ttk.Button(input_frame, text="Обзор...", command=lambda: self.browse_folder(self.enc_key_entry)).grid(row=3, column=2, padx=5, pady=5)
        
        # Предупреждение о ключах
        key_warning = ttk.Label(input_frame, 
                               text="ВАЖНО: Сохраните эту папку! Без ключей восстановление данных невозможно!",
                               style="KeyWarning.TLabel")
        key_warning.grid(row=4, column=0, columnspan=3, pady=(10, 5), sticky="w")
        
        # Кнопки управления
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill=tk.X, pady=10, padx=20)
        
        # Кнопка генерации ключей
        self.gen_key_button = ttk.Button(btn_frame, text="Сгенерировать новые ключи", 
                                        command=self.generate_keys, state=tk.DISABLED)
        self.gen_key_button.pack(side=tk.LEFT, padx=5)
        
        # Кнопка запуска шифрования
        self.enc_start_button = ttk.Button(btn_frame, text="Запустить шифрование", 
                                     command=lambda: self.start_processing("encrypt"), state=tk.DISABLED)
        self.enc_start_button.pack(side=tk.RIGHT, padx=5)
        
        # Прогресс бар
        self.enc_progress = ttk.Progressbar(tab, orient="horizontal", 
                                       length=600, mode="determinate")
        self.enc_progress.pack(pady=10, padx=20)
        
        # Лог операций
        log_frame = ttk.LabelFrame(tab, text="Журнал операций шифрования")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=20)
        
        self.enc_log_text = tk.Text(log_frame, height=8, state=tk.DISABLED)
        self.enc_log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Привязка событий для проверки заполнения
        for entry in [self.enc_source_entry, self.enc_dest_entry, 
                     self.enc_hash_entry, self.enc_key_entry]:
            entry.bind("<KeyRelease>", self.check_enc_fields)
    
    def setup_decryption_tab(self):
        """Настройка вкладки дешифрования"""
        tab = self.decrypt_tab
        
        # Заголовок
        header = ttk.Label(tab, text="Дешифрование файлов", 
                          style="Header.TLabel", anchor="center")
        header.pack(fill=tk.X, pady=(0, 15), ipady=10)
        
        # Фрейм для полей ввода
        input_frame = ttk.Frame(tab)
        input_frame.pack(fill=tk.X, pady=5, padx=20)
        
        # Поле 1: Папка с зашифрованными файлами
        ttk.Label(input_frame, text="Папка с зашифрованными файлами:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.dec_source_entry = ttk.Entry(input_frame, width=50)
        self.dec_source_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(input_frame, text="Обзор...", command=lambda: self.browse_folder(self.dec_source_entry)).grid(row=0, column=2, padx=5, pady=5)
        
        # Поле 2: Папка для расшифрованных файлов
        ttk.Label(input_frame, text="Папка для расшифрованных файлов:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.dec_dest_entry = ttk.Entry(input_frame, width=50)
        self.dec_dest_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(input_frame, text="Обзор...", command=lambda: self.browse_folder(self.dec_dest_entry)).grid(row=1, column=2, padx=5, pady=5)
        
        # Поле 3: Папка с хэшами (для проверки)
        ttk.Label(input_frame, text="Папка с хэшами (опционально):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.dec_hash_entry = ttk.Entry(input_frame, width=50)
        self.dec_hash_entry.grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(input_frame, text="Обзор...", command=lambda: self.browse_folder(self.dec_hash_entry)).grid(row=2, column=2, padx=5, pady=5)
        
        # Поле 4: Папка с ключами
        ttk.Label(input_frame, text="Папка с ключами шифрования:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.dec_key_entry = ttk.Entry(input_frame, width=50)
        self.dec_key_entry.grid(row=3, column=1, padx=5, pady=5)
        ttk.Button(input_frame, text="Обзор...", command=lambda: self.browse_folder(self.dec_key_entry)).grid(row=3, column=2, padx=5, pady=5)
        
        # Кнопки управления
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill=tk.X, pady=10, padx=20)
        
        # Кнопка загрузки ключей
        self.load_key_button = ttk.Button(btn_frame, text="Загрузить ключи", 
                                        command=self.load_decryption_keys, state=tk.DISABLED)
        self.load_key_button.pack(side=tk.LEFT, padx=5)
        
        # Кнопка запуска дешифрования
        self.dec_start_button = ttk.Button(btn_frame, text="Запустить дешифрование", 
                                     command=lambda: self.start_processing("decrypt"), state=tk.DISABLED)
        self.dec_start_button.pack(side=tk.RIGHT, padx=5)
        
        # Прогресс бар
        self.dec_progress = ttk.Progressbar(tab, orient="horizontal", 
                                       length=600, mode="determinate")
        self.dec_progress.pack(pady=10, padx=20)
        
        # Лог операций
        log_frame = ttk.LabelFrame(tab, text="Журнал операций дешифрования")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=20)
        
        self.dec_log_text = tk.Text(log_frame, height=8, state=tk.DISABLED)
        self.dec_log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Привязка событий для проверки заполнения
        for entry in [self.dec_source_entry, self.dec_dest_entry, 
                     self.dec_key_entry]:
            entry.bind("<KeyRelease>", self.check_dec_fields)
    
    def setup_verification_tab(self):
        """Настройка вкладки проверки целостности"""
        tab = self.verify_tab
        
        # Заголовок
        header = ttk.Label(tab, text="Проверка целостности файлов", 
                          style="Header.TLabel", anchor="center")
        header.pack(fill=tk.X, pady=(0, 15), ipady=10)
        
        # Фрейм для полей ввода
        input_frame = ttk.Frame(tab)
        input_frame.pack(fill=tk.X, pady=5, padx=20)
        
        # Поле 1: Папка с исходными файлами
        ttk.Label(input_frame, text="Папка с файлами для проверки:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.ver_source_entry = ttk.Entry(input_frame, width=50)
        self.ver_source_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(input_frame, text="Обзор...", command=lambda: self.browse_folder(self.ver_source_entry)).grid(row=0, column=2, padx=5, pady=5)
        
        # Поле 2: Папка с хэшами
        ttk.Label(input_frame, text="Папка с хранимыми хэшами:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.ver_hash_entry = ttk.Entry(input_frame, width=50)
        self.ver_hash_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(input_frame, text="Обзор...", command=lambda: self.browse_folder(self.ver_hash_entry)).grid(row=1, column=2, padx=5, pady=5)
        
        # Поле 3: Папка с ключами
        ttk.Label(input_frame, text="Папка с ключами шифрования:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.ver_key_entry = ttk.Entry(input_frame, width=50)
        self.ver_key_entry.grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(input_frame, text="Обзор...", command=lambda: self.browse_folder(self.ver_key_entry)).grid(row=2, column=2, padx=5, pady=5)
        
        # Кнопки управления
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill=tk.X, pady=10, padx=20)
        
        # Кнопка загрузки ключей
        self.ver_load_key_button = ttk.Button(btn_frame, text="Загрузить ключи", 
                                        command=self.load_verification_keys, state=tk.DISABLED)
        self.ver_load_key_button.pack(side=tk.LEFT, padx=5)
        
        # Кнопка запуска проверки
        self.ver_start_button = ttk.Button(btn_frame, text="Запустить проверку", 
                                     command=lambda: self.start_processing("verify"), state=tk.DISABLED)
        self.ver_start_button.pack(side=tk.RIGHT, padx=5)
        
        # Прогресс бар
        self.ver_progress = ttk.Progressbar(tab, orient="horizontal", 
                                       length=600, mode="determinate")
        self.ver_progress.pack(pady=10, padx=20)
        
        # Лог операций
        log_frame = ttk.LabelFrame(tab, text="Результаты проверки")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=20)
        
        self.ver_log_text = tk.Text(log_frame, height=8, state=tk.DISABLED)
        self.ver_log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Привязка событий для проверки заполнения
        for entry in [self.ver_source_entry, self.ver_hash_entry, 
                     self.ver_key_entry]:
            entry.bind("<KeyRelease>", self.check_ver_fields)
    
    def browse_folder(self, entry_widget):
        """Обзор папок"""
        path = filedialog.askdirectory()
        if path:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, path)
    
    def check_enc_fields(self, event=None):
        """Проверка заполнения полей шифрования"""
        fields_filled = all([
            self.enc_source_entry.get(),
            self.enc_dest_entry.get(),
            self.enc_hash_entry.get(),
            self.enc_key_entry.get()
        ])
        
        if fields_filled:
            self.gen_key_button.config(state=tk.NORMAL)
            self.enc_start_button.config(state=tk.NORMAL)
        else:
            self.gen_key_button.config(state=tk.DISABLED)
            self.enc_start_button.config(state=tk.DISABLED)
    
    def check_dec_fields(self, event=None):
        """Проверка заполнения полей дешифрования"""
        fields_filled = all([
            self.dec_source_entry.get(),
            self.dec_dest_entry.get(),
            self.dec_key_entry.get()
        ])
        
        if fields_filled:
            self.load_key_button.config(state=tk.NORMAL)
            self.dec_start_button.config(state=tk.NORMAL)
        else:
            self.load_key_button.config(state=tk.DISABLED)
            self.dec_start_button.config(state=tk.DISABLED)
    
    def check_ver_fields(self, event=None):
        """Проверка заполнения полей проверки"""
        fields_filled = all([
            self.ver_source_entry.get(),
            self.ver_hash_entry.get(),
            self.ver_key_entry.get()
        ])
        
        if fields_filled:
            self.ver_load_key_button.config(state=tk.NORMAL)
            self.ver_start_button.config(state=tk.NORMAL)
        else:
            self.ver_load_key_button.config(state=tk.DISABLED)
            self.ver_start_button.config(state=tk.DISABLED)
    
    def generate_keys(self):
        """Генерация новых ключей шифрования"""
        key_dir = self.enc_key_entry.get().strip()
        
        if not key_dir:
            messagebox.showerror("Ошибка", "Сначала укажите папку для ключей!")
            return
        
        try:
            # Генерируем новые ключи
            self.crypto = SecureDataGuard()
            
            # Сохраняем ключи в указанную папку
            self.crypto.save_keys(key_dir)
            
            # Сообщаем пользователю
            messagebox.showinfo("Ключи сгенерированы", 
                               f"Новые ключи шифрования успешно сохранены в:\n{key_dir}\n\n"
                               "Обязательно сохраните эту папку в безопасном месте!")
            
            self.log_message("enc", f"Сгенерированы новые ключи: {key_dir}")
            self.log_message("enc", f"Размер ключа шифрования: {len(self.crypto.key)*8} бит")
            self.log_message("enc", f"Размер соли для хеширования: {len(self.crypto.salt)*8} бит")
            
        except Exception as e:
            messagebox.showerror("Ошибка генерации ключей", f"Произошла ошибка:\n{str(e)}")
    
    def load_decryption_keys(self):
        """Загрузка ключей для дешифрования"""
        key_dir = self.dec_key_entry.get().strip()
        
        if not key_dir:
            messagebox.showerror("Ошибка", "Сначала укажите папку с ключами!")
            return
        
        try:
            # Загружаем ключи
            self.crypto = SecureDataGuard.load_keys(key_dir)
            
            if not self.crypto:
                raise ValueError("Ключи не найдены в указанной папке")
            
            # Сообщаем пользователю
            messagebox.showinfo("Ключи загружены", 
                               f"Ключи шифрования успешно загружены из:\n{key_dir}")
            
            self.log_message("dec", f"Загружены ключи: {key_dir}")
            self.log_message("dec", f"Размер ключа: {len(self.crypto.key)*8} бит")
            
        except Exception as e:
            messagebox.showerror("Ошибка загрузки ключей", f"Произошла ошибка:\n{str(e)}")
    
    def load_verification_keys(self):
        """Загрузка ключей для проверки"""
        key_dir = self.ver_key_entry.get().strip()
        
        if not key_dir:
            messagebox.showerror("Ошибка", "Сначала укажите папку с ключами!")
            return
        
        try:
            # Загружаем ключи
            self.crypto = SecureDataGuard.load_keys(key_dir)
            
            if not self.crypto:
                raise ValueError("Ключи не найдены в указанной папке")
            
            # Сообщаем пользователю
            messagebox.showinfo("Ключи загружены", 
                               f"Ключи шифрования успешно загружены из:\n{key_dir}")
            
            self.log_message("ver", f"Загружены ключи: {key_dir}")
            
        except Exception as e:
            messagebox.showerror("Ошибка загрузки ключей", f"Произошла ошибка:\n{str(e)}")
    
    def log_message(self, tab, message):
        """Добавить сообщение в лог указанной вкладки"""
        if tab == "enc":
            log_widget = self.enc_log_text
        elif tab == "dec":
            log_widget = self.dec_log_text
        else:
            log_widget = self.ver_log_text
        
        log_widget.config(state=tk.NORMAL)
        log_widget.insert(tk.END, message + "\n")
        log_widget.see(tk.END)
        log_widget.config(state=tk.DISABLED)
    
    def start_processing(self, mode):
        """Запуск процесса обработки файлов"""
        if self.is_running:
            return
            
        if mode == "encrypt":
            source = self.enc_source_entry.get()
            dest = self.enc_dest_entry.get()
            hash_dir = self.enc_hash_entry.get()
            key_dir = self.enc_key_entry.get()
            progress = self.enc_progress
            log_tab = "enc"
        elif mode == "decrypt":
            source = self.dec_source_entry.get()
            dest = self.dec_dest_entry.get()
            hash_dir = self.dec_hash_entry.get()
            key_dir = self.dec_key_entry.get()
            progress = self.dec_progress
            log_tab = "dec"
        else:  # verify
            source = self.ver_source_entry.get()
            hash_dir = self.ver_hash_entry.get()
            key_dir = self.ver_key_entry.get()
            progress = self.ver_progress
            log_tab = "ver"
        
        # Проверка существования директорий
        if not os.path.exists(source) or not os.path.isdir(source):
            messagebox.showerror("Ошибка", f"Директория '{source}' не существует!")
            return
        
        # Для шифрования и дешифрования нужны ключи
        if mode in ("encrypt", "decrypt", "verify") and not self.crypto:
            # Пытаемся загрузить ключи
            self.crypto = SecureDataGuard.load_keys(key_dir)
            
            if not self.crypto:
                messagebox.showerror("Ошибка", 
                                   "Ключи шифрования не загружены!\n"
                                   "Сначала загрузите или сгенерируйте ключи.")
                return
        
        # Создать целевые директории
        if mode == "encrypt":
            os.makedirs(dest, exist_ok=True)
            os.makedirs(hash_dir, exist_ok=True)
        elif mode == "decrypt":
            os.makedirs(dest, exist_ok=True)
        
        # Получить список файлов
        if mode == "encrypt":
            files = [f for f in os.listdir(source) if os.path.isfile(os.path.join(source, f))]
        elif mode == "decrypt":
            files = [f for f in os.listdir(source) if f.endswith(".enc")]
        else:  # verify
            files = [f for f in os.listdir(source) if os.path.isfile(os.path.join(source, f))]
        
        if not files:
            messagebox.showinfo("Информация", "В указанной папке нет файлов для обработки")
            return
        
        # Настройка прогрессбара
        progress["maximum"] = len(files)
        progress["value"] = 0
        
        # Очистить лог
        if mode == "encrypt":
            log_widget = self.enc_log_text
        elif mode == "decrypt":
            log_widget = self.dec_log_text
        else:
            log_widget = self.ver_log_text
            
        log_widget.config(state=tk.NORMAL)
        log_widget.delete(1.0, tk.END)
        log_widget.config(state=tk.DISABLED)
        
        self.log_message(log_tab, f"Начата обработка {len(files)} файлов...")
        
        # Запуск в отдельном потоке
        self.is_running = True
        threading.Thread(
            target=self.process_files, 
            args=(mode, source, dest, hash_dir, files),
            daemon=True
        ).start()
    
    def process_files(self, mode, source_dir, dest_dir, hash_dir, files):
        """Обработка файлов в фоновом режиме"""
        try:
            for i, filename in enumerate(files):
                if not self.is_running:
                    break
                    
                source_path = os.path.join(source_dir, filename)
                
                if mode == "encrypt":
                    # Чтение файла
                    with open(source_path, 'rb') as f:
                        data = f.read()
                    
                    # Шифрование
                    encrypted = self.crypto.encrypt_binary(data)
                    
                    # Сохранение зашифрованного файла
                    enc_filename = f"{filename}.enc"
                    enc_path = os.path.join(dest_dir, enc_filename)
                    with open(enc_path, 'wb') as f:
                        f.write(encrypted)
                    
                    # Генерация и сохранение хеша
                    file_hash = self.crypto.hash_binary(data)
                    hash_path = os.path.join(hash_dir, f"{filename}.hash")
                    with open(hash_path, 'w') as f:
                        f.write(file_hash)
                    
                    # Обновление GUI
                    self.root.after(0, self.update_progress, "enc", i+1, filename)
                
                elif mode == "decrypt":
                    # Чтение зашифрованного файла
                    with open(source_path, 'rb') as f:
                        encrypted_data = f.read()
                    
                    # Дешифрование
                    decrypted = self.crypto.decrypt_binary(encrypted_data)
                    
                    # Сохранение расшифрованного файла
                    dec_filename = filename[:-4]  # Удаляем .enc
                    dec_path = os.path.join(dest_dir, dec_filename)
                    with open(dec_path, 'wb') as f:
                        f.write(decrypted)
                    
                    # Проверка хеша (если указана папка с хэшами)
                    if hash_dir:
                        hash_file = os.path.join(hash_dir, f"{dec_filename}.hash")
                        if os.path.exists(hash_file):
                            with open(hash_file, 'r') as f:
                                original_hash = f.read().strip()
                            
                            current_hash = self.crypto.hash_binary(decrypted)
                            status = "✓" if current_hash == original_hash else "✗"
                            self.log_message("dec", f"Проверка хеша {dec_filename}: {status}")
                    
                    # Обновление GUI
                    self.root.after(0, self.update_progress, "dec", i+1, filename)
                
                else:  # verify
                    # Чтение файла
                    with open(source_path, 'rb') as f:
                        data = f.read()
                    
                    # Получение хеша
                    current_hash = self.crypto.hash_binary(data)
                    
                    # Поиск сохраненного хеша
                    hash_file = os.path.join(hash_dir, f"{filename}.hash")
                    if os.path.exists(hash_file):
                        with open(hash_file, 'r') as f:
                            original_hash = f.read().strip()
                        
                        status = "✓ Целостность подтверждена" if current_hash == original_hash else "✗ Нарушена целостность!"
                        self.log_message("ver", f"Файл: {filename} - {status}")
                    else:
                        self.log_message("ver", f"Файл: {filename} - Хеш не найден!")
                    
                    # Обновление GUI
                    self.root.after(0, self.update_progress, "ver", i+1, filename)
            
            self.root.after(0, self.complete_processing, mode)
        except Exception as e:
            self.root.after(0, self.show_error, mode, str(e))
    
    def update_progress(self, tab, value, filename):
        """Обновить прогрессбар и лог"""
        if tab == "enc":
            self.enc_progress["value"] = value
            self.log_message("enc", f"Зашифрован: {filename}")
        elif tab == "dec":
            self.dec_progress["value"] = value
            self.log_message("dec", f"Расшифрован: {filename}")
        else:
            self.ver_progress["value"] = value
            # Сообщение о проверке уже добавлено в process_files
    
    def complete_processing(self, mode):
        """Завершение обработки"""
        self.is_running = False
        
        if mode == "encrypt":
            self.log_message("enc", "-" * 50)
            self.log_message("enc", "Шифрование успешно завершено!")
            self.log_message("enc", f"Обработано файлов: {int(self.enc_progress['value'])}")
            messagebox.showinfo("Готово", "Все файлы успешно зашифрованы и защищены!")
        elif mode == "decrypt":
            self.log_message("dec", "-" * 50)
            self.log_message("dec", "Дешифрование успешно завершено!")
            self.log_message("dec", f"Обработано файлов: {int(self.dec_progress['value'])}")
            messagebox.showinfo("Готово", "Все файлы успешно расшифрованы!")
        else:
            self.log_message("ver", "-" * 50)
            self.log_message("ver", "Проверка целостности завершена!")
            self.log_message("ver", f"Проверено файлов: {int(self.ver_progress['value'])}")
            messagebox.showinfo("Готово", "Проверка целостности файлов завершена!")
    
    def show_error(self, mode, message):
        """Показать ошибку"""
        self.is_running = False
        self.log_message(mode, f"ОШИБКА: {message}")
        messagebox.showerror("Ошибка", f"Произошла ошибка:\n{message}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CryptoApp(root)
    root.mainloop()
