import tkinter as tk
from threading import Thread
from pynput import keyboard, mouse
import time

# Başlangıç ayarı
delay = 100  # ms cinsinden
running = False

# WASD tuşları
keys_to_press = ['w', 'a', 's', 'd']

# Dinleyiciler
mouse_listener = None
keyboard_controller = keyboard.Controller()

def strafe_loop():
    global running
    while running:
        for key in keys_to_press:
            keyboard_controller.press(key)
            keyboard_controller.release(key)
            time.sleep(delay / 1000.0)

def on_click(x, y, button, pressed):
    global running
    if button == mouse.Button.right:
        if pressed:
            running = True
            Thread(target=strafe_loop).start()
        else:
            running = False

def start_mouse_listener():
    global mouse_listener
    mouse_listener = mouse.Listener(on_click=on_click)
    mouse_listener.start()

def update_delay(val):
    global delay
    delay = int(val)

def create_gui():
    window = tk.Tk()
    window.title("FiveM Strafe Bot")
    window.geometry("300x150")
    
    label = tk.Label(window, text="Tuş Basım Gecikmesi (ms):")
    label.pack(pady=10)

    scale = tk.Scale(window, from_=10, to=500, orient="horizontal", command=update_delay)
    scale.set(delay)
    scale.pack()

    info = tk.Label(window, text="Strafe için sağ tık basılı tutun")
    info.pack(pady=10)

    window.mainloop()

if __name__ == "__main__":
    start_mouse_listener()
    create_gui()
    
pencere.mainloop()