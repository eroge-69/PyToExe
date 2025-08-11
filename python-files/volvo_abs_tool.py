#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Volvo ABS ID & Checksum Tool (Tkinter)
- Findet Bloecke anhand von 'FF 01'
- Liest/aendert ABS-ID (BCD in Block-Bytes 12,14,15)
- Prueft/aktualisiert Checksummen:
    CHK0 = XOR(Bytes 7..15)
    CHK1 = XOR(Bytes 0..7)
- Zeigt Status je Block (OK/Fehler) und speichert Aenderungen
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import List, Tuple, Dict, Optional

def find_ff01_indices(data: bytes):
    idxs = []
    i = 0
    while True:
        i = data.find(b'\xFF\x01', i)
        if i == -1:
            break
        idxs.append(i)
        i += 1
    return idxs

def xor_bytes(bs: bytes) -> int:
    x = 0
    for b in bs:
        x ^= b
    return x & 0xFF

def compute_checksums_for_block(data: bytes, block_start: int):
    blk = data[block_start:block_start+16]
    if len(blk) < 16:
        return (None, None)
    chk0 = xor_bytes(blk[7:16])
    chk1 = xor_bytes(blk[0:8])
    return chk0, chk1

def stored_checksums_at(data: bytes, ff01_idx: int):
    pos0 = ff01_idx + 2
    pos1 = ff01_idx + 3
    if pos1 >= len(data):
        return (None, None)
    return data[pos0], data[pos1]

def bcd_from_three_bytes(b0: int, b1: int, b2: int) -> str:
    def two_digits(b):
        return f"{(b >> 4) & 0xF}{b & 0xF}"
    return f"{two_digits(b0)}{two_digits(b1)}{two_digits(b2)}"

def three_bytes_from_bcd6(id6: str):
    if len(id6) != 6 or not id6.isdigit():
        raise ValueError("ABS-ID muss genau 6 Ziffern haben (z.B. 086643).")
    def mkbyte(s2: str) -> int:
        hi = int(s2[0]); lo = int(s2[1])
        if hi > 9 or lo > 9:
            raise ValueError("Ungueltige BCD-Ziffer.")
        return ((hi & 0xF) << 4) | (lo & 0xF)
    return mkbyte(id6[0:2]), mkbyte(id6[2:4]), mkbyte(id6[4:6])

def read_abs_id_from_block(data: bytes, block_start: int):
    offs = [12, 14, 15]
    try:
        b0 = data[block_start + offs[0]]
        b1 = data[block_start + offs[1]]
        b2 = data[block_start + offs[2]]
    except IndexError:
        return None
    return bcd_from_three_bytes(b0, b1, b2)

def write_abs_id_to_block(buf: bytearray, block_start: int, id6: str):
    b0, b1, b2 = three_bytes_from_bcd6(id6)
    offs = [12, 14, 15]
    buf[block_start + offs[0]] = b0
    buf[block_start + offs[1]] = b1
    buf[block_start + offs[2]] = b2

def write_checksums_for_block(buf: bytearray, ff01_idx: int, chk0: int, chk1: int):
    buf[ff01_idx + 2] = chk0 & 0xFF
    buf[ff01_idx + 3] = chk1 & 0xFF

