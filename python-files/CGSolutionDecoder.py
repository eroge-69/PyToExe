import tkinter as tk
from tkinter import filedialog, messagebox
import os
import re

# ---- Utility Funzioni ----

def load_file(path):
    with open(path, "rb") as f:
        return f.read()

def load_file_mutable(path):
    with open(path, "rb") as f:
        return bytearray(f.read())

def save_file(path, data):
    with open(path, "wb") as f:
        f.write(data)

def extract_patch(original, modified):
    patch = []
    min_len = min(len(original), len(modified))
    for i in range(min_len):
        if original[i] != modified[i]:
            patch.append((i, modified[i]))
    for i in range(min_len, len(modified)):
        patch.append((i, modified[i]))
    return patch

def save_patch_formatted(patch, output_path="patch.json"):
    with open(output_path, "w") as f:
        f.write("patch = [\n")
        for addr, val in patch:
            f.write(f"  (0x{addr:06X}, 0x{val:02X}),\n")
        f.write("]\n")

def parse_patch_file(path):
    with open(path, "r") as f:
        content = f.read()
    pattern = re.compile(r"\(\s*0x([0-9A-Fa-f]+)\s*,\s*0x([0-9A-Fa-f]+)\s*\)")
    return [(int(a, 16), int(v, 16)) for a, v in pattern.findall(content)]

# ---- GUI App ----

class DragDropLabel(tk.Label):
    def __init__(self, master, text, callback):
        super().__init__(master, text=text, relief="groove", width=40, height=2, bg="#f0f0f0")
        self.callback = callback
        self.bind("<Button-1>", self.on_click)


    def on_click(self, event):
        path = filedialog.askopenfilename()
        if path:
            self.callback(path)


class SolutionExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Solution Extractor & Patch Applier")
        self.root.geometry("820x350")
        self.original_path = ""
        self.modified_path = ""
        self.binary_path = ""
        self.patch_path = ""

        self.setup_ui()

    def setup_ui(self):
        container = tk.Frame(self.root)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Estrattore (sinistra) ---
        left = tk.LabelFrame(container, text="Estrazione Patch", padx=10, pady=10)
        left.pack(side="left", fill="both", expand=True, padx=5)

        self.lbl_orig = DragDropLabel(left, "File ORIGINALE", self.set_original)
        self.lbl_orig.pack(pady=5)
        self.lbl_mod = DragDropLabel(left, "File MODIFICATO", self.set_modified)
        self.lbl_mod.pack(pady=5)
        tk.Button(left, text="Genera Patch", command=self.generate_patch, bg="green", fg="white").pack(pady=10)

        # --- Applicatore (destra) ---
        right = tk.LabelFrame(container, text="Applicazione Patch", padx=10, pady=10)
        right.pack(side="right", fill="both", expand=True, padx=5)

        self.lbl_bin = DragDropLabel(right, "File BINARIO da patchare", self.set_binary)
        self.lbl_bin.pack(pady=5)
        self.lbl_patch = DragDropLabel(right, "File PATCH (.json)", self.set_patch)
        self.lbl_patch.pack(pady=5)
        tk.Button(right, text="Applica Patch", command=self.apply_patch, bg="blue", fg="white").pack(pady=10)

    # --- Callback UI Set ---
    def set_original(self, path):
        self.original_path = path
        self.lbl_orig.config(text=os.path.basename(path))

    def set_modified(self, path):
        self.modified_path = path
        self.lbl_mod.config(text=os.path.basename(path))

    def set_binary(self, path):
        self.binary_path = path
        self.lbl_bin.config(text=os.path.basename(path))

    def set_patch(self, path):
        self.patch_path = path
        self.lbl_patch.config(text=os.path.basename(path))

    # --- Azioni ---
    def generate_patch(self):
        if not self.original_path or not self.modified_path:
            messagebox.showerror("Errore", "Seleziona entrambi i file per l'estrazione.")
            return
        try:
            original = load_file(self.original_path)
            modified = load_file(self.modified_path)
            patch = extract_patch(original, modified)

            if not patch:
                messagebox.showinfo("Nessuna differenza", "I file sono identici.")
                return

            output_path = filedialog.asksaveasfilename(defaultextension=".json", title="Salva patch",
                                                       initialfile="patch.json")
            if output_path:
                save_patch_formatted(patch, output_path)
                messagebox.showinfo("Successo", f"Patch salvata con {len(patch)} modifiche.")
        except Exception as e:
            messagebox.showerror("Errore", str(e))

    def apply_patch(self):
        if not self.binary_path or not self.patch_path:
            messagebox.showerror("Errore", "Seleziona sia file binario che patch.")
            return
        try:
            data = load_file_mutable(self.binary_path)
            patch = parse_patch_file(self.patch_path)

            for addr, val in patch:
                if addr < len(data):
                    data[addr] = val
                else:
                    messagebox.showwarning("Indirizzo fuori range", f"0x{addr:X} oltre fine file.")

            output_path = filedialog.asksaveasfilename(defaultextension=".bin", title="Salva file patchato",
                                                       initialfile="patched_output.bin")
            if output_path:
                save_file(output_path, data)
                messagebox.showinfo("Successo", f"Patch applicata correttamente.")
        except Exception as e:
            messagebox.showerror("Errore", str(e))

# --- Avvio App ---
if __name__ == "__main__":
    root = tk.Tk()
    app = SolutionExtractorApp(root)
    root.mainloop()
