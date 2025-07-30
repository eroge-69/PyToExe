import webbrowser
from cryptography.fernet import Fernet
import wmi
import discord
import asyncio
import re
from datetime import datetime, timedelta
import pyperclip
import keyboard
from typing import Optional
import tkinter as tk
from tkinter import filedialog
from CTkMessagebox import CTkMessagebox
import customtkinter as ctk
import os
import threading
import json
import requests
import base64
import uuid

# Зашифрованный GitHub токен и ключ шифрования
ENCRYPTED_GITHUB_TOKEN = b'gAAAAABoiO09Ht7PujJlR30aUF_2lGIFexVfBM5KNafIJhpKcdJgPCMv3B0oRFp-PeBfcF2D0iBr4G7jsP2BKaftR0_6lyQ88cL_H4VFMVxsrE-xwiOc_oJonNKbhHhRVFnds21VTEGH'
CIPHER_KEY = b'aik3RFkl8UD56AylSWnbGC77VajVBOgzRUvEn1So6kg='
cipher = Fernet(CIPHER_KEY)
GITHUB_TOKEN = cipher.decrypt(ENCRYPTED_GITHUB_TOKEN).decode('utf-8')

# GitHub настройки
REPO_OWNER = "clipse0e"
REPO_NAME = "keysconnect"
FILE_PATH = "keys.txt"
API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

USER_TOKEN = ""
CHANNEL_IDS = {
    "under 500k": 1394958052536619059,
    "500k to 1m": 1394958062166474823,
    "1m to 10m": 1394958060828627064,
}
WORKSPACE_FOLDER = r"C:\Users\Кабан\AppData\Roaming\Swift\Workspace"
OUTPUT_FILE = os.path.join(WORKSPACE_FOLDER, "copy.txt")
AUTOEXEC_FOLDER = r"C:\Users\Кабан\AppData\Roaming\Swift\Workspace"
CONFIG_FILE = "config.json"
METAL_JSON = "metal.json"
CHANNEL_ID = CHANNEL_IDS["1m to 10m"]  # Initialize with default value


def get_hwid():
    c = wmi.WMI()
    disk = c.Win32_DiskDrive()[0].SerialNumber
    return f"{uuid.getnode()}_{disk}"

class SelfBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_message_id: Optional[int] = None
        self.running: bool = True
        self.paused: bool = False
        self.channel: Optional[discord.TextChannel] = None
        self.gui = kwargs.get('gui')

    async def on_ready(self):
        self.channel = self.get_channel(CHANNEL_ID)
        if not self.channel:
            self.gui.log_message("Канал не найден", "red")
            return
        self.gui.log_message(f"Подключено к {self.channel.name}", "green")
        await self.monitor_channel()

    async def on_message(self, message: discord.Message):
        if (self.paused or
                message.channel.id != CHANNEL_ID or
                message.id == self.last_message_id or
                not message.embeds):
            return

        self.last_message_id = message.id
        job_id_pc = next((field['value'] for field in message.embeds[0].to_dict().get('fields', [])
                         if field['name'] == '🆔 Job ID (PC)'), None)
        if job_id_pc:
            # Очищаем значение, удаляя обрамляющие символы ``` и пробелы
            job_id_clean = job_id_pc.strip('`').strip()
            # Проверяем, является ли значение валидным UUID
            uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
            if re.match(uuid_pattern, job_id_clean, re.IGNORECASE):
                with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                    f.write(job_id_clean)
                channel_name = self.channel.name if self.channel else "Неизвестный канал"
                current_time = datetime.now().strftime("%H:%M:%S")
                self.gui.log_message(f"[{current_time}] connected_{channel_name} (Job ID: {job_id_clean})", "green")
            else:
                self.gui.log_message(f"[{datetime.now().strftime('%H:%M:%S')}] Неверный формат Job ID: {job_id_clean}", "red")

    async def monitor_channel(self):
        def toggle_pause(_):
            if self.gui:
                self.gui.toggle_pause()

        keyboard.on_release_key("f1", toggle_pause)

        while self.running:
            await asyncio.sleep(0.1)

    async def close(self):
        self.running = False
        await super().close()

