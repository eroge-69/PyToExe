#!/usr/bin/env python3
"""
Hex Checksum Search Tool

Fast search for the first .hex file on C:\ drive whose Generic Loader-style word-sum checksum matches the one you specify.
Compatible with Python 3.4 on Windows XP 32-bit.
"""
import os
import sys


def parse_intel_hex(filepath):
    buf = bytearray()
    with open(filepath, 'r', encoding='utf-8-sig', errors='ignore') as f:
        for line in f:
            if not line.startswith(':'):
                continue
            line = line.strip()
            try:
                byte_count = int(line[1:3], 16)
                record_type = int(line[7:9], 16)
            except ValueError:
                continue
            if record_type != 0x00:
                continue
            data_str = line[9:9 + byte_count * 2]
            buf.extend(bytes.fromhex(data_str))
    return bytes(buf)


def parse_srec(filepath):
    buf = bytearray()
    with open(filepath, 'r', encoding='utf-8-sig', errors='ignore') as f:
        for line in f:
            s = line.strip()
            if not s.startswith('S') or len(s) < 4:
                continue
            rec = s[1]
            if rec not in ('1', '2', '3'):
                continue
            try:
                count = int(s[2:4], 16)
            except ValueError:
                continue
            addr_len = {'1':2, '2':3, '3':4}[rec]
            data_len = count - addr_len - 1
            start = 4 + addr_len * 2
            end = start + data_len * 2
            buf.extend(bytes.fromhex(s[start:end]))
    return bytes(buf)


def detect_and_extract(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8-sig', errors='ignore') as f:
            for line in f:
                l = line.strip()
                if not l:
                    continue
                if l.startswith('S'):
                    return parse_srec(filepath)
                if l.startswith(':'):
                    return parse_intel_hex(filepath)
                break
    except Exception:
        return b''
    return b''


def compute_word_sum_checksum(data):
    total = 0
    length = len(data)
    for i in range(0, length - (length % 2), 2):
        word = (data[i] << 8) | data[i+1]
        total = (total + word) & 0xFFFF
    if length % 2:
        total = (total + (data[-1] << 8)) & 0xFFFF
    return total


def main():
    # Clear screen on Windows XP
    os.system('cls')
    print('=' * 60)
    print('Hex Checksum Search Tool'.center(60))
    print('Search C:\\ drive for first matching .hex file'.center(60))
    print('=' * 60)

    # Scan for .hex files
    print('Scanning C:\\ for .hex files, please wait...')
    hex_files = []
    for root, dirs, files in os.walk('C:\\'):
        for fname in files:
            if fname.lower().endswith('.hex'):
                hex_files.append(os.path.join(root, fname))
    total = len(hex_files)
    if total == 0:
        print('\nNo .hex files found on C: drive.')
        return

    # Input checksum
    prompt = 'Found {0} .hex files. Enter checksum to search (hex, e.g. E918): '.format(total)
    chk_str = input(prompt).strip()
    try:
        target = int(chk_str, 16) & 0xFFFF
    except ValueError:
        print('Invalid checksum format.')
        return

    # Search
    print('\nStarting search...')
    bar_len = 40
    for idx, path in enumerate(hex_files, 1):
        percent = idx * 100 // total
        filled = idx * bar_len // total
        bar = '=' * filled + ' ' * (bar_len - filled)
        name = os.path.basename(path)
        status = '\r[{0}] {1:3d}% ({2}/{3}) Checking: {4}'.format(bar, percent, idx, total, name)
        # Clear and rewrite
        sys.stdout.write(status)
        sys.stdout.write(' ' * 10)  # padding to clear remnants
        sys.stdout.flush()

        data = detect_and_extract(path)
        if not data:
            continue
        if compute_word_sum_checksum(data) == target:
            print('\n\nMatch found: {0}'.format(path))
            return

    print('\n\nNo .hex file with checksum 0x{0:04X} was found.'.format(target))

if __name__ == '__main__':
    main()
