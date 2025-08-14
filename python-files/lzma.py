#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import struct
import hashlib
import lzma
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

APP_NAME = "GX Protector"
APP_ID = "gx_protector_v1"
MAGIC = b"GXP1"
CONFIG_DIR = Path.home() / ".gxprotector"
CONFIG_PATH = CONFIG_DIR / "settings.json"
DEFAULT_HEADER_CHOICES = [0x400, 0x1000, 0x2000, 0x4000, 0x8000]
DEFAULT_HEADER_SIZE = 0x1000

def human_size(n: int) -> str:
    units = ["B", "KB", "MB", "GB"]
    i = 0
    f = float(n)
    while f >= 1024 and i < len(units)-1:
        f /= 1024
        i += 1
    return f"{f:.2f} {units[i]}"

def save_settings(data: dict):
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def load_settings() -> dict:
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def derive_keystream(password: str, salt: bytes, length: int) -> bytes:
    if not password:
        return b"\x00" * length
    out = bytearray()
    counter = 0
    pw_bytes = password.encode("utf-8")
    while len(out) < length:
        h = hashlib.sha256()
        h.update(struct.pack("<Q", counter))
        h.update(salt)
        h.update(pw_bytes)
        out.extend(h.digest())
        counter += 1
    return bytes(out[:length])

def xor_bytes(data: bytes, key_stream: bytes) -> bytes:
    return bytes(d ^ k for d, k in zip(data, key_stream))

def build_metadata(header_size: int, orig_size: int, comp_size: int, flags: int, salt: bytes) -> bytes:
    return b"".join([
        MAGIC,
        struct.pack("<I", header_size),
        struct.pack("<Q", orig_size),
        struct.pack("<Q", comp_size),
        struct.pack("<B", flags),
        salt,
    ])

def parse_metadata(blob: bytes):
    if len(blob) < 4 or blob[:4] != MAGIC:
        raise ValueError("Metadata magic not found.")
    off = 4
    header_size = struct.unpack_from("<I", blob, off)[0]; off += 4
    orig_size = struct.unpack_from("<Q", blob, off)[0]; off += 8
    comp_size = struct.unpack_from("<Q", blob, off)[0]; off += 8
    flags = struct.unpack_from("<B", blob, off)[0]; off += 1
    salt = blob[off:off+8]
    return header_size, orig_size, comp_size, flags, salt

def protect_file(input_path: str, output_path: str, header_size: int, password: str, pad_to_original: bool) -> dict:
    with open(input_path, 'rb') as f:
        data = f.read()
    if header_size < 0 or header_size > len(data):
        raise ValueError("Invalid header size.")
    header = data[:header_size]
    body = data[header_size:]
    orig_size = len(data)
    comp_body = lzma.compress(body, preset=9)
    xor_flag = 1 if password else 0
    salt = os.urandom(8)
    ks = derive_keystream(password, salt, len(comp_body)) if xor_flag else b"\x00" * len(comp_body)
    comp_body_x = xor_bytes(comp_body, ks) if xor_flag else comp_body
    meta = build_metadata(header_size, orig_size, len(comp_body), xor_flag, salt)
    out = bytearray()
    out += header
    out += meta
    out += comp_body_x
    if pad_to_original and len(out) < orig_size:
        out += os.urandom(orig_size - len(out))
    with open(output_path, 'wb') as f:
        f.write(out)
    return {
        "original_size": orig_size,
        "compressed_body": len(comp_body),
        "final_size": len(out),
        "padded": pad_to_original and len(out) >= orig_size,
        "header_size": header_size,
        "xor": bool(xor_flag),
    }

