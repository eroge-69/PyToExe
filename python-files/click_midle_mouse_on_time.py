import tkinter as tk
from pynput.mouse import Button, Controller

# Создаем объект контроллера мыши
mouse = Controller()

def press_and_release():
    # Получаем значение из регулятора времени (ползунка)
    duration = slider.get() / 1000  # Переводим миллисекунды в секунды
    
    # Нажатие средней кнопки мыши
    mouse.press(Button.middle)
    
    # Пауза перед отпуском
    root.after(int(duration * 1000))  # Конвертируем обратно в миллисекунды
    
    # Отпускание средней кнопки мыши
    mouse.release(Button.middle)

# Создание окна приложения
root = tk.Tk()
root.title("Регулятор времени удерживания")

# Ползунок для выбора длительности удерживания (в диапазоне от 0 до 10 сек.)
slider = tk.Scale(root, from_=0, to=10000, orient="horizontal",
                  label="Время удерживания (мс)", length=300,
                  resolution=100, command=lambda x: None)
slider.pack(pady=20)

# Кнопка запуска удерживания
button = tk.Button(root, text="Нажать и удержать", command=press_and_release)
button.pack(pady=10)

# Запуск главного цикла Tkinter
root.mainloop()