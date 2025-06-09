import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os

# --- P-FLASH Features including Xenon Mode ---
pflash_feature_names = [
    "Xenon Mode",
    "Xenon Headlights",
    "Bulb Failure Monitoring",
    "Auto Leveling",
    "Mirror Folding",
    "High Beam Assistant",
    "Headlight Washer",
    "Daytime Running Lights (DRL)",
    "Cornering Lights",
    "Fog Lights Front",
    "Rain Sensor Control",
    "Welcome Light Sequence",
    "Footwell Lighting",
    "Comfort Blinker",
    "Bulb Check Disable",
    "Auto Headlight Activation"
]

pflash_patch_offsets = {
    "xenon_headlights": (0x30, 0x04),
    "bulb_failure_monitoring": (0x31, 0x20),
    "auto_leveling": (0x32, 0x08),
    "mirror_folding": (0x40, 0x80),
    "high_beam_assistant": (0x42, 0x10),
    "headlight_washer": (0x33, 0x40),
    "drl": (0x34, 0x02),
    "cornering_lights": (0x35, 0x08),
    "fog_lights_front": (0x36, 0x10),
    "rain_sensor_control": (0x37, 0x04),
    "welcome_light_sequence": (0x38, 0x01),
    "footwell_lighting": (0x39, 0x20),
    "comfort_blinker": (0x3A, 0x08),
    "bulb_check_disable": (0x3B, 0x10),
    "auto_headlight_activation": (0x3C, 0x04),
}

pflash_feature_descriptions = {
    "Xenon Mode": "Enable Xenon headlights and disable halogen related functions.",
    "Xenon Headlights": "Enables xenon headlight control and functionality.",
    "Bulb Failure Monitoring": "Detects and warns if a filament bulb is faulty.",
    "Auto Leveling": "Automatically adjusts the headlight beam height for proper illumination.",
    "Mirror Folding": "Automatically folds side mirrors when locking/unlocking the car.",
    "High Beam Assistant": "Automatically switches high beams on/off depending on traffic.",
    "Headlight Washer": "Activates washers for xenon headlights to clean lenses.",
    "Daytime Running Lights (DRL)": "Enables daytime running lights for better visibility.",
    "Cornering Lights": "Lights that activate when turning corners for better illumination.",
    "Fog Lights Front": "Controls front fog lights for improved visibility in fog.",
    "Rain Sensor Control": "Enables automatic windshield wipers based on rain detection.",
    "Welcome Light Sequence": "Activates light animations when unlocking or locking the car.",
    "Footwell Lighting": "Illuminates the footwell area inside the car cabin.",
    "Comfort Blinker": "Enable comfort blinker (three-flash turn signals).",
    "Bulb Check Disable": "Disable bulb check to avoid false warnings.",
    "Auto Headlight Activation": "Enables automatic switching of headlights."
}

# --- EEPROM Features including Xenon Mode and combined Power Windows ---
eeprom_feature_names = [
    "Power Windows",
    "Xenon Mode",
    "Central Locking",
    "Mirror Folding",
    "Interior Light Delay",
    "Alarm System Active",
    "Seat Belt Warning",
    "Daytime Running Lights (DRL)",
    "Fog Lights Front",
    "Automatic Headlight Activation",
    "Keyless Entry Active",
    "Warning Chimes Enabled",
    "Comfort Blinker",
    "Panic Alarm"
]

eeprom_patch_offsets = {
    "power_windows": (0x10, 0x0F),
    "central_locking": (0x11, 0x10),
    "mirror_folding": (0x12, 0x80),
    "interior_light_delay": (0x13, 0x04),
    "alarm_active": (0x14, 0x20),
    "seat_belt_warning": (0x15, 0x01),
    "drl": (0x34, 0x02),
    "fog_lights_front": (0x36, 0x10),
    "auto_headlight": (0x16, 0x08),
    "keyless_entry": (0x17, 0x10),
    "warning_chimes": (0x18, 0x04),
    "comfort_blinker": (0x19, 0x08),
    "panic_alarm": (0x1A, 0x02),
}

