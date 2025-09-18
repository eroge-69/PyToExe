import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
from dataclasses import dataclass
from typing import Dict, List, Optional, Union
import struct
from pathlib import Path

@dataclass
class ItemStats:
    primary_stat: Optional[int] = None
    secondary_stat: Optional[int] = None
    level: Optional[int] = None
    rarity: Optional[int] = None
    manufacturer: Optional[int] = None
    item_class: Optional[int] = None
    flags: Optional[List[int]] = None

@dataclass
class DecodedItem:
    serial: str
    item_type: str
    item_category: str
    length: int
    stats: ItemStats
    raw_fields: Dict[str, Union[int, List[int]]]
    confidence: str

def bit_pack_decode(serial: str) -> bytes:
    if serial.startswith('@Ug'):
        payload = serial[3:]
    else:
        payload = serial

    char_map = {}
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=!$%&*()[]{}~`^_<>?#;'
    for i, c in enumerate(chars):
        char_map[c] = i

    bits = []
    for c in payload:
        if c in char_map:
            val = char_map[c]
            bits.extend(format(val, '06b'))

    bit_string = ''.join(bits)
    while len(bit_string) % 8 != 0:
        bit_string += '0'

    byte_data = bytearray()
    for i in range(0, len(bit_string), 8):
        byte_val = int(bit_string[i:i+8], 2)
        byte_data.append(byte_val)

    return bytes(byte_data)

def bit_pack_encode(data: bytes, prefix: str = '@Ug') -> str:
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=!$%&*()[]{}~`^_<>?#;'

    bit_string = ''.join(format(byte, '08b') for byte in data)

    while len(bit_string) % 6 != 0:
        bit_string += '0'

    result = []
    for i in range(0, len(bit_string), 6):
        chunk = bit_string[i:i+6]
        val = int(chunk, 2)
        if val < len(chars):
            result.append(chars[val])

    return prefix + ''.join(result)

def extract_fields(data: bytes) -> Dict[str, Union[int, List[int]]]:
    fields = {}

    if len(data) >= 4:
        fields['header_le'] = struct.unpack('<I', data[:4])[0]
        fields['header_be'] = struct.unpack('>I', data[:4])[0]

    if len(data) >= 8:
        fields['field2_le'] = struct.unpack('<I', data[4:8])[0]

    if len(data) >= 12:
        fields['field3_le'] = struct.unpack('<I', data[8:12])[0]

    stats_16 = []
    for i in range(0, min(len(data)-1, 20), 2):
        val16 = struct.unpack('<H', data[i:i+2])[0]
        fields[f'val16_at_{i}'] = val16
        if 100 <= val16 <= 10000:
            stats_16.append((i, val16))

    fields['potential_stats'] = stats_16

    flags = []
    for i in range(min(len(data), 20)):
        byte_val = data[i]
        fields[f'byte_{i}'] = byte_val
        if byte_val < 100:
            flags.append((i, byte_val))

    fields['potential_flags'] = flags

    return fields

def decode_weapon(data: bytes, serial: str) -> DecodedItem:
    fields = extract_fields(data)
    stats = ItemStats()

    if 'val16_at_0' in fields:
        stats.primary_stat = fields['val16_at_0']

    if 'val16_at_12' in fields:
        stats.secondary_stat = fields['val16_at_12']

    if 'byte_4' in fields:
        stats.manufacturer = fields['byte_4']

    if 'byte_8' in fields:
        stats.item_class = fields['byte_8']

    if 'byte_1' in fields:
        stats.rarity = fields['byte_1']

    if 'byte_13' in fields and fields['byte_13'] in [2, 34]:
        stats.level = fields['byte_13']

    confidence = "high" if len(data) in [24, 26] else "medium"

    return DecodedItem(
        serial=serial,
        item_type='r',
        item_category='weapon',
        length=len(data),
        stats=stats,
        raw_fields=fields,
        confidence=confidence
    )

def decode_equipment_e(data: bytes, serial: str) -> DecodedItem:
    fields = extract_fields(data)
    stats = ItemStats()

    if 'val16_at_2' in fields:
        stats.primary_stat = fields['val16_at_2']

    if 'val16_at_8' in fields:
        stats.secondary_stat = fields['val16_at_8']

    if 'val16_at_10' in fields and len(data) > 38:
        stats.level = fields['val16_at_10']

    if 'byte_1' in fields:
        stats.manufacturer = fields['byte_1']

    if 'byte_3' in fields:
        stats.item_class = fields['byte_3']

    if 'byte_9' in fields:
        stats.rarity = fields['byte_9']

    confidence = "high" if 'byte_1' in fields and fields['byte_1'] == 49 else "medium"

    return DecodedItem(
        serial=serial,
        item_type='e',
        item_category='equipment',
        length=len(data),
        stats=stats,
        raw_fields=fields,
        confidence=confidence
    )