def unprotect_file(input_path: str, output_path: str, password: str) -> dict:
    with open(input_path, 'rb') as f:
        data = f.read()
    candidates = [0x400, 0x800, 0x1000, 0x2000, 0x4000, 0x8000]
    found = None
    for hs in candidates:
        if len(data) > hs + 4 and data[hs:hs+4] == MAGIC:
            try:
                md = parse_metadata(data[hs:hs+4+4+8+8+1+8])
                header_size, orig_size, comp_size, flags, salt = md
                if header_size == hs:
                    found = (header_size, orig_size, comp_size, flags, salt, hs)
                    break
            except Exception:
                continue
    if not found:
        raise ValueError("Could not locate metadata.")
    header_size, orig_size, comp_size, flags, salt, hs = found
    meta_len = 4 + 4 + 8 + 8 + 1 + 8
    meta_off = header_size
    comp_off = meta_off + meta_len
    comp_body_x = data[comp_off:comp_off + comp_size]
    xor_flag = flags & 0x01
    if xor_flag:
        ks = derive_keystream(password, salt, len(comp_body_x))
        comp_body = xor_bytes(comp_body_x, ks)
    else:
        comp_body = comp_body_x
    body = lzma.decompress(comp_body)
    restored = data[:header_size] + body
    with open(output_path, 'wb') as f:
        f.write(restored)
    return {
        "restored_size": len(restored),
        "original_size_in_meta": orig_size,
        "header_size": header_size,
        "used_password": bool(xor_flag),
    }

class GXProtectorGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("720x520")
        self.minsize(680, 480)
        self.settings = load_settings()
        self.last_dir = self.settings.get("last_dir", str(Path.home()))
        self.input_path = tk.StringVar()
        self.output_dir = tk.StringVar(value=self.last_dir)
        self.header_var = tk.StringVar(value=hex(DEFAULT_HEADER_SIZE))
        self.pass_var = tk.StringVar()
        self.pad_var = tk.BooleanVar(value=True)
        self._build_ui()

    def _build_ui(self):
        pad = 10
        f_file = ttk.LabelFrame(self, text="File")
        f_file.pack(fill="x", padx=pad, pady=pad)
        ttk.Label(f_file, text="Firmware file:").grid(row=0, column=0, sticky="w", padx=6, pady=6)
        e_in = ttk.Entry(f_file, textvariable=self.input_path, width=70)
        e_in.grid(row=0, column=1, sticky="we", padx=6, pady=6)
        ttk.Button(f_file, text="Browse…", command=self.browse_input).grid(row=0, column=2, padx=6, pady=6)
        ttk.Label(f_file, text="Save to folder:").grid(row=1, column=0, sticky="w", padx=6, pady=6)
        e_out = ttk.Entry(f_file, textvariable=self.output_dir, width=70)
        e_out.grid(row=1, column=1, sticky="we", padx=6, pady=6)
        ttk.Button(f_file, text="Choose…", command=self.choose_output_dir).grid(row=1, column=2, padx=6, pady=6)
        f_file.columnconfigure(1, weight=1)
        f_opt = ttk.LabelFrame(self, text="Options")
        f_opt.pack(fill="x", padx=pad, pady=pad)
        ttk.Label(f_opt, text="Header keep size:").grid(row=0, column=0, sticky="w", padx=6, pady=6)
        header_choices = [hex(x) for x in DEFAULT_HEADER_CHOICES]
        cmb = ttk.Combobox(f_opt, values=header_choices + ["custom"], textvariable=self.header_var, width=12, state="readonly")
        cmb.grid(row=0, column=1, sticky="w", padx=6, pady=6)
        cmb.bind("<<ComboboxSelected>>", self._on_header_choice)
        self.custom_header_entry = ttk.Entry(f_opt, width=12)
        self.custom_header_entry.grid(row=0, column=2, sticky="w", padx=6, pady=6)
        self.custom_header_entry.insert(0, hex(DEFAULT_HEADER_SIZE))
        self.custom_header_entry.configure(state="disabled")
        ttk.Label(f_opt, text="Password (XOR stream – optional):").grid(row=1, column=0, sticky="w", padx=6, pady=6)
        ttk.Entry(f_opt, textvariable=self.pass_var, show="*", width=24).grid(row=1, column=1, sticky="w", padx=6, pady=6)
        ttk.Checkbutton(f_opt, text="Pad to original size", variable=self.pad_var).grid(row=1, column=2, sticky="w", padx=6, pady=6)
        f_actions =
