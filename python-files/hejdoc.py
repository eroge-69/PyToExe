import io
import os
import json
import lz4.block

# ~~~De-Compressor Utilities~~~ 

def uint32(data: bytes) -> int:
    return int.from_bytes(data, byteorder='little', signed=False)

def byte4(data: int) -> bytes:
    return data.to_bytes(4, byteorder='little', signed=False)

def decompress(data):
    """Decompress NMS .hg file data from lz4 format."""
    size = len(data)
    din = io.BytesIO(data)
    out = bytearray()
    while din.tell() < size:
        magic = uint32(din.read(4))
        if magic != 0xfeeda1e5:
            print("[x] Missing a valid NMS .hg file")
            return bytes()
        compressedSize = uint32(din.read(4))
        uncompressedSize = uint32(din.read(4))
        din.seek(4, 1)
        out += lz4.block.decompress(
            din.read(compressedSize),
            uncompressed_size=uncompressedSize
        )
    return out

def readFile(path):
    with open(path, "rb") as f:
        return f.read()

def writeFile(path, data):
    with open(path, "wb") as f:
        f.write(data)

# ~~~Editing Block Logic~~~

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
        print("[x] EditBlock contains no data.")
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
                        print(f"[~] Found parent key '{key}' and replacing nested subkeys...")
                        parent_key_found = True
                        for subkey in nested_patch:
                            if subkey in obj[key] and subkey not in subkey_replaced:
                                obj[key][subkey] = nested_patch[subkey]
                                subkey_replaced.add(subkey)
                                print(f"    ↳ Replaced '{subkey}' in '{key}'")
                    continue
                walk(value)
        elif isinstance(obj, list):
            for item in obj:
                walk(item)
    walk(data)

# ~~~Editing Block Loader~~~

def load_edit_block(edits_path):
    with open(edits_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if "EditBlock" not in data or not isinstance(data["EditBlock"], dict):
        print("[x] edits.json must contain a top-level 'EditBlock' dictionary.")
        return None
    return data["EditBlock"]

# Backup & Editing Logic

def main():
    folder = os.getcwd()
    hg_file = next((f for f in os.listdir(folder) if f.endswith('.hg')), None)
    edits_path = os.path.join(folder, 'edits.json')

    if not hg_file:
        print("[x] .hg file not found in folder.")
        return
    if not os.path.isfile(edits_path):
        print("[x] edits.json not found in folder.")
        return

    hg_path = os.path.join(folder, hg_file)
    backup_path = hg_path.replace('.hg', '_backup.json')

    print(f"[+] Decoding {hg_file}...")

    decompressed_bytes = decompress(readFile(hg_path))
    if not decompressed_bytes:
        print("[x] Decodong failed.")
        return

    try:
        decompressed_text = decompressed_bytes.decode('utf-8')
        original_data = json.loads(decompressed_text)
    except json.JSONDecodeError as e:
        print(f"[x] Failed to parse JSON from decoded savefile: {e}")
        return

    # 1) Save unedited backup
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(decompressed_text)
    print(f"[✓] Backup saved as {backup_path}")

    # 2) Load edits
    edit_block = load_edit_block(edits_path)
    if not edit_block:
        return

    # 3) Apply edits
    hg_data = json.loads(decompressed_text)
    replace_nested_editblock(hg_data, edit_block)

    # 4) Save edited file as .hg
    print("[+] Saving edited file as .hg...")
    edited_text = json.dumps(hg_data, ensure_ascii=False, separators=(',', ':'))
    with open(hg_path, 'w', encoding='utf-8') as f:
        f.write(edited_text)

    print(f"[✓] {hg_file} edited successfully.")
    print("[✓] Program Complete!")

# ~~~Entry Point~~~

if __name__ == '__main__':
    main()