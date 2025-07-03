

import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

key_str = "Avenspace2025"
key = key_str.encode('utf-8')
key = key.ljust(16, b'\0')[:16]

block_size = AES.block_size

def encrypt_file_inplace(file_path):
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
        padded_data = pad(data, block_size)
        cipher = AES.new(key, AES.MODE_ECB)
        ciphertext = cipher.encrypt(padded_data)
        with open(file_path, 'wb') as f:
            f.write(ciphertext)
        print(f"Encrypted: {file_path}")
    except Exception as e:
        print(f"Failed to encrypt {file_path}: {e}")

def encrypt_folder_recursive(folder):
    for root, dirs, files in os.walk(folder):
        for file in files:
            full_path = os.path.join(root, file)
            encrypt_file_inplace(full_path)

if __name__ == "__main__":
    folder_to_encrypt = input("Enter folder path to encrypt recursively: ")
    encrypt_folder_recursive(folder_to_encrypt)
    print("Encryption complete.")