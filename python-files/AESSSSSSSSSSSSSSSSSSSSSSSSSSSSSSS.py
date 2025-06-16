#
# A complete Python implementation of the Advanced Encryption Standard (AES)
# with a Tkinter-based graphical user interface (GUI).
# Version 12: Restored plaintext alert and rewrote both key and plaintext
# alerts to be more educational.
#

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import binascii

# --- CORE AES ALGORITHM LOGIC (Unchanged) ---
S_BOX = (
    0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
    0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
    0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
    0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
    0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
    0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
    0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
    0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
    0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
    0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
    0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
    0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
    0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
    0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
    0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
    0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16,
)
INV_S_BOX = (
    0x52, 0x09, 0x6a, 0xd5, 0x30, 0x36, 0xa5, 0x38, 0xbf, 0x40, 0xa3, 0x9e, 0x81, 0xf3, 0xd7, 0xfb,
    0x7c, 0xe3, 0x39, 0x82, 0x9b, 0x2f, 0xff, 0x87, 0x34, 0x8e, 0x43, 0x44, 0xc4, 0xde, 0xe9, 0xcb,
    0x54, 0x7b, 0x94, 0x32, 0xa6, 0xc2, 0x23, 0x3d, 0xee, 0x4c, 0x95, 0x0b, 0x42, 0xfa, 0xc3, 0x4e,
    0x08, 0x2e, 0xa1, 0x66, 0x28, 0xd9, 0x24, 0xb2, 0x76, 0x5b, 0xa2, 0x49, 0x6d, 0x8b, 0xd1, 0x25,
    0x72, 0xf8, 0xf6, 0x64, 0x86, 0x68, 0x98, 0x16, 0xd4, 0xa4, 0x5c, 0xcc, 0x5d, 0x65, 0xb6, 0x92,
    0x6c, 0x70, 0x48, 0x50, 0xfd, 0xed, 0xb9, 0xda, 0x5e, 0x15, 0x46, 0x57, 0xa7, 0x8d, 0x9d, 0x84,
    0x90, 0xd8, 0xab, 0x00, 0x8c, 0xbc, 0xd3, 0x0a, 0xf7, 0xe4, 0x58, 0x05, 0xb8, 0xb3, 0x45, 0x06,
    0xd0, 0x2c, 0x1e, 0x8f, 0xca, 0x3f, 0x0f, 0x02, 0xc1, 0xaf, 0xbd, 0x03, 0x01, 0x13, 0x8a, 0x6b,
    0x3a, 0x91, 0x11, 0x41, 0x4f, 0x67, 0xdc, 0xea, 0x97, 0xf2, 0xcf, 0xce, 0xf0, 0xb4, 0xe6, 0x73,
    0x96, 0xac, 0x74, 0x22, 0xe7, 0xad, 0x35, 0x85, 0xe2, 0xf9, 0x37, 0xe8, 0x1c, 0x75, 0xdf, 0x6e,
    0x47, 0xf1, 0x1a, 0x71, 0x1d, 0x29, 0xc5, 0x89, 0x6f, 0xb7, 0x62, 0x0e, 0xaa, 0x18, 0xbe, 0x1b,
    0xfc, 0x56, 0x3e, 0x4b, 0xc6, 0xd2, 0x79, 0x20, 0x9a, 0xdb, 0xc0, 0xfe, 0x78, 0xcd, 0x5a, 0xf4,
    0x1f, 0xdd, 0xa8, 0x33, 0x88, 0x07, 0xc7, 0x31, 0xb1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xec, 0x5f,
    0x60, 0x51, 0x7f, 0xa9, 0x19, 0xb5, 0x4a, 0x0d, 0x2d, 0xe5, 0x7a, 0x9f, 0x93, 0xc9, 0x9c, 0xef,
    0xa0, 0xe0, 0x3b, 0x4d, 0xae, 0x2a, 0xf5, 0xb0, 0xc8, 0xeb, 0xbb, 0x3c, 0x83, 0x53, 0x99, 0x61,
    0x17, 0x2b, 0x04, 0x7e, 0xba, 0x77, 0xd6, 0x26, 0xe1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0c, 0x7d,
)
RCON = (
    0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40,
    0x80, 0x1b, 0x36, 0x6c, 0xd8, 0xab, 0x4d, 0x9a,
)

