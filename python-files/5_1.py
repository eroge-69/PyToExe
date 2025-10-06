import tkinter as tk
import math
from tkinter import ttk

class Barometer:
    def __init__(self, root):
        self.root = root
        self.root.title("Атмосферный барометр")
        self.root.geometry("900x700")
        self.root.configure(bg='#2a5298')
        
        # Основные параметры
        self.min_pressure_mmhg = 700  # мм рт. ст.
        self.max_pressure_mmhg = 800
        self.min_pressure_hpa = 930   # гПа
        self.max_pressure_hpa = 1070
        
        self.current_pressure = 760  # начальное значение в мм рт. ст.
        
        self.setup_ui()
        
    def setup_ui(self):
        # Заголовок
        title_frame = tk.Frame(self.root, bg='#2a5298')
        title_frame.pack(pady=10)
        
        title = tk.Label(title_frame, text="АТМОСФЕРНЫЙ БАРОМЕТР", 
                        font=('Arial', 24, 'bold'), fg='white', bg='#2a5298')
        title.pack()
        
        subtitle = tk.Label(title_frame, text="Измерение атмосферного давления", 
                           font=('Arial', 12), fg='#e0e0e0', bg='#2a5298')
        subtitle.pack()
        
        # Основной контент
        content_frame = tk.Frame(self.root, bg='#2a5298')
        content_frame.pack(pady=20)
        
        # Барометр
        self.canvas = tk.Canvas(content_frame, width=500, height=500, 
                               bg='#f8f8f8', highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, padx=20)
        
        # Панель управления
        control_frame = tk.Frame(content_frame, bg='white', relief='raised', bd=2)
        control_frame.pack(side=tk.RIGHT, padx=20)
        
        # Слайдер давления
        pressure_frame = tk.Frame(control_frame, bg='white')
        pressure_frame.pack(pady=15, padx=20, fill='x')
        
        pressure_label = tk.Label(pressure_frame, text="Атмосферное давление", 
                                 font=('Arial', 14, 'bold'), bg='white')
        pressure_label.pack(anchor='w')
        
        self.pressure_slider = ttk.Scale(pressure_frame, from_=self.min_pressure_mmhg, 
                                        to=self.max_pressure_mmhg, orient='horizontal',
                                        command=self.on_slider_change)
        self.pressure_slider.set(self.current_pressure)
        self.pressure_slider.pack(fill='x', pady=5)
        
        # Отображение значений
        values_frame = tk.Frame(control_frame, bg='white')
        values_frame.pack(pady=10, padx=20, fill='x')
        
        self.pressure_display = tk.Label(values_frame, 
                                        text=f"Давление: {self.current_pressure} мм рт. ст.",
                                        font=('Arial', 12), bg='#f8f8f8', 
                                        relief='sunken', bd=2, padx=10, pady=5)
        self.pressure_display.pack(fill='x', pady=5)
        
        self.hpa_display = tk.Label(values_frame, 
                                   text=f"гПа: {self.calculate_hpa(self.current_pressure)}",
                                   font=('Arial', 12), bg='#f8f8f8', 
                                   relief='sunken', bd=2, padx=10, pady=5)
        self.hpa_display.pack(fill='x', pady=5)
        
        # Статус давления
        self.status_display = tk.Label(control_frame, 
                                      text=self.get_pressure_status(self.current_pressure),
                                      font=('Arial', 14, 'bold'), bg='#e8f4fd',
                                      relief='raised', bd=2, padx=20, pady=10)
        self.status_display.pack(pady=15, padx=20, fill='x')
        
        # Рисуем барометр
        self.draw_barometer()
        
    def calculate_hpa(self, pressure_mmhg):
        # Конвертация мм рт. ст. в гПа
        return round(pressure_mmhg * 1.33322, 1)
    
    def calculate_mmhg(self, pressure_hpa):
        # Конвертация гПа в мм рт. ст.
        return round(pressure_hpa / 1.33322, 1)
    
    def get_pressure_status(self, pressure):
        if pressure < 720: return "ОЧЕНЬ НИЗКОЕ"
        if pressure < 740: return "НИЗКОЕ"
        if pressure < 750: return "ПОНИЖЕННОЕ"
        if pressure < 770: return "НОРМАЛЬНОЕ"
        if pressure < 790: return "ПОВЫШЕННОЕ"
        if pressure < 820: return "ВЫСОКОЕ"
        return "ОЧЕНЬ ВЫСОКОЕ"
    
    def update_status_color(self, pressure):
        colors = {
            "ОЧЕНЬ НИЗКОЕ": ("#ffcccc", "#990000"),
            "НИЗКОЕ": ("#ffe6cc", "#cc6600"),
            "ПОНИЖЕННОЕ": ("#ffe6cc", "#cc6600"),
            "НОРМАЛЬНОЕ": ("#e8f4fd", "#2c3e50"),
            "ПОВЫШЕННОЕ": ("#e6f7e6", "#2d662d"),
            "ВЫСОКОЕ": ("#e6e6ff", "#333399"),
            "ОЧЕНЬ ВЫСОКОЕ": ("#e6e6ff", "#333399")
        }
        status = self.get_pressure_status(pressure)
        bg_color, fg_color = colors[status]
        self.status_display.configure(bg=bg_color, fg=fg_color)
    
    def on_slider_change(self, value):
        self.current_pressure = float(value)
        self.update_displays()
        self.draw_barometer()
    
    def update_displays(self):
        self.pressure_display.config(text=f"Давление: {self.current_pressure:.1f} мм рт. ст.")
        self.hpa_display.config(text=f"гПа: {self.calculate_hpa(self.current_pressure)}")
        self.status_display.config(text=self.get_pressure_status(self.current_pressure))
        self.update_status_color(self.current_pressure)
    
    def draw_barometer(self):
        self.canvas.delete("all")
        
        # Параметры барометра
        center_x, center_y = 250, 250
        radius = 200
        start_angle = 135
        arc_angle = 270
        
        # Рисуем корпус
        self.canvas.create_oval(25, 25, 475, 475, width=15, outline='#8B4513', fill='#f0f0f0')
        self.canvas.create_oval(45, 45, 455, 455, width=2, outline='#cccccc', fill='#f8f8f8')
        
        # Рисуем шкалы и деления
        self.draw_scales(center_x, center_y, radius, start_angle, arc_angle)
        
        # Рисуем стрелку
        self.draw_needle(center_x, center_y, radius - 50)
        
        # Центральный колпачок
        self.canvas.create_oval(center_x-15, center_y-15, center_x+15, center_y+15, 
                               fill='#8B0000', outline='#600', width=3)
        
        # Подписи шкал - "мм рт. ст." поднята выше и правее
        mmhg_label_y = center_y + radius - 50  # Поднял выше (было -30)
        self.canvas.create_text(center_x - 40, mmhg_label_y, text="мм рт. ст.", 
                               font=('Arial', 12, 'bold'), fill='#333', anchor='e')  # Сдвинул правее (было -60)
        
        hpa_label_y = center_y + radius - 70
        self.canvas.create_text(center_x + 60, hpa_label_y, text="гПа", 
                               font=('Arial', 12, 'bold'), fill='#d63333', anchor='w')
    
    def draw_scales(self, cx, cy, radius, start_angle, arc_angle):
        # Основные деления для мм рт. ст. (каждые 10 единиц)
        major_steps_mmhg = [700, 710, 720, 730, 740, 750, 760, 770, 780, 790, 800]
        
        # Основные деления для гПа (каждые 10 единиц)
        major_steps_hpa = [930, 940, 950, 960, 970, 980, 990, 1000, 1010, 1020, 1030, 1040, 1050, 1060, 1070]
        
        # Рисуем деления и подписи для мм рт. ст. (внешняя шкала)
        for pressure in major_steps_mmhg:
            angle = start_angle + ((pressure - self.min_pressure_mmhg) / 
                                 (self.max_pressure_mmhg - self.min_pressure_mmhg)) * arc_angle
            rad = math.radians(angle)
            
            # Деления для мм рт. ст.
            x1 = cx + math.cos(rad) * (radius - 25)
            y1 = cy + math.sin(rad) * (radius - 25)
            x2 = cx + math.cos(rad) * radius
            y2 = cy + math.sin(rad) * radius
            self.canvas.create_line(x1, y1, x2, y2, width=3, fill='#333')
            
            # Подписи мм рт. ст. - внутри окружности
            label_radius = radius - 35
            label_x = cx + math.cos(rad) * label_radius
            label_y = cy + math.sin(rad) * label_radius
            
            self.canvas.create_text(label_x, label_y, text=str(pressure), 
                                   font=('Arial', 11, 'bold'), fill='#333', 
                                   angle=0)
        
        # Рисуем деления и подписи для гПа (внутренняя шкала)
        for hpa in major_steps_hpa:
            angle = start_angle + ((hpa - self.min_pressure_hpa) / 
                                 (self.max_pressure_hpa - self.min_pressure_hpa)) * arc_angle
            rad = math.radians(angle)
            
            # Деления для гПа
            x1 = cx + math.cos(rad) * (radius - 65)
            y1 = cy + math.sin(rad) * (radius - 65)
            x2 = cx + math.cos(rad) * (radius - 45)
            y2 = cy + math.sin(rad) * (radius - 45)
            self.canvas.create_line(x1, y1, x2, y2, width=2, fill='#d63333')
            
            # Подписи гПа
            label_radius = radius - 80
            label_x = cx + math.cos(rad) * label_radius
            label_y = cy + math.sin(rad) * label_radius
            
            self.canvas.create_text(label_x, label_y, text=str(hpa), 
                                   font=('Arial', 10), fill='#d63333', 
                                   angle=0)
        
        # Мелкие деления для мм рт. ст. (каждые 1 единица)
        for pressure in range(self.min_pressure_mmhg, self.max_pressure_mmhg + 1):
            if pressure not in major_steps_mmhg:
                angle = start_angle + ((pressure - self.min_pressure_mmhg) / 
                                     (self.max_pressure_mmhg - self.min_pressure_mmhg)) * arc_angle
                rad = math.radians(angle)
                
                x1 = cx + math.cos(rad) * (radius - 15)
                y1 = cy + math.sin(rad) * (radius - 15)
                x2 = cx + math.cos(rad) * radius
                y2 = cy + math.sin(rad) * radius
                self.canvas.create_line(x1, y1, x2, y2, width=1, fill='#666')
        
        # Мелкие деления для гПа (каждые 1 единица)
        for hpa in range(self.min_pressure_hpa, self.max_pressure_hpa + 1):
            if hpa not in major_steps_hpa:
                angle = start_angle + ((hpa - self.min_pressure_hpa) / 
                                     (self.max_pressure_hpa - self.min_pressure_hpa)) * arc_angle
                rad = math.radians(angle)
                
                x1 = cx + math.cos(rad) * (radius - 65)
                y1 = cy + math.sin(rad) * (radius - 65)
                x2 = cx + math.cos(rad) * (radius - 55)
                y2 = cy + math.sin(rad) * (radius - 55)
                self.canvas.create_line(x1, y1, x2, y2, width=1, fill='#ff6666')
    
    def draw_needle(self, cx, cy, length):
        # Используем мм рт. ст. для позиционирования стрелки
        angle = 135 + ((self.current_pressure - self.min_pressure_mmhg) / 
                      (self.max_pressure_mmhg - self.min_pressure_mmhg)) * 270
        rad = math.radians(angle)
        
        # Рисуем стрелку
        end_x = cx + math.cos(rad) * length
        end_y = cy + math.sin(rad) * length
        
        # Основная линия стрелки
        self.canvas.create_line(cx, cy, end_x, end_y, width=4, fill='#c00', 
                               arrow='last', arrowshape=(16, 20, 8))
        
        # Декоративная основа стрелки
        self.canvas.create_oval(cx-8, cy-8, cx+8, cy+8, fill='#c00', outline='#600')

if __name__ == "__main__":
    root = tk.Tk()
    app = Barometer(root)
    root.mainloop()