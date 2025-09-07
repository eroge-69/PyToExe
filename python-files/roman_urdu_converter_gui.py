# Roman Urdu to Urdu Converter - Tkinter GUI
import re
import json
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

APP_NAME = "Roman Urdu → Urdu Converter"
VERSION = "1.0"

LEXICON = {
    "mein": "میں", "me": "میں", "main": "میں", "mai": "میں", "maiN": "میں",
    "maiN": "میں", "men": "میں",
    "tum": "تم", "aap": "آپ", "ap": "آپ",
    "wo": "وہ", "woh": "وہ", "vo": "وہ",
    "hum": "ہم", "ham": "ہم",
    "un": "ان", "in": "ان",
    "ye": "یہ", "yeh": "یہ", "yey": "یہ", "y": "ی",
    "kya": "کیا", "kia": "کیا",
    "kyun": "کیوں", "kyon": "کیوں",
    "jo": "جو",
    "jis": "جس",
    "koi": "کوئی",
    "sab": "سب",
    "ab": "اب",
    "phir": "پھر", "fir": "پھر",
    "agar": "اگر",
    "magar": "مگر",
    "lekin": "لیکن", "likin": "لیکن",
    "bohat": "بہت", "bahut": "بہت",
    "zyada": "زیادہ", "ziada": "زیادہ",
    "thoda": "تھوڑا", "thora": "تھوڑا",
    "thori": "تھوڑی", "thora sa": "تھوڑا سا",
    "acha": "اچھا", "achha": "اچھا", "accha": "اچھا",
    "achhi": "اچھی",
    "bura": "بُرا", "buri": "بری",
    "acha lag": "اچھا لگ",
    "nahi": "نہیں", "nahiN": "نہیں", "nai": "نہیں",
    "han": "ہاں", "haan": "ہاں",
    "nahin": "نہیں",
    "hai": "ہے", "hay": "ہے", "hey": "ہے",
    "hain": "ہیں", "hen": "ہیں",
    "hon": "ہوں", "hun": "ہوں",
    "tha": "تھا", "thi": "تھی", "thy": "تھے", "thay": "تھے", "the": "تھے",
    "raha": "رہا", "rahi": "رہی", "rahe": "رہے",
    "kar": "کر", "ker": "کر", "kr": "کر",
    "karta": "کرتا", "kartay": "کرتے", "karte": "کرتے", "karti": "کرتی",
    "karo": "کرو",
    "kya hua": "کیا ہوا",
    "ho": "ہو",
    "gi": "گی", "ga": "گا", "ge": "گے",
    "se": "سے", "ko": "کو", "ka": "کا", "ki": "کی", "ke": "کے",
    "par": "پر", "per": "پر", "pe": "پر",
    "tak": "تک",
    "ky": "کی", "k": "کے",

    "aj": "آج", "aaj": "آج",
    "kal": "کل",
    "abhi": "ابھی",
    "baad": "بعد",
    "pehle": "پہلے",
    "der": "دیر",

    "dekh": "دیکھ",
    "bolo": "بولو", "kaho": "کہو",
    "chalo": "چلو",
    "chahiye": "چاہیے", "chahie": "چاہیے", "chahye": "چاہیے",
    "pyar": "پیار", "mohabbat": "محبت",
    "khushi": "خوشی",
    "dard": "درد",
    "mujhe": "مجھے", "mujhay": "مجھے",
    "tujhe": "تجھے", "tumhe": "تمہیں", "tumhain": "تمہیں", "tumhein": "تمہیں",
    "usay": "اسے", "usse": "اسے",
    "khuda": "خدا", "allah": "اللہ",
    "shukriya": "شکریہ", "meharbani": "مہربانی",
    "zindagi": "زندگی",
    "maaf": "معاف",
}

def transliterate_basic(text: str) -> str:
    placeholders = {}
    def protect(text, pattern, tag):
        i = 0
        def repl(m):
            nonlocal i
            key = f"§{tag}{i}§"
            placeholders[key] = m.group(0)
            i += 1
            return key
        return re.sub(pattern, repl, text)
    text = protect(text, r"https?://\\S+|www\\.\\S+", "URL")
    text = protect(text, r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}", "MAIL")
    text = protect(text, r"\\d+(?:[.,]\\d+)?", "NUM")

    rules = [
        (r"kh", "خ"),
        (r"gh", "غ"),
        (r"chh", "چھ"),
        (r"ch", "چ"),
        (r"sh", "ش"),
        (r"zh", "ژ"),
        (r"ph", "ف"),
        (r"bh", "بھ"),
        (r"jh", "جھ"),
        (r"th", "تھ"),
        (r"dh", "دھ"),
        (r"q", "ق"),
        (r"g", "گ"),
        (r"z", "ز"),
        (r"j", "ج"),
        (r"h", "ہ"),
        (r"k", "ک"),
        (r"t", "ت"),
        (r"d", "د"),
        (r"p", "پ"),
        (r"b", "ب"),
        (r"r", "ر"),
        (r"s", "س"),
        (r"y", "ی"),
        (r"i", "ِ"),
        (r"u", "ُ"),
        (r"o", "و"),
        (r"aa", "ا"),
        (r"a", "َ"),
        (r"e", "ے"),
        (r"m", "م"),
        (r"n", "ن"),
        (r"l", "ل"),
        (r"f", "ف"),
        (r"w", "و"),
    ]

    out = []
    for token in re.split(r"(\\s+)", text):
        if token.strip() == "":
            out.append(token); continue
        lower = token.lower()
        t = lower
        for pat, rep in rules:
            t = re.sub(pat, rep, t, flags=re.IGNORECASE)
        out.append(t)

    result = "".join(out)
    for key, val in placeholders.items():
        result = result.replace(key, val)
    result = re.sub(r"[َُِ]{2,}", "", result)
    return result

