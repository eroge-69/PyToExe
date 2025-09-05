# -*- coding: utf-8 -*-
"""
YAML Quote Translator (EN -> FA) with PersianReshaper & tkinter GUI
- Skips translation/shaping for keys: name, version
- Shaping is applied only to translated quoted text
- Output in 'output' subfolder
Requires: pip install deep-translator
"""
import os
import re
import time
import threading
import queue
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
from deep_translator import GoogleTranslator

# ---------------- Persian Reshaper Class ----------------
class PersianReshaper:
    def __init__(self, enable_persian_numbers=False, enable_arabic_numbers=False, enable_harakat=True):
        self.e_numbers = 1 if enable_arabic_numbers else 0
        self.f_numbers = 1 if enable_persian_numbers else 0
        self.e_harakat = 1 if enable_harakat else 0
        self.left = "ڤـئظشسيیبلپتنمكکگطضصثقفغعهخچحج"
        self.right = "ڤـئؤرلالآىیآةوزژظشسيپبللأاأتنمكکگطضصثقفغعهخحچجدذلإإ"
        self.arnumbs = "0123456789"
        self.fanumbs = "0123456789"
        self.ennumbs = "0123456789"
        self.harakat = "ًٌٍَُِّْ"
        self.symbols = "ـ.،؟ @#$%^&*-+|\/=~,:"
        self.unicode_chars = (
            "ﺁﺁﺂﺂ" + "ﺃﺃﺄﺄ" + "ﺇﺇﺈﺈ" + "ﺍﺍﺎﺎ" + "ﺏﺑﺒﺐ" + "ﺕﺗﺘﺖ" + "ﺙﺛﺜﺚ" +
            "ﺝﺟﺠﺞ" + "ﺡﺣﺤﺢ" + "ﺥﺧﺨﺦ" + "ﺩﺩﺪﺪ" + "ﺫﺫﺬﺬ" + "ﺭﺭﺮﺮ" + "ﺯﺯﺰﺰ" +
            "ﺱﺳﺴﺲ" + "ﺵﺷﺸﺶ" + "ﺹﺻﺼﺺ" + "ﺽﺿﻀﺾ" + "ﻁﻃﻄﻂ" + "ﻅﻇﻈﻆ" +
            "ﻉﻋﻌﻊ" + "ﻍﻏﻐﻎ" + "ﻑﻓﻔﻒ" + "ﻕﻗﻘﻖ" + "ﻙﻛﻜﻚ" + "ﻝﻟﻠﻞ" +
            "ﻡﻣﻤﻢ" + "ﻥﻧﻨﻦ" + "ﻩﻫﻬﻪ" + "ﻭﻭﻮﻮ" + "ﻱﻳﻴﻲ" + "ﺓﺓﺔﺔ" +
            "ﺅﺅﺆﺆ" + "ﺉﺋﺌﺊ" + "ﻯﻯﻰﻰ" + "گﮔﮕﮓ" + "چﭼﭽﭻ" +
            "پﭘﭙﭗ" + "ژﮊﮋﮋ" + "ﯼﯾﯿﯽ" + "کﮐﮑﮏ" + "ﭪﭬﭭﭫ" +
            "ﻵﻵﻶﻶ" + "ﻷﻷﻸﻷ" + "ﻹﻹﻺﻺ" + "ﻻﻻﻼﻼ"
        )
        self.arabic_chars = (
            "آ" + "أ" + "إ" + "ا" + "ب" + "ت" + "ث" + "ج" + "ح" + "خ" +
            "د" + "ذ" + "ر" + "ز" + "س" + "ش" + "ص" + "ض" + "ط" + "ظ" +
            "ع" + "غ" + "ف" + "ق" + "ك" + "ل" + "م" + "ن" + "ه" + "و" +
            "ي" + "ة" + "ؤ" + "ئ" + "ى" + "گ" + "چ" + "پ" + "ژ" + "ی" +
            "ک" + "ڤ"
        )
        self.laa_index = 168
        self.not_english = self.arabic_chars + self.harakat + "ء،؟"
        self.brackets = "(){}[]"

    def _get_char_pos(self, text_list, index):
        def get_effective_char(offset):
            b = offset
            while 0 <= index + b < len(text_list) and text_list[index + b] in self.harakat:
                b += offset
            if 0 <= index + b < len(text_list):
                return text_list[index + b]
            return None
        prev_char = get_effective_char(-1)
        next_char = get_effective_char(1)
        can_connect_left = prev_char is not None and prev_char in self.left
        can_connect_right = next_char is not None and next_char in self.right
        if not can_connect_left and not can_connect_right:
            return 0
        elif not can_connect_left and can_connect_right:
            return 1
        elif can_connect_left and can_connect_right:
            return 2
        elif can_connect_left and not can_connect_right:
            return 3
        return 0

    def process(self, text):
        output_chars, text_chars, i = [], list(text), 0
        while i < len(text_chars):
            char = text_chars[i]
            if char in self.arabic_chars:
                pos = self._get_char_pos(text_chars, i)
                if char == 'ل':
                    next_char_idx = i + 1
                    while next_char_idx < len(text_chars) and text_chars[next_char_idx] in self.harakat:
                        next_char_idx += 1
                    if next_char_idx < len(text_chars) and text_chars[next_char_idx] in "آأإا":
                        laa_char = text_chars[next_char_idx]
                        ar_pos = "آأإا".find(laa_char)
                        output_chars.append(self.unicode_chars[(ar_pos * 4) + pos + self.laa_index])
                        i = next_char_idx
                    else:
                        ar_pos = self.arabic_chars.find(char)
                        output_chars.append(self.unicode_chars[(ar_pos * 4) + pos])
                else:
                    ar_pos = self.arabic_chars.find(char)
                    output_chars.append(self.unicode_chars[(ar_pos * 4) + pos])
            elif char in self.harakat:
                if self.e_harakat:
                    output_chars.append(char)
            elif char == 'ء':
                output_chars.append("ﺀ")
            elif char in self.brackets:
                idx = self.brackets.find(char)
                output_chars.append(self.brackets[idx + 1] if idx % 2 == 0 else self.brackets[idx - 1])
            elif char in self.symbols or char in ['\n', '\r']:
                output_chars.append(char)
            else:
                english_run, j = [], i
                while j < len(text_chars) and text_chars[j] not in self.not_english and text_chars[j] not in self.brackets:
                    c = text_chars[j]
                    if c in self.ennumbs:
                        num_idx = self.ennumbs.find(c)
                        if self.e_numbers == 1: c = self.arnumbs[num_idx]
                        elif self.f_numbers == 1: c = self.fanumbs[num_idx]
                    elif c in self.arnumbs:
                        if self.e_numbers == 0: c = self.ennumbs[self.arnumbs.find(c)]
                    elif c in self.fanumbs:
                        if self.f_numbers == 0: c = self.ennumbs[self.fanumbs.find(c)]
                    english_run.append(c)
                    j += 1
                output_chars.extend(reversed(english_run))
                i = j - 1
            i += 1
        output_chars.reverse()
        return "".join(output_chars)

