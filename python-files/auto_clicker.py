import time
import ctypes
import keyboard  # Bu dış kütüphane

user32 = ctypes.windll.user32

def mouse_down(button="left"):
    if button == "left":
        user32.mouse_event(0x0002, 0, 0, 0, 0)
    elif button == "right":
        user32.mouse_event(0x0008, 0, 0, 0, 0)

def mouse_up(button="left"):
    if button == "left":
        user32.mouse_event(0x0004, 0, 0, 0, 0)
    elif button == "right":
        user32.mouse_event(0x0010, 0, 0, 0, 0)

print("Başladı. Durdurmak için F8'e bas.")

while True:
    if keyboard.is_pressed('F8'):
        print("F8'e basıldı, durduruluyor...")
        break
    mouse_down("left")
    time.sleep(1.5)
    mouse_up("left")
    time.sleep(20)
