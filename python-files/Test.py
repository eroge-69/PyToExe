import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

def crc16_arc(data: bytes) -> int:
    poly = 0x8005
    crc = 0x0000
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ poly
            else:
                crc >>= 1
    return crc & 0xFFFF

def calculate_crc():
    hex_input = input_area.get("1.0", tk.END).replace("\n", "").replace(";", "").replace(" ", "")
    try:
        data = bytes.fromhex(hex_input)
        crc = crc16_arc(data)
        result_label.config(text=f"CRC-16/ARC: {crc:04X}")
    except ValueError:
        messagebox.showerror("Fehler", "Ungültige HEX-Daten eingegeben.")

def load_file():
    filepath = filedialog.askopenfilename(filetypes=[("Textdateien", "*.txt")])
    if filepath:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        input_area.delete("1.0", tk.END)
        input_area.insert(tk.END, content)

root = tk.Tk()
root.title("CRC-16/ARC Prüfer")

tk.Label(root, text="Gib HEX-Daten ein:").pack()
input_area = scrolledtext.ScrolledText(root, height=10, width=80)
input_area.pack(padx=10)

tk.Button(root, text="CRC berechnen", command=calculate_crc).pack(pady=5)
tk.Button(root, text="Datei laden", command=load_file).pack()

result_label = tk.Label(root, text="CRC-16/ARC: ?", font=("Arial", 12, "bold"))
result_label.pack(pady=10)

root.mainloop()
