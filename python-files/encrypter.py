"""
Python Encrypter/Decrypter GUI (reversible) — updated safety fixes

What I fixed / added:
- Syntax checked and core round-trip verified.
- Added a safety limit on roller length (default max 6) to prevent combinatorial explosion and freezes.
- Added graceful handling for extremely large roller permutations (MemoryError / excessive runtime) with a clear message.
- Improved header parsing with robust base64 padding handling.
- Better error messages during decompress / base64 failures.
- Kept the reversible mash + roller + loops + compression mechanics as requested.

Run: python python_encrypter_gui.py (Python 3.8+)
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import hashlib
import base64
import itertools
import zlib
import json
import math

# Safety constants
MAX_ROLLER_LEN = 6  # keep permutations manageable; raise this only if you understand the perf implications
MAX_COMPRESS_PASSES = 20


# ------------------------- Utility functions -------------------------

def sha512_hex(s: str) -> str:
    return hashlib.sha512(s.encode('utf-8')).hexdigest()


def interleave_hex(digests):
    maxlen = max(len(d) for d in digests)
    out = []
    for i in range(maxlen):
        for d in digests:
            if i < len(d):
                out.append(d[i])
    return ''.join(out)


def hex_to_digit_sequence(hexstr: str) -> str:
    # Convert each hex char (0-9,a-f) to its numeric value and concatenate
    out = []
    for ch in hexstr:
        if ch.isdigit():
            out.append(ch)
        else:
            out.append(str(int(ch, 16)))
    return ''.join(out)


def safe_urlsafe_b64decode(s: str) -> bytes:
    # Add padding if missing
    if not isinstance(s, str):
        s = s.decode('ascii') if isinstance(s, bytes) else str(s)
    pad = -len(s) % 4
    if pad:
        s += '=' * pad
    return base64.urlsafe_b64decode(s.encode('ascii'))


def roller_permutation_indices(roller: str):
    # roller only letters a-z
    mapped = [str(ord(ch) - ord('a')) for ch in roller]
    # quick safety check: how many permutations would that generate?
    n = len(mapped)
    total = 0
    for L in range(1, n + 1):
        # permutations P(n, L) = n!/(n-L)!
        total += math.perm(n, L) if hasattr(math, 'perm') else _perm_estimate(n, L)
    if total > 20000:
        # refuse to generate huge index lists — this would freeze or OOM
        raise MemoryError(f'Roller would generate {total} permutations which is too large (limit ~20000).')
    indices = []
    for L in range(1, n+1):
        for perm in itertools.permutations(mapped, L):
            idx_str = ''.join(perm)
            try:
                idx = int(idx_str)
            except ValueError:
                continue
            indices.append(idx)
    return indices


def _perm_estimate(n, L):
    # fallback estimate for permutations when math.perm not available (py<3.8)
    # compute n!/(n-L)!
    num = 1
    for i in range(n, n-L, -1):
        num *= i
    return num


# ------------------------- Core reversible algorithms -------------------------

def reversible_mash_encrypt(plaintext: str, mash_digits: str) -> str:
    # Insert a digit from mash_digits after each character in plaintext
    if not plaintext:
        return ''
    out = []
    di = 0
    L = len(mash_digits)
    if L == 0:
        mash_digits = '0'
        L = 1
    for ch in plaintext:
        out.append(ch)
        out.append(mash_digits[di % L])
        di += 1
    return ''.join(out)


def reversible_mash_decrypt(mashed: str) -> str:
    # Remove every second character (digits) to recover plaintext
    out = []
    i = 0
    n = len(mashed)
    while i < n:
        out.append(mashed[i])
        i += 2
    return ''.join(out)


def roller_insert_encrypt(base: str, combined_hash: str, roller: str) -> str:
    # Deterministically insert characters derived from combined_hash into base using roller indices.
    if not roller:
        return base
    if len(roller) > MAX_ROLLER_LEN:
        raise ValueError(f'Roller length {len(roller)} is greater than max allowed ({MAX_ROLLER_LEN}).')
    try:
        indices = roller_permutation_indices(roller)
    except MemoryError as e:
        raise
    if not indices:
        return base
    result = list(base)
    ch_index = 0
    for idx in indices:
        pos = idx % (len(result) + 1)
        if combined_hash:
            c = combined_hash[ch_index % len(combined_hash)]
        else:
            c = '0'
        result.insert(pos, c)
        ch_index += 1
    return ''.join(result)


def roller_remove_decrypt(full: str, combined_hash: str, roller: str) -> str:
    # Reverse the insertion by computing positions (knowing original base length) and removing in reverse order.
    if not roller:
        return full
    if len(roller) > MAX_ROLLER_LEN:
        raise ValueError(f'Roller length {len(roller)} is greater than max allowed ({MAX_ROLLER_LEN}).')
    indices = roller_permutation_indices(roller)
    if not indices:
        return full
    total_inserted = len(indices)
    final_len = len(full)
    original_len = final_len - total_inserted
    if original_len < 0:
        raise ValueError('Data length smaller than expected — maybe wrong passwords or corrupted payload')
    positions = []
    cur_len = original_len
    for idx in indices:
        pos = idx % (cur_len + 1)
        positions.append(pos)
        cur_len += 1
    result = list(full)
    for pos in reversed(positions):
        if 0 <= pos < len(result):
            del result[pos]
    return ''.join(result)


# ------------------------- Header helpers -------------------------

def make_header(mode: str, loops: int, roller: str, compress_passes: int, extra: dict) -> str:
    hdr = {
        'mode': mode,
        'loops': int(loops),
        'roller': roller,
        'compress': int(compress_passes),
        'extra': extra,
    }
    j = json.dumps(hdr, separators=(',', ':'))
    b64 = base64.urlsafe_b64encode(j.encode()).decode('ascii')
    return 'H:' + b64 + '|'


def parse_header(payload: str):
    if not payload.startswith('H:'):
        return None, payload
    try:
        rest = payload[2:]
        b64, sep, after = rest.partition('|')
        if sep != '|':
            return None, payload
        # robust decode (padding-aware)
        decoded = safe_urlsafe_b64decode(b64)
        hdr = json.loads(decoded.decode('utf-8'))
        return hdr, after
    except Exception as e:
        # return None with original payload — caller will handle error
        return None, payload


# ------------------------- GUI / App -------------------------


class EncrypterApp:
    def __init__(self, root):
        self.root = root
        root.title('Python Encrypter/Decrypter')
        root.geometry('980x720')

        main = ttk.Frame(root, padding=8)
        main.pack(fill=tk.BOTH, expand=True)

        # Mode
        mode_frame = ttk.Frame(main)
        mode_frame.pack(fill=tk.X)
        ttk.Label(mode_frame, text='Mode:').pack(side=tk.LEFT)
        self.mode_var = tk.StringVar(value='Encrypt')
        ttk.Radiobutton(mode_frame, text='Encrypt', variable=self.mode_var, value='Encrypt').pack(side=tk.LEFT)
        ttk.Radiobutton(mode_frame, text='Decrypt', variable=self.mode_var, value='Decrypt').pack(side=tk.LEFT)

        # Passwords frame with scrollbar
        pw_frame = ttk.LabelFrame(main, text='Passwords (used to derive keys)')
        pw_frame.pack(fill=tk.X, pady=6)

        self.pw_entries = []
        self.pw_container = ttk.Frame(pw_frame)
        self.pw_container.pack(fill=tk.X)

        btn_row = ttk.Frame(pw_frame)
        btn_row.pack(fill=tk.X, pady=4)
        ttk.Button(btn_row, text='Add Password', command=self.add_password).pack(side=tk.LEFT)
        ttk.Button(btn_row, text='Remove Last', command=self.remove_last).pack(side=tk.LEFT, padx=6)

        # Add two password fields by default
        self.add_password()
        self.add_password()

        # Text input / paste
        text_frame = ttk.LabelFrame(main, text='Text to encrypt / Paste ciphertext to decrypt')
        text_frame.pack(fill=tk.BOTH, expand=False, pady=6)
        self.input_text = tk.Text(text_frame, height=6)
        self.input_text.pack(fill=tk.BOTH, expand=True)

        # Roller and repeater options
        options_frame = ttk.LabelFrame(main, text='Roller / Repeater')
        options_frame.pack(fill=tk.X, pady=6)

        ttk.Label(options_frame, text='Roller (letters only, a=0,b=1,...):').grid(row=0, column=0, sticky=tk.W, padx=4, pady=2)
        self.roller_var = tk.StringVar()
        ttk.Entry(options_frame, textvariable=self.roller_var, width=40).grid(row=0, column=1, sticky=tk.W, padx=4)

        ttk.Label(options_frame, text='Repeater loops (integer >=0):').grid(row=1, column=0, sticky=tk.W, padx=4, pady=2)
        self.loops_var = tk.IntVar(value=1)
        ttk.Spinbox(options_frame, from_=0, to=1000, textvariable=self.loops_var, width=8).grid(row=1, column=1, sticky=tk.W, padx=4)

        # Controls
        ctrl_frame = ttk.Frame(main)
        ctrl_frame.pack(fill=tk.X, pady=6)
        ttk.Button(ctrl_frame, text='Run', command=self.run).pack(side=tk.LEFT)
        ttk.Button(ctrl_frame, text='Clear Output', command=self.clear_output).pack(side=tk.LEFT, padx=6)
        ttk.Button(ctrl_frame, text='Copy Output', command=self.copy_output).pack(side=tk.LEFT, padx=6)
        ttk.Button(ctrl_frame, text='Save Output', command=self.save_output).pack(side=tk.LEFT, padx=6)

        # Output text
        out_frame = ttk.LabelFrame(main, text='Output')
        out_frame.pack(fill=tk.BOTH, expand=True, pady=6)
        self.output_text = tk.Text(out_frame, wrap=tk.NONE)
        self.output_text.pack(fill=tk.BOTH, expand=True)

        # Status bar
        self.status = tk.StringVar(value='Ready')
        status_bar = ttk.Label(root, textvariable=self.status, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def add_password(self):
        idx = len(self.pw_entries) + 1
        row = ttk.Frame(self.pw_container)
        row.pack(fill=tk.X, pady=2)
        ttk.Label(row, text=f'Password {idx}:').pack(side=tk.LEFT)
        var = tk.StringVar()
        ent = ttk.Entry(row, textvariable=var, show='*')
        ent.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6)
        self.pw_entries.append((row, var))

    def remove_last(self):
        if not self.pw_entries:
            return
        row, var = self.pw_entries.pop()
        row.destroy()

    def clear_output(self):
        self.output_text.delete('1.0', tk.END)
        self.status.set('Output cleared')

    def copy_output(self):
        txt = self.output_text.get('1.0', tk.END).strip()
        if not txt:
            messagebox.showinfo('Copy', 'No output to copy')
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(txt)
        self.status.set('Output copied to clipboard')

    def save_output(self):
        txt = self.output_text.get('1.0', tk.END).strip()
        if not txt:
            messagebox.showinfo('Save', 'No output to save')
            return
        path = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('Text files','*.txt'), ('All files','*.*')])
        if not path:
            return
        with open(path, 'w', encoding='utf-8') as f:
            f.write(txt)
        self.status.set(f'Saved to {path}')

    def run(self):
        mode = self.mode_var.get()
        if mode == 'Encrypt':
            self.encrypt()
        else:
            self.decrypt()

    def encrypt(self):
        plaintext = self.input_text.get('1.0', tk.END).rstrip('\n')
        if plaintext == '':
            messagebox.showerror('Error', 'Please enter text to encrypt')
            return
        # Collect passwords
        pws = [var.get() for (row, var) in self.pw_entries if var.get() != '']
        if not pws:
            messagebox.showerror('Error', 'Please enter at least one password (used to derive key)')
            return
        self.status.set('Hashing passwords...')
        self.root.update_idletasks()
        digests = [sha512_hex(pw) for pw in pws]
        combined = interleave_hex(digests)
        mash_digits = hex_to_digit_sequence(combined)

        # Step: mash plaintext reversibly
        mashed = reversible_mash_encrypt(plaintext, mash_digits)

        # Roller expansion
        roller = self.roller_var.get().strip().lower()
        roller = ''.join([c for c in roller if c.isalpha()])
        if len(roller) > MAX_ROLLER_LEN:
            messagebox.showerror('Error', f'Roller too long (max {MAX_ROLLER_LEN}). Reduce roller length to avoid freezing.)')
            return
        try:
            expanded = roller_insert_encrypt(mashed, combined, roller)
        except MemoryError as e:
            messagebox.showerror('Error', f'Roller caused too many permutations: {e}')
            return
        except Exception as e:
            messagebox.showerror('Error', f'Failed during roller expansion: {e}')
            return

        # Before loops: ensure we base64-encode inside loops as requested
        loops = max(0, int(self.loops_var.get()))
        data = expanded
        try:
            for i in range(loops):
                data = base64.b64encode(data.encode('utf-8')).decode('ascii')
        except Exception as e:
            messagebox.showerror('Error', f'Failed during base64 encode loops: {e}')
            return

        compress_passes = 0
        # Compress until under 2000 chars
        try:
            while len(data) > 2000 and compress_passes < MAX_COMPRESS_PASSES:
                compressed = zlib.compress(data.encode('utf-8'), level=9)
                data = base64.b64encode(compressed).decode('ascii')
                compress_passes += 1
        except Exception as e:
            messagebox.showerror('Error', f'Failed during compression: {e}')
            return

        header = make_header('E', loops, roller, compress_passes, extra={'pw_count': len(pws), 'mashed_len': len(mashed)})
        final = header + data

        self.output_text.delete('1.0', tk.END)
        self.output_text.insert(tk.END, final)
        self.status.set(f'Encrypted — length {len(final)}, compress passes {compress_passes}')

    def decrypt(self):
        payload = self.input_text.get('1.0', tk.END).strip()
        if not payload:
            messagebox.showerror('Error', 'Please paste ciphertext to decrypt')
            return
        hdr, after = parse_header(payload)
        if hdr is None:
            messagebox.showerror('Error', 'Header not found or invalid. Make sure the ciphertext was generated by this tool.')
            return
        # Extract header fields
        loops = int(hdr.get('loops', 0))
        roller = hdr.get('roller', '')
        compress_passes = int(hdr.get('compress', 0))
        extra = hdr.get('extra', {})

        if len(roller) > MAX_ROLLER_LEN:
            messagebox.showerror('Error', f'Roller length recorded in header exceeds max safe limit ({MAX_ROLLER_LEN}). Cannot safely decrypt.')
            return

        # Collect passwords
        pws = [var.get() for (row, var) in self.pw_entries if var.get() != '']
        if not pws:
            messagebox.showerror('Error', 'Please enter at least one password (used to derive key)')
            return
        self.status.set('Hashing passwords for decryption...')
        self.root.update_idletasks()
        digests = [sha512_hex(pw) for pw in pws]
        combined = interleave_hex(digests)
        mash_digits = hex_to_digit_sequence(combined)

        data = after
        # Reverse compression passes
        try:
            for i in range(compress_passes):
                decoded = base64.b64decode(data.encode('ascii'))
                decompressed = zlib.decompress(decoded)
                data = decompressed.decode('utf-8')
        except Exception as e:
            messagebox.showerror('Error', f'Failed during decompression pass {i+1}: {e}')
            return

        # Reverse loops: base64-decode loops times
        try:
            for i in range(loops):
                data = base64.b64decode(data.encode('ascii')).decode('utf-8')
        except Exception as e:
            messagebox.showerror('Error', f'Failed during base64 decode loops: {e}')
            return

        # Reverse roller insertions
        try:
            removed = roller_remove_decrypt(data, combined, roller)
        except Exception as e:
            messagebox.showerror('Error', f'Failed reversing roller: {e}')
            return

        # Reverse mash
        try:
            plaintext = reversible_mash_decrypt(removed)
        except Exception as e:
            messagebox.showerror('Error', f'Failed reversing mash: {e}')
            return

        self.output_text.delete('1.0', tk.END)
        self.output_text.insert(tk.END, plaintext)
        self.status.set('Decryption complete')


if __name__ == '__main__':
    root = tk.Tk()
    app = EncrypterApp(root)
    root.mainloop()
