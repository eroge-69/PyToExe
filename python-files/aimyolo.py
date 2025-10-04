import ctypes
import time
import sys
import numpy as np
import cv2
from mss import mss
import threading
import tkinter as tk
from tkinter import ttk
import json
import os
from pynput import keyboard
from uuid import uuid4
import torch

try:
    import pymeow as pm
    PYMEOW_AVAILABLE = True
    print("✅ PyMeow загружен успешно")
except ImportError:
    PYMEOW_AVAILABLE = False
    print("⚠️ PyMeow не найден. Будет использован встроенный оверлей.")
    print("💡 Для лучшей производительности установите: pip install pymeow")

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
    print("✅ YOLOv8 загружен успешно")
except ImportError:
    YOLO_AVAILABLE = False
    print("❌ YOLOv8 не найден. Установите: pip install ultralytics")
    sys.exit()

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    print("Перезапуск с правами администратора...")
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

user32 = ctypes.windll.user32

CONFIG_FILE = "aim_config.json"

DEFAULT_CONFIG = {
    "fov_width": 300,
    "fov_height": 200,
    "smooth_factor": 0.7,
    "pid_kp": 0.5,
    "pid_ki": 0.005,
    "pid_kd": 0.4,
    "stickiness": 2.0,
    "activation_key": "mouse_right",
    "dead_zone": 2,
    "show_fps": True,
    "show_debug": True,
    "target_offset_y": 0,
    "yolo_model": "yolov8n.pt",
    "yolo_confidence": 0.9,
    "yolo_iou": 0.7,
    "yolo_target_class": 0,
    "yolo_target_part": "head",
    "yolo_max_detections": 1,
    "yolo_min_box_size": 600,
    "yolo_max_box_size": 18000,
    "ignore_top_ratio": 0.2,
    "mouse_speed_factor": 1.0,
    "smoothness_precision": 0.5  # Новый параметр для баланса плавности и точности
}

