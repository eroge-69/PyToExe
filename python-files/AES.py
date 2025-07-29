import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import secrets

# Constants
KEY_SIZE = 32  # AES-256
IV_SIZE = 16
SALT_SIZE = 16
ITERATIONS = 100000
BLOCK_SIZE = 16


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive AES key from password using PBKDF2."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_SIZE,
        salt=salt,
        iterations=ITERATIONS,
        backend=default_backend()
    )
    return kdf.derive(password.encode())


def pad(data: bytes) -> bytes:
    pad_len = BLOCK_SIZE - (len(data) % BLOCK_SIZE)
    return data + bytes([pad_len] * pad_len)


def unpad(data: bytes) -> bytes:
    pad_len = data[-1]
    if pad_len < 1 or pad_len > BLOCK_SIZE:
        raise ValueError("Invalid padding.")
    return data[:-pad_len]


def encrypt_file(input_path: str, output_path: str, password: str):
    try:
        with open(input_path, 'rb') as f:
            plaintext = f.read()

        salt = secrets.token_bytes(SALT_SIZE)
        iv = secrets.token_bytes(IV_SIZE)
        key = derive_key(password, salt)

        padded_plaintext = pad(plaintext)

        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()

        with open(output_path, 'wb') as f:
            f.write(salt + iv + ciphertext)

        messagebox.showinfo("Success", "File encrypted successfully.")
    except Exception as e:
        messagebox.showerror("Encryption Error", str(e))


def decrypt_file(input_path: str, output_path: str, password: str):
    try:
        with open(input_path, 'rb') as f:
            raw = f.read()

        if len(raw) < SALT_SIZE + IV_SIZE:
            raise ValueError("File too short or corrupt.")

        salt = raw[:SALT_SIZE]
        iv = raw[SALT_SIZE:SALT_SIZE + IV_SIZE]
        ciphertext = raw[SALT_SIZE + IV_SIZE:]

        key = derive_key(password, salt)

        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        plaintext = unpad(padded_plaintext)

        with open(output_path, 'wb') as f:
            f.write(plaintext)

        messagebox.showinfo("Success", "File decrypted successfully.")
    except Exception as e:
        messagebox.showerror("Decryption Error", str(e))


def select_file_to_encrypt():
    file_path = filedialog.askopenfilename(title="Select File to Encrypt")
    if not file_path:
        return
    password = simpledialog.askstring("Password", "Enter a password for encryption:", show='*')
    if not password:
        return
    save_path = filedialog.asksaveasfilename(title="Save Encrypted File As", defaultextension=".aes")
    if not save_path:
        return
    encrypt_file(file_path, save_path, password)


def select_file_to_decrypt():
    file_path = filedialog.askopenfilename(title="Select File to Decrypt")
    if not file_path:
        return
    password = simpledialog.askstring("Password", "Enter the password for decryption:", show='*')
    if not password:
        return
    save_path = filedialog.asksaveasfilename(title="Save Decrypted File As")
    if not save_path:
        return
    decrypt_file(file_path, save_path, password)


# GUI Setup
root = tk.Tk()
root.title("AES File Encryptor/Decryptor")
root.geometry("350x180")
root.resizable(False, False)

frame = tk.Frame(root, padx=20, pady=20)
frame.pack()

label = tk.Label(frame, text="AES File Tool", font=("Arial", 16))
label.pack(pady=(0, 20))

encrypt_btn = tk.Button(frame, text="Encrypt File", width=25, command=select_file_to_encrypt)
encrypt_btn.pack(pady=5)

decrypt_btn = tk.Button(frame, text="Decrypt File", width=25, command=select_file_to_decrypt)
decrypt_btn.pack(pady=5)

root.mainloop()
