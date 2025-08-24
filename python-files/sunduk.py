import pandas as pd
import random
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import math

class WheelOfFortune:
    def __init__(self, root):
        self.root = root
        self.root.title("🏴‍☠️Пиратский сундук")
        self.root.geometry("900x700")
        
        # Данные для рулетки
        self.options = [
            'Сменить язык в игре на случайный',
            'Играть следующие 30 минут левой рукой',
            'Пройти отрезок с закрытыми глазами',
            'Использовать только стартовое оружие',
            'Включить максимальный уровень сложности',
            'Сыграть в игру, которую давно не запускал',
            'Сделать самого нелюбимого персонажа главным',
            'Проходить квесты, выбирая только злые ответы',
            'Проходить квесты, выбирая только добрые ответы',
            'Сыграть в симулятор, выбранный чатом',
            'Потратить все игровые деньги на ненужные вещи',
            'Устроить хаос в песочнице (GTA, Skyrim)',
            'Проходить уровень задом наперёд',
            'Не использовать способности/магию',
            'Говорить вслух за персонажа смешным голосом',
            'Сделать самую некрасивую внешность персонажу',
            'Сыграть в хоррор с выключенным звуком',
            'Запретить себе бегать, только ходить',
            'Сыграть в мобильную игру на пк'
        ]
        
        self.is_spinning = False
        self.current_angle = 0
        self.animation_id = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Основная рамка
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Заголовок
        title_label = ttk.Label(main_frame, 
                               text="🏴‍☠️Пиратский сундук", 
                               font=("Arial", 18, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Холст для колеса
        self.canvas = tk.Canvas(main_frame, width=400, height=400, bg='white', relief='raised', bd=3)
        self.canvas.grid(row=1, column=0, columnspan=2, pady=20)
        
        # Нарисовать начальное колесо
        self.draw_wheel()
        
        # Кнопка вращения
        self.spin_button = ttk.Button(main_frame, 
                                    text="🎯 Крутить колесо!", 
                                    command=self.start_spin)
        self.spin_button.grid(row=2, column=0, columnspan=2, pady=20)
        
        # Поле для результата
        self.result_var = tk.StringVar()
        self.result_var.set("Крутите колесо и узнайте вашу судьбу!")
        
        result_label = ttk.Label(main_frame, 
                                textvariable=self.result_var,
                                font=("Arial", 12, "bold"),
                                wraplength=600,
                                justify=tk.CENTER,
                                foreground="darkblue")
        result_label.grid(row=3, column=0, columnspan=2, pady=20)
        
        # Кнопка для показа диаграммы
        chart_button = ttk.Button(main_frame,
                                 text="📊 Показать диаграмму",
                                 command=self.show_chart)
        chart_button.grid(row=4, column=0, columnspan=2, pady=10)
        
    def draw_wheel(self, angle=0):
        """Рисует колесо фортуны с текущим углом поворота"""
        self.canvas.delete("all")
        
        # Центр и радиус колеса
        center_x, center_y = 200, 200
        radius = 180
        
        # Рисуем внешний круг
        self.canvas.create_oval(center_x - radius, center_y - radius,
                               center_x + radius, center_y + radius,
                               outline="black", width=3, fill="lightblue")
        
        # Рисуем сектора
        num_sectors = len(self.options)
        angle_per_sector = 360 / num_sectors
        
        # Цвета для секторов
        colors = [
            "#FF6B6B", "#4ECDC4", "#45B7D1", "#FFBE0B", 
            "#FB5607", "#FF006E", "#8338EC", "#3A86FF",
            "#38B000", "#FDFFB6", "#9BF6FF", "#BDB2FF",
            "#FFC6FF", "#A0C4FF", "#FFD6FF", "#BBDBFF",
            "#D0F4DE", "#FF99C8", "#FCF6BD"
        ]
        
        for i in range(num_sectors):
            start_angle = angle + i * angle_per_sector
            end_angle = start_angle + angle_per_sector
            
            # Рисуем сектор
            self.canvas.create_arc(center_x - radius, center_y - radius,
                                  center_x + radius, center_y + radius,
                                  start=start_angle, extent=angle_per_sector,
                                  fill=colors[i % len(colors)], outline="black")
            
            # Добавляем номер сектора
            mid_angle = start_angle + angle_per_sector / 2
            text_radius = radius * 0.7
            text_x = center_x + text_radius * math.cos(math.radians(mid_angle))
            text_y = center_y + text_radius * math.sin(math.radians(mid_angle))
            
            self.canvas.create_text(text_x, text_y, text=str(i+1), 
                                   font=("Arial", 12, "bold"), fill="white")
        
        # Рисуем центральную точку
        self.canvas.create_oval(center_x - 15, center_y - 15,
                               center_x + 15, center_y + 15,
                               fill="red", outline="black", width=2)
        
        # Рисуем указатель (стрелку)
        pointer_length = 30
        self.canvas.create_polygon(
            center_x, center_y - radius - 10,
            center_x - 15, center_y - radius + pointer_length,
            center_x + 15, center_y - radius + pointer_length,
            fill="gold", outline="black", width=2
        )
        
        # Декоративный текст в центре
        self.canvas.create_text(center_x, center_y, text="сундук\nдефицита", 
                               font=("Arial", 14, "bold"), fill="darkred")
    
    def start_spin(self):
        """Начинает анимацию вращения колеса"""
        if not self.is_spinning:
            self.is_spinning = True
            self.spin_button.config(state="disabled")
            self.result_var.set("Колесо вращается...")
            
            # Параметры анимации
            self.spin_speed = 30  # начальная скорость
            self.slowdown_factor = 0.96  # коэффициент замедления
            self.min_speed = 0.5  # минимальная скорость
            
            # Запускаем анимацию
            self.animate_spin()
    
    def animate_spin(self):
        """Анимация вращения колеса"""
        if self.spin_speed > self.min_speed:
            # Обновляем угол
            self.current_angle = (self.current_angle + self.spin_speed) % 360
            
            # Перерисовываем колесо
            self.draw_wheel(self.current_angle)
            
            # Замедляем вращение
            self.spin_speed *= self.slowdown_factor
            
            # Продолжаем анимацию
            self.animation_id = self.root.after(30, self.animate_spin)
        else:
            # Завершаем вращение
            self.finish_spin()
    
    def finish_spin(self):
        """Завершает вращение и показывает результат"""
        # Определяем результат
        final_angle = self.current_angle % 360
        sector_size = 360 / len(self.options)
        
        # Находим выигравший сектор (учитываем, что указатель вверху)
        winning_sector = int((360 - final_angle) / sector_size) % len(self.options)
        result = self.options[winning_sector]
        
        # Показываем результат
        self.result_var.set(f"🎉 ПОЗДРАВЛЯЕМ! ВЫПАЛО:\n{result}")
        
        # Визуальный эффект - меняем цвет фона
        self.flash_effect(0)
        
        # Сбрасываем флаг вращения
        self.is_spinning = False
        self.spin_button.config(state="normal")
    
    def flash_effect(self, count):
        """Мигающий эффект для выделения результата"""
        if count < 6:
            if count % 2 == 0:
                self.canvas.config(bg="lightyellow")
            else:
                self.canvas.config(bg="white")
            self.root.after(150, lambda: self.flash_effect(count + 1))
    
    def show_chart(self):
        """Показывает диаграмму распределения"""
        chart_window = tk.Toplevel(self.root)
        chart_window.title("Распределение вероятностей")
        chart_window.geometry("1000x800")
        
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Создаем данные для диаграммы
        sizes = [100/len(self.options)] * len(self.options)
        
        # Создаем круговую диаграмму
        wedges, texts, autotexts = ax.pie(sizes, labels=self.options, autopct='%1.1f%%',
                                         startangle=90, colors=plt.cm.Set3.colors)
        
        # Улучшаем внешний вид текста
        for text in texts:
            text.set_fontsize(8)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title('🎡 Распределение вероятностей колеса фортуны', fontsize=16, fontweight='bold')
        ax.axis('equal')
        
        canvas = FigureCanvasTkAgg(fig, chart_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# Запуск графического интерфейса
if __name__ == "__main__":
    root = tk.Tk()
    app = WheelOfFortune(root)
    root.mainloop()