#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

ZW0 = '\u200b'   # bit 0
ZW1 = '\u200c'   # bit 1
HEADER = '\u200d\u2060' * 4
PREFIX = b'STG1'
MODE_PLAIN = 0x00
MODE_ENCRYPTED = 0x01

def decode_zero_width(zw: str, count: int) -> str:
    if len(zw) < count:
        raise ValueError("Недостаточно скрытых данных.")
    out_bits = []
    for ch in zw[:count]:
        if ch == ZW0:
            out_bits.append('0')
        elif ch == ZW1:
            out_bits.append('1')
        else:
            raise ValueError("Посторонний символ в скрытых данных.")
    return ''.join(out_bits)

def bits_to_bytes(bits: str) -> bytes:
    if len(bits) % 8 != 0:
        raise ValueError("Битов не кратно 8.")
    return bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))

def main(path: str):
    text = open(path, 'r', encoding='utf-8', errors='strict').read()
    # Счётчик zero-width символов
    zw_set = {ZW0, ZW1, '\u200d', '\u2060'}
    count_zw = sum(ch in zw_set for ch in text)
    print(f"Zero-width символов найдено: {count_zw}")

    idx = text.rfind(HEADER)
    if idx == -1:
        print("HEADER не найден — либо контейнера нет, либо использована другая схема.")
        return

    print("HEADER найден. Пытаюсь извлечь контейнерные метаданные...")
    tail = text[idx + len(HEADER):]
    try:
        length_bits = decode_zero_width(tail, 32)
        length = int(length_bits, 2)
        data_bits = decode_zero_width(tail[32:], length * 8)
        container = bits_to_bytes(data_bits)
    except Exception as e:
        print(f"Ошибка декодирования битов: {e}")
        return

    print(f"Длина контейнера: {len(container)} байт (ожидалась {length})")

    if not container.startswith(PREFIX):
        print("Префикс STG1 не найден — формат не соответствует текущему инструменту.")
        return

    if len(container) == len(PREFIX):
        print("Пустой контейнер после префикса.")
        return

    mode = container[len(PREFIX)]
    if mode == MODE_PLAIN:
        print("Режим: без шифрования (PLAIN). Данные можно прочитать сразу после байта режима.")
    elif mode == MODE_ENCRYPTED:
        print("Режим: зашифровано (ENCRYPTED). Нужен пароль для расшифровки.")
    else:
        print("Похоже на legacy-формат (без байта режима) или неизвестный режим.")
        print("Вероятно требуется пароль (legacy: всегда зашифровано).")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Использование: {sys.argv[0]} path/to/text.txt")
        sys.exit(2)
    try:
        main(sys.argv[1])
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)