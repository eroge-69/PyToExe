import tkinter as tk
from tkinter import filedialog, messagebox

# Feature definitions
coding_map = [
    ("Close Windows with CA", 0x0A, 0x01),
    ("Mirror Folding with FOB", 0x0A, 0x08),
    ("Hazard Lights on Lock", 0x10, 0x01),
    ("Bulb Type Xenon (1=Yes)", 0x15, None),
    ("Welcome Light Front Parking", 0x30, 0x30),
    ("Double Blink Hazard", 0x12, 0x80),
    ("Auto Lock", 0x0C, 0x20),
    ("Interior Light Delay", 0x20, None),
    ("Panic Mode", 0x1F, 0x01),
    ("Fog Lights + Flash", 0x22, 0x01),
    ("DRL on Halogen", 0x24, 0x01),
    ("Auto Dimming Mirrors", 0x25, 0x01),
    ("Disable Window Safety", 0x40, 0x01),
    ("Double Blink Hazard in Crash", 0x14, 0x02),
]

xenon_features = [
    ("Xenon Module Installed", 0x15, 0x01),
    ("Auto Leveling Installed", 0x16, 0x02),
    ("Headlight Washer Installed", 0x16, 0x04),
    ("Halogen to Xenon Conversion Active", 0x17, 0x01),
    ("Halogen Deactivation", 0x17, 0x02),
    ("Disable Bulb Check", 0x25, 0x10),
    ("Xenon Ballast Type", 0x18, None),
]

VIN_OFFSET = 0x110  # Correct VIN offset
VIN_LENGTH = 17

