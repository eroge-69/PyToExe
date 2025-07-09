import json
import pyperclip
from cryptography.fernet import Fernet

# Generate a key for encryption
key = Fernet.generate_key()
cipher_suite = Fernet(key)

# Function to encrypt data
def encrypt_data(data):
    return cipher_suite.encrypt(data.encode())

# Function to decrypt data
def decrypt_data(data):
    return cipher_suite.decrypt(data).decode()

# Function to add a password
def add_password(account, password):
    encrypted_password = encrypt_data(password)
    with open('passwords.json', 'r+') as file:
        data = json.load(file)
        data[account] = encrypted_password
        file.seek(0)
        json.dump(data, file)

# Function to retrieve a password
def retrieve_password(account):
    with open('passwords.json', 'r') as file:
        data = json.load(file)
        encrypted_password = data.get(account)
        if encrypted_password:
            return decrypt_data(encrypted_password)
        else:
            return None

# Example usage
add_password('example_account', 'example_password')
print(retrieve_password('example_account'))
