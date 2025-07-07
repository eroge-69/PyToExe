import tkinter as tk
from tkinter import ttk, messagebox
import json, os, re
from datetime import datetime
import pyodbc
import pandas as pd
from PIL import Image, ImageTk

# --- Konstanten ---
PROGRESS_JSON = "gtin_progress.json"
EXPORT_XLSX   = "gtin_nachbearb.xlsx"

# --- Theme & Farben ---
BG_COLOR     = "#282c34"
FG_COLOR     = "#f8f8f2"
ACCENT_TEAL  = "#2bc7bd"
ACCENT_RED   = "#ff5555"
ENTRY_BG     = "#3b3f4b"
PROG_BG      = "#44475a"

# --- Hilfsfunktionen ---
def bin_stamm(b):
    for i,c in enumerate(b):
        if not c.isdigit(): return b[:i]
    return b

def bin_suffix(b):
    s = b[len(bin_stamm(b)):]
    return s or None

def format_gtin(raw):
    nums = ''.join(filter(str.isdigit, raw or ""))
    return nums.zfill(14) if nums else None

def parse_date(d):
    try:
        return datetime.strptime(d, "%d.%m.%Y")
    except:
        return datetime(1900,1,1)

class GTINToolProd(tk.Tk):
    def __init__(self):
        super().__init__()

        # Styles direkt beim Start festlegen (auch für Login)
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TFrame',       background=BG_COLOR)
        style.configure('TLabel',       background=BG_COLOR, foreground=FG_COLOR, font=('Helvetica',11))
        style.configure('TCheckbutton', background=BG_COLOR, foreground=FG_COLOR, font=('Helvetica',11))
        style.configure('TButton',
                        background=ACCENT_RED,
                        foreground=FG_COLOR,
                        font=('Helvetica',11,'bold'))
        style.map('TButton', background=[('active','#ff6b6b')])
        style.configure('TEntry',
                        fieldbackground=ENTRY_BG,
                        background=ENTRY_BG,
                        foreground=FG_COLOR,
                        font=('Helvetica',11))
        style.configure('TProgressbar',
                        troughcolor=PROG_BG,
                        background=ACCENT_TEAL)

        # Logos laden
        self.logo_img      = self._load_image(
            "20250707_1039_Dunkelgrauer Hintergrunddesign_remix_01jzj0hq6bfhybkq7e6h7e4033.png",
            (300,100)
        )
        self.user_logo_img = self._load_image(
            "20250707_1002_Modernisiertes SHG-Logo_remix_01jzhydy02fxk9er7dp5abnwye.png",
            (400,150)
        )

        # Login
        self.withdraw()
        if not self._show_login():
            self.destroy()
            return

        # Splash (2 Sekunden, eigenes Logo größer)
        splash = tk.Toplevel(self)
        splash.configure(bg=BG_COLOR)
        if self.user_logo_img:
            lbl = tk.Label(splash, image=self.user_logo_img,
                           bg=BG_COLOR, takefocus=False)
            lbl.pack(expand=True, padx=20, pady=20)
        splash.update()
        self.after(2000, splash.destroy)

        # Hauptfenster konfigurieren
        self.title("AutoStore GTIN-Zuweisung – Live")
        self.configure(bg=BG_COLOR)
        self.minsize(800,600)
        for c in range(5): self.columnconfigure(c, weight=1)
        for r in range(6): self.rowconfigure(r, weight=1)

        # Stammdaten & Progress laden
        self.meta     = self._load_meta()
        self.eingaben = self._load_progress()

        # Live-Datenbank (nur lesen)
        self.conn_live = pyodbc.connect(self.auto_conn_str, timeout=5)
        self.loader    = lambda: self._build_live_list()

        self.idx = 0
        self.current_gtin = None

        self._build_widgets()
        self._load_articles()
        self.bind("<F9>", lambda e: self.manual_gtin.focus_set())
        self.deiconify()

    def _show_login(self):
        win = tk.Toplevel(self)
        win.title("Login")
        win.configure(bg=BG_COLOR)
        win.grab_set()

        frm = ttk.Frame(win, padding=10)
        frm.pack()

        # Nur Programm-Logo
        if self.logo_img:
            tk.Label(frm, image=self.logo_img,
                     bg=BG_COLOR,
                     takefocus=False).grid(row=0, column=0, columnspan=2, pady=(0,10))

        # Eingabefelder mit takefocus=True
        ttk.Label(frm, text="SD-User:").grid(row=1, column=0, sticky="e")
        sd_u = ttk.Entry(frm, takefocus=True)
        sd_u.grid(row=1, column=1); sd_u.insert(0,"Apolog")
        ttk.Label(frm, text="SD-PW:").grid(row=2, column=0, sticky="e")
        sd_p = ttk.Entry(frm, show="*", takefocus=True)
        sd_p.grid(row=2, column=1)
        ttk.Label(frm, text="AS-User:").grid(row=3, column=0, sticky="e")
        as_u = ttk.Entry(frm, takefocus=True)
        as_u.grid(row=3, column=1); as_u.insert(0,"sa")
        ttk.Label(frm, text="AS-PW:").grid(row=4, column=0, sticky="e")
        as_p = ttk.Entry(frm, show="*", takefocus=True)
        as_p.grid(row=4, column=1)

        def do_login():
            u1,p1,u2,p2 = sd_u.get(), sd_p.get(), as_u.get(), as_p.get()
            if not all([u1,p1,u2,p2]):
                messagebox.showerror("Fehler","Alle Felder ausfüllen!"); return
            self.stamm_conn_str = (
                "Driver={SQL Server};"
                "Server=172.26.80.44\\Amor;"
                "Database=Amor3;"
                f"UID={u1};PWD={p1}"
            )
            self.auto_conn_str = (
                "Driver={SQL Server};"
                "Server=172.26.80.44\\autostore;"
                "Database=apolog_mw;"
                f"UID={u2};PWD={p2}"
            )
            try:
                with pyodbc.connect(self.stamm_conn_str, timeout=5): pass
                with pyodbc.connect(self.auto_conn_str, timeout=5): pass
            except Exception as e:
                messagebox.showerror("Verbindungsfehler", f"Login fehlgeschlagen:\n{e}")
                return
            win.destroy()

        ttk.Button(frm, text="Login", command=do_login, takefocus=True)\
            .grid(row=5, column=0, columnspan=2, pady=10)

        win.wait_window()
        return hasattr(self, "stamm_conn_str")

    def _load_image(self, path, size):
        try:
            img = Image.open(path)
            img.thumbnail(size, Image.LANCZOS)
            return ImageTk.PhotoImage(img)
        except:
            return None

    def _load_progress(self):
        if os.path.exists(PROGRESS_JSON):
            with open(PROGRESS_JSON, "r", encoding="utf-8-sig") as f:
                return json.load(f)
        else:
            with open(PROGRESS_JSON, "w", encoding="utf-8") as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
            return {}

    def _save_progress(self):
        with open(PROGRESS_JSON, "w", encoding="utf-8") as f:
            json.dump(self.eingaben, f, ensure_ascii=False, indent=2)

    def _load_meta(self):
        meta = {}
        with pyodbc.connect(self.stamm_conn_str) as cs:
            cur = cs.cursor()
            cur.execute("SELECT DISTINCT S1000art_Artikelnummer, S1000art_Grundeinheit FROM dbo.IT4_Stamm")
            for art,ge in cur.fetchall():
                a = str(art).strip()
                meta.setdefault(a, {"packungen":[], "charge_flag":False, "verfall_flag":False})
                meta[a]["packungen"].append({"uni":ge, "factor":1.0, "gtins":[]})
            cur.execute("""
                SELECT
                  S1000art_Artikelnummer,
                  S6026alu_Verpackungsform,
                  S6026alu_Menge,
                  S6027bar_Barcode,
                  [consumption requires expiration date],
                  [consumption requires lot number]
                FROM dbo.IT4_Stamm
            """)
            for art,uni,fak,bc,exp,lot in cur.fetchall():
                a = str(art).strip()
                parts = re.split(r'[;,]', bc or "")
                gtins = [format_gtin(p) for p in parts if p.strip()]
                if lot:  meta[a]["charge_flag"] = True
                if exp:  meta[a]["verfall_flag"] = True
                key = (uni, float(fak))
                ex = next((p for p in meta[a]["packungen"] if (p["uni"],p["factor"])==key), None)
                if ex:
                    for g in gtins:
                        if g not in ex["gtins"]: ex["gtins"].append(g)
                else:
                    meta[a]["packungen"].append({
                        "uni": uni,
                        "factor": float(fak),
                        "gtins": gtins
                    })
        return meta

    def _build_live_list(self):
        cur = self.conn_live.cursor()
        cur.execute("""
            SELECT DISTINCT q.StorageBinId, q.MaterialId, l.Materialtext,
                             FORMAT(q.LastMovement,'dd.MM.yyyy')
            FROM quant q
            JOIN lvsBarcode l ON q.MaterialId = l.MaterialId
        """)
        rows = cur.fetchall()
        items = [{"bin":r[0],
                  "amor":str(r[1]).strip(),
                  "bezeichnung":r[2],
                  "last_movement":r[3] or "01.01.1900"}
                 for r in rows]
        items.sort(key=lambda x: (bin_stamm(x["bin"]),
                                  -parse_date(x["last_movement"]).timestamp(),
                                  x["bin"]))
        seen = set(); result=[]
        for it in items:
            if it["amor"] in seen: continue
            seen.add(it["amor"])
            info = self.meta.get(it["amor"], {"packungen":[], "charge_flag":False, "verfall_flag":False})
            it.update(info); result.append(it)
        return result

    def _build_widgets(self):
        # Header mit beiden Logos & Uhr
        hdr = ttk.Frame(self, padding=5)
        hdr.grid(row=0, column=0, columnspan=5, sticky="ew", pady=(5,0))
        hdr.columnconfigure((0,1,2), weight=1)
        if self.logo_img:
            tk.Label(hdr, image=self.logo_img,
                     bg=BG_COLOR, takefocus=False)\
                .grid(row=0, column=0, sticky="w", padx=10)
        if self.user_logo_img:
            tk.Label(hdr, image=self.user_logo_img,
                     bg=BG_COLOR, takefocus=False)\
                .grid(row=0, column=1, sticky="e", padx=10)
        self.clock_lbl = ttk.Label(hdr, font=('Helvetica',10), foreground=FG_COLOR)
        self.clock_lbl.grid(row=0, column=2, sticky="e", padx=10)
        self._update_clock()

        # Accent-Stripe
        self.stripe = tk.Canvas(self, height=4, bg=BG_COLOR, highlightthickness=0)
        self.stripe.grid(row=1, column=0, columnspan=5, sticky="ew")
        self.stripe_bar_length = 100; self.stripe_pos = 0
        self.stripe_rect = self.stripe.create_rectangle(
            -self.stripe_bar_length, 0, 0, 4, fill=ACCENT_TEAL, outline=""
        )
        self._animate_stripe()

        # Status & nächste Bins
        sf = ttk.Frame(self, padding=(10,5))
        sf.grid(row=2, column=0, columnspan=5, sticky="ew", padx=15)
        sf.columnconfigure(1, weight=1)
        self.lbl_status = ttk.Label(sf, text="Artikel 0 von 0", font=('Helvetica',10,'bold'))
        self.lbl_status.grid(row=0, column=0, sticky="w")
        self.lbl_next   = ttk.Label(sf, text="Nächste Bins:", font=('Helvetica',10,'italic'))
        self.lbl_next.grid(row=0, column=1, sticky="w")
        self.progress   = ttk.Progressbar(sf)
        self.progress.grid(row=0, column=4, sticky="ew", padx=10)

        # Artikel-Info
        info = ttk.Frame(self, padding=15)
        info.grid(row=3, column=0, columnspan=5, sticky="ew", padx=15)
        info.columnconfigure(1, weight=1)
        self.info_vars = {}
        labels = ["Artikelnummer:","Bezeichnung:","Bin:","Letzte Bewegung:"]
        for i,lab in enumerate(labels):
            ttk.Label(info, text=lab).grid(row=i, column=0, sticky="e", pady=4)
            lbl = ttk.Label(info, text="", wraplength=(600 if i==1 else None))
            lbl.grid(row=i, column=1, sticky="w", pady=4)
            self.info_vars[lab] = lbl
        # ABCD-Indikator jetzt 60×60
        self.ind_canvas = tk.Canvas(info, width=60, height=60,
                                    bg=BG_COLOR, highlightthickness=0)
        self.ind_canvas.grid(row=3, column=2, sticky="w", padx=5)

        # Packungen, Flags & Notizen
        pf = ttk.Frame(self, padding=15, relief="groove")
        pf.grid(row=4, column=0, columnspan=5,
                sticky="ew", padx=15, pady=10)
        pf.columnconfigure(1, weight=1)
        self.charge_var  = tk.BooleanVar()
        self.verfall_var = tk.BooleanVar()
        ttk.Checkbutton(pf, text="Charge notwendig", variable=self.charge_var).grid(row=0, column=0, sticky="w", pady=4)
        self.charge_ind  = ttk.Label(pf, text="✓", foreground=ACCENT_TEAL)
        self.charge_ind.grid(row=0, column=4, sticky="w")
        ttk.Checkbutton(pf, text="Verfall notwendig", variable=self.verfall_var).grid(row=1, column=0, sticky="w", pady=4)
        self.verfall_ind = ttk.Label(pf, text="✓", foreground=ACCENT_TEAL)
        self.verfall_ind.grid(row=1, column=4, sticky="w")
        ttk.Label(pf, text="Notizen:").grid(row=2, column=0, sticky="nw", pady=(10,4))
        self.notiz_txt = tk.Text(pf, height=3, bg=ENTRY_BG, fg=FG_COLOR)
        self.notiz_txt.grid(row=2, column=1, columnspan=4, sticky="ew", pady=(10,4))
        self.pf = pf

        # Buttons & manueller GTIN
        bf = ttk.Frame(self, padding=15)
        bf.grid(row=5, column=0, columnspan=5, sticky="ew", padx=15, pady=10)
        for i in range(5): bf.columnconfigure(i, weight=1)
        ttk.Button(bf, text="Speichern & Weiter",
                   command=self._save_next, takefocus=True)\
            .grid(row=0, column=0, sticky="ew", padx=5)
        ttk.Button(bf, text="Export Excel",
                   command=self._export, takefocus=True)\
            .grid(row=0, column=1, sticky="ew", padx=5)
        ttk.Label(bf, text="GTIN (manuell):").grid(row=1, column=0, sticky="e", pady=(10,4))
        self.manual_gtin = ttk.Entry(bf, takefocus=True)
        self.manual_gtin.grid(row=1, column=1, columnspan=2, sticky="ew", pady=(10,4))
        self.manual_gtin.bind("<FocusIn>", lambda e: e.widget.select_range(0,'end'))
        self.manual_gtin.bind("<Return>", lambda e: self._process_gtin(self.manual_gtin.get()))
        ttk.Button(bf, text="Prüfen",
                   command=lambda: self._process_gtin(self.manual_gtin.get()),
                   takefocus=True)\
            .grid(row=1, column=4, sticky="ew", pady=(10,4))

    def _update_clock(self):
        now = datetime.now().strftime("%H:%M:%S")
        self.clock_lbl.config(text=now)
        self.after(500, self._update_clock)

    def _animate_stripe(self):
        w = self.stripe.winfo_width() or self.winfo_width()
        self.stripe_pos = (self.stripe_pos + 5) % (w + self.stripe_bar_length)
        x1 = self.stripe_pos - self.stripe_bar_length
        x2 = self.stripe_pos
        self.stripe.coords(self.stripe_rect, x1, 0, x2, 4)
        self.after(30, self._animate_stripe)

    def _draw_abcd(self, suf):
        c = self.ind_canvas; c.delete("all"); s=60
        cols = {k:"#4b4b4b" for k in "ABCD"}
        if suf in cols: cols[suf] = ACCENT_TEAL
        c.create_polygon(0,0, s/2,0, 0,s/2, fill=cols["A"], outline="")
        c.create_polygon(s,0, s,s/2, s/2,0, fill=cols["B"], outline="")
        c.create_polygon(0,s, s/2,s, 0,s/2, fill=cols["C"], outline="")
        c.create_polygon(s,s, s/2,s, s,s/2, fill=cols["D"], outline="")
        pos={"A":(s*0.25,s*0.25),"B":(s*0.75,s*0.25),"C":(s*0.25,s*0.75),"D":(s*0.75,s*0.75)}
        for k,(x,y) in pos.items():
            c.create_text(x,y, text=k, font=('Helvetica',14,'bold'), fill=FG_COLOR)

    def _load_articles(self):
        arts = self.loader()
        self.rest = [a for a in arts if a["amor"] not in self.eingaben]
        self.idx = 0
        if not self.rest:
            messagebox.showinfo("Ende","Alle Artikel erledigt")
            self._export()
            self.quit()
        else:
            self._show_article()

    def _show_article(self):
        art = self.rest[self.idx]
        self.charge_var.set(art["charge_flag"])
        self.charge_ind.config(text="✓" if art["charge_flag"] else "")
        self.verfall_var.set(art["verfall_flag"])
        self.verfall_ind.config(text="✓" if art["verfall_flag"] else "")

        self.lbl_status.config(text=f"Artikel {self.idx+1} von {len(self.rest)}")
        self.progress.config(maximum=len(self.rest), value=self.idx+1)
        nxt = [bin_stamm(a["bin"]) for a in self.rest[self.idx+1:self.idx+6]]
        self.lbl_next.config(text="Nächste Bins: " + " | ".join(nxt))

        self.info_vars["Artikelnummer:"].config(text=art["amor"])
        self.info_vars["Bezeichnung:"].config(text=art["bezeichnung"])
        self.info_vars["Bin:"].config(text=bin_stamm(art["bin"]), foreground=ACCENT_TEAL)
        self.info_vars["Letzte Bewegung:"].config(text=art["last_movement"])
        self._draw_abcd(bin_suffix(art["bin"]))

        self.notiz_txt.delete("1.0", tk.END)
        self.manual_gtin.delete(0, tk.END)
        self.current_gtin = None

        for w in self.pf.grid_slaves():
            if int(w.grid_info()["row"]) > 3:
                w.destroy()

        for i,p in enumerate(art["packungen"], start=4):
            ttk.Label(self.pf, text=f"{p['uni']} (x{p['factor']})").grid(row=i, column=0, sticky="w", pady=4)
            m = tk.Label(self.pf, width=3,
                         bg=(ACCENT_TEAL if p["gtins"] else "#4b4b4b"))
            m.grid(row=i, column=1, pady=4)
            s = tk.Label(self.pf, width=3, bg="#4b4b4b")
            s.grid(row=i, column=2, pady=4)
            btn = ttk.Button(self.pf, text="Zuordnen", takefocus=True,
                             command=lambda u=p['uni']: self._assign(u))
            btn.grid(row=i, column=3, padx=5)
            f = tk.Frame(self.pf, bg=BG_COLOR)
            f.grid(row=i, column=4, pady=4, sticky="w")
            p["_widget"] = {"meta":m, "scan":s, "btn":btn, "frame":f}

        self.manual_gtin.focus_set()

    def _process_gtin(self, raw):
        self.current_gtin = raw.strip() or None
        if not raw.strip(): return
        g14 = format_gtin(raw)
        g13 = raw if len(raw)==13 else None
        art = self.rest[self.idx]
        for p in art["packungen"]:
            ok = any(g in (g14, g13) for g in p["gtins"])
            p["_widget"]["scan"].config(bg=(ACCENT_TEAL if ok else "#4b4b4b"))

    def _assign(self, uni):
        art = self.rest[self.idx]
        factor = next((p["factor"] for p in art["packungen"] if p["uni"]==uni), None) if uni else None
        entry = {
            "gtin":     self.current_gtin or "",
            "zuordnen": uni,
            "factor":   factor,
            "charge":   self.charge_var.get(),
            "verfall":  self.verfall_var.get(),
            "löschen":  [p["uni"] for p in art["packungen"] if p["uni"]!=uni],
            "notiz":    self.notiz_txt.get("1.0", tk.END).strip(),
            "orig_charge": art["charge_flag"],
            "orig_verfall": art["verfall_flag"]
        }
        self.eingaben.setdefault(art["amor"], []).append(entry)
        self._save_progress()
        if uni:
            f = next(p["_widget"]["frame"] for p in art["packungen"] if p["uni"]==uni)
            tk.Frame(f, bg=ACCENT_TEAL, width=12, height=4).pack(side="left", padx=1)

    def _save_next(self):
        art = self.rest[self.idx]
        if art["amor"] not in self.eingaben:
            self._assign(None)
        if self.idx + 1 < len(self.rest):
            self.idx += 1
            self._show_article()
        else:
            messagebox.showinfo("Ende","Alle Artikel erledigt")
            self._export()
            self.quit()

    def _export(self):
        recs = []
        for art, ents in self.eingaben.items():
            for v in ents:
                changed = (
                    bool(v["zuordnen"]) or
                    v["notiz"] or
                    v["charge"] != v["orig_charge"] or
                    v["verfall"]!= v["orig_verfall"]
                )
                if not changed: continue
                recs.append({
                    "amor":     art,
                    "zuordnen": v["zuordnen"] or "",
                    "factor":   v["factor"] or "",
                    "gtin":     v["gtin"] or "",
                    "charge":   "Ja" if v["charge"] else "Nein",
                    "verfall":  "Ja" if v["verfall"] else "Nein",
                    "löschen":  ";".join(v["löschen"]),
                    "notiz":    v["notiz"]
                })
        df = pd.DataFrame.from_records(recs, columns=[
            "amor","zuordnen","factor","gtin","charge","verfall","löschen","notiz"
        ])
        df.to_excel(EXPORT_XLSX, index=False)
        messagebox.showinfo("Export", f"{EXPORT_XLSX} erstellt")

if __name__ == "__main__":
    GTINToolProd().mainloop()
