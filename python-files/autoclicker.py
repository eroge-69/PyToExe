
from pynput.mouse import Controller, Listener, Button
import threading
import time

controller = Controller()
clicking = False

def click_loop(button):
    while clicking:
        controller.click(button)
        time.sleep(0.01)  # adjust delay as needed

def on_click(x, y, button, pressed):
    global clicking
    if button in (Button.left, Button.right):
        if pressed:
            clicking = True
            threading.Thread(target=click_loop, args=(button,), daemon=True).start()
        else:
            clicking = False

if __name__ == "__main__":
    print("Hold down left or right mouse button to auto-click. Release to stop.")
    with Listener(on_click=on_click) as listener:
        listener.join()
