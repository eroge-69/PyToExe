import os
import time
import logging
import pyautogui
from your_module import import_file_and_play  # Укажите реальный модуль/пакет

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S"
)

def automate_import(file_path, play_button_image='play_button.png'):
    try:
        if not os.path.exists(file_path):
            logging.error(f"Файл не найден: {file_path}")
            return False

        import_file_and_play(file_path)
        time.sleep(3)  # Ждем, пока пользователь переключится в нужное окно

        # Открываем меню импорта
        pyautogui.hotkey('alt', 'i')
        time.sleep(1)

        # Вводим путь к файлу
        pyautogui.write(file_path)
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(2)

        # Ищем и кликаем по кнопке Play
        button = pyautogui.locateOnScreen(play_button_image, confidence=0.8)
        if button:
            pyautogui.click(pyautogui.center(button))
            logging.info("Импорт и запуск выполнены успешно")
            return True
        else:
            logging.error("Не удалось найти кнопку Play на экране")
            return False

    except pyautogui.FailSafeException:
        logging.exception("Переместили мышь в угол – аварийная остановка")
        return False
    except Exception:
        logging.exception("Произошла непредвиденная ошибка")
        return False

if __name__ == "__main__":
    FILE_PATH = r"C:\Users\msi\Desktop\test.3ds"
    SUCCESS = automate_import(FILE_PATH)
    if not SUCCESS:
        logging.info("Попробуйте вручную проверить этапы импорта.")