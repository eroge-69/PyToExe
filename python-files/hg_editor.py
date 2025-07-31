import io
import os
import json
import datetime
import lz4.block

# ========================= NMS Compression Utilities =========================

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
            print("[!] Invalid block — not a valid NMS .hg file")
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

# ========================= Edit Block Replacement Logic =========================

def replace_nested_editblock(data, edit_block):
    """
    Replace keys in nested structure like:
    {
      "<h0": {
        "Pk4": "Save1",
        "Lg8": 600000
      }
    }
    - Only replaces first match for parent key
    - Then, only first match for each subkey after that point
    """
    parent_keys = list(edit_block.keys())
    if not parent_keys:
        print("[!] EditBlock is empty.")
        return

    parent_key_found = False
    subkey_replaced = set()

    def walk(obj):
        nonlocal parent_key_found, subkey_replaced

        if isinstance(obj, dict):
            for key, value in obj.items():
                if not parent_key_found and key in edit_block:
                    nested_patch = edit_block[key]
                    if isinstance(obj[key], dict) and isinstance(nested_patch, dict):
                        print(f"[~] Found first parent key '{key}' — replacing nested subkeys...")
                        parent_key_found = True
                        for subkey in nested_patch:
                            if subkey in obj[key] and subkey not in subkey_replaced:
                                obj[key][subkey] = nested_patch[subkey]
                                subkey_replaced.add(subkey)
                                print(f"    ↳ Replaced '{subkey}' in '{key}'")
                    continue

                # Continue walking deeper
                walk(value)

        elif isinstance(obj, list):
            for item in obj:
                walk(item)

    walk(data)

# ========================= Main Script =========================

def load_edit_block(edits_path):
    with open(edits_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if "EditBlock" not in data or not isinstance(data["EditBlock"], dict):
        print("[!] edits.json must contain a top-level 'EditBlock' dictionary.")
        return None
    return data["EditBlock"]

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

    # Step 1: Decompress .hg
    decompressed = decompress(readFile(hg_path))
    if not decompressed:
        print("[!] Decompression failed.")
        return

    # Step 2: Save JSON backup
    with open(json_backup_path, 'w', encoding='utf-8') as f:
        f.write(decompressed.decode('utf-8'))
    print(f"[✓] Backup saved as: {json_backup_path}")

    # Step 3: Load JSON data
    try:
        with open(json_backup_path, 'r', encoding='utf-8') as f:
            hg_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"[!] JSON parsing failed: {e}")
        return

    # Step 4: Load edits
    edit_block = load_edit_block(edits_path)
    if not edit_block:
        return

    # Step 5: Replace using nested-aware logic
    replace_nested_editblock(hg_data, edit_block)

    # Step 6: Save modified JSON back
    with open(json_backup_path, 'w', encoding='utf-8') as f:
        json.dump(hg_data, f, ensure_ascii=False, indent=2)

    # Step 7: Recompress
    print("[+] Recompressing to .hg...")
    modified_raw = readFile(json_backup_path)
    compressed = compress(modified_raw)
    writeFile(hg_path, compressed)

    print(f"[✓] Successfully updated {hg_file}.")
    print("[✓] Done.")

if __name__ == '__main__':
    main()