eeprom_feature_descriptions = {
    "Power Windows": "Enable or disable all power windows.",
    "Xenon Mode": "Enable Xenon headlights and disable halogen related functions.",
    "Central Locking": "Controls central locking system activation.",
    "Mirror Folding": "Enable automatic mirror folding on lock/unlock.",
    "Interior Light Delay": "Sets delay time for interior lights after locking/unlocking.",
    "Alarm System Active": "Enable or disable vehicle alarm system.",
    "Seat Belt Warning": "Toggle seat belt warning chimes and indicators.",
    "Daytime Running Lights (DRL)": "Enable daytime running lights in EEPROM logic.",
    "Fog Lights Front": "Control front fog lights via EEPROM settings.",
    "Automatic Headlight Activation": "Enable auto headlight on/off via EEPROM.",
    "Keyless Entry Active": "Enable or disable keyless entry system.",
    "Warning Chimes Enabled": "Toggle audible warning chimes on/off.",
    "Comfort Blinker": "Enable comfort blinker (three-flash turn signals).",
    "Panic Alarm": "Activate or deactivate panic alarm function."
}

# Offsets and lengths for HW number and FRM part number in EEPROM and P-FLASH
HW_OFFSET_EEPROM = 0x100
HW_LEN_EEPROM = 4
FRM_OFFSET_EEPROM = 0x120
FRM_LEN_EEPROM = 12

HW_OFFSET_PFLASH = 0x200
HW_LEN_PFLASH = 4
FRM_OFFSET_PFLASH = 0x220
FRM_LEN_PFLASH = 12

def get_feature_status(data, offset, mask):
    return bool(data[offset] & mask)

def set_feature_status(data, offset, mask, enable):
    if enable:
        data[offset] |= mask
    else:
        data[offset] &= (~mask) & 0xFF

def read_ascii_string(data, offset, length):
    if data is None or len(data) < offset + length:
        return "Unknown"
    raw_bytes = data[offset:offset+length]
    try:
        return raw_bytes.decode('ascii', errors='ignore').strip('\x00 ').strip()
    except:
        return "Unknown"

