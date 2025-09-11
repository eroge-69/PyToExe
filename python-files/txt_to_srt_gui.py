# txt_to_srt_gui.pyw
# -*- coding: utf-8 -*-
import os
import re
import tkinter as tk
from tkinter import filedialog, ttk, messagebox

# ---------------- Sentence splitting with abbreviation handling ----------------

# Common abbreviations that end with a dot but shouldn't split a sentence.
ABBREVIATIONS = {
    # honorifics / titles
    "mr.", "mrs.", "ms.", "dr.", "prof.", "sr.", "jr.", "st.", "sir.", "madam.", "mme.", "mlle.",
    # latin / general
    "e.g.", "i.e.", "etc.", "vs.", "fig.", "al.", "ca.", "approx.",
    # time
    "a.m.", "p.m.",
    # places / orgs
    "u.s.", "u.k.", "u.a.e.", "u.n.", "eu.", "dept.",
    # degrees
    "ph.d.", "m.b.a.", "b.s.", "b.a.", "m.s.",
    # misc abbreviations often seen
    "no.", "vol.", "pp.", "ed.", "rev."
}

# Build patterns for quick protection of periods in abbreviations
# We will temporarily replace the trailing '.' in abbreviations with a placeholder
DOT_PLACEHOLDER = "∯DOT∯"

# Pre-compile a regex to protect dots in abbreviations (case-insensitive)
# Example: turns "Dr." -> "Dr∯DOT∯" so that splitting on sentence punctuation won't cut here.
ABBR_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(a[:-1]) for a in ABBREVIATIONS) + r")\.", re.IGNORECASE
)

# Also protect letter-initials like "J. K. Rowling" or "U.S.A."
# - Single-letter initials: "A." in names
INITIAL_DOT_PATTERN = re.compile(r"(?<=\b[A-Z])\.", re.UNICODE)
# - Consecutive dotted capitals: "U.S." or "U.S.A."
CONSEC_DOTTED_CAPS = re.compile(r"\b(?:[A-Z]\.){2,}")

# Main sentence split regex:
# Split at ., !, ? when followed by whitespace and then a likely sentence-start
SPLIT_REGEX = re.compile(
    r"(?<=[.!?])\s+(?=(?:[“\"'(]*[A-Z0-9]))"
)

def normalize_spaces(text: str) -> str:
    # Collapse multiple spaces, normalize newlines a bit while preserving paragraph boundaries
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    # Convert multiple spaces/tabs to single spaces
    text = re.sub(r"[ \t]+", " ", text)
    # Trim spaces around newlines
    text = re.sub(r" *\n *", "\n", text)
    # Collapse >2 newlines to 2 (paragraphs)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def protect_abbreviations(s: str) -> str:
    # Protect known abbreviations
    s = ABBR_PATTERN.sub(lambda m: m.group(1) + DOT_PLACEHOLDER, s)
    # Protect dotted caps blocks: turn every '.' inside into placeholder
    def repl_caps(m):
        return m.group(0).replace(".", DOT_PLACEHOLDER)
    s = CONSEC_DOTTED_CAPS.sub(repl_caps, s)
    # Protect single-letter initials in names (e.g., "J. R. R. Tolkien")
    s = INITIAL_DOT_PATTERN.sub(DOT_PLACEHOLDER, s)
    return s

def unprotect_abbreviations(s: str) -> str:
    return s.replace(DOT_PLACEHOLDER, ".")

def split_sentences(text: str):
    """Split text into sentences with abbreviation handling."""
    text = normalize_spaces(text)
    protected = protect_abbreviations(text)
    parts = SPLIT_REGEX.split(protected)
    # Restore the dots and clean up
    sentences = [unprotect_abbreviations(p).strip() for p in parts if p and p.strip()]
    return sentences

# ---------------- SRT helpers ----------------

def format_timestamp(total_seconds: int):
    # HH:MM:SS,mmm (we keep ,000 as each block is whole seconds)
    if total_seconds < 0:
        total_seconds = 0
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},000"

def sentences_to_srt(sentences, seconds_per_sentence=5):
    lines = []
    t = 0
    idx = 1
    for s in sentences:
        start = format_timestamp(t)
        end = format_timestamp(t + seconds_per_sentence)
        lines.append(f"{idx}")
        lines.append(f"{start} --> {end}")
        # Optional: wrap very long lines for readability (soft wrap at ~60–70 chars)
        lines.append(s)
        lines.append("")  # blank line between cues
        t += seconds_per_sentence
        idx += 1
    return "\n".join(lines).rstrip() + "\n"


