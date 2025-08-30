# -*- coding: utf-8 -*-
"""
JLPT Reading Helper JSON Generator (Batch Mode)
----------------------------------------------
A simplified Tkinter desktop app where the user pastes a block of text in the given format
(e.g., the numbered entries with Japanese, reading with furigana in parentheses, and English translation),
provides a Kanji, and generates JSON output for all parsed items at once.

Author: ChatGPT
"""

import json
import re
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

SAMPLE_TEXT = """477-1. 国民性。
国民性(こくみんせい)。
A national trait.  (101) 

477-2. 米国民。
米(べい)　国民(こくみん)。
American citizens.  (101) 

477-3. 市民会館。
市民(しみん)　会館(かいかん)。
Civic auditorium.  (101) 

477-4. 地元の住民。
地元(じもと)　の　住民(じゅうみん)。
The local citizens.  (101) 

477-5. スペイン国民。
スペイン　国民(こくみん)。
The Spanish people.  (101) 

477-6. 政府の民政部門。
政府(せいふ)　の　民政(みんせい)　部門(ぶもん)。
Civil branches of government.  (101) 

477-7. 人民政府の機関。
人民(じんみん)　政府(せいふ)　の　機関(きかん)。
Institutions of popular government.  (101) 

477-8. 関根氏は民主党の支持者だ。
関根(せきね) 氏(し)　は　民主党(みんしゅとう)　の　支持者(しじしゃ)　だ。
Mr. Sekine is a Democratic Party supporter.  (87) 

477-9. 次回の会合の日時は民主的に決定された。
次回(じかい)　の　会合(かいごう)　の　日時(にちじ)　は　民主的(みんしゅてき)　に　決定(けってい)　された。
The date of the next meeting was decided democratically.  (101) 

477-10. 井戸水を飲まないよう市が住民に注意をよびかける。
井戸水(いどみず)　を　飲ま(のま)ない　よう　市(し)　が　住民(じゅうみん)　に　注意(ちゅうい)　を　よびかける。
The city alerts all residents not to drink well water.  (10)
"""

ENTRY_HEADER_RE = re.compile(r"^\s*(\d{1,4}-\d{1,4})\.?\s*(.*\S)\s*$")
TRAILING_CODE_RE = re.compile(r"\s*\((\d+)\)\s*$")


def split_blocks(text: str):
    lines = [ln.rstrip("\n") for ln in text.splitlines()]
    blocks = []
    current = []
    for ln in lines:
        if ENTRY_HEADER_RE.match(ln):
            if current:
                blocks.append(current)
                current = []
        if ln.strip() != "":
            current.append(ln)
    if current:
        blocks.append(current)
    return blocks


def parse_block(block_lines):
    header = block_lines[0]
    m = ENTRY_HEADER_RE.match(header)
    if not m:
        raise ValueError("Header line not recognized: " + header)
    sentence = m.group(2)

    reading_help = None
    translation = None

    for i in range(1, len(block_lines)):
        ln = block_lines[i].strip()
        if reading_help is None and "(" in ln and ")" in ln:
            reading_help = ln
            continue
        if reading_help is not None:
            translation = ln
            break

    if reading_help is None and len(block_lines) >= 2:
        reading_help = block_lines[1].strip()
    if translation is None:
        translation = block_lines[-1].strip()

    translation = TRAILING_CODE_RE.sub("", translation).strip()

    return {
        "sentence": sentence,
        "reading_help": normalize_spaces(reading_help),
        "translation": translation,
    }


def normalize_spaces(s: str) -> str:
    s2 = re.sub(r"[\u3000\s]+", " ", s).strip()
    s2 = re.sub(r"\(", " ( ", s2)
    s2 = re.sub(r"\)", " ) ", s2)
    s2 = re.sub(r"\s+", " ", s2).strip()
    return s2


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Reading Helper JSON Generator (Batch)")
        self.geometry("1000x700")

        self._build_ui()

    def _build_ui(self):
        top = ttk.Frame(self)
        top.pack(fill=tk.X, padx=10, pady=8)

        ttk.Label(top, text="Target Kanji:").pack(side=tk.LEFT)
        self.kanji_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.kanji_var, width=10).pack(side=tk.LEFT, padx=(6, 12))

        parse_btn = ttk.Button(top, text="Generate JSON", command=self.on_generate)
        parse_btn.pack(side=tk.LEFT)

        copy_btn = ttk.Button(top, text="Copy JSON", command=self.on_copy_json)
        copy_btn.pack(side=tk.LEFT, padx=6)

        save_btn = ttk.Button(top, text="Save JSON…", command=self.on_save_json)
        save_btn.pack(side=tk.LEFT, padx=6)

        sample_btn = ttk.Button(top, text="Load Sample", command=self.on_load_sample)
        sample_btn.pack(side=tk.LEFT, padx=6)

        paned = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        left = ttk.Labelframe(paned, text="Paste Input Text (477-*)")
        self.input_text = tk.Text(left, wrap=tk.WORD, undo=True)
        self.input_text.pack(fill=tk.BOTH, expand=True)
        paned.add(left, weight=2)

        right = ttk.Labelframe(paned, text="JSON Output")
        self.output_text = tk.Text(right, wrap=tk.WORD)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        paned.add(right, weight=3)

    def on_load_sample(self):
        self.input_text.delete("1.0", tk.END)
        self.input_text.insert("1.0", SAMPLE_TEXT)
        messagebox.showinfo("Sample Loaded", "Sample text has been loaded.")

    def on_generate(self):
        text = self.input_text.get("1.0", tk.END)
        if not text.strip():
            messagebox.showwarning("No input", "Please paste the input text first.")
            return

        kanji = self.kanji_var.get().strip()
        if not kanji:
            messagebox.showwarning("Missing Kanji", "Please enter the target Kanji.")
            return

        try:
            blocks = split_blocks(text)
            items = [parse_block(b) for b in blocks]
        except Exception as e:
            messagebox.showerror("Parse error", f"Failed to parse input: {e}")
            return

        objs = []
        for it in items:
            objs.append({
                "kanji": kanji,
                "sentence": it["sentence"],
                "translation": it["translation"],
                "reading help": it["reading_help"],
            })

        pretty = json.dumps(objs, ensure_ascii=False, indent=2)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", pretty)

    def on_copy_json(self):
        data = self.output_text.get("1.0", tk.END).strip()
        if not data:
            messagebox.showwarning("Nothing to copy", "Generate JSON first.")
            return
        self.clipboard_clear()
        self.clipboard_append(data)
        messagebox.showinfo("Copied", "JSON copied to clipboard.")

    def on_save_json(self):
        data = self.output_text.get("1.0", tk.END).strip()
        if not data:
            messagebox.showwarning("Nothing to save", "Generate JSON first.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", ".json"), ("All files", ".*")],
            initialfile="reading-helper.json",
            title="Save JSON"
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(data)
            messagebox.showinfo("Saved", f"Saved to {path}")
        except Exception as e:
            messagebox.showerror("Save error", f"Failed to save file: {e}")


if __name__ == "__main__":
    app = App()
    app.mainloop()