def decode_equipment_d(data: bytes, serial: str) -> DecodedItem:
    fields = extract_fields(data)
    stats = ItemStats()

    if 'val16_at_4' in fields:
        stats.primary_stat = fields['val16_at_4']

    if 'val16_at_8' in fields:
        stats.secondary_stat = fields['val16_at_8']

    if 'val16_at_10' in fields:
        stats.level = fields['val16_at_10']

    if 'byte_5' in fields:
        stats.manufacturer = fields['byte_5']

    if 'byte_6' in fields:
        stats.item_class = fields['byte_6']

    if 'byte_14' in fields:
        stats.rarity = fields['byte_14']

    confidence = "high" if 'byte_5' in fields and fields['byte_5'] == 15 else "medium"

    return DecodedItem(
        serial=serial,
        item_type='d',
        item_category='equipment_alt',
        length=len(data),
        stats=stats,
        raw_fields=fields,
        confidence=confidence
    )

def decode_other_type(data: bytes, serial: str, item_type: str) -> DecodedItem:
    fields = extract_fields(data)
    stats = ItemStats()

    potential_stats = fields.get('potential_stats', [])
    if potential_stats:
        stats.primary_stat = potential_stats[0][1] if len(potential_stats) > 0 else None
        stats.secondary_stat = potential_stats[1][1] if len(potential_stats) > 1 else None

    if 'byte_1' in fields:
        stats.manufacturer = fields['byte_1']

    if 'byte_2' in fields:
        stats.rarity = fields['byte_2']

    category_map = {
        'w': 'weapon_special',
        'u': 'utility',
        'f': 'consumable',
        '!': 'special'
    }

    return DecodedItem(
        serial=serial,
        item_type=item_type,
        item_category=category_map.get(item_type, 'unknown'),
        length=len(data),
        stats=stats,
        raw_fields=fields,
        confidence="low"
    )

def decode_item_serial(serial: str) -> DecodedItem:
    try:
        data = bit_pack_decode(serial)

        if len(serial) >= 4 and serial.startswith('@Ug'):
            item_type = serial[3]
        else:
            item_type = '?'

        if item_type == 'r':
            return decode_weapon(data, serial)
        elif item_type == 'e':
            return decode_equipment_e(data, serial)
        elif item_type == 'd':
            return decode_equipment_d(data, serial)
        else:
            return decode_other_type(data, serial, item_type)

    except Exception as e:
        return DecodedItem(
            serial=serial,
            item_type='error',
            item_category='decode_failed',
            length=0,
            stats=ItemStats(),
            raw_fields={'error': str(e)},
            confidence="none"
        )

def encode_item_serial(decoded_item: DecodedItem) -> str:
    try:
        original_data = bit_pack_decode(decoded_item.serial)
        data = bytearray(original_data)

        if decoded_item.item_type == 'r':
            if decoded_item.stats.primary_stat is not None and len(data) >= 2:
                struct.pack_into('<H', data, 0, decoded_item.stats.primary_stat)
            if decoded_item.stats.secondary_stat is not None and len(data) >= 14:
                struct.pack_into('<H', data, 12, decoded_item.stats.secondary_stat)
            if decoded_item.stats.rarity is not None and len(data) >= 2:
                data[1] = decoded_item.stats.rarity
            if decoded_item.stats.manufacturer is not None and len(data) >= 5:
                data[4] = decoded_item.stats.manufacturer
            if decoded_item.stats.item_class is not None and len(data) >= 9:
                data[8] = decoded_item.stats.item_class

        elif decoded_item.item_type == 'e':
            if decoded_item.stats.primary_stat is not None and len(data) >= 4:
                struct.pack_into('<H', data, 2, decoded_item.stats.primary_stat)
            if decoded_item.stats.secondary_stat is not None and len(data) >= 10:
                struct.pack_into('<H', data, 8, decoded_item.stats.secondary_stat)
            if decoded_item.stats.manufacturer is not None and len(data) >= 2:
                data[1] = decoded_item.stats.manufacturer
            if decoded_item.stats.item_class is not None and len(data) >= 4:
                data[3] = decoded_item.stats.item_class
            if decoded_item.stats.rarity is not None and len(data) >= 10:
                data[9] = decoded_item.stats.rarity

        elif decoded_item.item_type == 'd':
            if decoded_item.stats.primary_stat is not None and len(data) >= 6:
                struct.pack_into('<H', data, 4, decoded_item.stats.primary_stat)
            if decoded_item.stats.secondary_stat is not None and len(data) >= 10:
                struct.pack_into('<H', data, 8, decoded_item.stats.secondary_stat)
            if decoded_item.stats.manufacturer is not None and len(data) >= 6:
                data[5] = decoded_item.stats.manufacturer
            if decoded_item.stats.item_class is not None and len(data) >= 7:
                data[6] = decoded_item.stats.item_class

        prefix = f'@Ug{decoded_item.item_type}'
        return bit_pack_encode(bytes(data), prefix)

    except Exception as e:
        print(f"Warning: Failed to encode item serial: {e}")
        return decoded_item.serial

class SerialCoderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Borderlands 4 Gear n Gun Editor")
        self.root.geometry("600x400")
        self.root.configure(bg="#2C2F33")

        self.decoded_item = None
        self.new_serial = None

        self.serial_label = tk.Label(self.root, text="Enter Serial:", bg="#2C2F33", fg="#FFFFFF", font=("Helvetica", 12))
        self.serial_label.pack(pady=10)

        self.serial_entry = tk.Entry(self.root, width=50, bg="#36393F", fg="#FFFFFF", insertbackground="#FFFFFF")
        self.serial_entry.pack(pady=5)

        self.decode_button = tk.Button(self.root, text="Decode", command=self.decode_serial, bg="#5865F2", fg="#FFFFFF")
        self.decode_button.pack(pady=10)

        self.stats_frame = tk.Frame(self.root, bg="#2C2F33")
        self.stats_frame.pack(pady=10, fill="both", expand=True)

        self.button_frame = tk.Frame(self.root, bg="#2C2F33")
        self.button_frame.pack(pady=5)

        self.raw_button = tk.Button(self.button_frame, text="Raw Data for Nerds", command=self.open_raw_data, state="disabled", bg="#5865F2", fg="#FFFFFF")
        self.raw_button.pack(side="left", padx=5)

        self.save_button = tk.Button(self.button_frame, text="Save & Encode", command=self.save_and_encode, state="disabled", bg="#43B581", fg="#FFFFFF")
        self.save_button.pack(side="left", padx=5)

        self.copy_button = tk.Button(self.button_frame, text="Copy New Serial", command=self.copy_serial, state="disabled", bg="#7289DA", fg="#FFFFFF")
        self.copy_button.pack(side="left", padx=5)

        self.output_label = tk.Label(self.root, text="", bg="#2C2F33", fg="#FFFFFF", font=("Helvetica", 12))
        self.output_label.pack(pady=10)

    def decode_serial(self):
        serial = self.serial_entry.get().strip()
        if not serial:
            messagebox.showerror("Error", "Please enter a serial.")
            return

        self.decoded_item = decode_item_serial(serial)
        if self.decoded_item.confidence == "none":
            messagebox.showerror("Error", "Failed to decode serial.")
            return

        self.display_stats()
        self.raw_button.config(state="normal")
        self.save_button.config(state="normal")
        self.copy_button.config(state="disabled")
        self.new_serial = None

    def display_stats(self):
        for widget in self.stats_frame.winfo_children():
            widget.destroy()

        stats = self.decoded_item.stats

        labels = [
            ("Primary Stat:", "Main weapon damage/equipment power", "primary_stat"),
            ("Secondary Stat:", "Secondary weapon/equipment stats", "secondary_stat"),
            ("Rarity:", "Item rarity level (affects item quality - common, uncommon, rare, etc.)", "rarity"),
            ("Manufacturer:", "Weapon/equipment manufacturer", "manufacturer"),
            ("Item Class:", "Specific weapon/equipment type", "item_class"),
            ("Level:", "Item level (when available)", "level")
        ]

        for label_text, desc, attr in labels:
            frame = tk.Frame(self.stats_frame, bg="#2C2F33")
            frame.pack(fill="x", pady=2)

            label = tk.Label(frame, text=label_text, bg="#2C2F33", fg="#FFFFFF", width=15, anchor="w")
            label.pack(side="left")

            entry = tk.Entry(frame, bg="#36393F", fg="#FFFFFF", insertbackground="#FFFFFF")
            entry.insert(0, str(getattr(stats, attr)) if getattr(stats, attr) is not None else "")
            entry.pack(side="left", fill="x", expand=True)
            setattr(self, f"{attr}_entry", entry)

            desc_label = tk.Label(frame, text=desc, bg="#2C2F33", fg="#8E9297", font=("Helvetica", 8))
            desc_label.pack(side="left", padx=5)

    def open_raw_data(self):
        raw_window = Toplevel(self.root)
        raw_window.title("Raw Data")
        raw_window.geometry("600x400")
        raw_window.configure(bg="#2C2F33")

        scroll = ttk.Scrollbar(raw_window)
        scroll.pack(side="right", fill="y")

        canvas = tk.Canvas(raw_window, bg="#2C2F33", yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True)

        scroll.config(command=canvas.yview)

        inner_frame = tk.Frame(canvas, bg="#2C2F33")
        canvas.create_window((0, 0), window=inner_frame, anchor="nw")

        for key, value in self.decoded_item.raw_fields.items():
            frame = tk.Frame(inner_frame, bg="#2C2F33")
            frame.pack(fill="x", pady=2)

            label = tk.Label(frame, text=f"{key}:", bg="#2C2F33", fg="#FFFFFF", width=20, anchor="w")
            label.pack(side="left")

            if isinstance(value, list):
                entry = tk.Entry(frame, bg="#36393F", fg="#FFFFFF", insertbackground="#FFFFFF")
                entry.insert(0, str(value))
                entry.pack(side="left", fill="x", expand=True)
                setattr(self, f"raw_{key}_entry", entry)
            else:
                entry = tk.Entry(frame, bg="#36393F", fg="#FFFFFF", insertbackground="#FFFFFF")
                entry.insert(0, str(value))
                entry.pack(side="left", fill="x", expand=True)
                setattr(self, f"raw_{key}_entry", entry)

        inner_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

        save_raw_button = tk.Button(raw_window, text="Save Raw Changes", command=self.save_raw_changes, bg="#43B581", fg="#FFFFFF")
        save_raw_button.pack(pady=10)

    def save_raw_changes(self):
        for key in self.decoded_item.raw_fields:
            if hasattr(self, f"raw_{key}_entry"):
                entry = getattr(self, f"raw_{key}_entry")
                value_str = entry.get().strip()
                if 'val16_at' in key or 'header' in key or 'field' in key:
                    try:
                        self.decoded_item.raw_fields[key] = int(value_str)
                    except:
                        pass
                elif 'byte_' in key:
                    try:
                        self.decoded_item.raw_fields[key] = int(value_str)
                    except:
                        pass
                elif isinstance(self.decoded_item.raw_fields[key], list):
                    try:
                        self.decoded_item.raw_fields[key] = eval(value_str)
                    except:
                        pass
        messagebox.showinfo("Info", "Raw changes saved.")

    def save_and_encode(self):
        stats = self.decoded_item.stats

        try:
            if hasattr(self, "primary_stat_entry"):
                stats.primary_stat = int(self.primary_stat_entry.get()) if self.primary_stat_entry.get() else None
            if hasattr(self, "secondary_stat_entry"):
                stats.secondary_stat = int(self.secondary_stat_entry.get()) if self.secondary_stat_entry.get() else None
            if hasattr(self, "rarity_entry"):
                stats.rarity = int(self.rarity_entry.get()) if self.rarity_entry.get() else None
            if hasattr(self, "manufacturer_entry"):
                stats.manufacturer = int(self.manufacturer_entry.get()) if self.manufacturer_entry.get() else None
            if hasattr(self, "item_class_entry"):
                stats.item_class = int(self.item_class_entry.get()) if self.item_class_entry.get() else None
            if hasattr(self, "level_entry"):
                stats.level = int(self.level_entry.get()) if self.level_entry.get() else None
        except ValueError:
            messagebox.showerror("Error", "Invalid integer value in stats.")
            return

        self.new_serial = encode_item_serial(self.decoded_item)
        self.output_label.config(text=f"New Serial: {self.new_serial}")
        self.copy_button.config(state="normal")
        messagebox.showinfo("Success", f"Encoded new serial: {self.new_serial}")

    def copy_serial(self):
        if self.new_serial:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.new_serial)
            messagebox.showinfo("Success", "New serial copied to clipboard!")
        else:
            messagebox.showerror("Error", "No new serial available to copy.")

if __name__ == "__main__":
    root = tk.Tk()
    app = SerialCoderGUI(root)
    root.mainloop()