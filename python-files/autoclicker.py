from pynput.mouse import Button, Controller
import time
import threading
import keyboard

mouse = Controller()
clicking = False
click_speed = 0.05  # كل كم ثانية يعمل كليك (0.001 = 1 مللي ثانية)

def clicker():
    while True:
        if clicking:
            mouse.click(Button.left, 1)
            time.sleep(click_speed)
        else:
            time.sleep(0.01)

def toggle_clicking():
    global clicking
    clicking = not clicking
    print("تشغيل" if clicking else "إيقاف")

print("📌 اضغط x لتشغيل/إيقاف الأوتوكليكر")
print("📌 اضغط ESC للخروج من البرنامج")

threading.Thread(target=clicker, daemon=True).start()

keyboard.add_hotkey('x', toggle_clicking)
keyboard.wait('esc')
