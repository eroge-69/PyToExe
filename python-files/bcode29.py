import tkinter as tk
from tkinter import ttk
import os

# ---------- Validation helper ----------
def make_numeric_limiter(root, max_len):
    def _validate(proposed):
        return proposed == "" or (proposed.isdigit() and len(proposed) <= max_len)
    return (root.register(_validate), '%P')

# ---------- App ----------
root = tk.Tk()
root.title("EAN_window")
root.geometry("980x950")
root.resizable(False, False)

# ---------- Fonts ----------
FONT_MAIN = ("Arial", 16)   # data-entry area
FONT_SMALL = ("Arial", 12)  # summaries & counters

# ---------- Styles (green borders) ----------
style = ttk.Style()
style.theme_use("clam")

style.configure("Green.TEntry",
    font=FONT_MAIN, fieldbackground="white",
    bordercolor="green", lightcolor="green", darkcolor="green",
    borderwidth=2, relief="solid"
)
style.configure("Green.TCombobox",
    font=FONT_MAIN, fieldbackground="white",
    bordercolor="green", lightcolor="green", darkcolor="green",
    borderwidth=2, relief="solid"
)
style.configure("GreenSmall.TEntry",
    font=FONT_SMALL, fieldbackground="white",
    bordercolor="green", lightcolor="green", darkcolor="green",
    borderwidth=2, relief="solid"
)
style.configure("TButton", font=FONT_MAIN)
style.configure("TLabel",  font=FONT_MAIN)

# ---------- Top-left EAN panel ----------
ean_panel = tk.Frame(root, width=420, height=50, relief="groove", borderwidth=2)
ean_panel.place(x=0, y=0)

tk.Label(ean_panel, text="EAN_window", font=FONT_MAIN).place(x=6, y=10)

ean_var = tk.StringVar()
vcmd_ean, fmt = make_numeric_limiter(root, 19)
ean_entry = ttk.Entry(ean_panel, textvariable=ean_var,
                      validate="key", validatecommand=(vcmd_ean, fmt),
                      width=22, style="Green.TEntry")
ean_entry.place(x=210, y=10)

# ---------- Slice rules ----------
slice_rules = {
    "TRUPCI":  slice(0, 5),
    "PAKETI":  slice(10, 12),
    "LISTOVA": slice(12, 14),
    "DUZINA":  slice(14, 17),
    "SIRINA":  slice(17, 19),
}

# ---------- Field definitions ----------
fields = [
    ("BROJ TRUPCA", 5, "TRUPCI"),
    ("BROJ PAKETA", 2, "PAKETI"),
    ("BROJ LISTOVA", 2, "LISTOVA"),
    ("DUŽINA", 3, "DUZINA"),
    ("ŠIRINA", 2, "SIRINA"),
    ("KVADRATURA", 10, None),
    ("BROJ PALETE", 2, None),
]

# ---------- Main form ----------
form = ttk.Frame(root, padding=12)
form.place(x=40, y=80)

entry_vars, entry_widgets, auto_targets = {}, {}, []

for r, (label_text, max_len, key) in enumerate(fields):
    ttk.Label(form, text=label_text + ":").grid(row=r, column=0, sticky="e", padx=(0, 20), pady=8)
    var = tk.StringVar()
    vcmd, fmt = make_numeric_limiter(root, max_len)
    ent = ttk.Entry(form, textvariable=var, validate="key", validatecommand=(vcmd, fmt),
                    width=max(6, max_len + 2), style="Green.TEntry")
    ent.grid(row=r, column=1, sticky="w", pady=8)
    entry_vars[label_text] = var
    entry_widgets[label_text] = ent
    if key:
        s = slice_rules.get(key)
        if s:
            ent.config(state="readonly")
            auto_targets.append((ent, var, s))

