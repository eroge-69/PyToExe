import tkinter as tk
from tkinter import ttk, messagebox, Toplevel, filedialog
from dataclasses import dataclass
from typing import Dict, List, Optional, Union, Tuple
import struct
from pathlib import Path
import datetime

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
    original_binary: bytes
    original_prefix: str
    original_payload: str
    data_positions: List[int]
    char_offsets: List[int]
    weapon_name: Optional[str] = None

WEAPON_NAMES = {
    'd_t@': 'Jakobs Shotgun',
    'bV{r': 'Jakobs Pistol', 
    'y3L+2}': 'Jakobs Sniper',
    'eU_{': 'Maliwan Shotgun',
    'w$Yw2}': 'Maliwan SMG',
    'velk2}': 'Vladof AR',
    'xFw!2}': 'Vladof SMG',
    'xp/&2}': 'Ripper Sniper',
    'ct)%': 'Torgue Pistol',
    'fs(8': 'Daedalus AR',
    'b)Kv': 'Order Pistol',
    'y>^2}': 'Order Sniper'
}

def get_weapon_name(serial: str) -> Optional[str]:
    if not serial.startswith('@Ug'):
        return None
    
    prefix = serial[3:12]
    
    for code, name in WEAPON_NAMES.items():
        if prefix.startswith(code):
            return name
    
    return None

def bit_pack_decode(serial: str) -> Tuple[bytes, str, List[int], List[int]]:
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=!$%&*()[]{}~`^_<>?#;'
    char_map = {c: i for i, c in enumerate(chars)}

    if serial.startswith('@Ug'):
        original_prefix = '@Ug'
        payload = serial[3:]
    else:
        original_prefix = ''
        payload = serial

    bits = []
    data_positions = []
    char_offsets = []
    for idx, c in enumerate(payload):
        if c in char_map:
            val = char_map[c]
            bits.extend(format(val % 64, '06b'))
            data_positions.append(idx)
            char_offsets.append(val // 64)

    bit_string = ''.join(bits)
    while len(bit_string) % 8 != 0:
        bit_string += '0'

    byte_data = bytearray()
    for i in range(0, len(bit_string), 8):
        byte_val = int(bit_string[i:i+8], 2)
        byte_data.append(byte_val)

    return bytes(byte_data), original_prefix, data_positions, char_offsets

def bit_pack_encode(modified_data: bytes, original_prefix: str, original_payload: str, data_positions: List[int], char_offsets: List[int]) -> str:
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=!$%&*()[]{}~`^_<>?#;'

    bit_string = ''.join(format(byte, '08b') for byte in modified_data)

    target_bit_length = len(data_positions) * 6
    if len(bit_string) > target_bit_length:
        bit_string = bit_string[:target_bit_length]
    else:
        bit_string += '0' * (target_bit_length - len(bit_string))

    new_data_chars = []
    for idx, chunk_start in enumerate(range(0, target_bit_length, 6)):
        chunk = bit_string[chunk_start:chunk_start+6]
        val = int(chunk, 2)
        offset = char_offsets[idx]
        if offset == 1 and val <= 20:
            new_char = chars[val + 64]
        else:
            new_char = chars[val]
        new_data_chars.append(new_char)

    new_payload_list = list(original_payload)
    for idx, pos in enumerate(data_positions):
        new_payload_list[pos] = new_data_chars[idx]

    new_payload = ''.join(new_payload_list)
    new_serial = original_prefix + new_payload

    return new_serial

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

def decode_weapon(data: bytes, serial: str, original_prefix: str, payload: str, data_positions: List[int], char_offsets: List[int]) -> DecodedItem:
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

    weapon_name = get_weapon_name(serial)
    
    confidence = "high" if len(data) in [24, 26] else "medium"

    return DecodedItem(
        serial=serial,
        item_type='r',
        item_category='weapon',
        length=len(data),
        stats=stats,
        raw_fields=fields,
        confidence=confidence,
        original_binary=data,
        original_prefix=original_prefix,
        original_payload=payload,
        data_positions=data_positions,
        char_offsets=char_offsets,
        weapon_name=weapon_name
    )

