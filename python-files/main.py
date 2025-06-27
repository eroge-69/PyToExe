#!/usr/bin/env python3
"""
decrypt_rbx_alt_manager.py

Decrypts RBX Alt Manager files by:
 1. Hashing your password with SHA-512 (UTF-8) – matching Sodium.CryptoHash.Hash(string)
 2. Argon2i-Moderate PBKDF to derive a 32-byte key
 3. XSalsa20-Poly1305 decryption via SecretBox
"""

import sys
import argparse
import hashlib

from nacl.pwhash.argon2i import kdf, OPSLIMIT_MODERATE, MEMLIMIT_MODERATE
from nacl.secret import SecretBox
from nacl.exceptions import CryptoError

RAM_HEADER = bytes([
    82,111, 98,108,111,120,32, 65, 99,  99,111,117,110,116,32, 77,
     97,110, 97,103,101,114,32, 99,114,101, 97,116,101,100,32, 98,
     121,32,105, 99, 51,119, 48,108,102, 50, 50,32, 64, 32,103,
    105,116,104,117, 98, 46, 99,111,109,32, 46, 46, 46, 46, 46,
     46, 46
])

def decrypt_bytes(enc: bytes, password: str) -> bytes:
    # 1) Pre-hash: SHA-512 over UTF-8 bytes
    pw_hash = hashlib.sha512(password.encode('utf-8')).digest()

    # 2) Verify header
    if not enc.startswith(RAM_HEADER):
        raise ValueError("Invalid RBX Alt Manager header.")
    off = len(RAM_HEADER)

    # 3) Parse salt (16), nonce (24), ciphertext
    salt = enc[off:off+16];   off += 16
    nonce = enc[off:off+24];  off += 24
    ciphertext = enc[off:]

    # 4) Derive 32-byte key with Argon2i-Moderate
    key = kdf(SecretBox.KEY_SIZE, pw_hash, salt, OPSLIMIT_MODERATE, MEMLIMIT_MODERATE)

    # 5) Decrypt
    box = SecretBox(key)
    try:
        return box.decrypt(ciphertext, nonce)
    except CryptoError:
        raise ValueError("Bad password or corrupted file.")

def main():
    p = argparse.ArgumentParser(description="Decrypt RBX Alt Manager file")
    p.add_argument("input",  help="Encrypted file path")
    p.add_argument("output", help="Where to write decrypted output")
    p.add_argument("password", help="Your clear-text password")
    args = p.parse_args()

    blob = open(args.input, "rb").read()
    try:
        pt = decrypt_bytes(blob, args.password)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    with open(args.output, "wb") as f:
        f.write(pt)
    print(f"✅ Decrypted! Wrote {len(pt)} bytes to {args.output}")

if __name__ == "__main__":
    main()
