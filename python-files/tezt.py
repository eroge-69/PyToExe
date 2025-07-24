import pyautogui
import time

def import_file_and_play(file_path):
    # Даем время переключиться на приложение (запустите его заранее)
    time.sleep(3)

    # Открываем меню импорта (может потребоваться настройка под ваше приложение)
    pyautogui.hotkey('ctrl', 'o')  # Часто используется для открытия файла
    time.sleep(1)

    # Вставляем путь к файлу в диалоговое окно
    pyautogui.write(file_path)
    time.sleep(1)
    pyautogui.press('enter')  # Подтверждаем выбор файла
    time.sleep(2)  # Ждем загрузки

    # Нажимаем кнопку Play (может потребоваться настройка координат)
    play_button_pos = pyautogui.locateOnScreen('play_button.png')  # Нужен скриншот кнопки
    if play_button_pos:
        pyautogui.click(play_button_pos)
        print("Кнопка Play нажата!")
    else:
        print("Не удалось найти кнопку Play. Проверьте скриншот.")

# Пример использования
file_path = r"C:\path\to\your\map_file.3dmap"  # Укажите свой путь
import_file_and_play(file_path)