# Imports 
from tkinter import filedialog , messagebox
import os
from tkinter import *
import tkinter as tk
import random
import time



def generate_key(x):
    import random
    z = """`1234567890-qwertyuiop[]asdfghjkl;'zxcvbnm,./<>?:"{}_+!@#$%^&*()QWERTYUIOPASDFGHJKLZXCVBNM """
    z = list(z)
    pre = random.choices(z,k=10)
    pre_str = ''.join(pre)
    post = random.choices(z,k=10)
    post_str = ''.join(post)
    x = str(x)
    key = pre_str+x+post_str
    key_path = filedialog.askdirectory(title='Choose where to save the key')
    if key_path != '':
        with open(key_path+'/key.key','w') as file:
            file.write(key)
            file.close()
    else:
        while key_path != '':
            key_path = filedialog.askdirectory(title='Choose where to save the key')
        with open(key_path+'/key.key','w') as file:
            file.write(key)
            file.close()

def encrypt(shift=2):
    path_of_file = filedialog.askopenfilename(title='Choose the file you want to encrypt')
    if path_of_file:
        file_path = path_of_file
        with open(file_path, "rb") as f:
            data = f.read()

        shifted_data = bytes(
            ((byte * 3 + shift) ^ 0xAA) % 256  # multiply, add shift, xor with 0xAA, then mod 256
            for byte in data
        )

        with open(file_path, "wb") as f:
            f.write(shifted_data)
        os.rename(path_of_file,path_of_file+'.enc')
        generate_key(2)
        messagebox.showinfo('Encrypto Decrypto',f'Success !!! The file : "{file_path}" has been successfully encrypted by an encryption protocol.')

def decrypt():
    path_of_file = filedialog.askopenfilename(title='Please select the encrypted file')
    file_path = path_of_file
    try:
        key_path = filedialog.askopenfilename(title='Please select the key file',filetypes=[("Key files", "*.key")])
        if key_path != '':
            with open(key_path,'r') as file:
                code = file.read()
                code = list(code)
                code_from_file = int(code[10]+code[11]+code[12])
            decryption_code = code_from_file
            os.rename(path_of_file,path_of_file.split('.enc')[0])
            file_path = path_of_file.split('.enc')[0]
            with open(file_path, "rb") as f:
                data = f.read()

            # To reverse: ((byte * 3 + shift) ^ 0xAA) % 256
            # We do: reverse XOR, reverse addition, and reverse multiply by modular inverse of 3 mod 256.

            mod_inv_3 = 171  # because 3 * 171 % 256 = 1

            reversed_data = bytes(
                (( (byte ^ 0xAA) - decryption_code) * mod_inv_3 ) % 256
                for byte in data
            )

            with open(file_path, "wb") as f:
                f.write(reversed_data)
        else:
            messagebox.showwarning('Warning !!!','A file cannot be decrypted without key file.')
        messagebox.showinfo('Encrypto Decrypto',f'Success !!! The file : "{file_path}" has been successfully decrypted by decryption protocol.')
    except Exception as e:
        messagebox.showerror('ERROR !!!',e)


def ens():
    folder = filedialog.askdirectory(title='Please select folder to encrypt all files in it')
    if folder:
        files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
        ask = messagebox.askyesno('Confirmation Dialogue',f'Are you sure that you want to encrypt {len(files)} files ?')
        if ask:
            for i in files:
                shift = 2
                path_of_file = folder+f'/{i}'
                file_path = path_of_file
                with open(file_path, "rb") as f:
                    data = f.read()

                shifted_data = bytes(
                    ((byte * 3 + shift) ^ 0xAA) % 256  # multiply, add shift, xor with 0xAA, then mod 256
                    for byte in data
                )

                with open(file_path, "wb") as f:
                    f.write(shifted_data)
                os.rename(path_of_file,path_of_file+'.enc')
        messagebox.showinfo('Encrypto Decrypto',f'Success !!! The file : "{file_path}" has been successfully encrypted by an encryption protocol.')
            
def des():
    folder = filedialog.askdirectory(title='Please select the folder to decrypt all the files with extension .enc')
    if folder:
        files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
        for i in files:
            if not(str(i).endswith('.enc')):
                files.remove(i)
        if len(files) == 0:
            messagebox.showerror('ERROR !!!','No files to decrypt.')
        else:
            ask = messagebox.askyesno('Confirmation Dialogue',f'Are you sure that you want to decrypt {len(files)} files ?')
            if ask:
                key_path = filedialog.askopenfilename(title='Please select the key file',filetypes=[("Key files", "*.key")])
                for i in files:
                    try:
                        path_of_file = folder+f'/{i}'
                        if key_path != '':
                            with open(key_path,'r') as file:
                                code = file.read()
                                code = list(code)
                                code_from_file = int(code[10]+code[11]+code[12])
                            decryption_code = code_from_file
                            os.rename(path_of_file,path_of_file.split('.enc')[0])
                            file_path = path_of_file.split('.enc')[0]
                            with open(file_path, "rb") as f:
                                data = f.read()

                            # To reverse: ((byte * 3 + shift) ^ 0xAA) % 256
                            # We do: reverse XOR, reverse addition, and reverse multiply by modular inverse of 3 mod 256.

                            mod_inv_3 = 171  # because 3 * 171 % 256 = 1

                            reversed_data = bytes(
                                (( (byte ^ 0xAA) - decryption_code) * mod_inv_3 ) % 256
                                for byte in data
                            )

                            with open(file_path, "wb") as f:
                                f.write(reversed_data)
                        else:
                            messagebox.showwarning('Warning !!!','A file cannot be decrypted without key file.')
                    except Exception as e:
                        messagebox.showerror('ERROR !!!',e)
                if key_path!='':
                    messagebox.showinfo('Encrypto Decrypto',f'Success !!! The file : "{file_path}" has been successfully decrypted by decryption protocol.')

