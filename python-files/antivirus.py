import os
import hashlib
import argparse

# База данных "вирусов" (в реальности это должна быть внешняя БД)
VIRUS_SIGNATURES = {
    "6f3c6b9c8c8a0f4e8b3c2c7a5f0e3b2a": "Test.Virus.1",
    "a1b2c3d4e5f6789012345678901234567": "Test.Virus.2"
}

SUSPICIOUS_PATTERNS = [
    b"malicious_string",
    b"eval(base64_decode",
    b"ransomware",
    b"<?php system("
]

def calculate_md5(file_path):
    """Вычисление MD5 хеша файла"""
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except IOError:
        return None

def scan_file_signatures(file_path):
    """Проверка по сигнатурам"""
    try:
        with open(file_path, "rb") as f:
            content = f.read()
            for pattern in SUSPICIOUS_PATTERNS:
                if pattern in content:
                    return True, f"Обнаружен подозрительный паттерн: {pattern}"
    except IOError:
        pass
    return False, ""

def scan_directory(path):
    """Сканирование директории"""
    results = []
    for root, dirs, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            print(f"Сканирую: {file_path}")
            
            # Проверка по хешу
            file_hash = calculate_md5(file_path)
            if file_hash and file_hash in VIRUS_SIGNATURES:
                results.append((file_path, VIRUS_SIGNATURES[file_hash], "KNOWN_VIRUS"))
            
            # Проверка по сигнатурам
            detected, reason = scan_file_signatures(file_path)
            if detected:
                results.append((file_path, reason, "SUSPICIOUS"))
    
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Простой антивирусный сканер')
    parser.add_argument('path', help='Путь для сканирования')
    args = parser.parse_args()

    print("Начинаем сканирование...")
    scan_results = scan_directory(args.path)
    
    print("\nРезультаты сканирования:")
    if scan_results:
        for result in scan_results:
            print(f"⚠️  Обнаружена угроза: {result[0]}")
            print(f"   Тип: {result[2]}")
            print(f"   Причина: {result[1]}")
            print()
    else:
        print("✅ Угроз не обнаружено")