
import tkinter as tk
from tkinter import filedialog, messagebox, Scrollbar, Text, RIGHT, Y, END

eeprom_bytes = bytearray()

def load_file():
    global eeprom_bytes
    file_path = filedialog.askopenfilename(filetypes=[("BIN files", "*.bin")])
    if file_path:
        with open(file_path, "rb") as f:
            eeprom_bytes = f.read()
        messagebox.showinfo("Loaded", f"{len(eeprom_bytes)} bytes loaded from:\n{file_path}")

def convert_region():
    try:
        start_offset = int(entry_start.get(), 16)
        end_offset = int(entry_end.get(), 16)
        region = eeprom_bytes[start_offset:end_offset]
        result_text.delete(1.0, END)
        for i, byte in enumerate(region):
            result_text.insert(END, f"Offset 0x{start_offset + i:04X}: {byte:3d} (0x{byte:02X})\n")
    except Exception as e:
        messagebox.showerror("Error", str(e))

app = tk.Tk()
app.title("EEPROM Hex to Bytes Converter")
app.geometry("600x400")

tk.Label(app, text="Start Offset (hex):").pack()
entry_start = tk.Entry(app)
entry_start.pack()
entry_start.insert(0, "0x10")

tk.Label(app, text="End Offset (hex):").pack()
entry_end = tk.Entry(app)
entry_end.pack()
entry_end.insert(0, "0x50")

tk.Button(app, text="Load EEPROM File", command=load_file).pack(pady=10)
tk.Button(app, text="Convert Region", command=convert_region).pack(pady=5)

frame = tk.Frame(app)
frame.pack(fill="both", expand=True)
result_text = Text(frame, wrap="none")
scrollbar = Scrollbar(frame, orient="vertical", command=result_text.yview)
result_text.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side=RIGHT, fill=Y)
result_text.pack(fill="both", expand=True)

app.mainloop()
