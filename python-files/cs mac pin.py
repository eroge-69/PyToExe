import tkinter as tk
from tkinter import messagebox
from binascii import unhexlify, hexlify

def derive_mac_key(key: bytes) -> bytes:
    dwords = [int.from_bytes(key[i:i+4], 'big') for i in range(0, 16, 4)]
    result = dwords[0] ^ dwords[1] ^ dwords[2] ^ dwords[3]
    return result.to_bytes(4, 'big')

def derive_cs_key(key: bytes) -> bytes:
    result = bytearray(7)
    for i in range(16):
        result[i % 7] ^= key[i]
    return bytes(result)

def derive_pin_key(key: bytes) -> bytes:
    return bytes([
        key[0] ^ key[2] ^ key[4] ^ key[6] ^ key[8] ^ key[10] ^ key[12] ^ key[14],
        key[1] ^ key[3] ^ key[5] ^ key[7] ^ key[9] ^ key[11] ^ key[13] ^ key[15]
    ])

def xor_decrypt(data: bytes, xor_key: bytes) -> bytes:
    return bytes(d ^ xor_key[i % len(xor_key)] for i, d in enumerate(data))

def decrypt():
    key_input = key_entry.get().strip()
    data_input = data_entry.get().strip().upper()

    if len(key_input) != 32 or len(data_input) != 26:
        messagebox.showerror("Input Error", "Key must be 32 hex chars, data must be 26 hex chars.")
        return

    try:
        key = unhexlify(key_input)
        mac2 = unhexlify(data_input[0:4])
        cs_enc = unhexlify(data_input[4:18])
        mac1 = unhexlify(data_input[18:22])
        pin_enc = unhexlify(data_input[22:26])
        mac_enc = mac1 + mac2

        cs_dec = xor_decrypt(cs_enc, derive_cs_key(key))
        mac_dec = xor_decrypt(mac_enc, derive_mac_key(key))
        pin_dec = xor_decrypt(pin_enc, derive_pin_key(key))

        cs_var.set(hexlify(cs_dec).upper().decode())
        mac_var.set(hexlify(mac_dec).upper().decode())
        pin_var.set(str(int.from_bytes(pin_dec, 'big')))

    except Exception as e:
        messagebox.showerror("Error", f"Decryption failed:\n{str(e)}")

# GUI layout
root = tk.Tk()
root.title("EDC17 MAC/CS/PIN Decryptor")

tk.Label(root, text="Decryption Key (32 hex chars):").grid(row=0, column=0, sticky="e")
key_entry = tk.Entry(root, width=40)
key_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(root, text="Encrypted String (26 hex chars):").grid(row=1, column=0, sticky="e")
data_entry = tk.Entry(root, width=40)
data_entry.grid(row=1, column=1, padx=5, pady=5)

tk.Button(root, text="Decrypt", command=decrypt).grid(row=2, column=0, columnspan=2, pady=10)

cs_var = tk.StringVar()
mac_var = tk.StringVar()
pin_var = tk.StringVar()

tk.Label(root, text="CS:").grid(row=3, column=0, sticky="e")
tk.Entry(root, textvariable=cs_var, state="readonly", width=40).grid(row=3, column=1)

tk.Label(root, text="MAC:").grid(row=4, column=0, sticky="e")
tk.Entry(root, textvariable=mac_var, state="readonly", width=40).grid(row=4, column=1)

tk.Label(root, text="PIN:").grid(row=5, column=0, sticky="e")
tk.Entry(root, textvariable=pin_var, state="readonly", width=40).grid(row=5, column=1)

root.mainloop()