def printg(text, r=0, g=255, b=0):
    print(f"\033[38;2;{r};{g};{b}m{text}\033[0m")

def printr(text, r=255, g=0, b=0):
    print(f"\033[38;2;{r};{g};{b}m{text}\033[0m")

import sys
import time

def print_animated(text, r, g, b, delay=0.01):
    color_code = f"\033[38;2;{r};{g};{b}m"
    reset_code = "\033[0m"
    
    for char in text:
        sys.stdout.write(color_code + char + reset_code)
        sys.stdout.flush()
        time.sleep(delay)
    print()

print_animated('Encrypto Decrypto [Version: KL01]\n', 0, 255, 0)
time.sleep(2)

rep = ('''
+--------------- Select the operation ---------------+
|1. Encrypt file                                     |
+----------------------------------------------------+
|2. Encrypt files                                    |
+----------------------------------------------------+
|3. Decrypt file                                     |
+----------------------------------------------------+
|4. Decrypt files                                    |
+----------------------------------------------------+
''')
print_animated(rep, 255, 255, 0)
time.sleep(2)
def main():
    shift_code = random.randint(100,999)
    inp = input(f"\033[38;2;0;255;255mEnter your selection: \033[0m")

    if not(inp.isnumeric()):
        time.sleep(1)
        printr('\nInvalid input !!!\n')
        time.sleep(1)
        main()
    
    inp = int(inp)

    if inp == 1:
        print()
        print_animated('Requesting file path ...',0,255,0)
        time.sleep(1)
        path_of_file = filedialog.askopenfilename(title='Choose the file you want to encrypt')
        time.sleep(1)
        if path_of_file:
            ask = input(f"\033[38;2;0;255;255mDo you want to encrypt the file with code(p) or with key(k) : \033[0m")
            if ask.strip().lower() == 'p':
                print()
                ask = input(f"\033[38;2;0;255;255mPlease enter your encryption code : \033[0m")
                while not(ask.isnumeric()):
                    print()
                    print_animated('Please Enter A Number !!!',255,0,0)
                    print()
                    ask = input(f"\033[38;2;0;255;255mPlease enter your encryption code : \033[0m")
                ask = int(ask)
                file_path = path_of_file
                print_animated('Encrypting ...',0,255,0)
                time.sleep(2)
                with open(file_path, "rb") as f:
                    data = f.read()

                shifted_data = bytes(
                    ((byte * 3 + ask) ^ 0xAA) % 256  # multiply, add shift, xor with 0xAA, then mod 256
                    for byte in data
                )

                with open(file_path, "wb") as f:
                    f.write(shifted_data)
                os.rename(path_of_file,path_of_file+'.enc')
                print_animated('The file has been successfully encrypted !!!.',0,255,0)
                print()
                main()
            elif ask.strip().lower() == 'k':
                print()
                file_path = path_of_file
                print_animated('Encrypting ...',0,255,0)
                with open(file_path, "rb") as f:
                    data = f.read()

                shifted_data = bytes(
                    ((byte * 3 + shift_code) ^ 0xAA) % 256  # multiply, add shift, xor with 0xAA, then mod 256
                    for byte in data
                )

                with open(file_path, "wb") as f:
                    f.write(shifted_data)
                os.rename(path_of_file,path_of_file+'.enc')
                print_animated('Generating Key ...',0,255,0)
                print()
                generate_key(shift_code)
                print_animated('WARNING: Do not modify the key.',255,0,0)
                print()
                print_animated('The file has been successfully encrypted !!!.')
                print()
                main()                

    elif inp == 3:
        print()
        print_animated('Requesting file path ...',0,255,0)
        time.sleep(1)
        path_of_file = filedialog.askopenfilename(title='Choose the file you want to encrypt')
        time.sleep(1)
        if path_of_file:
            ask = input(f"\033[38;2;0;255;255mDo you want to decrypt the file with code(p) or with key(k) : \033[0m")
            if ask.strip().lower() == 'p':
                print()
                ask = input(f"\033[38;2;0;255;255mPlease enter your encryption code : \033[0m")
                while not(ask.isnumeric()):
                    print()
                    print_animated('Please Enter A Number !!!',255,0,0)
                    print()
                    ask = input(f"\033[38;2;0;255;255mPlease enter your encryption code : \033[0m")
                ask = int(ask)
                os.rename(path_of_file,path_of_file.split('.enc')[0])
                file_path = path_of_file.split('.enc')[0]
                print_animated('Decrypting ...',0,255,0)
                with open(file_path, "rb") as f:
                    data = f.read()

                # To reverse: ((byte * 3 + shift) ^ 0xAA) % 256
                # We do: reverse XOR, reverse addition, and reverse multiply by modular inverse of 3 mod 256.

                mod_inv_3 = 171  # because 3 * 171 % 256 = 1

                reversed_data = bytes(
                    (( (byte ^ 0xAA) - ask) * mod_inv_3 ) % 256
                    for byte in data
                )

                with open(file_path, "wb") as f:
                    f.write(reversed_data)
                print()
                print_animated('The file has been successfully decrypted according to the encryption key provided by you.!!!.',255,0,0)
                print()
                main()
main()
