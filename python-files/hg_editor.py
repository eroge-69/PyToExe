import json
import os
import datetime

def load_edit_block(edits_path):
    """
    Loads edits.json and returns:
    - The edit block (first top-level value that's a dict and not a backup).
    - The whole edits.json data as a dict.
    """
    with open(edits_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for key, value in data.items():
        if isinstance(value, dict) and not key.startswith('backup_'):
            return value, data
    print("[!] No edit block found in edits.json.")
    return None, data

def main():
    folder = os.getcwd()

    # Locate .hg file and edits.json
    hg_file = next((f for f in os.listdir(folder) if f.endswith('.hg')), None)
    edits_file = os.path.join(folder, 'edits.json')

    if not hg_file or not os.path.isfile(edits_file):
        print("[!] Could not find .hg file or edits.json in the folder.")
        return

    hg_path = os.path.join(folder, hg_file)

    # Load .hg JSON (expected: list of objects)
    with open(hg_path, 'r', encoding='utf-8') as f:
        try:
            hg_list = json.load(f)
        except json.JSONDecodeError as e:
            print(f"[!] Failed to load .hg file: {e}")
            return

    if not isinstance(hg_list, list):
        print("[!] .hg file content is not a JSON list as expected.")
        return

    # Load edit block and full edits.json data
    edit_block, edits_data = load_edit_block(edits_file)
    if not edit_block:
        print("[!] No valid edit block found; aborting.")
        return

    # Find first block in hg_list with the same set of keys
    target_keys = set(edit_block.keys())
    target_index = None
    for idx, obj in enumerate(hg_list):
        if isinstance(obj, dict) and set(obj.keys()) == target_keys:
            target_index = idx
            break

    if target_index is None:
        print("[!] No matching block found in .hg file.")
        return

    # Backup the original block
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_key = f"backup_{timestamp}"
    edits_data[backup_key] = hg_list[target_index]

    # Replace block with edit block
    hg_list[target_index] = edit_block

    # Save updated edits.json
    with open(edits_file, 'w', encoding='utf-8') as f:
        json.dump(edits_data, f, ensure_ascii=False, indent=2)

    # Save updated .hg file
    with open(hg_path, 'w', encoding='utf-8') as f:
        json.dump(hg_list, f, ensure_ascii=False, indent=2)

    print(f"[✓] Backup saved in edits.json under key '{backup_key}'.")
    print(f"[✓] Updated block {target_index} in {hg_file} with data from edits.json.")
    print("[✓] Done.")

if __name__ == '__main__':
    main()