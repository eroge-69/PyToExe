import os
import re
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

# Map markers to extensions
FILE_TYPE_MAP = {
    b'Model Built File': 'model',
    b'Texture Built File': 'texture',
    b'Material Built File': 'material',
    b'Material Template Built File': 'materialgraph',
    b'Config Built File': 'config',
    b'Icon Built File': 'icon',
    b'PNG': 'png',
    b'JPG': 'jpg',
    b'TXT': 'txt',
}

def extract_all_assets(file_path):
    output_dir = Path(file_path).with_name(Path(file_path).stem + "_extracted")
    output_dir.mkdir(exist_ok=True)

    with open(file_path, 'rb') as f:
        data = f.read()

    # Find all "1TAD" markers
    positions = [m.start() - 36 for m in re.finditer(b'1TAD', data)]
    if not positions:
        messagebox.showinfo("Info", "No entries found in the .suit file.")
        return

    count_dict = {}
    total = 0

    for i, start in enumerate(positions):
        end = positions[i + 1] if i + 1 < len(positions) else len(data)
        chunk = data[start:end]

        # Determine type
        file_ext = 'bin'
        for marker, ext in FILE_TYPE_MAP.items():
            if marker in chunk:
                file_ext = ext
                break

        # Handle duplicate names
        count = count_dict.get(file_ext, 0)
        file_name = f"{file_ext}_{count}.{file_ext}" if count > 0 else f"{file_ext}.{file_ext}"
        count_dict[file_ext] = count + 1

        # Save chunk
        with open(output_dir / file_name, 'wb') as out_file:
            out_file.write(chunk)
        total += 1

    messagebox.showinfo("Done", f"Extracted {total} files to:\n{output_dir}")

def select_suit_file():
    path = filedialog.askopenfilename(title="Select .suit file", filetypes=[("Suit files", "*.suit")])
    entry_suit.delete(0, tk.END)
    entry_suit.insert(0, path)

def run_extraction():
    suit_path = entry_suit.get()
    if not os.path.exists(suit_path):
        messagebox.showerror("Error", "The selected .suit file does not exist.")
        return
    extract_all_assets(suit_path)

# GUI
root = tk.Tk()
root.title("Spider-Man 2 .suit Full Extractor")

tk.Label(root, text="Select .suit file:").grid(row=0, column=0, padx=5, pady=5)
entry_suit = tk.Entry(root, width=50)
entry_suit.grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=select_suit_file).grid(row=0, column=2, padx=5, pady=5)

tk.Button(root, text="Extract All Assets", command=run_extraction, width=20).grid(row=1, column=1, pady=10)

root.mainloop()