class FRMEditorApp:
    def __init__(self, root):
        self.root = root
        root.title("FRM3 EEPROM Editor")
        
        self.eeprom = None
        self.filepath = None
        
        self.load_btn = tk.Button(root, text="Load EEPROM File", command=self.load_file)
        self.load_btn.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        self.save_btn = tk.Button(root, text="Save Modified EEPROM", command=self.save_file, state='disabled')
        self.save_btn.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        tk.Label(root, text="VIN:").grid(row=1, column=0, sticky="w", padx=5)
        self.vin_var = tk.StringVar()
        self.vin_entry = tk.Entry(root, textvariable=self.vin_var, width=25, state='disabled')
        self.vin_entry.grid(row=1, column=1, sticky="w", padx=5)
        self.update_vin_btn = tk.Button(root, text="Update VIN", command=self.update_vin, state='disabled')
        self.update_vin_btn.grid(row=1, column=2, padx=5)
        
        self.main_features_frame = tk.LabelFrame(root, text="Main Features")
        self.main_features_frame.grid(row=2, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        
        self.xenon_features_frame = tk.LabelFrame(root, text="Xenon / Halogen Features")
        self.xenon_features_frame.grid(row=3, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        
        self.main_vars = {}
        self.xenon_vars = {}
        
        for i, (name, offset, mask) in enumerate(coding_map):
            var = tk.IntVar()
            cb = tk.Checkbutton(self.main_features_frame, text=name, variable=var, state='disabled',
                                command=lambda i=i: self.toggle_main_feature(i))
            cb.grid(row=i//2, column=i%2, sticky='w', padx=5)
            self.main_vars[i] = var
        
        for i, (name, offset, mask) in enumerate(xenon_features):
            var = tk.IntVar()
            cb = tk.Checkbutton(self.xenon_features_frame, text=name, variable=var, state='disabled',
                                command=lambda i=i: self.toggle_xenon_feature(i))
            cb.grid(row=i//2, column=i%2, sticky='w', padx=5)
            self.xenon_vars[i] = var

    def load_file(self):
        path = filedialog.askopenfilename(title="Select EEPROM BIN file", filetypes=[("BIN files", "*.bin"), ("All files", "*.*")])
        if not path:
            return
        try:
            with open(path, 'rb') as f:
                data = bytearray(f.read())
            self.eeprom = data
            self.filepath = path
            self.save_btn.config(state='normal')
            self.vin_entry.config(state='normal')
            self.update_vin_btn.config(state='normal')

            # Enable all checkboxes
            for cb in self.main_features_frame.winfo_children():
                cb.config(state='normal')
            for cb in self.xenon_features_frame.winfo_children():
                cb.config(state='normal')

            self.update_all_checkboxes()
            messagebox.showinfo("Success", f"Loaded {len(data)} bytes from {path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")

    def save_file(self):
        if not self.eeprom or not self.filepath:
            messagebox.showwarning("No file", "No EEPROM loaded to save")
            return
        checksum = (256 - (sum(self.eeprom[:-1]) % 256)) % 256
        self.eeprom[-1] = checksum
        save_path = filedialog.asksaveasfilename(title="Save modified EEPROM as", defaultextension=".bin",
                                                 filetypes=[("BIN files", "*.bin"), ("All files", "*.*")])
        if not save_path:
            return
        try:
            with open(save_path, 'wb') as f:
                f.write(self.eeprom)
            messagebox.showinfo("Saved", f"Modified EEPROM saved to {save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")

    def update_all_checkboxes(self):
        for i, (name, offset, mask) in enumerate(coding_map):
            if offset >= len(self.eeprom):
                self.main_vars[i].set(0)
                continue
            val = self.eeprom[offset]
            if mask is None:
                self.main_vars[i].set(1 if val > 0 else 0)
            else:
                self.main_vars[i].set(1 if (val & mask) else 0)

            trace_id = getattr(self, f"_main_trace_{i}", None)
            if trace_id is not None:
                self.main_vars[i].trace_vdelete("w", trace_id)

            def cb_closure(i):
                def on_change(*args):
                    self.toggle_main_feature(i)
                return on_change

            trace_id = self.main_vars[i].trace("w", cb_closure(i))
            setattr(self, f"_main_trace_{i}", trace_id)

        for i, (name, offset, mask) in enumerate(xenon_features):
            if offset >= len(self.eeprom):
                self.xenon_vars[i].set(0)
                continue
            val = self.eeprom[offset]
            if mask is None:
                self.xenon_vars[i].set(1 if val > 0 else 0)
            else:
                self.xenon_vars[i].set(1 if (val & mask) else 0)

            trace_id = getattr(self, f"_xenon_trace_{i}", None)
            if trace_id is not None:
                self.xenon_vars[i].trace_vdelete("w", trace_id)

            def cb_closure(i):
                def on_change(*args):
                    self.toggle_xenon_feature(i)
                return on_change

            trace_id = self.xenon_vars[i].trace("w", cb_closure(i))
            setattr(self, f"_xenon_trace_{i}", trace_id)

        vin_bytes = self.eeprom[VIN_OFFSET:VIN_OFFSET + VIN_LENGTH]
        try:
            vin_str = vin_bytes.decode('ascii')
        except Exception:
            vin_str = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in vin_bytes)
        self.vin_var.set(vin_str)

    def toggle_main_feature(self, i):
        name, offset, mask = coding_map[i]
        val = self.eeprom[offset]
        var_val = self.main_vars[i].get()
        if mask is None:
            self.eeprom[offset] = 1 if var_val else 0
        else:
            if var_val:
                self.eeprom[offset] = val | mask
            else:
                self.eeprom[offset] = val & (~mask)

    def toggle_xenon_feature(self, i):
        name, offset, mask = xenon_features[i]
        val = self.eeprom[offset]
        var_val = self.xenon_vars[i].get()
        if mask is None:
            self.eeprom[offset] = 1 if var_val else 0
        else:
            if var_val:
                self.eeprom[offset] = val | mask
            else:
                self.eeprom[offset] = val & (~mask)

    def update_vin(self):
        vin_text = self.vin_var.get().strip()
        if len(vin_text) != VIN_LENGTH or any(c not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789" for c in vin_text.upper()):
            messagebox.showerror("Invalid VIN", f"VIN must be exactly {VIN_LENGTH} alphanumeric characters (A-Z,0-9).")
            return
        self.eeprom[VIN_OFFSET:VIN_OFFSET + VIN_LENGTH] = vin_text.encode('ascii')
        messagebox.showinfo("VIN Updated", "VIN updated successfully in EEPROM buffer.")

def main():
    root = tk.Tk()
    app = FRMEditorApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
