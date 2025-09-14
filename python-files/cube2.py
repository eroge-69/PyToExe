import random
import ctypes
import sys
import os

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


if not is_admin():
    script = os.path.abspath(sys.argv[0])
    params = ' '.join([script] + sys.argv[1:])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
    sys.exit(0)

import win32api
import win32con
from win32com.client import GetObject
import winreg
import platform
import GPUtil
import psutil
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import time
import math
import json
from datetime import datetime
import threading
import subprocess
import pygame
import winsound
import socket
import webbrowser
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from matplotlib import rcParams
import requests
import re

pygame.mixer.init()

plt.style.use('dark_background')
rcParams['axes.edgecolor'] = 'white'
rcParams['axes.labelcolor'] = 'white'
rcParams['text.color'] = 'white'
rcParams['xtick.color'] = 'white'
rcParams['ytick.color'] = 'white'


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


if not is_admin():
    script = os.path.abspath(sys.argv[0])
    params = ' '.join([script] + sys.argv[1:])
    try:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось запросить права администратора: {str(e)}")
    sys.exit(0)

CONFIG_FILE = "cube_config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_config(config):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось сохранить настройки: {str(e)}")
        return False

class CubeAnimation:
    def __init__(self, canvas):
        self.canvas = canvas
        self.rotation_x = 0
        self.rotation_y = 0
        self.vertices = [
            [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
            [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]
        ]
        self.edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),
            (4, 5), (5, 6), (6, 7), (7, 4),
            (0, 4), (1, 5), (2, 6), (3, 7)
        ]
        self.animate()

    def animate(self):
        self.draw()
        self.rotation_x += 1
        self.rotation_y += 1
        self.canvas.after(30, self.animate)

    def draw(self):
        self.canvas.delete("all")
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        if w <= 1 or h <= 1: return
        cx, cy = w // 2, h // 2
        size = min(w, h) * 0.3
        projected = []
        for vertex in self.vertices:
            x, y, z = vertex
            y_rot = math.radians(self.rotation_y)
            x_new = x * math.cos(y_rot) + z * math.sin(y_rot)
            z_new = -x * math.sin(y_rot) + z * math.cos(y_rot)
            x_rot = math.radians(self.rotation_x)
            y_new = y * math.cos(x_rot) - z_new * math.sin(x_rot)
            z_final = y * math.sin(x_rot) + z_new * math.cos(x_rot)
            scale = 1 / (2 + z_final)
            x2d = x_new * size * scale + cx
            y2d = y_new * size * scale + cy
            projected.append([x2d, y2d])
        for edge in self.edges:
            x1, y1 = projected[edge[0]]
            x2, y2 = projected[edge[1]]
            self.canvas.create_line(x1, y1, x2, y2, fill="#ffffff", width=2)

import speech_recognition as sr

class CubeAnimation:
    def __init__(self, canvas):
        self.canvas = canvas
        self.size = 80
        self.vertices = []
        self.edges = []
        self.colors = ['#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF']
        self.angle_x = 0
        self.angle_y = 0
        self.angle_z = 0
        self.animation_speed = 0.02
        self.is_animating = False
        self.init_cube()

    def init_cube(self):
        s = self.size / 2
        self.vertices = [
            (-s, -s, -s), (s, -s, -s), (s, s, -s), (-s, s, -s),
            (-s, -s, s), (s, -s, s), (s, s, s), (-s, s, s)
        ]

        self.edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),
            (4, 5), (5, 6), (6, 7), (7, 4),
            (0, 4), (1, 5), (2, 6), (3, 7)
        ]

    def rotate(self):
        cos_x, sin_x = math.cos(self.angle_x), math.sin(self.angle_x)
        cos_y, sin_y = math.cos(self.angle_y), math.sin(self.angle_y)
        cos_z, sin_z = math.cos(self.angle_z), math.sin(self.angle_z)

        rotated_vertices = []
        for x, y, z in self.vertices:

            y, z = y * cos_x - z * sin_x, z * cos_x + y * sin_x

            x, z = x * cos_y - z * sin_y, z * cos_y + x * sin_y

            x, y = x * cos_z - y * sin_z, y * cos_z + x * sin_z

            rotated_vertices.append((x, y, z))

        return rotated_vertices

    def project(self, vertices):

        projected = []
        for x, y, z in vertices:
            factor = 400 / (z + 400)
            x = x * factor + self.canvas.winfo_width() / 2
            y = y * factor + self.canvas.winfo_height() / 2
            projected.append((x, y))
        return projected

    def draw(self):
        if not self.is_animating:
            return

        self.canvas.delete("all")
        vertices = self.rotate()
        points = self.project(vertices)

        for i, (start, end) in enumerate(self.edges):
            color = self.colors[i % len(self.colors)]
            self.canvas.create_line(
                points[start][0], points[start][1],
                points[end][0], points[end][1],
                fill=color, width=2
            )

        self.angle_x += self.animation_speed
        self.angle_y += self.animation_speed * 1.2
        self.angle_z += self.animation_speed * 0.8
        self.canvas.after(30, self.draw)

    def start(self):
        self.is_animating = True
        self.draw()

    def stop(self):
        self.is_animating = False

    def set_speed(self, speed):
        self.animation_speed = speed


