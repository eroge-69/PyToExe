import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import keyboard
import random
import time
import json
import os
import math
import datetime

TYPO_MAP = {
    'q': 'w', 'w': 'qe', 'e': 'wr', 'r': 'et', 't': 'ry', 'y': 'tu', 'u': 'yi', 'i': 'uo', 'o': 'ip', 'p': 'o',
    'a': 'sq', 's': 'ad', 'd': 'sf', 'f': 'dg', 'g': 'fh', 'h': 'gj', 'j': 'hk', 'k': 'jl', 'l': 'k;',
    'z': 'xs', 'x': 'zc', 'c': 'xv', 'v': 'cb', 'b': 'vn', 'n': 'bm', 'm': 'n',
    'й': 'цу', 'ц': 'йу', 'у': 'цы', 'к': 'уел', 'е': 'укн', 'н': 'евг', 'г': 'нш', 'ш': 'гщ', 'щ': 'шз',
    'ф': 'ва', 'ы': 'фв', 'в': 'ыап', 'а': 'выпр', 'п': 'арол', 'р': 'пасо', 'о': 'рлд', 'л': 'олд', 'д': 'олж',
    'я': 'чс', 'ч': 'яшс', 'с': 'ячм', 'м': 'сить', 'и': 'мть', 'т': 'ирь', 'ь': 'тб', 'б': 'ью', 'ю': 'б'
}
for k in list(TYPO_MAP):
    if k.isalpha():
        TYPO_MAP[k.upper()] = TYPO_MAP[k].upper()

def random_typo(text, typo_prob):
    typo_prob = typo_prob / 100
    result = []
    for char in text:
        if char in TYPO_MAP and random.random() < typo_prob:
            result.append(random.choice(TYPO_MAP[char]))
        else:
            result.append(char)
    return ''.join(result)

class PatternStorage:
    def __init__(self, filename='patterns.json'):
        self.filename = filename
        self.patterns = {}
        self.load()
    def load(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    self.patterns = json.load(f)
            except Exception:
                self.patterns = {}
        else:
            self.patterns = {}
    def save(self):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.patterns, f, ensure_ascii=False, indent=2)
    def list(self):
        return list(self.patterns.keys())
    def get(self, name):
        return self.patterns.get(name, "")
    def put(self, name, content):
        self.patterns[name] = content
        self.save()
    def delete(self, name):
        if name in self.patterns:
            del self.patterns[name]
            self.save()

def lerp_color(start, end, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(start, end))

def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(*rgb)

class RoundTabButton(tk.Frame):
    def __init__(self, master, text, active=False, command=None):
        super().__init__(master, bg=master['bg'])
        self.indicator = tk.Canvas(self, width=28, height=28, bg=master['bg'], highlightthickness=0, bd=0)
        self.indicator.pack(side="left", padx=9)
        self.label = tk.Label(self, text=text, font=("Arial", 13, "bold"), fg="#fff", bg=master['bg'])
        self.label.pack(side="left", padx=3)
        self.command = command
        self.active = active
        self.update_circle()
        self.bind("<Button-1>", lambda e: self.onclick())
        self.label.bind("<Button-1>", lambda e: self.onclick())
        self.indicator.bind("<Button-1>", lambda e: self.onclick())
    def update_circle(self):
        self.indicator.delete("all")
        color = "#e52c2c" if self.active else "#3b2022"
        outline = "#fff" if self.active else "#73393a"
        self.indicator.create_oval(4, 4, 24,24, fill=color, outline=outline, width=2)
    def set_active(self, on):
        self.active = on
        self.update_circle()
    def onclick(self):
        if self.command: self.command()

class SoftCheck(tk.Frame):
    def __init__(self, master, variable, **kwargs):
        super().__init__(master, bg=master['bg'])
        self.variable = variable
        self.canvas = tk.Canvas(self, width=26, height=26, highlightthickness=0, bg=master['bg'], bd=0)
        self.canvas.pack()
        self._draw()
        self.canvas.bind("<Button-1>", self.toggle)
    def _draw(self):
        self.canvas.delete("all")
        self.canvas.create_oval(2, 2, 24, 24, fill="#551718", outline="#c73030", width=2)
        if self.variable.get():
            self.canvas.create_line(8, 15, 12, 19, fill="#fff", width=4, capstyle="round")
            self.canvas.create_line(12, 19, 20, 7, fill="#fff", width=4, capstyle="round")
    def toggle(self, event=None):
        self.variable.set(not self.variable.get())
        self._draw()

class AutoTyperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AUTO-TYPER")
        self.iconfile = "lightning.ico"
        if os.path.exists(self.iconfile):
            self.root.iconbitmap(self.iconfile)
        self.root.geometry("860x590")
        self.root.minsize(690, 430)
        self.pat_storage = PatternStorage()
        self.running = False
        self.stoped = False

        self.iter_var = tk.StringVar(value="0/0")
        self.cfg_cyc = tk.IntVar(value=0)
        self.cfg_int = tk.DoubleVar(value=1.0)
        self.cfg_delay = tk.DoubleVar(value=0.0)
        self.cfg_onesend = tk.BooleanVar()
        self.cfg_typo = tk.BooleanVar()
        self.cfg_typo_pct = tk.IntVar(value=8)
        self.cfg_shuffle = tk.BooleanVar()
        self.pattern_name = tk.StringVar()
        self.prefix_var = tk.StringVar()

        self.theme_pos = 0.0
        self.theme_speed = 0.0035
        self.base_colors = ((25,17,20), (229,44,44))
        self.current_bg = "#191114"

        self.frames = {}
        self.tabs = []
        self.make_ui()
        self.animate_theme()
        self.bind_keys()
        self.update_time()

    def animate_theme(self):
        t = (1 + math.sin(self.theme_pos)) / 2
        col = lerp_color(self.base_colors[0], self.base_colors[1], t)
        hexcol = rgb_to_hex(col)
        self.root.configure(bg=hexcol)
        for fr in self.frames.values():
            fr.configure(bg=hexcol)
        if hasattr(self, 'left_menu'):
            self.left_menu.configure(bg=hexcol)
        self.current_bg = hexcol
        self.theme_pos += self.theme_speed
        self.root.after(20, self.animate_theme)

    def update_time(self):
        now = datetime.datetime.now().strftime('%H:%M:%S')
        self.time_label.config(text=now)
        self.root.after(500, self.update_time)

    def make_ui(self):
        self.left_menu = tk.Frame(self.root, bg=self.current_bg, width=152)
        self.left_menu.pack(side="left", fill="y")

        main_area = tk.Frame(self.root, bg=self.current_bg)
        main_area.pack(side="right", fill="both", expand=True)

        self.tab_names = ['Auto-typer', 'Настройки', 'Шаблоны', 'Info']
        for idx, tab in enumerate(self.tab_names):
            btn = RoundTabButton(self.left_menu, text=tab, active=(idx==0), command=lambda i=idx: self.show_tab(i))
            btn.pack(pady=(25 if idx == 0 else 9, 0), anchor="w")
            self.tabs.append(btn)

        f1 = tk.Frame(main_area, bg=self.current_bg)
        tk.Label(f1, text="Вставьте перечень строк для отправки",
                 bg=self.current_bg, fg="#fff", font=("Arial", 14, "bold")).pack(pady=(22,7))
        self.text_area = scrolledtext.ScrolledText(f1, width=52, height=8, wrap=tk.WORD, font=("Arial", 12),
            bg="#2c161a", fg="#fff", insertbackground="#fff", borderwidth=0)
        self.text_area.pack(pady=(0,13))
        tk.Label(f1, text="Префикс (например, @admin):", bg=self.current_bg, fg="#fff", font=("Arial", 11)).pack()
        tk.Entry(f1, textvariable=self.prefix_var, bg="#2c161a", fg="#fff", font=("Arial", 11),
                 insertbackground="#fff", borderwidth=0, width=24).pack()
        area = tk.Frame(f1, bg=self.current_bg)
        area.pack(pady=(13,4), anchor="w")
        tk.Label(area, text="Итерация:", bg=self.current_bg, fg="#fff", font=("Arial", 12)).pack(side="left")
        self.iter_entry = tk.Entry(area, textvariable=self.iter_var, font=("Arial", 11),
                                   width=8, bg="#211517", fg="#fff", borderwidth=0,
                                   readonlybackground="#23272e")
        self.iter_entry.pack(side="left", padx=(6,0))
        self.iter_entry.config(state="readonly")
        self.iter_entry.bind("<Control-a>", self.selall)
        self.iter_entry.bind("<Control-A>", self.selall)
        tk.Label(f1, text="F8 — запуск   |   F9 — стоп   |   шаблон — вкладка Шаблоны",
                 bg=self.current_bg, fg="#fff", font=("Arial", 10)).pack(anchor="center", pady=(6,4))
        self.frames[0] = f1

        f2 = tk.Frame(main_area, bg=self.current_bg)
        cpad = {'padx':14, 'pady':6}
        tk.Label(f2, text="Настройки Auto-Typer", font=("Arial", 15, "bold"), fg="#fff", bg=self.current_bg).pack(anchor="w", pady=(23,11), padx=14)
        form = tk.Frame(f2, bg=self.current_bg)
        form.pack(anchor="w", padx=29)
        tk.Label(form, text="Циклов (0=∞):", font=("Arial", 12), bg=self.current_bg, fg="#fff") \
            .grid(row=0, column=0, sticky="w", **cpad)
        tk.Entry(form, textvariable=self.cfg_cyc, width=6, bg="#2c161a",
                 fg="#fff", insertbackground="#fff", borderwidth=0, font=("Arial", 12)).grid(row=0, column=1, sticky="w", **cpad)
        tk.Label(form, text="Интервал (сек):", font=("Arial", 12), bg=self.current_bg, fg="#fff") \
            .grid(row=1, column=0, sticky="w", **cpad)
        tk.Entry(form, textvariable=self.cfg_int, width=6, bg="#2c161a",
                 fg="#fff", insertbackground="#fff", borderwidth=0, font=("Arial", 12)).grid(row=1, column=1, sticky="w", **cpad)
        tk.Label(form, text="Задержка буквы (мс):", font=("Arial", 12), bg=self.current_bg, fg="#fff") \
            .grid(row=2, column=0, sticky="w", **cpad)
        tk.Entry(form, textvariable=self.cfg_delay, width=6, bg="#2c161a",
                 fg="#fff", insertbackground="#fff", borderwidth=0, font=("Arial", 12)).grid(row=2, column=1, sticky="w", **cpad)
        tk.Label(form, text="Случайный порядок", font=("Arial", 12), bg=self.current_bg, fg="#fff") \
            .grid(row=3, column=0, sticky="w", **cpad)
        switch_shuffle = SoftCheck(form, self.cfg_shuffle)
        switch_shuffle.grid(row=3, column=1, sticky="w", **cpad)
        tk.Label(form, text="Всё одной строкой", font=("Arial", 12), bg=self.current_bg, fg="#fff") \
            .grid(row=4, column=0, sticky="w", **cpad)
        switch_onesend = SoftCheck(form, self.cfg_onesend)
        switch_onesend.grid(row=4, column=1, sticky="w", **cpad)
        tk.Label(form, text="Имитировать опечатки", font=("Arial", 12), bg=self.current_bg, fg="#fff") \
            .grid(row=5, column=0, sticky="w", **cpad)
        switch_typo = SoftCheck(form, self.cfg_typo)
        switch_typo.grid(row=5, column=1, sticky="w", **cpad)
        tk.Label(form, text="Процент опечаток:", font=("Arial", 12), bg=self.current_bg, fg="#fff") \
            .grid(row=6, column=0, sticky="w", **cpad)
        tk.Spinbox(form, from_=0, to=100, width=5, textvariable=self.cfg_typo_pct, font=("Arial", 12),
                   bg="#2c161a", fg="#fff", borderwidth=0, highlightthickness=0).grid(row=6, column=1, sticky="w", **cpad)
        self.frames[1] = f2

        f3 = tk.Frame(main_area, bg=self.current_bg)
        fr3 = tk.Frame(f3, bg=self.current_bg)
        fr3.pack(fill="both", expand=True, padx=10, pady=23)
        self.pattern_box = tk.Listbox(fr3, font=("Arial", 12), bg="#2c161a", fg="#fff",
                                      selectbackground="#b91724", width=24, height=8, borderwidth=0)
        self.pattern_box.pack(side="left", fill="y", padx=(6,17), pady=(8,8))
        self.pattern_box.bind("<Double-Button-1>", self.use_pattern)
        self.pattern_box.bind("<<ListboxSelect>>", self.pattern_selected)
        boxfr = tk.Frame(fr3, bg=self.current_bg)
        boxfr.pack(anchor="w", padx=(9,0))
        tk.Label(boxfr, text="Имя шаблона:", bg=self.current_bg, fg="#fff", font=("Arial", 12)) \
            .pack(anchor="w")
        tk.Entry(boxfr, textvariable=self.pattern_name, width=16, bg="#2c161a",
                 fg="#fff", borderwidth=0, font=("Arial", 11)).pack(anchor="w", pady=(2,7))
        tk.Button(boxfr, text="Сохранить как шаблон", font=("Arial", 11, "bold"),
                  bg="#e52c2c", fg="#fff", command=self.save_pattern, relief="flat", activebackground="#a02121").pack(anchor="w", pady=(4,7))
        tk.Button(boxfr, text="Удалить шаблон", font=("Arial", 11, "bold"),
                  bg="#e52c2c", fg="#fff", command=self.delete_pattern, relief="flat", activebackground="#a02121").pack(anchor="w")
        self.refresh_patterns()
        self.frames[2] = f3

        f4 = tk.Frame(main_area, bg=self.current_bg)
        tk.Label(f4, text="By: neskwik", font=("Arial", 25, "bold"),
                 fg="#fff", bg=self.current_bg).pack(pady=(100,8))
        tk.Label(f4, text="Discord: 3nn6", font=("Arial", 20, "bold"),
                 fg="#fff", bg=self.current_bg).pack(pady=(0,6))
        discord_button = tk.Button(f4, text="Скопировать Discord", font=("Arial", 11, "bold"),
                                   bg="#e52c2c", fg="#fff",
                                   command=lambda: self.copy_discord("3nn6"),
                                   relief="flat", activebackground="#a02121")
        discord_button.pack()
        self.frames[3] = f4

        for ind, fr in self.frames.items():
            fr.place(relwidth=1, relheight=1)
            fr.lower()
        self.frames[0].lift()

        self.time_label = tk.Label(self.root, fg="#fff", bg=self.current_bg, font=("Arial", 12))
        self.time_label.place(relx=1.0, rely=0.0, anchor="ne", x=-16, y=9)

    def pattern_selected(self, event):
        try:
            idx = self.pattern_box.curselection()[0]
            self.pattern_box.itemconfig(idx, {'bg': "#ff3838"})
        except IndexError:
            return

    def show_tab(self, index):
        for i, tab in enumerate(self.tabs):
            tab.set_active(i==index)
        for i, fr in self.frames.items():
            if i == index:
                fr.lift()
            else:
                fr.lower()

    def selall(self, event):
        event.widget.config(state="normal")
        event.widget.select_range(0, tk.END)
        event.widget.icursor(tk.END)
        event.widget.config(state="readonly")
        return 'break'

    def bind_keys(self):
        keyboard.add_hotkey('f8', self.start_async)
        keyboard.add_hotkey('f9', self.stop)

    def start_async(self):
        if not self.running:
            self.root.after(1, self.start)

    def save_pattern(self):
        name = self.pattern_name.get().strip()
        if not name:
            messagebox.showwarning("Ошибка", "Введите имя шаблона!")
            return
        content = self.text_area.get("1.0", "end").strip()
        self.pat_storage.put(name, content)
        self.refresh_patterns()
        messagebox.showinfo("Шаблон", "Сохранено!")

    def delete_pattern(self):
        idxs = self.pattern_box.curselection()
        if not idxs:
            return
        name = self.pattern_box.get(idxs[0])
        self.pat_storage.delete(name)
        self.refresh_patterns()

    def use_pattern(self, event):
        idxs = self.pattern_box.curselection()
        if not idxs:
            return
        name = self.pattern_box.get(idxs[0])
        content = self.pat_storage.get(name)
        self.text_area.delete("1.0", "end")
        self.text_area.insert("1.0", content)

    def refresh_patterns(self):
        self.pattern_box.delete(0, tk.END)
        for n in self.pat_storage.list():
            self.pattern_box.insert(tk.END, n)

    def start(self):
        if self.running:
            return
        self.stoped = False
        self.running = True
        t = threading.Thread(target=self.autotype)
        t.daemon = True
        t.start()

    def stop(self):
        self.stoped = True
        self.running = False
        self.iter_var.set("0/0")

    def autotype(self):
        texts = [s.strip() for s in self.text_area.get("1.0", "end").strip().split('\n') if s.strip()]
        if not texts:
            messagebox.showwarning("Ошибка", "Заполните список строк!")
            self.stoped = True
            self.running = False
            return
        n_all = len(texts)
        n_cyc = self.cfg_cyc.get()
        prefix = self.prefix_var.get().strip()
        onesend = self.cfg_onesend.get()
        shuffle = self.cfg_shuffle.get()
        use_typo = self.cfg_typo.get()
        typo_pct = self.cfg_typo_pct.get()
        pause = self.cfg_int.get()
        btndelay = self.cfg_delay.get() / 1000.0

        seq = texts[:]
        total = 0
        cycles = 0
        self.iter_var.set(f"{cycles}/{n_cyc if n_cyc else '∞'}")

        while not self.stoped:
            sarr = seq[:]
            if shuffle:
                random.shuffle(sarr)
            for line in ([" ".join(sarr)] if onesend else sarr):
                if prefix:
                    line = prefix + " " + line
                if use_typo:
                    line = random_typo(line, typo_pct)
                keyboard.write(line, delay=btndelay)
                keyboard.press_and_release("enter")
                total += 1
                self.iter_var.set(f"{cycles+1}/{n_cyc if n_cyc else '∞'}")
                time.sleep(pause)
                if self.stoped:
                    break
            cycles += 1
            self.iter_var.set(f"{cycles}/{n_cyc if n_cyc else '∞'}")
            if n_cyc > 0 and cycles >= n_cyc:
                self.running = False
                break

        self.running = False
        self.stoped = False
        self.iter_var.set("0/0")

    def copy_discord(self, nick):
        self.root.clipboard_clear()
        self.root.clipboard_append(nick)
        messagebox.showinfo("Discord", f"{nick} скопирован в буфер обмена!")

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoTyperApp(root)
    root.mainloop()
