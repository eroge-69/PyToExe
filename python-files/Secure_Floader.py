# %%
import os
import sqlite3
import hashlib
import secrets
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import lz4.frame
import sys

# Конфигурация
HEADER_SIZE = 1024
SALT_SIZE = 32
IV_SIZE = 16
KEY_SIZE = 32
MAGIC = b'SECURE_FOLDER_v1'

class SecureFolder:
    def __init__(self, container_path):
        self.container_path = container_path
        self.db_path = container_path + '.db'
        self.mounted = False
        self.temp_dir = None
        self.key = None
        
    def create(self, password):
        # Проверка, существует ли контейнер
        if os.path.exists(self.container_path):
            raise FileExistsError(f"Контейнер уже существует: {self.container_path}")
            
        # Генерация криптографических параметров
        salt = secrets.token_bytes(SALT_SIZE)
        self.key = self._derive_key(password, salt)
        
        # Создание заголовка
        header = MAGIC + salt
        header += secrets.token_bytes(HEADER_SIZE - len(header))
        
        # Запись заголовка
        with open(self.container_path, 'wb') as f:
            f.write(header)
            
        # Инициализация БД
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE files
                     (path TEXT PRIMARY KEY, iv BLOB, compressed INT, offset INTEGER, size INTEGER)''')
        conn.commit()
        conn.close()
        
        return True

    def open(self, password, mount_point):
        # Проверка существования контейнера
        if not os.path.exists(self.container_path):
            raise FileNotFoundError(f"Файл контейнера не найден: {self.container_path}")
            
        # Проверка заголовка
        with open(self.container_path, 'rb') as f:
            header = f.read(HEADER_SIZE)
            
        if not header.startswith(MAGIC):
            raise ValueError("Неверный формат контейнера")
            
        salt = header[len(MAGIC):len(MAGIC)+SALT_SIZE]
        self.key = self._derive_key(password, salt)
        
        # Проверка существования базы данных
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Файл базы данных не найден: {self.db_path}")
            
        # Создание точки монтирования
        os.makedirs(mount_point, exist_ok=True)
        self.mounted = True
        self.temp_dir = mount_point
        
        # Восстановление структуры файлов
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT path FROM files")
        for row in c.fetchall():
            target_path = os.path.join(self.temp_dir, row[0])
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            # Создаем файл с информацией о том, что это защищенный файл
            with open(target_path, 'w') as f:
                f.write(f"Это защищенный файл. Для доступа используйте приложение Secure Folder.\n")
                f.write(f"Файл: {row[0]}\n")
                f.write(f"Контейнер: {os.path.basename(self.container_path)}\n")
        conn.close()
        
        return True

    def unmount(self):
        if not self.mounted:
            return False
            
        # Очистка временных файлов
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        self.mounted = False
        self.key = None
        return True

    def add_file(self, source_path, relative_path):
        if not self.mounted:
            raise RuntimeError("Контейнер не смонтирован")
            
        # Генерация IV
        iv = secrets.token_bytes(IV_SIZE)
        
        # Шифрование файла
        with open(source_path, 'rb') as f:
            plaintext = f.read()
            
        compressed = lz4.frame.compress(plaintext)
        ciphertext = self._encrypt(compressed, iv)
        
        # Запись в контейнер
        with open(self.container_path, 'ab') as f:
            offset = f.tell()
            f.write(ciphertext)
            
        # Обновление БД
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO files VALUES (?, ?, ?, ?, ?)", 
                 (relative_path, iv, 1, offset, len(ciphertext)))
        conn.commit()
        conn.close()
        
        # Создание информационного файла
        target_path = os.path.join(self.temp_dir, relative_path)
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with open(target_path, 'w') as f:
            f.write(f"Это защищенный файл. Для доступа используйте приложение Secure Folder.\n")
            f.write(f"Файл: {relative_path}\n")
            f.write(f"Контейнер: {os.path.basename(self.container_path)}\n")
        
        return True

    def extract_file(self, relative_path, output_path):
        if not self.mounted:
            raise RuntimeError("Контейнер не смонтирован")
            
        # Получение метаданных файла
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT iv, compressed, offset, size FROM files WHERE path = ?", (relative_path,))
        row = c.fetchone()
        conn.close()
        
        if not row:
            raise FileNotFoundError(f"Файл не найден в контейнере: {relative_path}")
            
        iv, compressed, offset, size = row
        
        # Чтение зашифрованных данных
        with open(self.container_path, 'rb') as f:
            f.seek(offset)
            ciphertext = f.read(size)
            
        # Расшифровка
        decrypted = self._decrypt(ciphertext, iv)
        
        # Распаковка
        if compressed:
            plaintext = lz4.frame.decompress(decrypted)
        else:
            plaintext = decrypted
            
        # Сохранение
        with open(output_path, 'wb') as f:
            f.write(plaintext)
            
        return True

    def list_files(self):
        if not os.path.exists(self.db_path):
            return []
            
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT path FROM files")
        files = [row[0] for row in c.fetchall()]
        conn.close()
        return files

    def _derive_key(self, password, salt):
        return hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000,
            dklen=KEY_SIZE
        )

    def _encrypt(self, data, iv):
        cipher = Cipher(
            algorithms.AES(self.key),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # PKCS7 паддинг
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()
        
        return encryptor.update(padded_data) + encryptor.finalize()
        
    def _decrypt(self, data, iv):
        cipher = Cipher(
            algorithms.AES(self.key),
            modes.CBC(iv),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        # Дешифровка
        padded_data = decryptor.update(data) + decryptor.finalize()
        
        # Удаление паддинга
        unpadder = padding.PKCS7(128).unpadder()
        return unpadder.update(padded_data) + unpadder.finalize()

class SecureFolderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Защищенный контейнер")
        self.geometry("700x500")
        self.container = None
        
        # Создание вкладок
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Вкладка операций
        self.operations_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.operations_frame, text='Операции')
        self._create_operations_widgets()
        
        # Вкладка файлов
        self.files_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.files_frame, text='Файлы')
        self._create_files_widgets()
        
        # Вкладка логов
        self.log_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.log_frame, text='Логи')
        self._create_log_widgets()
        
    def _create_operations_widgets(self):
        # Поле контейнера
        container_frame = ttk.LabelFrame(self.operations_frame, text="Контейнер")
        container_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(container_frame, text="Файл контейнера:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.container_path = tk.StringVar()
        ttk.Entry(container_frame, textvariable=self.container_path, width=50).grid(row=0, column=1, padx=5, pady=5)
        
        # Раздельные кнопки для создания и открытия
        button_frame = ttk.Frame(container_frame)
        button_frame.grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Button(button_frame, text="     Создать новый...    ", 
                  command=self._browse_create_container).pack(side='top', pady=2)
        ttk.Button(button_frame, text="Открыть существующий...", 
                  command=self._browse_open_container).pack(side='top', pady=2)
        
        # Поле пароля
        password_frame = ttk.LabelFrame(self.operations_frame, text="Безопасность")
        password_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(password_frame, text="Пароль:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.password = tk.StringVar()
        ttk.Entry(password_frame, textvariable=self.password, show='*', width=50).grid(row=0, column=1, padx=5, pady=5)
        
        # Кнопки операций
        button_frame = ttk.Frame(self.operations_frame)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(button_frame, text="Создать контейнер", command=self._create_container).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Открыть контейнер", command=self._open_container).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Добавить файл", command=self._add_file).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Размонтировать", command=self._unmount_container).pack(side='left', padx=5)
        
    def _create_files_widgets(self):
        # Список файлов
        files_frame = ttk.LabelFrame(self.files_frame, text="Файлы в контейнере")
        files_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Список файлов
        self.files_listbox = tk.Listbox(files_frame, width=80, height=15)
        self.files_listbox.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(files_frame, orient='vertical', command=self.files_listbox.yview)
        scrollbar.pack(side='right', fill='y', padx=(0,5), pady=5)
        self.files_listbox.config(yscrollcommand=scrollbar.set)
        
        # Кнопки для файлов
        button_frame = ttk.Frame(self.files_frame)
        button_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(button_frame, text="Обновить список", command=self._refresh_files).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Извлечь файл", command=self._extract_file).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Открыть папку", command=self._open_folder).pack(side='right', padx=5)
        
    def _create_log_widgets(self):
        self.log_area = scrolledtext.ScrolledText(self.log_frame, wrap=tk.WORD)
        self.log_area.pack(fill='both', expand=True, padx=10, pady=10)
        self.log_area.config(state=tk.DISABLED)
        
    def _log(self, message):
        self.log_area.config(state=tk.NORMAL)
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state=tk.DISABLED)
        
    def _browse_create_container(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".sec",
            filetypes=[("Secure Container", "*.sec")]
        )
        if file_path:
            self.container_path.set(file_path)
            
    def _browse_open_container(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Secure Container", "*.sec")]
        )
        if file_path:
            self.container_path.set(file_path)
            
    def _create_container(self):
        path = self.container_path.get()
        password = self.password.get()
        
        if not path or not password:
            messagebox.showerror("Ошибка", "Укажите путь к контейнеру и пароль")
            return
            
        if not path.endswith('.sec'):
            path += '.sec'
            self.container_path.set(path)
            
        self.container = SecureFolder(path)
        try:
            if self.container.create(password):
                self._log(f"Контейнер создан: {path}")
                messagebox.showinfo("Успех", "Контейнер успешно создан")
            else:
                self._log("Ошибка создания контейнера")
                messagebox.showerror("Ошибка", "Не удалось создать контейнер")
        except Exception as e:
            self._log(f"Ошибка: {str(e)}")
            messagebox.showerror("Ошибка", str(e))
    
    def _open_container(self):
        path = self.container_path.get()
        password = self.password.get()
        
        if not path or not password:
            messagebox.showerror("Ошибка", "Укажите путь к контейнеру и пароль")
            return
            
        if not os.path.exists(path):
            self._log(f"Ошибка: файл контейнера не найден: {path}")
            messagebox.showerror("Ошибка", f"Файл контейнера не найден: {path}")
            return
            
        if not self.container or self.container.container_path != path:
            self.container = SecureFolder(path)
            
        mount_point = os.path.join(os.path.expanduser('~'), 'SecureFolder')
        os.makedirs(mount_point, exist_ok=True)
            
        try:
            if self.container.open(password, mount_point):
                self._log(f"Контейнер открыт: {path}")
                self._log(f"Контейнер смонтирован в: {mount_point}")
                self._log("Теперь вы можете добавлять файлы через кнопку 'Добавить файл'")
                messagebox.showinfo("Успех", f"Контейнер успешно открыт")
                self._refresh_files()
            else:
                self._log("Ошибка открытия контейнера")
                messagebox.showerror("Ошибка", "Не удалось открыть контейнер")
        except Exception as e:
            self._log(f"Ошибка: {str(e)}")
            messagebox.showerror("Ошибка", str(e))
    
    def _add_file(self):
        if not self.container or not self.container.mounted:
            messagebox.showerror("Ошибка", "Сначала откройте контейнер")
            return
            
        file_path = filedialog.askopenfilename(title="Выберите файл для добавления")
        if not file_path:
            return
            
        try:
            rel_path = os.path.basename(file_path)
            self.container.add_file(file_path, rel_path)
            self._log(f"Файл добавлен: {rel_path}")
            messagebox.showinfo("Успех", f"Файл добавлен: {rel_path}")
            self._refresh_files()
        except Exception as e:
            self._log(f"Ошибка: {str(e)}")
            messagebox.showerror("Ошибка", str(e))
    
    def _unmount_container(self):
        if self.container and self.container.mounted:
            try:
                if self.container.unmount():
                    self._log("Контейнер размонтирован")
                    messagebox.showinfo("Успех", "Контейнер успешно размонтирован")
                    # Очищаем список файлов
                    self.files_listbox.delete(0, tk.END)
                else:
                    self._log("Ошибка при размонтировании")
                    messagebox.showerror("Ошибка", "Не удалось размонтировать контейнер")
            except Exception as e:
                self._log(f"Ошибка при размонтировании: {str(e)}")
                messagebox.showerror("Ошибка", str(e))
        else:
            self._log("Нет открытых контейнеров")
            messagebox.showinfo("Информация", "Нет открытых контейнеров")
            
    def _refresh_files(self):
        if not self.container or not self.container.mounted:
            messagebox.showinfo("Информация", "Контейнер не открыт")
            return
            
        try:
            files = self.container.list_files()
            self.files_listbox.delete(0, tk.END)
            for file in files:
                self.files_listbox.insert(tk.END, file)
            self._log(f"Список файлов обновлен. Найдено файлов: {len(files)}")
        except Exception as e:
            self._log(f"Ошибка при обновлении списка файлов: {str(e)}")
            messagebox.showerror("Ошибка", str(e))
            
    def _extract_file(self):
        if not self.container or not self.container.mounted:
            messagebox.showerror("Ошибка", "Сначала откройте контейнер")
            return
            
        selected = self.files_listbox.curselection()
        if not selected:
            messagebox.showinfo("Информация", "Выберите файл для извлечения")
            return
            
        file_name = self.files_listbox.get(selected[0])
        
        output_path = filedialog.asksaveasfilename(
            title="Куда сохранить файл",
            initialfile=file_name,
            defaultextension=os.path.splitext(file_name)[1] if '.' in file_name else ""
        )
        
        if not output_path:
            return
            
        try:
            self.container.extract_file(file_name, output_path)
            self._log(f"Файл извлечен: {file_name} -> {output_path}")
            messagebox.showinfo("Успех", f"Файл успешно извлечен: {output_path}")
        except Exception as e:
            self._log(f"Ошибка при извлечении файла: {str(e)}")
            messagebox.showerror("Ошибка", str(e))
            
    def _open_folder(self):
        if not self.container or not self.container.mounted:
            messagebox.showerror("Ошибка", "Сначала откройте контейнер")
            return
            
        mount_point = os.path.join(os.path.expanduser('~'), 'SecureFolder')
        if os.path.exists(mount_point):
            if os.name == 'nt':  # Windows
                os.startfile(mount_point)
            elif os.name == 'posix':  # macOS, Linux
                os.system(f'open "{mount_point}"' if sys.platform == 'darwin' else f'xdg-open "{mount_point}"')
            self._log(f"Открыта папка: {mount_point}")
        else:
            self._log(f"Папка не найдена: {mount_point}")
            messagebox.showerror("Ошибка", f"Папка не найдена: {mount_point}")

if __name__ == '__main__':
    app = SecureFolderApp()
    app.mainloop()