def build_block_index(data: bytes):
    blocks = []
    for ff in find_ff01_indices(data):
        block_start = ff - 16
        if block_start < 0:
            continue
        abs_id = read_abs_id_from_block(data, block_start)
        chk0_st, chk1_st = stored_checksums_at(data, ff)
        chk0_calc, chk1_calc = compute_checksums_for_block(data, block_start)
        blocks.append({
            "ff01_idx": ff,
            "block_start": block_start,
            "abs_id": abs_id,
            "chk0_stored": chk0_st,
            "chk1_stored": chk1_st,
            "chk0_calc": chk0_calc,
            "chk1_calc": chk1_calc,
        })
    return blocks

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Volvo ABS ID & Checksum Tool")
        self.geometry("940x520")
        self.minsize(900, 500)

        self.data = None
        self.path = None
        self.blocks = []

        self.create_widgets()

    def create_widgets(self):
        bar = ttk.Frame(self, padding=8); bar.pack(fill="x")
        ttk.Button(bar, text="Datei oeffnen…", command=self.on_open).pack(side="left")
        self.lbl_path = ttk.Label(bar, text="— keine Datei —"); self.lbl_path.pack(side="left", padx=12)

        ctrl = ttk.Frame(self, padding=(8, 0, 8, 8)); ctrl.pack(fill="x")
        ttk.Label(ctrl, text="ABS-ID (6-stellig):").pack(side="left")
        self.entry_abs = ttk.Entry(ctrl, width=12); self.entry_abs.pack(side="left", padx=6)
        ttk.Button(ctrl, text="ABS-ID in ausgewaehltem Block setzen", command=self.on_set_selected).pack(side="left", padx=6)
        ttk.Button(ctrl, text="ABS-ID in allen Bloecken setzen", command=self.on_set_all).pack(side="left", padx=6)
        ttk.Button(ctrl, text="Checksummen im ausgewaehlten Block neu berechnen", command=self.on_recalc_selected).pack(side="left", padx=6)
        ttk.Button(ctrl, text="Checksummen in allen Bloecken neu berechnen", command=self.on_recalc_all).pack(side="left", padx=6)

        cols = ("idx","block_start","ff01_idx","abs_id","chk0_st","chk1_st","chk0_calc","chk1_calc","status")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=15)
        self.tree.pack(fill="both", expand=True, padx=8, pady=8)

        headers = {
            "idx": "#", "block_start": "Block-Start (hex)", "ff01_idx": "FF01 @ (hex)",
            "abs_id": "ABS-ID", "chk0_st": "CHK0 (stored)", "chk1_st": "CHK1 (stored)",
            "chk0_calc": "CHK0 (calc)", "chk1_calc": "CHK1 (calc)", "status": "Status",
        }
        for k, v in headers.items():
            self.tree.heading(k, text=v)
        self.tree.column("idx", width=40, anchor="center")
        self.tree.column("block_start", width=120, anchor="center")
        self.tree.column("ff01_idx", width=110, anchor="center")
        self.tree.column("abs_id", width=90, anchor="center")
        self.tree.column("chk0_st", width=120, anchor="center")
        self.tree.column("chk1_st", width=120, anchor="center")
        self.tree.column("chk0_calc", width=120, anchor="center")
        self.tree.column("chk1_calc", width=120, anchor="center")
        self.tree.column("status", width=90, anchor="center")

        bottom = ttk.Frame(self, padding=8); bottom.pack(fill="x")
        self.btn_save_as = ttk.Button(bottom, text="Speichern unter…", command=self.on_save_as, state="disabled")
        self.btn_save_as.pack(side="right")

        self.tree.tag_configure("good", foreground="#17803D")
        self.tree.tag_configure("bad", foreground="#B00020")
        self.tree.bind("<<TreeviewSelect>>", self.on_select_row)

    def on_open(self):
        path = filedialog.askopenfilename(
            title="BIN-Datei oeffnen",
            filetypes=[("BIN files","*.bin"), ("All files","*.*")]
        )
        if not path: return
        try:
            with open(path, "rb") as f:
                data = bytearray(f.read())
        except Exception as e:
            messagebox.showerror("Fehler", f"Kann Datei nicht lesen:\n{e}")
            return
        self.data = data; self.path = path
        self.lbl_path.config(text=path); self.btn_save_as.config(state="normal")
        self.rebuild_blocks_and_view()

    def on_save_as(self):
        if self.data is None: return
        out = filedialog.asksaveasfilename(
            title="BIN speichern unter",
            defaultextension=".bin",
            filetypes=[("BIN files","*.bin"), ("All files","*.*")]
        )
        if not out: return
        try:
            with open(out, "wb") as f: f.write(self.data)
            messagebox.showinfo("Gespeichert", f"Datei gespeichert:\n{out}")
        except Exception as e:
            messagebox.showerror("Fehler", f"Speichern fehlgeschlagen:\n{e}")

    def on_select_row(self, event=None):
        blk = self.get_selected_block()
        if blk and blk.get("abs_id"):
            self.entry_abs.delete(0, tk.END)
            self.entry_abs.insert(0, blk["abs_id"])

    def get_selected_block(self):
        sel = self.tree.selection()
        if not sel: return None
        idx = int(self.tree.item(sel[0], "values")[0])
        if 0 <= idx < len(self.blocks): return self.blocks[idx]
        return None

    def on_set_selected(self):
        if self.data is None: return
        blk = self.get_selected_block()
        if not blk:
            messagebox.showwarning("Hinweis", "Bitte zuerst einen Block auswaehlen.")
            return
        id6 = self.entry_abs.get().strip()
        try:
            write_abs_id_to_block(self.data, blk["block_start"], id6)
            chk0, chk1 = compute_checksums_for_block(self.data, blk["block_start"])
            write_checksums_for_block(self.data, blk["ff01_idx"], chk0, chk1)
            self.rebuild_blocks_and_view()
        except Exception as e:
            messagebox.showerror("Fehler", f"ABS-ID setzen fehlgeschlagen:\n{e}")

    def on_set_all(self):
        if self.data is None: return
        id6 = self.entry_abs.get().strip()
        try:
            for blk in self.blocks:
                write_abs_id_to_block(self.data, blk["block_start"], id6)
                chk0, chk1 = compute_checksums_for_block(self.data, blk["block_start"])
                write_checksums_for_block(self.data, blk["ff01_idx"], chk0, chk1)
            self.rebuild_blocks_and_view()
        except Exception as e:
            messagebox.showerror("Fehler", f"ABS-ID in allen Bloecken setzen fehlgeschlagen:\n{e}")

    def on_recalc_selected(self):
        if self.data is None: return
        blk = self.get_selected_block()
        if not blk:
            messagebox.showwarning("Hinweis", "Bitte zuerst einen Block auswaehlen.")
            return
        try:
            chk0, chk1 = compute_checksums_for_block(self.data, blk["block_start"])
            write_checksums_for_block(self.data, blk["ff01_idx"], chk0, chk1)
            self.rebuild_blocks_and_view()
        except Exception as e:
            messagebox.showerror("Fehler", f"Neuberechnung fehlgeschlagen:\n{e}")

    def on_recalc_all(self):
        if self.data is None: return
        try:
            for blk in self.blocks:
                chk0, chk1 = compute_checksums_for_block(self.data, blk["block_start"])
                write_checksums_for_block(self.data, blk["ff01_idx"], chk0, chk1)
            self.rebuild_blocks_and_view()
        except Exception as e:
            messagebox.showerror("Fehler", f"Neuberechnung (alle) fehlgeschlagen:\n{e}")

    def rebuild_blocks_and_view(self):
        if self.data is None: return
        self.blocks = build_block_index(self.data)
        for i in self.tree.get_children():
            self.tree.delete(i)
        for i, b in enumerate(self.blocks):
            bs = f"0x{b['block_start']:X}" if b['block_start'] is not None else "-"
            ff = f"0x{b['ff01_idx']:X}" if b['ff01_idx'] is not None else "-"
            absid = b.get("abs_id") or "-"
            def hx(v): return f"0x{v:02X}" if isinstance(v, int) else "-"
            chk0s = hx(b.get("chk0_stored")); chk1s = hx(b.get("chk1_stored"))
            chk0c = hx(b.get("chk0_calc"));   chk1c = hx(b.get("chk1_calc"))
            good = (b.get("chk0_stored") == b.get("chk0_calc")) and (b.get("chk1_stored") == b.get("chk1_calc"))
            status = "OK" if good else "Fehler"
            tag = "good" if good else "bad"
            self.tree.insert("", "end",
                             values=(i, bs, ff, absid, chk0s, chk1s, chk0c, chk1c, status),
                             tags=(tag,))

if __name__ == "__main__":
    App().mainloop()