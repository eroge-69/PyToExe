import webbrowser  # Для открытия веб-страниц
import time  # Для задержки времени
import os  # Для работы с операционной системой

def open_and_close_yandex_tab(text, close_delay=5):
    """
    Открывает вкладку в Яндекс с заданным текстом и закрывает её через указанное время.

    Args:
        text (str): Текст для поиска в Яндексе.
        close_delay (int): Время в секундах, через которое вкладка будет закрыта.
    """
    # Формируем URL для поиска в Яндексе
    url = f"https://yandex.ru/search/?text={text}"

    # Открываем URL в новой вкладке браузера по умолчанию
    webbrowser.open_new_tab(url)

    # Ждем указанное количество секунд
    time.sleep(close_delay)

    # Пытаемся закрыть вкладку (работает не всегда)
    try:
        if os.name == 'nt':  # Для Windows
            os.system("taskkill /im chrome.exe /f")  # Закрывает все копии Chrome
        elif os.name == 'posix':  # Для Linux/macOS
            os.system("pkill chrome")  # Закрывает все копии Chrome
        print("Вкладка должна была закрыться.")
    except Exception as e:
        print(f"Не удалось закрыть вкладку автоматически: {e}")
        print("Пожалуйста, закройте вкладку вручную.")

if __name__ == "__main__":
    # Текст для отображения в Яндексе
    text = "666 хихихххиих"

    # Открываем и закрываем вкладку
    open_and_close_yandex_tab(text, close_delay=5)

import ctypes  # Для взаимодействия с системными функциями
import os  # Для работы с файловой системой
import urllib.request  # Для скачивания изображения

def set_wallpaper(image_url):
    """
    Устанавливает изображение по URL в качестве обоев рабочего стола.

    Args:
        image_url (str): URL изображения.
    """
    try:
        # 1. Скачиваем изображение
        image_path = os.path.join(os.getcwd(), "wallpaper.jpg")  # Сохраняем в текущую директорию
        urllib.request.urlretrieve(image_url, image_path)

        # 2. Устанавливаем изображение в качестве обоев
        SPI_SETDESKWALLPAPER = 0x0014  # Код для установки обоев
        ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, image_path, 3)

        print("Обои успешно установлены!")

    except Exception as e:
        print(f"Ошибка при установке обоев: {e}")

if __name__ == "__main__":
    image_url = "https://avatars.mds.yandex.net/get-entity_search/1974363/1177760059/S600xU_2x"
    set_wallpaper(image_url)
