#!/usr/bin/env python3
import os
import sys
import time
import psutil
import tempfile
from pathlib import Path
import dpkt

# ==============================
# Конфигурация
# ==============================
PCAP_EXTENSIONS = {'.pcap', '.cap'}
SAFE_MODE = True

# ==============================
# Функции
# ==============================

def get_boot_time_unix():
    return psutil.boot_time()

def is_time_fixed(packet_ts, boot_time, tolerance_sec=3600):
    if packet_ts > boot_time:
        return True

    return False

def fix_pcap_file(input_path: Path, boot_time: float) -> bool:
    input_path = Path(input_path)
    print(f"[ ] Проверка файла: {input_path.name}")

    # Читаем первый пакет для проверки времени
    try:
        with open(input_path, 'rb') as f:
            pcap = dpkt.pcap.Reader(f)
            try:
                ts, buf = next(pcap)
            except StopIteration:
                print(f"[!] Файл пуст: {input_path.name}")
                return False

            if is_time_fixed(ts, boot_time):
                print(f"Время уже исправлено: {input_path.name}")
                return False

    except Exception as e:
        print(f"[!] Ошибка при чтении {input_path.name}: {e}")
        return False

    print(f"Исправление времени: {input_path.name}")

    # Создаём временный файл
    temp_fd, temp_path = tempfile.mkstemp(suffix='.pcap.tmp', dir=input_path.parent)
    os.close(temp_fd)

    success = False
    try:
        with open(input_path, 'rb') as fin, open(temp_path, 'wb') as fout:
            pcap_in = dpkt.pcap.Reader(fin)
            pcap_out = dpkt.pcap.Writer(fout, linktype=pcap_in.datalink())

            for ts, buf in pcap_in:
                new_ts = boot_time + ts
                pcap_out.writepkt(buf, new_ts)

        success = True

    except Exception as e:
        print(f"[!] Ошибка при записи: {e}")
        try:
            os.unlink(temp_path)
        except:
            pass
        return False

    if success and SAFE_MODE:
        try:
            input_path.unlink()
            os.rename(temp_path, input_path)
            print(f"[✓] Успешно заменён: {input_path.name}")
            return True
        except Exception as e:
            print(f"[!] Не удалось заменить файл: {e}")
            return False

    return False

def process_directory(directory: str):
    directory = Path(directory)
    if not directory.is_dir():
        print(f"[-] Это не директория: {directory}")
        return

    boot_time = get_boot_time_unix()
    print(f"Boot time: {time.ctime(boot_time)} (Unix: {boot_time})")
    print(f"[+] Поиск pcap-файлов в: {directory.resolve()}")

    pcap_files = [
        f for f in directory.iterdir()
        if f.is_file() and f.suffix.lower() in PCAP_EXTENSIONS
    ]

    if not pcap_files:
        print("[!] Нет pcap-файлов для обработки.")
        return

    modified_count = 0
    for pcap_file in pcap_files:
        if fix_pcap_file(pcap_file, boot_time):
            modified_count += 1

    print(f"\n Готово! Обработано файлов: {modified_count} из {len(pcap_files)}")

# ==============================
# Запуск
# ==============================

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Использование: python Real_Timer.py <путь_к_директории>")
        sys.exit(1)

    target_dir = sys.argv[1]
    process_directory(target_dir)