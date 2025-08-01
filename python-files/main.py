import requests
import socket
import time
from threading import Thread
from plyer import notification
from pystray import Icon, Menu, MenuItem
from PIL import Image

# Конфигурация
URL = "http://mine-souls.ru"
IP_PORT = "213.108.170.61:8006"  # Пример: замените на нужный IP:порт
CHECK_INTERVAL = 3  # секунд

# Глобальная переменная состояния
status = "red"  # "red", "yellow", "green"


# Функция для создания иконок
def create_image(color):
    image = Image.new('RGB', (64, 64), color)
    return image


# Проверка доступности сайта
def check_website(url):
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except Exception:
        return False


# Проверка доступности IP:порт
def check_ip_port(ip_port):
    try:
        ip, port = ip_port.split(":")
        with socket.create_connection((ip, int(port)), timeout=5):
            return True
    except Exception:
        return False


# Функция проверки состояния
def check_status(icon):
    global status
    notified = False

    while True:
        site_ok = check_website(URL)
        ip_ok = check_ip_port(IP_PORT)

        if site_ok and ip_ok:
            new_status = "green"
        elif site_ok or ip_ok:
            new_status = "yellow"
        else:
            new_status = "red"

        # Обновляем значок
        icon.icon = create_image(new_status)

        # Уведомление только при первом переходе в "OK"
        if new_status == "green" and not notified:
            notification.notify(
                title="Сервисы доступны",
                message="Сайт и IP:порт доступны.",
                timeout=5
            )
            notified = True
        elif new_status != "green":
            notified = False

        status = new_status
        time.sleep(CHECK_INTERVAL)


# Основная функция
def main():
    icon = Icon("Checker")
    icon.icon = create_image("red")
    icon.menu = Menu(MenuItem("Выход", lambda: icon.stop()))

    # Запуск проверки в отдельном потоке
    thread = Thread(target=check_status, args=(icon,))
    thread.daemon = True
    thread.start()

    icon.run()


if __name__ == "__main__":
    main()
