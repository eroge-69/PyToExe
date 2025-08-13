
import time
from pynput.mouse import Controller

mouse = Controller()

def move_mouse():
    while True:
        x, y = mouse.position
        mouse.position = (x + 1, y)
        time.sleep(0.1)
        mouse.position = (x, y)
        time.sleep(300)  # 5 dakikada bir hareket

if __name__ == "__main__":
    print("Anti-AFK çalışıyor... Kapatmak için pencereyi kapatın.")
    move_mouse()
