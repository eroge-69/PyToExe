#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# --- Основные импорты ---
import sys
import subprocess
import importlib
import hashlib
import asyncio
import json
import platform
import time
import os
import socket
from datetime import datetime
from collections import deque
import signal
import secrets
from tempfile import NamedTemporaryFile
import threading
import queue
import re

# --- Автоматическая установка и импорт зависимостей ---
def install_and_import(package, pip_name=None):
    try:
        importlib.import_module(package)
    except ImportError:
        pip_name = pip_name or package
        print(f"Installing required library: {pip_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", pip_name])
    finally:
        globals()[package] = importlib.import_module(package)

required_libraries = [
    ("colorama", None), ("psutil", None), ("PIL", "pillow"), ("tkinter", None),
    ("dns", "dnspython"), ("cpuinfo", "py-cpuinfo"), ("matplotlib", None)
]
for lib in required_libraries:
    install_and_import(lib[0], lib[1])

# --- Импорты из установленных библиотек ---
from colorama import Fore, init
import psutil
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import webbrowser
import dns.resolver
import cpuinfo
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np

init(autoreset=True)

# --- Вспомогательные функции ---
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# --- Система конфигурации ---
DEFAULT_WALLET = ""  # По умолчанию кошелек пустой
CONFIG_FILE = "config.json"

def load_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            return config.get("wallet", DEFAULT_WALLET)
    except (FileNotFoundError, json.JSONDecodeError):
        save_config(DEFAULT_WALLET)
        return DEFAULT_WALLET

def save_config(wallet_address):
    with open(CONFIG_FILE, 'w') as f:
        json.dump({"wallet": wallet_address}, f, indent=4)

# --- Глобальные переменные и константы ---
SERVER_HOST = "nyxaro.ru"
SERVER_PORT = 2025
WALLET = load_config()
REPORTING_BATCH_SIZE = 10000

# Цветовая схема GUI
PREMIUM_DARK_BG, CARD_BG = "#1A1D24", "#242831"
ACCENT_GOLD, ACCENT_CYAN = "#FFD700", "#00FFFF"
TEXT_LIGHT, TEXT_DARK = "#EAECEE", "#A9A9A9"
SUCCESS_COLOR, WARNING_COLOR, ERROR_COLOR = "#4CAF50", "#FFC107", "#F44336"
BORDER_COLOR, INFO_COLOR = "#3A3F4C", "#9C27B0"

stats = {
    "hashes": 0, "accepted": 0, "rejected": 0, "balance": 0.000,
    "session_earnings": 0.000, "hashrates_history": deque(maxlen=120), "max_hashrate": 0
}
stats_lock = threading.Lock()
running = True

# =============================================================================
# === Вспомогательные классы для GUI ==========================================
# =============================================================================

class SystemInfoWindow(tk.Toplevel):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.title("System Info")
        self.geometry("450x200")
        self.resizable(False, False)
        self.configure(bg=PREMIUM_DARK_BG)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.create_widgets()
        threading.Thread(target=self.fetch_and_display_info, daemon=True).start()

    def create_widgets(self):
        main_frame = ttk.Frame(self, style='Card.TFrame', padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        main_frame.grid_columnconfigure(1, weight=1)
        ttk.Label(main_frame, text="Processor (CPU):", style='Card.TLabel', font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, sticky="w", pady=5)
        self.cpu_label = ttk.Label(main_frame, text="Loading...", style='Card.TLabel', font=('Segoe UI', 10))
        self.cpu_label.grid(row=0, column=1, sticky="w", padx=10)
        ttk.Label(main_frame, text="Graphics (GPU):", style='Card.TLabel', font=('Segoe UI', 10, 'bold')).grid(row=1, column=0, sticky="w", pady=5)
        self.gpu_label = ttk.Label(main_frame, text="Loading...", style='Card.TLabel', font=('Segoe UI', 10))
        self.gpu_label.grid(row=1, column=1, sticky="w", padx=10)
        ttk.Label(main_frame, text="Memory (RAM):", style='Card.TLabel', font=('Segoe UI', 10, 'bold')).grid(row=2, column=0, sticky="w", pady=5)
        self.ram_label = ttk.Label(main_frame, text="Loading...", style='Card.TLabel', font=('Segoe UI', 10))
        self.ram_label.grid(row=2, column=1, sticky="w", padx=10)

    def _get_gpu_info(self):
        try:
            system = platform.system()
            if system == "Windows":
                command = "wmic path win32_videocontroller get name"
                output = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.DEVNULL)
                gpus = [line.strip() for line in output.split('\n') if line.strip() and line.strip() != "Name"]
                return ", ".join(gpus) if gpus else "N/A"
            elif system == "Linux":
                command = "lspci | grep -i 'vga\\|3d\\|2d'"
                output = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.DEVNULL)
                gpus = [line.split(":")[-1].strip() for line in output.strip().split('\n')]
                return ", ".join(gpus) if gpus else "N/A"
            elif system == "Darwin":
                command = "system_profiler SPDisplaysDataType"
                output = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.DEVNULL)
                for line in output.split('\n'):
                    if "Chipset Model:" in line: return line.split(":")[-1].strip()
                return "N/A"
            return "N/A (Unsupported OS)"
        except Exception:
            return "Could not determine GPU"

    def fetch_and_display_info(self):
        cpu_info = get_cpu_info()
        gpu_info = self._get_gpu_info()
        ram_info = f"{psutil.virtual_memory().total / (1024**3):.2f} GB"
        self.after(0, self.update_labels, cpu_info, gpu_info, ram_info)

    def update_labels(self, cpu, gpu, ram):
        self.cpu_label.config(text=cpu)
        self.gpu_label.config(text=gpu)
        self.ram_label.config(text=ram)

    def on_close(self):
        self.controller.sys_info_window = None
        self.destroy()

