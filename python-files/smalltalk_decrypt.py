#!/usr/bin/env python3
"""
Python equivalent of the Smalltalk decryption code
Converts the Smalltalk snippet to decrypt the secret message
"""

import hashlib
import base64
import argparse
import sys
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

def decrypt_message(bdk, secure_number, encrypted_message_b64):
    # Create encryption key by hashing the concatenated string with SHA256
    key_string = bdk + secure_number
    encryption_key = hashlib.sha256(key_string.encode('utf-8')).digest()
    
    # Initialize IV (16 zeros for AES-256-CBC)
    iv = b'\x00' * 16
    
    # Decode base64 message
    encrypted_message = base64.b64decode(encrypted_message_b64)
    
    # Set up AES-256-CBC cipher
    cipher = Cipher(
        algorithms.AES(encryption_key),
        modes.CBC(iv),
        backend=default_backend()
    )
    
    # Decrypt the message
    decryptor = cipher.decryptor()
    decrypted_padded = decryptor.update(encrypted_message) + decryptor.finalize()
    
    # Remove PKCS7 padding
    padding_length = decrypted_padded[-1]
    decrypted_message = decrypted_padded[:-padding_length]
    
    # Convert to string
    return decrypted_message.decode('utf-8')

def main():
    parser = argparse.ArgumentParser(description='Decrypt secret message using BDK and secure number')
    parser.add_argument('bdk', help='BDK (Base Derivation Key) - first part of the encryption key')
    parser.add_argument('secure_number', help='Secure number - second part of the encryption key')
    parser.add_argument('encrypted_message', help='Base64 encoded encrypted message to decrypt')
    
    args = parser.parse_args()
    
    try:
        result = decrypt_message(args.bdk, args.secure_number, args.encrypted_message)
        print("Decrypted message:")
        print(result)
    except Exception as e:
        print(f"Error during decryption: {e}")
        return 1
    return 0

if __name__ == "__main__":
    exit(main())