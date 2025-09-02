from pynput import keyboard
import threading
import time
import ctypes

q_pressed = False
paused = False  # Флаг паузы макроса
keyboard_controller = keyboard.Controller()

def get_current_keyboard_layout():
    user32 = ctypes.WinDLL('user32')
    hwnd = user32.GetForegroundWindow()
    thread_id = user32.GetWindowThreadProcessId(hwnd, 0)
    layout_id = user32.GetKeyboardLayout(thread_id)
    lang_id = layout_id & (2**16 - 1)
    return lang_id

def press_key_according_to_layout():
    while q_pressed:
        if paused:
            time.sleep(0.1)
            continue

        lang_id = get_current_keyboard_layout()
        if lang_id == 0x419:
            key_to_press = 'ц'
        else:
            key_to_press = 'w'

        if not paused and q_pressed:
            keyboard_controller.press(key_to_press)
            keyboard_controller.release(key_to_press)
            keyboard_controller.press(key_to_press)
            keyboard_controller.release(key_to_press)
            time.sleep(0.2)

def on_press(key):
    global q_pressed, paused
    try:
        if key == keyboard.Key.esc:
            if paused:
                paused = False
        elif key == keyboard.Key.enter:
            paused = not paused
        elif hasattr(key, 'char') and key.char == 'q' and not q_pressed:
            q_pressed = True
            threading.Thread(target=press_key_according_to_layout, daemon=True).start()
    except AttributeError:
        pass

def on_release(key):
    global q_pressed
    try:
        if hasattr(key, 'vk') and key.vk == 0x51:
            q_pressed = False
    except AttributeError:
        pass

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
