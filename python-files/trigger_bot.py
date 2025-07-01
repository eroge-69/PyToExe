import pyautogui
import time
from pynput import keyboard
from pynput.mouse import Button, Controller
from PIL import ImageGrab

mouse = Controller()
bot_active = False

def get_crosshair_pixel():
    screen_width, screen_height = pyautogui.size()
    x = screen_width // 2
    y = screen_height // 2
    img = ImageGrab.grab(bbox=(x, y, x + 1, y + 1))
    pixel = img.getpixel((0, 0))
    return pixel

def is_enemy_color(rgb):
    r, g, b = rgb
    return r > 200 and g < 80 and b < 80  # Anpassen je nach Spiel

def on_press(key):
    global bot_active
    try:
        if key == keyboard.Key.f8:
            bot_active = not bot_active
            print(f"[INFO] Trigger-Bot {'aktiviert' if bot_active else 'deaktiviert'} (F8)")
    except:
        pass

listener = keyboard.Listener(on_press=on_press)
listener.start()

print("🎯 Trigger-Bot gestartet. F8 zum Aktivieren/Deaktivieren. STRG+C zum Beenden.")
time.sleep(1)

try:
    while True:
        if bot_active:
            pixel = get_crosshair_pixel()
            if is_enemy_color(pixel):
                mouse.press(Button.left)
                time.sleep(0.05)
                mouse.release(Button.left)
        time.sleep(0.005)
except KeyboardInterrupt:
    print("\n🛑 Trigger-Bot beendet.")