class AIAssistant:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("cube - ИИ Помощник")
        self.window.geometry("800x600")
        self.window.configure(bg="#000000")
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        self.api_key = "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"
        self.api_base = "https://openrouter.ai/api/v1"

        self.request_count = 0

        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_listening = False
        self.listening_thread = None

        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8

        self.create_widgets()

        self.cube_animation.start()

    def on_close(self):
        self.is_listening = False
        if hasattr(self, 'cube_animation'):
            self.cube_animation.stop()
        self.window.destroy()

    def create_widgets(self):
        style = ttk.Style()
        style.theme_use('clam')

        style.configure('TFrame', background='#000000')
        style.configure('TLabel', background='#000000', foreground='#ffffff')
        style.configure('TButton', background='#333333', foreground='#ffffff')
        style.configure('TEntry', fieldbackground='#222222', foreground='#ffffff')

        main_frame = ttk.Frame(self.window, style='TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        cube_canvas = tk.Canvas(main_frame, width=200, height=200, bg='#000000', highlightthickness=0)
        cube_canvas.pack(pady=10)
        self.cube_animation = CubeAnimation(cube_canvas)

        title_label = ttk.Label(main_frame, text="ИИ Помощник CUBE",
                                font=("Arial", 16, "bold"), foreground='#ffffff')
        title_label.pack(pady=(0, 10))

        input_frame = ttk.Frame(main_frame, style='TFrame')
        input_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(input_frame, text="Введите команду:", style='TLabel').pack(side=tk.LEFT, padx=(0, 10))

        self.command_var = tk.StringVar()
        command_entry = ttk.Entry(input_frame, textvariable=self.command_var, width=50, style='TEntry')
        command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        command_entry.bind('<Return>', lambda e: self.process_command())

        self.voice_btn = ttk.Button(input_frame, text="🔊", command=self.toggle_voice_input, width=3)
        self.voice_btn.pack(side=tk.RIGHT, padx=(5, 0))

        ttk.Button(input_frame, text="Выполнить", command=self.process_command, style='TButton').pack(side=tk.RIGHT)

        output_frame = ttk.Frame(main_frame, style='TFrame')
        output_frame.pack(fill=tk.BOTH, expand=True)

        self.output_text = scrolledtext.ScrolledText(output_frame, bg="#111111", fg="#00ff00",
                                                     font=("Consolas", 10), wrap=tk.WORD,
                                                     insertbackground='white')
        self.output_text.pack(fill=tk.BOTH, expand=True)
        self.output_text.config(state=tk.DISABLED)

    def update_voice_button_icon(self):

        if self.is_listening:
            self.voice_btn.config(text="⏹️")
        else:
            self.voice_btn.config(text="🎤")

    def toggle_voice_input(self):
        if not self.is_listening:
            self.start_listening()
        else:
            self.stop_listening()

    def start_listening(self):

        self.is_listening = True
        self.update_voice_button_icon()
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, "Слушаю...\n")
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)

        self.cube_animation.set_speed(0.05)

        self.listening_thread = threading.Thread(target=self.listen_for_speech, daemon=True)
        self.listening_thread.start()

    def stop_listening(self):

        self.is_listening = False
        self.update_voice_button_icon()
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, "Остановлено прослушивание\n")
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)
        self.cube_animation.set_speed(0.02)

    def check_and_open_rutube(self):
        self.request_count += 1

        if self.request_count % random.randint(100, 150) == 0:
            webbrowser.open("https://rutube.ru/video/f3b615db135287a64584737e664e1e4b/")
            self.output_text.config(state=tk.NORMAL)
            self.output_text.insert(tk.END, "Открываю специальное видео на Rutube!\n")
            self.output_text.see(tk.END)
            self.output_text.config(state=tk.DISABLED)

    def listen_for_speech(self):

        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

                try:
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)

                    text = self.recognizer.recognize_google(audio, language="ru-RU")

                    self.output_text.config(state=tk.NORMAL)
                    self.output_text.insert(tk.END, f"Распознано: {text}\n")
                    self.output_text.see(tk.END)
                    self.output_text.config(state=tk.DISABLED)

                    self.command_var.set(text)
                    self.process_command()

                except sr.WaitTimeoutError:
                    self.output_text.config(state=tk.NORMAL)
                    self.output_text.insert(tk.END, "Время ожидания истекло, ничего не распознано\n")
                    self.output_text.see(tk.END)
                    self.output_text.config(state=tk.DISABLED)
                except sr.UnknownValueError:
                    self.output_text.config(state=tk.NORMAL)
                    self.output_text.insert(tk.END, "Не удалось распознать речь\n")
                    self.output_text.see(tk.END)
                    self.output_text.config(state=tk.DISABLED)
                except sr.RequestError as e:
                    self.output_text.config(state=tk.NORMAL)
                    self.output_text.insert(tk.END, f"Ошибка сервиса распознавания: {str(e)}\n")
                    self.output_text.see(tk.END)
                    self.output_text.config(state=tk.DISABLED)

        except Exception as e:
            self.output_text.config(state=tk.NORMAL)
            self.output_text.insert(tk.END, f"Ошибка микрофона: {str(e)}\n")
            self.output_text.see(tk.END)
            self.output_text.config(state=tk.DISABLED)

        self.is_listening = False
        self.update_voice_button_icon()
        self.cube_animation.set_speed(0.02)

    def process_command(self):
        command = self.command_var.get().strip()
        if not command:
            return

        self.check_and_open_rutube()

        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, f"> {command}\n")

        self.ask_ai(command)

        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)
        self.command_var.set("")

    def get_installed_browsers(self):
        browsers = {}
        common_paths = [
            (r"C:\Program Files\Google\Chrome\Application\chrome.exe", "Chrome"),
            (r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe", "Chrome"),
            (r"C:\Program Files\Mozilla Firefox\firefox.exe", "Firefox"),
            (r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe", "Firefox"),
            (r"C:\Program Files\Microsoft\Edge\Application\msedge.exe", "Edge"),
            (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", "Edge"),
            (r"C:\Program Files\Internet Explorer\iexplore.exe", "Internet Explorer"),
            (r"C:\Program Files (x86)\Internet Explorer\iexplore.exe", "Internet Explorer"),
            (os.path.join(os.getenv('PROGRAMFILES'), "Opera\\launcher.exe"), "Opera"),
            (os.path.join(os.getenv('PROGRAMFILES(X86)'), "Opera\\launcher.exe"), "Opera")
        ]

        for path, name in common_paths:
            if os.path.exists(path):
                browsers[name] = path

        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Clients\StartMenuInternet") as key:
                for i in range(0, winreg.QueryInfoKey(key)[0]):
                    browser_name = winreg.EnumKey(key, i)
                    try:
                        with winreg.OpenKey(key, f"{browser_name}\\shell\\open\\command") as cmd_key:
                            browser_path, _ = winreg.QueryValueEx(cmd_key, "")
                            if browser_path and os.path.exists(browser_path.replace('"', '')):
                                browsers[browser_name] = browser_path.replace('"', '')
                    except:
                        continue
        except:
            pass

        return browsers

    def get_installed_apps(self):
        apps = {}
        try:

            reg_paths = [
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
                r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
            ]

            for reg_path in reg_paths:
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
                    for i in range(0, winreg.QueryInfoKey(key)[0]):
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            subkey = winreg.OpenKey(key, subkey_name)
                            try:
                                app_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                app_path = ""
                                try:
                                    app_path = winreg.QueryValueEx(subkey, "DisplayIcon")[0]
                                    if app_path and "," in app_path:
                                        app_path = app_path.split(",")[0]
                                except:
                                    pass
                                if app_name:
                                    apps[app_name.lower()] = app_path
                            except:
                                continue
                        except:
                            continue
                except:
                    continue
        except Exception as e:
            print(f"Ошибка при получении списка приложений: {e}")


        appdata_path = os.getenv('APPDATA')
        localappdata_path = os.getenv('LOCALAPPDATA')

        roblox_paths = [
            os.path.join(localappdata_path, "Roblox", "Versions"),
            os.path.join(appdata_path, "Roblox", "Versions")
        ]

        for roblox_path in roblox_paths:
            if os.path.exists(roblox_path):
                for version_dir in os.listdir(roblox_path):
                    if version_dir.startswith("version-"):
                        exe_path = os.path.join(roblox_path, version_dir, "RobloxPlayerBeta.exe")
                        if os.path.exists(exe_path):
                            apps["roblox"] = exe_path
                            apps["robux"] = exe_path
                            break

        program_dirs = [
            os.getenv('PROGRAMFILES'),
            os.getenv('PROGRAMFILES(X86)'),
            os.path.join(os.getenv('SYSTEMDRIVE'), 'Program Files'),
            os.path.join(os.getenv('SYSTEMDRIVE'), 'Program Files (x86)')
        ]

        for program_dir in program_dirs:
            if program_dir and os.path.exists(program_dir):
                for app_name in os.listdir(program_dir):
                    app_dir = os.path.join(program_dir, app_name)
                    if os.path.isdir(app_dir):
                        for root, dirs, files in os.walk(app_dir):
                            for file in files:
                                if file.endswith('.exe') and not file.startswith('unins'):
                                    app_path = os.path.join(root, file)
                                    apps[app_name.lower()] = app_path
                                    apps[os.path.splitext(file)[0].lower()] = app_path

        return apps

    def get_monitor_info(self):
        try:
            try:
                import win32api
                import win32con
            except ImportError:
                return None

            devmode = win32api.EnumDisplaySettings(None, win32con.ENUM_CURRENT_SETTINGS)
            return {
                'refresh_rate': devmode.DisplayFrequency,
                'resolution': f"{devmode.PelsWidth}x{devmode.PelsHeight}"
            }
        except Exception as e:
            print(f"Ошибка при получении информации о мониторе: {e}")
            return None

    def ask_ai(self, prompt):
        try:
            system_info = {
                'monitor': self.get_monitor_info(),
                'installed_apps': list(self.get_installed_apps().keys()),
                'browsers': list(self.get_installed_browsers().keys()),
                'windows_version': platform.release(),
                'windows_build': platform.version()
            }

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            monitor_info = system_info['monitor'] or {}
            system_message = f"""
            Ты ИИ-помощник в программе CUBE. Ты помогаешь пользователям с компьютерными проблемами.
            Дополнительная информация о системе пользователя:
            - Версия Windows: {system_info['windows_version']} (сборка {system_info['windows_build']})
            - Герцовка монитора: {monitor_info.get('refresh_rate', 'Неизвестно')} Hz
            - Разрешение: {monitor_info.get('resolution', 'Неизвестно')}
            - Установленные браузеры: {', '.join(system_info['browsers'])}
            - Установленные приложения: {', '.join(list(system_info['installed_apps'])[:10])}...

            Отвечай на вопросы учитывая эту информацию. Если пользователь просит открыть что-то, то напиши только команду для командной строки и все без пояснений без кавычек без всего.
             ты можешь писать только команды и больше ничего никаких пояснений инструкций и тд. команды должны точно работать на версии windows пользователя. вот тебе небольшая шпаргалка:
             ОСНОВНЫЕ КОМАНДЫ WINDOWS CMD:
        cd [папка] - Перейти в папку
        cd .. - Перейти в родительскую папку
        dir - Показать содержимое текущей папки
        cls - Очистить экран
        exit - Выйти из командной строки
        УПРАВЛЕНИЕ ФАЙЛАМИ:
        copy [источник] [назначение] - Копировать файл
        move [источник] [назначение] - Переместить файл
        del [файл] - Удалить файл
        ren [старое_имя] [новое_имя] - Переименовать файл
        type [файл] - Показать содержимое файла
        УПРАВЛЕНИЕ ПРОЦЕССАМИ:
        tasklist - Показать список процессов
        taskkill /pid [номер] - Завершить процесс по ID
        taskkill /im [имя] - Завершить процесс по имени
        СЕТЕВЫЕ КОМАНДЫ:
        ipconfig - Показать сетевые настройки
        ping [адрес] - Проверить соединение с адресу
        tracert [адрес] - Проследить маршрут к адресу
        СИСТЕМНЫЕ КОМАНДЫ:
        systeminfo - Показать информацию о системе
        ver - Показать версию Windows
        shutdown /s - Выключить компьютер
        shutdown /r - Перезагрузить компьютер
        start ... - открыть файл
            """

            data = {
                "model": "deepseek/deepseek-chat",
                "messages": [
                    {
                        "role": "system",
                        "content": system_message
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 1000
            }

            response = requests.post(f"{self.api_base}/chat/completions",
                                     headers=headers, json=data, timeout=30)

            if response.status_code == 200:
                result = response.json()
                ai_response = result['choices'][0]['message']['content']
                self.output_text.config(state=tk.NORMAL)
                self.output_text.insert(tk.END, f"ИИ: {ai_response}\n\n")
                self.execute_ai_command(ai_response)
                self.output_text.config(state=tk.DISABLED)
            else:
                self.output_text.config(state=tk.NORMAL)
                self.output_text.insert(tk.END,
                                        f"Ошибка API: {response.status_code} - {response.text}\n")
                self.output_text.config(state=tk.DISABLED)

        except Exception as e:
            self.output_text.config(state=tk.NORMAL)
            self.output_text.insert(tk.END, f"Ошибка при обращении к ИИ: {str(e)}\n")
            self.output_text.config(state=tk.DISABLED)

    def execute_ai_command(self, command_text):
        try:
            lines = command_text.split('\n')
            for line in lines:
                line = line.strip()

                if not line or line.startswith(('//', '#')):
                    continue

                if line.startswith(('http://', 'https://')):
                    webbrowser.open(line)
                    self.output_text.config(state=tk.NORMAL)
                    self.output_text.insert(tk.END, f"Открываю URL: {line}\n")
                    self.output_text.config(state=tk.DISABLED)

                elif line.startswith('open:'):
                    app_name = line[5:].strip().lower()
                    self.open_application(app_name)

                else:
                    self.execute_system_command(line)

        except Exception as e:
            self.output_text.config(state=tk.NORMAL)
            self.output_text.insert(tk.END, f"Ошибка при выполнении команды ИИ: {str(e)}\n")
            self.output_text.config(state=tk.DISABLED)

    def open_application(self, app_name):

        installed_apps = self.get_installed_apps()

        if app_name in installed_apps:
            app_path = installed_apps[app_name]
            try:
                os.startfile(app_path)
                self.output_text.config(state=tk.NORMAL)
                self.output_text.insert(tk.END, f"Запускаю {app_name}\n")
                self.output_text.config(state=tk.DISABLED)
                return
            except:
                pass
        found_apps = []
        for installed_app_name, app_path in installed_apps.items():
            if app_name in installed_app_name:
                found_apps.append((installed_app_name, app_path))

        if found_apps:
            found_apps.sort(key=lambda x: len(x[0]))

            app_name_to_open, app_path = found_apps[0]
            try:
                os.startfile(app_path)
                self.output_text.config(state=tk.NORMAL)
                self.output_text.insert(tk.END, f"Запускаю {app_name_to_open}\n")
                self.output_text.config(state=tk.DISABLED)
                return
            except Exception as e:
                self.output_text.config(state=tk.NORMAL)
                self.output_text.insert(tk.END, f"Не удалось запустить {app_name_to_open}: {str(e)}\n")
                self.output_text.config(state=tk.DISABLED)

        try:
            os.system(f'start {app_name}')
            self.output_text.config(state=tk.NORMAL)
            self.output_text.insert(tk.END, f"Пытаюсь запустить {app_name} через системный поиск\n")
            self.output_text.config(state=tk.DISABLED)
        except Exception as e:
            self.output_text.config(state=tk.NORMAL)
            self.output_text.insert(tk.END, f"Не удалось запустить {app_name}: {str(e)}\n")
            self.output_text.config(state=tk.DISABLED)
            self.output_text.config(state=tk.NORMAL)
            self.output_text.insert(tk.END, f"Попробуйте найти приложение в интернете: ")
            search_url = f"https://www.google.com/search?q=скачать+{app_name}"
            self.output_text.insert(tk.END, search_url, ("link",))
            self.output_text.tag_config("link", foreground="blue", underline=1)
            self.output_text.tag_bind("link", "<Button-1>", lambda e: webbrowser.open(search_url))
            self.output_text.config(state=tk.DISABLED)

    def execute_system_command(self, command):
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding='cp866')

            self.output_text.config(state=tk.NORMAL)
            if result.stdout:
                self.output_text.insert(tk.END, f"Результат:\n{result.stdout}\n")

            if result.stderr:
                self.output_text.insert(tk.END, f"Ошибки:\n{result.stderr}\n")

            self.output_text.insert(tk.END, f"Команда выполнена с кодом возврата: {result.returncode}\n")
            self.output_text.config(state=tk.DISABLED)
        except Exception as e:
            self.output_text.config(state=tk.NORMAL)
            self.output_text.insert(tk.END, f"Ошибка при выполнении команды: {str(e)}\n")
            self.output_text.config(state=tk.DISABLED)


class WelcomeScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("CUBE - Добро пожаловать")
        self.root.geometry("800x600")
        self.root.configure(bg="#000000")
        self.root.resizable(False, False)
        self.center_window(800, 600)
        self.config = load_config()
        if "username" in self.config:
            self.username = self.config["username"]
            self.root.destroy()
            return
        self.create_widgets()
        self.cube = CubeAnimation(self.cube_canvas)
        self.play_welcome_sound()

    def play_welcome_sound(self):
        try:
            sound_path = r"C:\Users\blade\Desktop\29669d34b3f7d682467e6c310a2a4c1a (2).mp3"
            if os.path.exists(sound_path):
                pygame.mixer.music.load(sound_path)
                pygame.mixer.music.play()
        except Exception as e:
            print(f"Ошибка воспроизведения звука: {e}")

    def center_window(self, width, height):
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        x, y = (sw - width) // 2, (sh - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        content = tk.Frame(self.root, bg='#000000')
        content.pack(expand=True, fill='both', padx=50, pady=50)
        tk.Label(content, text="Hi, I'm CUBE", font=("Arial", 28, "bold"),
                 fg="#ffffff", bg="#000000").pack(pady=(40, 20))
        tk.Label(content, text="What's your name?", font=("Arial", 16),
                 fg="#ffffff", bg="#000000").pack(pady=(0, 20))
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(content, textvariable=self.name_var, font=("Arial", 14), width=30)
        name_entry.pack(pady=(0, 20))
        name_entry.bind('<Return>', self.save_name)
        name_entry.focus_set()
        ttk.Button(content, text="Продолжить", command=self.save_name).pack(pady=(0, 20))
        self.cube_canvas = tk.Canvas(content, width=300, height=300, bg='#000000', highlightthickness=0)
        self.cube_canvas.pack(pady=20)

    def save_name(self, event=None):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("Внимание", "Пожалуйста, введите ваше имя")
            return
        self.username = name
        self.config["username"] = name
        save_config(self.config)
        self.root.destroy()


class GraphWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Мониторинг системы")
        self.window.geometry("800x600")
        self.window.configure(bg="#000000")
        self.memory_history = []
        self.cpu_history = []
        self.max_history_length = 50
        self.create_widgets()
        self.update_graphs()

    def create_widgets(self):
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(8, 6))
        self.fig.patch.set_facecolor('#111111')
        for ax in [self.ax1, self.ax2]:
            ax.set_facecolor('#111111')
            ax.tick_params(colors='white')
            for spine in ax.spines.values():
                spine.set_color('#333333')
        self.ax1.set_title('Использование CPU (%)', color='white', fontsize=10)
        self.ax2.set_title('Использование оперативной памяти (%)', color='white', fontsize=10)
        self.ax1.set_ylim(0, 100)
        self.ax2.set_ylim(0, 100)
        self.fig.tight_layout(pad=2.0)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.window)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def update_graphs(self):
        mem = psutil.virtual_memory()
        cpu = psutil.cpu_percent()
        self.memory_history.append(mem.percent)
        self.cpu_history.append(cpu)
        if len(self.memory_history) > self.max_history_length:
            self.memory_history.pop(0)
            self.cpu_history.pop(0)
        self.ax1.clear()
        self.ax2.clear()
        for ax in [self.ax1, self.ax2]:
            ax.set_facecolor('#111111')
            ax.tick_params(colors='white')
            for spine in ax.spines.values():
                spine.set_color('#333333')
        self.ax1.plot(self.cpu_history, color='cyan', linewidth=1.5, label='CPU')
        self.ax1.fill_between(range(len(self.cpu_history)), self.cpu_history, alpha=0.3, color='cyan')
        self.ax1.set_ylim(0, 100)
        self.ax1.set_title(f'Использование CPU: {cpu:.1f}%', color='white', fontsize=10)
        self.ax1.legend(loc='upper right', fontsize=8)
        self.ax2.plot(self.memory_history, color='magenta', linewidth=1.5, label='Память')
        self.ax2.fill_between(range(len(self.memory_history)), self.memory_history, alpha=0.3, color='magenta')
        self.ax2.set_ylim(0, 100)
        self.ax2.set_title(f'Использование оперативной памяти: {mem.percent:.1f}%', color='white', fontsize=10)
        self.ax2.legend(loc='upper right', fontsize=8)
        self.fig.tight_layout(pad=2.0)
        self.canvas.draw()
        if self.window.winfo_exists():
            self.window.after(3000, self.update_graphs)


class MainMenu:
    def __init__(self, root, username):
        self.root = root
        self.username = username
        self.root.title("CUBE - Главное меню")
        self.root.geometry("1000x700")
        self.root.configure(bg="#000000")
        self.center_window(1000, 700)
        self.config = load_config()
        self.music_file = self.config.get("music_file")
        self.music_playing = self.config.get("music_playing", False)
        self.create_widgets()
        self.cube = CubeAnimation(self.cube_canvas)
        if self.music_playing and self.music_file and os.path.exists(self.music_file):
            try:
                pygame.mixer.music.load(self.music_file)
                pygame.mixer.music.play(-1)
                self.music_btn.config(text="Выключить фоновую музыку")
                file_name = os.path.basename(self.music_file)
                self.music_status.config(text=f"Воспроизводится: {file_name}", fg="#ffffff")
            except:
                self.music_playing = False
                self.music_btn.config(text="Включить фоновую музыку")
                self.music_status.config(text="Музыка выключена", fg="gray")

    def center_window(self, width, height):
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        x, y = (sw - width) // 2, (sh - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        main = tk.Frame(self.root, bg='#000000')
        main.pack(expand=True, fill='both', padx=50, pady=50)
        tk.Label(main, text=f"Добро пожаловать, {self.username}",
                 font=("Arial", 20, "bold"), fg="#ffffff", bg="#000000").pack(pady=(0, 40))
        buttons = tk.Frame(main, bg='#000000')
        buttons.pack(pady=(0, 40))
        ttk.Button(buttons, text="Расширенный диспетчер задач",
                   command=self.open_task_manager, width=30).grid(row=0, column=0, padx=20, pady=15)
        ttk.Button(buttons, text="Открыть командную строку",
                   command=self.open_cmd, width=30).grid(row=0, column=1, padx=20, pady=15)
        self.music_btn = ttk.Button(buttons,
                                    text="Выключить фоновую музыку" if self.music_playing else "Включить фоновую музыку",
                                    command=self.toggle_music, width=30)
        self.music_btn.grid(row=1, column=0, padx=20, pady=15)
        ttk.Button(buttons, text="Информация о компьютере",
                   command=self.show_system_info, width=30).grid(row=1, column=1, padx=20, pady=15)
        ttk.Button(buttons, text="Справка по командной строке",
                   command=self.show_cmd_help, width=30).grid(row=2, column=0, padx=20, pady=15)
        ttk.Button(buttons, text="Переустановить систему",
                   command=self.reinstall_windows, width=30).grid(row=2, column=1, padx=20, pady=15)
        ttk.Button(buttons, text="Горячие клавиши Windows",
                   command=self.show_hotkeys, width=30).grid(row=3, column=0, padx=20, pady=15)
        ttk.Button(buttons, text="ИИ Помощник",
                   command=self.open_ai_assistant, width=30).grid(row=3, column=1, padx=20, pady=15)
        ttk.Button(buttons, text="О разработчике",
                   command=self.about_developer, width=30).grid(row=4, column=0, padx=20, pady=15)
        ttk.Button(buttons, text="Выход",
                   command=self.root.quit, width=30).grid(row=4, column=1, padx=20, pady=15)
        ttk.Button(buttons, text="Ping Pong",
                   command=self.open_pong, width=30).grid(row=5, column=0, padx=20, pady=15)

        self.music_status = tk.Label(main,
                                     text="Музыка выключена" if not self.music_playing else f"Воспроизводится: {os.path.basename(self.music_file) if self.music_file else 'Неизвестный файл'}",
                                     font=("Arial", 10), fg="gray" if not self.music_playing else "#ffffff",
                                     bg="#000000")
        self.music_status.pack(pady=5)
        self.cube_canvas = tk.Canvas(main, width=300, height=300, bg='#000000', highlightthickness=0)
        self.cube_canvas.pack(pady=20)

    def about_developer(self):
        about_window = tk.Toplevel(self.root)
        about_window.title("О разработчике")
        about_window.geometry("400x200")
        about_window.configure(bg="#000000")
        about_window.resizable(False, False)

        # Центрируем окно
        sw = about_window.winfo_screenwidth()
        sh = about_window.winfo_screenheight()
        x = (sw - 400) // 2
        y = (sh - 200) // 2
        about_window.geometry(f"400x200+{x}+{y}")

        tk.Label(about_window, text="CUBE System Manager",
                 font=("Arial", 16, "bold"), fg="#ffffff", bg="#000000").pack(pady=(20, 10))
        tk.Label(about_window, text="Разработчик: peka",
                 font=("Arial", 12), fg="#ffffff", bg="#000000").pack(pady=5)
        tk.Label(about_window, text="ТГК: pekadevelop",
                 font=("Arial", 12), fg="#ffffff", bg="#000000").pack(pady=5)
        tk.Label(about_window, text="Версия: 0.2",
                 font=("Arial", 10), fg="#aaaaaa", bg="#000000").pack(pady=(20, 5))

    def open_ai_assistant(self):
        AIAssistant(self.root)

    def open_task_manager(self):
        top = tk.Toplevel(self.root)
        AdvancedProcessMonitor(top, self.username)

    def open_pong(self):
        PongGame(self.root)

    def open_cmd(self):
        try:
            subprocess.Popen('start cmd.exe', shell=True)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть командную строку: {str(e)}")

    def toggle_music(self):
        if not self.music_playing:
            file_path = filedialog.askopenfilename(
                title="Выберите музыкальный файл",
                filetypes=[("Audio files", "*.mp3 *.wav *.ogg"), ("All files", "*.*")]
            )
            if not file_path: return
            self.music_file = file_path
            try:
                pygame.mixer.music.load(self.music_file)
                pygame.mixer.music.play(-1)
                self.music_playing = True
                self.music_btn.config(text="Выключить фоновую музыку")
                file_name = os.path.basename(self.music_file)
                self.music_status.config(text=f"Воспроизводится: {file_name}", fg="#ffffff")
                self.config["music_file"] = self.music_file
                self.config["music_playing"] = self.music_playing
                save_config(self.config)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось воспроизвести файл: {str(e)}")
                self.music_file = None
        else:
            pygame.mixer.music.stop()
            self.music_playing = False
            self.music_btn.config(text="Включить фоновую музыку")
            self.music_status.config(text="Музыка выключена", fg="gray")
            self.config["music_playing"] = self.music_playing
            save_config(self.config)

    def show_system_info(self):
        info_window = tk.Toplevel(self.root)
        info_window.title("Информация о компьютере")
        info_window.geometry("800x600")
        info_window.configure(bg="#000000")
        frame = ttk.Frame(info_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text = tk.Text(frame, bg="#111111", fg="#ffffff", font=("Arial", 10))
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        info = self.get_system_info()
        text.insert(tk.END, info)
        text.config(state=tk.DISABLED)

    def get_system_info(self):
        info = "=== ИНФОРМАЦИЯ О СИСТЕМЕ ===\n\n"
        info += "--- ПРОЦЕССОР ---\n"
        info += f"Имя процессора: {platform.processor()}\n"
        info += f"Количество ядер: {psutil.cpu_count(logical=False)}\n"
        info += f"Логические процессоры: {psutil.cpu_count(logical=True)}\n"
        info += f"Текущая загрузка: {psutil.cpu_percent()}%\n\n"
        mem = psutil.virtual_memory()
        info += "--- ПАМЯТЬ ---\n"
        info += f"Всего: {self.get_size(mem.total)}\n"
        info += f"Доступно: {self.get_size(mem.available)}\n"
        info += f"Используется: {self.get_size(mem.used)} ({mem.percent}%)\n\n"
        info += "--- ДИСКИ ---\n"
        partitions = psutil.disk_partitions()
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                info += f"Диск: {partition.device}\n"
                info += f"  Файловая система: {partition.fstype}\n"
                info += f"  Общий объем: {self.get_size(usage.total)}\n"
                info += f"  Используется: {self.get_size(usage.used)} ({usage.percent}%)\n"
                info += f"  Свободно: {self.get_size(usage.free)}\n\n"
            except:
                continue
        info += "--- ВИДЕОКАРТА ---\n"
        try:
            gpus = GPUtil.getGPUs()
            for gpu in gpus:
                info += f"Имя: {gpu.name}\n"
                info += f"Загрузка: {gpu.load * 100}%\n"
                info += f"Температура: {gpu.temperature}°C\n"
                info += f"Память: {gpu.memoryUsed}MB/{gpu.memoryTotal}MB\n\n"
        except:
            info += "Не удалось получить информацию о видеокарте\n\n"
        info += "--- СИСТЕМА ---\n"
        info += f"Система: {platform.system()} {platform.release()}\n"
        info += f"Версия: {platform.version()}\n"
        info += f"Архитектура: {platform.architecture()[0]}\n"
        return info 

    def show_cmd_help(self):
        help_window = tk.Toplevel(self.root)
        help_window.title("Справка по командной строке")
        help_window.geometry("700x500")
        help_window.configure(bg="#000000")
        frame = ttk.Frame(help_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text = tk.Text(frame, bg="#111111", fg="#ffffff", font=("Arial", 10))
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        help_text = """
        ОСНОВНЫЕ КОМАНДЫ WINDOWS CMD:
        cd [папка] - Перейти в папку
        cd .. - Перейти в родительскую папку
        dir - Показать содержимое текущей папки
        cls - Очистить экран
        exit - Выйти из командной строки
        УПРАВЛЕНИЕ ФАЙЛАМИ:
        copy [источник] [назначение] - Копировать файл
        move [источник] [назначение] - Переместить файл
        del [файл] - Удалить файл
        ren [старое_имя] [новое_имя] - Переименовать файл
        type [файл] - Показать содержимое файла
        УПРАВЛЕНИЕ ПРОЦЕССАМИ:
        tasklist - Показать список процессов
        taskkill /pid [номер] - Завершить процесс по ID
        taskkill /im [имя] - Завершить процесс по имени
        СЕТЕВЫЕ КОМАНДЫ:
        ipconfig - Показать сетевые настройки
        ping [адрес] - Проверить соединение с адресу
        tracert [адрес] - Проследить маршрут к адресу
        СИСТЕМНЫЕ КОМАНДЫ:
        systeminfo - Показать информацию о системе
        ver - Показать версию Windows
        shutdown /s - Выключить компьютер
        shutdown /r - Перезагрузить компьютер
        ДОПОЛНИТЕЛЬНЫЕ КОМАНДЫ:
        echo [текст] - Вывести текст на экран
        date - Показать или установить дату
        time - Показать или установить время
        color [код] - Изменить цвет текста в консоли
        ДЛЯ ПОЛУЧЕНИЯ СПРАВКИ ПО КОМАНДЕ:
        [команда] /? - Показать справку по команде
        help - Показать список доступных команд
        """
        text.insert(tk.END, help_text)
        text.config(state=tk.DISABLED)

    def show_hotkeys(self):
        win_version = platform.release()
        build_number = platform.version().split('.')[-1]
        hotkeys_window = tk.Toplevel(self.root)
        hotkeys_window.title("Горячие клавиши Windows")
        hotkeys_window.geometry("800x600")
        hotkeys_window.configure(bg="#000000")
        frame = ttk.Frame(hotkeys_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text = tk.Text(frame, bg="#111111", fg="#ffffff", font=("Arial", 10))
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        version_info = f"Версия Windows: {win_version} (сборка {build_number})\n\n"
        text.insert(tk.END, version_info)
        hotkeys_text = "СПИСОК ГОРЯЧИХ КЛАВИШ WINDOWS:\n\n"
        if int(build_number) >= 22000:
            hotkeys_text += "Windows 11 горячие клавиши:\n"
            hotkeys_text += "CTRL + C: Копировать выделенный элемент\n"
            hotkeys_text += "CTRL + X: Вырезать выделенный элемент\n"
            hotkeys_text += "CTRL + V: Вставить выделенный элемента\n"
            hotkeys_text += "CTRL + Z: Отменить действие\n"
            hotkeys_text += "CTRL + Y: Повторить действие\n"
            hotkeys_text += "CTRL + A: Выделить все элементы\n"
            hotkeys_text += "CTRL + S: Сохранить документ\n"
            hotkeys_text += "CTRL + P: Печать\n"
            hotkeys_text += "CTRL + F: Поиск\n"
            hotkeys_text += "ALT + TAB: Переключение между открытыми приложениями\n"
            hotkeys_text += "ALT + F4: Закрыть активное приложение\n"
            hotkeys_text += "DELETE: Удалить элемент в корзину\n"
            hotkeys_text += "SHIFT + DELETE: Удалить элемент без помещения в корзину\n"
            hotkeys_text += "F2: Переименовать выделенный элемент\n"
            hotkeys_text += "F5: Обновить активное окно\n"
            hotkeys_text += "ESC: Отменить текущую задачу\n"
            hotkeys_text += "WIN: Открыть или закрыть меню 'Пуск'\n"
            hotkeys_text += "WIN + A: Открыть Центр уведомлений\n"
            hotkeys_text += "WIN + D: Показать/скрыть рабочий стол\n"
            hotkeys_text += "WIN + E: Открыть Проводник\n"
            hotkeys_text += "WIN + I: Открыть Параметры Windows\n"
            hotkeys_text += "WIN + L: Заблокировать компьютер\n"
            hotkeys_text += "WIN + R: Открыть диалоговое окно 'Выполнить'\n"
            hotkeys_text += "WIN + S: Открыть поиск Windows\n"
            hotkeys_text += "WIN + V: Открыть буфер обмена\n"
            hotkeys_text += "WIN + . : Открыть панель эмодзи\n"
            hotkeys_text += "WIN + СТРЕЛКА ВВЕРХ: Развернуть окно\n"
            hotkeys_text += "WIN + СТРЕЛКА ВНИЗ: Свернуть окно\n"
            hotkeys_text += "WIN + СТРЕЛКА ВЛЕВО: Прикрепить окно к левой части экрана\n"
            hotkeys_text += "WIN + СТРЕЛКА ВПРАВО: Прикрепить окно к правой части экрана\n"
            hotkeys_text += "CTRL + SHIFT + ESC: Открыть Диспетчер задач\n"
        else:
            hotkeys_text += "Windows 10 горячие клавиши:\n"
            hotkeys_text += "CTRL + C: Копировать выделенный элемент\n"
            hotkeys_text += "CTRL + X: Вырезать выделенный элемент\n"
            hotkeys_text += "CTRL + V: Вставить выделенный элемент\n"
            hotkeys_text += "CTRL + Z: Отменить действие\n"
            hotkeys_text += "CTRL + Y: Повторить действие\n"
            hotkeys_text += "CTRL + A: Выделить все элементы\n"
            hotkeys_text += "CTRL + S: Сохранить документ\n"
            hotkeys_text += "CTRL + P: Печать\n"
            hotkeys_text += "CTRL + F: Поиск\n"
            hotkeys_text += "ALT + TAB: Переключение между открытыми приложениями\n"
            hotkeys_text += "ALT + F4: Закрыть активное приложение\n"
            hotkeys_text += "DELETE: Удалить элемент в корзину\n"
            hotkeys_text += "SHIFT + DELETE: Удалить элемент без помещения в корзину\n"
            hotkeys_text += "F2: Переименовать выделенный элемент\n"
            hotkeys_text += "F5: Обновить активное окно\n"
            hotkeys_text += "ESC: Отменить текущую задачу\n"
            hotkeys_text += "WIN: Открыть или закрыть меню 'Пуск'\n"
            hotkeys_text += "WIN + A: Открыть Центр уведомлений\n"
            hotkeys_text += "WIN + D: Показать/скрыть рабочий стол\n"
            hotkeys_text += "WIN + E: Открыть Проводник\n"
            hotkeys_text += "WIN + I: Открыть Параметры Windows\n"
            hotkeys_text += "WIN + L: Заблокировать компьютер\n"
            hotkeys_text += "WIN + R: Открыть диалоговое окно 'Выполнить'\n"
            hotkeys_text += "WIN + S: Открыть поиск Windows\n"
            hotkeys_text += "WIN + V: Открыть буфер обмена\n"
            hotkeys_text += "WIN + . : Открыть панель эмодзи\n"
            hotkeys_text += "WIN + СТРЕЛКА ВВЕРХ: Развернуть окно\n"
            hotkeys_text += "WIN + СТРЕЛКА ВНИЗ: Свернуть окно\n"
            hotkeys_text += "WIN + СТРЕЛКА ВЛЕВО: Прикрепить окно к левой части экрана\n"
            hotkeys_text += "WIN + СТРЕЛКА ВПРАВО: Прикрепить окно к правой части экрана\n"
            hotkeys_text += "CTRL + SHIFT + ESC: Открыть Диспетчер задач\n"
        text.insert(tk.END, hotkeys_text)
        text.config(state=tk.DISABLED)

    def reinstall_windows(self):
        try:
            subprocess.Popen('control.exe /name Microsoft.Recovery', shell=True)
        except Exception as e:
            try:
                subprocess.Popen('systempropertiesrecovery', shell=True)
            except Exception as e2:
                messagebox.showerror("Ошибка", f"Не удалось открыть настройки восстановления: {str(e2)}")

    def get_size(self, bytes):
        for unit in ['', 'K', 'M', 'G', 'T', 'P']:
            if bytes < 1024:
                return f"{bytes:.2f}{unit}B"
            bytes /= 1024


class AdvancedProcessMonitor:
    def __init__(self, root, username):
        self.root = root
        self.username = username
        self.root.title(f"CUBE Process Monitor - {username}")
        self.root.geometry("1400x800")
        self.root.configure(bg="#000000")
        self.sort_column = 'Memory'
        self.sort_ascending = False
        self.startup_items = []
        self.is_filtering = False
        self.search_cache = []
        self.memory_history = []
        self.max_history_length = 50
        self.cpu_history = []
        self.memory_usage = 0
        self.cpu_usage = 0
        self.child_windows = []
        self.create_widgets()
        self.load_startup_items()
        self.update_processes()
        self.auto_update()

    def create_widgets(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('.', background='#000000', foreground='#ffffff', fieldbackground='#222222')
        self.style.map('.', background=[('selected', '#333333')])
        self.style.configure('Treeview', background='#111111', foreground='#ffffff', fieldbackground='#111111')
        self.style.map('Treeview', background=[('selected', '#333333')])
        self.style.configure('TLabelframe', background='#000000', foreground='#ffffff')
        self.style.configure('TLabelframe.Label', background='#000000', foreground='#ffffff')
        main = ttk.Frame(self.root, padding="10")
        main.pack(fill=tk.BOTH, expand=True)
        left = ttk.Frame(main)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        right = ttk.Frame(main, width=400)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)
        right.pack_propagate(False)
        greeting = ttk.Frame(left)
        greeting.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(greeting, text=f"{self.username}, добро пожаловать в CUBE Process Monitor!",
                  font=("Arial", 12, "bold"), foreground="#ffffff").pack(side=tk.LEFT)
        self.info_frame = ttk.LabelFrame(left, text="Системная информация", padding="10")
        self.info_frame.pack(fill=tk.X, pady=(0, 10))
        info_grid = ttk.Frame(self.info_frame)
        info_grid.pack(fill=tk.X)
        self.cpu_label = ttk.Label(info_grid, text="CPU: 0%", font=('Arial', 10), foreground='#ffffff')
        self.cpu_label.grid(row=0, column=0, padx=10, sticky=tk.W)
        self.mem_label = ttk.Label(info_grid, text="Память: 0/0 GB (0%)", font=('Arial', 10), foreground='#ffffff')
        self.mem_label.grid(row=0, column=1, padx=10, sticky=tk.W)
        self.optimize_btn = ttk.Button(info_grid, text="⚡ ОПТИМИЗИРОВАТЬ", command=self.optimize_memory)
        self.optimize_btn.grid(row=0, column=2, padx=20)
        self.graph_btn = ttk.Button(info_grid, text="📊 Графики", command=self.open_graphs)
        self.graph_btn.grid(row=0, column=3, padx=20)
        control = ttk.Frame(left)
        control.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(control, text="Поиск процесса:", font=('Arial', 9), foreground='#ffffff').pack(side=tk.LEFT,
                                                                                                 padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(control, textvariable=self.search_var, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.search_entry.bind('<KeyRelease>', self.filter_processes)
        self.update_btn = ttk.Button(control, text="🔄 Обновить", command=self.update_processes)
        self.update_btn.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(control, text="Сортировка:", font=('Arial', 9), foreground='#ffffff').pack(side=tk.LEFT, padx=(20, 5))
        ttk.Button(control, text="По памяти", command=lambda: self.sort_processes('Memory')).pack(side=tk.LEFT,
                                                                                                  padx=(0, 5))
        ttk.Button(control, text="По CPU", command=lambda: self.sort_processes('CPU %')).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control, text="По имени", command=lambda: self.sort_processes('Name')).pack(side=tk.LEFT)
        ttk.Button(control, text="🔍 Поиск майнеров", command=self.scan_for_miners).pack(side=tk.LEFT, padx=(20, 5))
        self.tree_frame = ttk.LabelFrame(left, text="Процессы", padding="10")
        self.tree_frame.pack(fill=tk.BOTH, expand=True)


        columns = ('PID', 'Name', 'Memory', 'Memory %', 'Status', 'User', 'CPU %')
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show='headings', height=20)
        vsb = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        hsb = ttk.Scrollbar(self.tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(column=0, row=0, sticky='nsew', in_=self.tree_frame)
        vsb.grid(column=1, row=0, sticky='ns', in_=self.tree_frame)
        hsb.grid(column=0, row=1, sticky='ew', in_=self.tree_frame)
        self.tree_frame.grid_columnconfigure(0, weight=1)
        self.tree_frame.grid_rowconfigure(0, weight=1)

        column_widths = {
            'PID': 80, 'Name': 200, 'Memory': 120, 'Memory %': 100,
            'Status': 120, 'User': 150, 'CPU %': 80
        }
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths.get(col, 100))

        self.menu = tk.Menu(self.tree, tearoff=0)
        self.menu.add_command(label="Завершить процесс", command=self.kill_selected_process)
        self.menu.add_command(label="Подробности", command=self.show_process_details)
        self.tree.bind('<Button-3>', self.show_context_menu)

        self.status_var = tk.StringVar()
        self.status_var.set("Готово")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        startup_frame = ttk.LabelFrame(right, text="Автозагрузка", padding="10")
        startup_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        startup_columns = ('Name', 'Path', 'Enabled', 'Location')
        self.startup_tree = ttk.Treeview(startup_frame, columns=startup_columns, show='headings', height=10)
        startup_vsb = ttk.Scrollbar(startup_frame, orient=tk.VERTICAL, command=self.startup_tree.yview)
        self.startup_tree.configure(yscrollcommand=startup_vsb.set)
        self.startup_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        startup_vsb.pack(side=tk.RIGHT, fill=tk.Y)

        for col in startup_columns:
            self.startup_tree.heading(col, text=col)
            self.startup_tree.column(col, width=120)

        self.startup_menu = tk.Menu(self.startup_tree, tearoff=0)
        self.startup_menu.add_command(label="Включить/Выключить", command=self.toggle_startup_item)
        self.startup_tree.bind('<Button-3>', self.show_startup_context_menu)

        cube_frame = ttk.LabelFrame(right, text="3D Куб", padding="10")
        cube_frame.pack(fill=tk.BOTH, expand=True)
        self.cube_canvas = tk.Canvas(cube_frame, width=300, height=300, bg='#000000', highlightthickness=0)
        self.cube_canvas.pack(fill=tk.BOTH, expand=True)
        self.rotation_x = 0
        self.rotation_y = 0
        self.auto_rotate = True
        self.cube_canvas.bind('<Button-1>', self.set_last_pos)
        self.cube_canvas.bind('<B1-Motion>', self.rotate_cube)
        self.cube_canvas.bind('<Double-Button-1>', self.reset_rotation)
        self.cube_canvas.bind('<Enter>', self.enable_auto_rotate)
        self.auto_rotate_cube()

    def open_graphs(self):
        graph_window = GraphWindow(self.root)
        self.child_windows.append(graph_window.window)
        graph_window.window.protocol("WM_DELETE_WINDOW",
                                     lambda: self.on_child_close(graph_window.window))

    def on_child_close(self, window):
        if window in self.child_windows:
            self.child_windows.remove(window)
        window.destroy()

    def get_size(self, bytes):
        for unit in ['', 'K', 'M', 'G', 'T', 'P']:
            if bytes < 1024:
                return f"{bytes:.2f}{unit}B"
            bytes /= 1024

    def filter_processes(self, event=None):
        search_term = self.search_var.get().lower()
        if not search_term:
            for item in self.tree.get_children():
                self.tree.reattach(item, '', 'end')
            return

        if not self.search_cache:
            self.search_cache = []
            for item in self.tree.get_children():
                values = self.tree.item(item)['values']
                self.search_cache.append((item, values))

        for item, values in self.search_cache:
            if search_term in str(values).lower():
                self.tree.reattach(item, '', 'end')
            else:
                self.tree.detach(item)

    def sort_processes(self, column):
        if column == self.sort_column:
            self.sort_ascending = not self.sort_ascending
        else:
            self.sort_column = column
            self.sort_ascending = False

        items = [(self.tree.set(item, column), item) for item in self.tree.get_children('')]
        try:
            if column in ['Memory', 'Memory %', 'CPU %']:
                items.sort(key=lambda x: float(x[0].replace('B', '').replace('%', '')),
                           reverse=not self.sort_ascending)
            else:
                items.sort(key=lambda x: x[0].lower(), reverse=not self.sort_ascending)
        except:
            items.sort(key=lambda x: x[0].lower(), reverse=not self.sort_ascending)

        for index, (value, item) in enumerate(items):
            self.tree.move(item, '', index)

        self.status_var.set(f"Сортировка по: {column} {'↑' if self.sort_ascending else '↓'}")

    def update_processes(self):
        self.search_cache = []
        for item in self.tree.get_children():
            self.tree.delete(item)

        mem = psutil.virtual_memory()
        cpu = psutil.cpu_percent()
        self.cpu_label.config(text=f"CPU: {cpu}%")
        self.mem_label.config(text=f"Память: {self.get_size(mem.used)}/{self.get_size(mem.total)} ({mem.percent}%)")

        processes = []
        for proc in psutil.process_iter(
                ['pid', 'name', 'memory_info', 'memory_percent', 'status', 'username', 'cpu_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        processes.sort(key=lambda p: p['memory_info'].rss if p['memory_info'] else 0, reverse=True)

        process_count = 0
        for proc in processes:
            try:
                pid = proc['pid']
                name = proc['name'] or "N/A"
                memory = self.get_size(proc['memory_info'].rss) if proc['memory_info'] else "0B"
                memory_percent = f"{proc['memory_percent']:.2f}" if proc['memory_percent'] else "0.00"
                status = proc['status'] or "N/A"
                username = proc['username'] or "SYSTEM"
                cpu_percent = f"{proc['cpu_percent']:.1f}" if proc['cpu_percent'] else "0.0"

                tags = ()
                try:
                    if float(memory_percent) > 10 or float(cpu_percent) > 30:
                        tags = ('high_usage',)
                    elif float(memory_percent) > 5 or float(cpu_percent) > 15:
                        tags = ('medium_usage',)
                except:
                    pass

                self.tree.insert('', 'end', values=(
                    pid, name, memory, memory_percent, status, username, cpu_percent
                ), tags=tags)
                process_count += 1
            except:
                continue

        self.tree.tag_configure('high_usage', foreground='#ff6666')
        self.tree.tag_configure('medium_usage', foreground='#ff9966')

        if self.search_var.get():
            self.filter_processes()

        self.status_var.set(
            f"Найдено процессов: {process_count}. Последнее обновление: {time.strftime('%H:%M:%S')}")

    def auto_update(self):
        self.update_processes()
        self.root.after(3000, self.auto_update)

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.menu.post(event.x_root, event.y_root)

    def kill_selected_process(self):
        selected = self.tree.selection()
        if not selected:
            return

        item = selected[0]
        values = self.tree.item(item)['values']
        pid = values[0]
        name = values[1]

        try:
            process = psutil.Process(pid)
            process.terminate()
            time.sleep(0.5)
            messagebox.showinfo("Успех", f"Процесс {name} (PID: {pid}) завершен")
            self.update_processes()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось завершить процесс: {str(e)}")

    def show_process_details(self):
        selected = self.tree.selection()
        if not selected:
            return

        item = selected[0]
        values = self.tree.item(item)['values']
        pid = values[0]

        try:
            process = psutil.Process(pid)
            with process.oneshot():
                info = f"""
Детальная информация о процессе:
PID: {pid}
Имя: {process.name()}
Статус: {process.status()}
Память: {self.get_size(process.memory_info().rss)}
Память (%): {process.memory_percent():.2f}%
CPU (%): {process.cpu_percent():.1f}%
Путь: {process.exe() or 'Не доступен'}
Запущен: {time.ctime(process.create_time())}
Пользователь: {process.username()}
                """

            detail_window = tk.Toplevel(self.root)
            self.child_windows.append(detail_window)
            detail_window.title(f"Детали процесса: {process.name()}")
            detail_window.geometry("500x400")
            detail_window.configure(bg="#000000")
            detail_window.protocol("WM_DELETE_WINDOW",
                                   lambda: self.on_child_close(detail_window))

            text_widget = tk.Text(detail_window, bg="#111111", fg="#ffffff", font=("Arial", 10))
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            text_widget.insert(tk.END, info)
            text_widget.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось получить информацию: {str(e)}")

    def optimize_memory(self):
        try:
            processes_to_kill = []
            total_memory = 0

            for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'username']):
                try:
                    if (proc.info['memory_info'].rss > 100 * 1024 * 1024 and
                            proc.info['username'] and
                            not any(sys_proc in proc.info['name'].lower() for sys_proc in
                                    ['system', 'svchost', 'wininit', 'winlogon', 'csrss', 'lsass', 'services',
                                     'explorer'])):
                        processes_to_kill.append(proc.info)
                        total_memory += proc.info['memory_info'].rss
                except:
                    continue

            if not processes_to_kill:
                messagebox.showinfo("Оптимизация", "Нет процессов для оптимизации")
                return

            processes_to_kill.sort(key=lambda p: p['memory_info'].rss, reverse=True)
            killed = 0

            for proc in processes_to_kill[:5]:  
                try:
                    p = psutil.Process(proc['pid'])
                    p.terminate()
                    killed += 1
                    time.sleep(0.3)
                except:
                    continue

            messagebox.showinfo("Оптимизация",
                                f"Завершено процессов: {killed}\n"
                                f"Освобождено памяти: {self.get_size(total_memory)}")
            self.update_processes()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось выполнить оптимизацию: {str(e)}")

    def is_system_process(self, username):
        system_users = ['SYSTEM', 'LOCAL SERVICE', 'NETWORK SERVICE']
        return username in system_users if username else False

    def scan_for_miners(self):
        suspicious_processes = []
        miner_keywords = [
            'miner', 'xmrig', 'nicehash', 'ethminer', 'ccminer',
            'cgminer', 'minerd', 'nbminer', 't-rex', 'lolminer'
        ]

        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'username']):
            try:
                proc_name = proc.info['name'].lower() if proc.info['name'] else ''
                if any(keyword in proc_name for keyword in miner_keywords):
                    suspicious_processes.append(proc.info)
                    continue

                if (proc.info['cpu_percent'] and proc.info['cpu_percent'] > 40 and
                        proc.info['memory_percent'] and proc.info['memory_percent'] > 5):
                    if not self.is_system_process(proc.info['username']):
                        suspicious_processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        if suspicious_processes:
            result = "Найдены подозрительные процессы:\n\n"
            for proc in suspicious_processes:
                result += f"PID: {proc['pid']}, Имя: {proc['name']}, CPU: {proc['cpu_percent']}%, Память: {proc['memory_percent']:.2f}%\n"

            result_window = tk.Toplevel(self.root)
            self.child_windows.append(result_window)
            result_window.title("Результаты поиска майнеров")
            result_window.geometry("600x400")
            result_window.configure(bg="#000000")
            result_window.protocol("WM_DELETE_WINDOW",
                                   lambda: self.on_child_close(result_window))

            text = tk.Text(result_window, bg="#111111", fg="#ffffff", font=("Arial", 10))
            scrollbar = ttk.Scrollbar(result_window, orient=tk.VERTICAL, command=text.yview)
            text.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            text.insert(tk.END, result)
            text.config(state=tk.DISABLED)

            btn_frame = ttk.Frame(result_window)
            btn_frame.pack(fill=tk.X, pady=10)
            ttk.Button(btn_frame, text="Завершить все подозрительные процессы",
                       command=lambda: self.kill_suspicious_processes(suspicious_processes)).pack(pady=5)
        else:
            messagebox.showinfo("Поиск майнеров", "Подозрительные процессы не обнаружены.")

    def kill_suspicious_processes(self, processes):
        killed = 0
        for proc in processes:
            try:
                p = psutil.Process(proc['pid'])
                p.terminate()
                killed += 1
                time.sleep(0.1)
            except:
                continue

        messagebox.showinfo("Завершение процессов", f"Завершено процессов: {killed}")
        self.update_processes()

    def set_last_pos(self, event):
        self.last_x = event.x
        self.last_y = event.y
        self.auto_rotate = False

    def rotate_cube(self, event):
        dx = event.x - self.last_x
        dy = event.y - self.last_y
        self.rotation_y += dx * 0.5
        self.rotation_x += dy * 0.5
        self.last_x = event.x
        self.last_y = event.y
        self.draw_cube()
        self.auto_rotate = False

    def enable_auto_rotate(self, event=None):
        self.auto_rotate = True

    def reset_rotation(self, event):
        self.rotation_x = 0
        self.rotation_y = 0
        self.draw_cube()
        self.auto_rotate = True

    def auto_rotate_cube(self):
        if self.auto_rotate:
            self.rotation_x += 0.5
            self.rotation_y += 0.5
            self.draw_cube()
        self.root.after(50, self.auto_rotate_cube)

    def draw_cube(self):
        self.cube_canvas.delete("all")
        w, h = self.cube_canvas.winfo_width(), self.cube_canvas.winfo_height()
        if w <= 1 or h <= 1:
            return

        cx, cy = w // 2, h // 2
        size = min(w, h) * 0.3

        vertices = [
            [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
            [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]
        ]

        edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),
            (4, 5), (5, 6), (6, 7), (7, 4),
            (0, 4), (1, 5), (2, 6), (3, 7)
        ]

        rotated = []
        for vertex in vertices:
            x, y, z = vertex
            y_rot = math.radians(self.rotation_y)
            x_new = x * math.cos(y_rot) + z * math.sin(y_rot)
            z_new = -x * math.sin(y_rot) + z * math.cos(y_rot)

            x_rot = math.radians(self.rotation_x)
            y_new = y * math.cos(x_rot) - z_new * math.sin(x_rot)
            z_final = y * math.sin(x_rot) + z_new * math.cos(x_rot)

            rotated.append([x_new, y_new, z_final])

        projected = []
        for vertex in rotated:
            x, y, z = vertex
            scale = 1 / (2 + z)
            x2d = x * size * scale + cx
            y2d = y * size * scale + cy
            projected.append([x2d, y2d])

        for edge in edges:
            x1, y1 = projected[edge[0]]
            x2, y2 = projected[edge[1]]
            self.cube_canvas.create_line(x1, y1, x2, y2, fill="#ffffff", width=2)

    def load_startup_items(self):
        for item in self.startup_tree.get_children():
            self.startup_tree.delete(item)

        self.startup_items = []

        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run") as key:
                i = 0
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(key, i)
                        self.startup_items.append({
                            'name': name,
                            'path': value,
                            'enabled': True,
                            'location': 'HKCU'
                        })
                        i += 1
                    except WindowsError:
                        break
        except:
            pass

        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run") as key:
                i = 0
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(key, i)
                        self.startup_items.append({
                            'name': name,
                            'path': value,
                            'enabled': True,
                            'location': 'HKLM'
                        })
                        i += 1
                    except WindowsError:
                        break
        except:
            pass

        startup_dir = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup')
        if os.path.exists(startup_dir):
            for item in os.listdir(startup_dir):
                if item.endswith('.lnk') or item.endswith('.exe'):
                    full_path = os.path.join(startup_dir, item)
                    self.startup_items.append({
                        'name': item,
                        'path': full_path,
                        'enabled': True,
                        'location': 'Startup Folder'
                    })

        for item in self.startup_items:
            self.startup_tree.insert('', 'end', values=(
                item['name'],
                item['path'],
                'Да' if item['enabled'] else 'Нет',
                item['location']
            ))

    def show_startup_context_menu(self, event):
        item = self.startup_tree.identify_row(event.y)
        if item:
            self.startup_tree.selection_set(item)
            self.startup_menu.post(event.x_root, event.y_root)

    def toggle_startup_item(self):
        selected = self.startup_tree.selection()
        if not selected:
            return

        item = selected[0]
        values = self.startup_tree.item(item)['values']
        name = values[0]

        for startup_item in self.startup_items:
            if startup_item['name'] == name:
                startup_item['enabled'] = not startup_item['enabled']

                self.startup_tree.item(item, values=(
                    startup_item['name'],
                    startup_item['path'],
                    'Да' if startup_item['enabled'] else 'Нет',
                    startup_item['location']
                ))

                try:
                    if startup_item['location'] == 'HKCU':
                        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                             r"Software\Microsoft\Windows\CurrentVersion\Run",
                                             0, winreg.KEY_SET_VALUE)
                    elif startup_item['location'] == 'HKLM':
                        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                             r"Software\Microsoft\Windows\CurrentVersion\Run",
                                             0, winreg.KEY_SET_VALUE)
                    else:
                        messagebox.showinfo("Информация",
                                            "Для элементов из папки автозагрузки необходимо вручную удалить или добавить файл")
                        return

                    if startup_item['enabled']:
                        winreg.SetValueEx(key, startup_item['name'], 0, winreg.REG_SZ, startup_item['path'])
                    else:
                        winreg.DeleteValue(key, startup_item['name'])

                    winreg.CloseKey(key)
                    messagebox.showinfo("Успех",
                                        f"Автозагрузка для {name} {'включена' if startup_item['enabled'] else 'выключена'}")
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось изменить автозагрузку: {str(e)}")

                break