class RestartDialog(tk.Toplevel):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.title("Success")
        self.geometry("450x150")
        self.resizable(False, False)
        self.configure(bg=PREMIUM_DARK_BG)
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.create_widgets()
        self.transient(master)
        self.grab_set()

    def create_widgets(self):
        main_frame = ttk.Frame(self, style='TFrame', padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        message = "Адрес кошелька успешно изменен и сохранен.\n\nИзменения вступят в силу для воркеров после перезапуска майнинга."
        ttk.Label(main_frame, text=message, style='TLabel', justify=tk.LEFT).pack(anchor="w", expand=True, fill=tk.X)
        button_frame = ttk.Frame(main_frame, style='TFrame')
        button_frame.pack(fill=tk.X, pady=(20, 0))
        ttk.Button(button_frame, text="Restart", style='Gold.TButton', command=self.controller.restart_application).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="OK", style='Secondary.TButton', command=self.destroy).pack(side=tk.RIGHT, padx=(0, 10))

class ChangeWalletWindow(tk.Toplevel):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.title("Change Wallet Address")
        self.geometry("500x150")
        self.resizable(False, False)
        self.configure(bg=PREMIUM_DARK_BG)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.create_widgets()
        self.transient(master)
        self.grab_set()

    def create_widgets(self):
        main_frame = ttk.Frame(self, style='TFrame', padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(main_frame, text="Enter new BetaCoin wallet address:", style='TLabel').pack(anchor="w")
        self.wallet_entry = ttk.Entry(main_frame, font=('Consolas', 10), width=50)
        self.wallet_entry.pack(fill=tk.X, pady=10)
        self.wallet_entry.insert(0, WALLET)
        button_frame = ttk.Frame(main_frame, style='TFrame')
        button_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(button_frame, text="Save", style='Gold.TButton', command=self.save_wallet).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="Cancel", style='Secondary.TButton', command=self.on_close).pack(side=tk.RIGHT, padx=(0, 10))

    def save_wallet(self):
        new_wallet = self.wallet_entry.get().strip()
        if not new_wallet.startswith("BC") or len(new_wallet) != 42:
            messagebox.showerror("Invalid Address", "Возможно вы вписали адрес кошелька некорректно, либо он не от BetaCoin, попробуйте еще раз.", parent=self)
            return
        is_confirmed = messagebox.askyesno("Confirm Address", f"Проверьте правильно ли вы написали адрес кошелька:\n\n{new_wallet}", icon='warning', detail="Нажмите 'Yes' для подтверждения, 'No' для отмены.", parent=self)
        if is_confirmed:
            self.controller.update_wallet(new_wallet)
            self.on_close()

    def on_close(self):
        self.controller.wallet_window = None
        self.destroy()

class QueueLogger:
    def __init__(self, log_queue): self.log_queue, self.line_buffer = log_queue, ""
    def write(self, text):
        self.line_buffer += text
        if '\n' in self.line_buffer:
            lines = self.line_buffer.split('\n')
            for line in lines[:-1]:
                if line.strip(): self.log_queue.put(line)
            self.line_buffer = lines[-1]
    def flush(self): pass