def decode_equipment_e(data: bytes, serial: str, original_prefix: str, payload: str, data_positions: List[int], char_offsets: List[int]) -> DecodedItem:
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

    weapon_name = get_weapon_name(serial)
    
    confidence = "high" if 'byte_1' in fields and fields['byte_1'] == 49 else "medium"

    return DecodedItem(
        serial=serial,
        item_type='e',
        item_category='equipment',
        length=len(data),
        stats=stats,
        raw_fields=fields,
        confidence=confidence,
        original_binary=data,
        original_prefix=original_prefix,
        original_payload=payload,
        data_positions=data_positions,
        char_offsets=char_offsets,
        weapon_name=weapon_name
    )

def decode_equipment_d(data: bytes, serial: str, original_prefix: str, payload: str, data_positions: List[int], char_offsets: List[int]) -> DecodedItem:
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

    weapon_name = get_weapon_name(serial)
    
    confidence = "high" if 'byte_5' in fields and fields['byte_5'] == 15 else "medium"

    return DecodedItem(
        serial=serial,
        item_type='d',
        item_category='equipment_alt',
        length=len(data),
        stats=stats,
        raw_fields=fields,
        confidence=confidence,
        original_binary=data,
        original_prefix=original_prefix,
        original_payload=payload,
        data_positions=data_positions,
        char_offsets=char_offsets,
        weapon_name=weapon_name
    )

def decode_other_type(data: bytes, serial: str, item_type: str, original_prefix: str, payload: str, data_positions: List[int], char_offsets: List[int]) -> DecodedItem:
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

    if 'byte_3' in fields:
        stats.item_class = fields['byte_3']

    if 'val16_at_10' in fields:
        stats.level = fields['val16_at_10']

    weapon_name = get_weapon_name(serial)
    
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
        confidence="low",
        original_binary=data,
        original_prefix=original_prefix,
        original_payload=payload,
        data_positions=data_positions,
        char_offsets=char_offsets,
        weapon_name=weapon_name
    )

def decode_item_serial(serial: str) -> DecodedItem:
    try:
        data, original_prefix, data_positions, char_offsets = bit_pack_decode(serial)

        payload = serial[len(original_prefix):] if original_prefix else serial

        if len(serial) >= 4 and serial.startswith('@Ug'):
            item_type = serial[3]
        else:
            item_type = '?'

        if item_type == 'r':
            return decode_weapon(data, serial, original_prefix, payload, data_positions, char_offsets)
        elif item_type == 'e':
            return decode_equipment_e(data, serial, original_prefix, payload, data_positions, char_offsets)
        elif item_type == 'd':
            return decode_equipment_d(data, serial, original_prefix, payload, data_positions, char_offsets)
        else:
            return decode_other_type(data, serial, item_type, original_prefix, payload, data_positions, char_offsets)

    except Exception as e:
        return DecodedItem(
            serial=serial,
            item_type='error',
            item_category='decode_failed',
            length=0,
            stats=ItemStats(),
            raw_fields={'error': str(e)},
            confidence="none",
            original_binary=b'',
            original_prefix='',
            original_payload='',
            data_positions=[],
            char_offsets=[],
            weapon_name=None
        )

