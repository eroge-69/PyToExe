import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
import time
import pygame
import threading
import os

class AlarmClock:
    def __init__(self, root):
        self.root = root
        self.root.title("Будильник")
        self.root.geometry("400x300")
        
        # Инициализация pygame для воспроизведения звука
        pygame.mixer.init()
        
        # Переменные
        self.alarm_time = tk.StringVar()
        self.alarm_set = False
        self.alarm_sound = None
        self.alarm_sound_path = None
        
        # Создание интерфейса
        self.create_widgets()
        
        # Запуск потока для проверки времени
        self.check_alarm_thread = threading.Thread(target=self.check_alarm, daemon=True)
        self.check_alarm_thread.start()
    
    def create_widgets(self):
        # Текущее время
        self.time_label = tk.Label(self.root, font=('Arial', 24))
        self.time_label.pack(pady=20)
        self.update_time()
        
        # Поле для установки времени будильника
        tk.Label(self.root, text="Установите время будильника (HH:MM):").pack()
        self.alarm_entry = tk.Entry(self.root, textvariable=self.alarm_time, font=('Arial', 14))
        self.alarm_entry.pack(pady=5)
        
        # Кнопки
        tk.Button(self.root, text="Установить будильник", command=self.set_alarm).pack(pady=5)
        tk.Button(self.root, text="Отключить будильник", command=self.stop_alarm).pack(pady=5)
        tk.Button(self.root, text="Выбрать звук будильника", command=self.choose_sound).pack(pady=5)
        
        # Информация о выбранном звуке
        self.sound_info = tk.Label(self.root, text="Звук не выбран", wraplength=350)
        self.sound_info.pack(pady=10)
    
    def update_time(self):
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)
    
    def set_alarm(self):
        alarm_time_str = self.alarm_time.get()
        try:
            # Проверка формата времени
            datetime.strptime(alarm_time_str, "%H:%M")
            self.alarm_set = True
            messagebox.showinfo("Будильник", f"Будильник установлен на {alarm_time_str}")
        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите время в формате HH:MM")
    
    def stop_alarm(self):
        self.alarm_set = False
        pygame.mixer.music.stop()
        messagebox.showinfo("Будильник", "Будильник отключен")
    
    def choose_sound(self):
        file_path = filedialog.askopenfilename(
            title="Выберите звуковой файл",
            filetypes=[("Audio Files", "*.mp3 *.wav *.ogg"), ("All Files", "*.*")]
        )
        
        if file_path:
            self.alarm_sound_path = file_path
            self.sound_info.config(text=f"Выбран звук: {os.path.basename(file_path)}")
    
    def check_alarm(self):
        while True:
            if self.alarm_set:
                now = datetime.now().strftime("%H:%M")
                alarm_time = self.alarm_time.get()
                
                if now == alarm_time:
                    self.trigger_alarm()
                    self.alarm_set = False
            
            time.sleep(1)  # Проверяем каждые 1 секунд
    
    def trigger_alarm(self):
        if self.alarm_sound_path:
            try:
                pygame.mixer.music.load(self.alarm_sound_path)
                pygame.mixer.music.play(loops=-1)  # Бесконечное воспроизведение
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось воспроизвести звук: {e}")
                # Используем стандартный звук
                pygame.mixer.music.load("sound.wav")  # Нужен файл sound.wav в той же папке
                pygame.mixer.music.play(loops=-1)
        else:
            # Если звук не выбран, пробуем воспроизвести стандартный
            try:
                pygame.mixer.music.load("sound.wav")
                pygame.mixer.music.play(loops=-1)
            except:
                # Если стандартного звука нет, просто выводим сообщение
                messagebox.showwarning("Будильник", "Время вышло! Выберите звук для будущих будильников.")
        
        # Показываем окно с сообщением
        messagebox.showinfo("Будильник", "Время вышло! Нажмите OK для отключения.")
        pygame.mixer.music.stop()

if __name__ == "__main__":
    root = tk.Tk()
    app = AlarmClock(root)
    root.mainloop()