# =============================================================================
# === Основной класс приложения (GUI) =========================================
# =============================================================================
class MinerGUI:
    def __init__(self, root):
        self.root = root
        self.cpu_name = get_cpu_info()
        self.root.title(f"UTKminer [BetaCoin] v1.7 BETA | {self.cpu_name}")
        self.root.geometry("1000x750")
        self.root.minsize(908, 789)
        self.root.configure(bg=PREMIUM_DARK_BG)
        
        self.miner_threads, self.child_processes = [], []
        self.log_queue = queue.Queue()
        self.worker_hashrates = {}
        self.wallet_window = None
        self.sys_info_window = None

        self.setup_icon()
        self.setup_styles()
        self.create_widgets()

        self.start_time = time.time()
        self.process_log_queue()
        self.update_ui()

    def setup_icon(self):
        try:
            icon_path = resource_path(os.path.join("Resourses", "ico.png"))
            if not os.path.exists(icon_path):
                self.log_queue.put(f"warning: Icon file not found: {icon_path}")
                return
            with Image.open(icon_path) as img:
                img_resized = img.resize((256, 256), Image.Resampling.LANCZOS)
                with NamedTemporaryFile(delete=False, suffix='.ico') as tmp:
                    img_resized.save(tmp.name, format='ICO')
                    self.root.iconbitmap(tmp.name)
                os.unlink(tmp.name)
        except Exception as e:
            self.log_queue.put(f"error: Failed to set application icon: {e}")

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('.', background=PREMIUM_DARK_BG, foreground=TEXT_LIGHT, borderwidth=0, focusthickness=0)
        self.style.configure('TFrame', background=PREMIUM_DARK_BG)
        self.style.configure('TLabel', background=PREMIUM_DARK_BG, foreground=TEXT_LIGHT, font=('Segoe UI', 10))
        self.style.configure('TButton', background=CARD_BG, foreground=TEXT_LIGHT, font=('Segoe UI', 10), padding=(10, 8))
        self.style.map('TButton', background=[('active', '#3c414d'), ('pressed', '#4a4f5c')])
        self.style.configure('Card.TFrame', background=CARD_BG, relief=tk.SOLID, borderwidth=1, bordercolor=BORDER_COLOR)
        self.style.configure('Card.TLabel', background=CARD_BG, foreground=TEXT_LIGHT)
        self.style.configure('Gold.TButton', background=ACCENT_GOLD, foreground=PREMIUM_DARK_BG, font=('Segoe UI', 11, 'bold'),padding=(15, 10), borderwidth=2, relief=tk.RAISED)
        self.style.map('Gold.TButton', background=[('active', '#ffeb80'), ('pressed', '#e6c200')], relief=[('pressed', 'sunken'), ('!pressed', 'raised')])
        self.style.configure('Red.TButton', background=ERROR_COLOR, foreground=TEXT_LIGHT, font=('Segoe UI', 11, 'bold'), padding=(15, 10), borderwidth=2, relief=tk.RAISED)
        self.style.map('Red.TButton', background=[('active', '#ff7961'), ('pressed', '#ba000d')], relief=[('pressed', 'sunken'), ('!pressed', 'raised')])
        self.style.configure('Secondary.TButton', background='#3A3F4C', foreground=TEXT_LIGHT, font=('Segoe UI', 10))
        self.style.map('Secondary.TButton', background=[('active', '#4a4f5c')])
        self.style.configure('TCombobox', fieldbackground=CARD_BG, background=CARD_BG, foreground=TEXT_LIGHT, arrowcolor=TEXT_LIGHT, selectbackground=CARD_BG, selectforeground=TEXT_LIGHT, borderwidth=1, padding=5)
        self.style.map('TCombobox', fieldbackground=[('readonly', CARD_BG)], foreground=[('readonly', TEXT_LIGHT)])
        self.style.configure('TEntry', fieldbackground=CARD_BG, foreground=TEXT_LIGHT, insertcolor=ACCENT_GOLD, borderwidth=1, relief=tk.FLAT)
        self.style.map('TEntry', fieldbackground=[('focus', CARD_BG), ('!disabled', CARD_BG)], foreground=[('focus', TEXT_LIGHT), ('!disabled', TEXT_LIGHT)])

    def create_widgets(self):
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.create_header()
        self.create_stats_grid()
        self.create_main_content()
        self.create_footer()

    def create_header(self):
        header_frame = ttk.Frame(self.main_frame)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        
        try:
            logo_path = resource_path(os.path.join("Resourses", "ico.png"))
            if os.path.exists(logo_path):
                with Image.open(logo_path) as img:
                    logo_img_resized = img.resize((64, 64), Image.Resampling.LANCZOS)
                    self.logo_img = ImageTk.PhotoImage(logo_img_resized)
                    ttk.Label(header_frame, image=self.logo_img).pack(side=tk.LEFT, padx=(0, 10))
        except Exception:
            pass

        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT)
        ttk.Label(title_frame, text="UTKminer [BetaCoin]", font=('Segoe UI', 16, 'bold'), foreground=TEXT_LIGHT).pack(anchor=tk.W)
        conn_frame = ttk.Frame(title_frame)
        conn_frame.pack(anchor=tk.W, pady=(5,0))
        ttk.Label(conn_frame, text="Pool:", font=('Segoe UI', 8), foreground=TEXT_DARK).pack(side=tk.LEFT)
        ttk.Label(conn_frame, text=f"{SERVER_HOST}:{SERVER_PORT}", font=('Consolas', 8), foreground=TEXT_LIGHT).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(conn_frame, text="Copy", style='Secondary.TButton', command=lambda: self.copy_to_clipboard(f"{SERVER_HOST}:{SERVER_PORT}"), padding=(2,0)).pack(side=tk.LEFT, padx=(0, 10))
        
        wallet_frame = ttk.Frame(conn_frame)
        wallet_frame.pack(side=tk.LEFT)
        ttk.Label(wallet_frame, text="Wallet:", font=('Segoe UI', 8), foreground=TEXT_DARK).pack(side=tk.LEFT)
        
        wallet_display_text = f"{WALLET[:8]}...{WALLET[-6:]}" if WALLET else "Not Configured. Click 'Change'."
        wallet_color = TEXT_LIGHT if WALLET else WARNING_COLOR
        self.wallet_label = ttk.Label(wallet_frame, text=wallet_display_text, font=('Consolas', 8), foreground=wallet_color)
        self.wallet_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.copy_wallet_button = ttk.Button(wallet_frame, text="Copy", style='Secondary.TButton', command=lambda: self.copy_to_clipboard(WALLET), padding=(2,0))
        self.copy_wallet_button.pack(side=tk.LEFT)
        ttk.Button(wallet_frame, text="Change", style='Secondary.TButton', command=self.open_wallet_window, padding=(2,0)).pack(side=tk.LEFT, padx=(5,0))
        
        button_frame = ttk.Frame(header_frame)
        button_frame.pack(side=tk.RIGHT, padx=10)
        ttk.Button(button_frame, text="System Info", style='Secondary.TButton', command=self.open_system_info_window).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Help", style='Secondary.TButton', command=self.open_help).pack(side=tk.LEFT)

    def create_stats_grid(self):
        stats_frame = ttk.Frame(self.main_frame)
        stats_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 15))
        controls_card = self.create_card(stats_frame, "Miner Controls")
        self.create_miner_controls(controls_card)
        controls_card.pack(fill=tk.X, pady=(0, 15))
        stats_card = self.create_card(stats_frame, "Live Statistics")
        self.create_stats_section(stats_card)
        stats_card.pack(fill=tk.X, pady=(0, 15))
        info_card = self.create_card(stats_frame, "Session Info")
        self.create_info_section(info_card)
        info_card.pack(fill=tk.X, pady=(0, 15))

    def create_main_content(self):
        content_frame = ttk.Frame(self.main_frame)
        content_frame.grid(row=1, column=1, sticky="nsew")
        content_frame.grid_rowconfigure(1, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)
        self.create_graph_section(content_frame)
        self.create_log_section(content_frame)

    def create_card(self, parent, title):
        card = ttk.Frame(parent, style='Card.TFrame', padding=12)
        title_label = ttk.Label(card, text=title.upper(), font=('Segoe UI', 9, 'bold'), foreground=TEXT_DARK, style='Card.TLabel')
        title_label.pack(anchor=tk.W, pady=(0, 8))
        ttk.Separator(card, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(0, 8))
        return card

    def create_miner_controls(self, parent):
        power_frame = ttk.Frame(parent, style='Card.TFrame')
        power_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(power_frame, text="Power Level:", style='Card.TLabel', font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        self.power_selector = ttk.Combobox(power_frame, values=list(range(1, 11)), state="readonly", width=5)
        self.power_selector.set(1)
        self.power_selector.pack(side=tk.LEFT)
        btn_frame = ttk.Frame(parent, style='Card.TFrame')
        btn_frame.pack(fill=tk.X, pady=5)
        self.start_button = ttk.Button(btn_frame, text="START MINING", style='Gold.TButton', command=self.start_mining)
        self.start_button.pack(side=tk.LEFT, expand=True, fill=tk.X, ipady=5)
        self.stop_button = ttk.Button(btn_frame, text="STOP", style='Red.TButton', command=self.stop_mining, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(10, 0), ipady=5)

    def create_stats_section(self, parent):
        self.hashrate_label = self.create_stat_entry(parent, "Total Hashrate", "0.0 kH/s", ACCENT_CYAN, 18)
        self.balance_label = self.create_stat_entry(parent, "Total Balance", "0.0000 BC", ACCENT_CYAN, 18)
        ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8)
        self.accepted_label = self.create_stat_entry(parent, "Accepted Shares", "0", SUCCESS_COLOR)
        self.rejected_label = self.create_stat_entry(parent, "Rejected Shares", "0", WARNING_COLOR)
        ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8)
        self.max_hashrate_label = self.create_stat_entry(parent, "Max Hashrate", "0.0 kH/s")
        self.earnings_label = self.create_stat_entry(parent, "Session Earnings", "0.0000 BC")

    def create_info_section(self, parent):
        self.uptime_label = self.create_stat_entry(parent, "Uptime", "00:00:00")
        self.hashes_label = self.create_stat_entry(parent, "Total Hashes", "0")

    def create_stat_entry(self, parent, title, value, value_color=TEXT_LIGHT, value_size=14):
        frame = ttk.Frame(parent, style='Card.TFrame')
        frame.pack(fill=tk.X, pady=3)
        ttk.Label(frame, text=title, font=('Segoe UI', 9), foreground=TEXT_DARK, style='Card.TLabel').pack(side=tk.LEFT)
        value_label = ttk.Label(frame, text=value, font=('Segoe UI', value_size, 'bold'), foreground=value_color, style='Card.TLabel')
        value_label.pack(side=tk.RIGHT)
        return value_label

    def create_graph_section(self, parent):
        graph_card = self.create_card(parent, "Total Hashrate Performance (H/s)")
        graph_card.grid(row=0, column=0, sticky="nsew", pady=(0, 15))
        self.fig = Figure(figsize=(5, 2.5), dpi=100, facecolor=CARD_BG)
        self.ax = self.fig.add_subplot(111, facecolor=CARD_BG)
        self.fig.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.2)
        
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['bottom'].set_color(BORDER_COLOR)
        self.ax.spines['left'].set_color(BORDER_COLOR)
        self.ax.tick_params(axis='x', colors=TEXT_DARK)
        self.ax.tick_params(axis='y', colors=TEXT_DARK)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_card)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=5)

    def _prevent_log_modification(self, event=None):
        return "break"

    def create_log_section(self, parent):
        log_card = self.create_card(parent, "Mining Log")
        log_card.grid(row=1, column=0, sticky="nsew")
        self.log_text = scrolledtext.ScrolledText(
            log_card, wrap=tk.WORD, bg=PREMIUM_DARK_BG, fg=TEXT_LIGHT,
            insertbackground=ACCENT_GOLD, font=('Consolas', 9), relief=tk.SOLID,
            borderwidth=1, highlightcolor=BORDER_COLOR, padx=10, pady=10
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=5)
        self.log_text.bind("<KeyPress>", self._prevent_log_modification)
        self.log_text.tag_config("timestamp", foreground=TEXT_DARK)
        self.log_text.tag_config("worker", foreground="#888888")
        self.log_text.tag_config("miner", foreground=ACCENT_CYAN)
        self.log_text.tag_config("accepted", foreground=SUCCESS_COLOR, font=('Consolas', 9, 'bold'))
        self.log_text.tag_config("rejected", foreground=WARNING_COLOR)
        self.log_text.tag_config("error", foreground=ERROR_COLOR)
        self.log_text.tag_config("warning", foreground=WARNING_COLOR)
        self.log_text.tag_config("info", foreground=INFO_COLOR)
        self.log_text.tag_config("normal", foreground=TEXT_LIGHT)

    def create_footer(self):
        footer_frame = ttk.Frame(self.main_frame)
        footer_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        self.status_label = ttk.Label(footer_frame, text="Status: Ready", font=('Segoe UI', 9), foreground=TEXT_DARK)
        self.status_label.pack(side=tk.LEFT)
        ttk.Label(footer_frame, text="UTKminer © 2025", font=('Segoe UI', 9), foreground=TEXT_DARK).pack(side=tk.RIGHT)

    def copy_to_clipboard(self, text):
        try:
            self.root.clipboard_clear(); self.root.clipboard_append(text)
            self.log_queue.put(f"info: Copied to clipboard: {text}")
        except tk.TclError: self.log_queue.put("error: Could not access clipboard.")

    def update_graph(self):
        self.ax.clear()
        with stats_lock:
            values = list(stats["hashrates_history"])
        
        if not values:
            self.ax.text(0.5, 0.5, "Waiting for data...", ha='center', va='center', color=TEXT_DARK)
        else:
            x_data = np.arange(len(values))
            self.ax.plot(x_data, values, color=ACCENT_CYAN, linewidth=1.5)
            self.ax.fill_between(x_data, values, color=ACCENT_CYAN, alpha=0.1)
            self.ax.grid(True, color=BORDER_COLOR, linestyle='--', linewidth=0.5, alpha=0.5)
            self.ax.set_ylim(bottom=0)
            self.ax.set_xlim(left=0, right=max(1, len(x_data)-1))
        
        self.canvas.draw()

    def update_ui(self):
        total_hashrate = 0; now = time.time()
        current_workers = list(self.worker_hashrates.keys())
        for worker_id in current_workers:
            hashrate, timestamp = self.worker_hashrates[worker_id]
            if now - timestamp < 15: total_hashrate += hashrate
            else: del self.worker_hashrates[worker_id]
        
        with stats_lock:
            stats["hashrates_history"].append(total_hashrate)
            if total_hashrate > stats["max_hashrate"]:
                stats["max_hashrate"] = total_hashrate
            
            self.hashrate_label.config(text=f"{total_hashrate/1000:,.1f} kH/s")
            self.max_hashrate_label.config(text=f"{stats['max_hashrate']/1000:,.1f} kH/s")
            self.accepted_label.config(text=f'{stats["accepted"]:,}')
            self.rejected_label.config(text=f'{stats["rejected"]:,}')
            self.balance_label.config(text=f"{stats['balance']:.4f} BC")
            self.hashes_label.config(text=f"{stats['hashes']:,}")
            self.earnings_label.config(text=f"{stats['session_earnings']:.4f} BC")
        
        is_running = self.child_processes or any(t.is_alive() for t in self.miner_threads)
        if is_running:
            uptime = int(time.time() - self.start_time)
            h, rem = divmod(uptime, 3600); m, s = divmod(rem, 60)
            self.uptime_label.config(text=f"{h:02d}:{m:02d}:{s:02d}")
            self.status_label.config(text=f"Status: Mining ({len(self.worker_hashrates)} workers)...", foreground=SUCCESS_COLOR)
        else:
            self.status_label.config(text="Status: Stopped", foreground=ERROR_COLOR)

        self.update_graph()
        self.root.after(1000, self.update_ui)

    def start_mining(self):
        global running
        if not WALLET:
            messagebox.showerror(
                "Wallet Not Configured",
                "Невозможно начать майнинг. Пожалуйста, сначала укажите ваш адрес кошелька BetaCoin.\n\nЭто можно сделать, нажав 'Change' рядом с полем кошелька.",
                parent=self.root
            )
            return

        if not (self.miner_threads or self.child_processes):
            running = True
            self.start_time = time.time()
            self.worker_hashrates.clear()
            with stats_lock:
                stats["session_earnings"] = 0.0; stats["hashes"] = 0
                stats["accepted"] = 0; stats["rejected"] = 0
                stats["max_hashrate"] = 0; stats["hashrates_history"].clear()
            
            power_level = int(self.power_selector.get())
            self.log_queue.put(f"info: Starting miner with power level {power_level}...")
            
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.power_selector.config(state=tk.DISABLED)
            
            internal_miner_thread = threading.Thread(target=self.run_internal_miner, daemon=True)
            self.miner_threads.append(internal_miner_thread)
            internal_miner_thread.start()

            for i in range(power_level - 1):
                self.start_external_miner(i + 2)
        else:
            self.log_queue.put("warning: Miner is already running.")

    def start_external_miner(self, worker_id):
        try:
            process = subprocess.Popen(
                [sys.executable, "external_miner.py"],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                encoding='utf-8', errors='replace', bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
            )
            self.child_processes.append(process)
            log_thread = threading.Thread(
                target=self.read_process_output, args=(process.stdout, f"Worker-{worker_id}"), daemon=True
            )
            log_thread.start()
        except Exception as e:
            self.log_queue.put(f"error: Failed to start external miner {worker_id}: {e}")

    def run_internal_miner(self):
        sys.stdout = QueueLogger(self.log_queue)
        asyncio.run(mine())

    def read_process_output(self, pipe, worker_id):
        try:
            for line in iter(pipe.readline, ''):
                if line.strip(): self.log_queue.put(f"[{worker_id}] {line.strip()}")
        finally: pipe.close()
            
    def stop_mining(self):
        global running
        running = False
        self.log_queue.put("warning: Stopping all mining processes...")
        for p in self.child_processes:
            try: p.terminate()
            except Exception: pass
        for p in self.child_processes:
            try: p.wait(timeout=3)
            except subprocess.TimeoutExpired: p.kill()
        self.child_processes.clear(); self.miner_threads.clear()
        self.worker_hashrates.clear()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.power_selector.config(state=tk.NORMAL)
    
    def process_log_queue(self):
        try:
            while not self.log_queue.empty():
                log_line = self.log_queue.get_nowait()
                
                worker_id = "Worker-1"
                raw_message = log_line
                worker_match = re.match(r'\[(.*?)\] (.*)', log_line)
                if worker_match:
                    worker_id = worker_match.group(1)
                    raw_message = worker_match.group(2)
                
                hash_report_match = re.search(r'hashrate_report:([0-9\.]+)', raw_message)
                if hash_report_match:
                    self.worker_hashrates[worker_id] = (float(hash_report_match.group(1)), time.time())
                    continue

                hashes_report_match = re.search(r'hashes_report:(\d+)', raw_message)
                if hashes_report_match:
                    with stats_lock:
                        stats['hashes'] += int(hashes_report_match.group(1))
                    continue
                
                with stats_lock:
                    reward_match = re.search(r'accepted:.*?\+\s*([0-9\.]+)\s*\|\s*Balance:\s*([0-9\.]+)', raw_message, re.IGNORECASE)
                    if reward_match:
                        stats["session_earnings"] += float(reward_match.group(1))
                        stats["balance"] = float(reward_match.group(2))
                        stats["accepted"] += 1
                    elif "rejected" in raw_message.lower() or "invalid wallet" in raw_message.lower():
                        stats["rejected"] += 1
                
                self.log_message(raw_message, worker_id)
        finally:
            self.root.after(100, self.process_log_queue)

    def log_message(self, message, worker_id):
        msg_type = "normal"
        lower_message = message.lower()
        if "accepted" in lower_message or "block found" in lower_message: msg_type = "accepted"
        elif "invalid wallet" in lower_message: msg_type = "error"
        elif "rejected" in lower_message: msg_type = "rejected"
        elif "error" in lower_message: msg_type = "error"
        elif "warning" in lower_message: msg_type = "warning"
        elif "miner" in lower_message: msg_type = "miner"
        elif "info:" in lower_message: msg_type = "info"
        
        clean_message = message
        parts = message.split(":", 1)
        if len(parts) > 1 and parts[0].lower() in ["info", "error", "warning", "miner", "accepted", "rejected"]:
             clean_message = parts[1].strip()

        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] ", ("timestamp",))
        self.log_text.insert(tk.END, f"[{worker_id}] ", ("worker",))
        self.log_text.insert(tk.END, f"{clean_message}\n", (msg_type,))
        self.log_text.see(tk.END)

    def on_close(self):
        self.stop_mining()
        self.root.after(500, self.root.destroy)
        
    def open_help(self):
        self.log_queue.put("info: Opening GitHub help page...")
        webbrowser.open("https://github.com/MinArtem/UTKgui-BetaCoin-Miner/blob/main/README.md")

    def open_wallet_window(self):
        if self.wallet_window is None:
            self.wallet_window = ChangeWalletWindow(self.root, self)
        else:
            self.wallet_window.lift()

    def open_system_info_window(self):
        if self.sys_info_window is None:
            self.sys_info_window = SystemInfoWindow(self.root, self)
        else:
            self.sys_info_window.lift()

    def update_wallet(self, new_wallet):
        global WALLET
        WALLET = new_wallet
        save_config(new_wallet)
        wallet_display_text = f"{WALLET[:8]}...{WALLET[-6:]}" if WALLET else "Not Configured. Click 'Change'."
        wallet_color = TEXT_LIGHT if WALLET else WARNING_COLOR
        self.wallet_label.config(text=wallet_display_text, foreground=wallet_color)
        RestartDialog(self.root, self)

    def restart_application(self):
        python = sys.executable
        os.execl(python, python, *sys.argv)

