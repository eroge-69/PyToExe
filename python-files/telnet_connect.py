import telnetlib
import sys
import time

HOST = "192.168.1.100"  # Замените при необходимости
PORT = 10000
PASSWORD = "1234"

try:
    print(f"Подключение к {HOST}:{PORT}...")
    tn = telnetlib.Telnet(HOST, PORT, timeout=10)
    print("Соединение установлено.")

    # Ждём приглашение на ввод пароля
    tn.read_until(b"Password: ", timeout=5)
    tn.write(PASSWORD.encode('ascii') + b"\n")
    print("Пароль отправлен.")

    time.sleep(1)  # Подождём немного

    # Отправка команды C00
    tn.write(b"C00\n")
    print("Команда C00 отправлена.")

    # Получение и вывод ответа
    response = tn.read_until(b"\n", timeout=5)
    print("Ответ устройства:", response.decode('utf-8', errors='ignore'))

    tn.close()

except Exception as e:
    print("Ошибка:", e)
    sys.exit(1)
