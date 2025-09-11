import tkinter as tk
import random
import screeninfo
import time
import threading

# Получаем информацию о мониторе
monitors = screeninfo.get_monitors()
monitor = monitors[0]  # Берем первый монитор

# Параметры окна
window_width = 300
window_height = 200
windows_to_create = 500
spawn_rate = 4  # 4 окна в секунду

# Флаг для остановки процесса
running = True

def create_window():
    global running
    
    # Создаем новое окно
    root = tk.Tk()
    root.protocol("WM_DELETE_WINDOW", lambda: None)  # Запрещаем закрытие через крестик
    
    # Генерируем случайные координаты
    max_x = monitor.width - window_width
    max_y = monitor.height - window_height
    x = random.randint(0, max_x)
    y = random.randint(0, max_y)
    
    # Устанавливаем параметры окна
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    root.configure(bg='red')  # Красный фон
    
    # Добавляем надпись ERROR
    label = tk.Label(root, text="ERROR", font=("Arial", 48), bg='red', fg='white')
    label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    
    # Обработчик нажатия ESC
    def on_escape(event):
        global running
        running = False
        root.destroy()
    
    root.bind("<Escape>", on_escape)
    
    root.mainloop()

def main():
    global running
    
    # Создаем главное окно для обработки ESC
    main_root = tk.Tk()
    main_root.withdraw()  # Скрываем главное окно
    
    def spawn_windows():
        global running  # Указываем, что используем внешнюю переменную
        created = 0
        start_time = time.time()
        
        while running and created < windows_to_create:
            if time.time() - start_time >= 1/spawn_rate:
                threading.Thread(target=create_window).start()
                created += 1
                start_time = time.time()
    
    # Запуск спавна окон в отдельном потоке
    spawn_thread = threading.Thread(target=spawn_windows)
    spawn_thread.start()
    
    # Обработчик ESC для главного окна
    def stop_on_escape(event):
        global running
        running = False
        main_root.destroy()
    
    main_root.bind("<Escape>", stop_on_escape)
    main_root.mainloop()

if __name__ == "__main__":
    main()