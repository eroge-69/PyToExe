#!/usr/bin/env python3
import base64
import time
import os
import random
import socket

# === Obfuscated C2 beacon ===
def xor(data, key):
    return ''.join(chr(c ^ key) for c in data)

# Encoded "http://malicious-backdoor.ru"
encoded_c2 = [0x3d, 0x3d, 0x21, 0x2e, 0x2c, 0x3f, 0x3f, 0x33, 0x66, 0x3a, 0x3b, 0x3a, 0x39, 0x26, 0x20, 0x3a, 0x39, 0x26, 0x25, 0x35, 0x31, 0x3a, 0x3e, 0x26]
c2 = xor(encoded_c2, 0x55)

# === Fake mutex (suspicious string) ===
MUTEX = "Global\\ReallySuspiciousMutex"

# === Fake registry persistence key ===
REG_KEY = r"HKCU\Software\Microsoft\Windows\CurrentVersion\Run"
REG_VALUE = "SystemUpdater"
REG_COMMAND = "client.dll"

# === Fake YARA bait ===
YARA_RULE = "rule backdoor_rat : njrat darkcomet"

def simulate_beacon():
    print(f"[*] Beaconing to C2: {c2}")
    time.sleep(1.2)

def drop_payload():
    # Empty but realistic PE stub (just MZ header)
    payload = base64.b64decode("TVqQAAMAAAAEAAAA//8AALgAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
    fname = "client.dll"
    with open(fname, "wb") as f:
        f.write(payload)
    print(f"[+] Dropped payload: ./{fname}")

def show_registry_key():
    print(f"[*] Registry Persistence (simulated):")
    print(f"    reg add {REG_KEY} /v {REG_VALUE} /t REG_SZ /d \"{REG_COMMAND}\"")

def main():
    print(f"[=] Mutex created: {MUTEX}")
    simulate_beacon()
    drop_payload()
    show_registry_key()
    print(f"[=] Suspicious YARA string: {YARA_RULE}")
    print("[!] Execution complete.")

if __name__ == "__main__":
    main()