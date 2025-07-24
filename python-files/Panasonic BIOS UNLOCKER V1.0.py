from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import subprocess
import sys
import os

# --- Constants ---
SIGNATURE = bytes.fromhex("41 4D 49 54 53 45 53 65 74 75 70")  # "AMITSESetup"
ZERO_PATCH_200 = bytes([0x00] * 200)
ICON_PATH = Path(__file__).with_name("unlock.ico")  # icon in same folder

# --- Signature Patch Function ---
def patch_signature_block(data: bytearray) -> int:
    count = 0
    i = 0
    while i <= len(data) - len(SIGNATURE):
        index = data.find(SIGNATURE, i)
        if index == -1:
            break
        patch_start = index + len(SIGNATURE)
        patch_end = patch_start + len(ZERO_PATCH_200)
        if patch_end > len(data):
            break
        data[patch_start:patch_end] = ZERO_PATCH_200
        count += 1
        i = index + len(SIGNATURE)
    return count

# --- Unlock BIOS File ---
def unlock_signature(input_file_path: str) -> tuple[str, Path | None]:
    input_path = Path(input_file_path)
    if not input_path.exists():
        return "[!] File not found.", None

    data = bytearray(input_path.read_bytes())
    total_patches = patch_signature_block(data)

    if total_patches == 0:
        return "[!] No signature patches were applied.", None

    output_file_path = input_path.with_name(input_path.stem + "_UNLOCKED" + input_path.suffix)
    Path(output_file_path).write_bytes(data)
    return f"[✔] File unlocked successfully.\nSaved as:\n{output_file_path}", output_file_path

# --- Open output folder in Explorer ---
def open_folder(path: Path):
    subprocess.Popen(f'explorer /select,"{path}"')

# --- GUI Logic ---
def select_file():
    file_path = filedialog.askopenfilename(title="Select BIOS File", filetypes=[("All Files", "*.*")])
    if file_path:
        result, out_path = unlock_signature(file_path)
        result_box.config(state=tk.NORMAL)
        result_box.delete(1.0, tk.END)
        result_box.insert(tk.END, result)
        result_box.config(state=tk.DISABLED)

        if "[!]" in result:
            messagebox.showerror("Error", result)
        elif "[✔]" in result and out_path:
            open_folder(out_path)

# --- Setup Window ---
root = tk.Tk()
root.title("Panasonic BIOS Unlocker v1.0 by www.indiafix.in")
root.geometry("480x340")
root.configure(bg="#1e1e2f")

# Set window icon if available
try:
    root.iconbitmap(str(ICON_PATH))
except Exception as e:
    print(f"[!] Icon not loaded: {e}")

# --- UI Elements ---
header = tk.Label(root, text="Panasonic BIOS Unlocker v1.0", font=("Segoe UI", 16, "bold"),
                  fg="#00ffc8", bg="#1e1e2f")
header.pack(pady=12)

browse_btn = tk.Button(root, text="🔓 Select BIOS File", command=select_file,
                       font=("Segoe UI", 12, "bold"), bg="#00aaff", fg="white", width=25)
browse_btn.pack(pady=10)

result_box = scrolledtext.ScrolledText(root, height=5, width=50, font=("Consolas", 10), wrap=tk.WORD)
result_box.pack(pady=10)
result_box.insert(tk.END, "Awaiting file selection...")
result_box.config(state=tk.DISABLED)

disclaimer = tk.Label(root, text="⚠️ Use responsibly. This modifies BIOS files.",
                      font=("Segoe UI", 8), fg="orange", bg="#1e1e2f")
disclaimer.pack()

footer = tk.Label(root, text="Developed by www.indiafix.in", font=("Segoe UI", 9, "italic"),
                  fg="#aaaaaa", bg="#1e1e2f")
footer.pack(side="bottom", pady=10)

root.mainloop()
