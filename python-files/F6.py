from pynput import mouse
import keyboard

# تابعی که وقتی دکمه موس فشرده شد اجرا می‌شود
def on_click(x, y, button, pressed):
    if pressed:
        # بررسی کلیدهای کنار موس (مثلاً Button.x1 یا Button.x2)
        if button == mouse.Button.x1:  # کلید کنار موس 1
            keyboard.press_and_release('f6')
        elif button == mouse.Button.x2:  # کلید کنار موس 2
            keyboard.press_and_release('f6')

# Listener برای موس
with mouse.Listener(on_click=on_click) as listener:
    listener.join()
