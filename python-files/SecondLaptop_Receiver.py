import socket
from pynput.keyboard import Controller, Key

PORT = 5555
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("", PORT))

keyboard_controller = Controller()

print("Фоновый скрипт запущен. Ожидание сигналов...")

while True:
    data, addr = sock.recvfrom(1024)
    if data == b"NEXT":
        keyboard_controller.press(Key.page_down)
        keyboard_controller.release(Key.page_down)
        print(f"Слайд переключен (сигнал от {addr})")