# save this as file_encryptor.py
import os
import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# ======= CONFIG =======
folder_path = r"C:\Users\WDAGUtilityAccount\Desktop\New folder"
password = "Amarnath"
# ======================

# Derive a key from the password
def derive_key(password: str) -> bytes:
    salt = b'\x00' * 16  # fixed salt for demo (use random salt in real apps)
    kdf = PBKDF2HMAC(
        algorithm=hashlib.sha256(),
        length=32,
        salt=salt,
        iterations=100_000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

# Encrypt a file
def encrypt_file(file_path, cipher):
    with open(file_path, 'rb') as f:
        data = f.read()
    encrypted_data = cipher.encrypt(data)
    with open(file_path, 'wb') as f:
        f.write(encrypted_data)

def main():
    key = derive_key(password)
    cipher = Fernet(key)

    for root, dirs, files in os.walk(folder_path):
        for name in files:
            full_path = os.path.join(root, name)
            try:
                encrypt_file(full_path, cipher)
                print(f"Encrypted: {full_path}")
            except Exception as e:
                print(f"Failed: {full_path} ({e})")

    print("✅ All files encrypted successfully.")

if __name__ == "__main__":
    main()