# ---------- KLASA (editable combobox) ----------
klasa_row = len(fields)
ttk.Label(form, text="KLASA:").grid(row=klasa_row, column=0, sticky="e", padx=(0, 20), pady=15)
klasa_var = tk.StringVar()
klasa_combo = ttk.Combobox(form, textvariable=klasa_var,
                           values=("A", "B", "AB", "EXTRA"),
                           state="normal", width=10, style="Green.TCombobox")
klasa_combo.grid(row=klasa_row, column=1, sticky="w", pady=15)
entry_vars["KLASA"] = klasa_var
entry_widgets["KLASA"] = klasa_combo

# ---------- Spacer after KLASA ----------
ttk.Label(form, text="", font=FONT_MAIN).grid(row=klasa_row + 1, column=0, pady=10)

# ---------- Sum rows (small font) ----------
def make_sum_row(row, label):
    ttk.Label(form, text=label, font=FONT_SMALL)\
       .grid(row=row, column=0, sticky="e", padx=(0, 20), pady=4)
    var = tk.StringVar(value="0,00")
    ent = ttk.Entry(form, textvariable=var, state="readonly", width=15, style="GreenSmall.TEntry")
    ent.grid(row=row, column=1, sticky="w", pady=4)
    return var

sum_a_row     = klasa_row + 2
sum_b_row     = klasa_row + 3
sum_ab_row    = klasa_row + 4
sum_extra_row = klasa_row + 5
sum_total_row = klasa_row + 6

sum_a_var     = make_sum_row(sum_a_row,     "SUMA KVADRATURE (KLASA A):")
sum_b_var     = make_sum_row(sum_b_row,     "SUMA KVADRATURE (KLASA B):")
sum_ab_var    = make_sum_row(sum_ab_row,    "SUMA KVADRATURE (KLASA AB):")
sum_extra_var = make_sum_row(sum_extra_row, "SUMA KVADRATURE (KLASA EXTRA):")
sum_total_var = make_sum_row(sum_total_row, "UKUPNO KVADRATURE (A+B+AB+EXTRA):")

# ---------- Spacer BEFORE BROJ PAKETA KLASA A (requested) ----------
ttk.Label(form, text="", font=FONT_SMALL).grid(row=sum_total_row + 1, column=0, pady=10)

# ---------- Count rows (small font) ----------
def make_count_row(row, label):
    ttk.Label(form, text=label, font=FONT_SMALL)\
       .grid(row=row, column=0, sticky="e", padx=(0, 20), pady=6)
    var = tk.StringVar(value="0")
    ent = ttk.Entry(form, textvariable=var, state="readonly", width=15, style="GreenSmall.TEntry")
    ent.grid(row=row, column=1, sticky="w", pady=6)
    return var

count_a_row   = sum_total_row + 2
count_b_row   = sum_total_row + 3
count_ab_row  = sum_total_row + 4
count_ex_row  = sum_total_row + 5

count_a_var   = make_count_row(count_a_row,  "BROJ PAKETA KLASA A:")
count_b_var   = make_count_row(count_b_row,  "BROJ PAKETA KLASA B:")
count_ab_var  = make_count_row(count_ab_row, "BROJ PAKETA KLASA AB:")
count_ex_var  = make_count_row(count_ex_row, "BROJ PAKETA KLASA EXTRA:")

# ---------- Helpers ----------
def safe_int(v):
    try: return int(v)
    except ValueError: return 0

def update_kvadratura(*_):
    duzina = safe_int(entry_vars["DUŽINA"].get())
    sirina = safe_int(entry_vars["ŠIRINA"].get())
    listova = safe_int(entry_vars["BROJ LISTOVA"].get())
    kv_str = ""
    if duzina and sirina and listova:
        kv = (duzina * sirina * listova) / 10000
        kv_str = f"{kv:.2f}".replace('.', ',')
    ent = entry_widgets["KVADRATURA"]
    was_ro = (ent.cget("state") == "readonly")
    ent.config(state="normal"); entry_vars["KVADRATURA"].set(kv_str); 
    if was_ro: ent.config(state="readonly")

