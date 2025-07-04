import os
import re
import threading
import time
import random
import tkinter as tk
import sys
import ctypes
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import filedialog, ttk, messagebox, scrolledtext
from pynput import keyboard
from collections import deque

def is_admin():
    """Проверка прав администратора"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

class OsuAutoPlayer:
    def __init__(self):
        self.active = False
        self.key_controller = keyboard.Controller()
        self.hotkey_listener = None
        self.play_thread = None
        self.current_key = 0
        self.keys = ["z", "x"]
        self.spread = 10
        self.calibration = 0
        self.delay = 0
        self.ignore_spinners = True
        self.osu_path = ""
        self.song_dir = ""
        self.diff_file = ""
        self.hotkey = "f6"
        self.last_key = None
        self.hotkey_active = True
        self.slider_multiplier = 1.4
        self.log_data = []
        self.log_counter = 0
        self.calibration_history = {}
        self.latency_history = deque(maxlen=100)
        self.register_hotkey()

    def register_hotkey(self):
        """Регистрация горячей клавиши"""
        if self.hotkey_listener:
            self.hotkey_listener.stop()
        
        try:
            if self.hotkey.startswith('f') and self.hotkey[1:].isdigit():
                hotkey_str = f'<{self.hotkey}>'
            else:
                hotkey_str = self.hotkey
                
            self.hotkey_listener = keyboard.GlobalHotKeys({
                hotkey_str: self.toggle_activation
            })
            self.hotkey_listener.start()
            return True
        except Exception as e:
            return False

    def parse_osu_file(self, file_path):
        hit_objects = []
        slider_multiplier = self.slider_multiplier
        timing_points = []
        
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            diff_match = re.search(r"\[Difficulty\][\s\S]*?SliderMultiplier\s*:\s*(\d*\.?\d+)", content)
            if diff_match:
                slider_multiplier = float(diff_match.group(1))
                self.slider_multiplier = slider_multiplier

            timing_section = re.search(r"\[TimingPoints\][\s\S]*?(\n\n|$)", content)
            if timing_section:
                for line in timing_section.group(0).split('\n')[1:]:
                    if not line.strip() or line.startswith('['):
                        continue
                    parts = line.split(',')
                    if len(parts) < 2:
                        continue
                    try:
                        time_val = int(float(parts[0]))
                        beat_length = float(parts[1])
                        uninherited = int(parts[6]) if len(parts) > 6 else 1
                        timing_points.append({
                            "time": time_val,
                            "beat_length": beat_length,
                            "uninherited": uninherited
                        })
                    except (ValueError, IndexError):
                        continue

            hit_objects_section = re.search(r"\[HitObjects]\s*(.*)", content, re.DOTALL | re.IGNORECASE)
            if not hit_objects_section:
                return []
            
            lines = hit_objects_section.group(1).strip().split('\n')
            for i, line in enumerate(lines):
                parts = line.split(',')
                if len(parts) < 5: 
                    continue
                
                try:
                    obj_type = int(parts[3])
                    time_val = int(parts[2])
                    
                    if obj_type & 1:
                        hit_objects.append(("press", time_val, "circle", i))
                        hit_objects.append(("release", time_val + 10, "circle", i))
                    
                    elif obj_type & 2 and len(parts) >= 8:
                        pixel_length = float(parts[7])
                        repeat = int(parts[6])
                        
                        current_tp = None
                        for tp in reversed(timing_points):
                            if tp["time"] <= time_val:
                                current_tp = tp
                                break
                        
                        if current_tp and current_tp["uninherited"]:
                            duration = (pixel_length * repeat) / (slider_multiplier * 100) * current_tp["beat_length"]
                        else:
                            duration = (pixel_length * repeat) / (slider_multiplier * 100) * 1000
                            
                        hit_objects.append(("press", time_val, "slider_start", i))
                        hit_objects.append(("release", time_val + duration, "slider_end", i))
                    
                    elif obj_type & 8 and not self.ignore_spinners:
                        end_time = int(parts[5])
                        hit_objects.append(("press", time_val, "spinner_start", i))
                        hit_objects.append(("release", end_time, "spinner_end", i))
                        
                except (ValueError, IndexError):
                    continue
                    
            return sorted(hit_objects, key=lambda x: x[1])
        
        except Exception:
            return []

    def play_beatmap(self, hit_objects):
        if not hit_objects:
            return
            
        # Предстартовый отсчет
        for i in range(3, 0, -1):
            if not self.active: 
                return
            time.sleep(1)
        
        start_time = time.time() * 1000 + self.delay
        self.current_key = 0
        self.log_data = []
        self.log_counter = 0
        self.latency_history.clear()
        
        key_states = {key: False for key in self.keys}
        active_objects = {}
        
        try:
            for i, (action, obj_time, obj_type, obj_id) in enumerate(hit_objects):
                if not self.active: 
                    break
                    
                target_time = start_time + obj_time - self.calibration
                offset = 0
                if "press" in action:
                    offset = random.uniform(-self.spread, self.spread)
                    target_time += offset
                    
                current_time = time.time() * 1000
                if current_time < target_time:
                    sleep_time = (target_time - current_time) / 1000 * 0.9
                    if sleep_time > 0.001:
                        time.sleep(sleep_time)
                    
                    while time.time() * 1000 < target_time:
                        pass
                
                current_time = time.time() * 1000
                latency = current_time - target_time
                self.latency_history.append(latency)
                
                self.log_event(
                    action=action[0],  # 'p' или 'r'
                    obj_type=obj_type[0],  # Первая буква типа
                    obj_time=obj_time,
                    latency=int(latency),
                    offset=int(offset) if offset else 0
                )
                
                if "press" in action:
                    if "slider" in obj_type:
                        key = self.keys[0]
                    else:
                        key = self.keys[self.current_key]
                        self.current_key = (self.current_key + 1) % len(self.keys)
                    
                    if not key_states[key]:
                        self.key_controller.press(key)
                        key_states[key] = True
                        self.last_key = key
                        active_objects[obj_id] = key
                
                elif "release" in action:
                    key = active_objects.get(obj_id, self.last_key if self.last_key else self.keys[0])
                    
                    if key_states.get(key, False):
                        self.key_controller.release(key)
                        key_states[key] = False
                        if obj_id in active_objects:
                            del active_objects[obj_id]
            
            for key, pressed in key_states.items():
                if pressed:
                    self.key_controller.release(key)
                
        except Exception:
            self.save_log()
        finally:
            self.active = False
            self.save_log()
            
            # Сохраняем калибровку для карты
            if self.song_dir and self.diff_file:
                map_id = f"{self.song_dir}_{self.diff_file}"
                self.calibration_history[map_id] = self.calibration

    def log_event(self, action, obj_type, obj_time, latency, offset=0):
        """Компактное логирование событий"""
        self.log_data.append({
            "a": action,        # p/r (press/release)
            "t": obj_type,      # c/s/e (circle/slider_end/etc)
            "tm": obj_time,     # время объекта
            "l": latency,       # задержка
            "o": offset         # разброс
        })
        self.log_counter += 1

    def save_log(self):
        """Сохранение компактного лога"""
        if not self.log_data:
            return
            
        try:
            log_file = f"osu_log_{int(time.time())}.json"
            with open(log_file, "w", encoding="utf-8") as f:
                json.dump({
                    "m": {  # Метаданные
                        "s": self.song_dir,
                        "d": self.diff_file,
                        "c": self.calibration,
                        "sm": self.slider_multiplier
                    },
                    "e": self.log_data  # События
                }, f)
                
            return log_file
        except Exception:
            return None

    def auto_calibrate(self, log_file=None):
        """Автоматическая калибровка на основе логов"""
        if not log_file:
            # Создаем тестовый лог
            self.calibration = 0
            self.toggle_activation()
            if self.play_thread:
                self.play_thread.join()
            log_file = "osu_log_test.json"
        
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                log = json.load(f)
            
            # Анализируем только круги (нажатия)
            press_latencies = [
                e["l"] for e in log["e"] 
                if e["a"] == "p" and e["t"] == "c"
            ]
            
            if not press_latencies:
                return False
                
            # Рассчитываем медианную задержку
            median_latency = sorted(press_latencies)[len(press_latencies) // 2]
            
            # Корректируем калибровку
            self.calibration += int(median_latency * 0.7)
            
            # Ограничиваем диапазон
            self.calibration = max(-100, min(100, self.calibration))
            return True
            
        except Exception:
            return False

    def toggle_activation(self):
        if not self.song_dir or not self.diff_file:
            return
            
        self.active = not self.active
        if self.active:
            osu_path = os.path.join(self.osu_path, "Songs", self.song_dir, self.diff_file)
            hit_objects = self.parse_osu_file(osu_path)
            
            self.play_thread = threading.Thread(
                target=self.play_beatmap, 
                args=(hit_objects,),
                daemon=True
            )
            self.play_thread.start()

class OsuAutoPlayerGUI:
    def __init__(self, master):
        self.master = master
        self.player = OsuAutoPlayer()
        master.title("osu! Auto Player v5")
        master.geometry("800x650")
        master.resizable(True, True)
        
        # Стиль
        style = ttk.Style()
        style.configure("TFrame", padding=5)
        style.configure("TButton", padding=5)
        style.configure("TLabel", padding=5)
        
        # Основные фреймы
        main_frame = ttk.Frame(master)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Notebook для вкладок
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Вкладка основного управления
        control_frame = ttk.Frame(self.notebook)
        self.notebook.add(control_frame, text="Управление")
        
        # Вкладка графиков
        graph_frame = ttk.Frame(self.notebook)
        self.notebook.add(graph_frame, text="Анализ")
        
        # Вкладка логов
        log_frame = ttk.Frame(self.notebook)
        self.notebook.add(log_frame, text="Логи")
        
        # === Control Frame ===
        path_frame = ttk.LabelFrame(control_frame, text="Настройки osu!")
        path_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(path_frame, text="Папка osu!:").grid(row=0, column=0, sticky="w")
        self.osu_path_entry = ttk.Entry(path_frame, width=50)
        self.osu_path_entry.grid(row=0, column=1, padx=5)
        ttk.Button(path_frame, text="Обзор", command=self.browse_osu_path).grid(row=0, column=2)
        
        beatmap_frame = ttk.LabelFrame(control_frame, text="Выбор карты")
        beatmap_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(beatmap_frame, text="Песня:").grid(row=0, column=0, sticky="w")
        self.song_var = tk.StringVar()
        self.song_combobox = ttk.Combobox(beatmap_frame, textvariable=self.song_var, width=40)
        self.song_combobox.grid(row=0, column=1, padx=5, pady=2)
        self.song_combobox.bind("<<ComboboxSelected>>", self.on_song_selected)
        self.song_combobox.bind('<KeyRelease>', self.filter_songs)
        
        ttk.Label(beatmap_frame, text="Сложность:").grid(row=1, column=0, sticky="w")
        self.diff_var = tk.StringVar()
        self.diff_combobox = ttk.Combobox(beatmap_frame, textvariable=self.diff_var, width=40)
        self.diff_combobox.grid(row=1, column=1, padx=5, pady=2)
        self.diff_combobox.bind('<KeyRelease>', self.filter_diffs)
        
        ttk.Label(beatmap_frame, text="Slider Multiplier:").grid(row=2, column=0, sticky="w")
        self.slider_multiplier_var = tk.StringVar(value="1.4")
        ttk.Label(beatmap_frame, textvariable=self.slider_multiplier_var, 
                 font=("Arial", 10, "bold"), foreground="blue").grid(row=2, column=1, sticky="w", padx=5)
        
        ttk.Button(beatmap_frame, text="Обновить", command=self.load_songs).grid(row=0, column=2, rowspan=3, padx=5)
        
        settings_frame = ttk.LabelFrame(control_frame, text="Настройки игры")
        settings_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(settings_frame, text="Клавиша 1:").grid(row=0, column=0, sticky="w")
        self.key1_var = tk.StringVar(value="z")
        ttk.Entry(settings_frame, textvariable=self.key1_var, width=5).grid(row=0, column=1, padx=5)
        
        ttk.Label(settings_frame, text="Клавиша 2:").grid(row=0, column=2, sticky="w")
        self.key2_var = tk.StringVar(value="x")
        ttk.Entry(settings_frame, textvariable=self.key2_var, width=5).grid(row=0, column=3, padx=5)
        
        ttk.Label(settings_frame, text="Горячая клавиша:").grid(row=0, column=4, sticky="w")
        self.hotkey_var = tk.StringVar(value="f6")
        ttk.Entry(settings_frame, textvariable=self.hotkey_var, width=5).grid(row=0, column=5, padx=5)
        
        ttk.Label(settings_frame, text="Разброс (ms):").grid(row=1, column=0, sticky="w")
        self.spread_scale = ttk.Scale(settings_frame, from_=0, to=50, orient="horizontal")
        self.spread_scale.set(10)
        self.spread_scale.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        self.spread_value = tk.StringVar(value="10")
        ttk.Label(settings_frame, textvariable=self.spread_value).grid(row=1, column=3, padx=5)
        
        ttk.Label(settings_frame, text="Калибровка (ms):").grid(row=2, column=0, sticky="w")
        self.calibration_scale = ttk.Scale(settings_frame, from_=-100, to=100, orient="horizontal")
        self.calibration_scale.set(0)
        self.calibration_scale.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        self.calibration_value = tk.StringVar(value="0")
        ttk.Label(settings_frame, textvariable=self.calibration_value).grid(row=2, column=3, padx=5)
        
        ttk.Label(settings_frame, text="Задержка старта (ms):").grid(row=3, column=0, sticky="w")
        self.delay_scale = ttk.Scale(settings_frame, from_=0, to=10000, orient="horizontal")
        self.delay_scale.set(0)
        self.delay_scale.grid(row=3, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        self.delay_value = tk.StringVar(value="0")
        ttk.Label(settings_frame, textvariable=self.delay_value).grid(row=3, column=3, padx=5)
        
        self.ignore_spinners_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            settings_frame, text="Игнорировать спиннеры", 
            variable=self.ignore_spinners_var
        ).grid(row=4, column=0, columnspan=3, pady=5, sticky="w")
        
        self.hotkey_active_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            settings_frame, text="Активная горячая клавиша", 
            variable=self.hotkey_active_var
        ).grid(row=4, column=3, columnspan=3, pady=5, sticky="w")
        
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=10)
        
        self.start_button = ttk.Button(
            button_frame, text="Старт (F6)", 
            command=self.start_playback, width=15
        )
        self.start_button.pack(side=tk.LEFT, padx=10)
        
        self.stop_button = ttk.Button(
            button_frame, text="Стоп", 
            command=self.stop_playback, width=15, state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=10)
        
        self.calibrate_button = ttk.Button(
            button_frame, text="Автокалибровка", 
            command=self.auto_calibrate, width=15
        )
        self.calibrate_button.pack(side=tk.LEFT, padx=10)
        
        # === Graph Frame ===
        graph_settings = ttk.Frame(graph_frame)
        graph_settings.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(graph_settings, text="Тип графика:").pack(side=tk.LEFT, padx=5)
        self.graph_type = tk.StringVar(value="latency")
        graph_types = [("Задержки", "latency"), ("Точность", "accuracy"), ("Дрифт", "drift")]
        for text, mode in graph_types:
            ttk.Radiobutton(
                graph_settings, text=text, variable=self.graph_type,
                value=mode, command=self.update_graph
            ).pack(side=tk.LEFT, padx=5)
        
        self.figure = plt.Figure(figsize=(6, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Индикатор дрифта
        drift_frame = ttk.Frame(graph_frame)
        drift_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(drift_frame, text="Дрифт времени:").pack(side=tk.LEFT)
        self.drift_var = tk.StringVar(value="0.0 ms")
        ttk.Label(drift_frame, textvariable=self.drift_var, font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        
        # === Log Frame ===
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=15)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.log_text.config(state=tk.DISABLED)
        
        log_buttons = ttk.Frame(log_frame)
        log_buttons.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(log_buttons, text="Очистить", command=self.clear_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(log_buttons, text="Анализировать", command=self.analyze_logs).pack(side=tk.LEFT, padx=5)
        
        # Статус бар
        self.status_var = tk.StringVar(value="Готов")
        status_bar = ttk.Label(master, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Привязки
        self.master.bind('<F6>', lambda e: self.start_playback())
        
        # Инициализация
        self.song_list = []
        self.diff_names = []
        self.diff_map = {}
        
        self.spread_scale.config(command=lambda e: self.spread_value.set(f"{self.spread_scale.get():.0f}"))
        self.calibration_scale.config(command=lambda e: self.calibration_value.set(f"{self.calibration_scale.get():.0f}"))
        self.delay_scale.config(command=lambda e: self.delay_value.set(f"{self.delay_scale.get():.0f}"))
        
        # Обновление UI
        self.update_ui()

    def update_ui(self):
        """Обновление интерфейса"""
        # Обновление индикатора дрифта
        if self.player.latency_history:
            avg_drift = sum(self.player.latency_history) / len(self.player.latency_history)
            self.drift_var.set(f"{avg_drift:.1f} ms")
        
        # Планируем следующее обновление
        self.master.after(500, self.update_ui)

    def update_graph(self):
        """Обновление графика"""
        if not hasattr(self, 'log_data') or not self.log_data:
            return
            
        self.ax.clear()
        graph_type = self.graph_type.get()
        
        if graph_type == "latency":
            times = [e['tm'] for e in self.log_data]
            latencies = [e['l'] for e in self.log_data]
            self.ax.plot(times, latencies, 'b-', alpha=0.7)
            self.ax.set_title('Задержка нажатий')
            self.ax.set_xlabel('Время (ms)')
            self.ax.set_ylabel('Задержка (ms)')
            self.ax.grid(True)
            
        elif graph_type == "accuracy":
            # Гистограмма точности
            latencies = [e['l'] for e in self.log_data if e['a'] == 'p']
            if latencies:
                self.ax.hist(latencies, bins=20, color='green', alpha=0.7)
                self.ax.set_title('Распределение точности')
                self.ax.set_xlabel('Задержка (ms)')
                self.ax.set_ylabel('Количество нажатий')
                self.ax.grid(True)
        
        elif graph_type == "drift":
            # График дрифта времени
            times = [e['tm'] for e in self.log_data]
            latencies = [e['l'] for e in self.log_data]
            cumulative = np.cumsum(latencies)
            self.ax.plot(times, cumulative, 'r-', alpha=0.7)
            self.ax.set_title('Накопление ошибки времени')
            self.ax.set_xlabel('Время (ms)')
            self.ax.set_ylabel('Суммарная ошибка (ms)')
            self.ax.grid(True)
        
        self.canvas.draw()

    def clear_logs(self):
        """Очистка логов"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

    def analyze_logs(self):
        """Анализ логов и обновление калибровки"""
        if self.player.auto_calibrate():
            self.calibration_scale.set(self.player.calibration)
            self.calibration_value.set(f"{self.player.calibration:.0f}")
            self.status_var.set(f"Автокалибровка успешна! Новое значение: {self.player.calibration} ms")
        else:
            self.status_var.set("Ошибка автокалибровки. Недостаточно данных.")

    def auto_calibrate(self):
        """Запуск автокалибровки"""
        self.status_var.set("Запуск автокалибровки...")
        self.player.calibration = int(self.calibration_value.get())
        threading.Thread(target=self._run_calibration, daemon=True).start()

    def _run_calibration(self):
        """Фоновый процесс калибровки"""
        if self.player.auto_calibrate():
            self.master.after(0, lambda: self.status_var.set(
                f"Автокалибровка успешна! Новое значение: {self.player.calibration} ms"
            ))
            self.master.after(0, lambda: self.calibration_scale.set(self.player.calibration))
            self.master.after(0, lambda: self.calibration_value.set(f"{self.player.calibration:.0f}"))
        else:
            self.master.after(0, lambda: self.status_var.set("Ошибка автокалибровки"))

    # Остальные методы без изменений (filter_songs, filter_diffs, browse_osu_path, 
    # load_songs, on_song_selected, start_playback, stop_playback) 
    # ...

    def start_playback(self):
        """Начало воспроизведения с загрузкой калибровки"""
        # Загрузка сохраненной калибровки для карты
        if self.song_combobox.get() and self.diff_combobox.get():
            map_id = f"{self.song_combobox.get()}_{self.diff_combobox.get()}"
            if map_id in self.player.calibration_history:
                self.player.calibration = self.player.calibration_history[map_id]
                self.calibration_scale.set(self.player.calibration)
                self.calibration_value.set(f"{self.player.calibration:.0f}")
        
        # Остальной код без изменений
        # ...

if __name__ == "__main__":
    root = tk.Tk()
    app = OsuAutoPlayerGUI(root)
    root.mainloop()