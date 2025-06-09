
import pyautogui
import numpy as np
import cv2
from pynput import mouse
import threading

def find_red_and_move():
    screenshot = pyautogui.screenshot()
    img = np.array(screenshot)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    height, width, _ = img.shape
    center_x, center_y = width // 2, height // 2

    # تحديد اللون الأحمر (بتدرجاته)
    lower_red = np.array([0, 0, 150])
    upper_red = np.array([100, 100, 255])

    mask = cv2.inRange(img, lower_red, upper_red)
    red_points = cv2.findNonZero(mask)

    if red_points is None:
        print("ماكو نقطة حمراء")
        return

    # نحسب أقرب نقطة حمراء للمنتصف
    closest_point = min(
        red_points,
        key=lambda pt: (pt[0][0] - center_x) ** 2 + (pt[0][1] - center_y) ** 2
    )

    target_x, target_y = closest_point[0][0], closest_point[0][1]
    print(f"تحريك الماوس إلى: ({target_x}, {target_y})")
    pyautogui.moveTo(target_x, target_y, duration=0.3)

# تابع يستمع للزر الأيسر
def on_click(x, y, button, pressed):
    if button == mouse.Button.left and pressed:
        threading.Thread(target=find_red_and_move).start()

# يبدأ الاستماع
with mouse.Listener(on_click=on_click) as listener:
    print("شغّال... اضغط زر الماوس الأيسر للبحث عن الأحمر")
    listener.join()
