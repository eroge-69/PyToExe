from cryptography.fernet import Fernet

def decrypt_file(encrypted_path, key_path):
    with open(key_path, 'rb') as key_file:
        key = key_file.read()
    f = Fernet(key)
    with open(encrypted_path, 'rb') as enc_file:
        encrypted = enc_file.read()
    decrypted = f.decrypt(encrypted)
    with open('decrypted_' + encrypted_path.replace('.enc', ''), 'wb') as dec_file:
        dec_file.write(decrypted)
    print("[+] File decrypted successfully.")

decrypt_file('test_document.txt.enc', 'encryption.key')
