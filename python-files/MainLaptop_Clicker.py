
# Online IDE - Code Editor, Compiler, Interpreter

print('Welcome to Online IDE!! Happy Coding :)')
import socket
import threading
import tkinter as tk
from pynput import keyboard
from pynput.keyboard import Controller, Key

PORT = 5555
BROADCAST_IP = "255.255.255.255"

send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

keyboard_controller = Controller()
clicker_active = False

def receive_signals():
    recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    recv_sock.bind(("", PORT))
    while True:
        data, addr = recv_sock.recvfrom(1024)
        if data == b"NEXT":
            keyboard_controller.press(Key.page_down)
            keyboard_controller.release(Key.page_down)
            print("Слайд переключен (получено)")

def on_press(key):
    global clicker_active
    if not clicker_active:
        return
    try:
        if key == keyboard.Key.page_down:
            keyboard_controller.press(Key.page_down)
            keyboard_controller.release(Key.page_down)
            print("Слайд переключен (локально)")
            send_sock.sendto(b"NEXT", (BROADCAST_IP, PORT))
    except Exception as e:
        print(e)

def start_clicker():
    global clicker_active
    clicker_active = True
    status_label.config(text="Кликер активен")
    print("Кликер запущен")

threading.Thread(target=receive_signals, daemon=True).start()
threading.Thread(target=lambda: keyboard.Listener(on_press=on_press).start(), daemon=True).start()

root = tk.Tk()
root.title("Синхронный кликер")

start_button = tk.Button(root, text="Запустить кликер", command=start_clicker, width=20, height=2)
start_button.pack(pady=20)

status_label = tk.Label(root, text="Кликер не активен")
status_label.pack(pady=10)

root.mainloop()