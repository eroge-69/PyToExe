import tkinter as tk
from tkinter import filedialog, messagebox
import os

# Czysty wzorzec bloku
clean_block_hex = (
    "FF FF 00 00 00 00 00 00 00 00 00 00 00 00 00 00 FE "
    "FF FF 00 00 00 00 00 00 00 00 00 00 00 00 00 00 FE "
    "FF FF 00 00 00 00 00 00 00 00 00 00 00 00 00 00 FE "
    "FF FF 00 00 00 00 00 00 00 00 00 00 00 00 00 00 FE "
    "FF FF 00 00 00 00 00 00 00 00 00 00 00 00 00 00 FE "
    "FF FF 00 00 00 00 00 00 00 00 00 00 00 00 00 00 FE "
    "FF FF 00 00 00 00 00 00 00 00 00 00 00 00 00 00 FE "
    "FF FF 00 00 00 00 00 00 00 00 00 00 00 00 00 00 FE "
    "FF FF 00 00 00 00 00 00 00 00 00 00 00 00 00 00 FE "
    "FF FF 00 00 00 00 00 00 00 00 00 00 00 00 00 00 FE "
    "FF FF 00 00 00 00 00 00 00 00 00 00 00 00 00 00 FE "
    "FF FF 00 00 00 00 00 00 00 00 00 00 00 00 00 00 FE "
    "FF FF 00 00 00 00 00 00 00 00 00 00 00 00 00 00 FE "
    "FF FF 00 00 00 00 00 00 00 00 00 00 00 00 00 00 FE "
    "FF FF 00 00 00 00 00 00 00 00 00 00 00 00 00 00 FE "
    "FF FF 00 00 00 00 00 00 00 00 00 00 00 00 00 00 FE"
)

clean_block = bytes.fromhex(clean_block_hex)
BLOCK_SIZE = len(clean_block)


class EEPROMCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EEPROM Checker")
        self.data = b""
        self.fixed_data = b""
        self.path = None

        self.label = tk.Label(root, text="Wczytaj wsad EEPROM")
        self.label.pack(pady=10)

        self.load_btn = tk.Button(root, text="Wczytaj plik", command=self.load_file)
        self.load_btn.pack(pady=5)

        self.analyze_btn = tk.Button(root, text="Analizuj i napraw", command=self.analyze, state=tk.DISABLED)
        self.analyze_btn.pack(pady=5)

        self.save_btn = tk.Button(root, text="Zapisz naprawiony wsad", command=self.save_file, state=tk.DISABLED)
        self.save_btn.pack(pady=5)

    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[("BIN files", "*.bin"), ("All files", "*.*")])
        if not path:
            return

        with open(path, "rb") as f:
            self.data = f.read()

        self.path = path
        self.label.config(text=f"Wczytano: {os.path.basename(path)} ({len(self.data)} bajtów)")
        self.analyze_btn.config(state=tk.NORMAL)
        self.save_btn.config(state=tk.DISABLED)

    def analyze(self):
        if not self.data:
            messagebox.showerror("Błąd", "Brak danych")
            return

        data = bytearray(self.data)  # robimy kopię modyfikowalną
        bad_blocks = 0
        bad_offsets = []

        i = 0
        while i <= len(data) - BLOCK_SIZE:
            block = data[i:i + BLOCK_SIZE]
            if block == clean_block:
                i += BLOCK_SIZE  # czysty blok – przeskakujemy
            elif block[:4] == clean_block[:4] and block[-1:] == clean_block[-1:]:
                # Podejrzany blok – wygląda podobnie
                bad_blocks += 1
                bad_offsets.append(i)
                data[i:i + BLOCK_SIZE] = clean_block
                i += BLOCK_SIZE
            else:
                i += 1  # nie wygląda jak blok, przesuwamy się o 1 bajt

        self.fixed_data = bytes(data)

        if bad_blocks == 0:
            messagebox.showinfo("Wynik", "Wsad jest OK – brak uszkodzonych bloków.")
            self.save_btn.config(state=tk.DISABLED)
        else:
            info = f"Znaleziono {bad_blocks} uszkodzonych bloków.\n"
            info += "Offsety: " + ", ".join(hex(x) for x in bad_offsets)
            messagebox.showwarning("Wynik", info)
            self.save_btn.config(state=tk.NORMAL)

    def save_file(self):
        if not self.fixed_data:
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".bin",
            filetypes=[("BIN files", "*.bin"), ("All files", "*.*")],
            initialfile="naprawiony_wsad.bin"
        )
        if not save_path:
            return

        with open(save_path, "wb") as f:
            f.write(self.fixed_data)

        messagebox.showinfo("Sukces", "Naprawiony wsad zapisany pomyślnie.")


if __name__ == "__main__":
    root = tk.Tk()
    app = EEPROMCheckerApp(root)
    root.mainloop()
