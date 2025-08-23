import json
import base64
import hashlib
from cryptography.fernet import Fernet
import getpass

# Биржи, которые использует твой арбитражный бот
EXCHANGES = [
    "binance",
    "bybit",
    "bitget",
    "kucoinfutures",
    "gateio"
]

def generate_key(password: str) -> bytes:
    """Генерация ключа из пароля (sha256 → 32 байта → base64)."""
    return base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())

def encrypt_keys(keys: dict, password: str, filename: str):
    """Шифрование словаря с ключами и запись в файл."""
    key = generate_key(password)
    fernet = Fernet(key)
    data = json.dumps(keys, indent=2).encode()
    encrypted = fernet.encrypt(data)
    with open(filename, "wb") as f:
        f.write(encrypted)

def main():
    print("=== Генератор API-ключей для арбитражного бота ===\n")
    keys = {}

    for ex in EXCHANGES:
        print(f"\nБиржа: {ex.upper()}")
        apiKey = input("  Введите API Key: ").strip()
        secret = input("  Введите Secret Key: ").strip()
        passphrase = None
        # ⚠️ Bitget и KuCoin Futures требуют passphrase
        if ex in ["bitget", "kucoinfutures"]:
            passphrase = input("  Введите Passphrase (если есть, иначе Enter): ").strip()

        entry = {"apiKey": apiKey, "secret": secret}
        if passphrase:
            entry["password"] = passphrase  # ccxt использует поле "password" для passphrase

        keys[ex] = entry

    print("\nУкажите пароль для шифрования файла (его нужно будет вводить в приложении)")
    password = getpass.getpass("Пароль: ")
    confirm = getpass.getpass("Повторите пароль: ")

    if password != confirm:
        print("❌ Пароли не совпадают, попробуйте заново")
        return

    filename = "keys.enc"
    encrypt_keys(keys, password, filename)
    print(f"\n✅ Файл '{filename}' успешно создан и зашифрован.")

if __name__ == "__main__":
    main()