def encode_item_serial(decoded_item: DecodedItem) -> str:
    try:
        data = bytearray(decoded_item.original_binary)
        
        modified = False
        stats = decoded_item.stats
        
        if decoded_item.item_type == 'r':
            if stats.primary_stat is not None and stats.primary_stat != decoded_item.raw_fields.get('val16_at_0', None) and len(data) >= 2:
                struct.pack_into('<H', data, 0, stats.primary_stat)
                modified = True
                
            if stats.secondary_stat is not None and stats.secondary_stat != decoded_item.raw_fields.get('val16_at_12', None) and len(data) >= 14:
                struct.pack_into('<H', data, 12, stats.secondary_stat)
                modified = True
                
            if stats.rarity is not None and stats.rarity != decoded_item.raw_fields.get('byte_1', None) and len(data) >= 2:
                data[1] = stats.rarity
                modified = True
                    
            if stats.manufacturer is not None and stats.manufacturer != decoded_item.raw_fields.get('byte_4', None) and len(data) >= 5:
                data[4] = stats.manufacturer
                modified = True
                    
            if stats.item_class is not None and stats.item_class != decoded_item.raw_fields.get('byte_8', None) and len(data) >= 9:
                data[8] = stats.item_class
                modified = True

            if stats.level is not None and stats.level != decoded_item.raw_fields.get('byte_13', None) and len(data) >= 14:
                data[13] = stats.level
                modified = True

        elif decoded_item.item_type == 'e':
            if stats.primary_stat is not None and stats.primary_stat != decoded_item.raw_fields.get('val16_at_2', None) and len(data) >= 4:
                struct.pack_into('<H', data, 2, stats.primary_stat)
                modified = True
                
            if stats.secondary_stat is not None and stats.secondary_stat != decoded_item.raw_fields.get('val16_at_8', None) and len(data) >= 10:
                struct.pack_into('<H', data, 8, stats.secondary_stat)
                modified = True
                
            if stats.manufacturer is not None and stats.manufacturer != decoded_item.raw_fields.get('byte_1', None) and len(data) >= 2:
                data[1] = stats.manufacturer
                modified = True
                    
            if stats.item_class is not None and stats.item_class != decoded_item.raw_fields.get('byte_3', None) and len(data) >= 4:
                data[3] = stats.item_class
                modified = True
                    
            if stats.rarity is not None and stats.rarity != decoded_item.raw_fields.get('byte_9', None) and len(data) >= 10:
                data[9] = stats.rarity
                modified = True

            if stats.level is not None and stats.level != decoded_item.raw_fields.get('val16_at_10', None) and len(data) >= 12:
                struct.pack_into('<H', data, 10, stats.level)
                modified = True

        elif decoded_item.item_type == 'd':
            if stats.primary_stat is not None and stats.primary_stat != decoded_item.raw_fields.get('val16_at_4', None) and len(data) >= 6:
                struct.pack_into('<H', data, 4, stats.primary_stat)
                modified = True
                
            if stats.secondary_stat is not None and stats.secondary_stat != decoded_item.raw_fields.get('val16_at_8', None) and len(data) >= 10:
                struct.pack_into('<H', data, 8, stats.secondary_stat)
                modified = True
                
            if stats.manufacturer is not None and stats.manufacturer != decoded_item.raw_fields.get('byte_5', None) and len(data) >= 6:
                data[5] = stats.manufacturer
                modified = True
                    
            if stats.item_class is not None and stats.item_class != decoded_item.raw_fields.get('byte_6', None) and len(data) >= 7:
                data[6] = stats.item_class
                modified = True
                    
            if stats.rarity is not None and stats.rarity != decoded_item.raw_fields.get('byte_14', None) and len(data) >= 15:
                data[14] = stats.rarity
                modified = True
                
            if stats.level is not None and stats.level != decoded_item.raw_fields.get('val16_at_10', None) and len(data) >= 12:
                struct.pack_into('<H', data, 10, stats.level)
                modified = True
        
        else:
            potential_stats = decoded_item.raw_fields.get('potential_stats', [])
            
            if stats.primary_stat is not None and len(potential_stats) > 0 and stats.primary_stat != potential_stats[0][1]:
                pos = potential_stats[0][0]
                if len(data) > pos + 1:
                    struct.pack_into('<H', data, pos, stats.primary_stat)
                    modified = True
            
            if stats.secondary_stat is not None and len(potential_stats) > 1 and stats.secondary_stat != potential_stats[1][1]:
                pos = potential_stats[1][0]
                if len(data) > pos + 1:
                    struct.pack_into('<H', data, pos, stats.secondary_stat)
                    modified = True
            
            if stats.manufacturer is not None and 'byte_1' in decoded_item.raw_fields and stats.manufacturer != decoded_item.raw_fields['byte_1'] and len(data) >= 2:
                data[1] = stats.manufacturer
                modified = True
            
            if stats.rarity is not None and 'byte_2' in decoded_item.raw_fields and stats.rarity != decoded_item.raw_fields['byte_2'] and len(data) >= 3:
                data[2] = stats.rarity
                modified = True
            
            if stats.item_class is not None and 'byte_3' in decoded_item.raw_fields and stats.item_class != decoded_item.raw_fields['byte_3'] and len(data) >= 4:
                data[3] = stats.item_class
                modified = True
            
            if stats.level is not None and 'val16_at_10' in decoded_item.raw_fields and stats.level != decoded_item.raw_fields['val16_at_10'] and len(data) >= 12:
                struct.pack_into('<H', data, 10, stats.level)
                modified = True

        new_serial = bit_pack_encode(bytes(data), decoded_item.original_prefix, decoded_item.original_payload, decoded_item.data_positions, decoded_item.char_offsets)
        
        return new_serial

    except Exception as e:
        return decoded_item.serial

