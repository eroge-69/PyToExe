#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TF2 Arabic Visual‑Order Converter (Windows EXE)
------------------------------------------------
• Type normal Arabic + optional English terms.
• Output is TF2‑ready (Arabic is pre‑shaped + visual‑order reversed), while English stays readable.
• Hotkeys:
    - Ctrl+Enter  → Convert
    - Ctrl+C      → Copy Output
    - F2          → Convert & Copy (one-shot)
• Options:
    - Strip diacritics (tashkīl)
    - Insert Zero‑Width Joiners
    - Always on top
    - Auto‑copy after convert

Build to EXE with PyInstaller (see bottom of file for command).
"""

import tkinter as tk
from tkinter import ttk, messagebox

# ---------------- Arabic shaping core ----------------
RIGHT_JOIN_ONLY = {
    0x0622, 0x0623, 0x0625, 0x0627, 0x062F, 0x0630, 0x0631, 0x0632, 0x0648, 0x0649, 0x0629, 0x0624
}
NON_JOINING = {
    0x0621
}

ARABIC_SET = set([
    0x0621,0x0622,0x0623,0x0624,0x0625,0x0626,0x0627,0x0628,0x0629,0x062A,0x062B,0x062C,0x062D,0x062E,
    0x062F,0x0630,0x0631,0x0632,0x0633,0x0634,0x0635,0x0636,0x0637,0x0638,0x0639,0x063A,
    0x0641,0x0642,0x0643,0x0644,0x0645,0x0646,0x0647,0x0648,0x0649,0x064A
])

FORMS = {
    0x0621: (0xFE80,0xFE80,0xFE80,0xFE80), # HAMZA
    0x0622: (0xFE81,0xFE82,0,0),
    0x0623: (0xFE83,0xFE84,0,0),
    0x0624: (0xFE85,0xFE86,0,0),
    0x0625: (0xFE87,0xFE88,0,0),
    0x0626: (0xFE89,0xFE8A,0xFE8B,0xFE8C),
    0x0627: (0xFE8D,0xFE8E,0,0),
    0x0628: (0xFE8F,0xFE90,0xFE91,0xFE92),
    0x0629: (0xFE93,0xFE94,0,0),
    0x062A: (0xFE95,0xFE96,0xFE97,0xFE98),
    0x062B: (0xFE99,0xFE9A,0xFE9B,0xFE9C),
    0x062C: (0xFE9D,0xFE9E,0xFE9F,0xFEA0),
    0x062D: (0xFEA1,0xFEA2,0xFEA3,0xFEA4),
    0x062E: (0xFEA5,0xFEA6,0xFEA7,0xFEA8),
    0x062F: (0xFEA9,0xFEAA,0,0),
    0x0630: (0xFEAB,0xFEAC,0,0),
    0x0631: (0xFEAD,0xFEAE,0,0),
    0x0632: (0xFEAF,0xFEB0,0,0),
    0x0633: (0xFEB1,0xFEB2,0xFEB3,0xFEB4),
    0x0634: (0xFEB5,0xFEB6,0xFEB7,0xFEB8),
    0x0635: (0xFEB9,0xFEBA,0xFEBB,0xFEBC),
    0x0636: (0xFEBD,0xFEBE,0xFEBF,0xFEC0),
    0x0637: (0xFEC1,0xFEC2,0xFEC3,0xFEC4),
    0x0638: (0xFEC5,0xFEC6,0xFEC7,0xFEC8),
    0x0639: (0xFEC9,0xFECA,0xFECB,0xFECC),
    0x063A: (0xFECD,0xFECE,0xFECF,0xFED0),
    0x0641: (0xFED1,0xFED2,0xFED3,0xFED4),
    0x0642: (0xFED5,0xFED6,0xFED7,0xFED8),
    0x0643: (0xFED9,0xFEDA,0xFEDB,0xFEDC),
    0x0644: (0xFEDD,0xFEDE,0xFEDF,0xFEE0),
    0x0645: (0xFEE1,0xFEE2,0xFEE3,0xFEE4),
    0x0646: (0xFEE5,0xFEE6,0xFEE7,0xFEE8),
    0x0647: (0xFEE9,0xFEEA,0xFEEB,0xFEEC),
    0x0648: (0xFEED,0xFEEE,0,0),
    0x0649: (0xFEEF,0xFEF0,0,0),
    0x064A: (0xFEF1,0xFEF2,0xFEF3,0xFEF4),
}

TATWEEL = 0x0640

HARAKAT_RANGES = [
    (0x0610,0x061A), (0x064B,0x065F), (0x0670,0x0670), (0x06D6,0x06ED)
]

def is_arabic_letter(cp:int)->bool:
    return cp in ARABIC_SET

def joining_type(cp:int)->str:
    if cp in NON_JOINING: return 'none'
    if cp in RIGHT_JOIN_ONLY: return 'right'
    if is_arabic_letter(cp): return 'dual'
    return 'other'

def can_connect_next(cp:int)->bool:
    return joining_type(cp)=='dual'

def can_connect_prev(cp:int)->bool:
    jt = joining_type(cp)
    return jt in ('dual','right')

def pick_form(cp:int, connect_prev:bool, connect_next:bool)->int:
    f = FORMS.get(cp)
    if not f:
        return cp
    iso, fin, init, med = f
    jt = joining_type(cp)
    if jt=='none':
        return iso
    if jt=='right':
        return fin if (connect_prev and fin) else iso
    if connect_prev and connect_next and med:
        return med
    if connect_prev and fin:
        return fin
    if connect_next and init:
        return init
    return iso

def strip_diacritics(text:str)->str:
    out = []
    for ch in text:
        cp = ord(ch)
        if any(a<=cp<=b for a,b in HARAKAT_RANGES):
            continue
        out.append(ch)
    return ''.join(out)

def to_presentation_forms_b(text:str)->str:
    cps = [ord(ch) for ch in text]
    out = []
    for i, cp in enumerate(cps):
        if not is_arabic_letter(cp):
            out.append(cp)
            continue
        # find prev/next arabic letters for joining
        j_prev = None
        j = i-1
        while j >= 0:
            c = cps[j]
            if is_arabic_letter(c):
                j_prev = c; break
            if c == TATWEEL:
                j -= 1; continue
            break
        j_next = None
        j = i+1
        while j < len(cps):
            c = cps[j]
            if is_arabic_letter(c):
                j_next = c; break
            if c == TATWEEL:
                j += 1; continue
            break
        connect_prev = (j_prev is not None) and can_connect_next(j_prev) and can_connect_prev(cp)
        connect_next = (j_next is not None) and can_connect_next(cp) and can_connect_prev(j_next)
        shaped = pick_form(cp, connect_prev, connect_next)
        out.append(shaped if shaped else cp)
    return ''.join(chr(x) for x in out)

# --- Visual‑order algorithm that keeps English readable ---
# 1) Shape Arabic letters to Forms‑B.
# 2) Walk the shaped string from end to start. When we hit:
#    • Arabic run  → emit characters in that backward traversal (so Arabic is visually correct).
#    • Non‑Arabic run (Latin, digits, punctuation) → collect the run and emit it in its ORIGINAL order.
# This preserves English words while fixing Arabic.

import re

# Arabic Presentation Forms blocks + basic Arabic range
RE_ARABIC_CODEPOINT = re.compile(r"[\u0600-\u06FF\uFB50-\uFDFF\uFE70-\uFEFF]")


def reverse_visual_but_preserve_latin(shaped: str) -> str:
    out_chars = []
    i = len(shaped) - 1
    while i >= 0:
        ch = shaped[i]
        if RE_ARABIC_CODEPOINT.match(ch):
            # Arabic: just append this char (we're already traversing right->left)
            out_chars.append(ch)
            i -= 1
        else:
            # Non‑Arabic run: collect full run backward, then emit in forward order
            j = i
            while j >= 0 and not RE_ARABIC_CODEPOINT.match(shaped[j]):
                j -= 1
            # run is shaped[j+1 : i+1]
            segment = shaped[j+1:i+1]
            out_chars.extend(segment)  # keep original order for Latin/digits/punct
            i = j
    return ''.join(out_chars)


def convert_text(src: str, strip_harakat: bool, zwj: bool, words_only: bool) -> str:
    if strip_harakat:
        src = strip_diacritics(src)
    shaped = to_presentation_forms_b(src)
    if zwj:
        shaped = insert_zwj(shaped)
    if words_only:
        # Reverse by whitespace‑separated words (fallback option)
        return ' '.join(shaped.split()[::-1])
    # Default: Variant A but with English preserved
    return reverse_visual_but_preserve_latin(shaped)


def insert_zwj(s: str) -> str:
    ZWJ = '\u200D'
    out = []
    for i, ch in enumerate(s):
        out.append(ch)
        if i+1 < len(s) and ch != ' ' and s[i+1] != ' ':
            out.append(ZWJ)
    return ''.join(out)

# ---------------- UI (Tkinter) ----------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TF2 Arabic Visual‑Order Converter")
        self.geometry("980x560")
        self.minsize(820, 480)

        # --- Styles
        try:
            self.tk.call("tk", "scaling", 1.2)
        except Exception:
            pass

        # --- Variables
        self.var_strip = tk.BooleanVar(value=True)
        self.var_zwj = tk.BooleanVar(value=False)
        self.var_words_only = tk.BooleanVar(value=False)
        self.var_always_on_top = tk.BooleanVar(value=True)
        self.var_autocopy = tk.BooleanVar(value=True)

        # --- Layout
        root = ttk.Frame(self, padding=12)
        root.pack(fill=tk.BOTH, expand=True)

        top = ttk.Frame(root)
        top.pack(fill=tk.X)
        ttk.Label(top, text="TF2 Arabic Visual‑Order Converter", font=("Segoe UI", 14, "bold")).pack(side=tk.LEFT)
        ttk.Checkbutton(top, text="Always on top", variable=self.var_always_on_top, command=self.toggle_topmost).pack(side=tk.RIGHT)
        self.toggle_topmost()

        mid = ttk.Frame(root)
        mid.pack(fill=tk.BOTH, expand=True, pady=(8,6))

        left = ttk.Frame(mid)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,6))
        ttk.Label(left, text="Input (normal Arabic, with optional English)").pack(anchor=tk.W)
        self.txt_in = tk.Text(left, wrap=tk.WORD, font=("Segoe UI", 11))
        self.txt_in.pack(fill=tk.BOTH, expand=True)

        right = ttk.Frame(mid)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(6,0))
        ttk.Label(right, text="Output (paste into TF2 chat)").pack(anchor=tk.W)
        self.txt_out = tk.Text(right, wrap=tk.WORD, font=("Segoe UI", 11))
        self.txt_out.pack(fill=tk.BOTH, expand=True)

        bottom = ttk.Frame(root)
        bottom.pack(fill=tk.X, pady=(6,0))

        # Buttons
        btn_convert = ttk.Button(bottom, text="Convert  (Ctrl+Enter)", command=self.on_convert)
        btn_convert.pack(side=tk.LEFT)
        ttk.Button(bottom, text="Copy Output  (Ctrl+C)", command=self.copy_output).pack(side=tk.LEFT, padx=6)
        ttk.Button(bottom, text="Convert & Copy  (F2)", command=self.on_convert_and_copy).pack(side=tk.LEFT)

        # Options
        opts = ttk.Frame(bottom)
        opts.pack(side=tk.RIGHT)
        ttk.Checkbutton(opts, text="Strip diacritics", variable=self.var_strip).grid(row=0, column=0, sticky=tk.W, padx=6)
        ttk.Checkbutton(opts, text="Insert Zero‑Width Joiners", variable=self.var_zwj).grid(row=0, column=1, sticky=tk.W, padx=6)
        ttk.Checkbutton(opts, text="Reverse words only (fallback)", variable=self.var_words_only).grid(row=0, column=2, sticky=tk.W, padx=6)
        ttk.Checkbutton(opts, text="Auto‑copy after convert", variable=self.var_autocopy).grid(row=0, column=3, sticky=tk.W, padx=6)

        # Status
        self.status = ttk.Label(root, text="", foreground="#00897B")
        self.status.pack(anchor=tk.W, pady=(6,0))

        # Hotkeys
        self.bind_all("<Control-Return>", lambda e: self.on_convert())
        self.bind_all("<Control-KP_Enter>", lambda e: self.on_convert())
        self.bind_all("<Control-c>", lambda e: self.copy_output())
        self.bind_all("<F2>", lambda e: self.on_convert_and_copy())

        # Sample text
        self.txt_in.insert("1.0", "سويلي هاي الجمله تا اشوف\nالمشكلة بسبب النظام + test TF2")

    def toggle_topmost(self):
        self.attributes("-topmost", bool(self.var_always_on_top.get()))

    def on_convert(self):
        src = self.txt_in.get("1.0", tk.END).rstrip('\n')
        out = convert_text(
            src,
            strip_harakat=self.var_strip.get(),
            zwj=self.var_zwj.get(),
            words_only=self.var_words_only.get()
        )
        self.txt_out.delete("1.0", tk.END)
        self.txt_out.insert("1.0", out)
        self.set_status("Converted ✔")
        if self.var_autocopy.get():
            self.copy_output()

    def on_convert_and_copy(self):
        self.on_convert()
        self.copy_output()

    def copy_output(self):
        text = self.txt_out.get("1.0", tk.END)
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()  # now it stays on the clipboard after app closes
        self.set_status("Copied to clipboard 📋")

    def set_status(self, msg:str):
        self.status.config(text=msg)
        self.after(2200, lambda: self.status.config(text=""))


if __name__ == "__main__":
    try:
        app = App()
        app.mainloop()
    except Exception as e:
        messagebox.showerror("Error", str(e))

"""
Build instructions (Windows):
1) Install Python 3.10+ and pip.
2) Save this file as: tf2_arabic_converter.py
3) Install PyInstaller:    pip install pyinstaller
4) Build EXE (one‑file):   pyinstaller --onefile --noconsole tf2_arabic_converter.py
   → Check the 'dist' folder for tf2_arabic_converter.exe

Tips:
• Keep the app on "Always on top" so you can Alt+Tab quickly. Use Ctrl+Enter to convert and Ctrl+C to copy without the mouse.
• If a server/client behaves differently, try toggling "Reverse words only" or "Insert Zero‑Width Joiners".
• English stays readable thanks to the run‑aware visual reverse algorithm.
"""