# ---------------- Translation Logic ----------------
CHAR_LIMIT = 4800
DELAY_BETWEEN_CHUNKS = 0.5
SPECIAL_KEYS = {"name", "version"}

def translate_yaml_quotes(folder_path, log_func):
    reshaper = PersianReshaper(enable_persian_numbers=False)  # numbers remain English
    output_folder = os.path.join(folder_path, "output")
    os.makedirs(output_folder, exist_ok=True)
    log_func(f"Output folder created: {output_folder}\n")
    files = [f for f in os.listdir(folder_path) if f.lower().endswith((".yml", ".yaml"))]
    if not files:
        log_func("No YAML files found.\n")
        return
    translator = GoogleTranslator(source="en", target="fa")
    quote_pattern = re.compile(r'([\'"])(.+?)\1')
    for filename in files:
        input_path = os.path.join(folder_path, filename)
        output_path = os.path.join(output_folder, filename)
        log_func(f"\nProcessing {filename}\n")
        try:
            with open(input_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            chunks, translation_map = [], []
            for i, line in enumerate(lines):
                key_match = re.match(r'^\s*([^:]+):', line)
                current_key = key_match.group(1).strip() if key_match else None
                for m in quote_pattern.finditer(line):
                    if current_key in SPECIAL_KEYS: 
                        continue
                    content = m.group(2)
                    if content.strip():
                        chunks.append(content)
                        translation_map.append((i, m.span(2), content))
            if not chunks:
                with open(output_path, "w", encoding="utf-8") as f:
                    f.writelines(lines)
                log_func("  -> No translatable content.\n")
                continue
            translated_chunks, batch, char_count = [], [], 0
            def flush_batch():
                nonlocal batch, char_count, translated_chunks
                if batch:
                    try:
                        txt = "\n".join(batch)
                        res = translator.translate(txt)
                        if isinstance(res, list): translated_chunks.extend(res)
                        else: translated_chunks.extend(res.split("\n"))
                    except Exception as e:
                        log_func(f"  -> Translation error: {e}\n")
                        translated_chunks.extend(batch)
                    batch.clear(); char_count = 0
                    time.sleep(DELAY_BETWEEN_CHUNKS)
            for c in chunks:
                if char_count + len(c) > CHAR_LIMIT and batch:
                    flush_batch()
                batch.append(c)
                char_count += len(c)
            flush_batch()
            for (line_idx, span, _), t_text in zip(translation_map, translated_chunks):
                shaped = reshaper.process(t_text)
                s = lines[line_idx]
                lines[line_idx] = s[:span[0]] + shaped + s[span[1]:]
            with open(output_path, "w", encoding="utf-8") as f:
                f.writelines(lines)
            log_func("  -> Done.\n")
        except Exception as e:
            log_func(f"  -> Error: {e}\n")
    log_func("\nAll YAML processing complete!\n")

# ---------------- GUI Logger ----------------
class GuiLogger:
    def __init__(self, text_widget, root):
        self.text_widget = text_widget
        self.root = root
        self.queue = queue.Queue()
        self._running = True
        self._drain()
    def log(self, msg):
        self.queue.put(str(msg))
    def _drain(self):
        try:
            while True:
                msg = self.queue.get_nowait()
                self.text_widget.insert(tk.END, msg)
                self.text_widget.see(tk.END)
        except queue.Empty:
            pass
        if self._running:
            self.root.after(100, self._drain)
    def stop(self):
        self._running = False

# ---------------- Tkinter App ----------------
def create_app():
    root = tk.Tk()
    root.title("YAML Quote Translator (EN -> FA) + Reshaper")
    root.geometry("760x520")
    frm_top = ttk.Frame(root, padding=8)
    frm_top.pack(fill=tk.X)
    folder_var = tk.StringVar()
    ttk.Label(frm_top, text="Select folder with YAML files:").pack(side=tk.LEFT)
    ttk.Entry(frm_top, textvariable=folder_var, width=65).pack(side=tk.LEFT, padx=8)
    def browse_folder():
        path = filedialog.askdirectory()
        if path:
            folder_var.set(path)
            logger.log(f"Selected folder: {path}\n")
    btn_browse = ttk.Button(frm_top, text="Browse...", command=browse_folder)
    btn_browse.pack(side=tk.LEFT)
    frm_mid = ttk.Frame(root, padding=8)
    frm_mid.pack(fill=tk.X)
    btn_start = ttk.Button(frm_mid, text="Start Translation")
    btn_start.pack(side=tk.LEFT)
    progress_label = ttk.Label(frm_mid, text="")
    progress_label.pack(side=tk.LEFT, padx=10)
    txt = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=25)
    txt.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
    global logger
    logger = GuiLogger(txt, root)
    def worker(folder):
        btn_start.config(state=tk.DISABLED)
        btn_browse.config(state=tk.DISABLED)
        progress_label.config(text="Processing...")
        translate_yaml_quotes(folder, logger.log)
        btn_start.config(state=tk.NORMAL)
        btn_browse.config(state=tk.NORMAL)
        progress_label.config(text="")
    def start_task():
        folder = folder_var.get().strip()
        if not os.path.isdir(folder):
            messagebox.showerror("Error", "Invalid folder path")
            return
        threading.Thread(target=worker, args=(folder,), daemon=True).start()
    btn_start.config(command=start_task)
    root.protocol("WM_DELETE_WINDOW", lambda: (logger.stop(), root.destroy()))
    return root

if __name__ == "__main__":
    app = create_app()
    app.mainloop()
