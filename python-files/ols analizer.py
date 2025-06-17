import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import struct
import os

def read_pointer(data, offset):
    return struct.unpack_from('<I', data, offset)[0]

def read_ascii(data, start, length=512):
    text = data[start:start+length]
    try:
        return text.split(b'\x00')[0].decode('ascii', errors='ignore')
    except:
        return ''

def analyze_ols_file(filepath):
    try:
        with open(filepath, 'rb') as f:
            data = f.read()

        results = []
        results.append(f"Analyzing: {os.path.basename(filepath)}")
        results.append(f"File size: {len(data)} bytes\n")

        ascii_ptr = read_pointer(data, 0x20)
        bin_ptr   = read_pointer(data, 0x24)
        id_block  = read_pointer(data, 0x1C)

        results.append(f"OLS internal ID @ 0x1C   : 0x{id_block:08X}")
        results.append(f"ASCII text starts @ 0x20 : 0x{ascii_ptr:08X}")
        results.append(f"BIN dump starts @ 0x24   : 0x{bin_ptr:08X}\n")

        results.append("Preview ASCII region:")
        ascii_preview = read_ascii(data, ascii_ptr, 1024)
        results.append(f">>> {ascii_preview[:256]}\n")

        results.append("Hex dump [0x1C�0x2CF]:")
        for i in range(0x1C, 0x2D0, 16):
            row = data[i:i+16]
            hexrow = ' '.join(f"{b:02X}" for b in row)
            asciir = ''.join(chr(b) if 32 <= b < 127 else '.' for b in row)
            results.append(f"{i:04X}: {hexrow:<48} | {asciir}")

        return '\n'.join(results)

    except Exception as e:
        return f"Error: {str(e)}"

def open_file():
    filepath = filedialog.askopenfilename(title="Select OLS File", filetypes=[("OLS files", "*.ols")])
    if filepath:
        result = analyze_ols_file(filepath)
        text_area.delete(1.0, tk.END)
        text_area.insert(tk.END, result)
        root.title(f"OLS Header Analyzer - {os.path.basename(filepath)}")

def save_to_txt():
    content = text_area.get(1.0, tk.END)
    if not content.strip():
        messagebox.showwarning("Warning", "No content to save!")
        return
    save_path = filedialog.asksaveasfilename(title="Save as TXT", defaultextension=".txt",
                                             filetypes=[("Text files", "*.txt")])
    if save_path:
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(content)
            messagebox.showinfo("Saved", f"Results saved to:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")

# GUI setup
root = tk.Tk()
root.title("OLS Header Analyzer")

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

btn_open = tk.Button(frame, text="Open OLS File", command=open_file, width=20)
btn_open.pack(side=tk.LEFT, padx=5)

btn_save = tk.Button(frame, text="Save Output to TXT", command=save_to_txt, width=20)
btn_save.pack(side=tk.LEFT, padx=5)

text_area = scrolledtext.ScrolledText(root, width=100, height=35)
text_area.pack(padx=10, pady=10)

root.mainloop()
