import string
from itertools import product

def excel_password_hash(password: str) -> int:
    password = password[:15]
    hash_value = 0
    for i, char in enumerate(password):
        char_code = ord(char)
        hash_value ^= (char_code << (i + 1))
    return hash_value & 0xFFFF

def main():
    target_hash_hex = "CC7B"
    target_hash = int(target_hash_hex, 16)
    charset = string.ascii_letters + string.digits
    max_len = 5

    print(f"Поиск пароля с Excel-хешем: 0x{target_hash:04X}...")

    for length in range(1, max_len + 1):
        for chars in product(charset, repeat=length):
            pwd = ''.join(chars)
            if excel_password_hash(pwd) == target_hash:
                print(f"Найден пароль: {pwd}")
                return

    print("Пароль не найден.")

if _name_ == "_main_":
    main()