class Config:
    def __init__(self):
        self.load()
    
    def load(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for key, default_value in DEFAULT_CONFIG.items():
                        setattr(self, key, data.get(key, default_value))
            except:
                self.load_defaults()
        else:
            self.load_defaults()
    
    def load_defaults(self):
        for key, value in DEFAULT_CONFIG.items():
            setattr(self, key, value)
    
    def save(self):
        data = {key: getattr(self, key) for key in DEFAULT_CONFIG}
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

class ConfigWindow:
    def __init__(self, config, on_save_callback):
        self.config = config
        self.on_save_callback = on_save_callback
        
        self.root = tk.Tk()
        self.root.title("Aim Assistant Pro - YOLO Settings")
        self.root.geometry("650x1000")
        self.root.resizable(True, True)
        
        canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, padding="10")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        main_frame = scrollable_frame
        
        start_frame_top = ttk.Frame(main_frame)
        start_frame_top.pack(fill='x', pady=(0, 20))
        
        start_btn_top = tk.Button(start_frame_top, 
                                 text="▶️ СОХРАНИТЬ И ЗАПУСТИТЬ ▶️",
                                 command=self.save_and_start,
                                 bg='#00ff00',
                                 fg='black',
                                 font=('Arial', 14, 'bold'),
                                 height=2,
                                 cursor='hand2')
        start_btn_top.pack(fill='x', padx=20)
        
        yolo_section = ttk.LabelFrame(main_frame, text="🤖 YOLO Detection Settings", padding=10)
        yolo_section.pack(fill='x', pady=(0, 15))
        
        if not YOLO_AVAILABLE:
            ttk.Label(yolo_section, 
                     text="⚠️ YOLO не установлен. Установите: pip install ultralytics",
                     foreground='red').pack(anchor='w')
            return
        
        ttk.Label(yolo_section, text="Модель YOLO:", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(5, 0))
        self.yolo_model_var = tk.StringVar(value=config.yolo_model)
        model_frame = ttk.Frame(yolo_section)
        model_frame.pack(fill='x', pady=5)
        models = [
            ("Nano (быстро, менее точно)", "yolov8n.pt"),
            ("Small (баланс)", "yolov8s.pt"),
            ("Medium (медленнее, точнее)", "yolov8m.pt"),
            ("Large (медленно, очень точно)", "yolov8l.pt")
        ]
        for text, value in models:
            ttk.Radiobutton(model_frame, text=text, variable=self.yolo_model_var, value=value).pack(anchor='w')
        
        ttk.Label(yolo_section, text="Уверенность (Confidence):", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(10, 0))
        self.yolo_conf_var = tk.DoubleVar(value=config.yolo_confidence)
        conf_frame = ttk.Frame(yolo_section)
        conf_frame.pack(fill='x', pady=5)
        ttk.Scale(conf_frame, from_=0.1, to=0.9, variable=self.yolo_conf_var, orient='horizontal').pack(side='left', fill='x', expand=True)
        self.yolo_conf_entry = ttk.Entry(conf_frame, textvariable=self.yolo_conf_var, width=5)
        self.yolo_conf_entry.pack(side='right', padx=(5, 0))
        
        ttk.Label(yolo_section, text="Порог IOU (NMS):", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(10, 0))
        self.yolo_iou_var = tk.DoubleVar(value=config.yolo_iou)
        iou_frame = ttk.Frame(yolo_section)
        iou_frame.pack(fill='x', pady=5)
        ttk.Scale(iou_frame, from_=0.1, to=0.9, variable=self.yolo_iou_var, orient='horizontal').pack(side='left', fill='x', expand=True)
        self.yolo_iou_entry = ttk.Entry(iou_frame, textvariable=self.yolo_iou_var, width=5)
        self.yolo_iou_entry.pack(side='right', padx=(5, 0))
        
        ttk.Label(yolo_section, text="Макс. объектов:", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(10, 0))
        self.yolo_max_det_var = tk.IntVar(value=config.yolo_max_detections)
        max_det_frame = ttk.Frame(yolo_section)
        max_det_frame.pack(fill='x', pady=5)
        ttk.Scale(max_det_frame, from_=1, to=10, variable=self.yolo_max_det_var, orient='horizontal').pack(side='left', fill='x', expand=True)
        self.yolo_max_det_entry = ttk.Entry(max_det_frame, textvariable=self.yolo_max_det_var, width=5)
        self.yolo_max_det_entry.pack(side='right', padx=(5, 0))
        
        ttk.Label(yolo_section, text="Мин. размер бокса (пиксели²):", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(10, 0))
        self.yolo_min_box_var = tk.IntVar(value=config.yolo_min_box_size)
        min_box_frame = ttk.Frame(yolo_section)
        min_box_frame.pack(fill='x', pady=5)
        ttk.Scale(min_box_frame, from_=500, to=5000, variable=self.yolo_min_box_var, orient='horizontal').pack(side='left', fill='x', expand=True)
        self.yolo_min_box_entry = ttk.Entry(min_box_frame, textvariable=self.yolo_min_box_var, width=5)
        self.yolo_min_box_entry.pack(side='right', padx=(5, 0))
        
        ttk.Label(yolo_section, text="Макс. размер бокса (пиксели²):", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(10, 0))
        self.yolo_max_box_var = tk.IntVar(value=config.yolo_max_box_size)
        max_box_frame = ttk.Frame(yolo_section)
        max_box_frame.pack(fill='x', pady=5)
        ttk.Scale(max_box_frame, from_=10000, to=100000, variable=self.yolo_max_box_var, orient='horizontal').pack(side='left', fill='x', expand=True)
        self.yolo_max_box_entry = ttk.Entry(max_box_frame, textvariable=self.yolo_max_box_var, width=6)
        self.yolo_max_box_entry.pack(side='right', padx=(5, 0))
        
        ttk.Label(yolo_section, text="Игнорировать верхнюю часть (%):", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(10, 0))
        self.ignore_top_var = tk.DoubleVar(value=config.ignore_top_ratio)
        ignore_top_frame = ttk.Frame(yolo_section)
        ignore_top_frame.pack(fill='x', pady=5)
        ttk.Scale(ignore_top_frame, from_=0.0, to=0.5, variable=self.ignore_top_var, orient='horizontal').pack(side='left', fill='x', expand=True)
        self.ignore_top_entry = ttk.Entry(ignore_top_frame, textvariable=self.ignore_top_var, width=5)
        self.ignore_top_entry.pack(side='right', padx=(5, 0))
        
        ttk.Label(yolo_section, text="Цель обнаружения:", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(10, 0))
        self.yolo_class_var = tk.IntVar(value=config.yolo_target_class)
        class_frame = ttk.Frame(yolo_section)
        class_frame.pack(fill='x', pady=5)
        classes = [
            ("Человек (Person)", 0),
            ("Автомобиль (Car)", 2),
            ("Мотоцикл (Motorcycle)", 3),
            ("Птица (Bird)", 14),
            ("Кошка (Cat)", 15),
            ("Собака (Dog)", 16)
        ]
        for text, value in classes:
            ttk.Radiobutton(class_frame, text=text, variable=self.yolo_class_var, value=value).pack(anchor='w')
        
        ttk.Label(yolo_section, text="Точка прицеливания:", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(10, 0))
        self.yolo_part_var = tk.StringVar(value=config.yolo_target_part)
        part_frame = ttk.Frame(yolo_section)
        part_frame.pack(fill='x', pady=5)
        parts = [
            ("Голова (Head)", "head"),
            ("Грудь (Chest)", "chest"),
            ("Центр (Center)", "center")
        ]
        for text, value in parts:
            ttk.Radiobutton(part_frame, text=text, variable=self.yolo_part_var, value=value).pack(anchor='w')
        
        ttk.Label(main_frame, text="Ширина FOV (пикселей):", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(15, 0))
        self.fov_width_var = tk.IntVar(value=config.fov_width)
        fov_width_frame = ttk.Frame(main_frame)
        fov_width_frame.pack(fill='x', pady=5)
        ttk.Scale(fov_width_frame, from_=100, to=800, variable=self.fov_width_var, orient='horizontal').pack(side='left', fill='x', expand=True)
        self.fov_width_entry = ttk.Entry(fov_width_frame, textvariable=self.fov_width_var, width=5)
        self.fov_width_entry.pack(side='right', padx=(5, 0))
        
        ttk.Label(main_frame, text="Высота FOV (пикселей):", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(10, 0))
        self.fov_height_var = tk.IntVar(value=config.fov_height)
        fov_height_frame = ttk.Frame(main_frame)
        fov_height_frame.pack(fill='x', pady=5)
        ttk.Scale(fov_height_frame, from_=100, to=600, variable=self.fov_height_var, orient='horizontal').pack(side='left', fill='x', expand=True)
        self.fov_height_entry = ttk.Entry(fov_height_frame, textvariable=self.fov_height_var, width=5)
        self.fov_height_entry.pack(side='right', padx=(5, 0))
        
        ttk.Label(main_frame, text="Плавность (0.1 - плавно, 1.0 - резко):", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(10, 0))
        self.smooth_var = tk.DoubleVar(value=config.smooth_factor)
        smooth_frame = ttk.Frame(main_frame)
        smooth_frame.pack(fill='x', pady=5)
        ttk.Scale(smooth_frame, from_=0.1, to=1.0, variable=self.smooth_var, orient='horizontal').pack(side='left', fill='x', expand=True)
        self.smooth_entry = ttk.Entry(smooth_frame, textvariable=self.smooth_var, width=5)
        self.smooth_entry.pack(side='right', padx=(5, 0))
        
        ttk.Label(main_frame, text="Точность/Плавность (0.1 - точнее, 1.0 - плавнее):", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(10, 0))
        self.smoothness_precision_var = tk.DoubleVar(value=config.smoothness_precision)
        smoothness_precision_frame = ttk.Frame(main_frame)
        smoothness_precision_frame.pack(fill='x', pady=5)
        ttk.Scale(smoothness_precision_frame, from_=0.1, to=1.0, variable=self.smoothness_precision_var, orient='horizontal').pack(side='left', fill='x', expand=True)
        self.smoothness_precision_entry = ttk.Entry(smoothness_precision_frame, textvariable=self.smoothness_precision_var, width=5)
        self.smoothness_precision_entry.pack(side='right', padx=(5, 0))
        
        ttk.Label(main_frame, text="Скорость аима (0.5 - медленно, 5.0 - быстро):", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(10, 0))
        self.mouse_speed_var = tk.DoubleVar(value=config.mouse_speed_factor)
        speed_frame = ttk.Frame(main_frame)
        speed_frame.pack(fill='x', pady=5)
        ttk.Scale(speed_frame, from_=0.5, to=5.0, variable=self.mouse_speed_var, orient='horizontal').pack(side='left', fill='x', expand=True)
        self.mouse_speed_entry = ttk.Entry(speed_frame, textvariable=self.mouse_speed_var, width=5)
        self.mouse_speed_entry.pack(side='right', padx=(5, 0))
        
        pid_section = ttk.LabelFrame(main_frame, text="🎚️ PID настройки", padding=10)
        pid_section.pack(fill='x', pady=(10, 15))
        
        ttk.Label(pid_section, text="PID Kp (чувствительность):", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(10, 0))
        self.pid_kp_var = tk.DoubleVar(value=config.pid_kp)
        kp_frame = ttk.Frame(pid_section)
        kp_frame.pack(fill='x', pady=5)
        ttk.Scale(kp_frame, from_=0.1, to=2.0, variable=self.pid_kp_var, orient='horizontal').pack(side='left', fill='x', expand=True)
        self.pid_kp_entry = ttk.Entry(kp_frame, textvariable=self.pid_kp_var, width=5)
        self.pid_kp_entry.pack(side='right', padx=(5, 0))
        
        ttk.Label(pid_section, text="PID Ki (устойчивость):", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(10, 0))
        self.pid_ki_var = tk.DoubleVar(value=config.pid_ki)
        ki_frame = ttk.Frame(pid_section)
        ki_frame.pack(fill='x', pady=5)
        ttk.Scale(ki_frame, from_=0.0, to=0.2, variable=self.pid_ki_var, orient='horizontal').pack(side='left', fill='x', expand=True)
        self.pid_ki_entry = ttk.Entry(ki_frame, textvariable=self.pid_ki_var, width=5)
        self.pid_ki_entry.pack(side='right', padx=(5, 0))
        
        ttk.Label(pid_section, text="PID Kd (демпфирование):", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(10, 0))
        self.pid_kd_var = tk.DoubleVar(value=config.pid_kd)
        kd_frame = ttk.Frame(pid_section)
        kd_frame.pack(fill='x', pady=5)
        ttk.Scale(kd_frame, from_=0.0, to=0.5, variable=self.pid_kd_var, orient='horizontal').pack(side='left', fill='x', expand=True)
        self.pid_kd_entry = ttk.Entry(kd_frame, textvariable=self.pid_kd_var, width=5)
        self.pid_kd_entry.pack(side='right', padx=(5, 0))
        
        ttk.Label(pid_section, text="Липкость (сек):", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(10, 0))
        self.stickiness_var = tk.DoubleVar(value=config.stickiness)
        stickiness_frame = ttk.Frame(pid_section)
        stickiness_frame.pack(fill='x', pady=5)
        ttk.Scale(stickiness_frame, from_=0.1, to=2.0, variable=self.stickiness_var, orient='horizontal').pack(side='left', fill='x', expand=True)
        self.stickiness_entry = ttk.Entry(stickiness_frame, textvariable=self.stickiness_var, width=5)
        self.stickiness_entry.pack(side='right', padx=(5, 0))
        
        ttk.Label(main_frame, text="Смещение цели по Y:", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(10, 0))
        self.offset_var = tk.IntVar(value=config.target_offset_y)
        offset_frame = ttk.Frame(main_frame)
        offset_frame.pack(fill='x', pady=5)
        ttk.Scale(offset_frame, from_=-50, to=50, variable=self.offset_var, orient='horizontal').pack(side='left', fill='x', expand=True)
        self.offset_entry = ttk.Entry(offset_frame, textvariable=self.offset_var, width=5)
        self.offset_entry.pack(side='right', padx=(5, 0))
        
        ttk.Label(main_frame, text="Кнопка активации:", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(10, 0))
        self.key_var = tk.StringVar(value=config.activation_key)
        key_frame = ttk.Frame(main_frame)
        key_frame.pack(fill='x', pady=5)
        keys = [
            ("Правая кнопка мыши", "mouse_right"),
            ("Средняя кнопка мыши", "mouse_middle"),
            ("Shift", "shift"),
            ("Ctrl", "ctrl"),
            ("Alt", "alt")
        ]
        for text, value in keys:
            ttk.Radiobutton(key_frame, text=text, variable=self.key_var, value=value).pack(anchor='w')
        
        ttk.Label(main_frame, text="Мертвая зона (пикселей):", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(10, 0))
        self.dead_zone_var = tk.IntVar(value=config.dead_zone)
        dead_zone_frame = ttk.Frame(main_frame)
        dead_zone_frame.pack(fill='x', pady=5)
        ttk.Scale(dead_zone_frame, from_=0, to=20, variable=self.dead_zone_var, orient='horizontal').pack(side='left', fill='x', expand=True)
        self.dead_zone_entry = ttk.Entry(dead_zone_frame, textvariable=self.dead_zone_var, width=5)
        self.dead_zone_entry.pack(side='right', padx=(5, 0))
        
        ttk.Label(main_frame, text="Визуальные опции:", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(10, 0))
        self.show_fps_var = tk.BooleanVar(value=config.show_fps)
        ttk.Checkbutton(main_frame, text="Показывать FPS", variable=self.show_fps_var).pack(anchor='w', pady=2)
        self.show_debug_var = tk.BooleanVar(value=config.show_debug)
        ttk.Checkbutton(main_frame, text="Показывать отладочную информацию", variable=self.show_debug_var).pack(anchor='w', pady=2)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=20)
        
        start_btn_bottom = tk.Button(button_frame, 
                                    text="▶️ СОХРАНИТЬ И ЗАПУСТИТЬ ▶️",
                                    command=self.save_and_start,
                                    bg='#00ff00',
                                    fg='black',
                                    font=('Arial', 12, 'bold'),
                                    height=2,
                                    cursor='hand2')
        start_btn_bottom.pack(fill='x', pady=(0, 10))
        
        other_buttons = ttk.Frame(button_frame)
        other_buttons.pack(fill='x')
        
        ttk.Button(other_buttons, text="🔄 Сбросить", command=self.reset).pack(side='left', padx=5, expand=True, fill='x')
        ttk.Button(other_buttons, text="❌ Выход", command=self.root.quit).pack(side='right', padx=5, expand=True, fill='x')
        
        self.status_label = ttk.Label(main_frame, text="", foreground='green')
        self.status_label.pack(pady=10)
    
    def save_and_start(self):
        try:
            self.config.fov_width = self.fov_width_var.get()
            self.config.fov_height = self.fov_height_var.get()
            self.config.smooth_factor = self.smooth_var.get()
            self.config.pid_kp = self.pid_kp_var.get()
            self.config.pid_ki = self.pid_ki_var.get()
            self.config.pid_kd = self.pid_kd_var.get()
            self.config.stickiness = self.stickiness_var.get()
            self.config.activation_key = self.key_var.get()
            self.config.dead_zone = self.dead_zone_var.get()
            self.config.show_fps = self.show_fps_var.get()
            self.config.show_debug = self.show_debug_var.get()
            self.config.target_offset_y = self.offset_var.get()
            self.config.yolo_model = self.yolo_model_var.get()
            self.config.yolo_confidence = self.yolo_conf_var.get()
            self.config.yolo_iou = self.yolo_iou_var.get()
            self.config.yolo_max_detections = self.yolo_max_det_var.get()
            self.config.yolo_min_box_size = self.yolo_min_box_var.get()
            self.config.yolo_max_box_size = self.yolo_max_box_var.get()
            self.config.yolo_target_class = self.yolo_class_var.get()
            self.config.yolo_target_part = self.yolo_part_var.get()
            self.config.ignore_top_ratio = self.ignore_top_var.get()
            self.config.mouse_speed_factor = self.mouse_speed_var.get()
            self.config.smoothness_precision = self.smoothness_precision_var.get()
            
            self.config.save()
            self.status_label.config(text="✓ Настройки сохранены!")
            self.root.after(1000, self.root.destroy)
            self.on_save_callback()
        except Exception as e:
            self.status_label.config(text=f"⚠ Ошибка сохранения: {e}", foreground='red')
    
    def reset(self):
        self.config.load_defaults()
        self.fov_width_var.set(self.config.fov_width)
        self.fov_height_var.set(self.config.fov_height)
        self.smooth_var.set(self.config.smooth_factor)
        self.pid_kp_var.set(self.config.pid_kp)
        self.pid_ki_var.set(self.config.pid_ki)
        self.pid_kd_var.set(self.config.pid_kd)
        self.stickiness_var.set(self.config.stickiness)
        self.key_var.set(self.config.activation_key)
        self.dead_zone_var.set(self.config.dead_zone)
        self.show_fps_var.set(self.config.show_fps)
        self.show_debug_var.set(self.config.show_debug)
        self.offset_var.set(self.config.target_offset_y)
        self.yolo_model_var.set(self.config.yolo_model)
        self.yolo_conf_var.set(self.config.yolo_confidence)
        self.yolo_iou_var.set(self.config.yolo_iou)
        self.yolo_max_det_var.set(self.config.yolo_max_detections)
        self.yolo_min_box_var.set(self.config.yolo_min_box_size)
        self.yolo_max_box_var.set(self.config.yolo_max_box_size)
        self.yolo_class_var.set(self.config.yolo_target_class)
        self.yolo_part_var.set(self.config.yolo_target_part)
        self.ignore_top_var.set(self.config.ignore_top_ratio)
        self.mouse_speed_var.set(self.config.mouse_speed_factor)
        self.smoothness_precision_var.set(self.config.smoothness_precision)
        
        self.status_label.config(text="⚠ Настройки сброшены к дефолтным")
    
    def run(self):
        self.root.mainloop()

