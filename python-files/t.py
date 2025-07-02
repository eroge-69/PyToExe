Python 3.11.4 (tags/v3.11.4:d2340ef, Jun  7 2023, 05:45:37) [MSC v.1934 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
import cv2
... import numpy as np
... import pyautogui
... import keyboard
... import time
... import random
... from PIL import ImageGrab
... 
... # تنظیمات منطقه مرکزی اسکرین برای بررسی (برای مانیتور 1920x1080)
... REGION_SIZE = 10  # ناحیه‌ای 10x10 پیکسلی در مرکز
... SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()
... CENTER_X = SCREEN_WIDTH // 2 - REGION_SIZE // 2
... CENTER_Y = SCREEN_HEIGHT // 2 - REGION_SIZE // 2
... 
... TRIGGER_KEY = 'alt'  # کلید فعال‌سازی
... TRIGGER_COLOR = np.array([255, 50, 50])  # رنگ حدودی دشمن
... COLOR_TOLERANCE = 40
... 
... # بررسی میانگین رنگ با تلورانس
... def is_color_detected(image_np, target_color, tolerance):
...     avg_color = image_np.mean(axis=(0, 1))
...     return np.all(np.abs(avg_color - target_color) <= tolerance)
... 
... print("🔫 TriggerBot آماده‌ست. نگه‌داشتن ALT برای فعال‌سازی...")
... 
... while True:
...     if keyboard.is_pressed(TRIGGER_KEY):
...         # گرفتن تصویر از وسط صفحه
...         img = ImageGrab.grab(bbox=(CENTER_X, CENTER_Y, CENTER_X + REGION_SIZE, CENTER_Y + REGION_SIZE))
...         img_np = np.array(img)
... 
...         # پردازش ساده روی تصویر (کاهش نویز)
...         blurred = cv2.GaussianBlur(img_np, (3, 3), 0)
... 
...         if is_color_detected(blurred, TRIGGER_COLOR, COLOR_TOLERANCE):
...             delay = random.uniform(0.03, 0.08)
...             time.sleep(delay)
...             pyautogui.click()
... 