class PongGame:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Ping Pong")
        self.window.geometry("800x600")
        self.window.configure(bg="#000000")
        self.window.resizable(False, False)

        self.canvas = tk.Canvas(self.window, width=800, height=600, bg='black', highlightthickness=0)
        self.canvas.pack()

        self.width = 800
        self.height = 600
        self.paddle_width = 15
        self.paddle_height = 100
        self.ball_size = 15
        self.paddle_speed = 20

        self.left_paddle_y = self.height // 2 - self.paddle_height // 2
        self.right_paddle_y = self.height // 2 - self.paddle_height // 2

        self.ball_x = self.width // 2
        self.ball_y = self.height // 2
        self.ball_dx = 5  # скорость по x
        self.ball_dy = 5  # скорость по y

        self.left_score = 0
        self.right_score = 0

        self.left_paddle = self.canvas.create_rectangle(
            50, self.left_paddle_y,
            50 + self.paddle_width, self.left_paddle_y + self.paddle_height,
            fill="white"
        )
        self.right_paddle = self.canvas.create_rectangle(
            self.width - 50 - self.paddle_width, self.right_paddle_y,
            self.width - 50, self.right_paddle_y + self.paddle_height,
            fill="white"
        )
        self.ball = self.canvas.create_oval(
            self.ball_x - self.ball_size, self.ball_y - self.ball_size,
            self.ball_x + self.ball_size, self.ball_y + self.ball_size,
            fill="white"
        )
        self.score_text = self.canvas.create_text(
            self.width // 2, 50,
            text=f"{self.left_score} : {self.right_score}",
            fill="white",
            font=("Arial", 24)
        )

        self.window.bind('<KeyPress>', self.key_press)
        self.window.focus_set()
        self.update()

        exit_btn = ttk.Button(self.window, text="Выход", command=self.window.destroy)
        exit_btn.place(x=10, y=10)

    def key_press(self, event):
        key = event.keysym
        if key == 'w':
            self.left_paddle_y = max(0, self.left_paddle_y - self.paddle_speed)
        elif key == 's':
            self.left_paddle_y = min(self.height - self.paddle_height, self.left_paddle_y + self.paddle_speed)
        elif key == 'Up':
            self.right_paddle_y = max(0, self.right_paddle_y - self.paddle_speed)
        elif key == 'Down':
            self.right_paddle_y = min(self.height - self.paddle_height, self.right_paddle_y + self.paddle_speed)

        self.canvas.coords(self.left_paddle,
                           50, self.left_paddle_y,
                           50 + self.paddle_width, self.left_paddle_y + self.paddle_height)
        self.canvas.coords(self.right_paddle,
                           self.width - 50 - self.paddle_width, self.right_paddle_y,
                           self.width - 50, self.right_paddle_y + self.paddle_height)

    def update(self):
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy

        if self.ball_y <= 0 or self.ball_y >= self.height:
            self.ball_dy *= -1

        if (self.ball_x - self.ball_size <= 50 + self.paddle_width and
                self.ball_y >= self.left_paddle_y and
                self.ball_y <= self.left_paddle_y + self.paddle_height):
            self.ball_dx = abs(self.ball_dx)

        if (self.ball_x + self.ball_size >= self.width - 50 - self.paddle_width and
                self.ball_y >= self.right_paddle_y and
                self.ball_y <= self.right_paddle_y + self.paddle_height):
            self.ball_dx = -abs(self.ball_dx)

        if self.ball_x < 0:
            self.right_score += 1
            self.reset_ball()
        elif self.ball_x > self.width:
            self.left_score += 1
            self.reset_ball()

        self.canvas.coords(self.ball,
                           self.ball_x - self.ball_size, self.ball_y - self.ball_size,
                           self.ball_x + self.ball_size, self.ball_y + self.ball_size
                           )

        self.canvas.itemconfig(self.score_text, text=f"{self.left_score} : {self.right_score}")

        self.window.after(30, self.update)

    def reset_ball(self):
        self.ball_x = self.width // 2
        self.ball_y = self.height // 2
        self.ball_dx *= -1
        self.ball_dy = random.choice([-5, 5])


def main():
    root = tk.Tk()
    welcome = WelcomeScreen(root)
    root.mainloop()

    if hasattr(welcome, 'username'):
        root = tk.Tk()
        app = MainMenu(root, welcome.username)
        root.mainloop()


if __name__ == "__main__":
    main()