class GearNGunEditor:
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

        self.save_text_button = tk.Button(self.button_frame, text="Save to Raw Text", command=self.save_to_text, state="disabled", bg="#F47C7C", fg="#FFFFFF")
        self.save_text_button.pack(side="left", padx=5)

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
        self.save_text_button.config(state="normal")
        self.save_button.config(state="normal")
        self.copy_button.config(state="disabled")
        self.new_serial = None

    def display_stats(self):
        for widget in self.stats_frame.winfo_children():
            widget.destroy()

        stats = self.decoded_item.stats

        if self.decoded_item.weapon_name:
            name_frame = tk.Frame(self.stats_frame, bg="#2C2F33")
            name_frame.pack(fill="x", pady=5)
            name_label = tk.Label(name_frame, text=f"Editing: {self.decoded_item.weapon_name}", 
                                bg="#2C2F33", fg="#FEE75C", font=("Helvetica", 12, "bold"))
            name_label.pack()

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

    def save_to_text(self):
        if not self.decoded_item:
            messagebox.showerror("Error", "No decoded item to save.")
            return

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        text_content = f"Borderlands 4 Gear N Gun Editor Output\n"
        text_content += f"Generated: {timestamp}\n"
        text_content += "=" * 50 + "\n\n"

        if self.decoded_item.weapon_name:
            text_content += f"WEAPON: {self.decoded_item.weapon_name}\n\n"

        text_content += f"ORIGINAL SERIAL:\n"
        text_content += f"{self.decoded_item.serial}\n\n"

        text_content += f"ITEM SUMMARY:\n"
        text_content += f"Type: {self.decoded_item.item_type}\n"
        text_content += f"Category: {self.decoded_item.item_category}\n"
        text_content += f"Binary Length: {len(self.decoded_item.original_binary)} bytes\n"
        text_content += f"Confidence: {self.decoded_item.confidence}\n\n"

        text_content += f"MAIN STATS:\n"
        stats = self.decoded_item.stats
        stat_lines = [
            f"Primary Stat: {stats.primary_stat if stats.primary_stat is not None else 'N/A'}",
            f"Secondary Stat: {stats.secondary_stat if stats.secondary_stat is not None else 'N/A'}",
            f"Rarity: {stats.rarity if stats.rarity is not None else 'N/A'}",
            f"Manufacturer: {stats.manufacturer if stats.manufacturer is not None else 'N/A'}",
            f"Item Class: {stats.item_class if stats.item_class is not None else 'N/A'}",
            f"Level: {stats.level if stats.level is not None else 'N/A'}"
        ]
        text_content += "\n".join(stat_lines) + "\n\n"

        text_content += f"RAW DATA FIELDS:\n"
        text_content += "-" * 20 + "\n"
        
        structured_fields = []
        for key, value in self.decoded_item.raw_fields.items():
            if key not in ['potential_stats', 'potential_flags']:
                structured_fields.append((key, value))
        
        for key, value in structured_fields:
            if isinstance(value, list):
                value_str = f"[{', '.join(map(str, value))}]"
            else:
                value_str = str(value)
            text_content += f"{key}: {value_str}\n"
        
        if 'potential_stats' in self.decoded_item.raw_fields:
            stats_list = self.decoded_item.raw_fields['potential_stats']
            text_content += f"\nPotential Stats: {len(stats_list)} found\n"
            for pos, val in stats_list:
                text_content += f"  Position {pos}: {val}\n"
        
        if 'potential_flags' in self.decoded_item.raw_fields:
            flags_list = self.decoded_item.raw_fields['potential_flags']
            text_content += f"\nPotential Flags: {len(flags_list)} found\n"
            for pos, val in flags_list:
                text_content += f"  Position {pos}: {val}\n"

        filename = f"item_{self.decoded_item.serial[:10]}_{timestamp.replace(':', '-')}.txt"
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=filename,
            title="Save decoded item data"
        )

        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(text_content)
                messagebox.showinfo("Success", f"Decoded data saved to:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")

    def open_raw_data(self):
        raw_window = Toplevel(self.root)
        raw_window.title("Raw Data")
        raw_window.geometry("600x400")
        raw_window.configure(bg="#2C2F33")

        if self.decoded_item.weapon_name:
            raw_window.title(f"Raw Data - {self.decoded_item.weapon_name}")

        scroll = ttk.Scrollbar(raw_window)
        scroll.pack(side="right", fill="y")

        canvas = tk.Canvas(raw_window, bg="#2C2F33", yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True)

        scroll.config(command=canvas.yview)

        inner_frame = tk.Frame(canvas, bg="#2C2F33")
        canvas.create_window((0, 0), window=inner_frame, anchor="nw")

        frame = tk.Frame(inner_frame, bg="#2C2F33")
        frame.pack(fill="x", pady=2)
        label = tk.Label(frame, text=f"Binary Length: {len(self.decoded_item.original_binary)} bytes", 
                         bg="#2C2F33", fg="#FFFFFF", width=20, anchor="w")
        label.pack(side="left")

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
                value = self.primary_stat_entry.get().strip()
                if value:
                    stats.primary_stat = int(value)
            if hasattr(self, "secondary_stat_entry"):
                value = self.secondary_stat_entry.get().strip()
                if value:
                    stats.secondary_stat = int(value)
            if hasattr(self, "rarity_entry"):
                value = self.rarity_entry.get().strip()
                if value:
                    stats.rarity = int(value)
            if hasattr(self, "manufacturer_entry"):
                value = self.manufacturer_entry.get().strip()
                if value:
                    stats.manufacturer = int(value)
            if hasattr(self, "item_class_entry"):
                value = self.item_class_entry.get().strip()
                if value:
                    stats.item_class = int(value)
            if hasattr(self, "level_entry"):
                value = self.level_entry.get().strip()
                if value:
                    stats.level = int(value)
        except ValueError:
            messagebox.showerror("Error", "Invalid integer value in stats.")
            return

        self.new_serial = encode_item_serial(self.decoded_item)
        if self.decoded_item.weapon_name:
            display_text = f"{self.new_serial}"
        else:
            display_text = self.new_serial
        if self.decoded_item.weapon_name:     
           self.output_label.config(text=f"New Serial for {self.decoded_item.weapon_name}: {display_text}")
           self.copy_button.config(state="normal")
           messagebox.showinfo("Success", f"Encoded new serial for {self.decoded_item.weapon_name}:\n{self.new_serial}")
        else:
           self.output_label.config(text=f"New Serial: {display_text}")
           self.copy_button.config(state="normal")
           messagebox.showinfo("Success", f"Encoded new serial:\n{self.new_serial}")            

    def copy_serial(self):
        if self.new_serial:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.new_serial)
            messagebox.showinfo("Success", "New serial copied to clipboard!")
        else:
            messagebox.showerror("Error", "No new serial available to copy.")

if __name__ == "__main__":
    root = tk.Tk()
    app = GearNGunEditor(root)
    root.mainloop()