class TkinterOverlay:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-transparentcolor', 'black')
        self.root.attributes('-alpha', 0.7)
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        self.canvas = tk.Canvas(self.root, width=width, height=height, 
                                bg='black', highlightthickness=0)
        self.canvas.pack()
        
        self.info_label = tk.Label(self.root, text="", fg='white', bg='black',
                                    font=('Arial', 10))
        self.info_label.place(x=10, y=10)
    
    def update_display(self, is_active, target, fps, targets_found):
        self.canvas.delete('all')
        
        center_x = self.width // 2
        center_y = self.height // 2
        self.canvas.create_rectangle(2, 2, self.width-2, self.height-2, 
                                    outline='lime', width=2)
        
        self.canvas.create_line(center_x-10, center_y, center_x+10, center_y, 
                                fill='lime', width=2)
        self.canvas.create_line(center_x, center_y-10, center_x, center_y+10, 
                                fill='lime', width=2)
        
        if target:
            dx, dy = target
            x = center_x + dx
            y = center_y + dy
            if abs(dx) < self.width * 0.8 // 2 and abs(dy) < self.height * 0.8 // 2:
                self.canvas.create_oval(x-8, y-8, x+8, y+8, 
                                        fill='', outline='red', width=2)
                if is_active:
                    self.canvas.create_line(center_x, center_y, x, y,
                                           fill='yellow', width=1)
        
        info_text = f"FPS: {fps} | Целей: {targets_found}"
        self.info_label.config(text=info_text)
        
        self.root.update()
    
    def close(self):
        try:
            self.root.destroy()
        except:
            pass

