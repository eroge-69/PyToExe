import tkinter as tk
from ttkthemes import ThemedTk
from tkinter import ttk, filedialog, messagebox

PIN_MAP = {
    0x03: '1',
    0x65: '4',
    0x2E: '7',
    0x14: '0',
    0x48: '2',
    0x72: '5',
    0xD1: '8',
    0x5F: '3',
    0x39: '6',
    0xC6: '9'
}

def decode_pin_simple(data):
    if len(data) < 0x658 + 8:
        return None, "File too small to contain required data."

    # Read 8 bytes from 0x658
    segment = data[0x658:0x658 + 8]
    
    # Remove all 0xAA
    filtered = [b for b in segment if b != 0x5F]
    print(filtered)  # Debug: Print the raw bytes for inspection
    # Decode remaining bytes
    try:
        pin = ''.join(PIN_MAP[b] for b in filtered)
        return pin, None
    except KeyError as e:
        return None, f"Unknown byte 0x{e.args[0]:02X} in PIN"

class EEPROMDecoderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Astra H CIM EEPROM PIN Decoder")
        self.root.resizable(False, False)
        self.root.attributes('-toolwindow', True)

        self.file_path = None
        self.data = None

        style = ttk.Style()
        style.configure("Green.TLabel", foreground="green", font=("Courier", 24))
        style.configure("Blue.TLabel", foreground="blue")

        self.status_label = ttk.Label(root, text="No file loaded.", style="Blue.TLabel")
        self.status_label.pack(pady=(10, 0))

        self.pin_label = ttk.Label(root, text="", style="Green.TLabel")
        self.pin_label.pack(pady=(10, 20))

        ttk.Button(root, text="EXIT", command=root.quit, width=30).pack(side="bottom", pady=(0, 10))
        ttk.Button(root, text="DECODE", command=self.decode_pin, width=30).pack(side="bottom", pady=5)
        ttk.Button(root, text="OPEN", command=self.open_file, width=30).pack(side="bottom", pady=5)
        
    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("Binary files", "*.bin"), ("All files", "*.*")])
        if not path:
            return

        try:
            with open(path, 'rb') as f:
                self.data = bytearray(f.read())
            self.file_path = path
            self.status_label.config(text=f"Loaded OK!", style="Green.TLabel")
            self.pin_label.pack(pady=(10, 20))
            self.pin_label.config(text="")
        except Exception as e:
            messagebox.showerror("Error", f"Could not read file:\n{e}")

    def decode_pin(self):
        if not self.data:
            messagebox.showwarning("Warning", "Please load a file first.")
            return

        pin, error = decode_pin_simple(self.data)
        if error:
            self.pin_label.config(text="", style="Red.TLabel")
            messagebox.showerror("Decode Error", error)
        else:
            self.pin_label.config(text=f"{pin}", style="Green.TLabel")



if __name__ == "__main__":
    root = ThemedTk(theme="arc")  # Try 'arc', 'plastik', 'clearlooks', etc.
    app = EEPROMDecoderApp(root)
    root.mainloop()
