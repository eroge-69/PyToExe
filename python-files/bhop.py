import time
import keyboard
def jump(duration):
    keyboard.send("space")
    time.sleep(duration)
while True:
    if keyboard.is_pressed("space"):
        jump(0.0156 * 1)
        while keyboard.is_pressed("space"):
                jump(0.0156 * 2)
    else:
        time.sleep(0.001)