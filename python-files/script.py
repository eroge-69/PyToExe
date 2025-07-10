import os
import json
import threading
import ctypes
import logging
from datetime import datetime
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import re
import customtkinter as ctk
from tkinter import messagebox, filedialog
import tkinter as tk


def clear_string_memory(string):
    """Очищает строку из памяти, перезаписывая её нули."""
    if not string:
        logging.debug("clear_string_memory: Пустая строка, очистка не требуется")
        return
    try:
        str_len = len(string)
        buffer = ctypes.create_string_buffer(string.encode('utf-8'))
        ctypes.memset(buffer, 0, str_len)
        logging.debug(f"clear_string_memory: Очищена строка длиной {str_len} символов")
    except Exception as e:
        logging.error(f"clear_string_memory: Ошибка при очистке памяти: {e}")

# --- Менеджер настроек ---
class SettingsManager:
    def __init__(self, settings_file="settings.json"):
        self.settings_file = settings_file
        self.default_settings = {
            "theme": "dark",
            "font_size": 14,
            "language": "ru"
        }
        self.settings = self.load_settings()
        self.localization = {
            "ru": {
                "app_title": "🔐 Защищенный блокнот",
                "login_title": "🔐 Защищенный блокнот - Вход",
                "password_label": "Пароль:",
                "file_label": "Файл блокнота:",
                "create_button": "Создать новый",
                "load_button": "Открыть",
                "info_text": "• Создайте новый блокнот или откройте существующий\n• Все данные шифруются с помощью AES-256\n• Без пароля данные невозможно расшифровать",
                "error": "Ошибка",
                "success": "Успех",
                "new_note": "📝 Новая запись",
                "save": "💾 Сохранить",
                "change_password": "🔑 Сменить пароль",
                "settings": "⚙️ Настройки",
                "notes_label": "📋 Записи",
                "select_note": "Выберите запись для просмотра",
                "edit": "✏️ Редактировать",
                "delete": "🗑️ Удалить",
                "settings_title": "⚙️ Настройки",
                "theme_label": "Тема:",
                "font_size_label": "Размер шрифта:",
                "language_label": "Язык:",
                "save_settings": "Сохранить",
                "cancel": "Отмена",
                "dark_theme": "Темная",
                "light_theme": "Светлая",
                "russian": "Русский",
                "english": "Английский",
                "created": "Создано",
                "modified": "Изменено",
                "confirm_delete": "Подтверждение",
                "delete_note_confirm": "Вы уверены, что хотите удалить запись '{}'?",
                "save_result": "Результат сохранения",
                "close_confirm": "Закрытие",
                "save_before_exit": "Сохранить изменения перед выходом?",
                "save_error": "Ошибка сохранения при выходе",
                "invalid_password": "Неверный пароль",
                "corrupted_file": "Поврежденный файл: некорректные данные",
                "file_not_found": "Файл не найден",
                "invalid_file_extension": "Выберите файл с расширением .dat",
                "password_required": "Введите пароль",
                "file_required": "Выберите или введите имя файла",
                "weak_password": "Пароль слишком слабый. Проверьте требования",
                "file_exists": "Файл '{}' уже существует. Перезаписать?"
            },
            "en": {
                "app_title": "🔐 Secure Notepad",
                "login_title": "🔐 Secure Notepad - Login",
                "password_label": "Password:",
                "file_label": "Notepad File:",
                "create_button": "Create New",
                "load_button": "Open",
                "info_text": "• Create a new notepad or open an existing one\n• All data is encrypted with AES-256\n• Data cannot be decrypted without the password",
                "error": "Error",
                "success": "Success",
                "new_note": "📝 New Note",
                "save": "💾 Save",
                "change_password": "🔑 Change Password",
                "settings": "⚙️ Settings",
                "notes_label": "📋 Notes",
                "select_note": "Select a note to view",
                "edit": "✏️ Edit",
                "delete": "🗑️ Delete",
                "settings_title": "⚙️ Settings",
                "theme_label": "Theme:",
                "font_size_label": "Font Size:",
                "language_label": "Language:",
                "save_settings": "Save",
                "cancel": "Cancel",
                "dark_theme": "Dark",
                "light_theme": "Light",
                "russian": "Russian",
                "english": "English",
                "created": "Created",
                "modified": "Modified",
                "confirm_delete": "Confirmation",
                "delete_note_confirm": "Are you sure you want to delete the note '{}'?",
                "save_result": "Save Result",
                "close_confirm": "Closing",
                "save_before_exit": "Save changes before exiting?",
                "save_error": "Error saving on exit",
                "invalid_password": "Invalid password",
                "corrupted_file": "Corrupted file: invalid data",
                "file_not_found": "File not found",
                "invalid_file_extension": "Select a file with .dat extension",
                "password_required": "Enter a password",
                "file_required": "Select or enter a file name",
                "weak_password": "Password is too weak. Check requirements",
                "file_exists": "File '{}' already exists. Overwrite?"
            }
        }

    def load_settings(self):
        """Загрузка настроек из файла"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                # Проверяем, что все ключи присутствуют
                for key in self.default_settings:
                    if key not in settings:
                        settings[key] = self.default_settings[key]
                return settings
            except (OSError, json.JSONDecodeError):
                return self.default_settings.copy()
        return self.default_settings.copy()

    def save_settings(self, settings):
        """Сохранение настроек в файл"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            self.settings = settings
            return True, "Настройки сохранены."
        except OSError as e:
            return False, f"Ошибка сохранения настроек: {e}"

    def apply_settings(self, root):
        """Применение настроек к приложению"""
        ctk.set_appearance_mode(self.settings["theme"])
        # Применение размера шрифта и темы будет в UI классах
        return self.settings["font_size"], self.settings["language"]

    def get_text(self, key):
        """Получение локализованного текста"""
        return self.localization[self.settings["language"]].get(key, key)