# =============================================================================
# === Функции майнинга (async) для внутреннего майнера ========================
# =============================================================================
def get_cpu_info():
    try: return cpuinfo.get_cpu_info().get('brand_raw', platform.processor())
    except Exception: return "N/A"

def calculate_hash(challenge, nonce, wallet):
    return hashlib.sha256(f"{challenge}{nonce}{wallet}".encode()).hexdigest()

async def resolve_with_dns(hostname):
    dns_servers = ['8.8.8.8', '1.1.1.1', '77.88.8.8', '208.67.222.222']
    for dns_server in dns_servers:
        try:
            resolver = dns.resolver.Resolver(); resolver.nameservers = [dns_server]
            answer = await asyncio.get_event_loop().run_in_executor(None, lambda: resolver.resolve(hostname, 'A'))
            return str(answer[0])
        except Exception as e: print(f"warning: Failed to resolve {hostname} using {dns_server}: {e}")
    raise Exception(f"All DNS servers failed to resolve {hostname}")

async def connect_to_server():
    try:
        ip_address = await resolve_with_dns(SERVER_HOST)
        print(f"info: Resolved {SERVER_HOST} -> {ip_address}")
        return await asyncio.wait_for(asyncio.open_connection(ip_address, SERVER_PORT), timeout=30.0)
    except Exception as e:
        print(f"error: Connection failed: {str(e)}"); return None, None