class TabFeatureEditor(tk.Frame):
    def __init__(self, parent, feature_names, feature_descriptions, patch_offsets, save_callback):
        super().__init__(parent)
        self.feature_names = feature_names
        self.feature_descriptions = feature_descriptions
        self.patch_offsets = patch_offsets
        self.data = None
        self.check_vars = {}
        self.checkbuttons = {}
        self.save_callback = save_callback

        self.create_widgets()

    def create_widgets(self):
        container = tk.Frame(self)
        container.pack(fill='both', expand=True)

        # Left frame: checkboxes
        self.chk_frame = tk.Frame(container)
        self.chk_frame.pack(side='left', padx=10, fill='y')

        # Xenon Mode checkbox first (special handling)
        self.xenon_var = tk.BooleanVar(value=False)
        self.xenon_chk = tk.Checkbutton(self.chk_frame, text="Xenon Mode", variable=self.xenon_var,
                                        command=self.on_xenon_toggle, wraplength=250, justify='left')
        self.xenon_chk.pack(anchor='w', pady=5)
        self.check_vars["Xenon Mode"] = self.xenon_var
        self.checkbuttons["Xenon Mode"] = self.xenon_chk

        # Other features except Xenon Mode
        for name in self.feature_names:
            if name == "Xenon Mode":
                continue
            var = tk.BooleanVar(value=False)
            chk = tk.Checkbutton(self.chk_frame, text=name, variable=var, state='disabled', wraplength=250, justify='left')
            chk.pack(anchor='w', pady=2)
            self.check_vars[name] = var
            self.checkbuttons[name] = chk

        # Right frame: description box
        desc_frame = tk.Frame(container)
        desc_frame.pack(side='left', padx=10, fill='both', expand=True)

        desc_label = tk.Label(desc_frame, text="Feature Descriptions", font=("Arial", 12, "bold"))
        desc_label.pack(anchor='nw')

        self.desc_text = scrolledtext.ScrolledText(desc_frame, width=40, height=22, wrap='word', state='disabled')
        self.desc_text.pack(fill='both', expand=True, pady=5)

        self.desc_text.config(state='normal')
        for name in self.feature_names:
            desc = self.feature_descriptions.get(name, "No description available.")
            self.desc_text.insert('end', f"{name}:\n{desc}\n\n")
        self.desc_text.config(state='disabled')

        self.save_btn = tk.Button(self, text="Save", state='disabled', command=self.on_save)
        self.save_btn.pack(pady=10)

    def on_xenon_toggle(self):
        enabled = self.xenon_var.get()
        xenon_related = {
            "Xenon Headlights": True,
            "Auto Leveling": True,
            "Headlight Washer": True,
            "Bulb Check Disable": True,
            "Bulb Failure Monitoring": False,
        }
        for name, should_enable in xenon_related.items():
            if name in self.check_vars:
                self.check_vars[name].set(should_enable if enabled else not should_enable)
                self.checkbuttons[name].config(state='disabled' if enabled else 'normal')

    def load_data(self, data):
        self.data = data
        self.save_btn.config(state='normal')
        for chk in self.checkbuttons.values():
            chk.config(state='normal')
        self.xenon_chk.config(state='normal')

        xenon_enabled = self.check_xenon_mode_enabled()
        self.xenon_var.set(xenon_enabled)
        self.on_xenon_toggle()

        for name in self.feature_names:
            if name == "Xenon Mode":
                continue
            key = name.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_')
            offset, mask = self.patch_offsets.get(key, (None, None))
            if offset is not None and offset < len(self.data):
                if key == "power_windows":
                    enabled = (self.data[offset] & mask) != 0
                else:
                    enabled = get_feature_status(self.data, offset, mask)
                self.check_vars[name].set(enabled)
            else:
                self.check_vars[name].set(False)

    def check_xenon_mode_enabled(self):
        xenon_bits = [
            ("xenon_headlights", True),
            ("auto_leveling", True),
            ("headlight_washer", True),
            ("bulb_failure_monitoring", False),
            ("bulb_check_disable", True),
        ]
        for key, should_be_enabled in xenon_bits:
            offset, mask = self.patch_offsets.get(key, (None, None))
            if offset is None or offset >= len(self.data):
                continue
            enabled = get_feature_status(self.data, offset, mask)
            if enabled != should_be_enabled:
                return False
        return True

    def apply_changes(self):
        if self.data is None:
            return None

        xenon_enabled = self.xenon_var.get()
        xenon_bits = [
            ("xenon_headlights", True),
            ("auto_leveling", True),
            ("headlight_washer", True),
            ("bulb_failure_monitoring", False),
            ("bulb_check_disable", True),
        ]
        for key, should_enable in xenon_bits:
            offset, mask = self.patch_offsets.get(key, (None, None))
            if offset is not None and offset < len(self.data):
                set_feature_status(self.data, offset, mask, should_enable if xenon_enabled else not should_enable)

        for name in self.feature_names:
            if name == "Xenon Mode" or name in ["Xenon Headlights", "Auto Leveling", "Headlight Washer",
                                               "Bulb Failure Monitoring", "Bulb Check Disable"]:
                continue
            key = name.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_')
            offset, mask = self.patch_offsets.get(key, (None, None))
            if offset is not None and offset < len(self.data):
                enabled = self.check_vars[name].get()
                if key == "power_windows":
                    if enabled:
                        self.data[offset] |= mask
                    else:
                        self.data[offset] &= (~mask) & 0xFF
                else:
                    set_feature_status(self.data, offset, mask, enabled)

        return self.data

    def on_save(self):
        if self.save_callback:
            self.save_callback(self)

