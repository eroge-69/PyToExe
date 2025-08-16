#!/usr/bin/env python3
"""
Minecraft Server Manager 4.0 - Полная версия с интерфейсом и всем функционалом
"""
import os
import sys
import json
import time
import webbrowser
import subprocess
import threading
import pyperclip
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext, simpledialog
from pathlib import Path
import requests
import re
from datetime import datetime
import shutil
import zipfile
import base64
import io
from PIL import Image, ImageTk
import platform

# Попытка импорта psutil для мониторинга ресурсов (не обязательно)
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("Модуль 'psutil' не найден. Мониторинг ресурсов будет ограничен.")

# --- Цветовая схема ---
COLORS = {
    "primary": "#4a90e2",
    "primary-dark": "#357abd",
    "success": "#5cb85c",
    "danger": "#d9534f",
    "warning": "#f0ad4e",
    "info": "#5bc0de",
    "dark": "#2c3e50",
    "light": "#ecf0f1",
    "background": "#f5f7fa",
    "card": "#ffffff",
    "border": "#d1d8e0"
}

# --- Фиктивные данные для плагинов ---
PLUGINS_DB = [
    {"name": "EssentialsX", "version": "2.19.7", "downloads": "5,000,000+", "rating": "4.8/5.0",
     "compatible": "1.16.5 - 1.20.1", "description": "Базовый набор команд и функций для сервера",
     "url": "https://www.spigotmc.org/resources/essentialsx.9089/", "features": ["Телепортация", "Экономика", "Дома"], "dependencies": ["Vault"]},
    {"name": "WorldEdit", "version": "7.2.10", "downloads": "5,200,000+", "rating": "4.9/5.0",
     "compatible": "1.16.5 - 1.20.1", "description": "Мощный инструмент для редактирования мира",
     "url": "https://enginehub.org/worldedit/", "features": ["Редактирование блоков", "Схемы"], "dependencies": []},
    {"name": "Vault", "version": "1.7.3", "downloads": "10,000,000+", "rating": "4.7/5.0",
     "compatible": "1.16.5 - 1.20.1", "description": "API для экономики, чат-менеджеров и пермишенов",
     "url": "https://www.spigotmc.org/resources/vault.34315/", "features": ["API"], "dependencies": []},
    {"name": "LuckPerms", "version": "5.4.20", "downloads": "8,000,000+", "rating": "4.9/5.0",
     "compatible": "1.16.5 - 1.20.1", "description": "Продвинутый плагин управления правами",
     "url": "https://luckperms.net/", "features": ["Группы", "Права", "Контексты"], "dependencies": []},
    {"name": "Multiverse-Core", "version": "4.3.1", "downloads": "3,500,000+", "rating": "4.6/5.0",
     "compatible": "1.16.5 - 1.20.1", "description": "Создание и управление несколькими мирами",
     "url": "https://dev.bukkit.org/projects/multiverse-core", "features": ["Миры", "Порталы"], "dependencies": []},
]

# --- Фиктивные данные для задач планировщика ---
TASKS_DB = [
    {"time": "04:00", "task": "stop", "enabled": True},
    {"time": "04:05", "task": "start", "enabled": True},
    {"time": "12:00", "task": "say Дневной бэкап сервера", "enabled": False},
    {"time": "12:01", "task": "save-all", "enabled": False},
]

# --- Сопоставление версий Minecraft и Java ---
JAVA_VERSIONS_FOR_MINECRAFT = {
    "1.20.1": "17",  # 1.20.1 и выше требуют Java 17+
    "1.20": "17",
    "1.19.4": "17",
    "1.19.3": "17",
    "1.19.2": "17",
    "1.19.1": "17",
    "1.19": "17",
    "1.18.2": "17",
    "1.18.1": "17",
    "1.18": "17",
    "1.17.1": "17",
    "1.17": "17",
    "1.16.5": "8",   # 1.16.5 и ниже требуют Java 8
    "1.16.4": "8",
    "1.16.3": "8",
    "1.16.2": "8",
    "1.16.1": "8",
    "1.16": "8",
    "1.15.2": "8",
    "1.15.1": "8",
    "1.15": "8",
    "1.14.4": "8",
    "1.14.3": "8",
    "1.14.2": "8",
    "1.14.1": "8",
    "1.14": "8",
    "1.13.2": "8",
    "1.13.1": "8",
    "1.13": "8",
    "1.12.2": "8",
    "1.12.1": "8",
    "1.12": "8",
    "1.11.2": "8",
    "1.11.1": "8",
    "1.11": "8",
    "1.10.2": "8",
    "1.10.1": "8",
    "1.10": "8",
    "1.9.4": "8",
    "1.9.3": "8",
    "1.9.2": "8",
    "1.9.1": "8",
    "1.9": "8",
    "1.8.9": "8",
    "1.8.8": "8",
    "1.8.7": "8",
    "1.8.6": "8",
    "1.8.5": "8",
    "1.8.4": "8",
    "1.8.3": "8",
    "1.8.2": "8",
    "1.8.1": "8",
    "1.8": "8",
    "1.7.10": "8",
    "1.7.9": "8",
    "1.7.8": "8",
    "1.7.7": "8",
    "1.7.6": "8",
    "1.7.5": "8",
    "1.7.4": "8",
    "1.7.3": "8",
    "1.7.2": "8",
    "1.7.1": "8",
    "1.7": "8",
    "1.6.4": "8",
    "1.6.3": "8",
    "1.6.2": "8",
    "1.6.1": "8",
    "1.6": "8",
    "1.5.2": "8",
    "1.5.1": "8",
    "1.5": "8",
    "1.4.7": "8",
    "1.4.6": "8",
    "1.4.5": "8",
    "1.4.4": "8",
    "1.4.3": "8",
    "1.4.2": "8",
    "1.4.1": "8",
    "1.4": "8",
    "1.3.2": "8",
    "1.3.1": "8",
    "1.3": "8",
    "1.2.5": "8",
    "1.2.4": "8",
    "1.2.3": "8",
    "1.2.2": "8",
    "1.2.1": "8",
    "1.2": "8",
    "1.1": "8",
    "1.0": "8",
}

