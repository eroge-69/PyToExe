import io
import os
import json
import lz4.block

# =================== Compression Utilities ===================

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
            print("[!] Invalid block — not a valid NMS .hg file")
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

# =================== Edit Block Logic ===================

def replace_nested_editblock(data, edit_block, resume_path=None):
    """
    Replace keys in nested structure, starting after `resume_path` if provided.
    Returns the path where the last parent key was found.
    """
    parent_keys = list(edit_block.keys())
    if not parent_keys:
        print("[!] EditBlock is empty.")
        return resume_path

    parent_key_found = False
    subkey_replaced = set()
    last_match_path = None

    def walk(obj, path=()):
        nonlocal parent_key_found, subkey_replaced, last_match_path, resume_path

        # Skip everything until we reach resume_path (if provided)
        if resume_path and path < resume_path:
            return

        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = path + (key,)
                if not parent_key_found and key in edit_block:
                    nested_patch = edit_block[key]
                    if isinstance(obj[key], dict) and isinstance(nested_patch, dict):
                        print(f"[~] Found parent key '{key}' — replacing nested subkeys...")
                        parent_key_found = True
                        last_match_path = current_path
                        for subkey in nested_patch:
                            if subkey in obj[key] and subkey not in subkey_replaced:
                                obj[key][subkey] = nested_patch[subkey]
                                subkey_replaced.add(subkey)
                                print(f"    ↳ Replaced '{subkey}' in '{key}'")
                    continue
                walk(value, current_path)
        elif isinstance(obj, list):
            for idx, item in enumerate(obj):
                walk(item, path + (idx,))

    walk(data)
    return last_match_path

# =================== Edit Loader ===================

def load_edit_blocks(edits_path):
    with open(edits_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if "EditBlocks" not in data or not isinstance(data["EditBlocks"], list):
        print("[!] edits.json must contain a top-level 'EditBlocks' list.")
        return None
    return data["EditBlocks"]

# =================== Combined Backup + Edit ===================

def main():
    folder = os.getcwd()
    hg_file = next((f for f in os.listdir(folder) if f.endswith('.hg')), None)
    edits_path = os.path.join(folder, 'edits.json')

    if not hg_file:
        print("[!] No .hg file found in current folder.")
        return
    if not os.path.isfile(edits_path):
        print("[!] edits.json not found.")
        return

    hg_path = os.path.join(folder, hg_file)
    backup_path = hg_path.replace('.hg', '_backup.json')

    print(f"[+] Decompressing {hg_file}...")

    decompressed_bytes = decompress(readFile(hg_path))
    if not decompressed_bytes:
        print("[!] Decompression failed.")
        return

    # 🔹 Clean JSON text
    decompressed_text = decompressed_bytes.decode('utf-8', errors='replace')
    end_idx = decompressed_text.rfind('}')
    if end_idx != -1:
        decompressed_text = decompressed_text[:end_idx + 1]

    # Parse JSON
    try:
        original_data = json.loads(decompressed_text)
    except json.JSONDecodeError as e:
        print(f"[x] Failed to parse JSON: {e}")
        with open("debug_dump.txt", "w", encoding="utf-8") as dump:
            dump.write(decompressed_text)
        print("[!] Decompressed text saved to debug_dump.txt")
        return

    # Backup
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(original_data, ensure_ascii=False, indent=2))
    print(f"[✓] Backup saved as {backup_path}")

    # Load multiple EditBlocks
    edit_blocks = load_edit_blocks(edits_path)
    if not edit_blocks:
        return

    # Apply edits in forward order
    hg_data = json.loads(decompressed_text)
    resume_path = None
    for i, block in enumerate(edit_blocks, 1):
        print(f"[#] Applying EditBlock {i}...")
        resume_path = replace_nested_editblock(hg_data, block, resume_path=resume_path)

    # Save edited JSON (uncompressed)
    print("[+] Saving edited file (JSON format) as .hg...")
    edited_text = json.dumps(hg_data, ensure_ascii=False, separators=(',', ':'))
    with open(hg_path, 'w', encoding='utf-8') as f:
        f.write(edited_text)

    print(f"[✓] All edits applied and saved to {hg_file}")
    print("[✓] Done.")

# =================== Entry Point ===================

if __name__ == '__main__':
    main()