#!/usr/bin/env python3
import sys
import os
import zlib
import hashlib
import hmac
import getpass
from Crypto.Cipher import AES
from Crypto.Util import Counter

# ---------- Utilities ----------

def sha1024(data: bytes) -> bytes:
    h1 = hashlib.sha512(data).digest()
    h2 = hashlib.sha512(h1).digest()
    return h1 + h2

def hash86(data: bytes) -> bytes:
    if len(data) < 16:
        key = data.ljust(16, b'\x00')
    else:
        key = data[:16]
    x = bytearray(data)
    for i in range(6):
        hm = hmac.new(key, bytes(x), hashlib.sha256).digest()
        for j in range(len(x)):
            x[j] ^= hm[j % len(hm)] ^ (i * 31 & 0xFF)
        r = i % len(x)
        if r:
            x = x[r:] + x[:r]
        key = hashlib.sha256(key + hm).digest()[:16]
    final = hashlib.sha512(bytes(x)).digest() + hashlib.sha512(bytes(x[::-1])).digest()
    return final

def derive_aes256_keys_from_1024(key1024: bytes):
    if len(key1024) != 128:
        raise ValueError("Expected 128 bytes for 1024-bit key material")
    return [key1024[i*32:(i+1)*32] for i in range(4)]

def aes256_ctr(data: bytes, key: bytes, nonce: bytes) -> bytes:
    iv_int = int.from_bytes(nonce, byteorder='big')
    ctr = Counter.new(128, initial_value=iv_int)
    cipher = AES.new(key, AES.MODE_CTR, counter=ctr)
    return cipher.encrypt(data)

def swap_bits_6_7_in_byte(b: int) -> int:
    i, j = 5, 6
    bit_i = (b >> i) & 1
    bit_j = (b >> j) & 1
    if bit_i != bit_j:
        b ^= (1 << i) | (1 << j)
    return b

def swap_bits_in_bytes(data: bytes) -> bytes:
    return bytes(swap_bits_6_7_in_byte(b) for b in data)

def generate_permutation(n: int, key_bytes: bytes) -> list:
    perm = list(range(n))
    stream = bytearray()
    counter = 0
    while len(stream) < n * 4:
        ctr_bytes = counter.to_bytes(8, 'big')
        stream += hmac.new(key_bytes, ctr_bytes, hashlib.sha256).digest()
        counter += 1
    idx = 0
    for i in range(n-1, 0, -1):
        r = int.from_bytes(stream[idx:idx+4], 'big')
        idx += 4
        j = r % (i+1)
        perm[i], perm[j] = perm[j], perm[i]
    return perm

def permute_bytes(data: bytes, key_bytes: bytes) -> bytes:
    perm = generate_permutation(len(data), key_bytes)
    out = bytearray(len(data))
    for i, p in enumerate(perm):
        out[i] = data[p]
    return bytes(out)

def inverse_permutation(perm: list) -> list:
    inv = [0]*len(perm)
    for i, p in enumerate(perm):
        inv[p] = i
    return inv

def unpermute_bytes(data: bytes, key_bytes: bytes) -> bytes:
    perm = generate_permutation(len(data), key_bytes)
    inv = inverse_permutation(perm)
    out = bytearray(len(data))
    for i, p in enumerate(inv):
        out[i] = data[p]
    return bytes(out)

# ---------- Pipeline ----------

def encrypt_file(in_bytes: bytes, passphrase: str) -> bytes:
    compressed = zlib.compress(in_bytes)
    sha_in = sha1024(passphrase.encode('utf-8'))
    scrambled = hash86(sha_in)
    keys = derive_aes256_keys_from_1024(scrambled)
    nonce = hashlib.sha256(scrambled + b'nonce').digest()[:16]
    data = compressed
    for k in keys:
        data = aes256_ctr(data, k, nonce)
    data = swap_bits_in_bytes(data)
    data = permute_bytes(data, scrambled)
    header = b'A1024v1' + len(in_bytes).to_bytes(8, 'big') + hashlib.sha256(scrambled).digest()
    return header + data

def decrypt_file(enc: bytes, passphrase: str) -> bytes:
    if len(enc) < 47:
        raise ValueError("Invalid file")
    if enc[:7] != b'A1024v1':
        raise ValueError("Not a .kip file")
    orig_len = int.from_bytes(enc[7:15], 'big')
    stored_sha = enc[15:47]
    payload = enc[47:]
    sha_in = sha1024(passphrase.encode('utf-8'))
    scrambled = hash86(sha_in)
    if hashlib.sha256(scrambled).digest() != stored_sha:
        raise ValueError("Wrong key")
    data = unpermute_bytes(payload, scrambled)
    data = swap_bits_in_bytes(data)
    keys = derive_aes256_keys_from_1024(scrambled)
    nonce = hashlib.sha256(scrambled + b'nonce').digest()[:16]
    for k in reversed(keys):
        data = aes256_ctr(data, k, nonce)
    decompressed = zlib.decompress(data)
    if len(decompressed) != orig_len:
        raise ValueError("File corrupted or wrong key")
    return decompressed

# ---------- Drag-and-drop handler ----------

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Drag and drop a file onto this script to encrypt/decrypt.")
        sys.exit(1)

    filepath = sys.argv[1]
    if not os.path.isfile(filepath):
        print("Not a valid file.")
        sys.exit(1)

    with open(filepath, 'rb') as f:
        file_data = f.read()

    if filepath.lower().endswith(".kip"):
        print(f"Decrypting {os.path.basename(filepath)}...")
        key = getpass.getpass("Enter decryption key: ")
        try:
            decrypted = decrypt_file(file_data, key)
            outpath = filepath[:-4]  # remove .kip
            with open(outpath, 'wb') as f:
                f.write(decrypted)
            print(f"Decrypted to {outpath}")
        except Exception as e:
            print(f"Decryption failed: {e}")
    else:
        print(f"Encrypting {os.path.basename(filepath)}...")
        key = getpass.getpass("Enter encryption key: ")
        encrypted = encrypt_file(file_data, key)
        outpath = filepath + ".kip"
        with open(outpath, 'wb') as f:
            f.write(encrypted)
        print(f"Encrypted to {outpath}")
