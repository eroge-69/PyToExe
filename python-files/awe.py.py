import threading
import time
from pynput.mouse import Controller, Button, Listener

mouse = Controller()
LEFT_CPS = 15
RIGHT_CPS = 25
left_interval = 1 / LEFT_CPS
right_interval = 1 / RIGHT_CPS
left_pressed = False
right_pressed = False

def click_loop(button, interval, flag_name):
    while globals()[flag_name]:
        mouse.click(button)
        time.sleep(interval)

def on_click(x, y, button, pressed):
    global left_pressed, right_pressed
    # Uncomment to check what button your mouse sends
    # print(button, pressed)
    if str(button) == 'Button.x1':  # Adjust if your mouse prints differently
        left_pressed = pressed
        if pressed:
            threading.Thread(target=click_loop, args=(Button.left, left_interval, 'left_pressed'), daemon=True).start()
    elif str(button) == 'Button.x2':  # Adjust if your mouse prints differently
        right_pressed = pressed
        if pressed:
            threading.Thread(target=click_loop, args=(Button.right, right_interval, 'right_pressed'), daemon=True).start()

with Listener(on_click=on_click) as listener:
    listener.join()
