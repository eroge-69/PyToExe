import os
import re
from datetime import datetime

# Configuration
company_name = "Dragon Studios ENT LLC"
start_year = 2024
current_year = datetime.now().year

# Supported file types and their comment syntax
comment_styles = {
    ".cpp": "//",
    ".h": "//",
    ".cs": "//",
    ".js": "//",
    ".py": "#"
}

# Regex for existing footer detection
def get_footer_pattern(ext, comment_prefix):
    return re.compile(
        rf"{re.escape(comment_prefix)} End of File\n{re.escape(comment_prefix)} © (\d{{4}})(–(\d{{4}}))? {re.escape(company_name)}\. All Rights Reserved\.",
        re.MULTILINE
    )

def generate_footer(ext):
    prefix = comment_styles[ext]
    return (
        f"\n{prefix} -------------------------------------------------------------------------------\n"
        f"{prefix} End of File\n"
        f"{prefix} © {start_year}–{current_year} {company_name}. All Rights Reserved.\n"
        f"{prefix} -------------------------------------------------------------------------------\n"
    )

def update_or_insert_footer(path, ext):
    comment_prefix = comment_styles.get(ext)
    if not comment_prefix:
        return  # Skip unsupported extensions

    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        print(f"Skipped binary or unreadable file: {path}")
        return

    updated = False
    footer_pattern = get_footer_pattern(ext, comment_prefix)

    if footer_pattern.search(content):
        def replacer(match):
            year1 = int(match.group(1))
            return (
                f"{comment_prefix} End of File\n"
                f"{comment_prefix} © {year1}–{current_year} {company_name}. All Rights Reserved."
            )
        content = footer_pattern.sub(replacer, content)
        updated = True
    else:
        footer = generate_footer(ext)
        content = content.rstrip() + footer
        updated = True

    if updated:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✔ Footer updated or inserted: {path}")

def scan_directory(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            _, ext = os.path.splitext(file)
            if ext in comment_styles:
                full_path = os.path.join(root, file)
                update_or_insert_footer(full_path, ext)

if __name__ == "__main__":
    directory = input("Enter the path to scan: ").strip()

    if os.path.isdir(directory):
        print(f"📁 Scanning directory: {directory}")
        scan_directory(directory)
        print("✅ All eligible files updated.")
    else:
        print("❌ Invalid directory path.")
# -------------------------------------------------------------------------------
# End of File
# © 2024–2025 Dragon Studios ENT LLC. All Rights Reserved.
# -------------------------------------------------------------------------------