async def submit_solution(reader, writer, challenge, nonce, wallet):
    try:
        request = json.dumps({"action": "submit_solution", "address": wallet, "nonce": nonce, "challenge": challenge})
        writer.write(len(request).to_bytes(4, 'big') + request.encode())
        await writer.drain()
        length = int.from_bytes(await asyncio.wait_for(reader.readexactly(4), timeout=30.0), 'big')
        return json.loads((await asyncio.wait_for(reader.readexactly(length), timeout=30.0)).decode())
    except Exception as e:
        print(f"error: Submit failed: {str(e)}"); return {"error": str(e)}

async def mine_block(challenge, difficulty, reader, writer):
    local_hashes, total_hashes_in_block = 0, 0
    start_time = time.perf_counter()
    start_nonce = secrets.randbits(64)
    
    for i in range(100000):
        if not running: return "stopped", total_hashes_in_block + local_hashes

        nonce = f"{start_nonce + i:016x}"; local_hashes += 1
        
        if calculate_hash(challenge, nonce, WALLET).startswith('0' * difficulty):
            total_hashes_in_block += local_hashes
            if writer.is_closing():
                return "connection_lost", total_hashes_in_block
            
            response = await submit_solution(reader, writer, challenge, nonce, WALLET)
            
            if response.get("success"):
                print(f"accepted: Block found! +{response.get('reward', 0):.4f} | Balance: {response.get('balance', 0):.4f}")
                return "found", total_hashes_in_block
            else:
                error_msg = response.get('error', 'unknown error')
                if "Invalid wallet address" in error_msg:
                    print(f"error: Invalid wallet address provided. Please change it in the settings.")
                else:
                    print(f"rejected: Share rejected by pool.")
                return "rejected", total_hashes_in_block
        
        if local_hashes >= REPORTING_BATCH_SIZE:
            print(f"hashes_report:{local_hashes}")
            total_hashes_in_block += local_hashes
            local_hashes = 0
            
    elapsed = time.perf_counter() - start_time
    if elapsed > 0: print(f"hashrate_report:{100000 / elapsed:.2f}")
            
    return "not_found", total_hashes_in_block + local_hashes