def apply_lexicon(text: str, lexicon: dict) -> str:
    keys = sorted(lexicon.keys(), key=len, reverse=True)
    for k in keys:
        pattern = r'(?i)(?<!\\w)' + re.escape(k) + r'(?!\\w)'
        text = re.sub(pattern, lexicon[k], text)
    return text

def roman_to_urdu(text: str, user_lex=None) -> str:
    if user_lex:
        text = apply_lexicon(text, user_lex)
    text = apply_lexicon(text, LEXICON)
    text = transliterate_basic(text)
    text = re.sub(r"[َُِ]{2,}", "", text)
    return text

class ConverterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME}  v{VERSION}")
        self.geometry("960x640")
        self.user_lex = {}
        self.user_lex_path = Path.home() / ".roman_urdu_user_lexicon.json"
        self._load_user_lex()
        self._build_ui()

    def _build_ui(self):
        root = ttk.Frame(self, padding=12); root.pack(fill="both", expand=True)
        top = ttk.Frame(root); top.pack(fill="x", pady=(0, 8))
        ttk.Label(top, text="Roman Urdu → Urdu (Offline)").pack(side="left")
        ttk.Button(top, text="Open Text…", command=self.open_text).pack(side="right", padx=(6,0))
        ttk.Button(top, text="Save Output…", command=self.save_output).pack(side="right", padx=(6,0))
        ttk.Button(top, text="Convert", command=self.convert).pack(side="right")

        paned = ttk.Panedwindow(root, orient="horizontal"); paned.pack(fill="both", expand=True)
        left = ttk.Frame(paned, padding=(0,0,6,0))
        right = ttk.Frame(paned, padding=(6,0,0,0))
        paned.add(left, weight=1); paned.add(right, weight=1)

        ttk.Label(left, text="Input (Roman Urdu)").pack(anchor="w")
        self.in_text = tk.Text(left, wrap="word", font=("Noto Sans", 12))
        self.in_text.pack(fill="both", expand=True)

        ttk.Label(right, text="Output (Urdu)").pack(anchor="w")
        self.out_text = tk.Text(right, wrap="word", font=("Noto Nastaliq Urdu", 16, "normal"))
        self.out_text.pack(fill="both", expand=True)

        lex_frame = ttk.LabelFrame(root, text="Custom Dictionary (Roman → Urdu)")
        lex_frame.pack(fill="x", pady=(8,0))
        self.entry_key = ttk.Entry(lex_frame, width=30)
        self.entry_val = ttk.Entry(lex_frame, width=30)
        ttk.Label(lex_frame, text="Roman:").grid(row=0, column=0, padx=4, pady=6, sticky="e")
        self.entry_key.grid(row=0, column=1, padx=4, pady=6, sticky="w")
        ttk.Label(lex_frame, text="Urdu:").grid(row=0, column=2, padx=4, pady=6, sticky="e")
        self.entry_val.grid(row=0, column=3, padx=4, pady=6, sticky="w")
        ttk.Button(lex_frame, text="Add/Update", command=self.add_lex).grid(row=0, column=4, padx=6)
        ttk.Button(lex_frame, text="Save Dictionary", command=self.save_lex).grid(row=0, column=5, padx=6)
        lex_frame.grid_columnconfigure(1, weight=1); lex_frame.grid_columnconfigure(3, weight=1)

        footer = ttk.Frame(root); footer.pack(fill="x", pady=(8,0))
        ttk.Label(footer, text="Tip: Add tricky words to the custom dictionary for perfect results.").pack(side="left")

    def open_text(self):
        path = filedialog.askopenfilename(title="Open Text File", filetypes=[("Text Files", "*.txt"), ("All files", "*.*")])
        if not path: return
        try:
            content = Path(path).read_text(encoding="utf-8", errors="ignore")
            self.in_text.delete("1.0", "end"); self.in_text.insert("1.0", content)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file:\\n{e}")

    def save_output(self):
        path = filedialog.asksaveasfilename(title="Save Output", defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if not path: return
        try:
            content = self.out_text.get("1.0", "end-1c")
            Path(path).write_text(content, encoding="utf-8")
            messagebox.showinfo("Saved", "Output saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file:\\n{e}")

    def convert(self):
        src = self.in_text.get("1.0", "end-1c")
        if not src.strip():
            messagebox.showwarning("Empty", "Please paste or type Roman Urdu text first."); return
        try:
            out = roman_to_urdu(src, self.user_lex)
            self.out_text.delete("1.0", "end"); self.out_text.insert("1.0", out)
        except Exception as e:
            messagebox.showerror("Error", f"Conversion failed:\\n{e}")

    def add_lex(self):
        k = self.entry_key.get().strip()
        v = self.entry_val.get().strip()
        if not k or not v:
            messagebox.showwarning("Missing", "Enter both Roman and Urdu."); return
        self.user_lex[k] = v
        messagebox.showinfo("Added", f"Added/updated mapping:\\n{k} → {v}")
        self.entry_key.delete(0, "end"); self.entry_val.delete(0, "end")

    def _load_user_lex(self):
        try:
            if self.user_lex_path.exists():
                self.user_lex = json.loads(self.user_lex_path.read_text(encoding="utf-8"))
        except Exception:
            self.user_lex = {}

    def save_lex(self):
        try:
            self.user_lex_path.write_text(json.dumps(self.user_lex, ensure_ascii=False, indent=2), encoding="utf-8")
            messagebox.showinfo("Saved", f"Dictionary saved to:\\n{self.user_lex_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save dictionary:\\n{e}")

if __name__ == "__main__":
    app = ConverterApp()
    app.mainloop()
