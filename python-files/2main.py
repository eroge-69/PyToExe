import tkinter as tk
import random

def create_random_window():
  """Создает окно tkinter в случайном месте экрана."""
  window = tk.Tk() 
  window_width = 200 # ширина окна
  window_height = 50 # высота окна

  # Получаем размеры экрана
  screen_width = window.winfo_screenwidth()
  screen_height = window.winfo_screenheight()

  # Генерируем случайные координаты для окна
  x = random.randint(0, screen_width - window_width)
  y = random.randint(0, screen_height - window_height)

  # Устанавливаем положение окна
  window.geometry(f"{window_width}x{window_height}+{x}+{y}")

  # Добавляем какой-нибудь текст в окно 
  label = tk.Label(window, text="удалениe папки:System32...")
  label.pack()

  return window


if __name__ == "__main__":
  num_windows = 50  # Количество окон, которые нужно открыть

  windows = []
  for _ in range(num_windows):
    window = create_random_window()
    windows.append(window)

  # Запускаем главный цикл tkinter (нужен только один раз)
  windows[0].mainloop() #привязываем mainloop к первому окну, чтобы программа работала
