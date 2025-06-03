import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Circle
import random
import time
from threading import Thread
from PIL import Image, ImageTk
import os

class RadarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Фоновый радиолокатор v1.0")
        self.setup_ui()
        
    def setup_ui(self):
        # Конфигурация РЛС
        self.radar_pos = (45.0, 41.1)
        self.radar_range = 0.3
        self.detection_prob = 0.8
        self.simulation_active = False
        self.uavs = []
        
        # Главный фрейм
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Графическая область
        self.fig, self.ax = plt.subplots(figsize=(9, 7))
        self.canvas = FigureCanvasTkAgg(self.fig, master=main_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Панель управления
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        self.btn_start = ttk.Button(
            control_frame, 
            text="Старт", 
            command=self.start_simulation,
            width=10
        )
        self.btn_start.pack(side=tk.LEFT, padx=5)
        
        self.btn_stop = ttk.Button(
            control_frame,
            text="Стоп",
            command=self.stop_simulation,
            state=tk.DISABLED,
            width=10
        )
        self.btn_stop.pack(side=tk.LEFT, padx=5)
        
        self.lbl_status = ttk.Label(
            control_frame,
            text="Готов к работе | БПЛА: 0",
            font=('Arial', 10)
        )
        self.lbl_status.pack(side=tk.LEFT, padx=20)
        
        # Инициализация графики
        self.init_plot()
        
    def init_plot(self):
        """Инициализация графического интерфейса"""
        self.ax.clear()
        
        # Серый фон с сеткой
        self.ax.imshow(np.zeros((600, 800, 3)) + 0.85, 
                      extent=[40.5, 41.5, 44.5, 45.5])
        
        # Зона обзора РЛС
        radar_zone = Circle(
            (self.radar_pos[1], self.radar_pos[0]),
            self.radar_range,
            fill=False,
            color='red',
            linewidth=2,
            alpha=0.5,
            label='Зона обнаружения'
        )
        self.ax.add_patch(radar_zone)
        
        # Радиолокатор
        self.ax.plot(
            self.radar_pos[1], self.radar_pos[0],
            'ro', markersize=12, label='РЛС Армавир'
        )
        
        # Настройки отображения
        self.ax.set_title("Фоновый радиолокатор: обнаружение БПЛА", pad=20)
        self.ax.legend(loc='upper right')
        self.ax.set_xlim(40.5, 41.5)
        self.ax.set_ylim(44.5, 45.5)
        self.ax.grid(True, linestyle='--', alpha=0.5)
        
        self.canvas.draw()
    
    def start_simulation(self):
        """Запуск симуляции"""
        self.simulation_active = True
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.lbl_status.config(text="Идет обнаружение... | БПЛА: 0")
        
        # Поток для генерации БПЛА
        Thread(target=self.uav_generator, daemon=True).start()
        
        # Запуск обновления экрана
        self.update_display()
    
    def stop_simulation(self):
        """Остановка симуляции"""
        self.simulation_active = False
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.lbl_status.config(text=f"Симуляция остановлена | БПЛА: {len(self.uavs)}")
    
    def uav_generator(self):
        """Генератор БПЛА"""
        while self.simulation_active:
            # Случайный интервал 5-10 секунд
            time.sleep(random.uniform(5, 10))
            
            if not self.simulation_active:
                break
                
            # Параметры нового БПЛА
            angle = random.uniform(0, 360)
            distance = self.radar_range * 1.5
            
            uav = {
                'id': len(self.uavs) + 1,
                'pos': [
                    self.radar_pos[0] + distance * np.cos(np.radians(angle)),
                    self.radar_pos[1] + distance * np.sin(np.radians(angle))
                ],
                'speed': random.uniform(0.002, 0.006),
                'angle': (angle + 180) % 360,
                'detected': False,
                'path': []
            }
            
            self.uavs.append(uav)
    
    def update_display(self):
        """Обновление графики"""
        if not self.simulation_active and not self.uavs:
            return
            
        self.ax.clear()
        self.init_plot()  # Перерисовываем фон
        
        active_uavs = 0
        
        for uav in self.uavs[:]:  # Работаем с копией списка
            # Движение БПЛА
            uav['pos'][0] += uav['speed'] * np.cos(np.radians(uav['angle']))
            uav['pos'][1] += uav['speed'] * np.sin(np.radians(uav['angle']))
            uav['path'].append((uav['pos'][1], uav['pos'][0]))
            
            # Проверка обнаружения
            distance = np.hypot(
                uav['pos'][1] - self.radar_pos[1],
                uav['pos'][0] - self.radar_pos[0]
            )
            uav['detected'] = distance <= self.radar_range
            
            # Визуализация
            color = 'yellow' if uav['detected'] else 'lime'
            marker = 'o' if uav['detected'] else '^'
            size = 14 if uav['detected'] else 10
            
            # Траектория
            if len(uav['path']) > 1:
                x, y = zip(*uav['path'])
                self.ax.plot(x, y, 'b-', alpha=0.2, linewidth=1)
            
            # БПЛА
            self.ax.plot(
                uav['pos'][1], uav['pos'][0],
                marker=marker, color=color, markersize=size,
                markeredgecolor='black' if uav['detected'] else 'none'
            )
            
            # Подпись
            if uav['detected']:
                self.ax.text(
                    uav['pos'][1] + 0.02, uav['pos'][0],
                    f"#{uav['id']}", 
                    color='red',
                    fontsize=9
                )
            
            # Удаление вышедших за границы
            if not (40.5 <= uav['pos'][1] <= 41.5 and 44.5 <= uav['pos'][0] <= 45.5):
                self.uavs.remove(uav)
            else:
                active_uavs += 1
        
        # Обновление статуса
        self.lbl_status.config(text=f"Обнаружение... | БПЛА: {active_uavs}")
        
        self.canvas.draw()
        
        # Продолжаем обновление
        if self.simulation_active or self.uavs:
            self.root.after(50, self.update_display)

if __name__ == "__main__":
    root = tk.Tk()
    app = RadarApp(root)
    root.mainloop()