# --- Основной класс приложения ---
class MinecraftServerManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Minecraft Server Manager 4.0")
        self.root.geometry("1200x800")
        self.root.configure(bg=COLORS["background"])
        self.server_process = None
        self.logs = []
        self.minecraft_versions = []
        self.forge_versions = {}
        self.paper_versions = {}
        self.fabric_versions = {}
        self.java_versions = ["8", "11", "17", "21"] # Поддерживаемые версии Java
        self.java_paths = {} # Пути к разным версиям Java
        self.is_running = False
        self.online_players = []

        self.setup_variables()
        self.setup_styles()
        self.create_widgets()
        self.load_versions() # Загружаем версии при запуске
        self.update_server_types()
        self.check_java()
        self.refresh_diagnostics()

    def setup_variables(self):
        self.server_path = tk.StringVar(value=os.getcwd())
        self.minecraft_version = tk.StringVar(value="")
        self.server_type = tk.StringVar(value="Paper")
        self.memory = tk.StringVar(value="4")
        self.status_var = tk.StringVar(value="Сервер остановлен")
        self.selected_plugin = tk.StringVar()
        self.selected_task = tk.StringVar()
        self.java_version = tk.StringVar(value="17") # По умолчанию Java 17
        # Для настроек сервера
        self.server_properties = {}

    def setup_styles(self):
        style = ttk.Style()
        style.configure("Primary.TButton", background=COLORS["primary"], foreground="white")
        style.map("Primary.TButton", background=[('active', COLORS["primary-dark"])])
        style.configure("Success.TButton", background=COLORS["success"], foreground="white")
        style.map("Success.TButton", background=[('active', '#449d44')])
        style.configure("Danger.TButton", background=COLORS["danger"], foreground="white")
        style.map("Danger.TButton", background=[('active', '#c9302c')])
        style.configure("Warning.TLabel", foreground=COLORS["warning"])
        style.configure("Success.TLabel", foreground=COLORS["success"])
        style.configure("Danger.TLabel", foreground=COLORS["danger"])
        style.configure("Info.TLabel", foreground=COLORS["info"])

    def create_widgets(self):
        # --- Верхняя панель ---
        top_frame = tk.Frame(self.root, bg=COLORS["dark"], height=60)
        top_frame.pack(fill="x")
        top_frame.pack_propagate(False)

        title_label = tk.Label(top_frame, text="🎮 Minecraft Server Manager 4.0", font=("Arial", 16, "bold"),
                               fg=COLORS["light"], bg=COLORS["dark"])
        title_label.pack(side="left", padx=20, pady=10)

        status_label = tk.Label(top_frame, textvariable=self.status_var, font=("Arial", 10),
                                fg=COLORS["warning"], bg=COLORS["dark"])
        status_label.pack(side="right", padx=20, pady=10)

        # --- Основной контейнер ---
        main_paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg=COLORS["background"], sashwidth=5)
        main_paned.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Левая панель (Настройки) ---
        settings_frame = tk.Frame(main_paned, bg=COLORS["card"], relief="raised", bd=1)
        main_paned.add(settings_frame)

        # --- Путь к серверу ---
        path_frame = tk.Frame(settings_frame, bg=COLORS["card"])
        path_frame.pack(fill="x", padx=15, pady=10)
        tk.Label(path_frame, text="📁 Путь к серверу:", bg=COLORS["card"], font=("Arial", 10, "bold")).pack(anchor="w")
        path_entry_frame = tk.Frame(path_frame, bg=COLORS["card"])
        path_entry_frame.pack(fill="x", pady=5)
        tk.Entry(path_entry_frame, textvariable=self.server_path, state="readonly").pack(side="left", fill="x", expand=True)
        tk.Button(path_entry_frame, text="Обзор", command=self.browse_path, bg=COLORS["primary"], fg="white").pack(side="right", padx=(5, 0))

        # --- Версия Minecraft ---
        version_frame = tk.Frame(settings_frame, bg=COLORS["card"])
        version_frame.pack(fill="x", padx=15, pady=10)
        tk.Label(version_frame, text="⛏ Версия Minecraft:", bg=COLORS["card"], font=("Arial", 10, "bold")).pack(anchor="w")
        version_combo_frame = tk.Frame(version_frame, bg=COLORS["card"])
        version_combo_frame.pack(fill="x", pady=5)
        self.version_combo = ttk.Combobox(version_combo_frame, textvariable=self.minecraft_version,
                                          values=[], state="readonly")
        self.version_combo.pack(side="left", fill="x", expand=True)
        self.version_combo.bind("<<ComboboxSelected>>", lambda e: self.update_server_types())

        # --- Тип сервера ---
        type_frame = tk.Frame(settings_frame, bg=COLORS["card"])
        type_frame.pack(fill="x", padx=15, pady=10)
        tk.Label(type_frame, text="🔧 Тип сервера:", bg=COLORS["card"], font=("Arial", 10, "bold")).pack(anchor="w")
        type_combo_frame = tk.Frame(type_frame, bg=COLORS["card"])
        type_combo_frame.pack(fill="x", pady=5)
        self.type_combo = ttk.Combobox(type_combo_frame, textvariable=self.server_type, state="readonly")
        self.type_combo.pack(side="left", fill="x", expand=True)

        # --- Версия Java ---
        java_frame = tk.Frame(settings_frame, bg=COLORS["card"])
        java_frame.pack(fill="x", padx=15, pady=10)
        tk.Label(java_frame, text="☕ Версия Java:", bg=COLORS["card"], font=("Arial", 10, "bold")).pack(anchor="w")
        java_combo_frame = tk.Frame(java_frame, bg=COLORS["card"])
        java_combo_frame.pack(fill="x", pady=5)
        self.java_combo = ttk.Combobox(java_combo_frame, textvariable=self.java_version, values=self.java_versions, state="readonly")
        self.java_combo.pack(side="left", fill="x", expand=True)
        self.java_status = tk.Label(java_combo_frame, text="Проверка...", bg=COLORS["card"], fg=COLORS["info"])
        self.java_status.pack(side="left", padx=5)

        # --- Память ---
        memory_frame = tk.Frame(settings_frame, bg=COLORS["card"])
        memory_frame.pack(fill="x", padx=15, pady=10)
        tk.Label(memory_frame, text="💾 Память (ГБ):", bg=COLORS["card"], font=("Arial", 10, "bold")).pack(anchor="w")
        memory_combo_frame = tk.Frame(memory_frame, bg=COLORS["card"])
        memory_combo_frame.pack(fill="x", pady=5)
        ram_options = [str(i) for i in range(1, int(self.get_total_ram_gb()) + 1)]
        self.memory_combo = ttk.Combobox(memory_combo_frame, textvariable=self.memory, values=ram_options, state="readonly")
        self.memory_combo.pack(side="left", fill="x", expand=True)

        # --- Кнопки управления ---
        buttons_frame = tk.Frame(settings_frame, bg=COLORS["card"])
        buttons_frame.pack(fill="x", padx=15, pady=10)
        btn_width = 15
        tk.Button(buttons_frame, text="🔨 Создать сервер", command=self.create_server_thread,
                  bg=COLORS["success"], fg="white", width=btn_width).pack(side="left", padx=2)
        self.start_btn = tk.Button(buttons_frame, text="▶️ Запустить", command=self.start_server,
                                   bg=COLORS["primary"], fg="white", width=btn_width)
        self.start_btn.pack(side="left", padx=2)
        self.stop_btn = tk.Button(buttons_frame, text="⏹ Остановить", command=self.stop_server,
                                  bg=COLORS["danger"], fg="white", width=btn_width, state="disabled")
        self.stop_btn.pack(side="left", padx=2)

        # --- Быстрые действия ---
        quick_actions_frame = tk.Frame(settings_frame, bg=COLORS["card"])
        quick_actions_frame.pack(fill="x", padx=15, pady=10)
        tk.Label(quick_actions_frame, text="⚡ Быстрые действия:", bg=COLORS["card"], font=("Arial", 10, "bold")).pack(anchor="w")
        actions_frame = tk.Frame(quick_actions_frame, bg=COLORS["card"])
        actions_frame.pack(fill="x", pady=5)
        tk.Button(actions_frame, text="📂 Mods", command=self.open_mods_folder, bg=COLORS["info"], fg="white").pack(side="left", padx=2)
        tk.Button(actions_frame, text="📁 Data Packs", command=self.open_datapacks_folder, bg=COLORS["warning"], fg="white").pack(side="left", padx=2)
        tk.Button(actions_frame, text="⚙️ Настройки", command=self.open_server_properties, bg=COLORS["warning"], fg="white").pack(side="left", padx=2)
        tk.Button(actions_frame, text="📦 Бэкапы", command=self.manage_backups, bg=COLORS["primary"], fg="white").pack(side="left", padx=2)
        tk.Button(actions_frame, text="🧩 Плагины", command=self.open_plugin_manager, bg=COLORS["success"], fg="white").pack(side="left", padx=2)
        tk.Button(actions_frame, text="🕒 Планировщик", command=self.open_scheduler, bg=COLORS["info"], fg="white").pack(side="left", padx=2)

        # --- Правая панель (Логи и диагностика) ---
        right_frame = tk.Frame(main_paned, bg=COLORS["background"])
        main_paned.add(right_frame)

        # --- Логи сервера ---
        logs_label = tk.Label(right_frame, text="📜 Логи сервера", bg=COLORS["background"], font=("Arial", 12, "bold"))
        logs_label.pack(anchor="w", padx=5, pady=(0, 5))
        
        # --- Фильтр логов ---
        filter_frame = tk.Frame(right_frame, bg=COLORS["background"])
        filter_frame.pack(fill="x", padx=5, pady=2)
        tk.Label(filter_frame, text="🔍 Фильтр:", bg=COLORS["background"]).pack(side="left")
        self.log_filter_var = tk.StringVar()
        self.log_filter_entry = tk.Entry(filter_frame, textvariable=self.log_filter_var)
        self.log_filter_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.log_filter_entry.bind("<Return>", self.filter_logs)
        tk.Button(filter_frame, text="Очистить", command=self.clear_logs, bg=COLORS["warning"], fg="white").pack(side="right", padx=2)
        tk.Button(filter_frame, text="Сохранить", command=self.save_logs, bg=COLORS["primary"], fg="white").pack(side="right", padx=2)

        self.log_text = scrolledtext.ScrolledText(right_frame, state='disabled', height=15, bg="#2c3e50", fg="#ecf0f1")
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)

        # --- Диагностика ---
        diag_frame = tk.LabelFrame(right_frame, text="🔍 Диагностика", bg=COLORS["card"], fg=COLORS["dark"])
        diag_frame.pack(fill="x", padx=5, pady=10)

        self.diag_label = tk.Label(diag_frame, text="Проверка...", bg=COLORS["card"], fg=COLORS["warning"])
        self.diag_label.pack(anchor="w", padx=10, pady=5)

        conn_frame = tk.Frame(diag_frame, bg=COLORS["card"])
        conn_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(conn_frame, text="🌐 Локальный IP:", bg=COLORS["card"]).pack(side="left")
        self.local_ip = tk.Label(conn_frame, text="...", bg=COLORS["card"], fg=COLORS["info"])
        self.local_ip.pack(side="left", padx=5)
        tk.Label(conn_frame, text=" | Публичный IP:", bg=COLORS["card"]).pack(side="left")
        self.public_ip = tk.Label(conn_frame, text="...", bg=COLORS["card"], fg=COLORS["info"])
        self.public_ip.pack(side="left", padx=5)

        # --- Мониторинг ресурсов ---
        res_frame = tk.Frame(diag_frame, bg=COLORS["card"])
        res_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(res_frame, text="🖥 CPU:", bg=COLORS["card"]).pack(side="left")
        self.cpu_usage = tk.Label(res_frame, text="...", bg=COLORS["card"], fg=COLORS["info"])
        self.cpu_usage.pack(side="left", padx=5)
        tk.Label(res_frame, text=" | 🧠 RAM:", bg=COLORS["card"]).pack(side="left")
        self.ram_usage = tk.Label(res_frame, text="...", bg=COLORS["card"], fg=COLORS["info"])
        self.ram_usage.pack(side="left", padx=5)
        
        # --- Командная строка ---
        cmd_frame = tk.Frame(right_frame, bg=COLORS["background"])
        cmd_frame.pack(fill="x", padx=5, pady=5)
        tk.Label(cmd_frame, text="⌨ Команда:", bg=COLORS["background"]).pack(side="left")
        self.cmd_entry = tk.Entry(cmd_frame)
        self.cmd_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.cmd_entry.bind("<Return>", self.send_command)
        tk.Button(cmd_frame, text="Отправить", command=self.send_command, bg=COLORS["primary"], fg="white").pack(side="right")

        # --- Вкладки ---
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)

        # --- Вкладка "Настройки сервера" ---
        self.props_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.props_frame, text="⚙️ Настройки сервера")
        self.create_properties_widgets()

        # --- Вкладка "Менеджер плагинов" ---
        self.plugins_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.plugins_frame, text="🧩 Менеджер плагинов")
        self.create_plugin_widgets()

        # --- Вкладка "Бэкапы" ---
        self.backups_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.backups_frame, text="📦 Бэкапы")
        self.create_backup_widgets()
        
        # --- Вкладка "Планировщик" ---
        self.scheduler_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.scheduler_frame, text="🕒 Планировщик")
        self.create_scheduler_widgets()
        
        # --- Вкладка "Оптимизация" ---
        self.optimization_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.optimization_frame, text="🚀 Оптимизация")
        self.create_optimization_widgets()

    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.logs.append(formatted_message)
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, formatted_message + "\n")
        self.log_text.config(state='disabled')
        self.log_text.see(tk.END)

    def get_total_ram_gb(self):
        try:
            if PSUTIL_AVAILABLE:
                return int(psutil.virtual_memory().total / (1024**3))
            else:
                # Простая оценка по количеству процессоров (очень приблизительно)
                import multiprocessing
                cores = multiprocessing.cpu_count()
                # Предположим, что на ядро ~2ГБ (очень грубо)
                estimated_gb = max(4, cores * 2)
                return estimated_gb
        except Exception as e:
            self.log(f"Ошибка определения ОЗУ: {e}. Используется значение по умолчанию 8 ГБ.")
            return 8

    def browse_path(self):
        path = filedialog.askdirectory(initialdir=self.server_path.get())
        if path:
            self.server_path.set(path)

    def load_versions(self):
        """Загружает доступные версии Minecraft, Forge и Fabric"""
        self.log("Загружаю список версий...")
        # Версии Minecraft
        try:
            response = requests.get("https://launchermeta.mojang.com/mc/game/version_manifest.json")
            manifest = response.json()
            # Сортируем версии по возрастанию (самые новые в конце)
            all_versions = [v["id"] for v in manifest["versions"] if v["type"] == "release"]
            self.minecraft_versions = sorted(all_versions, key=lambda x: tuple(map(int, x.split('.'))) if '.' in x else x)
            # Устанавливаем первую версию в списке
            if self.minecraft_versions:
                self.minecraft_version.set(self.minecraft_versions[-1]) # Берем последнюю (новую)
            self.log("Список версий Minecraft загружен")
            self.version_combo["values"] = self.minecraft_versions
        except Exception as e:
            self.log(f"Ошибка загрузки версий Minecraft: {str(e)}")
            self.minecraft_versions = ["1.20.1", "1.19.4", "1.18.2", "1.17.1", "1.16.5"]
            self.version_combo["values"] = self.minecraft_versions
            self.minecraft_version.set(self.minecraft_versions[0])

        # Версии Paper (лучше для плагинов)
        try:
            response = requests.get("https://papermc.io/api/v2/projects/paper")
            data = response.json()
            self.paper_versions = {}
            for version in data["versions"][-5:]: # Последние 5 версий
                response = requests.get(f"https://papermc.io/api/v2/projects/paper/versions/{version}")
                builds = response.json()["builds"]
                if builds:
                    self.paper_versions[version] = f"paper-{version}-{builds[-1]}"
            self.log("Список версий Paper загружен")
        except Exception as e:
            self.log(f"Ошибка загрузки версий Paper: {str(e)}")
            self.paper_versions = {
                "1.20.1": "paper-1.20.1-196",
                "1.19.4": "paper-1.19.4-550",
                "1.18.2": "paper-1.18.2-387",
                "1.17.1": "paper-1.17.1-411",
                "1.16.5": "paper-1.16.5-804"
            }

        # Версии Forge
        try:
            response = requests.get("https://files.minecraftforge.net/net/minecraftforge/forge/index.json")
            data = response.json()
            self.forge_versions = {}
            for version, builds in data["builds"].items():
                if builds:
                    self.forge_versions[version] = builds[-1]["version"]
            self.log("Список версий Forge загружен")
        except Exception as e:
            self.log(f"Ошибка загрузки версий Forge: {str(e)}")
            self.forge_versions = {
                "1.20.1": "1.20.1-47.2.0",
                "1.19.4": "1.19.4-45.2.0",
                "1.18.2": "1.18.2-40.2.17",
                "1.16.5": "1.16.5-36.2.42"
            }

        # Версии Fabric
        try:
            response = requests.get("https://meta.fabricmc.net/v2/versions/loader")
            self.fabric_versions = {item["loader"]["version"]: item["loader"]["version"]
                                    for item in response.json()[:10]}
            self.log("Список версий Fabric загружен")
        except Exception as e:
            self.log(f"Ошибка загрузки версий Fabric: {str(e)}")
            self.fabric_versions = {
                "0.15.11": "0.15.11",
                "0.15.10": "0.15.10",
                "0.15.9": "0.15.9",
                "0.14.23": "0.14.23",
                "0.14.22": "0.14.22"
            }

        self.update_server_types()

    def update_server_types(self):
        """Обновляет доступные типы серверов для выбранной версии"""
        version = self.minecraft_version.get()
        types = ["Paper"] # Paper лучше всего подходит для плагинов
        if version in self.forge_versions:
            types.append("Forge")
        if version in self.fabric_versions:
            types.append("Fabric")
        self.type_combo["values"] = types
        if self.server_type.get() not in types:
            self.server_type.set(types[0] if types else "Paper")
        self.update_memory_limits()

    def update_memory_limits(self):
        """Обновляет лимиты памяти в зависимости от доступной ОЗУ"""
        total_ram = self.get_total_ram_gb()
        max_usable = max(1, int(total_ram * 0.7)) # 70% от общей памяти
        ram_options = [str(i) for i in range(1, max_usable + 1)]
        self.memory_combo['values'] = ram_options
        if int(self.memory.get()) > max_usable:
            self.memory.set(str(max_usable))

    def check_java(self):
        """Проверяет наличие различных версий Java"""
        self.java_paths = {}
        java_versions_found = []
        # Проверяем стандартные пути для разных ОС
        java_paths = []
        if os.name == 'nt':  # Windows
            # Попробуем найти Java в стандартных местах
            java_paths.extend([
                r"C:\Program Files\Java\jdk-17\bin\java.exe",
                r"C:\Program Files\Java\jdk-11\bin\java.exe",
                r"C:\Program Files\Java\jdk-8\bin\java.exe",
                r"C:\Program Files\Java\jre-17\bin\java.exe",
                r"C:\Program Files\Java\jre-11\bin\java.exe",
                r"C:\Program Files\Java\jre-8\bin\java.exe",
                r"C:\Program Files\Eclipse Adoptium\jdk-17.0.11.1_windows-x64\bin\java.exe",
                r"C:\Program Files\Eclipse Adoptium\jdk-11.0.20.1_1_windows-x64\bin\java.exe",
                r"C:\Program Files\Eclipse Adoptium\jdk-8.0.402.6-hotspot\bin\java.exe",
            ])
            # Проверяем переменную окружения JAVA_HOME
            java_home = os.environ.get("JAVA_HOME")
            if java_home:
                java_paths.append(os.path.join(java_home, "bin", "java.exe"))
        else:  # Unix-like (Linux, macOS)
            java_paths.extend([
                "/usr/lib/jvm/java-17/bin/java",
                "/usr/lib/jvm/java-11/bin/java",
                "/usr/lib/jvm/java-8/bin/java",
                "/usr/lib/jvm/default-java/bin/java",
                "/opt/java/openjdk/bin/java",
                "/Library/Java/JavaVirtualMachines/jdk-17.jdk/Contents/Home/bin/java",
                "/Library/Java/JavaVirtualMachines/jdk-11.jdk/Contents/Home/bin/java",
                "/Library/Java/JavaVirtualMachines/jdk-8.jdk/Contents/Home/bin/java",
            ])
            # Проверяем переменную окружения JAVA_HOME
            java_home = os.environ.get("JAVA_HOME")
            if java_home:
                java_paths.append(os.path.join(java_home, "bin", "java"))

        # Проверяем наличие Java по указанным путям
        for path in java_paths:
            if os.path.exists(path):
                try:
                    # Получаем версию Java
                    result = subprocess.run([path, "-version"], capture_output=True, text=True, check=True)
                    version_match = re.search(r'version "(\d+(?:\.\d+)?)', result.stderr or result.stdout)
                    if version_match:
                        version = version_match.group(1)
                        self.java_paths[version] = path
                        java_versions_found.append(version)
                        self.log(f"Найдена Java {version}: {path}")
                except Exception as e:
                    self.log(f"Ошибка проверки Java в {path}: {e}")

        # Проверяем через команду 'java -version' (если доступна в PATH)
        try:
            result = subprocess.run(["java", "-version"], capture_output=True, text=True, check=True)
            version_match = re.search(r'version "(\d+(?:\.\d+)?)', result.stderr or result.stdout)
            if version_match:
                version = version_match.group(1)
                if version not in self.java_paths:
                    self.java_paths[version] = "java"
                    java_versions_found.append(version)
                    self.log(f"Найдена Java {version} из PATH")
        except Exception as e:
            self.log(f"Ошибка проверки Java из PATH: {e}")

        # Устанавливаем статус Java
        if java_versions_found:
            # Выбираем наиболее подходящую версию для текущей версии Minecraft
            current_mc_version = self.minecraft_version.get()
            required_java = JAVA_VERSIONS_FOR_MINECRAFT.get(current_mc_version, "17")
            if required_java in java_versions_found:
                self.java_version.set(required_java)
                self.java_status.config(text=f"Java {required_java} доступна", fg=COLORS["success"])
            else:
                # Если нужная версия не найдена, используем первую найденную
                first_version = java_versions_found[0]
                self.java_version.set(first_version)
                self.java_status.config(text=f"Java {first_version} доступна", fg=COLORS["warning"])
            self.log(f"Доступны версии Java: {', '.join(java_versions_found)}")
        else:
            self.java_status.config(text="Java не установлена!", fg=COLORS["danger"])
            self.log("⚠️ Java не обнаружена. Установите Java с https://adoptium.net/")
            return False

        return True

    def create_server_thread(self):
        thread = threading.Thread(target=self.create_server)
        thread.daemon = True
        thread.start()

    def create_server(self):
        if not self.check_java():
             messagebox.showerror("Ошибка", "Java не найдена. Установка сервера невозможна.")
             return

        path = Path(self.server_path.get())
        version = self.minecraft_version.get()
        server_type = self.server_type.get()
        memory = self.memory.get()
        java_version = self.java_version.get()

        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)

        self.log(f"Создаю {server_type} сервер для Minecraft {version} (Java {java_version}) в {path}")
        try:
            if server_type == "Vanilla":
                self.create_vanilla_server(path, version)
            elif server_type == "Paper":
                self.create_paper_server(path, version)
            elif server_type == "Forge":
                self.create_forge_server(path, version)
            elif server_type == "Fabric":
                self.create_fabric_server(path, version)

            self.create_start_script(path, memory, server_type, version, java_version)
            self.log("✅ Сервер успешно создан!")
            messagebox.showinfo("Успех", "Сервер успешно создан!")
        except Exception as e:
            self.log(f"❌ Ошибка создания сервера: {e}")
            messagebox.showerror("Ошибка", f"Не удалось создать сервер:\n{str(e)}")

    def create_vanilla_server(self, path, version):
        self.log("Создаю Vanilla сервер...")
        manifest_url = "https://launchermeta.mojang.com/mc/game/version_manifest.json"
        manifest = requests.get(manifest_url).json()
        version_url = None
        for ver in manifest["versions"]:
            if ver["id"] == version:
                version_url = ver["url"]
                break
        else:
            raise Exception(f"Версия {version} не найдена в manifest")

        version_data = requests.get(version_url).json()
        server_url = version_data["downloads"]["server"]["url"]
        server_jar = path / f"server-{version}.jar"
        if not server_jar.exists():
            self.log("Скачиваю серверный JAR...")
            response = requests.get(server_url)
            with open(server_jar, "wb") as f:
                f.write(response.content)
        with open(path / "eula.txt", "w") as f:
            f.write("eula=true")

    def create_paper_server(self, path, version):
        self.log("Создаю Paper сервер...")
        if version not in self.paper_versions:
            raise Exception(f"Для версии {version} нет доступных сборок Paper")
        paper_version = self.paper_versions[version]
        self.log(f"Использую Paper {paper_version}")
        jar_name = f"{paper_version}.jar"
        server_jar = path / jar_name
        if not server_jar.exists():
             self.log("Скачиваю Paper JAR...")
             # Пример URL, может потребоваться обновление
             paper_url = f"https://api.papermc.io/v2/projects/paper/versions/{version}/builds/{paper_version.split('-')[-1]}/downloads/{jar_name}"
             response = requests.get(paper_url)
             if response.status_code == 200:
                 with open(server_jar, "wb") as f:
                     f.write(response.content)
             else:
                 raise Exception(f"Не удалось скачать Paper. Код ошибки: {response.status_code}")
        with open(path / "eula.txt", "w") as f:
            f.write("eula=true")

    def create_forge_server(self, path, version):
        self.log("Создаю Forge сервер...")
        if version not in self.forge_versions:
            raise Exception(f"Для версии {version} нет доступных сборок Forge")
        forge_version = self.forge_versions[version]
        self.log(f"Использую Forge {forge_version}")
        installer_name = f"forge-{forge_version}-installer.jar"
        installer_path = path / installer_name
        if not installer_path.exists():
            self.log("Скачиваю Forge Installer...")
            # Пример URL, может потребоваться обновление
            installer_url = f"https://maven.minecraftforge.net/net/minecraftforge/forge/{forge_version}/{installer_name}"
            response = requests.get(installer_url)
            if response.status_code == 200:
                with open(installer_path, "wb") as f:
                    f.write(response.content)
            else:
                 raise Exception(f"Не удалось скачать Forge Installer. Код ошибки: {response.status_code}")
        
        self.log("Запускаю установку Forge...")
        try:
            # Запуск установщика в тихом режиме
            subprocess.run([
                "java", "-jar", installer_name, "--installServer"
            ], cwd=path, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.log("Forge установлен.")
            # Удаление установщика после установки (опционально)
            # installer_path.unlink()
        except subprocess.CalledProcessError as e:
            raise Exception(f"Ошибка при запуске установщика Forge: {e}")

    def create_fabric_server(self, path, version):
        self.log("Создаю Fabric сервер...")
        if version not in self.fabric_versions:
            raise Exception(f"Для версии {version} нет доступных сборок Fabric")
        fabric_version = self.fabric_versions[version]
        self.log(f"Использую Fabric Loader {fabric_version}")
        
        # Скачивание Fabric Installer (если его нет)
        installer_path = path / "fabric-installer.jar"
        if not installer_path.exists():
            self.log("Скачиваю Fabric Installer...")
            installer_url = "https://meta.fabricmc.net/v2/versions/installer"
            response = requests.get(installer_url)
            if response.status_code == 200:
                latest_installer = response.json()[0] # Берем последнюю версию установщика
                installer_download_url = latest_installer['url']
                installer_response = requests.get(installer_download_url)
                with open(installer_path, "wb") as f:
                    f.write(installer_response.content)
            else:
                 raise Exception(f"Не удалось получить информацию об установщике Fabric. Код ошибки: {response.status_code}")

        self.log("Запускаю установку Fabric...")
        try:
            # Запуск установщика в тихом режиме
            subprocess.run([
                "java", "-jar", "fabric-installer.jar", "server", "-mcversion", version, "-loader", fabric_version.split('+')[0], "-downloadMinecraft"
            ], cwd=path, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.log("Fabric установлен.")
            # Переименование server.jar в более понятное имя (опционально)
            # (path / "fabric-server-launch.jar").rename(path / f"fabric-{version}-{fabric_version.split('+')[0]}.jar")
        except subprocess.CalledProcessError as e:
            raise Exception(f"Ошибка при запуске установщика Fabric: {e}")

    def create_start_script(self, path, memory, server_type, version, java_version):
        max_mem = memory
        min_mem = max(1, int(memory) // 2) # Минимум 1ГБ или половина от выделенной
        java_path = self.java_paths.get(java_version, "java") # Получаем путь к нужной версии Java
        if os.name == 'nt': # Windows
            start_script = path / "start.bat"
            jar_name = ""
            if server_type == "Vanilla":
                jar_name = f"server-{version}.jar"
            elif server_type == "Paper":
                jar_name = f"{self.paper_versions[version]}.jar"
            elif server_type == "Forge":
                 # Имя может отличаться, ищем подходящий файл
                 potential_names = [f"forge-{self.forge_versions[version]}.jar", "forge-server.jar", "server.jar"]
                 for name in potential_names:
                     if (path / name).exists():
                         jar_name = name
                         break
                 if not jar_name:
                    jar_name = "server.jar" # fallback
            elif server_type == "Fabric":
                jar_name = "fabric-server-launch.jar" # или другое имя, если переименовано

            with open(start_script, "w") as f:
                f.write(f"@echo off\n")
                f.write(f"echo Запуск сервера Minecraft {version} ({server_type}) с Java {java_version}\n")
                f.write(f"echo Выделено памяти: {memory} ГБ (макс. {max_mem} ГБ)\n")
                f.write(f"\"{java_path}\" -Xms{min_mem}G -Xmx{max_mem}G -XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200 -XX:+UnlockExperimentalVMOptions -XX:+DisableExplicitGC -XX:G1NewSizePercent=30 -XX:G1MaxNewSizePercent=40 -XX:G1HeapRegionSize=8M -XX:G1ReservePercent=20 -XX:G1HeapWastePercent=5 -XX:G1MixedGCCountTarget=4 -XX:InitiatingHeapOccupancyPercent=15 -XX:G1MixedGCLiveThresholdPercent=90 -XX:G1RSetUpdatingPauseTimePercent=5 -XX:SurvivorRatio=32 -XX:+PerfDisableSharedMem -XX:MaxTenuringThreshold=1 -jar \"{jar_name}\" nogui\n")
                f.write("pause\n")
        else: # Unix-like
            start_script = path / "start.sh"
            jar_name = ""
            if server_type == "Vanilla":
                jar_name = f"server-{version}.jar"
            elif server_type == "Paper":
                jar_name = f"{self.paper_versions[version]}.jar"
            elif server_type == "Forge":
                 potential_names = [f"forge-{self.forge_versions[version]}.jar", "forge-server.jar", "server.jar"]
                 for name in potential_names:
                     if (path / name).exists():
                         jar_name = name
                         break
                 if not jar_name:
                    jar_name = "server.jar"
            elif server_type == "Fabric":
                jar_name = "fabric-server-launch.jar"

            with open(start_script, "w") as f:
                f.write("#!/bin/bash\n")
                f.write(f"echo \"Запуск сервера Minecraft {version} ({server_type}) с Java {java_version}\"\n")
                f.write(f"echo \"Выделено памяти: {memory} ГБ (макс. {max_mem} ГБ)\"\n")
                f.write(f"\"{java_path}\" -Xms{min_mem}G -Xmx{max_mem}G -XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200 -XX:+UnlockExperimentalVMOptions -XX:+DisableExplicitGC -XX:G1NewSizePercent=30 -XX:G1MaxNewSizePercent=40 -XX:G1HeapRegionSize=8M -XX:G1ReservePercent=20 -XX:G1HeapWastePercent=5 -XX:G1MixedGCCountTarget=4 -XX:InitiatingHeapOccupancyPercent=15 -XX:G1MixedGCLiveThresholdPercent=90 -XX:G1RSetUpdatingPauseTimePercent=5 -XX:SurvivorRatio=32 -XX:+PerfDisableSharedMem -XX:MaxTenuringThreshold=1 -jar \"{jar_name}\" nogui\n")
            os.chmod(start_script, 0o755) # Делаем скрипт исполняемым

    def start_server(self):
        path = Path(self.server_path.get())
        if not path.exists():
            messagebox.showerror("Ошибка", "Указанный путь не существует!")
            return

        # Проверяем наличие start скрипта или jar файла
        start_script = path / ("start.bat" if os.name == 'nt' else "start.sh")
        server_jar = None
        if not start_script.exists():
            # Ищем jar файлы
            jar_files = list(path.glob("*.jar"))
            if not jar_files:
                messagebox.showerror("Ошибка", "Не найден скрипт запуска или .jar файл сервера!")
                return
            # Предполагаем, что первый найденный jar - это сервер
            server_jar = jar_files[0]
            self.log(f"Скрипт запуска не найден. Попытка запустить {server_jar.name} напрямую.")

        self.log("Запускаю сервер...")
        try:
            if start_script.exists():
                # Запуск через скрипт
                if os.name == 'nt':
                     self.server_process = subprocess.Popen(
                         ["cmd", "/c", "start.bat"],
                         cwd=path,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT,
                         text=True,
                         encoding='utf-8',
                         creationflags=subprocess.CREATE_NEW_CONSOLE
                     )
                else:
                     self.server_process = subprocess.Popen(
                         ["bash", "start.sh"],
                         cwd=path,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT,
                         text=True,
                         encoding='utf-8'
                     )
            elif server_jar:
                # Запуск напрямую через java
                 memory = self.memory.get()
                 max_mem = memory
                 min_mem = max(1, int(memory) // 2)
                 java_path = self.java_paths.get(self.java_version.get(), "java")
                 if os.name == 'nt':
                     self.server_process = subprocess.Popen(
                         [java_path, f"-Xms{min_mem}G", f"-Xmx{max_mem}G", "-jar", server_jar.name, "nogui"],
                         cwd=path,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT,
                         text=True,
                         encoding='utf-8',
                         creationflags=subprocess.CREATE_NEW_CONSOLE
                     )
                 else:
                     self.server_process = subprocess.Popen(
                         [java_path, f"-Xms{min_mem}G", f"-Xmx{max_mem}G", "-jar", server_jar.name, "nogui"],
                         cwd=path,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT,
                         text=True,
                         encoding='utf-8'
                     )
            else:
                 raise Exception("Не удалось определить способ запуска сервера.")

            self.is_running = True
            self.status_var.set("Сервер запущен")
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            self.log("Сервер запущен. Логи отображаются ниже.")
            # Запуск потока для чтения логов
            threading.Thread(target=self.read_server_logs, daemon=True).start()
            # Запуск потока для мониторинга ресурсов
            if PSUTIL_AVAILABLE:
                threading.Thread(target=self.monitor_resources, daemon=True).start()
        except Exception as e:
            self.log(f"❌ Ошибка запуска сервера: {e}")
            messagebox.showerror("Ошибка", f"Не удалось запустить сервер:\n{str(e)}")

    def read_server_logs(self):
        """Читает логи сервера в реальном времени"""
        if self.server_process and self.server_process.stdout:
            try:
                while True:
                    output = self.server_process.stdout.readline()
                    if output == '' and self.server_process.poll() is not None:
                        break
                    if output:
                        # Попробуем декодировать как UTF-8
                        try:
                            decoded_output = output.strip()
                            self.log(decoded_output)
                        except UnicodeDecodeError:
                            # Если UTF-8 не работает, попробуем Windows-1251
                            try:
                                decoded_output = output.decode('cp1251').strip()
                                self.log(decoded_output)
                            except Exception as e:
                                # Если и cp1251 не работает, просто используем raw bytes
                                self.log(f"Ошибка декодирования лога: {e}")
            except Exception as e:
                 self.log(f"Ошибка чтения логов: {e}")
        # После завершения процесса обновляем кнопки
        self.server_process = None
        self.is_running = False
        self.status_var.set("Сервер остановлен")
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")

    def monitor_resources(self):
        """Мониторит использование ресурсов"""
        while self.is_running and self.server_process and self.server_process.poll() is None:
            try:
                if PSUTIL_AVAILABLE:
                    # Получаем информацию о процессе сервера
                    p = psutil.Process(self.server_process.pid)
                    cpu_percent = p.cpu_percent()
                    mem_info = p.memory_info()
                    mem_mb = mem_info.rss / 1024 / 1024
                    # Общая информация о системе
                    total_ram_gb = self.get_total_ram_gb()
                    self.root.after(0, lambda: self.cpu_usage.config(text=f"{cpu_percent:.1f}%", fg=COLORS["success"] if cpu_percent < 50 else (COLORS["warning"] if cpu_percent < 80 else COLORS["danger"])))
                    self.root.after(0, lambda: self.ram_usage.config(text=f"{mem_mb:.1f} МБ / {total_ram_gb} ГБ", fg=COLORS["success"] if mem_mb < total_ram_gb * 1024 * 0.6 else (COLORS["warning"] if mem_mb < total_ram_gb * 1024 * 0.8 else COLORS["danger"])))
                time.sleep(2) # Обновляем каждые 2 секунды
            except psutil.NoSuchProcess:
                # Процесс завершен
                break
            except Exception as e:
                self.log(f"Ошибка мониторинга ресурсов: {e}")
                break

    def stop_server(self):
         if self.server_process:
             try:
                 # Отправляем команду 'stop' в сервер
                 self.send_command_internal("stop")
                 self.log("Команда 'stop' отправлена серверу...")
                 # Ждем завершения процесса
                 self.server_process.wait(timeout=30) # Ждем максимум 30 секунд
                 self.log("Сервер остановлен.")
             except subprocess.TimeoutExpired:
                 self.log("Сервер не отвечает. Принудительная остановка...")
                 self.server_process.kill()
                 self.server_process.wait()
                 self.log("Сервер принудительно остановлен.")
             except Exception as e:
                 self.log(f"Ошибка при остановке сервера: {e}")
             finally:
                 self.server_process = None
                 self.is_running = False
                 self.status_var.set("Сервер остановлен")
                 self.start_btn.config(state="normal")
                 self.stop_btn.config(state="disabled")

    def send_command_internal(self, command):
        """Отправляет команду запущенному серверу (внутренняя функция)"""
        if self.server_process and self.server_process.stdin:
            try:
                self.server_process.stdin.write(command + "\n")
                self.server_process.stdin.flush()
                self.log(f"Команда отправлена: {command}")
            except Exception as e:
                self.log(f"Ошибка отправки команды: {e}")
        else:
            self.log("Сервер не запущен или недоступен для отправки команд.")

    def send_command(self, event=None):
        """Отправляет команду из интерфейса"""
        if not self.is_running or not self.server_process:
            messagebox.showerror("Ошибка", "Сервер не запущен!")
            return
        command = self.cmd_entry.get().strip()
        if not command:
            return
        self.send_command_internal(command)
        self.cmd_entry.delete(0, tk.END)

    def open_mods_folder(self):
        path = Path(self.server_path.get())
        mods_path = path / "mods"
        if not mods_path.exists():
            mods_path.mkdir(parents=True, exist_ok=True)
        self.open_folder(mods_path)

    def open_datapacks_folder(self):
        """Открывает папку datapacks для текущего мира сервера."""
        path = Path(self.server_path.get())
        # Получаем имя мира из server.properties (или используем значение по умолчанию)
        world_name = self.server_properties.get("level-name", "world")
        datapacks_path = path / world_name / "datapacks"
        if not datapacks_path.exists():
            datapacks_path.mkdir(parents=True, exist_ok=True)
            self.log(f"Создана папка для дата-паков: {datapacks_path}")
        self.open_folder(datapacks_path)

    def open_server_properties(self):
        path = Path(self.server_path.get())
        props_file = path / "server.properties"
        if not props_file.exists():
            with open(props_file, "w") as f:
                f.write("#Minecraft server properties\n")
        self.open_folder(props_file)

    def open_folder(self, path):
        try:
            if os.name == 'nt':  # Windows
                os.startfile(path)
            elif os.name == 'posix':  # macOS or Linux
                subprocess.run(['open' if sys.platform == 'darwin' else 'xdg-open', str(path)])
        except Exception as e:
            self.log(f"Ошибка открытия папки: {e}")
            messagebox.showerror("Ошибка", f"Не удалось открыть папку:\n{str(e)}")

    def manage_backups(self):
        # Простой вызов окна бэкапов
        self.notebook.select(self.backups_frame)
        
    def open_plugin_manager(self):
        # Простой вызов окна плагинов
        self.notebook.select(self.plugins_frame)
        
    def open_scheduler(self):
        # Простой вызов окна планировщика
        self.notebook.select(self.scheduler_frame)

    # --- Виджеты для вкладки "Настройки сервера" ---
    def create_properties_widgets(self):
        self.props_vars = {}
        self.props_entries = {}
        canvas = tk.Canvas(self.props_frame, borderwidth=0)
        frame = tk.Frame(canvas)
        vsb = tk.Scrollbar(self.props_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)

        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window((0, 0), window=frame, anchor="nw")
        frame.bind("<Configure>", lambda event, canvas=canvas: self.on_frame_configure(canvas))

        self.props_container = frame

        # Кнопки сохранения и обновления
        btn_frame = tk.Frame(self.props_frame)
        btn_frame.pack(side="bottom", fill="x", padx=5, pady=5)
        tk.Button(btn_frame, text="🔄 Обновить", command=self.load_server_properties, bg=COLORS["info"], fg="white").pack(side="left", padx=5)
        tk.Button(btn_frame, text="💾 Сохранить", command=self.save_server_properties, bg=COLORS["success"], fg="white").pack(side="left", padx=5)
        tk.Button(btn_frame, text="🔄 Сбросить", command=self.reset_server_properties, bg=COLORS["warning"], fg="white").pack(side="left", padx=5)

    def on_frame_configure(self, canvas):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def load_server_properties(self):
        path = Path(self.server_path.get())
        props_file = path / "server.properties"
        default_props = {
            "difficulty": "easy", "gamemode": "survival", "level-seed": "",
            "view-distance": "10", "simulation-distance": "10", "max-players": "20",
            "level-name": "world", "level-type": "default", "online-mode": "true",
            "white-list": "false", "pvp": "true"
        }
        properties = default_props.copy()
        if props_file.exists():
            try:
                with open(props_file, "r") as f:
                    for line in f:
                        if line.strip() and not line.startswith("#"):
                            key, value = line.strip().split("=", 1)
                            properties[key] = value
            except Exception as e:
                self.log(f"Ошибка загрузки server.properties: {e}")

        # Очистка предыдущих виджетов
        for widget in self.props_container.winfo_children():
            widget.destroy()
        self.props_vars.clear()
        self.props_entries.clear()

        # Создание виджетов для каждого свойства
        for key, value in properties.items():
            row_frame = tk.Frame(self.props_container, bg=COLORS["card"])
            row_frame.pack(fill="x", padx=5, pady=2)
            tk.Label(row_frame, text=key, width=20, anchor="w", bg=COLORS["card"]).pack(side="left")
            var = tk.StringVar(value=value)
            self.props_vars[key] = var
            entry = tk.Entry(row_frame, textvariable=var)
            entry.pack(side="left", fill="x", expand=True, padx=(5, 0))
            self.props_entries[key] = entry # Сохраняем ссылку на entry

        # Сохраняем свойства для использования в других функциях (например, open_datapacks_folder)
        self.server_properties = properties

    def save_server_properties(self):
        path = Path(self.server_path.get())
        props_file = path / "server.properties"
        try:
            with open(props_file, "w") as f:
                f.write("#Minecraft server properties\n")
                f.write(f"#Saved on {datetime.now().strftime('%a %b %d %H:%M:%S MSK %Y')}\n")
                for key, var in self.props_vars.items():
                    f.write(f"{key}={var.get()}\n")
            self.log("Настройки сервера сохранены.")
            messagebox.showinfo("Успех", "Настройки сервера сохранены!")
        except Exception as e:
            self.log(f"Ошибка сохранения server.properties: {e}")
            messagebox.showerror("Ошибка", f"Не удалось сохранить настройки:\n{str(e)}")

    def reset_server_properties(self):
        """Сбрасывает настройки к стандартным"""
        result = messagebox.askyesno("Сброс настроек", "Вы уверены, что хотите сбросить все настройки к стандартным?")
        if not result:
            return
        path = Path(self.server_path.get())
        props_file = path / "server.properties"
        try:
            props_file.unlink(missing_ok=True)
            self.load_server_properties() # Перезагружаем стандартные значения
            self.log("Настройки сервера сброшены к стандартным.")
            messagebox.showinfo("Успех", "Настройки сброшены! Изменения вступят в силу после перезапуска сервера.")
        except Exception as e:
            self.log(f"Ошибка сброса server.properties: {e}")
            messagebox.showerror("Ошибка", f"Не удалось сбросить настройки:\n{str(e)}")

    # --- Виджеты для вкладки "Менеджер плагинов" ---
    def create_plugin_widgets(self):
        # Поиск
        search_frame = tk.Frame(self.plugins_frame)
        search_frame.pack(fill="x", padx=5, pady=5)
        tk.Label(search_frame, text="🔍 Поиск:").pack(side="left")
        self.plugin_search_var = tk.StringVar()
        self.plugin_search_var.trace_add("write", self.filter_plugins)
        tk.Entry(search_frame, textvariable=self.plugin_search_var).pack(side="left", fill="x", expand=True, padx=5)

        # Список плагинов
        list_frame = tk.Frame(self.plugins_frame)
        list_frame.pack(fill="both", expand=True, padx=5, pady=5)
        self.plugin_listbox = tk.Listbox(list_frame)
        self.plugin_listbox.pack(side="left", fill="both", expand=True)
        self.plugin_listbox.bind('<<ListboxSelect>>', self.on_plugin_select)

        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.plugin_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.plugin_listbox.config(yscrollcommand=scrollbar.set)

        # Информация о плагине
        info_frame = tk.Frame(self.plugins_frame, relief="groove", bd=1)
        info_frame.pack(fill="x", padx=5, pady=5)
        self.plugin_info_text = tk.Text(info_frame, height=10, state='disabled')
        self.plugin_info_text.pack(fill="both", expand=True)

        # Кнопки
        plugin_btn_frame = tk.Frame(self.plugins_frame)
        plugin_btn_frame.pack(fill="x", padx=5, pady=5)
        tk.Button(plugin_btn_frame, text="🌐 Открыть сайт", command=self.open_plugin_url, bg=COLORS["primary"], fg="white").pack(side="left", padx=5)
        tk.Button(plugin_btn_frame, text="⬇️ Установить", command=self.install_plugin, bg=COLORS["success"], fg="white").pack(side="left", padx=5)
        tk.Button(plugin_btn_frame, text="🗑 Удалить", command=self.remove_plugin, bg=COLORS["danger"], fg="white").pack(side="left", padx=5)

        self.populate_plugin_list()

    def populate_plugin_list(self):
        self.plugin_listbox.delete(0, tk.END)
        for plugin in PLUGINS_DB:
            self.plugin_listbox.insert(tk.END, plugin["name"])

    def filter_plugins(self, *args):
        search_term = self.plugin_search_var.get().lower()
        self.plugin_listbox.delete(0, tk.END)
        for plugin in PLUGINS_DB:
            if search_term in plugin["name"].lower() or search_term in plugin["description"].lower():
                self.plugin_listbox.insert(tk.END, plugin["name"])

    def on_plugin_select(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            plugin_name = event.widget.get(index)
            plugin = next((p for p in PLUGINS_DB if p["name"] == plugin_name), None)
            if plugin:
                self.display_plugin_info(plugin)

    def display_plugin_info(self, plugin):
        info = f"Название: {plugin['name']}\n"
        info += f"Версия: {plugin['version']}\n"
        info += f"Скачиваний: {plugin['downloads']}\n"
        info += f"Рейтинг: {plugin['rating']}\n"
        info += f"Совместимость: {plugin['compatible']}\n"
        info += f"Описание: {plugin['description']}\n"
        if plugin.get("features"):
            info += f"Основные функции:\n"
            for feature in plugin["features"]:
                info += f"  • {feature}\n"
        if plugin.get("dependencies"):
            info += f"Зависимости:\n"
            for dep in plugin["dependencies"]:
                info += f"  • {dep}\n"
        info += f"Подробнее: {plugin['url']}\n"
        self.plugin_info_text.config(state='normal')
        self.plugin_info_text.delete(1.0, tk.END)
        self.plugin_info_text.insert(tk.END, info)
        self.plugin_info_text.config(state='disabled')
        self.selected_plugin.set(plugin['name'])

    def open_plugin_url(self):
        plugin_name = self.selected_plugin.get()
        if plugin_name:
            plugin = next((p for p in PLUGINS_DB if p["name"] == plugin_name), None)
            if plugin:
                webbrowser.open(plugin["url"])
            else:
                messagebox.showwarning("Плагин не найден", "Выбранный плагин не найден в базе данных.")
        else:
            messagebox.showwarning("Плагин не выбран", "Пожалуйста, выберите плагин из списка.")

    def install_plugin(self):
        plugin_name = self.selected_plugin.get()
        if plugin_name:
            plugin = next((p for p in PLUGINS_DB if p["name"] == plugin_name), None)
            if plugin:
                # В реальной программе здесь должен быть код для скачивания .jar файла
                # и его копирования в папку plugins.
                # Так как автоматическое скачивание нежелательно, просто открываем сайт.
                messagebox.showinfo("Установка плагина", f"Для установки плагина '{plugin_name}' перейдите на его страницу и скачайте .jar файл вручную. Затем поместите его в папку 'plugins' вашего сервера.")
                webbrowser.open(plugin["url"])
                self.log(f"Открыта страница для установки плагина: {plugin_name}")
            else:
                messagebox.showwarning("Плагин не найден", "Выбранный плагин не найден в базе данных.")
        else:
            messagebox.showwarning("Плагин не выбран", "Пожалуйста, выберите плагин из списка.")

    def remove_plugin(self):
        plugin_name = self.selected_plugin.get()
        if plugin_name:
            # В реальной программе здесь должен быть код для поиска и удаления .jar файла
            # из папки plugins. Так как у нас нет прямого доступа к файлам плагинов,
            # просто показываем сообщение.
            messagebox.showinfo("Удаление плагина", f"Для удаления плагина '{plugin_name}' найдите соответствующий .jar файл в папке 'plugins' вашего сервера и удалите его вручную.")
            self.log(f"Инструкция по удалению плагина: {plugin_name}")
        else:
            messagebox.showwarning("Плагин не выбран", "Пожалуйста, выберите плагин из списка.")

    # --- Виджеты для вкладки "Бэкапы" ---
    def create_backup_widgets(self):
        # Список бэкапов
        list_frame = tk.Frame(self.backups_frame)
        list_frame.pack(fill="both", expand=True, padx=5, pady=5)
        self.backup_listbox = tk.Listbox(list_frame)
        self.backup_listbox.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.backup_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.backup_listbox.config(yscrollcommand=scrollbar.set)

        # Кнопки
        backup_btn_frame = tk.Frame(self.backups_frame)
        backup_btn_frame.pack(fill="x", padx=5, pady=5)
        tk.Button(backup_btn_frame, text="➕ Создать бэкап", command=self.create_backup, bg=COLORS["success"], fg="white").pack(side="left", padx=5)
        tk.Button(backup_btn_frame, text="🔄 Восстановить", command=self.restore_backup, bg=COLORS["warning"], fg="white").pack(side="left", padx=5)
        tk.Button(backup_btn_frame, text="🗑 Удалить", command=self.delete_backup, bg=COLORS["danger"], fg="white").pack(side="left", padx=5)

        self.refresh_backups_list()

    def refresh_backups_list(self):
        self.backup_listbox.delete(0, tk.END)
        path = Path(self.server_path.get()) / "backups"
        if path.exists():
            backups = sorted(path.glob("*.zip"), key=os.path.getmtime, reverse=True)
            for backup in backups:
                self.backup_listbox.insert(tk.END, backup.name)

    def create_backup(self):
        path = Path(self.server_path.get())
        backups_path = path / "backups"
        backups_path.mkdir(exist_ok=True)
        backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        backup_file = backups_path / backup_name
        try:
            with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(path):
                    # Исключаем папку backups из архива
                    dirs[:] = [d for d in dirs if os.path.join(root, d) != str(backups_path)]
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, path)
                        zipf.write(file_path, arcname)
            self.log(f"✅ Бэкап создан: {backup_name}")
            messagebox.showinfo("Успех", f"Бэкап {backup_name} успешно создан!")
            self.refresh_backups_list()
        except Exception as e:
            self.log(f"❌ Ошибка создания бэкапа: {e}")
            messagebox.showerror("Ошибка", f"Не удалось создать бэкап:\n{str(e)}")

    def restore_backup(self):
        selection = self.backup_listbox.curselection()
        if not selection:
            messagebox.showwarning("Бэкап не выбран", "Пожалуйста, выберите бэкап из списка.")
            return
        backup_name = self.backup_listbox.get(selection[0])
        result = messagebox.askyesno("Подтверждение восстановления",
                                     f"Вы уверены, что хотите восстановить сервер из бэкапа {backup_name}? Это перезапишет текущие файлы сервера.")
        if result:
            path = Path(self.server_path.get())
            backups_path = path / "backups"
            backup_file = backups_path / backup_name
            try:
                # Останавливаем сервер, если он запущен
                if self.server_process:
                    self.stop_server()
                    time.sleep(2) # Небольшая задержка

                # Создаем временную папку для распаковки
                temp_restore = path / "temp_restore"
                if temp_restore.exists():
                    shutil.rmtree(temp_restore)
                temp_restore.mkdir()

                # Распаковываем бэкап во временную папку
                with zipfile.ZipFile(backup_file, 'r') as zipf:
                    zipf.extractall(temp_restore)

                # Перемещаем файлы из временной папки в папку сервера, исключая backups
                for item in temp_restore.iterdir():
                    if item.name != "backups":
                        if (path / item.name).exists():
                            if (path / item.name).is_dir():
                                shutil.rmtree(path / item.name)
                            else:
                                (path / item.name).unlink()
                        shutil.move(str(item), str(path / item.name))

                # Удаляем временную папку
                shutil.rmtree(temp_restore)

                self.log(f"✅ Восстановление из бэкапа {backup_name} завершено!")
                messagebox.showinfo("Успех", f"Сервер восстановлен из бэкапа: {backup_name}")
                self.load_server_properties() # Обновляем настройки в интерфейсе
            except Exception as e:
                self.log(f"❌ Ошибка восстановления: {e}")
                messagebox.showerror("Ошибка", f"Не удалось восстановить сервер:\n{str(e)}")

    def delete_backup(self):
        selection = self.backup_listbox.curselection()
        if not selection:
            messagebox.showwarning("Бэкап не выбран", "Пожалуйста, выберите бэкап из списка.")
            return
        backup_name = self.backup_listbox.get(selection[0])
        result = messagebox.askyesno("Подтверждение удаления",
                                     f"Вы уверены, что хотите удалить бэкап {backup_name}? Это действие нельзя отменить.")
        if result:
            path = Path(self.server_path.get()) / "backups" / backup_name
            try:
                path.unlink()
                self.log(f"✅ Бэкап {backup_name} удален!")
                messagebox.showinfo("Успех", f"Бэкап {backup_name} успешно удален!")
                self.refresh_backups_list()
            except Exception as e:
                self.log(f"❌ Ошибка удаления бэкапа: {e}")
                messagebox.showerror("Ошибка", f"Не удалось удалить бэкап:\n{str(e)}")

    # --- Виджеты для вкладки "Планировщик" ---
    def create_scheduler_widgets(self):
        # Список задач
        list_frame = tk.Frame(self.scheduler_frame)
        list_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        columns = ("time", "task", "enabled")
        self.tasks_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)
        self.tasks_tree.heading("time", text="Время")
        self.tasks_tree.heading("task", text="Задача")
        self.tasks_tree.heading("enabled", text="Включено")
        self.tasks_tree.column("time", width=100)
        self.tasks_tree.column("task", width=300)
        self.tasks_tree.column("enabled", width=80)
        self.tasks_tree.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tasks_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tasks_tree.configure(yscrollcommand=scrollbar.set)
        
        # Кнопки
        task_btn_frame = tk.Frame(self.scheduler_frame)
        task_btn_frame.pack(fill="x", padx=5, pady=5)
        tk.Button(task_btn_frame, text="➕ Добавить", command=self.add_task, bg=COLORS["success"], fg="white").pack(side="left", padx=5)
        tk.Button(task_btn_frame, text="✏️ Редактировать", command=self.edit_task, bg=COLORS["primary"], fg="white").pack(side="left", padx=5)
        tk.Button(task_btn_frame, text="🗑 Удалить", command=self.delete_task, bg=COLORS["danger"], fg="white").pack(side="left", padx=5)
        
        # Привязка двойного клика для редактирования
        self.tasks_tree.bind("<Double-1>", lambda e: self.edit_task())

    def populate_tasks_list(self):
        """Заполняет список задач из базы данных"""
        for item in self.tasks_tree.get_children():
            self.tasks_tree.delete(item)
        for task in TASKS_DB:
            enabled_text = "Да" if task["enabled"] else "Нет"
            self.tasks_tree.insert("", "end", values=(task["time"], task["task"], enabled_text))

    def add_task(self):
        """Добавляет новую задачу"""
        task_window = tk.Toplevel(self.root)
        task_window.title("Добавить задачу")
        task_window.geometry("400x200")
        task_window.transient(self.root)
        task_window.grab_set()
        # Центрируем окно
        task_window.geometry("+%d+%d" % (self.root.winfo_rootx() + 50,
                                        self.root.winfo_rooty() + 50))

        # Форма добавления задачи
        form_frame = ttk.Frame(task_window)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ttk.Label(form_frame, text="Время (ЧЧ:ММ):").grid(row=0, column=0, sticky="w", pady=5)
        time_entry = ttk.Entry(form_frame, width=10)
        time_entry.grid(row=0, column=1, sticky="w", pady=5, padx=(10, 0))

        ttk.Label(form_frame, text="Задача:").grid(row=1, column=0, sticky="w", pady=5)
        task_entry = ttk.Entry(form_frame, width=30)
        task_entry.grid(row=1, column=1, sticky="w", pady=5, padx=(10, 0))

        enabled_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(form_frame, text="Включено", variable=enabled_var).grid(row=2, column=0, columnspan=2, sticky="w", pady=10)

        # Кнопки
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)

        def save_new_task():
            time_str = time_entry.get().strip()
            task_name = task_entry.get().strip()
            enabled = enabled_var.get()
            if not time_str or not task_name:
                messagebox.showerror("Ошибка", "Заполните все поля!")
                return
            # Проверка формата времени
            if not re.match(r"^\d{2}:\d{2}$", time_str):
                messagebox.showerror("Ошибка", "Неверный формат времени (ЧЧ:ММ)")
                return
            
            enabled_text = "Да" if enabled else "Нет"
            self.tasks_tree.insert("", "end", values=(time_str, task_name, enabled_text))
            task_window.destroy()

        ttk.Button(btn_frame, text="Сохранить", command=save_new_task, style="Primary.TButton").pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Отмена", command=task_window.destroy).pack(side="left", padx=5)

    def edit_task(self):
        """Редактирует выбранную задачу"""
        selected = self.tasks_tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите задачу для редактирования!")
            return
        values = self.tasks_tree.item(selected[0], "values")
        
        task_window = tk.Toplevel(self.root)
        task_window.title("Редактировать задачу")
        task_window.geometry("400x200")
        task_window.transient(self.root)
        task_window.grab_set()
        # Центрируем окно
        task_window.geometry("+%d+%d" % (self.root.winfo_rootx() + 50,
                                        self.root.winfo_rooty() + 50))

        # Форма редактирования задачи
        form_frame = ttk.Frame(task_window)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ttk.Label(form_frame, text="Время (ЧЧ:ММ):").grid(row=0, column=0, sticky="w", pady=5)
        time_entry = ttk.Entry(form_frame, width=10)
        time_entry.grid(row=0, column=1, sticky="w", pady=5, padx=(10, 0))
        time_entry.insert(0, values[0])

        ttk.Label(form_frame, text="Задача:").grid(row=1, column=0, sticky="w", pady=5)
        task_entry = ttk.Entry(form_frame, width=30)
        task_entry.grid(row=1, column=1, sticky="w", pady=5, padx=(10, 0))
        task_entry.insert(0, values[1])

        enabled_var = tk.BooleanVar(value=values[2] == "Да")
        ttk.Checkbutton(form_frame, text="Включено", variable=enabled_var).grid(row=2, column=0, columnspan=2, sticky="w", pady=10)

        # Кнопки
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)

        def update_task():
            time_str = time_entry.get().strip()
            task_name = task_entry.get().strip()
            enabled = enabled_var.get()
            if not time_str or not task_name:
                messagebox.showerror("Ошибка", "Заполните все поля!")
                return
            # Проверка формата времени
            if not re.match(r"^\d{2}:\d{2}$", time_str):
                messagebox.showerror("Ошибка", "Неверный формат времени (ЧЧ:ММ)")
                return
            
            enabled_text = "Да" if enabled else "Нет"
            self.tasks_tree.item(selected[0], values=(time_str, task_name, enabled_text))
            task_window.destroy()

        ttk.Button(btn_frame, text="Сохранить", command=update_task, style="Primary.TButton").pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Отмена", command=task_window.destroy).pack(side="left", padx=5)

    def delete_task(self):
        """Удаляет выбранную задачу"""
        selected = self.tasks_tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите задачу для удаления!")
            return
        result = messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить выбранную задачу?")
        if result:
            self.tasks_tree.delete(selected[0])
            
    # --- Виджеты для вкладки "Оптимизация" ---
    def create_optimization_widgets(self):
        opt_frame = tk.Frame(self.optimization_frame, bg=COLORS["card"])
        opt_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        tk.Label(opt_frame, text="🔧 Рекомендации по оптимизации", font=("Arial", 12, "bold"), bg=COLORS["card"]).pack(anchor="w", pady=(0, 10))
        
        self.optimization_text = tk.Text(opt_frame, height=15, state='disabled')
        self.optimization_text.pack(fill="both", expand=True, pady=(0, 10))
        
        btn_frame = tk.Frame(opt_frame, bg=COLORS["card"])
        btn_frame.pack(fill="x")
        tk.Button(btn_frame, text="Анализ логов", command=self.analyze_logs, bg=COLORS["primary"], fg="white").pack(side="left", padx=5)
        tk.Button(btn_frame, text="Проверить TPS", command=self.check_tps, bg=COLORS["info"], fg="white").pack(side="left", padx=5)
        tk.Button(btn_frame, text="Обновить рекомендации", command=self.refresh_diagnostics, bg=COLORS["success"], fg="white").pack(side="left", padx=5)

    def analyze_logs(self):
        """Анализирует логи сервера"""
        self.log("Анализ логов...")
        issues = []
        suggestions = []
        # Простой анализ последних логов
        for log_line in self.logs[-100:]: # Анализируем последние 100 строк
            if "WARN" in log_line:
                issues.append(f"Предупреждение в логах: {log_line}")
            elif "ERROR" in log_line:
                issues.append(f"Ошибка в логах: {log_line}")
            elif "lag" in log_line.lower() or "slow" in log_line.lower():
                issues.append(f"Возможная задержка: {log_line}")

        if issues:
            self.optimization_text.config(state='normal')
            self.optimization_text.delete(1.0, tk.END)
            self.optimization_text.insert(tk.END, "⚠️ Найдены потенциальные проблемы:\n")
            for issue in issues:
                self.optimization_text.insert(tk.END, f"  • {issue}\n")
            self.optimization_text.config(state='disabled')
        else:
            self.optimization_text.config(state='normal')
            self.optimization_text.delete(1.0, tk.END)
            self.optimization_text.insert(tk.END, "✅ В логах не найдено критических проблем.\n")
            self.optimization_text.config(state='disabled')

    def check_tps(self):
        """Проверяет TPS сервера (имитация)"""
        # В реальном приложении это требует подключения к серверу (например, через RCON)
        # или анализа логов на предмет сообщений о TPS
        self.log("Проверка TPS...")
        # Имитация TPS
        import random
        tps = random.uniform(18.0, 20.0)
        if tps < 15.0:
            self.diag_label.config(text="🔴 Очень низкий TPS! Рассмотрите оптимизацию", fg=COLORS["danger"])
        elif tps < 19.0:
            self.diag_label.config(text="⚠️ Низкий TPS. Рассмотрите оптимизацию", fg=COLORS["warning"])
        else:
            self.diag_label.config(text="✅ Сервер работает нормально", fg=COLORS["success"])
        self.log(f"TPS: {tps:.2f}")

    # --- Функции для работы с логами ---
    def filter_logs(self, event=None):
        """Фильтрует логи (заглушка)"""
        filter_text = self.log_filter_var.get()
        self.log(f"Фильтрация логов по: '{filter_text}' (функция не реализована полностью)")
        # В реальном приложении здесь была бы логика фильтрации
        
    def clear_logs(self):
        """Очищает логи"""
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')
        self.logs.clear()
        self.log("Логи очищены.")

    def save_logs(self):
        """Сохраняет логи в файл"""
        logs_content = "\n".join(self.logs)
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Сохранить логи"
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(logs_content)
                self.log(f"Логи сохранены в: {file_path}")
                messagebox.showinfo("Успех", "Логи успешно сохранены!")
            except Exception as e:
                self.log(f"Ошибка сохранения логов: {e}")
                messagebox.showerror("Ошибка", f"Не удалось сохранить логи:\n{str(e)}")

    # --- Диагностика ---
    def refresh_diagnostics(self):
        self.update_connection_info()
        self.analyze_server()
        self.log("Диагностическая информация обновлена")

    def update_connection_info(self):
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            self.local_ip.config(text=local_ip, fg=COLORS["success"])
        except Exception:
            self.local_ip.config(text="Не определен", fg=COLORS["danger"])

        try:
            response = requests.get("https://api.ipify.org", timeout=5)
            public_ip = response.text
            self.public_ip.config(text=public_ip, fg=COLORS["success"])
        except Exception:
            self.public_ip.config(text="Не определен", fg=COLORS["danger"])

    def analyze_server(self):
        path = Path(self.server_path.get())
        issues = []
        suggestions = []

        # Проверка eula.txt
        eula_file = path / "eula.txt"
        if not eula_file.exists():
            issues.append("❌ Файл eula.txt не найден.")
        else:
            with open(eula_file, 'r') as f:
                if 'eula=true' not in f.read():
                    issues.append("❌ Лицензионное соглашение (eula.txt) не принято.")
                else:
                    suggestions.append("✅ Лицензионное соглашение принято.")

        # Проверка server.properties
        props_file = path / "server.properties"
        if props_file.exists():
            with open(props_file, 'r') as f:
                props_content = f.read()
                if 'online-mode=false' in props_content:
                    issues.append("⚠️ Рекомендуется включить online-mode=true для безопасности.")
                if 'view-distance=12' in props_content or 'view-distance=16' in props_content or 'view-distance=14' in props_content:
                    suggestions.append("💡 Рассмотрите уменьшение view-distance до 8 или 10 для лучшей производительности.")

        # Проверка памяти (примерная)
        allocated_memory_gb = int(self.memory.get())
        total_ram_gb = self.get_total_ram_gb()
        if allocated_memory_gb > total_ram_gb * 0.8:
            issues.append(f"⚠️ Выделено много памяти ({allocated_memory_gb}ГБ). Рекомендуется не более 80% от {total_ram_gb}ГБ.")

        # Проверка наличия start скрипта
        start_script = path / ("start.bat" if os.name == 'nt' else "start.sh")
        if not start_script.exists():
            issues.append("⚠️ Скрипт запуска (start.bat/sh) не найден. Он будет создан при следующем создании/запуске сервера.")

        if not issues and not suggestions:
            self.diag_label.config(text="✅ Сервер настроен оптимально", fg=COLORS["success"])
        else:
            diag_text = ""
            if issues:
                diag_text += "Проблемы:\n" + "\n".join(issues) + "\n\n"
            if suggestions:
                diag_text += "Рекомендации:\n" + "\n".join(suggestions)
            self.diag_label.config(text=diag_text, fg=COLORS["warning"] if issues else COLORS["info"])

# --- Запуск приложения ---
if __name__ == "__main__":
    # Проверяем права администратора (для Windows)
    if os.name == 'nt':
        try:
            is_admin = os.getuid() == 0
        except AttributeError:
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        if not is_admin:
            messagebox.showwarning("Права доступа", "Запустите программу от имени администратора для корректной работы!")

    root = tk.Tk()
    app = MinecraftServerManager(root)
    root.mainloop()