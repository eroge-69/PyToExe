#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplicație standalone pentru monitorizarea tensiunii arteriale și pulsului.
- Introducere măsurători (Data, Ora, Sistolică, Diastolică, Puls repaus)
- Grafic live care se actualizează la fiecare adăugare/ștergere
- Filtrare pe perioade: 1, 3, 7, 30 zile (și Toate)
- Calcule Max/Min în funcție de perioada selectată
- Export Excel / PDF și tipărire PDF (Windows)
- Datele sunt salvate în masuratori.csv (în același folder cu aplicația)

Dependințe: pandas, matplotlib, reportlab, openpyxl
Pentru .exe: PyInstaller
"""
import os
import sys
import platform
import tempfile
import datetime as dt
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # pentru randare offscreen a figurilor
import matplotlib.pyplot as plt

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
except Exception as e:
    print("Tkinter este necesar pentru UI:", e)
    sys.exit(1)

# Pentru tipărire pe Windows
def windows_print(filepath):
    if platform.system().lower() == "windows":
        try:
            os.startfile(filepath, "print")  # tipărire cu aplicația asociată PDF-urilor
            return True
        except Exception as e:
            messagebox.showerror("Eroare tipărire", f"Nu am putut trimite la imprimantă.\n{e}")
            return False
    else:
        messagebox.showinfo("Tipărire", "Tipărirea directă este disponibilă doar pe Windows prin această aplicație.\n"
                             "Pe alte sisteme, deschide PDF-ul exportat și tipărește-l.")
        return False

APP_NAME = "Monitor Tensiune"
CSV_FILE = "masuratori.csv"

PERIOADE = ["Toate", "1 zi", "3 zile", "7 zile", "30 zile"]

COLS = ["Data", "Ora", "Tensiune Sistolică", "Tensiune Diastolică", "Puls Repaus"]

def load_data():
    if os.path.exists(CSV_FILE):
        try:
            df = pd.read_csv(CSV_FILE, encoding="utf-8", sep=",")
        except UnicodeDecodeError:
            df = pd.read_csv(CSV_FILE, encoding="latin-1", sep=",")
        # Normalizăm coloane lipsă/ordine
        for c in COLS:
            if c not in df.columns:
                df[c] = ""
        df = df[COLS]
    else:
        df = pd.DataFrame(columns=COLS)
    return df

def save_data(df):
    df.to_csv(CSV_FILE, index=False, encoding="utf-8")

def parse_dt(row):
    # Combina Data (YYYY-MM-DD sau DD.MM.YYYY) cu Ora (HH:MM)
    d_raw = str(row.get("Data", "")).strip()
    t_raw = str(row.get("Ora", "")).strip()
    dt_val = None
    fmts = ["%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y"]
    for f in fmts:
        try:
            d = dt.datetime.strptime(d_raw, f).date()
            break
        except:
            d = None
    if d is None:
        return None
    if t_raw:
        for tf in ["%H:%M", "%H:%M:%S"]:
            try:
                tm = dt.datetime.strptime(t_raw, tf).time()
                dt_val = dt.datetime.combine(d, tm)
                break
            except:
                continue
    if dt_val is None:
        dt_val = dt.datetime.combine(d, dt.time(0, 0))
    return dt_val

def filter_by_period(df, perioada):
    if perioada == "Toate" or df.empty:
        return df.copy()
    days = int(perioada.split()[0])  # "1 zi" -> 1, "30 zile" -> 30
    now = dt.datetime.now()
    cutoff = now - dt.timedelta(days=days)
    # Calculăm o coloană temporară cu datetime
    tmp = df.copy()
    tmp["_dt"] = tmp.apply(parse_dt, axis=1)
    tmp = tmp.dropna(subset=["_dt"])
    return tmp[tmp["_dt"] >= cutoff].drop(columns=["_dt"])

def compute_stats(df):
    # Returnează dict cu max/min pentru coloanele numerice
    out = {}
    numeric_cols = ["Tensiune Sistolică", "Tensiune Diastolică", "Puls Repaus"]
    for c in numeric_cols:
        try:
            s = pd.to_numeric(df[c], errors="coerce")
            out[c] = {"max": None if s.dropna().empty else float(s.max()),
                      "min": None if s.dropna().empty else float(s.min())}
        except Exception:
            out[c] = {"max": None, "min": None}
    return out

def draw_plot(df, filepath_png):
    plt.close("all")
    if df.empty:
        # desenăm o figură goală cu mesaj
        fig = plt.figure(figsize=(8, 4.2))
        plt.title("Grafic măsurători (nu există date)")
        plt.xlabel("Măsurători (ordine)")
        plt.ylabel("Valoare")
        fig.tight_layout()
        fig.savefig(filepath_png, dpi=150)
        plt.close(fig)
        return

    # Pregătim seriile (în ordinea cronologică după Data+Ora)
    tmp = df.copy()
    tmp["_dt"] = tmp.apply(parse_dt, axis=1)
    tmp = tmp.sort_values(by="_dt", kind="stable")
    # Dacă nu există datetime valid, folosim index
    x = range(len(tmp))

    fig = plt.figure(figsize=(8, 4.2))
    try:
        ys = pd.to_numeric(tmp["Tensiune Sistolică"], errors="coerce")
        yd = pd.to_numeric(tmp["Tensiune Diastolică"], errors="coerce")
        yp = pd.to_numeric(tmp["Puls Repaus"], errors="coerce")
        plt.plot(x, ys, label="Sistolică")
        plt.plot(x, yd, label="Diastolică")
        plt.plot(x, yp, label="Puls")
        plt.legend()
        plt.title("Evoluția tensiunii și pulsului")
        plt.xlabel("Măsurători (ordine cronologică)")
        plt.ylabel("Valoare")
    except Exception:
        pass
    fig.tight_layout()
    fig.savefig(filepath_png, dpi=150)
    plt.close(fig)

def export_excel(df_all, save_path):
    # Creează un Excel cu datele (toate și filtrate) și un sheet cu statistici pentru 1,3,7,30 zile
    with pd.ExcelWriter(save_path, engine="openpyxl") as writer:
        df_all.to_excel(writer, sheet_name="Masuratori", index=False)

        # Statistici pentru perioade
        perioade = ["1 zi", "3 zile", "7 zile", "30 zile"]
        rows = []
        for p in perioade:
            dff = filter_by_period(df_all, p)
            st = compute_stats(dff)
            rows.append([
                p,
                st["Tensiune Sistolică"]["max"], st["Tensiune Sistolică"]["min"],
                st["Tensiune Diastolică"]["max"], st["Tensiune Diastolică"]["min"],
                st["Puls Repaus"]["max"], st["Puls Repaus"]["min"],
            ])
        df_stats = pd.DataFrame(rows, columns=[
            "Perioadă", "Max Sistolică", "Min Sistolică", "Max Diastolică", "Min Diastolică", "Max Puls", "Min Puls"
        ])
        df_stats.to_excel(writer, sheet_name="Statistici", index=False)

def export_pdf(df_filtered, save_path):
    # Exportă PDF care conține graficul curent + un tabel cu datele filtrate
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import cm
    from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer, Image
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet

    # Salvăm temporar graficul curent ca PNG
    import tempfile
    tmp_png = os.path.join(tempfile.gettempdir(), "graf_tensiune.png")
    draw_plot(df_filtered, tmp_png)

    doc = SimpleDocTemplate(save_path, pagesize=landscape(A4), leftMargin=1*cm, rightMargin=1*cm, topMargin=1*cm, bottomMargin=1*cm)
    styles = getSampleStyleSheet()
    elems = []

    elems.append(Paragraph("Evoluția tensiunii și pulsului", styles["Title"]))
    elems.append(Spacer(1, 0.4*cm))
    elems.append(Image(tmp_png, width=24*cm, height=10*cm))
    elems.append(Spacer(1, 0.5*cm))

    # Tabel cu date
    data = [COLS] + df_filtered[COLS].astype(str).values.tolist()
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("ALIGN", (2,1), (-1,-1), "CENTER"),
    ]))
    elems.append(table)

    doc.build(elems)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("1100x650")
        self.minsize(1000, 600)

        self.df = load_data()
        self.filtered = self.df.copy()
        self.last_export_pdf = None

        self.create_widgets()
        self.refresh_view()

    def create_widgets(self):
        # Cadru de input
        frm_in = ttk.LabelFrame(self, text="Adaugă măsurătoare")
        frm_in.pack(fill="x", padx=10, pady=8)

        ttk.Label(frm_in, text="Data (YYYY-MM-DD sau DD.MM.YYYY):").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.var_data = tk.StringVar()
        ttk.Entry(frm_in, textvariable=self.var_data, width=20).grid(row=0, column=1, sticky="w", padx=6, pady=4)

        ttk.Label(frm_in, text="Ora (HH:MM):").grid(row=0, column=2, sticky="w", padx=6, pady=4)
        self.var_ora = tk.StringVar()
        ttk.Entry(frm_in, textvariable=self.var_ora, width=12).grid(row=0, column=3, sticky="w", padx=6, pady=4)

        ttk.Label(frm_in, text="Sistolică:").grid(row=1, column=0, sticky="w", padx=6, pady=4)
        self.var_sys = tk.StringVar()
        ttk.Entry(frm_in, textvariable=self.var_sys, width=10).grid(row=1, column=1, sticky="w", padx=6, pady=4)

        ttk.Label(frm_in, text="Diastolică:").grid(row=1, column=2, sticky="w", padx=6, pady=4)
        self.var_dia = tk.StringVar()
        ttk.Entry(frm_in, textvariable=self.var_dia, width=10).grid(row=1, column=3, sticky="w", padx=6, pady=4)

        ttk.Label(frm_in, text="Puls repaus:").grid(row=1, column=4, sticky="w", padx=6, pady=4)
        self.var_pulse = tk.StringVar()
        ttk.Entry(frm_in, textvariable=self.var_pulse, width=10).grid(row=1, column=5, sticky="w", padx=6, pady=4)

        ttk.Button(frm_in, text="Adaugă", command=self.add_row).grid(row=0, column=6, rowspan=2, padx=10, pady=4, sticky="ns")

        # Filtrare perioadă
        frm_filter = ttk.LabelFrame(self, text="Filtru perioadă")
        frm_filter.pack(fill="x", padx=10, pady=4)

        ttk.Label(frm_filter, text="Perioadă:").grid(row=0, column=0, padx=6, pady=6, sticky="w")
        self.var_period = tk.StringVar(value=PERIOADE[0])
        self.cmb_period = ttk.Combobox(frm_filter, textvariable=self.var_period, values=PERIOADE, state="readonly", width=12)
        self.cmb_period.grid(row=0, column=1, padx=6, pady=6, sticky="w")
        self.cmb_period.bind("<<ComboboxSelected>>", lambda e: self.refresh_view())

        # Statistici (max/min)
        self.lbl_stats = ttk.Label(frm_filter, text="Max/Min (—)")
        self.lbl_stats.grid(row=0, column=2, padx=20, pady=6, sticky="w")

        # Tabel date
        frm_tbl = ttk.Frame(self)
        frm_tbl.pack(fill="both", expand=True, padx=10, pady=6)

        columns = COLS
        self.tree = ttk.Treeview(frm_tbl, columns=columns, show="headings", selectmode="browse")
        for c in columns:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=120, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True)

        vsb = ttk.Scrollbar(frm_tbl, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")

        # Butoane acțiuni
        frm_actions = ttk.Frame(self)
        frm_actions.pack(fill="x", padx=10, pady=6)

        ttk.Button(frm_actions, text="Șterge selecția", command=self.delete_selected).pack(side="left", padx=4)
        ttk.Button(frm_actions, text="Export Excel", command=self.on_export_excel).pack(side="left", padx=4)
        ttk.Button(frm_actions, text="Export PDF", command=self.on_export_pdf).pack(side="left", padx=4)
        ttk.Button(frm_actions, text="Tipărește PDF", command=self.on_print_pdf).pack(side="left", padx=4)

        # Canvas grafic (imagine randată din matplotlib)
        frm_plot = ttk.LabelFrame(self, text="Grafic")
        frm_plot.pack(fill="x", padx=10, pady=6)

        self.plot_label = ttk.Label(frm_plot)
        self.plot_label.pack(fill="both", expand=True)

        # Notă
        ttk.Label(self, text="Datele sunt salvate automat în masuratori.csv în folderul aplicației.").pack(padx=10, pady=4, anchor="w")

        # Update imagine grafic inițial
        self.update_plot_image()

    def refresh_view(self):
        perioada = self.var_period.get()
        self.filtered = filter_by_period(self.df, perioada)
        # Tabel
        for i in self.tree.get_children():
            self.tree.delete(i)
        for _, row in self.filtered.iterrows():
            self.tree.insert("", "end", values=[row.get(c, "") for c in COLS])
        # Statistici
        st = compute_stats(self.filtered)
        txt = (f"Sistolică: max={st['Tensiune Sistolică']['max']}  min={st['Tensiune Sistolică']['min']}   |   "
               f"Diastolică: max={st['Tensiune Diastolică']['max']}  min={st['Tensiune Diastolică']['min']}   |   "
               f"Puls: max={st['Puls Repaus']['max']}  min={st['Puls Repaus']['min']}")
        self.lbl_stats.config(text=txt)
        # Grafic
        self.update_plot_image()

    def update_plot_image(self):
        # Randăm graficul curent în PNG și îl afișăm în UI
        try:
            import tempfile
            tmp_png = os.path.join(tempfile.gettempdir(), "graf_tensiune_ui.png")
            draw_plot(self.filtered, tmp_png)
            # Încărcăm imaginea în Tkinter
            try:
                from PIL import Image, ImageTk
                img = Image.open(tmp_png)
                self.tk_img = ImageTk.PhotoImage(img)
                self.plot_label.configure(image=self.tk_img)
            except Exception:
                # Fără Pillow, afișăm doar un text
                self.plot_label.configure(text=f"Grafic generat: {tmp_png}")
        except Exception as e:
            self.plot_label.configure(text=f"Eroare generare grafic: {e}")

    def add_row(self):
        row = {
            "Data": self.var_data.get().strip(),
            "Ora": self.var_ora.get().strip(),
            "Tensiune Sistolică": self.var_sys.get().strip(),
            "Tensiune Diastolică": self.var_dia.get().strip(),
            "Puls Repaus": self.var_pulse.get().strip(),
        }
        # Validări simple
        if not row["Data"] or not row["Tensiune Sistolică"] or not row["Tensiune Diastolică"] or not row["Puls Repaus"]:
            messagebox.showwarning("Valori lipsă", "Te rog completează cel puțin Data și valorile numeric (Sistolică, Diastolică, Puls).")
            return
        # Încearcă conversia numerică
        for k in ["Tensiune Sistolică", "Tensiune Diastolică", "Puls Repaus"]:
            try:
                float(str(row[k]).replace(",", "."))
            except:
                messagebox.showwarning("Valoare invalidă", f"Valoare numerică invalidă pentru {k}.")
                return
        # Adăugăm
        self.df = pd.concat([self.df, pd.DataFrame([row])], ignore_index=True)
        save_data(self.df)
        # Clear inputs (păstrăm data/ora pentru comoditate)
        self.var_sys.set(""); self.var_dia.set(""); self.var_pulse.set("")
        self.refresh_view()

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        # Obținem valorile rândului selectat
        vals = self.tree.item(sel[0], "values")
        # Eliminăm primul rând din df care se potrivește exact (poate exista duplicat)
        mask = (self.df[COLS].astype(str) == pd.Series(vals, index=COLS).astype(str)).all(axis=1)
        idxs = list(self.df[mask].index)
        if idxs:
            self.df = self.df.drop(index=idxs[0]).reset_index(drop=True)
            save_data(self.df)
        self.refresh_view()

    def on_export_excel(self):
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")], title="Salvează Excel")
        if not path:
            return
        try:
            export_excel(self.df, path)
            messagebox.showinfo("Export Excel", f"Fișier Excel salvat:\n{path}")
        except Exception as e:
            messagebox.showerror("Eroare export", f"Nu am putut exporta în Excel.\n{e}")

    def on_export_pdf(self):
        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")], title="Salvează PDF")
        if not path:
            return
        try:
            export_pdf(self.filtered, path)
            self.last_export_pdf = path
            messagebox.showinfo("Export PDF", f"Fișier PDF salvat:\n{path}")
        except Exception as e:
            messagebox.showerror("Eroare export", f"Nu am putut exporta PDF.\n{e}")

    def on_print_pdf(self):
        if self.last_export_pdf and os.path.exists(self.last_export_pdf):
            windows_print(self.last_export_pdf)
        else:
            # dacă nu avem un PDF exportat, generăm rapid unul temporar din datele filtrate
            import tempfile
            tmp_pdf = os.path.join(tempfile.gettempdir(), "tensiune_print.pdf")
            try:
                export_pdf(self.filtered, tmp_pdf)
                self.last_export_pdf = tmp_pdf
                windows_print(tmp_pdf)
            except Exception as e:
                messagebox.showerror("Eroare tipărire", f"Nu am putut genera/trimite PDF la imprimantă.\n{e}")

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