class AutoJoinerGUI:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        self.root = ctk.CTk()
        self.root.title("AutoJoiner Key Verification")
        self.root.geometry("400x200")
        self.root.resizable(False, False)
        self.keys = {}  # key: (duration_value, duration_type, expiration_datetime if activated, hwid if activated)
        self.active_key = None
        self.active_key_expiration = None
        self.load_config()
        self.ensure_metal_theme(silent=True)
        ctk.set_default_color_theme(METAL_JSON)
        self.load_keys_from_github()
        now = datetime.now()
        if self.active_key:
            self.check_and_handle_active_key(now)
        if self.active_key_expiration and now < self.active_key_expiration:
            self.root.title("AutoJoiner Control Panel")
            self.root.geometry("620x405")
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.setup_gui()
            self.update_folder_display()
            self.check_key_expiration()
        else:
            self.setup_key_verification_gui()

    def get_github_file(self):
        response = requests.get(API_URL, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            content = base64.b64decode(data['content']).decode('utf-8')
            sha = data['sha']
            return content, sha
        else:
            self.log_message(f"Ошибка загрузки с GitHub: {response.status_code} - {response.text}", "red")
            return None, None

    def update_github_file(self, new_content, sha):
        data = {
            "message": "Update keys.txt",
            "content": base64.b64encode(new_content.encode('utf-8')).decode('utf-8'),
            "sha": sha
        }
        response = requests.put(API_URL, headers=HEADERS, json=data)
        if response.status_code != 200:
            self.log_message(f"Ошибка обновления GitHub: {response.status_code} - {response.text}", "red")
        return response.status_code == 200

    def load_keys_from_github(self):
        content, _ = self.get_github_file()
        if content:
            lines = content.split('\n')
            now = datetime.now()
            self.keys = {}
            for line in lines:
                if not line.strip():
                    continue
                parts = [p.strip() for p in line.split('|')]
                if len(parts) < 2:
                    continue
                key = parts[0]
                duration_part = parts[1]
                duration_match = re.search(r'Duration: (\d+) (minutes|hours|days)', duration_part)
                if not duration_match:
                    continue
                duration_value = int(duration_match.group(1))
                duration_type = duration_match.group(2)
                expiration_dt = None
                hwid = None
                if len(parts) > 2 and 'Expire date:' in parts[2]:
                    expire_match = re.search(r'Expire date: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', parts[2])
                    if expire_match:
                        expiration_dt = datetime.strptime(expire_match.group(1), "%Y-%m-%d %H:%M:%S")
                if len(parts) > 3 and 'HWID:' in parts[3]:
                    hwid_match = re.search(r'HWID: (\w+)', parts[3])
                    if hwid_match:
                        hwid = hwid_match.group(1)
                self.keys[key] = (duration_value, duration_type, expiration_dt, hwid)

    def activate_key(self, key):
        content, sha = self.get_github_file()
        if content:
            lines = content.split('\n')
            new_lines = []
            current_hwid = get_hwid()
            for line in lines:
                if line.strip().startswith(key):
                    parts = [p.strip() for p in line.split('|')]
                    if len(parts) < 3 or 'Expire date:' not in parts[2]:
                        duration_part = parts[1]
                        duration_match = re.search(r'Duration: (\d+) (minutes|hours|days)', duration_part)
                        if duration_match:
                            duration_value = int(duration_match.group(1))
                            duration_type = duration_match.group(2)
                            activation = datetime.now()
                            if duration_type == 'minutes':
                                expires = activation + timedelta(minutes=duration_value)
                            elif duration_type == 'hours':
                                expires = activation + timedelta(hours=duration_value)
                            else:
                                expires = activation + timedelta(days=duration_value)
                            line += f" | Expire date: {expires.strftime('%Y-%m-%d %H:%M:%S')} | HWID: {current_hwid}"
                    else:
                        if len(parts) < 4 or 'HWID:' not in parts[3]:
                            line += f" | HWID: {current_hwid}"
                    new_lines.append(line)
                else:
                    new_lines.append(line)
            new_content = '\n'.join(new_lines)
            self.update_github_file(new_content, sha)

    def remove_key_from_github(self, key):
        content, sha = self.get_github_file()
        if content:
            lines = content.split('\n')
            new_lines = [line for line in lines if not line.strip().startswith(key)]
            new_content = '\n'.join(new_lines)
            self.update_github_file(new_content, sha)

    def check_and_handle_active_key(self, now):
        self.load_keys_from_github()
        if self.active_key in self.keys:
            _, _, expiration_dt, _ = self.keys[self.active_key]
            if expiration_dt:
                self.active_key_expiration = expiration_dt
                if now > expiration_dt:
                    self.remove_key_from_github(self.active_key)
                    self.active_key = None
                    self.save_config()
                    self.expire_key()
                else:
                    pass
            else:
                self.active_key = None
                self.save_config()
                self.expire_key()
        else:
            self.active_key = None
            self.save_config()
            self.expire_key()

    def ensure_metal_theme(self, silent=False):
        if not os.path.exists(METAL_JSON):
            url = "https://raw.githubusercontent.com/a13xe/CTkThemesPack/refs/heads/main/themes/metal.json"
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    with open(METAL_JSON, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    if not silent:
                        self.log_message("Тема metal.json успешно загружена из интернета.", "green")
                else:
                    if not silent:
                        self.log_message(f"Не удалось загрузить тему. Код: {response.status_code}", "red")
            except Exception as e:
                if not silent:
                    self.log_message(f"Ошибка загрузки темы: {e}", "red")

    def setup_key_verification_gui(self):
        self.verification_frame = ctk.CTkFrame(self.root, fg_color="#2b2b2b", corner_radius=10)
        self.verification_frame.pack(padx=10, pady=10, fill="both", expand=True)

        ctk.CTkLabel(self.verification_frame, text="Введите ваш ключ:", font=("Segoe UI", 16)).pack(pady=(20, 5))
        
        self.key_entry = ctk.CTkEntry(self.verification_frame, width=300, show="*")
        self.key_entry.pack(pady=10)
        self.key_entry.bind("<Return>", lambda event: self.verify_key())

        ctk.CTkButton(self.verification_frame, text="Подтвердить", command=self.verify_key,
                     fg_color="#4a4a4a", hover_color="#5a5a5a", text_color="white").pack(pady=10)

        # Добавляем кнопки для покупки ключей
        button_frame = ctk.CTkFrame(self.verification_frame, fg_color="#2b2b2b")
        button_frame.pack(pady=5)
        
        ctk.CTkButton(button_frame, text="Купить 1d", command=lambda: webbrowser.open("https://funpay.com/lots/offer?id=45625471"),
                     fg_color="#4a4a4a", hover_color="#5a5a5a", text_color="#00bfff", width=80).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Купить 7d", command=lambda: webbrowser.open("https://funpay.com/lots/offer?id=45967457"),
                     fg_color="#4a4a4a", hover_color="#5a5a5a", text_color="#00bfff", width=80).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Купить 14d", command=lambda: webbrowser.open("https://funpay.com/lots/offer?id=45643676"),
                     fg_color="#4a4a4a", hover_color="#5a5a5a", text_color="#00bfff", width=80).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Купить 30d", command=lambda: webbrowser.open("https://funpay.com/lots/offer?id=45966511"),
                     fg_color="#4a4a4a", hover_color="#5a5a5a", text_color="#00bfff", width=80).pack(side="left", padx=5)

    def verify_key(self):
        key = self.key_entry.get().strip()
        now = datetime.now()
        self.load_keys_from_github()
        if key in self.keys:
            _, _, expiration_dt, stored_hwid = self.keys[key]
            current_hwid = get_hwid()
            if stored_hwid and stored_hwid != current_hwid:
                CTkMessagebox(title="Ошибка", message="Неправильный HWID!", icon="cancel")
                return
            if expiration_dt is None or stored_hwid is None:
                self.activate_key(key)
                self.load_keys_from_github()
                _, _, expiration_dt, stored_hwid = self.keys[key]
            self.active_key = key
            self.active_key_expiration = expiration_dt
            if now > expiration_dt:
                self.remove_key_from_github(key)
                CTkMessagebox(title="Ошибка", message="Ключ истёк!", icon="cancel")
                return
            self.save_config()
            self.verification_frame.pack_forget()
            self.root.title("AutoJoiner Control Panel")
            self.root.geometry("620x405")
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.setup_gui()
            self.update_folder_display()
            self.check_key_expiration()
        else:
            CTkMessagebox(title="Ошибка", message="Неверный ключ!", icon="cancel")

    def check_key_expiration(self):
        now = datetime.now()
        if self.active_key_expiration and now > self.active_key_expiration:
            self.expire_key()
        else:
            self.root.after(60000, self.check_key_expiration)  # Check every 60 seconds

    def expire_key(self):
        if self.client and self.client.running:
            self.toggle_start_stop()
        if self.active_key:
            self.remove_key_from_github(self.active_key)
        self.active_key = None
        self.active_key_expiration = None
        self.save_config()
        self.main_frame.grid_forget()
        self.root.title("AutoJoiner Key Verification")
        self.root.geometry("400x200")
        self.setup_key_verification_gui()

    def load_config(self):
        global CHANNEL_ID, USER_TOKEN, OUTPUT_FILE
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.workspace_folder = config.get('workspace_folder', WORKSPACE_FOLDER)
                self.autoexec_folder = config.get('autoexec_folder', AUTOEXEC_FOLDER)
                self.selected_channel = config.get('selected_channel', "1m to 10m")
                if self.selected_channel == "10m plus":
                    self.selected_channel = "1m to 10m"
                CHANNEL_ID = CHANNEL_IDS[self.selected_channel]
                USER_TOKEN = config.get('user_token', "")
                OUTPUT_FILE = os.path.join(self.workspace_folder, "copy.txt")
                self.active_key = config.get('active_key', None)
        else:
            self.workspace_folder = WORKSPACE_FOLDER
            self.autoexec_folder = AUTOEXEC_FOLDER
            self.selected_channel = "1m to 10m"
            CHANNEL_ID = CHANNEL_IDS[self.selected_channel]
            self.active_key = None

    def save_config(self):
        config = {
            'workspace_folder': self.workspace_folder,
            'autoexec_folder': self.autoexec_folder,
            'selected_channel': self.selected_channel,
            'user_token': USER_TOKEN,
            'active_key': self.active_key
        }
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)

    def on_closing(self):
        self.save_config()
        if self.client and self.client.running:
            self.client.loop.create_task(self.client.close())
            if self.client_thread and self.client_thread.is_alive():
                self.client_thread.join(timeout=2.0)
        self.root.destroy()

    def setup_gui(self):
        self.main_frame = ctk.CTkFrame(self.root, fg_color="#2b2b2b", corner_radius=10)
        self.main_frame.grid(row=0, column=0, padx=10, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=0)
        self.main_frame.rowconfigure(1, weight=0)
        self.main_frame.rowconfigure(2, weight=0)
        self.main_frame.rowconfigure(3, weight=1)
        self.main_frame.rowconfigure(4, weight=0)

        ctk.CTkLabel(self.main_frame, text="AutoJoiner Control Panel", font=("Segoe UI", 25, "bold")).grid(row=0, column=0, columnspan=3, pady=(0, 5), sticky="w", padx=(5, 0))

        ctk.CTkLabel(self.main_frame, text="Токен пользователя:", font=("Segoe UI", 15)).grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.token_entry = ctk.CTkEntry(self.main_frame, width=200, show="*")
        self.token_entry.place(x=155, y=44)
        self.token_entry.insert(0, USER_TOKEN)

        self.token_entry.bind("<Control-a>", self.select_all)
        self.token_entry.bind("<Control-c>", self.copy)
        self.token_entry.bind("<Control-v>", self.paste)

        expire_label = ctk.CTkLabel(self.main_frame, text=f"Expire date: {self.active_key_expiration.strftime('%Y-%m-%d %H:%M:%S')}", text_color="green", font=("Segoe UI", 16, "bold"))
        expire_label.place(x=340, y=5)

        button_frame = ctk.CTkFrame(self.main_frame, fg_color="#2b2b2b")
        button_frame.grid(row=2, column=0, columnspan=3, pady=5, sticky=tk.W)
        button_frame.columnconfigure((0, 1, 2, 3, 4), weight=0)
        button_frame.rowconfigure((0, 1), weight=0)

        ctk.CTkButton(button_frame, text="Папка Autoexec", command=self.select_autoexec_folder, corner_radius=10, fg_color="#4a4a4a").grid(row=0, column=0, padx=5, pady=5)
        ctk.CTkButton(button_frame, text="Папка Workspace", command=self.select_workspace_folder, corner_radius=10, fg_color="#4a4a4a").grid(row=1, column=0, padx=5, pady=5)

        ctk.CTkButton(button_frame, text="Создать", command=self.create_files, corner_radius=10, fg_color="#4a4a4a").grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(button_frame, text="Выберите канал:").grid(row=0, column=2, padx=5, pady=5)
        self.channel_var = tk.StringVar(value=self.selected_channel)
        channel_options = list(CHANNEL_IDS.keys())
        self.channel_menu = ctk.CTkOptionMenu(button_frame, variable=self.channel_var, values=channel_options, command=self.update_channel, fg_color="#4a4a4a", button_color="#3c3c3c")
        self.channel_menu.grid(row=0, column=3, padx=5, pady=5)

        self.start_stop_button = ctk.CTkButton(button_frame, text="Старт", command=self.toggle_start_stop, corner_radius=10, fg_color="#28a745", text_color="black")
        self.start_stop_button.grid(row=1, column=1, padx=5, pady=5)

        self.pause_button = ctk.CTkButton(button_frame, text="Пауза", command=self.toggle_pause, corner_radius=10, fg_color="#ff8c00", text_color="black", state="disabled")
        self.pause_button.grid(row=1, column=2, padx=5, pady=5)

        self.log_text = ctk.CTkTextbox(self.main_frame, fg_color="#1e1e1e", text_color="white", font=("Consolas", 11), corner_radius=10, border_width=1, state="disabled")
        self.log_text.grid(row=3, column=0, columnspan=3, padx=10, pady=(10), sticky=(tk.W, tk.E, tk.N, tk.S))

        self.log_text.tag_config("red", foreground="red")
        self.log_text.tag_config("green", foreground="green")
        self.log_text.tag_config("yellow", foreground="yellow")
        self.log_text.tag_config("white", foreground="white")
        self.log_text.tag_config("orange", foreground="#ff8c00")

        self.client = None
        self.client_thread = None
        self.is_stopping = False

    def log_message(self, message, color):
        if hasattr(self, 'log_text'):
            self.log_text.configure(state="normal")
            self.log_text.insert("end", f"{message}\n", color)
            self.log_text.see("end")
            self.log_text.configure(state="disabled")

    def select_all(self, event):
        self.token_entry.select_range(0, tk.END)
        return "break"

    def copy(self, event):
        selected_text = self.token_entry.get()[self.token_entry.index(tk.SEL_FIRST):self.token_entry.index(tk.SEL_LAST)]
        if selected_text:
            pyperclip.copy(selected_text)
        return "break"

    def paste(self, event):
        clipboard_text = pyperclip.paste()
        if clipboard_text:
            self.token_entry.delete(0, tk.END)
            self.token_entry.insert(0, clipboard_text)
        return "break"

    def toggle_start_stop(self):
        global USER_TOKEN
        USER_TOKEN = self.token_entry.get()
        
        if not USER_TOKEN:
            self.log_message("Введите действительный токен пользователя!", "red")
            return

        if self.start_stop_button.cget("text") == "Старт":
            if self.client and self.client_thread and self.client_thread.is_alive():
                self.log_message("Останавливаю старую сессию...", "yellow")
                self.client.running = False
                self.client.loop.create_task(self.client.close())
                self.client_thread.join(timeout=2.0)
                self.client = None

            self.client = SelfBot(gui=self)
            self.client_thread = threading.Thread(target=self.run_client)
            self.client_thread.start()
            self.log_message("Скрипт запущен!", "white")
            self.start_stop_button.configure(text="Стоп", fg_color="#ff0000")
            self.pause_button.configure(state="normal")
            self.update_pause_button()

        else:
            if self.client and self.client.running and not self.is_stopping:
                self.is_stopping = True
                self.log_message("Останавливаю скрипт...", "yellow")
                self.client.running = False
                self.client.loop.create_task(self.client.close())
                self.root.after(100, self.check_thread_stop)

    def check_thread_stop(self):
        if self.client_thread and self.client_thread.is_alive():
            self.client_thread.join(timeout=0.1)
            self.root.after(100, self.check_thread_stop)
        else:
            self.client = None
            self.client_thread = None
            self.start_stop_button.configure(text="Старт", fg_color="#28a745")
            self.pause_button.configure(state="disabled")
            self.log_message(f"[{datetime.now().strftime('%H:%M:%S')}] СКРИПТ ОСТАНОВЛЕН", "red")
            self.update_pause_button(reset=True)
            self.is_stopping = False

    def update_pause_button(self, reset=False):
        if reset or not self.client or not self.client.running:
            self.pause_button.configure(text="Пауза", fg_color="#ff8c00", state="disabled")
        elif self.client.paused:
            self.pause_button.configure(text="Возобновить", fg_color="#cc7000")
        else:
            self.pause_button.configure(text="Пауза", fg_color="#ff8c00")

    def select_autoexec_folder(self):
        folder = filedialog.askdirectory(title="Выберите папку Autoexec")
        if folder:
            self.autoexec_folder = folder
            self.log_message(f"Папка Autoexec выбрана: {self.autoexec_folder}", "white")

    def select_workspace_folder(self):
        folder = filedialog.askdirectory(title="Выберите папку Workspace")
        if folder:
            self.workspace_folder = folder
            self.log_message(f"Папка Workspace выбрана: {self.workspace_folder}", "white")
            global OUTPUT_FILE
            OUTPUT_FILE = os.path.join(self.workspace_folder, "copy.txt")

    def update_folder_display(self):
        self.log_message(f"Папка Autoexec (из конфигурации): {self.autoexec_folder}", "white")
        self.log_message(f"Папка Workspace (из конфигурации): {self.workspace_folder}", "white")

    def create_files(self):
        if not self.workspace_folder or not self.autoexec_folder:
            self.log_message("Сначала выберите папки Workspace и Autoexec!", "red")
            return
        lua_file_path = os.path.join(self.autoexec_folder, "AutoJoiner.lua")  # Используем autoexec_folder для Lua
        copy_file_path = os.path.join(self.workspace_folder, "copy.txt")  # Используем workspace_folder для copy.txt

        lua_content = """loadstring(game:HttpGet("https://gist.githubusercontent.com/clipse0e/29511b21de97dc090c5e61ddd578546d/raw/8d787c99ea7ba2cae11d5f24c990667fa25add49/obf_VU9TY2238I45ZrPB72h1WCg37Zb91E9oEdk651ljx8t1teoJ9MnSB73Bo2fGC09A.lua"))()"""

        created = False
        try:
            if not os.path.exists(lua_file_path):
                with open(lua_file_path, 'w', encoding='utf-8') as f:
                    f.write(lua_content)
                self.log_message(f"AutoJoiner.lua создан в: {lua_file_path}", "white")
                created = True
            else:
                self.log_message(f"AutoJoiner.lua уже существует в: {lua_file_path}", "yellow")

            if not os.path.exists(copy_file_path):
                with open(copy_file_path, 'w', encoding='utf-8') as f:
                    f.write("")
                self.log_message(f"copy.txt создан в: {copy_file_path}", "white")
                created = True
            else:
                self.log_message(f"copy.txt уже существует в: {copy_file_path}", "yellow")

            if not created:
                self.log_message("Файлы не созданы; оба уже существуют.", "yellow")
        except Exception as e:
            self.log_message(f"Ошибка создания файлов: {str(e)}", "red")

    def update_channel(self, channel):
        global CHANNEL_ID
        self.selected_channel = channel
        CHANNEL_ID = CHANNEL_IDS[channel]
        self.log_message(f"Выбран канал: {channel} (ID: {CHANNEL_ID})", "white")
        if self.client and self.client.running:
            self.log_message("Чтобы переключить канал, сначала остановите скрипт.", "yellow")

    def toggle_pause(self):
        if self.client and self.client.running:
            self.client.paused = not self.client.paused
            status = "ПРИОСТАНОВЛЕН" if self.client.paused else "ВОЗОБНОВЛЕН"
            self.log_message(f"[{datetime.now().strftime('%H:%M:%S')}] СКРИПТ {status}", "orange")
            self.update_pause_button()
        else:
            self.log_message("Скрипт не запущен, пауза недоступна!", "yellow")

    def run_client(self):
        try:
            asyncio.run(self.client.run(USER_TOKEN))
        except Exception as e:
            self.log_message(f"Ошибка запуска клиента: {e}", "red")
            if self.start_stop_button:
                self.start_stop_button.configure(text="Старт", fg_color="#28a745")
                self.pause_button.configure(state="disabled")
            self.update_pause_button(reset=True)

    def run(self):
        self.root.mainloop()

def main():
    gui = AutoJoinerGUI()
    gui.run()

if __name__ == "__main__":
    main()

# Инструкции для обфускации и создания EXE:
# 1. Установите PyArmor:
#    pip install pyarmor
# 2. Обфусцируйте скрипт:
#    pyarmor obfuscate --restrict 2 autojoiner.py
# 3. Создайте EXE с PyInstaller:
#    pyinstaller --onefile dist/autojoiner.py
# 4. Для дополнительной защиты используйте --encrypt в PyArmor (требуется лицензия):
#    pyarmor obfuscate --encrypt autojoiner.py