import tkinter as tk
from datetime import datetime, timedelta
import threading
import time

class DualStopwatch:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Ебашь")
        self.root.geometry("600x400")
        self.root.configure(bg='black')
        
        # Состояние циферблатов
        self.timer1_running = False
        self.timer2_running = False
        self.timer1_time = timedelta()
        self.timer2_time = timedelta()
        self.timer1_start = None
        self.timer2_start = None
        
        self.setup_ui()
        self.update_display()
        
    def setup_ui(self):
        # Заголовок
        title = tk.Label(self.root, text="Ебашить", 
                        font=("Arial", 20, "bold"), fg="white", bg="black")
        title.pack(pady=10)
        
        # Фрейм для первого циферблата
        frame1 = tk.Frame(self.root, bg="black")
        frame1.pack(pady=20)
        
        tk.Label(frame1, text="Циферблат 1", font=("Arial", 14), 
                fg="cyan", bg="black").pack()
        
        self.display1 = tk.Label(frame1, text="00:00:00.00", 
                                font=("Arial", 24, "bold"), 
                                fg="cyan", bg="black", width=15)
        self.display1.pack(pady=5)
        
        self.btn1 = tk.Button(frame1, text="СТАРТ", font=("Arial", 12, "bold"),
                             bg="green", fg="white", width=15,
                             command=self.toggle_timer1)
        self.btn1.pack(pady=5)
        
        # Фрейм для второго циферблата
        frame2 = tk.Frame(self.root, bg="black")
        frame2.pack(pady=20)
        
        tk.Label(frame2, text="Циферблат 2", font=("Arial", 14), 
                fg="orange", bg="black").pack()
        
        self.display2 = tk.Label(frame2, text="00:00:00.00", 
                                font=("Arial", 24, "bold"), 
                                fg="orange", bg="black", width=15)
        self.display2.pack(pady=5)
        
        self.btn2 = tk.Button(frame2, text="СТАРТ", font=("Arial", 12, "bold"),
                             bg="green", fg="white", width=15,
                             command=self.toggle_timer2)
        self.btn2.pack(pady=5)
        
        # Кнопка сброса
        reset_btn = tk.Button(self.root, text="СБРОС ВСЕХ", 
                             font=("Arial", 12, "bold"),
                             bg="red", fg="white", width=20,
                             command=self.reset_all)
        reset_btn.pack(pady=20)
        
    def toggle_timer1(self):
        if self.timer1_running:
            # Остановка первого таймера
            self.timer1_running = False
            elapsed = datetime.now() - self.timer1_start
            self.timer1_time += elapsed
            self.btn1.config(text="СТАРТ", bg="green")
        else:
            # Запуск первого таймера (остановка второго)
            if self.timer2_running:
                self.stop_timer2()
            
            self.timer1_running = True
            self.timer1_start = datetime.now()
            self.btn1.config(text="СТОП", bg="red")
    
    def toggle_timer2(self):
        if self.timer2_running:
            # Остановка второго таймера
            self.timer2_running = False
            elapsed = datetime.now() - self.timer2_start
            self.timer2_time += elapsed
            self.btn2.config(text="СТАРТ", bg="green")
        else:
            # Запуск второго таймера (остановка первого)
            if self.timer1_running:
                self.stop_timer1()
            
            self.timer2_running = True
            self.timer2_start = datetime.now()
            self.btn2.config(text="СТОП", bg="red")
    
    def stop_timer1(self):
        if self.timer1_running:
            elapsed = datetime.now() - self.timer1_start
            self.timer1_time += elapsed
            self.timer1_running = False
            self.btn1.config(text="СТАРТ", bg="green")
    
    def stop_timer2(self):
        if self.timer2_running:
            elapsed = datetime.now() - self.timer2_start
            self.timer2_time += elapsed
            self.timer2_running = False
            self.btn2.config(text="СТАРТ", bg="green")
    
    def reset_all(self):
        self.timer1_running = False
        self.timer2_running = False
        self.timer1_time = timedelta()
        self.timer2_time = timedelta()
        self.btn1.config(text="СТАРТ", bg="green")
        self.btn2.config(text="СТАРТ", bg="green")
    
    def format_time(self, total_time):
        total_seconds = int(total_time.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        centiseconds = int(total_time.microseconds / 10000)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{centiseconds:02d}"
    
    def update_display(self):
        # Обновление времени для первого циферблата
        if self.timer1_running:
            current_time = self.timer1_time + (datetime.now() - self.timer1_start)
        else:
            current_time = self.timer1_time
        self.display1.config(text=self.format_time(current_time))
        
        # Обновление времени для второго циферблата
        if self.timer2_running:
            current_time = self.timer2_time + (datetime.now() - self.timer2_start)
        else:
            current_time = self.timer2_time
        self.display2.config(text=self.format_time(current_time))
        
        # Обновление каждые 10 миллисекунд
        self.root.after(10, self.update_display)
    
    def run(self):
        self.root.mainloop()

# Запуск программы
if __name__ == "__main__":
    app = DualStopwatch()
    app.run()