class AimAssistant:
    def __init__(self, config):
        self.config = config
        self.is_active = False
        self.running = True
        self.fps = 0
        self.frame_count = 0
        self.fps_time = time.time()
        self.last_target = None
        self.initial_target = None
        self.targets_found = 0
        self.prev_dx = 0
        self.prev_dy = 0
        self.integral_x = 0
        self.integral_y = 0
        self.last_target_time = 0
        self.smoothed_dx = 0
        self.smoothed_dy = 0
        
        self.device = '0' if torch.cuda.is_available() else 'cpu'
        self.half = torch.cuda.is_available()
        print(f"🖥️ Используемое устройство: {self.device}")
        if self.half:
            print("🔥 Включен half-precision (FP16) для ускорения")
        
        try:
            print(f"⏳ Загрузка YOLO модели: {self.config.yolo_model}...")
            self.yolo_model = YOLO(self.config.yolo_model)
            self.yolo_model.fuse()
            print(f"✅ YOLO модель загружена успешно!")
            print(f"🎯 Цель: класс {self.config.yolo_target_class}, точка прицеливания: {self.config.yolo_target_part}")
        except Exception as e:
            print(f"❌ Ошибка загрузки YOLO: {e}")
            sys.exit()
        
        dummy_img = np.zeros((self.config.fov_height, self.config.fov_width, 3), dtype=np.uint8)
        self.yolo_model.predict(dummy_img, verbose=False, device=self.device, half=self.half, imgsz=(self.config.fov_width, self.config.fov_height))
        print("✅ Модель разогрета")
        
        self.setup_activation_listener()
    
    def setup_activation_listener(self):
        def on_press(key):
            try:
                if self.config.activation_key == "shift" and key == keyboard.Key.shift:
                    self.is_active = True
                elif self.config.activation_key == "ctrl" and key == keyboard.Key.ctrl:
                    self.is_active = True
                elif self.config.activation_key == "alt" and key == keyboard.Key.alt:
                    self.is_active = True
            except:
                pass
        
        def on_release(key):
            try:
                if self.config.activation_key == "shift" and key == keyboard.Key.shift:
                    self.is_active = False
                    self.initial_target = None
                elif self.config.activation_key == "ctrl" and key == keyboard.Key.ctrl:
                    self.is_active = False
                    self.initial_target = None
                elif self.config.activation_key == "alt" and key == keyboard.Key.alt:
                    self.is_active = False
                    self.initial_target = None
            except:
                pass
        
        if self.config.activation_key in ["shift", "ctrl", "alt"]:
            self.listener = keyboard.Listener(on_press=on_press, on_release=on_release)
            self.listener.start()
    
    def is_mouse_button_pressed(self):
        if self.config.activation_key == "mouse_right":
            pressed = user32.GetAsyncKeyState(0x02) & 0x8000
            if not pressed:
                self.initial_target = None
            return pressed
        elif self.config.activation_key == "mouse_middle":
            pressed = user32.GetAsyncKeyState(0x04) & 0x8000
            if not pressed:
                self.initial_target = None
            return pressed
        return False
    
    def get_screen_center(self):
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)
        return screen_width // 2, screen_height // 2
    
    def capture_fov(self, sct, center_x, center_y):
        monitor = {
            "top": center_y - self.config.fov_height // 2,
            "left": center_x - self.config.fov_width // 2,
            "width": self.config.fov_width,
            "height": self.config.fov_height
        }
        img = np.array(sct.grab(monitor))
        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    
    def find_yolo_target(self, img):
        try:
            results = self.yolo_model.predict(
                source=img,
                conf=self.config.yolo_confidence,
                iou=self.config.yolo_iou,
                max_det=self.config.yolo_max_detections,
                classes=[self.config.yolo_target_class],
                verbose=False,
                device=self.device,
                half=self.half,
                imgsz=(self.config.fov_width, self.config.fov_height)
            )[0]
            
            current_time = time.time()
            center_x = self.config.fov_width // 2
            center_y = self.config.fov_height // 2
            ignore_top_y = self.config.fov_height * self.config.ignore_top_ratio
            fov_width_limit = self.config.fov_width * 0.8 // 2
            fov_height_limit = self.config.fov_height * 0.8 // 2
            
            if self.initial_target:
                tx, ty = self.initial_target
                dx = tx - center_x
                dy = ty - center_y
                if abs(dx) < fov_width_limit and abs(dy) < fov_height_limit and (current_time - self.last_target_time) < self.config.stickiness:
                    return int(tx), int(ty), 0
            
            closest_box = None
            min_distance = float('inf')
            
            for box in results.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                area = (x2 - x1) * (y2 - y1)
                
                if y1 < ignore_top_y:
                    continue
                
                if area < self.config.yolo_min_box_size or area > self.config.yolo_max_box_size:
                    continue
                
                if self.config.yolo_target_part == "head":
                    target_x = (x1 + x2) / 2
                    target_y = y1 + (y2 - y1) * 0.2 + self.config.target_offset_y
                elif self.config.yolo_target_part == "chest":
                    target_x = (x1 + x2) / 2
                    target_y = y1 + (y2 - y1) * 0.4 + self.config.target_offset_y
                else:
                    target_x = (x1 + x2) / 2
                    target_y = (y1 + y2) / 2 + self.config.target_offset_y
                
                dx = target_x - center_x
                dy = target_y - center_y
                if abs(dx) < fov_width_limit and abs(dy) < fov_height_limit:
                    distance = np.sqrt(dx**2 + dy**2)
                    if distance < min_distance:
                        min_distance = distance
                        closest_box = (target_x, target_y, area)
            
            if closest_box:
                self.last_target_time = current_time
                tx, ty, area = closest_box
                if not self.initial_target:
                    self.initial_target = (tx, ty)
                return int(tx), int(ty), area
            
            if self.initial_target and (current_time - self.last_target_time) < self.config.stickiness:
                tx, ty = self.initial_target
                dx = tx - center_x
                dy = ty - center_y
                if abs(dx) < fov_width_limit and abs(dy) < fov_height_limit:
                    return int(tx), int(ty), 0
                else:
                    self.initial_target = None
            
        except Exception as e:
            print(f"⚠️ Ошибка YOLO детекции: {e}")
        
        self.initial_target = None
        return None, None, 0
    
    def smooth_move(self, dx, dy):
        kp = self.config.pid_kp
        ki = self.config.pid_ki
        kd = self.config.pid_kd
        speed_factor = self.config.mouse_speed_factor
        smoothness_precision = self.config.smoothness_precision
        
        # Динамическое масштабирование kp в зависимости от расстояния
        distance = np.sqrt(dx**2 + dy**2)
        kp_scale = 1.0 + (1.0 - smoothness_precision) * (distance / max(self.config.fov_width, self.config.fov_height))
        kp_dynamic = kp * kp_scale
        
        # Уменьшаем ki для малых дистанций, чтобы избежать перерегулирования
        ki_dynamic = ki * max(0.1, smoothness_precision if distance < 50 else 1.0)
        
        self.integral_x += dx * 0.01
        self.integral_y += dy * 0.01
        
        self.integral_x = max(min(self.integral_x, 10), -10)
        self.integral_y = max(min(self.integral_y, 10), -10)
        
        deriv_x = dx - self.prev_dx
        deriv_y = dy - self.prev_dy
        
        move_x = (kp_dynamic * dx + ki_dynamic * self.integral_x + kd * deriv_x) * speed_factor
        move_y = (kp_dynamic * dy + ki_dynamic * self.integral_y + kd * deriv_y) * speed_factor
        
        # Экспоненциальное сглаживание для плавности
        smooth_alpha = self.config.smooth_factor * smoothness_precision
        self.smoothed_dx = smooth_alpha * move_x + (1 - smooth_alpha) * self.smoothed_dx
        self.smoothed_dy = smooth_alpha * move_y + (1 - smooth_alpha) * self.smoothed_dy
        
        max_move = 15  # Увеличено для большей скорости
        move_x = max(min(self.smoothed_dx, max_move), -max_move)
        move_y = max(min(self.smoothed_dy, max_move), -max_move)
        
        if abs(move_x) < self.config.dead_zone and abs(move_y) < self.config.dead_zone:
            return
        
        self.prev_dx = dx
        self.prev_dy = dy
        
        steps = max(1, int(max(abs(move_x), abs(move_y)) / 1.5))
        for i in range(steps):
            step_x = int(move_x / steps)
            step_y = int(move_y / steps)
            if step_x != 0 or step_y != 0:
                user32.mouse_event(0x0001, step_x, step_y, 0, 0)
                time.sleep(0.001 / steps)
    
    def update_fps(self):
        self.frame_count += 1
        current_time = time.time()
        if current_time - self.fps_time >= 1.0:
            self.fps = self.frame_count
            self.frame_count = 0
            self.fps_time = current_time
    
    def draw_overlay(self):
        if not PYMEOW_AVAILABLE:
            return
        
        center_x, center_y = self.get_screen_center()
        half_width = self.config.fov_width // 2
        half_height = self.config.fov_height // 2
        
        try:
            pm.draw_rectangle_lines(center_x - half_width, center_y - half_height, 
                                   self.config.fov_width, self.config.fov_height, 
                                   pm.get_color("lime"), 2)
            
            crosshair_size = 10
            pm.draw_line(
                center_x - crosshair_size, center_y,
                center_x + crosshair_size, center_y,
                pm.get_color("lime"), 2
            )
            pm.draw_line(
                center_x, center_y - crosshair_size,
                center_x, center_y + crosshair_size,
                pm.get_color("lime"), 2
            )
            
            if self.initial_target:
                target_x, target_y = self.initial_target
                screen_x = center_x + (target_x - self.config.fov_width // 2)
                screen_y = center_y + (target_y - self.config.fov_height // 2)
                
                if abs(target_x - self.config.fov_width // 2) < half_width * 0.8 and abs(target_y - self.config.fov_height // 2) < half_height * 0.8:
                    pm.draw_circle(screen_x, screen_y, 8, pm.get_color("red"), 2)
                    
                    if self.is_active:
                        pm.draw_line(
                            center_x, center_y,
                            screen_x, screen_y,
                            pm.get_color("yellow"), 1
                        )
            
            if self.config.show_fps:
                pm.draw_text(f"FPS: {self.fps} | Целей: {self.targets_found}", 10, 10, 18, pm.get_color("white"))
            
            if self.config.show_debug:
                debug_y = 40
                pm.draw_text(f"FOV: {self.config.fov_width}x{self.config.fov_height}px", 10, debug_y, 14, pm.get_color("white"))
                pm.draw_text(f"Smooth: {self.config.smooth_factor:.2f}", 10, debug_y + 20, 14, pm.get_color("white"))
                pm.draw_text(f"P: {self.config.pid_kp:.2f} I: {self.config.pid_ki:.2f} D: {self.config.pid_kd:.2f}", 10, debug_y + 40, 14, pm.get_color("white"))
                pm.draw_text(f"Stickiness: {self.config.stickiness:.2f}s", 10, debug_y + 60, 14, pm.get_color("white"))
                pm.draw_text(f"Speed: {self.config.mouse_speed_factor:.2f}", 10, debug_y + 80, 14, pm.get_color("white"))
                pm.draw_text(f"Smoothness/Precision: {self.config.smoothness_precision:.2f}", 10, debug_y + 100, 14, pm.get_color("white"))
                pm.draw_text(f"Model: {self.config.yolo_model}", 10, debug_y + 120, 12, pm.get_color("white"))
                pm.draw_text(f"Conf: {self.config.yolo_confidence:.2f}", 10, debug_y + 140, 12, pm.get_color("white"))
                pm.draw_text(f"IOU: {self.config.yolo_iou:.2f}", 10, debug_y + 160, 12, pm.get_color("white"))
                pm.draw_text(f"Max Det: {self.config.yolo_max_detections}", 10, debug_y + 180, 12, pm.get_color("white"))
                pm.draw_text(f"Target: {self.config.yolo_target_part}", 10, debug_y + 200, 12, pm.get_color("white"))
        except Exception as e:
            print(f"⚠️ Ошибка отрисовки: {e}")
    
    def run(self):
        print(f"\n{'='*60}")
        print("🎯 AIM ASSISTANT PRO - YOLO DETECTION")
        print(f"{'='*60}")
        print(f"🤖 Режим детекции: YOLO")
        print(f"📐 FOV: {self.config.fov_width}x{self.config.fov_height}")
        print(f"🎚️ Плавность: {self.config.smooth_factor}")
        print(f"🎛️ PID: P={self.config.pid_kp:.2f}, I={self.config.pid_ki:.2f}, D={self.config.pid_kd:.2f}")
        print(f"🧲 Липкость: {self.config.stickiness:.2f} сек")
        print(f"⌨️ Кнопка активации: {self.config.activation_key}")
        print(f"🎯 Мертвая зона: {self.config.dead_zone} пикселей")
        print(f"⚡ Скорость аима: {self.config.mouse_speed_factor:.2f}")
        print(f"🎯 Точность/Плавность: {self.config.smoothness_precision:.2f}")
        print(f"🤖 YOLO модель: {self.config.yolo_model}")
        print(f"📊 Уверенность: {self.config.yolo_confidence}")
        print(f"📏 IOU: {self.config.yolo_iou}")
        print(f"🔢 Макс. объектов: {self.config.yolo_max_detections}")
        print(f"📏 Мин. размер бокса: {self.config.yolo_min_box_size}")
        print(f"📏 Макс. размер бокса: {self.config.yolo_max_box_size}")
        print(f"🎯 Класс цели: {self.config.yolo_target_class}")
        print(f"🎯 Точка прицеливания: {self.config.yolo_target_part}")
        print(f"🌌 Игнорировать верх (%): {self.config.ignore_top_ratio*100:.0f}%")
        print(f"\n💡 Нажмите Ctrl+C для остановки")
        print(f"{'='*60}\n")
        
        tkinter_overlay = None
        use_pymeow = False
        
        if PYMEOW_AVAILABLE:
            try:
                print("⏳ Инициализация PyMeow оверлея...")
                pm.overlay_init(target=None, fps=144, trackTarget=False)
                use_pymeow = True
                print("✅ PyMeow оверлей успешно инициализирован!")
            except Exception as e:
                print(f"⚠️ Ошибка PyMeow: {e}")
                print("📦 Переключаюсь на встроенный оверлей...")
                use_pymeow = False
        
        if not use_pymeow:
            print("⏳ Запуск встроенного оверлея...")
            tkinter_overlay = TkinterOverlay(self.config.fov_width, self.config.fov_height)
            print("✅ Встроенный оверлей готов!")
        
        time.sleep(0.5)
        center_x, center_y = self.get_screen_center()
        
        print("🚀 Запуск основного цикла...\n")
        
        try:
            with mss() as sct:
                while self.running:
                    try:
                        if use_pymeow and not pm.overlay_loop():
                            print("⚠️ PyMeow оверлей был закрыт")
                            break
                        
                        self.update_fps()
                        
                        if self.config.activation_key in ["mouse_right", "mouse_middle"]:
                            self.is_active = self.is_mouse_button_pressed()
                        
                        if self.is_active:
                            img = self.capture_fov(sct, center_x, center_y)
                            target_x, target_y, area = self.find_yolo_target(img)
                            
                            if target_x is not None and target_y is not None:
                                dx = target_x - self.config.fov_width // 2
                                dy = target_y - self.config.fov_height // 2
                                
                                self.last_target = (dx, dy)
                                if area > 0:
                                    self.targets_found += 1
                                
                                if abs(dx) > self.config.dead_zone or abs(dy) > self.config.dead_zone:
                                    self.smooth_move(dx, dy)
                        
                        else:
                            self.last_target = None
                            self.prev_dx = 0
                            self.prev_dy = 0
                            self.integral_x = 0
                            self.integral_y = 0
                            self.smoothed_dx = 0
                            self.smoothed_dy = 0
                        
                        if use_pymeow:
                            self.draw_overlay()
                        else:
                            tkinter_overlay.update_display(
                                self.is_active,
                                self.initial_target or self.last_target,
                                self.fps,
                                self.targets_found
                            )
                        
                        time.sleep(0.001 if use_pymeow else 0.002)
                    
                    except Exception as e:
                        print(f"⚠️ Ошибка в основном цикле: {e}")
                        time.sleep(0.05)
                        continue
        
        except KeyboardInterrupt:
            print("\n🛑 Остановка по запросу пользователя...")
        except Exception as e:
            print(f"\n❌ Критическая ошибка: {e}")
            import traceback
            traceback.print_exc()
        finally:
            print("🧹 Закрытие оверлея...")
            if use_pymeow:
                try:
                    pm.overlay_close()
                except:
                    pass
            elif tkinter_overlay:
                tkinter_overlay.close()
            print("✅ Программа завершена")
            self.running = False

def main():
    print("🚀 Загрузка конфигурации...")
    config = Config()
    
    start_assistant = [False]
    
    def on_save():
        start_assistant[0] = True
    
    config_window = ConfigWindow(config, on_save)
    config_window.run()
    
    if start_assistant[0]:
        assistant = AimAssistant(config)
        assistant.run()

if __name__ == "__main__":
    main()