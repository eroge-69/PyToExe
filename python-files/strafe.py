import time
import threading
import keyboard as kb  # для is_pressed
from pynput import mouse, keyboard  # для Controller

# --- Настройки ---
MOUSE_BUTTON_SCROLL = mouse.Button.x1  # Верхняя боковая
MOUSE_BUTTON_PRESS = mouse.Button.x2   # Нижняя боковая

SCROLL_UP_INTERVAL = 0.008
SCROLL_DOWN_INTERVAL = 0.030

WHEEL_UP = 1
WHEEL_DOWN = -1

DOUBLE_TAP_DELAY = 0.020
HOLD_CHECK_INTERVAL = 0.01

# --- Состояния ---
scroll_up_running = False
scroll_down_running = False
xbutton1_held = False

scroll_up_thread = None
scroll_down_thread = None
tap_threads = {}

mouse_controller = mouse.Controller()
keyboard_controller = keyboard.Controller()

# --- Scroll вверх ---
def scroll_up_cycle():
    global scroll_up_running
    while scroll_up_running:
        if kb.is_pressed("w") or kb.is_pressed("a") or kb.is_pressed("d") or kb.is_pressed("x"):
            mouse_controller.scroll(0, WHEEL_UP)
        time.sleep(SCROLL_UP_INTERVAL)

# --- Scroll вниз ---
def scroll_down_cycle():
    global scroll_down_running
    while scroll_down_running:
        mouse_controller.scroll(0, WHEEL_DOWN)
        time.sleep(SCROLL_DOWN_INTERVAL)

# --- Даблтап + удержание ---
def double_tap_hold(key):
    # Даблтап
    kb.press(key)
    time.sleep(DOUBLE_TAP_DELAY)
    kb.release(key)
    time.sleep(DOUBLE_TAP_DELAY)
    kb.press(key)

    # Удержание пока боковая зажата и клавиша физически нажата
    while xbutton1_held and kb.is_pressed(key):
        time.sleep(HOLD_CHECK_INTERVAL)

    # Отпускаем только если клавиша физически отпущена
    if not kb.is_pressed(key):
        kb.release(key)

# --- Слушатель для клавиш W и S ---
def start_key_tap_listener():
    def listener():
        tapped = {"w": False, "s": False}
        while xbutton1_held:
            for key in tapped:
                if kb.is_pressed(key) and not tapped[key]:
                    tapped[key] = True
                    t = threading.Thread(target=double_tap_hold, args=(key,), daemon=True)
                    tap_threads[key] = t
                    t.start()
                elif not kb.is_pressed(key):
                    tapped[key] = False
            time.sleep(0.01)
    threading.Thread(target=listener, daemon=True).start()

# --- Обработка мыши ---
def on_click(x, y, button, pressed):
    global scroll_up_running, scroll_down_running, xbutton1_held

    if button == MOUSE_BUTTON_SCROLL:
        xbutton1_held = pressed
        if pressed:
            if not scroll_up_running:
                scroll_up_running = True
                threading.Thread(target=scroll_up_cycle, daemon=True).start()
            if not scroll_down_running:
                scroll_down_running = True
                threading.Thread(target=scroll_down_cycle, daemon=True).start()
            start_key_tap_listener()
        else:
            scroll_up_running = False
            scroll_down_running = False

    elif button == MOUSE_BUTTON_PRESS:
        if pressed:
            keyboard_controller.press(keyboard.Key.space)
            time.sleep(0.005)
            keyboard_controller.press(keyboard.Key.ctrl)
            time.sleep(0)
            keyboard_controller.release(keyboard.Key.ctrl)
            keyboard_controller.release(keyboard.Key.space)

# --- Запуск ---
if __name__ == "__main__":
    try:
        print("Скрипт запущен. XBUTTON1 = scroll + даблтап W/S, XBUTTON2 = прыжок + присед")
        mouse_listener = mouse.Listener(on_click=on_click)
        mouse_listener.start()
        mouse_listener.join()
    except Exception as e:
        print(f"[main] Ошибка: {e}")
