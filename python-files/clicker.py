Python 3.13.7 (tags/v3.13.7:bcee1c3, Aug 14 2025, 14:15:11) [MSC v.1944 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
import pyautogui
import time
import threading
import keyboard
import sys

class AutoClicker:
    def __init__(self):
        self.running = False
        self.click_thread = None
        self.click_area = None
        self.clicks_per_minute = 60
        
    def set_click_area(self):
        """Установить область для кликов"""
        print("Наведите курсор в нужную позицию и нажмите 's' чтобы установить область кликов")
        print("Нажмите 'q' для отмены")
        
        while True:
            if keyboard.is_pressed('s'):
                self.click_area = pyautogui.position()
                print(f"Область установлена: {self.click_area}")
                return True
            elif keyboard.is_pressed('q'):
                print("Отмена установки области")
                return False
            time.sleep(0.1)
    
    def set_clicks_per_minute(self):
        """Установить количество кликов в минуту"""
        try:
            cpm = input("Введите количество кликов в минуту (по умолчанию 60): ")
            if cpm:
                self.clicks_per_minute = int(cpm)
                if self.clicks_per_minute <= 0:
                    print("Количество кликов должно быть больше 0!")
                    return False
            print(f"Установлено {self.clicks_per_minute} кликов в минуту")
            return True
        except ValueError:
            print("Ошибка! Введите целое число.")
            return False
    
    def click_loop(self):
        """Основной цикл кликов"""
        if not self.click_area:
            print("Сначала установите область кликов!")
            return
        
        delay = 60.0 / self.clicks_per_minute
        
        print(f"Запуск кликера! Клики в секунду: {1/delay:.2f}")
        print("Нажмите F2 для остановки")
        
        while self.running:
            pyautogui.click(self.click_area.x, self.click_area.y)
            time.sleep(delay)
    
    def start(self):
        """Запустить кликер"""
        if self.running:
            print("Кликер уже запущен!")
            return
        
        print("=== Настройка кликера ===")
        
        # Установка области кликов
        if not self.set_click_area():
            return
        
        # Установка скорости кликов
        if not self.set_clicks_per_minute():
            return
        
        self.running = True
        self.click_thread = threading.Thread(target=self.click_loop)
        self.click_thread.daemon = True
        self.click_thread.start()
        
        print("Кликер запущен! Нажмите F2 для остановки")
        
        # Ожидание остановки
        while self.running:
...             if keyboard.is_pressed('f2'):
...                 self.stop()
...             time.sleep(0.1)
...     
...     def stop(self):
...         """Остановить кликер"""
...         self.running = False
...         print("Кликер остановлен!")
... 
... def main():
...     print("=== Простой Авто-Кликер ===")
...     print("Инструкция:")
...     print("1. Установите область для кликов")
...     print("2. Установите количество кликов в минуту")
...     print("3. Нажмите F2 для остановки")
...     print("4. Нажмите ESC для выхода")
...     print()
...     
...     clicker = AutoClicker()
...     
...     try:
...         while True:
...             print("\nМеню:")
...             print("1 - Запустить кликер")
...             print("ESC - Выход")
...             
...             if keyboard.is_pressed('1'):
...                 clicker.start()
...             elif keyboard.is_pressed('esc'):
...                 print("Выход из программы...")
...                 break
...             
...             time.sleep(0.1)
...             
...     except KeyboardInterrupt:
...         print("\nПрограмма завершена.")
... 
... if __name__ == "__main__":
...     # Установите библиотеки: pip install pyautogui keyboard
