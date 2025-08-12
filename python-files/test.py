import pyautogui
import pytesseract
import time
import threading
import tkinter as tk
from PIL import Image, ImageGrab
from tkinter import messagebox

# Настройка пути к Tesseract OCR (установите его отдельно)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Поменяйте на свой путь

class NumberMonitorApp:
    def __init__(self, master):
        self.master = master
        master.title("Number Monitor")
        master.geometry("200x120")
        master.attributes("-topmost", True)
        
        # Начальное значение X
        self.x_value = 80
        self.is_running = False
        
        # Создание интерфейса
        self.label = tk.Label(master, text=f"Текущее X: {self.x_value}", font=("Arial", 12))
        self.label.pack(pady=10)
        
        self.start_button = tk.Button(master, text="Пуск", command=self.start_monitoring, width=10)
        self.start_button.pack(pady=5)
        
        self.stop_button = tk.Button(master, text="Стоп", command=self.stop_monitoring, state=tk.DISABLED, width=10)
        self.stop_button.pack(pady=5)

    def capture_area(self):
        # Координаты области захвата (лево, верх, право, низ)
        region = (680, 635, 745, 670)
        screenshot = ImageGrab.grab(bbox=region)
        return screenshot

    def recognize_number(self, image):
        # Улучшение распознавания для цифр
        image = image.convert('L')  # В градации серого
        image = image.point(lambda x: 0 if x < 200 else 255)  # Бинаризация
        
        # Распознавание текста с ограничением на цифры
        custom_config = r'--oem 3 --psm 6 outputbase digits'
        text = pytesseract.image_to_string(image, config=custom_config)
        
        # Фильтрация нечисловых символов
        digits = ''.join(filter(str.isdigit, text))
        return int(digits) if digits else None

    def monitoring_loop(self):
        while self.is_running:
            try:
                screenshot = self.capture_area()
                y_value = self.recognize_number(screenshot)
                
                if y_value is not None:
                    if y_value > self.x_value:
                        self.x_value = y_value
                        pyautogui.click(x=820, y=540)
                        self.update_display()
                        
            except Exception as e:
                print(f"Ошибка: {e}")
            
            time.sleep(1)

    def start_monitoring(self):
        if not self.is_running:
            self.is_running = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            threading.Thread(target=self.monitoring_loop, daemon=True).start()

    def stop_monitoring(self):
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def update_display(self):
        self.label.config(text=f"Текущее X: {self.x_value}")

if __name__ == "__main__":
    root = tk.Tk()
    app = NumberMonitorApp(root)
    root.mainloop()