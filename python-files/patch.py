#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mp4_full_mdhd_mvhd_patcher.py – Reproduction exacte du bug TikTok.

- Divise par 2 la timescale **et** la durée dans `mvhd` (boîte globale).
- Divise par 2 la timescale **et** la durée dans **chaque** boîte `mdhd` (toutes pistes).
- Ne modifie **pas** les STTS ni TKHD.

Ainsi, les joueurs PC (qui se basent sur STTS) restent fluides, et TikTok mobile (qui lit MDHD) comptera la durée ×2.
Bypass compression TikTok by Vano Lambda.
UI ultra-minimale : boîte de dialogue de sélection.
"""
import os
import struct
import tkinter as tk
from tkinter import filedialog, messagebox


def patch_mvhd(buf):
    patched = 0
    offset = 0
    # boucle sur toutes les boîtes 'mvhd'
    while True:
        idx = buf.find(b'mvhd', offset)
        if idx < 0:
            break
        pos = idx - 4
        # version+flags at pos+8
        version = buf[pos+8]
        # timescale offset: version(1)+flags(3)+creation(4)+modification(4)
        ts_off = pos + 8 + 1 + 3 + 4 + 4
        old_ts = struct.unpack_from('>I', buf, ts_off)[0]
        new_ts = max(1, old_ts // 2)
        struct.pack_into('>I', buf, ts_off, new_ts)
        # duration offset
        if version == 0:
            dur_off = ts_off + 4
            old_dur = struct.unpack_from('>I', buf, dur_off)[0]
            struct.pack_into('>I', buf, dur_off, old_dur // 2)
        else:
            dur_off = ts_off + 4
            old_dur = struct.unpack_from('>Q', buf, dur_off)[0]
            struct.pack_into('>Q', buf, dur_off, old_dur // 2)
        patched += 1
        offset = idx + 4
    return patched


def patch_mdhd(buf):
    patched = 0
    offset = 0
    # boucle sur toutes les boîtes 'mdhd'
    while True:
        idx = buf.find(b'mdhd', offset)
        if idx < 0:
            break
        pos = idx - 4
        version = buf[pos+8]
        # offset after version+flags
        base = pos + 8 + 1 + 3
        if version == 0:
            ts_off = base + 4 + 4  # creation(4)+modification(4)
            dur_off = ts_off + 4
            old_ts = struct.unpack_from('>I', buf, ts_off)[0]
            new_ts = max(1, old_ts // 2)
            struct.pack_into('>I', buf, ts_off, new_ts)
            old_dur = struct.unpack_from('>I', buf, dur_off)[0]
            struct.pack_into('>I', buf, dur_off, old_dur // 2)
        else:
            ts_off = base + 8 + 8  # creation(8)+modification(8)
            dur_off = ts_off + 4
            old_ts = struct.unpack_from('>I', buf, ts_off)[0]
            new_ts = max(1, old_ts // 2)
            struct.pack_into('>I', buf, ts_off, new_ts)
            old_dur = struct.unpack_from('>Q', buf, dur_off)[0]
            struct.pack_into('>Q', buf, dur_off, old_dur // 2)
        patched += 1
        offset = idx + 4
    return patched


def run_patch(filepath):
    buf = bytearray(open(filepath, 'rb').read())
    mvhd_count = patch_mvhd(buf)
    mdhd_count = patch_mdhd(buf)
    if mvhd_count == 0 and mdhd_count == 0:
        raise RuntimeError("Aucune boîte mvhd ou mdhd trouvée.")
    out = filepath.replace('.mp4', '_patched.mp4')
    with open(out, 'wb') as f:
        f.write(buf)
    return out, mvhd_count, mdhd_count


def on_click():
    file = filedialog.askopenfilename(
        title="Select an MP4 to patch", filetypes=[("MP4","*.mp4")]
    )
    if not file:
        return
    try:
        out, mv, md = run_patch(file)
        messagebox.showinfo(
            "Success",
            f"Bypass by Vano Lambda !\n"
            f"Generated file : {os.path.basename(out)}\n"
            f"mvhd patched : {mv}, mdhd patched : {md}"
        )
    except Exception as e:
        messagebox.showerror("Error", str(e))

if __name__ == '__main__':
    root = tk.Tk()
    root.title("TikTok Bypass by Vano Lambda")
    root.geometry("320x160")
    tk.Label(root, text="Bypass compression TikTok by Vano Lambda", font=("Arial", 11, "bold")).pack(pady=12)
    tk.Button(root, text="Choose and patch", command=on_click, width=20, height=2).pack()
    root.mainloop()