class AES:
    def __init__(self, key):
        key_bits = len(key) * 8
        if key_bits not in [128, 192, 256]:
            raise ValueError(f"Invalid final key length: {len(key)} bytes ({key_bits} bits). Must be 128, 192, or 256 bits.")
        self.key = key
        self.Nk = key_bits // 32
        self.Nr = {128: 10, 192: 12, 256: 14}[key_bits]
        self.Nb = 4
        self.expanded_key = self._key_expansion(self.key)
    def _sub_bytes(self, state):
        for i in range(len(state)): state[i] = S_BOX[state[i]]
    def _inv_sub_bytes(self, state):
        for i in range(len(state)): state[i] = INV_S_BOX[state[i]]
    def _shift_rows(self, state):
        state[1], state[5], state[9], state[13] = state[5], state[9], state[13], state[1]
        state[2], state[6], state[10], state[14] = state[10], state[14], state[2], state[6]
        state[3], state[7], state[11], state[15] = state[15], state[3], state[7], state[11]
    def _inv_shift_rows(self, state):
        state[5], state[9], state[13], state[1] = state[1], state[5], state[9], state[13]
        state[10], state[14], state[2], state[6] = state[2], state[6], state[10], state[14]
        state[15], state[3], state[7], state[11] = state[3], state[7], state[11], state[15]
    def _mix_columns(self, state):
        for i in range(self.Nb):
            col_start = i * 4; c = state[col_start : col_start + 4]
            s0 = self._gmul(0x02, c[0]) ^ self._gmul(0x03, c[1]) ^ c[2] ^ c[3]
            s1 = c[0] ^ self._gmul(0x02, c[1]) ^ self._gmul(0x03, c[2]) ^ c[3]
            s2 = c[0] ^ c[1] ^ self._gmul(0x02, c[2]) ^ self._gmul(0x03, c[3])
            s3 = self._gmul(0x03, c[0]) ^ c[1] ^ c[2] ^ self._gmul(0x02, c[3])
            state[col_start:col_start + 4] = [s0, s1, s2, s3]
    def _inv_mix_columns(self, state):
        for i in range(self.Nb):
            col_start = i * 4; c = state[col_start:col_start + 4]
            s0 = self._gmul(0x0e, c[0]) ^ self._gmul(0x0b, c[1]) ^ self._gmul(0x0d, c[2]) ^ self._gmul(0x09, c[3])
            s1 = self._gmul(0x09, c[0]) ^ self._gmul(0x0e, c[1]) ^ self._gmul(0x0b, c[2]) ^ self._gmul(0x0d, c[3])
            s2 = self._gmul(0x0d, c[0]) ^ self._gmul(0x09, c[1]) ^ self._gmul(0x0e, c[2]) ^ self._gmul(0x0b, c[3])
            s3 = self._gmul(0x0b, c[0]) ^ self._gmul(0x0d, c[1]) ^ self._gmul(0x09, c[2]) ^ self._gmul(0x0e, c[3])
            state[col_start:col_start + 4] = [s0, s1, s2, s3]
    def _add_round_key(self, state, round_key):
        for i in range(len(state)): state[i] ^= round_key[i]
    def _key_expansion(self, key):
        key_bytes = bytearray(key)
        words = [key_bytes[i:i+4] for i in range(0, len(key_bytes), 4)]
        for i in range(self.Nk, self.Nb * (self.Nr + 1)):
            temp = list(words[i-1])
            if i % self.Nk == 0:
                temp = temp[1:] + temp[:1]
                temp = [S_BOX[b] for b in temp]
                temp[0] ^= RCON[i // self.Nk]
            elif self.Nk > 6 and i % self.Nk == 4:
                temp = [S_BOX[b] for b in temp]
            prev_word = words[i - self.Nk]
            new_word = bytes([prev_word[j] ^ temp[j] for j in range(4)])
            words.append(new_word)
        return [b"".join(words[i:i+4]) for i in range(0, len(words), 4)]
    def _gmul(self, a, b):
        p = 0
        for _ in range(8):
            if b & 1: p ^= a
            hi_bit_set = a & 0x80
            a = (a << 1) & 0xFF
            if hi_bit_set: a ^= 0x1b
            b >>= 1
        return p
    def _cipher(self, input_bytes, steps_log):
        state = list(input_bytes)
        if steps_log is not None: steps_log.append(("Initial State (Plaintext Block)", list(state)))
        self._add_round_key(state, self.expanded_key[0])
        if steps_log is not None: steps_log.append(("After AddRoundKey (Key 0)", list(state)))
        for r in range(1, self.Nr):
            self._sub_bytes(state);
            if steps_log is not None: steps_log.append((f"Round {r}: After SubBytes", list(state)))
            self._shift_rows(state);
            if steps_log is not None: steps_log.append((f"Round {r}: After ShiftRows", list(state)))
            self._mix_columns(state);
            if steps_log is not None: steps_log.append((f"Round {r}: After MixColumns", list(state)))
            self._add_round_key(state, self.expanded_key[r]);
            if steps_log is not None: steps_log.append((f"Round {r}: After AddRoundKey", list(state)))
        self._sub_bytes(state);
        if steps_log is not None: steps_log.append((f"Final Round ({self.Nr}): After SubBytes", list(state)))
        self._shift_rows(state);
        if steps_log is not None: steps_log.append((f"Final Round ({self.Nr}): After ShiftRows", list(state)))
        self._add_round_key(state, self.expanded_key[self.Nr]);
        if steps_log is not None: steps_log.append((f"Final Ciphertext Block", list(state)))
        return bytes(state)
    def _inv_cipher(self, input_bytes, steps_log):
        state = list(input_bytes)
        if steps_log is not None: steps_log.append(("Initial State (Ciphertext Block)", list(state)))
        self._add_round_key(state, self.expanded_key[self.Nr]);
        if steps_log is not None: steps_log.append((f"Pre-Round: After AddRoundKey (Key {self.Nr})", list(state)))
        self._inv_shift_rows(state);
        if steps_log is not None: steps_log.append((f"Pre-Round: After inv. ShiftRows", list(state)))
        self._inv_sub_bytes(state);
        if steps_log is not None: steps_log.append((f"Pre-Round: After inv. SubBytes", list(state)))
        for r in range(self.Nr - 1, 0, -1):
            self._add_round_key(state, self.expanded_key[r]);
            if steps_log is not None: steps_log.append((f"Round {r}: After AddRoundKey", list(state)))
            self._inv_mix_columns(state);
            if steps_log is not None: steps_log.append((f"Round {r}: After inv. MixColumns", list(state)))
            self._inv_shift_rows(state);
            if steps_log is not None: steps_log.append((f"Round {r}: After inv. ShiftRows", list(state)))
            self._inv_sub_bytes(state);
            if steps_log is not None: steps_log.append((f"Round {r}: After inv. SubBytes", list(state)))
        self._add_round_key(state, self.expanded_key[0]);
        if steps_log is not None: steps_log.append(("Final Round: After AddRoundKey (Key 0)", list(state)))
        return bytes(state)
    def _pad(self, data):
        padding_len = 16 - (len(data) % 16)
        return data + bytes([padding_len] * padding_len)
    def _unpad(self, data):
        if not data: return b""
        padding_len = data[-1]
        if padding_len > 16 or padding_len == 0 or len(data) < padding_len or data[-padding_len:] != bytes([padding_len] * padding_len):
            messagebox.showwarning("Padding Warning", "Invalid padding detected. Output may be incorrect. This can happen if the key or IV is wrong during decryption.")
            return data
        return data[:-padding_len]
    def encrypt(self, plaintext, mode, iv, show_steps):
        steps_log = [] if show_steps else None
        padded_data = self._pad(plaintext)
        if steps_log is not None: steps_log.append(("PKCS#7 Data Padding", (plaintext, padded_data)))
        if mode == 'ECB':
            ciphertext = b''
            for i in range(0, len(padded_data), 16):
                log_this_block = steps_log if i == 0 else None
                ciphertext += self._cipher(padded_data[i:i+16], log_this_block)
            return ciphertext, steps_log
        elif mode == 'CBC':
            ciphertext = b''; prev_block = iv
            for i in range(0, len(padded_data), 16):
                block = padded_data[i:i+16]
                block_to_encrypt = bytes([b ^ p for b, p in zip(block, prev_block)])
                log_this_block = steps_log if i == 0 else None
                if log_this_block: log_this_block.append(("CBC XOR (Before Encrypt)", list(block_to_encrypt)))
                encrypted_block = self._cipher(block_to_encrypt, log_this_block)
                ciphertext += encrypted_block; prev_block = encrypted_block
            return ciphertext, steps_log
    def decrypt(self, ciphertext, mode, iv, show_steps):
        steps_log = [] if show_steps else None
        if len(ciphertext) % 16 != 0: raise ValueError("Ciphertext length must be a multiple of 16.")
        if mode == 'ECB':
            decrypted_padded = b''
            for i in range(0, len(ciphertext), 16):
                log_this_block = steps_log if i == 0 else None
                decrypted_padded += self._inv_cipher(ciphertext[i:i+16], log_this_block)
        elif mode == 'CBC':
            decrypted_padded = b''; prev_block = iv
            for i in range(0, len(ciphertext), 16):
                block = ciphertext[i:i+16]
                log_this_block = steps_log if i == 0 else None
                decrypted_block = self._inv_cipher(block, log_this_block)
                plaintext_block = bytes([b ^ p for b, p in zip(decrypted_block, prev_block)])
                if log_this_block: log_this_block.append(("CBC XOR (After Decrypt)", list(plaintext_block)))
                decrypted_padded += plaintext_block; prev_block = block
        if steps_log is not None: steps_log.append(("Before Unpadding", list(decrypted_padded)))
        unpadded_data = self._unpad(decrypted_padded)
        if steps_log is not None: steps_log.append(("Final Unpadded Result", (decrypted_padded, unpadded_data)))
        return unpadded_data, steps_log

# --- GRAPHICAL USER INTERFACE (GUI) ---

class AES_GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AES Encryption Tool & Visualizer")
        self.root.geometry("750x600")
        
        self.notebook = ttk.Notebook(root); self.main_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.main_tab, text='AES Encrypt/Decrypt')
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # --- WIDGETS ---
        controls_frame = ttk.Frame(self.main_tab)
        controls_frame.grid(row=0, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
        ttk.Label(controls_frame, text="Key Size:").pack(side='left', padx=(5,0), pady=5)
        self.key_size_var = tk.StringVar(value='128')
        ttk.OptionMenu(controls_frame, self.key_size_var, '128', '128', '192', '256', command=self.on_config_change).pack(side='left', padx=(0,5), pady=5)
        ttk.Label(controls_frame, text="Mode:").pack(side='left', padx=5, pady=5)
        self.mode_var = tk.StringVar(value='CBC')
        ttk.OptionMenu(controls_frame, self.mode_var, 'CBC', 'CBC', 'ECB', command=self.on_config_change).pack(side='left', padx=5, pady=5)
        
        key_frame = ttk.Labelframe(self.main_tab, text="Credentials")
        key_frame.grid(row=1, column=0, columnspan=2, sticky='ew', padx=5, pady=5, ipadx=5, ipady=5)
        ttk.Label(key_frame, text="Key:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.key_entry = ttk.Entry(key_frame); self.key_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=2)
        self.key_helper_label = ttk.Label(key_frame, text="", foreground="grey"); self.key_helper_label.grid(row=0, column=2, sticky='w', padx=5)
        self.iv_label = ttk.Label(key_frame, text="IV:"); self.iv_label.grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.iv_entry = ttk.Entry(key_frame); self.iv_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=2)
        self.iv_helper_label = ttk.Label(key_frame, text="(16 chars)", foreground="grey"); self.iv_helper_label.grid(row=1, column=2, sticky='w', padx=5)
        key_frame.grid_columnconfigure(1, weight=1)

        io_frame = ttk.Frame(self.main_tab); io_frame.grid(row=2, column=0, columnspan=2, sticky='nsew')
        io_frame.grid_rowconfigure(0, weight=1); io_frame.grid_columnconfigure(0, weight=1); io_frame.grid_columnconfigure(1, weight=1)
        
        input_frame = ttk.Labelframe(io_frame, text="Input"); input_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        self.input_format_var = tk.StringVar(value='Text')
        ttk.OptionMenu(input_frame, self.input_format_var, 'Text', 'Text', 'Hex', 'Base64').pack(anchor='w', padx=5)
        self.input_text = scrolledtext.ScrolledText(input_frame, height=8); self.input_text.pack(expand=True, fill='both', padx=5, pady=5)
        
        output_frame = ttk.Labelframe(io_frame, text="Output"); output_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        self.output_format_var = tk.StringVar(value='Hex')
        ttk.OptionMenu(output_frame, self.output_format_var, 'Hex', 'Hex', 'Base64', 'Text').pack(anchor='w', padx=5)
        self.output_text = scrolledtext.ScrolledText(output_frame, height=8, state='disabled'); self.output_text.pack(expand=True, fill='both', padx=5, pady=5)
        
        actions_frame = ttk.Frame(self.main_tab); actions_frame.grid(row=3, column=0, columnspan=2, pady=10)
        self.show_steps_var = tk.BooleanVar(); ttk.Checkbutton(actions_frame, text="Show All Steps", variable=self.show_steps_var).pack(side='left', padx=5)
        ttk.Button(actions_frame, text="Encrypt", command=lambda: self.process_action(True)).pack(side='left', padx=5)
        ttk.Button(actions_frame, text="Decrypt", command=lambda: self.process_action(False)).pack(side='left', padx=5)
        
        self.main_tab.grid_rowconfigure(2, weight=1); self.main_tab.grid_columnconfigure(0, weight=1)
        self.on_config_change()

    def on_config_change(self, *args):
        mode = self.mode_var.get(); iv_state = 'normal' if mode == 'CBC' else 'disabled'
        self.iv_entry.config(state=iv_state); self.iv_label.config(state=iv_state); self.iv_helper_label.config(state=iv_state)
        key_size_chars = int(self.key_size_var.get()) // 8
        self.key_helper_label.config(text=f"({key_size_chars} chars for {self.key_size_var.get()}-bit)")

    def _get_bytes(self, input_str, input_format):
        if input_format == 'Text': return input_str.encode('utf-8')
        elif input_format == 'Hex': return binascii.unhexlify(input_str.strip().replace(" ", ""))
        elif input_format == 'Base64': return binascii.a2b_base64(input_str.strip())
    
    def _format_output(self, output_bytes, output_format):
        if output_format == 'Text':
            try: return output_bytes.decode('utf-8')
            except UnicodeDecodeError: return f"(Warning: Output not valid UTF-8)\n{binascii.hexlify(output_bytes).decode('ascii')}"
        elif output_format == 'Hex': return binascii.hexlify(output_bytes).decode('ascii')
        elif output_format == 'Base64': return binascii.b2a_base64(output_bytes).decode('ascii').strip()

    def process_action(self, is_encrypt):
        try:
            key_size = int(self.key_size_var.get()); mode = self.mode_var.get()
            input_format = self.input_format_var.get()
            output_format = self.output_format_var.get()
            
            show_steps = self.show_steps_var.get()
            steps_log = [] if show_steps else None
            
            required_len = key_size // 8
            original_key_bytes = self.key_entry.get().encode('utf-8')
            
            if len(original_key_bytes) != required_len:
                messagebox.showinfo(
                    "AES Key Length Requirement",
                    f"The AES algorithm requires a key of a specific, fixed length. For AES-{key_size}, the key must be exactly {required_len} bytes long.\n\n"
                    f"Your key is {len(original_key_bytes)} bytes long, so it will be automatically corrected:\n"
                    "  • If too short, it will be padded with null bytes.\n"
                    "  • If too long, it will be truncated.\n\n"
                    "This action is detailed in the 'Key Processing' step of the visualization.",
                    parent=self.root
                )

            if len(original_key_bytes) > required_len:
                final_key = original_key_bytes[:required_len]
                action = "Key was TRUNCATED"
            elif len(original_key_bytes) < required_len:
                padding = bytes([0] * (required_len - len(original_key_bytes)))
                final_key = original_key_bytes + padding
                action = "Key was PADDED with null bytes"
            else:
                final_key = original_key_bytes
                action = "Key is correct length"
            
            if steps_log is not None:
                steps_log.append(("Key Processing", (original_key_bytes, final_key, action, required_len)))

            iv_bytes = None
            if mode == 'CBC':
                iv_str = self.iv_entry.get()
                if len(iv_str.encode('utf-8')) != 16:
                    messagebox.showerror("Error", "IV must be exactly 16 bytes (characters) for CBC mode.")
                    return
                iv_bytes = iv_str.encode('utf-8')

            input_data = self.input_text.get("1.0", tk.END).strip()
            if not input_data:
                messagebox.showwarning("Input Missing", "Please provide input data to process.")
                return
            data_bytes = self._get_bytes(input_data, input_format)

            # Check for plaintext padding only during encryption with text input
            if is_encrypt and input_format == 'Text' and len(data_bytes) % 16 != 0:
                 messagebox.showinfo(
                    "Plaintext Padding Notice",
                    "The AES algorithm encrypts data in fixed 16-byte blocks. Because your plaintext is not a perfect multiple of 16 bytes, a standard padding method (PKCS#7) will be used to fill the last block.\n\n"
                    "This is a normal and necessary part of the encryption process.\n\n"
                    "The exact padding added is shown in the step-by-step visualization.",
                    parent=self.root
                )

            aes = AES(final_key)
            if steps_log is not None:
                steps_log.append(("Key Schedule Generation", (aes.expanded_key, aes.Nr)))
            
            if is_encrypt:
                result_bytes, steps = aes.encrypt(data_bytes, mode, iv_bytes, show_steps)
                if steps: steps_log.extend(steps)
            else:
                result_bytes, steps = aes.decrypt(data_bytes, mode, iv_bytes, show_steps)
                if steps: steps_log.extend(steps)

            output_str = self._format_output(result_bytes, output_format)
            self.output_text.config(state='normal'); self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, output_str); self.output_text.config(state='disabled')
            
            if show_steps and steps_log:
                StepWindow(self.root, steps_log)

        except (ValueError, binascii.Error) as e: messagebox.showerror("Processing Error", f"An error occurred: {e}")
        except Exception as e: messagebox.showerror("Unexpected Error", f"An unexpected error occurred: {e}")

