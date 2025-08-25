from pynput import mouse, keyboard
from pynput.keyboard import Key, Controller
import time

# Создаем контроллер для эмуляции нажатий клавиш
keyboard_controller = Controller()

# Текст для вставки
text_to_insert = "40817810"

# Флаг для блокировки, чтобы избежать рекурсии
blocked = False

def on_click(x, y, button, pressed):
    global blocked
    if pressed and button == mouse.Button.middle and not blocked:
        blocked = True
        print(f"Вставляем '{text_to_insert}' в позиции ({x}, {y})")
        
        # Эмулируем комбинацию Ctrl+V для вставки
        with keyboard_controller.pressed(Key.ctrl):
            keyboard_controller.press('v')
            keyboard_controller.release('v')
        
        # Небольшая задержка для стабильности
        time.sleep(0.1)
        blocked = False
        return False  # Останавливаем обработчик, если нужно одноразовое действие

# Копируем текст в буфер обмена
def copy_to_clipboard(text):
    import pyperclip
    pyperclip.copy(text)

# Установите текст в буфер обмена при запуске
copy_to_clipboard(text_to_insert)
print(f"Текст '{text_to_insert}' скопирован в буфер обмена.")
print("Приложение активно. Нажмите среднюю кнопку мыши для вставки.")

# Создаем и запускаем обработчик мыши
with mouse.Listener(on_click=on_click) as listener:
    listener.join()