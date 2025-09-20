import pyautogui
import keyboard
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox

class AutoClicker:
    def __init__(self, root):
        self.root = root
        self.root.title("Clicker")
        self.root.geometry("300x200")
        self.root.resizable(False, False)
        
        self.clicking = False
        self.click_thread = None
        
        self.setup_ui()
        self.setup_hotkeys()
        
    def setup_ui(self):
        # Основная рамка
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Статус
        self.status_label = ttk.Label(main_frame, text="Статус: Остановлен", foreground="red")
        self.status_label.grid(row=0, column=0, columnspan=2, pady=5)
        
        # Интервал кликов
        ttk.Label(main_frame, text="Интервал (секунды):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.interval_var = tk.DoubleVar(value=0.1)
        self.interval_entry = ttk.Entry(main_frame, textvariable=self.interval_var, width=10)
        self.interval_entry.grid(row=1, column=1, pady=5)
        
        # Количество кликов
        ttk.Label(main_frame, text="Количество кликов (0=бесконечно):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.clicks_var = tk.IntVar(value=0)
        self.clicks_entry = ttk.Entry(main_frame, textvariable=self.clicks_var, width=10)
        self.clicks_entry.grid(row=2, column=1, pady=5)
        
        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="Запустить", command=self.start_clicking)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Остановить", command=self.stop_clicking, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Информация
        info_label = ttk.Label(main_frame, text="F8 - запуск/остановка", foreground="gray")
        info_label.grid(row=4, column=0, columnspan=2, pady=5)
        
    def setup_hotkeys(self):
        keyboard.add_hotkey('f8', self.toggle_clicking)
        
    def toggle_clicking(self):
        if self.clicking:
            self.stop_clicking()
        else:
            self.start_clicking()
            
    def start_clicking(self):
        if self.clicking:
            return
            
        try:
            interval = self.interval_var.get()
            if interval <= 0:
                messagebox.showerror("Ошибка", "Интервал должен быть больше 0")
                return
                
            self.clicking = True
            self.status_label.config(text="Статус: Работает", foreground="green")
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            
            # Запуск кликера в отдельном потоке
            self.click_thread = threading.Thread(target=self.click_loop, daemon=True)
            self.click_thread.start()
            
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные значения")
            
    def stop_clicking(self):
        if not self.clicking:
            return
            
        self.clicking = False
        self.status_label.config(text="Статус: Остановлен", foreground="red")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
    def click_loop(self):
        interval = self.interval_var.get()
        max_clicks = self.clicks_var.get()
        clicks_count = 0
        
        while self.clicking:
            try:
                pyautogui.click(button='left')
                clicks_count += 1
                
                # Проверка на ограничение количества кликов
                if max_clicks > 0 and clicks_count >= max_clicks:
                    self.stop_clicking()
                    break
                    
                time.sleep(interval)
                
            except pyautogui.FailSafeException:
                self.stop_clicking()
                messagebox.showwarning("Предупреждение", "Автокликер остановлен из-за движения мыши к углу экрана")
                break
                
    def on_closing(self):
        self.clicking = False
        self.root.destroy()

def main():
    root = tk.Tk()
    app = AutoClicker(root)
    
    # Обработка закрытия окна
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Центрирование окна
    root.eval('tk::PlaceWindow . center')
    
    root.mainloop()

if __name__ == "__main__":
    main()
