# Console version adapted for non-interactive (sandboxed) environments
# Use predefined variables instead of input() for I/O-less environments

import os
import itertools
import string
import logging
from datetime import datetime
import subprocess

# === CONFIGURATION START ===
# Set paths here manually since input() is not supported in some environments
RAR_FILES = ["example1.rar", "example2.rar"]  # Replace with actual paths
OUTPUT_DIRECTORY = "./output"                 # Replace with actual extraction path
WORDLIST_PATH = "passwords.txt"              # Set to None to use generated passwords
GENERATE_MAX_LENGTH = 4                       # Used only if WORDLIST_PATH is None
# === CONFIGURATION END ===

def setup_logging():
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"rar_recovery_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    logging.basicConfig(filename=log_file, level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s", encoding='utf-8')

def load_wordlist(path):
    if path and os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    return None

def generate_passwords(max_length=4):
    characters = string.ascii_letters + string.digits
    for length in range(1, max_length + 1):
        for password in itertools.product(characters, repeat=length):
            yield ''.join(password)

def try_passwords_unrar(rar_path, output_path, passwords):
    for i, password in enumerate(passwords, 1):
        try:
            result = subprocess.run([
                "unrar", "x", f"-p{password}", "-y", rar_path, output_path
            ], capture_output=True, text=True)

            if "All OK" in result.stdout or "OK" in result.stdout:
                print(f"✅ Пароль найден: {password}")
                logging.info(f"Успешное извлечение {rar_path} с паролем: {password}")
                return True
        except Exception as e:
            logging.debug(f"Ошибка при использовании пароля {password} для {rar_path}: {e}")

        if i % 100 == 0:
            print(f"Попробовано паролей: {i}")

    print(f"❌ Пароль не найден для {rar_path}")
    logging.warning(f"Пароль не найден для {rar_path}")
    return False

def main():
    setup_logging()

    rar_files = [f for f in RAR_FILES if os.path.exists(f)]
    if not rar_files:
        print("❌ Не найдены указанные RAR-файлы. Проверьте пути в конфигурации.")
        return

    if not os.path.exists(OUTPUT_DIRECTORY):
        print("❌ Указанная папка для извлечения не существует. Проверьте OUTPUT_DIRECTORY.")
        return

    wordlist = load_wordlist(WORDLIST_PATH)
    if wordlist:
        passwords = wordlist
    else:
        passwords = generate_passwords(GENERATE_MAX_LENGTH)

    for rar in rar_files:
        try_passwords_unrar(rar, OUTPUT_DIRECTORY, passwords)

    print("\n✅ Завершено.")

if __name__ == "__main__":
    main()
