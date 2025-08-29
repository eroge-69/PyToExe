import os
import json
import base64
import win32crypt
import sys

def get_key_and_print(local_state_path):
    try:
        if not os.path.exists(local_state_path):
            return
        with open(local_state_path, "r", encoding="utf-8", errors="ignore") as f:
            ls = json.load(f)
        key = base64.b64decode(ls["os_crypt"]["encrypted_key"])[5:]
        unprotected_key = win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]
        # A visszafejtett kulcsot hexadecimális formában írjuk ki, hogy a PowerShell könnyen beolvassa
        print(unprotected_key.hex())
    except Exception as e:
        # Hiba esetén a standard hibakimenetre írunk, hogy a PowerShell tudja, hogy baj van
        print(f"Error: {e}", file=sys.stderr)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        get_key_and_print(sys.argv[1])