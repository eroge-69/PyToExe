import tkinter as tk
from tkinter import messagebox
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
import hashlib

def pad(text):
    return text + (16 - len(text) % 16) * chr(16 - len(text) % 16)

def unpad(text):
    return text[:-ord(text[-1])]

def encrypt(text, password):
    key = hashlib.sha256(password.encode()).digest()
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(text).encode())
    return base64.b64encode(iv + encrypted).decode()

def decrypt(ciphertext, password):
    try:
        key = hashlib.sha256(password.encode()).digest()
        raw = base64.b64decode(ciphertext)
        iv = raw[:16]
        encrypted = raw[16:]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = unpad(cipher.decrypt(encrypted).decode())
        return decrypted
    except Exception:
        return None

def encrypt_action():
    plaintext = entry_text.get("1.0", tk.END).strip()
    password = entry_password.get()
    if not plaintext or not password:
        messagebox.showerror("Errore", "Inserisci sia testo che password.")
        return
    encrypted = encrypt(plaintext, password)
    entry_result.delete("1.0", tk.END)
    entry_result.insert(tk.END, encrypted)

def decrypt_action():
    ciphertext = entry_text.get("1.0", tk.END).strip()
    password = entry_password.get()
    if not ciphertext or not password:
        messagebox.showerror("Errore", "Inserisci sia testo cifrato che password.")
        return
    decrypted = decrypt(ciphertext, password)
    if decrypted is None:
        messagebox.showerror("Errore", "Decrittazione fallita. Password errata o dati corrotti.")
        return
    entry_result.delete("1.0", tk.END)
    entry_result.insert(tk.END, decrypted)

root = tk.Tk()
root.title("Cifratura AES-256")
root.geometry("600x400")

tk.Label(root, text="Testo / Testo cifrato:").pack()
entry_text = tk.Text(root, height=6)
entry_text.pack(fill=tk.BOTH, padx=10, pady=5)

tk.Label(root, text="Password:").pack()
entry_password = tk.Entry(root, show="*")
entry_password.pack(fill=tk.X, padx=10, pady=5)

tk.Button(root, text="Cripta", command=encrypt_action).pack(pady=5)
tk.Button(root, text="Decripta", command=decrypt_action).pack(pady=5)

tk.Label(root, text="Risultato:").pack()
entry_result = tk.Text(root, height=6)
entry_result.pack(fill=tk.BOTH, padx=10, pady=5)

root.mainloop()

