import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re

# Where renamed files end up
OUTPUT_DIR = "output"

# All of your categories and items
DESCRIPTION_MAP = {
    "Electrical":  ["Cable", "Connector", "Sensor", "Relay", "Switch", "Fuse", "Cover"],
    "Mechanical":  ["Gear", "Bearing", "Shaft", "Coupling", "Bracket", "Housing", "Cover"],
    "Hydraulic":   ["Pump", "Valve", "Cylinder", "Hose", "Filter", "Seal", "Cover"],
    "Pneumatic":   ["Actuator", "Regulator", "Compressor", "Hose", "Nozzle"],
    "Electronic":  ["PCB", "Microcontroller", "Display", "Module", "Power Supply", "Cover"],
    "Structural":  ["Frame", "Panel", "Beam", "Support", "Enclosure", "Cover"],
    "Consumables": ["Tape", "Glue", "Oil", "Grease", "Cleaner"],
    "Fasteners":   ["Screw", "Bolt", "Nut", "Washer", "Rivet", "Clip"],
    "Packaging":   ["Box", "Bag", "Label", "Wrap", "Insert"]
}

class AutocompleteCombobox(ttk.Combobox):
    """A ttk.Combobox that filters its dropdown as you type."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._completion_list = []
        self.bind('<KeyRelease>', self._on_keyrelease)

    def set_completion_list(self, completion_list):
        self._completion_list = sorted(completion_list, key=str.lower)
        self['values'] = self._completion_list

    def _on_keyrelease(self, event):
        if event.keysym in ('BackSpace','Left','Right','Up','Down','Return','Escape','Tab'):
            return
        text = self.get()
        filtered = (
            [item for item in self._completion_list if text.lower() in item.lower()]
            if text else self._completion_list
        )
        self['values'] = filtered
        self.set(text)
        if filtered:
            self.event_generate('<Down>')

class STLRenamer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("STL File Renamer")
        self.geometry("550x420") # Adjusted for new layout
        self.resizable(False, False)
        self.stl_path = ""

        self.main_frame = ttk.Frame(self, padding=10)
        self.main_frame.pack(fill="both", expand=True)
        self.main_frame.columnconfigure(0, weight=1)

        self._build_widgets()

    def _build_widgets(self):
        pad = {"padx": 6, "pady": 4}

        # --- Step 1: File selection ---
        file_frame = ttk.LabelFrame(self.main_frame, text="Step 1: Select STL File", padding=10)
        file_frame.grid(row=0, column=0, sticky="ew", **pad)
        file_frame.columnconfigure(1, weight=1)

        ttk.Button(file_frame, text="Browse…", command=self.browse_file).grid(row=0, column=0, **pad)
        self.file_label = ttk.Label(file_frame, text="No file selected", anchor="w")
        self.file_label.grid(row=0, column=1, sticky="ew", **pad)

        # --- Step 2: Part Details ---
        input_frame = ttk.LabelFrame(self.main_frame, text="Step 2: Enter Part Details", padding=10)
        input_frame.grid(row=1, column=0, sticky="ew", **pad)
        input_frame.columnconfigure(1, weight=1)

        ttk.Label(input_frame, text="Part Type:").grid(row=0, column=0, sticky="e", **pad)
        self.type_combo = AutocompleteCombobox(input_frame, state="normal")
        self.type_combo.grid(row=0, column=1, sticky="ew", **pad)
        self.type_combo.set_completion_list(list(DESCRIPTION_MAP.keys()))
        self.type_combo.bind("<<ComboboxSelected>>", self._update_descriptions)
        self.type_combo.bind("<KeyRelease>", self._update_preview)

        ttk.Label(input_frame, text="Description:").grid(row=1, column=0, sticky="e", **pad)
        self.desc_combo = AutocompleteCombobox(input_frame, state="normal")
        self.desc_combo.grid(row=1, column=1, sticky="ew", **pad)
        self.desc_combo.bind("<<ComboboxSelected>>", self._update_preview)
        self.desc_combo.bind("<KeyRelease>", self._update_preview)

        ttk.Label(input_frame, text="Part Number:").grid(row=2, column=0, sticky="e", **pad)
        self.part_number_entry = ttk.Entry(input_frame)
        self.part_number_entry.grid(row=2, column=1, sticky="ew", **pad)
        self.part_number_entry.bind("<KeyRelease>", self._update_preview)

        # --- Step 3: Preview & Action ---
        action_frame = ttk.LabelFrame(self.main_frame, text="Step 3: Preview & Save", padding=10)
        action_frame.grid(row=2, column=0, sticky="ew", **pad)
        action_frame.columnconfigure(0, weight=1)

        self.preview_label = ttk.Label(
            action_frame,
            text="Preview: <type>_<desc>_<number>.stl",
            foreground="blue"
        )
        self.preview_label.grid(row=0, column=0, sticky="w", **pad)

        self.rename_btn = ttk.Button(
            action_frame, text="Rename and Save", command=self.rename_and_save
        )
        self.rename_btn.grid(row=1, column=0, pady=(8, 0))

        # --- Status Bar ---
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(self, textvariable=self.status_var, relief="sunken", anchor="w")
        self.status_label.pack(fill="x", side="bottom")

    def _update_descriptions(self, event=None):
        ptype = self.type_combo.get()
        options = DESCRIPTION_MAP.get(ptype, [])
        self.desc_combo.set_completion_list(options)
        self.desc_combo.set("")
        self._update_preview()

    def _update_preview(self, event=None):
        ptype    = self.type_combo.get().strip() or "<type>"
        desc     = self.desc_combo.get().strip() or "<desc>"
        part_num = self.part_number_entry.get().strip() or "<number>"
        preview  = f"{ptype}_{desc}_{part_num}.stl"
        self.preview_label.config(text=f"Preview: {preview}")

    def browse_file(self):
        path = filedialog.askopenfilename(
            title="Select STL File",
            filetypes=[("STL files", "*.stl")],
            defaultextension=".stl"
        )
        if path:
            self.stl_path = path
            self.file_label.config(text=os.path.basename(path))
            self.status_var.set("Ready")

    def sanitize_filename(self, name):
        """Replace illegal characters with underscores."""
        return re.sub(r'[\\\/:*?"<>|]', '_', name)

    def resolve_collision(self, dest):
        """If dest exists, prompt to overwrite, auto-increment, or cancel."""
        base, ext = os.path.splitext(dest)
        version = 2
        while os.path.exists(dest):
            response = messagebox.askyesnocancel(
                "File Exists",
                f"A file named '{os.path.basename(dest)}' already exists.\n\n"
                "Yes: overwrite it.\n"
                "No: save as a new version (_v2, _v3, …).\n"
                "Cancel: abort the operation.",
                icon='warning'
            )
            if response is None:
                return None          # Cancel
            if response:
                return dest          # Overwrite
            # No → auto-increment
            dest = f"{base}_v{version}{ext}"
            version += 1
        return dest

    def rename_and_save(self):
        ptype    = self.type_combo.get().strip()
        desc     = self.desc_combo.get().strip()
        part_num = self.part_number_entry.get().strip()

        if not (ptype and desc and part_num):
            self.status_var.set("Error: Please fill in Part Type, Description, and Part Number.")
            return

        if not self.stl_path:
            self.status_var.set("Error: Please select an existing .stl file.")
            return

        raw_name  = f"{ptype}_{desc}_{part_num}.stl"
        clean_name = self.sanitize_filename(raw_name)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        dest = os.path.join(OUTPUT_DIR, clean_name)

        # Handle collision (overwrite, version, or cancel)
        dest = self.resolve_collision(dest)
        if dest is None:
            self.status_var.set("Cancelled: File rename aborted.")
            return

        try:
            shutil.copy2(self.stl_path, dest)
            self.status_var.set(f"Success: File saved as {os.path.basename(dest)}")
        except Exception as e:
            self.status_var.set(f"Error: Failed to save file: {e}")

if __name__ == "__main__":
    app = STLRenamer()
    app.mainloop()