class FRM3PFlashEEPROMApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BMW FRM3 P-Flash & EEPROM Feature Editor")
        self.geometry("720x750")
        self.resizable(False, False)

        self.pflash_data = None
        self.eeprom_data = None
        self.current_filetype = None
        self.current_filepath = None

        self.create_widgets()

    def create_widgets(self):
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        open_pflash_btn = tk.Button(btn_frame, text="Open P-FLASH.bin", command=self.open_pflash)
        open_pflash_btn.pack(side='left', padx=10)

        open_eeprom_btn = tk.Button(btn_frame, text="Open EEPROM.bin", command=self.open_eeprom)
        open_eeprom_btn.pack(side='left', padx=10)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        self.pflash_tab = TabFeatureEditor(
            self.notebook,
            pflash_feature_names,
            pflash_feature_descriptions,
            pflash_patch_offsets,
            save_callback=self.save_pflash
        )
        self.notebook.add(self.pflash_tab, text="P-FLASH Features")

        self.eeprom_tab = TabFeatureEditor(
            self.notebook,
            eeprom_feature_names,
            eeprom_feature_descriptions,
            eeprom_patch_offsets,
            save_callback=self.save_eeprom
        )
        self.notebook.add(self.eeprom_tab, text="EEPROM Features")

        self.file_label = tk.Label(self, text="No file loaded")
        self.file_label.pack()

        self.hw_label = tk.Label(self, text="HW Number: N/A")
        self.hw_label.pack()

        self.frm_label = tk.Label(self, text="FRM Part Number: N/A")
        self.frm_label.pack()

    def open_pflash(self):
        self.open_file("pflash")

    def open_eeprom(self):
        self.open_file("eeprom")

    def open_file(self, filetype):
        title = "Open P-FLASH.bin" if filetype == "pflash" else "Open EEPROM.bin"
        path = filedialog.askopenfilename(
            title=title,
            filetypes=[("Binary files", "*.bin"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            with open(path, "rb") as f:
                data = bytearray(f.read())
            self.current_filepath = path
            self.current_filetype = filetype

            if filetype == "pflash":
                self.pflash_data = data
                self.pflash_tab.load_data(data)
                self.notebook.select(self.pflash_tab)
                hw = read_ascii_string(data, HW_OFFSET_PFLASH, HW_LEN_PFLASH)
                frm = read_ascii_string(data, FRM_OFFSET_PFLASH, FRM_LEN_PFLASH)
            else:
                self.eeprom_data = data
                self.eeprom_tab.load_data(data)
                self.notebook.select(self.eeprom_tab)
                hw = read_ascii_string(data, HW_OFFSET_EEPROM, HW_LEN_EEPROM)
                frm = read_ascii_string(data, FRM_OFFSET_EEPROM, FRM_LEN_EEPROM)

            self.file_label.config(text=f"Loaded: {os.path.basename(path)} ({filetype.upper()})")
            self.hw_label.config(text=f"HW Number: {hw}")
            self.frm_label.config(text=f"FRM Part Number: {frm}")

            messagebox.showinfo("Success", f"Loaded {os.path.basename(path)} successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file:\n{e}")

    def save_pflash(self, tab):
        data = tab.apply_changes()
        if data is None:
            messagebox.showwarning("No Data", "No P-FLASH data to save.")
            return
        self.save_file_dialog(data, "P-FLASH_patched.bin")

    def save_eeprom(self, tab):
        data = tab.apply_changes()
        if data is None:
            messagebox.showwarning("No Data", "No EEPROM data to save.")
            return
        self.save_file_dialog(data, "EEPROM_patched.bin")

    def save_file_dialog(self, data, default_name):
        save_path = filedialog.asksaveasfilename(
            defaultextension=".bin",
            initialfile=default_name,
            filetypes=[("Binary files", "*.bin"), ("All files", "*.*")],
            title="Save patched file"
        )
        if not save_path:
            return
        try:
            with open(save_path, "wb") as f:
                f.write(data)
            messagebox.showinfo("Saved", f"Patched file saved as:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file:\n{e}")

if __name__ == "__main__":
    app = FRM3PFlashEEPROMApp()
    app.mainloop()