# ---------------- Batch conversion ----------------

def convert_folder(input_dir, output_dir, seconds_per_sentence=5, encoding="utf-8"):
    count = 0
    for name in sorted(os.listdir(input_dir)):
        if not name.lower().endswith(".txt"):
            continue
        in_path = os.path.join(input_dir, name)
        base = os.path.splitext(name)[0]
        out_path = os.path.join(output_dir, base + ".srt")
        try:
            with open(in_path, "r", encoding=encoding, errors="replace") as f:
                text = f.read()
            sentences = split_sentences(text)
            srt = sentences_to_srt(sentences, seconds_per_sentence=seconds_per_sentence)
            with open(out_path, "w", encoding="utf-8", newline="\n") as f:
                f.write(srt)
            count += 1
        except Exception as e:
            print(f"Failed: {name}: {e}")
    return count

# ---------------- GUI ----------------

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TXT → SRT Converter")
        self.geometry("640x260")
        self.resizable(False, False)

        self.input_dir = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.seconds_per_sentence = tk.IntVar(value=5)
        self.encoding = tk.StringVar(value="utf-8")

        pad = {"padx": 10, "pady": 6}

        # Input dir
        ttk.Label(self, text="Thư mục chứa TXT:").grid(row=0, column=0, sticky="e", **pad)
        in_entry = ttk.Entry(self, textvariable=self.input_dir, width=56)
        in_entry.grid(row=0, column=1, **pad)
        ttk.Button(self, text="Chọn...", command=self.pick_input).grid(row=0, column=2, **pad)

        # Output dir
        ttk.Label(self, text="Thư mục xuất SRT:").grid(row=1, column=0, sticky="e", **pad)
        out_entry = ttk.Entry(self, textvariable=self.output_dir, width=56)
        out_entry.grid(row=1, column=1, **pad)
        ttk.Button(self, text="Chọn...", command=self.pick_output).grid(row=1, column=2, **pad)

        # Seconds per sentence
        ttk.Label(self, text="Thời lượng mỗi câu (giây):").grid(row=2, column=0, sticky="e", **pad)
        sec_spin = ttk.Spinbox(self, from_=1, to=60, textvariable=self.seconds_per_sentence, width=8)
        sec_spin.grid(row=2, column=1, sticky="w", **pad)

        # Encoding
        ttk.Label(self, text="Encoding đọc TXT:").grid(row=3, column=0, sticky="e", **pad)
        enc_combo = ttk.Combobox(self, textvariable=self.encoding, values=["utf-8", "utf-16", "cp1258", "cp1252"], width=10)
        enc_combo.grid(row=3, column=1, sticky="w", **pad)

        # Run button
        run_btn = ttk.Button(self, text="RUN", command=self.run_conversion)
        run_btn.grid(row=4, column=1, **pad)

        # Hint
        ttk.Label(self, text="Mặc định tách theo từng câu, xử lý ngoại lệ như Dr., A.M., U.S. ...").grid(
            row=5, column=0, columnspan=3, **pad
        )

    def pick_input(self):
        d = filedialog.askdirectory(title="Chọn thư mục chứa TXT")
        if d:
            self.input_dir.set(d)

    def pick_output(self):
        d = filedialog.askdirectory(title="Chọn thư mục xuất SRT")
        if d:
            self.output_dir.set(d)

    def run_conversion(self):
        in_dir = self.input_dir.get().strip()
        out_dir = self.output_dir.get().strip()
        secs = int(self.seconds_per_sentence.get())
        enc = self.encoding.get()

        if not in_dir or not os.path.isdir(in_dir):
            messagebox.showerror("Lỗi", "Chưa chọn thư mục TXT hợp lệ.")
            return
        if not out_dir:
            out_dir = in_dir
            self.output_dir.set(out_dir)
        os.makedirs(out_dir, exist_ok=True)

        count = convert_folder(in_dir, out_dir, seconds_per_sentence=secs, encoding=enc)
        messagebox.showinfo("Hoàn tất", f"Đã tạo {count} file .srt trong:\n{out_dir}")

if __name__ == "__main__":
    App().mainloop()
