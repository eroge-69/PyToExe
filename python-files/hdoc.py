import io
import os
import json
import datetime
import lz4.block

# De- and Re-Compression

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
            print("Valid .hg file not found!")
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
  fin = open(path, "rb")
  data = fin.read()
  fin.close()
  return data

def writeFile(path, data):
  fout = open(path, "wb")
  fout.write(data)
  fout.close()

# Replacement Logic

def replace_nested_editblock(data, edit_block):

    parent_keys = list(edit_block.keys())
    if not parent_keys:
        print("[x] EditBlock is empty.")
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
                        print(f"Found parent key '{key}' — replacing nested subkeys...")
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

# Primary Script

def load_edit_block(edits_path):
    with open(edits_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if "EditBlock" not in data or not isinstance(data["EditBlock"], dict):
        print("[x] edits.json must contain a top-level 'EditBlock' dictionary.")
        return None
    return data["EditBlock"]

def main():
    folder = os.getcwd()
    hg_file = next((f for f in os.listdir(folder) if f.endswith('.hg')), None)
    edits_path = os.path.join(folder, 'edits.json')

    if not hg_file or not os.path.isfile(edits_path):
        print("[x] .hg file or edits.json not found!")
        return

    hg_path = os.path.join(folder, hg_file)
    json_backup_path = hg_path.replace('.hg', '_backup.json')

    print(f"[+] Decompressing {hg_file}...")

    # 1) Decompress .hg file
    decompressed = decompress(readFile(hg_path))
    if not decompressed:
        print("[x] Decompression unsuccessful.")
        return

    # 2) Save original JSON backup prior to edits
    try:
        original_data = json.loads(decompressed.decode('utf-8'))
    except json.JSONDecodeError as e:
        print(f"[x] Failed to parse JSON from decompressed .hg: {e}")
        return

    with open(json_backup_path, 'w', encoding='utf-8') as f:
        json.dump(original_data, f, ensure_ascii=False, indent=2)
    print(f"[✓] Backup saved as: {json_backup_path}")

    # 3) Load edits
    edit_block = load_edit_block(edits_path)
    if not edit_block:
        return

    # 4) Apply edits to a fresh copy
    hg_data = json.loads(decompressed.decode('utf-8'))
    replace_nested_editblock(hg_data, edit_block)

    # 5) Recompress edited copy
    print("[+] Recompressing to .hg...")
    json_bytes = json.dumps(hg_data, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    compressed = compress(json_bytes)
    writeFile(hg_path, compressed)

    print(f"[✓] Successfully updated {hg_file}.")
    print("[✓] Done.")

if __name__ == '__main__':
    main()