async def mine():
    reader, writer = None, None
    while running:
        hashes_done = 0
        try:
            try:
                if not WALLET:
                    print("warning: Wallet is not configured. Pausing miner.")
                    await asyncio.sleep(15)
                    continue

                if reader is None or writer.is_closing():
                    if writer: writer.close(); await writer.wait_closed()
                    print("info: Connecting to server...")
                    reader, writer = await connect_to_server()
                    if not reader: await asyncio.sleep(5); continue
                    print("info: Connection established.")

                request = json.dumps({"action": "get_challenge", "address": WALLET}).encode()
                writer.write(len(request).to_bytes(4, 'big') + request)
                await writer.drain()
                length = int.from_bytes(await asyncio.wait_for(reader.readexactly(4), timeout=30.0), 'big')
                job = json.loads((await asyncio.wait_for(reader.readexactly(length), timeout=30.0)).decode())
                
                status, hashes_done = await mine_block(job["challenge"], job["difficulty"], reader, writer)
                
                if status == "stopped": break
                if status == "connection_lost": reader = writer = None
                await asyncio.sleep(0.1)
            except (asyncio.TimeoutError, ConnectionError, OSError) as e:
                print(f"warning: Connection issue ({type(e).__name__}), reconnecting...")
                if writer: writer.close(); await writer.wait_closed()
                reader = writer = None; await asyncio.sleep(5)
            except Exception as e:
                print(f"error: Mining loop error: {e}")
                if writer: writer.close(); await writer.wait_closed()
                reader = writer = None; await asyncio.sleep(10)
        finally:
            if hashes_done > 0:
                print(f"hashes_report:{hashes_done}")

    if writer: writer.close(); await writer.wait_closed()
    print("info: Internal miner stopped.")

# =============================================================================
# === Точка входа в приложение ================================================
# =============================================================================
def main_gui():
    if sys.version_info < (3, 7):
        print("Python 3.7 or higher is required to run this program."); sys.exit(1)
    root = tk.Tk()
    gui = MinerGUI(root)
    root.protocol("WM_DELETE_WINDOW", gui.on_close)
    root.mainloop()

if __name__ == "__main__":
    main_gui()