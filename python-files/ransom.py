import os, shutil, time, argparse
from cryptography.fernet import Fernet

def generate_key():
    return Fernet.generate_key()

def encrypt_file(file_path, key):
    f = Fernet(key)
    with open(file_path, 'rb') as file:
        original_data = file.read()
    encrypted_data = f.encrypt(original_data)
    with open(file_path, 'wb') as file:
        file.write(encrypted_data)

def decrypt_file(file_path, key):
    f = Fernet(key)
    with open(file_path, 'rb') as file:
        encrypted_data = file.read()
    decrypted_data = f.decrypt(encrypted_data)
    with open(file_path, 'wb') as file:
        file.write(decrypted_data)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--key', help='The key to use for encryption/decryption', default=None)
    parser.add_argument('--encrypt', help='Encrypt files with the specified extension(s)', nargs='+', default=[])
    parser.add_argument('--decrypt', help='Decrypt files with the specified extension(s)', nargs='+', default=[])
    args = parser.parse_args()

    if args.key is None:
        key = generate_key()
        print("Generated a new key:")
        print(key)
    else:
        key = bytes(args.key, 'utf-8')

    for ext in args.encrypt:
        for filename in os.listdir('.'):
            if filename.endswith(ext):
                encrypt_file(filename, key)

    for ext in args.decrypt:
        for filename in os.listdir('.'):
            if filename.endswith(ext):
                decrypt_file(filename, key)

if __name__ == "__main__":
    main()