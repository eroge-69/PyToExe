import os

# Replacement mapping
replacement_map = {
    "ps-t0": "ps-t6",
    "ps-t1": "ps-t0",
    "ps-t2": "ps-t1"
}

def process_ini_file(filepath):
    filename = os.path.basename(filepath)
    if filename.startswith("DISABLED"):
        print(f"[SKIPPED] {filepath} - Filename starts with 'DISABLED'")
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Check if already modified
    if lines and lines[0].strip() == ";5.7modified":
        print(f"[SKIPPED] {filepath} - File already 5.7 compatible")
        return

    modified = False
    new_lines = []

    for line in lines:
        original_line = line
        for key, val in replacement_map.items():
            if key in line:
                line = line.replace(key, val)
        if line != original_line:
            modified = True
        new_lines.append(line)

    if modified:
        # Backup original file as .txt
        backup_path = filepath.rsplit('.', 1)[0] + ".txt"
        if not os.path.exists(backup_path):
            with open(backup_path, 'w', encoding='utf-8') as backup_file:
                backup_file.writelines(lines)
            print(f"[BACKUP] Created backup: {backup_path}")

        # Add the modification flag at the top
        new_lines.insert(0, ";5.7modified\n")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"[MODIFIED] {filepath}")
    else:
        print(f"[UNCHANGED] {filepath} - No matching ps-tX lines found")

def scan_and_process_ini_files(root_folder):
    for dirpath, dirnames, filenames in os.walk(root_folder):
        # Skip any subdirectories starting with "DISABLED"
        dirnames[:] = [d for d in dirnames if not d.startswith("DISABLED")]

        for filename in filenames:
            if filename.lower().endswith('.ini') and not filename.startswith("DISABLED"):
                full_path = os.path.join(dirpath, filename)
                print(f"[FOUND] {full_path}")
                process_ini_file(full_path)

# No input, just scan current directory
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    print(f"Scanning and processing .ini files in: {current_dir}")
    scan_and_process_ini_files(current_dir)