for dep in ["DUŽINA", "ŠIRINA", "BROJ LISTOVA"]:
    entry_vars[dep].trace_add("write", update_kvadratura)

def update_from_ean(*_):
    ean = ean_var.get()
    for ent, var, s in auto_targets:
        ent.config(state="normal"); var.set(ean[s]); ent.config(state="readonly")
    update_kvadratura()
    if len(ean) == 19:
        root.after(100, lambda: entry_widgets["BROJ PALETE"].focus_set())

ean_var.trace_add("write", update_from_ean)
entry_widgets["KVADRATURA"].config(state="readonly")

def read_sum_from_file(filename):
    total = 0.0
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.rstrip("\n").split("\t")
                if len(parts) >= 6:
                    try: total += float(parts[5].replace(',', '.'))
                    except ValueError: pass
    return total

def count_lines(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return sum(1 for _ in f)
    return 0

def update_all_summaries_and_counts():
    total_a     = read_sum_from_file("popis_klasa_a.txt")
    total_b     = read_sum_from_file("popis_klasa_b.txt")
    total_ab    = read_sum_from_file("popis_klasa_ab.txt")
    total_extra = read_sum_from_file("popis_klasa_extra.txt")

    sum_a_var.set(f"{total_a:.2f}".replace('.', ','))
    sum_b_var.set(f"{total_b:.2f}".replace('.', ','))
    sum_ab_var.set(f"{total_ab:.2f}".replace('.', ','))
    sum_extra_var.set(f"{total_extra:.2f}".replace('.', ','))
    sum_total_var.set(f"{(total_a+total_b+total_ab+total_extra):.2f}".replace('.', ','))

    count_a_var.set(str(count_lines("popis_klasa_a.txt")))
    count_b_var.set(str(count_lines("popis_klasa_b.txt")))
    count_ab_var.set(str(count_lines("popis_klasa_ab.txt")))
    count_ex_var.set(str(count_lines("popis_klasa_extra.txt")))

# ---------- Save ----------
def save_to_file(event=None):
    data = [
        entry_vars["BROJ TRUPCA"].get(),
        entry_vars["DUŽINA"].get(),
        entry_vars["ŠIRINA"].get(),
        entry_vars["BROJ PAKETA"].get(),
        entry_vars["BROJ LISTOVA"].get(),
        entry_vars["KVADRATURA"].get(),
        entry_vars["KLASA"].get(),
        entry_vars["BROJ PALETE"].get(),
    ]
    data = [v.replace('.', ',') for v in data]
    line = "\t".join(data) + "\n"

    with open("popis.txt", "a", encoding="utf-8") as f: f.write(line)

    klasa = entry_vars["KLASA"].get().strip().upper()
    if klasa in ["A", "B", "AB", "EXTRA"]:
        with open(f"popis_klasa_{klasa.lower()}.txt", "a", encoding="utf-8") as f:
            f.write(line)

    update_all_summaries_and_counts()

    # reset for next entry
    ean_var.set(""); klasa_var.set("")
    entry_widgets["KVADRATURA"].config(state="normal"); entry_vars["KVADRATURA"].set(""); entry_widgets["KVADRATURA"].config(state="readonly")
    entry_widgets["BROJ PALETE"].delete(0, tk.END)
    ean_entry.focus_set()

# ---------- Key bindings ----------
def focus_klasa(event=None):
    entry_widgets["KLASA"].focus_set()
    return "break"

entry_widgets["BROJ PALETE"].bind("<Return>", focus_klasa)
entry_widgets["KLASA"].bind("<Return>", save_to_file)

# ---------- EXIT ----------
def exit_app():
    root.destroy()

ttk.Button(root, text="EXIT", command=exit_app).place(relx=1.0, rely=1.0, x=-20, y=-20, anchor="se")

# ---------- Init ----------
update_all_summaries_and_counts()
root.mainloop()