# --- Класс EncryptedNotepad ---
class EncryptedNotepad:
    def __init__(self, filename="encrypted_notes.dat"):
        self.filename = filename
        self.notes = []
        self.key = None
        self.cipher = None
        self.salt = None

    def _derive_key(self, password, salt):
        """Создание ключа шифрования из пароля"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=600000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    def _encrypt_data(self, data):
        """Шифрование данных"""
        if self.cipher is None:
            raise ValueError("Блокнот не инициализирован для шифрования.")
        return self.cipher.encrypt(data.encode())

    def _decrypt_data(self, encrypted_data):
        """Расшифровка данных"""
        if self.cipher is None:
            raise ValueError("Блокнот не инициализирован для расшифровки.")
        return self.cipher.decrypt(encrypted_data).decode()

    def create_new_notepad(self, password):
        """Создание нового блокнота"""
        try:
            self.salt = os.urandom(16)
            self.key = self._derive_key(password, self.salt)
            self.cipher = Fernet(self.key)
            self.notes = []

            with open(self.filename, 'wb') as f:
                f.write(self.salt)

            return True, "Новый блокнот создан успешно!"
        except OSError as e:
            return False, f"Ошибка записи файла: {e}"
        except Exception as e:
            return False, f"Ошибка при создании нового блокнота: {e}"

    def load_notepad(self, password):
        """Загрузка существующего блокнота"""
        if not os.path.exists(self.filename):
            return False, "Файл блокнота не найден."

        try:
            with open(self.filename, 'rb') as f:
                salt = f.read(16)
                if len(salt) != 16:
                    return False, "Поврежденный файл: Неверный формат соли."
                encrypted_data = f.read()

            temp_key = self._derive_key(password, salt)
            temp_cipher = Fernet(temp_key)

            self.notes = []
            if encrypted_data:
                try:
                    decrypted_data = temp_cipher.decrypt(encrypted_data).decode()
                    self.notes = json.loads(decrypted_data)
                except InvalidToken:
                    return False, "Неверный пароль."
                except json.JSONDecodeError:
                    return False, "Поврежденный файл: некорректные данные."
            self.key = temp_key
            self.cipher = temp_cipher
            self.salt = salt
            return True, "Блокнот загружен успешно."
        except OSError as e:
            return False, f"Ошибка чтения файла: {e}"
        except Exception as e:
            return False, f"Непредвиденная ошибка при чтении файла: {e}"

    def save_notepad(self):
        """Сохранение блокнота"""
        if self.cipher is None or self.salt is None:
            return False, "Блокнот не инициализирован."

        try:
            json_data = json.dumps(self.notes, ensure_ascii=False, indent=2)
            encrypted_data = self._encrypt_data(json_data)

            with open(self.filename, 'wb') as f:
                f.write(self.salt)
                f.write(encrypted_data)

            return True, "Блокнот сохранен успешно!"
        except OSError as e:
            return False, f"Ошибка записи файла: {e}"
        except Exception as e:
            return False, f"Ошибка при сохранении блокнота: {e}"

    def change_password(self, old_password, new_password):
        """Смена пароля блокнота"""
        if not self.key or not self.cipher or not self.salt:
            return False, "Блокнот не загружен."

        temp_key = self._derive_key(old_password, self.salt)
        if temp_key != self.key:
            return False, "Старый пароль неверен."

        try:
            new_salt = os.urandom(16)
            self.key = self._derive_key(new_password, new_salt)
            self.cipher = Fernet(self.key)
            json_data = json.dumps(self.notes, ensure_ascii=False, indent=2)
            encrypted_data = self.cipher.encrypt(json_data.encode())

            with open(self.filename, 'wb') as f:
                f.write(new_salt)
                f.write(encrypted_data)

            self.salt = new_salt
            return True, "Пароль успешно изменен!"
        except OSError as e:
            return False, f"Ошибка записи файла: {e}"
        except Exception as e:
            return False, f"Ошибка при смене пароля: {e}"

    def add_note(self, title, content):
        """Добавление новой записи"""
        if len(title) > 100:
            return False, "Заголовок слишком длинный (макс. 100 символов)."
        if len(content) > 10000:
            return False, "Содержимое слишком длинное (макс. 10000 символов)."

        note = {
            'id': max([n['id'] for n in self.notes], default=0) + 1,
            'title': title,
            'content': content,
            'created': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'modified': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.notes.append(note)
        return True, note

    def get_note_by_id(self, note_id):
        """Получение записи по ID"""
        for note in self.notes:
            if note['id'] == note_id:
                return note
        return None

    def edit_note(self, note_id, new_title=None, new_content=None):
        """Редактирование записи"""
        if new_title and len(new_title) > 100:
            return False, "Заголовок слишком длинный (макс. 100 символов)."
        if new_content and len(new_content) > 10000:
            return False, "Содержимое слишком длинное (макс. 10000 символов)."

        note = self.get_note_by_id(note_id)
        if note:
            if new_title is not None:
                note['title'] = new_title
            if new_content is not None:
                note['content'] = new_content
            note['modified'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            return True, "Запись обновлена."
        return False, "Запись не найдена."

    def delete_note(self, note_id):
        """Удаление записи"""
        note = self.get_note_by_id(note_id)
        if note:
            self.notes.remove(note)
            return True, "Запись удалена."
        return False, "Запись не найдена."

    def search_notes(self, query):
        """Поиск записей"""
        if not query:
            return sorted(self.notes, key=lambda x: x['modified'], reverse=True)

        query_lower = query.lower()
        found_notes = [
            note for note in self.notes
            if query_lower in note['title'].lower() or query_lower in note['content'].lower()
        ]
        return sorted(found_notes, key=lambda x: x['modified'], reverse=True)


# --- Вспомогательные функции ---
def _check_password_strength(password):
    """Проверка сложности пароля"""
    if len(password) < 8:
        return "Пароль должен содержать минимум 8 символов."
    if not re.search(r"[a-z]", password):
        return "Пароль должен содержать хотя бы одну строчную букву."
    if not re.search(r"[A-Z]", password):
        return "Пароль должен содержать хотя бы одну заглавную букву."
    if not re.search(r"[0-9]", password):
        return "Пароль должен содержать хотя бы одну цифру."
    if not re.search(r"[!@#$%^&*()_+=\-{}[\]|;:'\",.<>/?`~]", password):
        return "Пароль должен содержать хотя бы один специальный символ."
    return None


# --- Окно настроек ---
class SettingsWindow:
    def __init__(self, main_app):
        self.main_app = main_app
        self.window = ctk.CTkToplevel()
        self.window.title(self.main_app.settings.get_text("settings_title"))
        self.window.geometry("550x480")
        self.window.resizable(False, False)
        self.window.transient(main_app.root)
        self.window.grab_set()
        self.setup_ui()

    def setup_ui(self):
        title_label = ctk.CTkLabel(
            self.window,
            text=self.main_app.settings.get_text("settings_title"),
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=20)

        # Тема
        ctk.CTkLabel(self.window, text=self.main_app.settings.get_text("theme_label")).pack(pady=(10, 5))
        self.theme_var = tk.StringVar(value=self.main_app.settings.settings["theme"])
        theme_menu = ctk.CTkOptionMenu(
            self.window,
            variable=self.theme_var,
            values=["dark", "light"],
            width=200
        )
        theme_menu.pack(pady=5)

        # Размер шрифта
        ctk.CTkLabel(self.window, text=self.main_app.settings.get_text("font_size_label")).pack(pady=(10, 5))
        self.font_size_var = tk.StringVar(value=str(self.main_app.settings.settings["font_size"]))
        font_size_menu = ctk.CTkOptionMenu(
            self.window,
            variable=self.font_size_var,
            values=["12", "14", "16"],
            width=200
        )
        font_size_menu.pack(pady=5)

        # Язык
        ctk.CTkLabel(self.window, text=self.main_app.settings.get_text("language_label")).pack(pady=(10, 5))
        self.language_var = tk.StringVar(value=self.main_app.settings.settings["language"])
        language_menu = ctk.CTkOptionMenu(
            self.window,
            variable=self.language_var,
            values=["ru", "en"],
            width=200
        )
        language_menu.pack(pady=5)

        button_frame = ctk.CTkFrame(self.window)
        button_frame.pack(pady=20)
        save_button = ctk.CTkButton(
            button_frame,
            text=self.main_app.settings.get_text("save_settings"),
            command=self.save_settings,
            width=120
        )
        save_button.pack(side="left", padx=5)
        cancel_button = ctk.CTkButton(
            button_frame,
            text=self.main_app.settings.get_text("cancel"),
            command=self.window.destroy,
            width=120
        )
        cancel_button.pack(side="left", padx=5)

    def save_settings(self):
        new_settings = {
            "theme": self.theme_var.get(),
            "font_size": int(self.font_size_var.get()),
            "language": self.language_var.get()
        }
        success, message = self.main_app.settings.save_settings(new_settings)
        if success:
            ctk.set_appearance_mode(new_settings["theme"])  # Применяем тему только при сохранении
            self.main_app.apply_settings()  # Перестраиваем UI
            messagebox.showinfo(self.main_app.settings.get_text("success"), message)
            self.window.destroy()
        else:
            messagebox.showerror(self.main_app.settings.get_text("error"), message)


# --- Окно входа/создания ---
class LoginWindow:
    def __init__(self, main_app):
        self.main_app = main_app
        self.window = ctk.CTkToplevel()
        self.window.title(self.main_app.settings.get_text("login_title"))
        self.window.geometry("550x480")
        self.window.resizable(False, False)
        self.window.transient(main_app.root)
        self.window.grab_set()
        self.notepad_filepath = tk.StringVar(value=self.main_app.notepad.filename)
        self.setup_ui()

    def setup_ui(self):
        font_size = self.main_app.settings.settings["font_size"]
        title_label = ctk.CTkLabel(
            self.window,
            text=self.main_app.settings.get_text("app_title"),
            font=ctk.CTkFont(size=font_size + 6, weight="bold")
        )
        title_label.pack(pady=20)

        file_frame = ctk.CTkFrame(self.window)
        file_frame.pack(pady=(10, 5), padx=20, fill="x")
        ctk.CTkLabel(file_frame, text=self.main_app.settings.get_text("file_label"),
                     font=ctk.CTkFont(size=font_size)).pack(side="left", padx=(0, 10))
        self.file_path_entry = ctk.CTkEntry(file_frame, textvariable=self.notepad_filepath, width=250,
                                            font=ctk.CTkFont(size=font_size))
        self.file_path_entry.pack(side="left", fill="x", expand=True)
        self.browse_button = ctk.CTkButton(file_frame, text="...", command=self._browse_file, width=80,
                                           font=ctk.CTkFont(size=font_size))
        self.browse_button.pack(side="right", padx=(10, 0))

        ctk.CTkLabel(self.window, text=self.main_app.settings.get_text("password_label"),
                     font=ctk.CTkFont(size=font_size)).pack(pady=(10, 5))
        self.password_entry = ctk.CTkEntry(self.window, show="*", width=250,
                                           placeholder_text=self.main_app.settings.get_text("password_label"),
                                           font=ctk.CTkFont(size=font_size))
        self.password_entry.pack(pady=5)

        button_frame = ctk.CTkFrame(self.window)
        button_frame.pack(pady=20)
        self.create_button = ctk.CTkButton(button_frame, text=self.main_app.settings.get_text("create_button"),
                                           command=self._create_new_notepad_threaded, width=90,
                                           font=ctk.CTkFont(size=font_size))
        self.create_button.pack(side="left", padx=5)
        self.load_button = ctk.CTkButton(button_frame, text=self.main_app.settings.get_text("load_button"),
                                         command=self._load_notepad_threaded, width=90,
                                         font=ctk.CTkFont(size=font_size))
        self.load_button.pack(side="left", padx=5)

        info_label = ctk.CTkLabel(
            self.window,
            text=self.main_app.settings.get_text("info_text"),
            font=ctk.CTkFont(size=font_size - 3),
            justify="left"
        )
        info_label.pack(pady=10)

        self.password_entry.bind('<Return>', lambda e: self._load_notepad_threaded())
        self.password_entry.focus()

    def _browse_file(self):
        initial_dir = os.path.dirname(self.notepad_filepath.get()) or os.getcwd()
        filepath = filedialog.askopenfilename(
            parent=self.window,
            initialdir=initial_dir,
            title=self.main_app.settings.get_text("file_label"),
            filetypes=[("Encrypted Notepad Files", "*.dat"), ("All Files", "*.*")]
        )
        if filepath and os.path.splitext(filepath)[1].lower() == '.dat':
            self.notepad_filepath.set(filepath)
        elif filepath:
            messagebox.showerror(self.main_app.settings.get_text("error"),
                                 self.main_app.settings.get_text("invalid_file_extension"))

    def _create_new_notepad_threaded(self):
        password = self.password_entry.get()
        if not password:
            messagebox.showerror(self.main_app.settings.get_text("error"),
                                 self.main_app.settings.get_text("password_required"))
            return

        strength_error = _check_password_strength(password)
        if strength_error:
            messagebox.showerror(self.main_app.settings.get_text("error"), strength_error)
            return

        filename = self.notepad_filepath.get()
        if not filename:
            messagebox.showerror(self.main_app.settings.get_text("error"),
                                 self.main_app.settings.get_text("file_required"))
            return
        if not filename.endswith('.dat'):
            filename += '.dat'

        if os.path.exists(filename):
            confirm = messagebox.askyesno(
                self.main_app.settings.get_text("confirm_delete"),
                self.main_app.settings.get_text("file_exists").format(os.path.basename(filename)),
                parent=self.window
            )
            if not confirm:
                return

        self.set_buttons_state("disabled")
        self.main_app.notepad.filename = filename
        threading.Thread(target=self._create_new_notepad_task, args=(password,)).start()

    def _create_new_notepad_task(self, password):
        try:
            success, message = self.main_app.notepad.create_new_notepad(password)
        finally:
            clear_string_memory(password)
        self.main_app.root.after(0, lambda: self._handle_result(success, message))

    def _load_notepad_threaded(self):
        password = self.password_entry.get()
        if not password:
            messagebox.showerror(self.main_app.settings.get_text("error"),
                                 self.main_app.settings.get_text("password_required"))
            return

        filename = self.notepad_filepath.get()
        if not filename:
            messagebox.showerror(self.main_app.settings.get_text("error"),
                                 self.main_app.settings.get_text("file_required"))
            return
        if not os.path.exists(filename):
            messagebox.showerror(self.main_app.settings.get_text("error"),
                                 self.main_app.settings.get_text("file_not_found"))
            return
        if not filename.endswith('.dat'):
            messagebox.showerror(self.main_app.settings.get_text("error"),
                                 self.main_app.settings.get_text("invalid_file_extension"))
            return

        self.set_buttons_state("disabled")
        self.main_app.notepad.filename = filename
        threading.Thread(target=self._load_notepad_task, args=(password,)).start()

    def _load_notepad_task(self, password):
        try:
            success, message = self.main_app.notepad.load_notepad(password)
        finally:
            clear_string_memory(password)
        self.main_app.root.after(0, lambda: self._handle_result(success, message))

    def _handle_result(self, success, message):
        self.set_buttons_state("normal")
        if success:
            messagebox.showinfo(self.main_app.settings.get_text("success"), message)
            self.window.destroy()
            self.main_app.show_main_window()
        else:
            messagebox.showerror(self.main_app.settings.get_text("error"), message)

    def set_buttons_state(self, state):
        self.create_button.configure(state=state)
        self.load_button.configure(state=state)
        self.password_entry.configure(state=state)
        self.browse_button.configure(state=state)
        self.file_path_entry.configure(state=state)


# --- Окно смены пароля ---
class ChangePasswordWindow:
    def __init__(self, main_app):
        self.main_app = main_app
        self.window = ctk.CTkToplevel()
        self.window.title(self.main_app.settings.get_text("change_password"))
        self.window.geometry("600x400")
        self.window.resizable(False, False)
        self.window.transient(main_app.root)
        self.window.grab_set()
        self.setup_ui()

    def setup_ui(self):
        font_size = self.main_app.settings.settings["font_size"]
        title_label = ctk.CTkLabel(
            self.window,
            text=self.main_app.settings.get_text("change_password"),
            font=ctk.CTkFont(size=font_size + 4, weight="bold")
        )
        title_label.pack(pady=20)

        ctk.CTkLabel(self.window, text="Старый пароль:", font=ctk.CTkFont(size=font_size)).pack(pady=(10, 5))
        self.old_password_entry = ctk.CTkEntry(self.window, show="*", width=250, font=ctk.CTkFont(size=font_size))
        self.old_password_entry.pack(pady=5)

        ctk.CTkLabel(self.window, text="Новый пароль:", font=ctk.CTkFont(size=font_size)).pack(pady=(10, 5))
        self.new_password_entry = ctk.CTkEntry(self.window, show="*", width=250, font=ctk.CTkFont(size=font_size))
        self.new_password_entry.pack(pady=5)

        ctk.CTkLabel(self.window, text="Подтвердить новый пароль:", font=ctk.CTkFont(size=font_size)).pack(pady=(10, 5))
        self.confirm_password_entry = ctk.CTkEntry(self.window, show="*", width=250, font=ctk.CTkFont(size=font_size))
        self.confirm_password_entry.pack(pady=5)

        button_frame = ctk.CTkFrame(self.window)
        button_frame.pack(pady=20)
        self.change_button = ctk.CTkButton(
            button_frame,
            text=self.main_app.settings.get_text("save_settings"),
            command=self._change_password_threaded,
            width=120,
            font=ctk.CTkFont(size=font_size)
        )
        self.change_button.pack(side="left", padx=5)
        self.cancel_button = ctk.CTkButton(
            button_frame,
            text=self.main_app.settings.get_text("cancel"),
            command=self.window.destroy,
            width=120,
            font=ctk.CTkFont(size=font_size)
        )
        self.cancel_button.pack(side="left", padx=5)

        self.old_password_entry.focus()

    def _change_password_threaded(self):
        old_password = self.old_password_entry.get()
        new_password = self.new_password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        if not old_password or not new_password or not confirm_password:
            messagebox.showerror(self.main_app.settings.get_text("error"), "All fields must be filled.")
            return

        if new_password != confirm_password:
            messagebox.showerror(self.main_app.settings.get_text("error"),
                                 "New password and confirmation do not match.")
            return

        strength_error = _check_password_strength(new_password)
        if strength_error:
            messagebox.showerror(self.main_app.settings.get_text("error"), strength_error)
            return

        self.set_buttons_state("disabled")
        threading.Thread(target=self._change_password_task, args=(old_password, new_password)).start()

    def _change_password_task(self, old_password, new_password):
        try:
            success, message = self.main_app.notepad.change_password(old_password, new_password)
        finally:
            clear_string_memory(old_password)
            clear_string_memory(new_password)
        self.main_app.root.after(0, lambda: self._handle_result(success, message))

    def _handle_result(self, success, message):
        self.set_buttons_state("normal")
        if success:
            messagebox.showinfo(self.main_app.settings.get_text("success"), message)
            self.window.destroy()
        else:
            messagebox.showerror(self.main_app.settings.get_text("error"), message)

    def set_buttons_state(self, state):
        self.change_button.configure(state=state)
        self.cancel_button.configure(state=state)
        self.old_password_entry.configure(state=state)
        self.new_password_entry.configure(state=state)
        self.confirm_password_entry.configure(state=state)


# --- Окно редактирования записи ---
class NoteEditWindow:
    def __init__(self, main_app, note=None):
        self.main_app = main_app
        self.note = note
        self.window = ctk.CTkToplevel()
        self.window.title("Edit Note" if note else "New Note")
        self.window.geometry("600x500")
        self.window.transient(main_app.root)
        self.window.grab_set()
        self.setup_ui()

    def setup_ui(self):
        font_size = self.main_app.settings.settings["font_size"]
        ctk.CTkLabel(
            self.window,
            text="Title:",
            font=ctk.CTkFont(size=font_size, weight="bold")
        ).pack(pady=(10, 5), anchor="w", padx=20)
        self.title_entry = ctk.CTkEntry(
            self.window,
            width=560,
            placeholder_text="Enter note title",
            font=ctk.CTkFont(size=font_size)
        )
        self.title_entry.pack(pady=(0, 10), padx=20)
        ctk.CTkLabel(
            self.window,
            text="Content:",
            font=ctk.CTkFont(size=font_size, weight="bold")
        ).pack(pady=(10, 5), anchor="w", padx=20)
        self.content_textbox = ctk.CTkTextbox(
            self.window,
            width=560,
            height=300,
            font=ctk.CTkFont(size=font_size)
        )
        self.content_textbox.pack(pady=(0, 10), padx=20)

        if self.note:
            self.title_entry.insert(0, self.note['title'])
            self.content_textbox.insert("1.0", self.note['content'])

        button_frame = ctk.CTkFrame(self.window)
        button_frame.pack(pady=10)
        self.save_button = ctk.CTkButton(
            button_frame,
            text=self.main_app.settings.get_text("save_settings"),
            command=self.save_note,
            width=120,
            font=ctk.CTkFont(size=font_size)
        )
        self.save_button.pack(side="left", padx=5)
        self.cancel_button = ctk.CTkButton(
            button_frame,
            text=self.main_app.settings.get_text("cancel"),
            command=self.window.destroy,
            width=120,
            font=ctk.CTkFont(size=font_size)
        )
        self.cancel_button.pack(side="left", padx=5)

        self.title_entry.focus()

    def save_note(self):
        title = self.title_entry.get().strip()
        content = self.content_textbox.get("1.0", "end-1c").strip()

        if not title:
            messagebox.showerror(self.main_app.settings.get_text("error"), "Enter a title.")
            return
        if not content:
            messagebox.showerror(self.main_app.settings.get_text("error"), "Enter content.")
            return

        if self.note:
            success, message = self.main_app.notepad.edit_note(self.note['id'], title, content)
            if success:
                messagebox.showinfo(self.main_app.settings.get_text("success"), message)
                self.window.destroy()
                self.main_app.refresh_notes_list()
            else:
                messagebox.showerror(self.main_app.settings.get_text("error"), message)
        else:
            success, result = self.main_app.notepad.add_note(title, content)
            if success:
                messagebox.showinfo(self.main_app.settings.get_text("success"), "Note created.")
                self.window.destroy()
                self.main_app.refresh_notes_list()
            else:
                messagebox.showerror(self.main_app.settings.get_text("error"), result)


# --- Основное приложение ---
class EncryptedNotepadApp:
    def __init__(self):
        self.settings = SettingsManager()
        font_size, language = self.settings.apply_settings(None)
        self.notepad = EncryptedNotepad()
        self.root = ctk.CTk()
        self.root.title(self.settings.get_text("app_title"))
        self.root.geometry("800x600")
        self.root.withdraw()
        self.selected_note = None
        self.notes_listbox = None
        self.search_var = None
        self.font_size = font_size
        self.main_frame = None  # Добавляем для управления основным контейнером
        self.show_login()

    def show_login(self):
        LoginWindow(self)

    def show_main_window(self):
        self.root.deiconify()
        self.setup_main_ui()
        self.refresh_notes_list()

    def setup_main_ui(self):
        # Удаляем старый main_frame, если он существует
        if self.main_frame:
            self.main_frame.destroy()

        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True)

        top_frame = ctk.CTkFrame(self.main_frame)
        top_frame.pack(fill="x", padx=10, pady=10)

        search_frame = ctk.CTkFrame(top_frame)
        search_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(search_frame, text="🔍 Search:", font=ctk.CTkFont(size=self.font_size)).pack(side="left", padx=10)
        self.search_var = tk.StringVar()
        self.search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            placeholder_text=self.settings.get_text("search_placeholder"),
            font=ctk.CTkFont(size=self.font_size)
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=10)
        self.search_var.trace("w", lambda *args: self.refresh_notes_list())

        button_frame = ctk.CTkFrame(top_frame)
        button_frame.pack(side="right")
        self.new_button = ctk.CTkButton(
            button_frame,
            text=self.settings.get_text("new_note"),
            command=self.new_note,
            width=120,
            font=ctk.CTkFont(size=self.font_size)
        )
        self.new_button.pack(side="left", padx=5)
        self.save_button = ctk.CTkButton(
            button_frame,
            text=self.settings.get_text("save"),
            command=self.save_notepad,
            width=120,
            font=ctk.CTkFont(size=self.font_size)
        )
        self.save_button.pack(side="left", padx=5)
        self.change_password_button = ctk.CTkButton(
            button_frame,
            text=self.settings.get_text("change_password"),
            command=self.change_password,
            width=140,
            font=ctk.CTkFont(size=self.font_size)
        )
        self.change_password_button.pack(side="left", padx=5)
        self.settings_button = ctk.CTkButton(
            button_frame,
            text=self.settings.get_text("settings"),
            command=self.open_settings,
            width=120,
            font=ctk.CTkFont(size=self.font_size)
        )
        self.settings_button.pack(side="left", padx=5)

        content_frame = ctk.CTkFrame(self.main_frame)
        content_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        left_frame = ctk.CTkFrame(content_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        ctk.CTkLabel(
            left_frame,
            text=self.settings.get_text("notes_label"),
            font=ctk.CTkFont(size=self.font_size + 2, weight="bold")
        ).pack(pady=10)
        self.notes_listbox = tk.Listbox(
            left_frame,
            font=("Arial", self.font_size),
            bg="#212121" if self.settings.settings["theme"] == "dark" else "#f0f0f0",  # Мягкий светлый фон
            fg="white" if self.settings.settings["theme"] == "dark" else "black",
            selectbackground="#1f538d" if self.settings.settings["theme"] == "dark" else "#add8e6",
            selectforeground="white",
            bd=0,
            highlightthickness=0
        )
        self.notes_listbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.notes_listbox.bind('<Double-Button-1>', lambda e: self.view_note())
        self.notes_listbox.bind('<<ListboxSelect>>', self.on_note_select)

        right_frame = ctk.CTkFrame(content_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        self.note_title_label = ctk.CTkLabel(
            right_frame,
            text=self.settings.get_text("select_note"),
            font=ctk.CTkFont(size=self.font_size + 2, weight="bold")
        )
        self.note_title_label.pack(pady=10)
        self.note_info_label = ctk.CTkLabel(
            right_frame,
            text="",
            font=ctk.CTkFont(size=self.font_size + 1)
        )
        self.note_info_label.pack(pady=(0, 10))
        self.note_content_textbox = ctk.CTkTextbox(
            right_frame,
            width=350,
            height=300,
            font=ctk.CTkFont(size=self.font_size)
        )
        self.note_content_textbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.note_content_textbox.configure(state="disabled")

        note_buttons_frame = ctk.CTkFrame(right_frame)
        note_buttons_frame.pack(pady=10)
        self.edit_button = ctk.CTkButton(
            note_buttons_frame,
            text=self.settings.get_text("edit"),
            command=self.edit_note,
            width=110,
            state="disabled",
            font=ctk.CTkFont(size=self.font_size)
        )
        self.edit_button.pack(side="left", padx=5)
        self.delete_button = ctk.CTkButton(
            note_buttons_frame,
            text=self.settings.get_text("delete"),
            command=self.delete_note,
            width=110,
            state="disabled",
            font=ctk.CTkFont(size=self.font_size)
        )
        self.delete_button.pack(side="left", padx=5)

    def open_settings(self):
        SettingsWindow(self)

    def apply_settings(self):
        """Переприменение настроек к главному окну"""
        self.font_size, _ = self.settings.apply_settings(self.root)
        self.root.title(self.settings.get_text("app_title"))
        self.setup_main_ui()  # Перестраиваем UI для применения темы, шрифта и языка
        self.refresh_notes_list()

    def refresh_notes_list(self):
        if not self.notes_listbox:
            return

        self.notes_listbox.delete(0, tk.END)
        search_query = self.search_var.get().lower() if self.search_var else ""
        notes_to_show = self.notepad.search_notes(search_query)

        for note in notes_to_show:
            title = note['title'][:40] + "..." if len(note['title']) > 40 else note['title']
            date = note['modified'][:16]
            display_text = f"{title} ({date})"
            self.notes_listbox.insert(tk.END, display_text)

        count = len(notes_to_show)
        self.root.title(f"{self.settings.get_text('app_title')} - {'Found' if search_query else 'Notes'}: {count}")

        if not notes_to_show and self.selected_note:
            self.selected_note = None
            self.note_title_label.configure(text=self.settings.get_text("select_note"))
            self.note_info_label.configure(text="")
            self.note_content_textbox.configure(state="normal")
            self.note_content_textbox.delete("1.0", tk.END)
            self.note_content_textbox.configure(state="disabled")
            self.edit_button.configure(state="disabled")
            self.delete_button.configure(state="disabled")

    def on_note_select(self, event):
        selection = self.notes_listbox.curselection()
        if not selection:
            self.selected_note = None
            self.note_title_label.configure(text=self.settings.get_text("select_note"))
            self.note_info_label.configure(text="")
            self.note_content_textbox.configure(state="normal")
            self.note_content_textbox.delete("1.0", tk.END)
            self.note_content_textbox.configure(state="disabled")
            self.edit_button.configure(state="disabled")
            self.delete_button.configure(state="disabled")
            return

        index = selection[0]
        search_query = self.search_var.get().lower() if self.search_var else ""
        notes = self.notepad.search_notes(search_query)

        if index < len(notes):
            self.selected_note = notes[index]
            self.display_note(self.selected_note)
            self.edit_button.configure(state="normal")
            self.delete_button.configure(state="normal")
        else:
            self.selected_note = None
            self.note_title_label.configure(text=self.settings.get_text("select_note"))
            self.note_info_label.configure(text="")
            self.note_content_textbox.configure(state="normal")
            self.note_content_textbox.delete("1.0", tk.END)
            self.note_content_textbox.configure(state="disabled")
            self.edit_button.configure(state="disabled")
            self.delete_button.configure(state="disabled")

    def display_note(self, note):
        self.note_title_label.configure(text=note['title'])
        info_text = f"{self.settings.get_text('created')}: {note['created']} | {self.settings.get_text('modified')}: {note['modified']}"
        self.note_info_label.configure(text=info_text)
        self.note_content_textbox.configure(state="normal")
        self.note_content_textbox.delete("1.0", tk.END)
        self.note_content_textbox.insert("1.0", note['content'])
        self.note_content_textbox.configure(state="disabled")

    def new_note(self):
        NoteEditWindow(self)

    def edit_note(self):
        if self.selected_note:
            NoteEditWindow(self, self.selected_note)

    def view_note(self):
        if self.selected_note:
            self.edit_note()

    def delete_note(self):
        if not self.selected_note:
            return

        result = messagebox.askyesno(
            self.settings.get_text("confirm_delete"),
            self.settings.get_text("delete_note_confirm").format(self.selected_note['title'])
        )
        if result:
            success, message = self.notepad.delete_note(self.selected_note['id'])
            if success:
                self.selected_note = None
                self.refresh_notes_list()
                self.note_title_label.configure(text=self.settings.get_text("select_note"))
                self.note_info_label.configure(text="")
                self.note_content_textbox.configure(state="normal")
                self.note_content_textbox.delete("1.0", tk.END)
                self.note_content_textbox.configure(state="disabled")
                self.edit_button.configure(state="disabled")
                self.delete_button.configure(state="disabled")
                messagebox.showinfo(self.settings.get_text("success"), message)
            else:
                messagebox.showerror(self.settings.get_text("error"), message)

    def save_notepad(self):
        def save_thread():
            success, message = self.notepad.save_notepad()
            self.root.after(0, lambda: messagebox.showinfo(self.settings.get_text("save_result"), message))
        threading.Thread(target=save_thread, daemon=True).start()

    def change_password(self):
        ChangePasswordWindow(self)

    def run(self):
        """Запуск основного цикла приложения"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_closing(self):
        result = messagebox.askyesnocancel(
            self.settings.get_text("close_confirm"),
            self.settings.get_text("save_before_exit")
        )
        if result is True:
            success, message = self.notepad.save_notepad()
            if success:
                self.root.destroy()
            else:
                messagebox.showerror(self.settings.get_text("save_error"), message)
        elif result is False:
            self.root.destroy()


if __name__ == "__main__":
    app = EncryptedNotepadApp()
    app.run()