# -*- coding: utf-8 -*-
import random
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# ========= СЛОВАРИ (EN) =========
PREFIXES_EN = [
    "Dark","Stal","Ghost","Dead","Iron","Blood","Shadow","Radio","Toxic","Cyber",
    "Storm","Acid","Steel","Rust","Night","Grim","Echo","Blind","Silent","Cold",
    "Chern","Rad","Black","Burnt","Lost","Savage","Ash","Nuclear","Wild","Mad","Scar",
    "Dusk","Gloom","Feral","Rogue","Grave","Howl","Hollow","Shiver","Wasted"
]

BASES_EN = [
    "Hunter","Wolf","Bandit","Merc","Stalker","Dog","Sniper","Mutant","Soldier","Raider",
    "Killer","Ghost","Crow","Vulture","Beast","Psy","Scout","Wanderer","Marauder","Seeker",
    "Doctor","Trader","Nomad","Shaman","Zombie","Ghoul","Boar","Bear","Spider","Raven","Shade",
    "Rat","Lurker","Reaper","Butcher","Seer","Howler","Drifter","Strider","Ward","Warden"
]

SUFFIXES_EN = [
    "X","Pro","God","Boss","Elite","One","Last","End","Soul","Core","Void","Hell",
    "Master","King","Lord","Legend","Alpha","Omega","Strike","Shadow","Skull","Ash",
    "Fang","Claw","Gloom","Fury","Mist","Howl","Grim","Wraith"
]

# ========= СЛОВАРИ (RU) =========
PREFIXES_RU = [
    "Тёмный","Стал","Призрачный","Мёртвый","Железный","Кровавый","Теневой","Радиационный","Токсичный","Кибер",
    "Штормовой","Кислотный","Стальной","Ржавый","Ночной","Мрачный","Эхо","Слепой","Безмолвный","Холодный",
    "Черн","Рад","Чёрный","Опалённый","Забытый","Дикий","Пепельный","Ядерный","Сумеречный","Лютый","Шрамный"
]

BASES_RU = [
    "Охотник","Волк","Бандит","Наёмник","Сталкер","Пёс","Снайпер","Мутант","Солдат","Рейдер",
    "Убийца","Призрак","Ворон","Стервятник","Зверь","Пси","Разведчик","Бродяга","Мародёр","Искатель",
    "Доктор","Торговец","Кочевник","Шаман","Зомби","Гуль","Кабан","Медведь","Паук","Вороной","Тень",
    "Крыс","Скрытник","Жнец","Мясник","Провидец","Воющий","Дрифтер","Страйдер","Страж","Хранитель"
]

SUFFIXES_RU = [
    "Х","Про","Бог","Босс","Элита","Один","Последний","Конец","Душа","Ядро","Пустота","Ад",
    "Мастер","Король","Лорд","Легенда","Альфа","Омега","Удар","Тень","Череп","Пепел",
    "Клык","Коготь","Мгла","Ярость","Туман","Вой","Мрач","Призрак"
]

# ========= ЛОГИКА =========
def pick_lists(lang: str):
    if lang == "EN":
        return PREFIXES_EN, BASES_EN, SUFFIXES_EN
    else:
        return PREFIXES_RU, BASES_RU, SUFFIXES_RU

def gen_one(mode: str, use_underscore: bool, max_len: int, lang: str) -> str:
    P, B, S = pick_lists(lang)
    p = random.choice(P)
    b = random.choice(B)

    if mode == "pb_":
        nick = f"{p}_{b}" if use_underscore else f"{p}{b}"
    elif mode == "pbs":
        s = random.choice(S)
        nick = f"{p}{b}{s}"
        if use_underscore and random.random() < 0.5:
            nick = f"{p}_{b}"
    else:  # "pb"
        nick = f"{p}{b}"
        if use_underscore and random.random() < 0.25:
            nick = f"{p}_{b}"

    # убираем двойные подчёркивания
    while "__" in nick:
        nick = nick.replace("__", "_")

    if max_len > 0 and len(nick) > max_len:
        nick = nick[:max_len]

    return nick if len(nick) >= 3 else gen_one(mode, use_underscore, max_len, lang)

def gen_batch(count: int, mode: str, use_underscore: bool, max_len: int, unique: bool, lang: str):
    result, seen = [], set()
    for _ in range(count * 3):
        n = gen_one(mode, use_underscore, max_len, lang)
        if unique and n in seen:
            continue
        seen.add(n)
        result.append(n)
        if len(result) >= count:
            break
    return result[:count] or [gen_one(mode, use_underscore, max_len, lang)]

