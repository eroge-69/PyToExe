import re, os, zlib, lzma, base64, webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

class MultiLineInputDialog(simpledialog.Dialog):
    def __init__(self, parent, title, prompt):
        self.prompt = prompt
        super().__init__(parent, title)

    def body(self, master):
        tk.Label(master, text=self.prompt, anchor="w").pack(fill="x", padx=10, pady=(10,0))
        self.text = tk.Text(master, width=80, height=20)
        self.text.pack(fill="both", expand=True, padx=10, pady=5)
        return self.text

    def apply(self):
        data = self.text.get("1.0", "end").strip()
        self.result = data if data else None

def detect_format(data: bytes) -> str:
    if data.startswith(b'\xFF\xD8\xFF'):
        return 'jpg'
    if data.startswith(b'BM'):
        return 'bmp'
    if data.startswith(b'\x00\x00\x01\x00'):
        return 'ico'
    if data.startswith(b'\x89PNG\r\n\x1A\n'):
        return 'png'
    if data.startswith(b'MZ'):
        if len(data) >= 0x40:
            e_lfanew = int.from_bytes(data[0x3C:0x40], 'little')
            if data[e_lfanew:e_lfanew+4] == b'PE\x00\x00':
                char_off = e_lfanew + 4 + 18
                if len(data) >= char_off+2:
                    flags = int.from_bytes(data[char_off:char_off+2], 'little')
                    return 'dll' if (flags & 0x2000) else 'exe'
        return 'exe'
    # SVG or XML detection
    try:
        text = data.decode("utf-8", errors="ignore").strip().lower()
        if text.startswith("<?xml") and "<svg" in text:
            return "svg"
        elif text.startswith("<?xml") or text.startswith("<xml"):
            return "xml"
        elif text.startswith("<svg"):
            return "svg"
    except Exception:
        pass
    return 'bin'

def detect_compression(blob: bytes) -> str:
    if blob.startswith(b'\x78'):
        return 'zlib'
    if len(blob) > 13 and blob[0] in (0x5D, 0x00, 0x01):
        return 'lzma'
    return 'none'

def decompress_blob(blob: bytes) -> bytes:
    method = detect_compression(blob)
    try:
        if method == 'zlib':
            return zlib.decompress(blob)
        elif method == 'lzma':
            return lzma.decompress(blob)
        else:
            return blob
    except Exception as e:
        messagebox.showerror("Decompression Error", f"{method.upper()} decompression failed:\n{e}")
        return b''

def get_encoded_string(root: tk.Tk) -> tuple[str,str|None]:
    use_file = messagebox.askyesno(
        "Input Method",
        "Load encoded text from a file?\n\n"
        "Yes → open file dialog\n"
        "No  → paste text manually"
    )

    raw_lines = []
    input_name = None

    if use_file:
        path = filedialog.askopenfilename(
            title="Select encoded .txt",
            filetypes=[("Text files","*.txt"),("All files","*.*")]
        )
        if not path:
            return "", None
        with open(path, 'r', encoding='utf-8') as f:
            raw_lines = f.read().splitlines()
        input_name = os.path.basename(path)
    else:
        dlg = MultiLineInputDialog(root,
            title="Paste Encoded Text",
            prompt="Paste the entire encoded blob here:"
        )
        if not dlg.result:
            return "", None
        raw_lines = dlg.result.splitlines()

    parts = [re.sub(r'^\d+=', '', line.strip()) for line in raw_lines if line.strip()]
    return "".join(parts), input_name

def resolve_output_path(directory: str, base: str, ext: str) -> str:
    target = os.path.join(directory, f"{base}.{ext}")
    if not os.path.exists(target):
        return target

    if messagebox.askyesno("File Exists",
        f"'{base}.{ext}' already exists. Overwrite?\nIf you select No, the file will be renamed"):
        return target

    i = 1
    while True:
        candidate = os.path.join(directory, f"{base}_{i}.{ext}")
        if not os.path.exists(candidate):
            return candidate
        i += 1

def decode_and_save(root: tk.Tk, encoded_b64: str, input_name: str|None):
    pad = (-len(encoded_b64)) % 4
    if pad:
        encoded_b64 += "=" * pad

    try:
        blob = base64.b64decode(encoded_b64)
    except Exception as e:
        messagebox.showerror("Decode Error", f"Base64 decoding failed:\n{e}")
        return

    data = decompress_blob(blob)
    if not data:
        return

    ext = detect_format(data)
    if ext == "bin":
        messagebox.showerror("Unknown Format", "Decoded data has an unknown format. No file will be saved.")
        return

    pref = r"D:\Downloads"
    out_dir = pref if os.path.isdir(pref) else os.path.dirname(__file__)
    base = os.path.splitext(input_name or "decoded_output")[0]
    out_path = resolve_output_path(out_dir, base, ext)

    with open(out_path, 'wb') as f:
        f.write(data)

    if ext in ("jpg", "bmp", "png", "ico"):
        try:
            os.startfile(out_path)
        except Exception:
            pass
    elif ext == "svg":
        webbrowser.open(out_path)

    messagebox.showinfo("Done", f"Saved to:\n{out_path}")

def main():
    root = tk.Tk()
    root.withdraw()

    encoded, name = get_encoded_string(root)
    if not encoded:
        return

    decode_and_save(root, encoded, name)

if __name__ == "__main__":
    main()