import io
import os
import json
import datetime
import lz4.block

# ========================== NMS SaveTool Functions ==========================

def uint32(data: bytes) -> int:
    return int.from_bytes(data, byteorder='little', signed=False) & 0xffffffff

def byte4(data: int):
    return data.to_bytes(4, byteorder='little', signed=False)

def decompress(data):
    size = len(data)
    din = io.BytesIO(data)
    out = bytearray()
    while din.tell() < size:
        magic = uint32(din.read(4))
        if magic != 0xfeeda1e5:
            print("[!] Invalid Block — not a valid NMS .hg file")
            return bytes()
        compressedSize = uint32(din.read(4))
        uncompressedSize = uint32(din.read(4))
        din.seek(4, 1)
        out += lz4.block.decompress(din.read(compressedSize), uncompressed_size=uncompressedSize)
    return out

def compress(data):
    size = len(data)
    din = io.BytesIO(data)
    out = bytearray()
    while din.tell() < size:
        uncompressedSize = min([0x80000, size - din.tell()])
        block = lz4.block.compress(din.read(uncompressedSize), store_size=False)
        out += byte4(0xfeeda1e5)
        out += byte4(len(block))
        out += byte4(uncompressedSize)
        out += byte4(0)
        out += block
    return out

def readFile(path):
    with open(path, "rb") as f:
        return f.read()

def writeFile(path, data):
    with open(path, "wb") as f:
        f.write(data)

# ========================== HG Edit Functions ==========================

def load_edit_block(edits_path):
    with open(edits_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for key, value in data.items():
        if isinstance(value, dict) and not key.startswith('backup_'):
            return value
    print("[!] No edit block found in edits.json.")
    return None

def main():
    folder = os.getcwd()
    hg_file = next((f for f in os.listdir(folder) if f.endswith('.hg')), None)
    edits_path = os.path.join(folder, 'edits.json')

    if not hg_file or not os.path.isfile(edits_path):
        print("[!] .hg file or edits.json not found.")
        return

    hg_path = os.path.join(folder, hg_file)
    json_backup_path = hg_path.replace('.hg', '_backup.json')

    print(f"[+] Decompressing {hg_file}...")

    # Step 1: Decompress .hg file to JSON
    decompressed = decompress(readFile(hg_path))
    if not decompressed:
        print("[!] Decompression failed.")
        return

    with open(json_backup_path, 'w', encoding='utf-8') as f:
        f.write(decompressed.decode('utf-8'))

    print(f"[✓] Backup saved as: {json_backup_path}")

    # Step 2: Load the decompressed JSON
    try:
        with open(json_backup_path, 'r', encoding='utf-8') as f:
            hg_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"[!] JSON parsing failed: {e}")
        return

    if not isinstance(hg_data, list):
        print("[!] Decoded file does not contain a JSON list.")
        return

    # Step 3: Load edits.json
    edit_block = load_edit_block(edits_path)
    if not edit_block:
        return

    # Step 4: Find matching object to replace
    target_keys = set(edit_block.keys())
    match_index = None

    for idx, obj in enumerate(hg_data):
        if isinstance(obj, dict) and set(obj.keys()) == target_keys:
            match_index = idx
            break

    if match_index is None:
        print("[!] No matching block found in decompressed file.")
        return

    print(f"[~] Replacing block #{match_index} in decoded JSON...")

    hg_data[match_index] = edit_block

    # Step 5: Save modified JSON
    with open(json_backup_path, 'w', encoding='utf-8') as f:
        json.dump(hg_data, f, ensure_ascii=False, indent=2)

    # Step 6: Recompress back to .hg
    print(f"[+] Recompressing modified JSON to {hg_file}...")
    modified_raw = readFile(json_backup_path)
    compressed = compress(modified_raw)
    writeFile(hg_path, compressed)

    print(f"[✓] Successfully updated {hg_file}.")
    print("[✓] Done.")

if __name__ == '__main__':
    main()