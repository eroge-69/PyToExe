import sys

def main():
    sys.stdout.write("This malware is no joke. Continue? (yes/no): ")
    user_input = sys.stdin.readline().lower().strip()

    if user_input == "yes":
        sys.stdout.write("Starting the virus...\n")
        # Placeholder for the actual malware code
        pass
    else:
        sys.stdout.write("Okay, self-destructing virus.\n")
        sys.exit(0)

if __name__ == "__main__":
    main()

from cryptography.fernet import Fernet
import os
import pyperclip

# Generate a secret key
key = Fernet.generate_key()

# Save the secret key to use for decryption later
with open("secret_key.key", "wb") as key_file:
    key_file.write(key)

# Function to encrypt the file
def encrypt_file(file_path):
    with open(file_path, "rb") as file:
        original_data = file.read()
    encrypted_data = Fernet(key).encrypt(original_data)
    with open(file_path + ".encrypted", "wb") as encrypted_file:
        encrypted_file.write(encrypted_data)
    os.rename(file_path, file_path + ".original")
    os.rename(file_path + ".encrypted", file_path)

# Function to decrypt the file
def decrypt_file(file_path, key_path):
    with open(key_path, "rb") as key_file:
        secret_key = key_file.read()
    fernet = Fernet(secret_key)
    with open(file_path, "rb") as file:
        encrypted_data = file.read()
    decrypted_data = fernet.decrypt(encrypted_data)
    with open(file_path[:-len(".encrypted")], "wb") as decrypted_file:
        decrypted_file.write(decrypted_data)

# Example usage
# Encrypt a file
encrypt_file("example.txt")

# Decrypt a file
decrypt_file("example.txt.encrypted", "secret_key.key")