# ========= GUI =========
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Stalcraft Nickname Generator")
        self.geometry("720x540")
        self.configure(bg="#e6f2ff")  # светло-голубой фон

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#e6f2ff")
        style.configure("TLabelframe", background="#e6f2ff", foreground="#003366")
        style.configure("TLabelframe.Label", background="#e6f2ff", foreground="#003366")
        style.configure("TLabel", background="#e6f2ff", foreground="#003366", font=("Segoe UI", 10))
        style.configure("TCheckbutton", background="#e6f2ff", foreground="#003366")
        style.configure("TRadiobutton", background="#e6f2ff", foreground="#003366")
        style.configure("TButton", background="#3399ff", foreground="white", font=("Segoe UI", 10, "bold"))
        style.map("TButton", background=[("active", "#66b3ff")])

        # Верхняя панель
        top = ttk.Frame(self, padding=10)
        top.pack(fill=tk.X)

        # Режимы
        self.mode = tk.StringVar(value="pb_")
        modes_box = ttk.LabelFrame(top, text="Режим")
        modes_box.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(modes_box, text="PrefixBase (DarkWolf / ТёмныйВолк)", value="pb", variable=self.mode).pack(anchor="w", padx=5)
        ttk.Radiobutton(modes_box, text="Prefix_Base (Dark_Wolf / Тёмный_Волк)", value="pb_", variable=self.mode).pack(anchor="w", padx=5)
        ttk.Radiobutton(modes_box, text="PrefixBaseSuffix (DarkWolfOmega / ТёмныйВолкОмега)", value="pbs", variable=self.mode).pack(anchor="w", padx=5)

        # Опции
        options = ttk.LabelFrame(top, text="Опции")
        options.pack(side=tk.LEFT, padx=(0, 10))
        self.use_underscore = tk.BooleanVar(value=True)
        ttk.Checkbutton(options, text="Разрешить _", variable=self.use_underscore).pack(anchor="w", padx=5)
        self.unique_only = tk.BooleanVar(value=True)
        ttk.Checkbutton(options, text="Только уникальные", variable=self.unique_only).pack(anchor="w", padx=5)
        ttk.Label(options, text="Макс. длина:").pack(anchor="w", padx=5)
        self.max_len = tk.IntVar(value=16)
        ttk.Spinbox(options, from_=0, to=24, textvariable=self.max_len, width=5).pack(anchor="w", padx=5)

        # Язык
        lang_box = ttk.LabelFrame(top, text="Язык")
        lang_box.pack(side=tk.LEFT, padx=(0, 10))
        self.lang = tk.StringVar(value="EN")
        self.lang_combo = ttk.Combobox(lang_box, textvariable=self.lang, values=["EN", "RU"], width=6, state="readonly")
        self.lang_combo.pack(padx=5, pady=10)

        # Количество
        qty_box = ttk.LabelFrame(top, text="Количество")
        qty_box.pack(side=tk.LEFT)
        self.count = tk.IntVar(value=20)
        ttk.Spinbox(qty_box, from_=1, to=200, textvariable=self.count, width=6).pack(padx=5, pady=10)

        # Кнопки
        btns = ttk.Frame(self, padding=(10, 0, 10, 10))
        btns.pack(fill=tk.X)
        ttk.Button(btns, text="Сгенерировать", command=self.on_generate).pack(side=tk.LEFT, padx=5)
        ttk.Button(btns, text="Копировать выделенный", command=self.on_copy).pack(side=tk.LEFT, padx=5)
        ttk.Button(btns, text="Копировать все", command=self.on_copy_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(btns, text="Сохранить в файл...", command=self.on_save).pack(side=tk.RIGHT, padx=5)

        # Список результатов
        list_frame = ttk.Frame(self, padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True)
        self.listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED,
                                  bg="#f0f8ff", fg="#003366", font=("Consolas", 11),
                                  highlightbackground="#3399ff", selectbackground="#66b3ff",
                                  selectforeground="white")
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.listbox.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scroll.set)

        self.on_generate()

    def on_generate(self):
        count = max(1, int(self.count.get()))
        nicks = gen_batch(count, self.mode.get(),
                          bool(self.use_underscore.get()),
                          int(self.max_len.get()),
                          bool(self.unique_only.get()),
                          self.lang.get())
        self.listbox.delete(0, tk.END)
        for n in nicks:
            self.listbox.insert(tk.END, n)

    def on_copy(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo("Копирование", "Выдели хотя бы один ник.")
            return
        text = "\n".join(self.listbox.get(i) for i in sel)
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Копирование", "Скопировано в буфер обмена.")

    def on_copy_all(self):
        n = self.listbox.size()
        if n == 0:
            messagebox.showinfo("Копирование", "Список пуст.")
            return
        text = "\n".join(self.listbox.get(i) for i in range(n))
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Копирование", "Все ники скопированы.")

    def on_save(self):
        n = self.listbox.size()
        if n == 0:
            messagebox.showinfo("Сохранение", "Список пуст.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt",
                                            filetypes=[("Text", "*.txt"), ("All files", "*.*")])
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            for i in range(n):
                f.write(self.listbox.get(i) + "\n")
        messagebox.showinfo("Сохранение", f"Сохранено: {path}")


if __name__ == "__main__":
    App().mainloop()