# --- VISUALIZATION WINDOWS ---
def bytes_to_printable_str(b_data):
    return "".join(chr(b) if 32 <= b <= 126 else '.' for b in b_data)

def format_state_to_matrix(state_bytes):
    matrix_str = ""
    for r in range(4):
        row_values = [state_bytes[r + c*4] for c in range(4)]
        matrix_str += " ".join(f"{b:02x}" for b in row_values) + "\n"
    return matrix_str.strip()

class StepWindow:
    def __init__(self, parent, steps):
        self.parent = parent; self.steps = steps; self.current_step = 0
        self.top = tk.Toplevel(parent); self.top.title("AES Step-by-Step Visualization"); self.top.geometry("550x500")
        self.label = ttk.Label(self.top, text="", font=("Helvetica", 12, "bold")); self.label.pack(pady=10)
        self.text = scrolledtext.ScrolledText(self.top, height=15, width=60, wrap=tk.WORD); self.text.pack(pady=5, padx=10, expand=True, fill='both')
        button_frame = ttk.Frame(self.top); button_frame.pack(pady=10)
        self.prev_button = ttk.Button(button_frame, text="<-- Previous", command=self.prev_step); self.prev_button.pack(side='left', padx=10)
        self.next_button = ttk.Button(button_frame, text="Next -->", command=self.next_step); self.next_button.pack(side='left', padx=10)
        self.update_step_view(); self.top.transient(parent); self.top.grab_set()

    def update_step_view(self):
        title, data = self.steps[self.current_step]
        self.label.config(text=f"Step {self.current_step + 1}/{len(self.steps)}: {title}")
        content = ""
        if title == "Key Processing":
            original, final, action, req_len = data
            content = f"The key must be {req_len} bytes for the selected AES mode.\n\n"
            content += f"Original Key (Text): '{bytes_to_printable_str(original)}'\n"
            content += f"Original Key (Hex):  {binascii.hexlify(original).decode()}\n\n"
            content += f"Action: {action}.\n\n"
            content += f"Final Key Used (Text): '{bytes_to_printable_str(final)}'\n"
            content += f"Final Key Used (Hex):  {binascii.hexlify(final).decode()}"
        elif title == "Key Schedule Generation":
            expanded_key, num_rounds = data
            content = "The processed key is expanded into multiple Round Keys.\n\n"
            for i, rk in enumerate(expanded_key):
                if i > num_rounds: break
                content += f"--- Round Key {i} ---\n"
                content += format_state_to_matrix(rk) + "\n\n"
        elif title == "PKCS#7 Data Padding":
            original, padded = data
            padding_bytes = padded[len(original):]
            content = "Plaintext is padded to be a multiple of 16 bytes.\n\n"
            content += f"Original Data (Text):\n'{bytes_to_printable_str(original)}'\n\n"
            content += f"Original Data (Hex):\n{binascii.hexlify(original).decode()}\n\n"
            content += f"Padding Added (Hex):\n{binascii.hexlify(padding_bytes).decode()}\n\n"
            content += f"Result for Encryption (Hex):\n{binascii.hexlify(padded).decode()}"
        elif title == "Final Unpadded Result":
            padded, unpadded = data
            content = "Decrypted data is unpadded to get the original message.\n\n"
            content += f"Padded Data (Text): '{bytes_to_printable_str(padded)}'\n"
            content += f"Padded Data (Hex):  {binascii.hexlify(padded).decode()}\n\n"
            content += f"Final Result (Text): '{bytes_to_printable_str(unpadded)}'\n"
            content += f"Final Result (Hex):  {binascii.hexlify(unpadded).decode()}"
        else:
            content = "State (Hex Matrix):\n\n" + format_state_to_matrix(data)

        self.text.config(state='normal'); self.text.delete("1.0", tk.END)
        self.text.insert(tk.END, content); self.text.config(state='disabled')
        self.prev_button.config(state='disabled' if self.current_step == 0 else 'normal')
        self.next_button.config(state='disabled' if self.current_step == len(self.steps) - 1 else 'normal')

    def next_step(self):
        if self.current_step < len(self.steps) - 1: self.current_step += 1; self.update_step_view()
    def prev_step(self):
        if self.current_step > 0: self.current_step -= 1; self.update_step_view()

if __name__ == '__main__':
    root = tk.Tk()
    app = AES_GUI(root)
    root.mainloop()

