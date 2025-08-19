
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sqlite3
from datetime import datetime, date
import re
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

DB_PATH = "kalite_takip.db"

class KaliteTakipSistemi:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Kalite Takip Sistemi")
        self.root.geometry("1100x720")
        self.root.configure(bg="white")

        # Renk şeması (turuncu/beyaz düz tasarım)
        self.colors = {
            "bg": "#FFFFFF",
            "primary": "#FF8C00",
            "success": "#27AE60",
            "danger": "#E74C3C",
            "text": "#2C3E50",
            "light_gray": "#F8F8F8",
            "border": "#D5D5D5"
        }

        self.init_db()
        self.show_main_menu()

    # ---------------- DB ----------------
    def init_db(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.execute("PRAGMA foreign_keys = ON;")
        cur = self.conn.cursor()

        # CMM ölçüm tablosu
        cur.execute("""
            CREATE TABLE IF NOT EXISTS cmm_olcum (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                isleme_kodu TEXT NOT NULL,
                dokum_kodu TEXT NOT NULL,
                izlenebilirlik_no TEXT NOT NULL,
                olcum_tarihi TEXT NOT NULL,
                operator_adi TEXT NOT NULL,
                operator_sicil TEXT NOT NULL,
                vardiya TEXT DEFAULT '',
                uygunluk TEXT NOT NULL,                 -- 'Uygun' / 'Uygun Değil'
                uygunsuzluk_nedeni TEXT,                -- serbest metin
                hata_tipi TEXT,                         -- opsiyonel
                kayit_tarihi TEXT DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # İskarta giriş tablosu (manuel)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS iskarta_giris (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                isleme_kodu TEXT NOT NULL,
                dokum_kodu TEXT NOT NULL,
                operator_adi TEXT NOT NULL,
                sicil_no TEXT NOT NULL,
                izlenebilirlik_no TEXT NOT NULL,
                operator_kisim TEXT NOT NULL,
                hata_tipi TEXT NOT NULL,                -- burada 'iskarta sebebi'ni saklayacağız
                iskarta_sebebi TEXT NOT NULL,
                kayit_tarihi TEXT DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Kalite onay tablosu (CMM / İskarta kaynaklı)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS kalite_onay (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kaynak_tablo TEXT NOT NULL,             -- 'cmm_olcum' | 'iskarta_giris'
                kaynak_id INTEGER NOT NULL,
                onay_veren_adi TEXT NOT NULL,
                onay_veren_sicil TEXT NOT NULL,
                karar TEXT NOT NULL,                    -- 'Tekrar İşle' | 'İskartalık'
                onay_tarihi TEXT DEFAULT CURRENT_TIMESTAMP
            );
        """)
        self.conn.commit()

    # --------------- Utilities ---------------
    def clear(self):
        for w in self.root.winfo_children():
            w.destroy()

    def header(self, title):
        top = tk.Frame(self.root, bg=self.colors["bg"], pady=20)
        top.pack(fill="x")
        tk.Label(
            top, text=title, font=("Arial", 20, "bold"),
            bg=self.colors["bg"], fg=self.colors["text"]
        ).pack()
        return top

    def orange_button(self, parent, text, cmd, width=28, height=3, font=("Arial", 14, "bold")):
        return tk.Button(parent, text=text, command=cmd, width=width, height=height,
                         font=font, bg=self.colors["primary"], fg="white", relief="flat", activebackground=self.colors["primary"])

    def white_button(self, parent, text, cmd, width=16, height=2, font=("Arial", 12, "bold"), border=2, color="primary"):
        bdcolor = self.colors["primary"] if color=="primary" else self.colors[color]
        btn = tk.Button(parent, text=text, command=cmd, width=width, height=height, font=font,
                        bg="white", fg=self.colors["text"], relief="solid", bd=border, highlightthickness=0)
        btn.configure(highlightbackground=bdcolor, highlightcolor=bdcolor)
        return btn

    # --------------- Main Menu ---------------
    def show_main_menu(self):
        self.clear()
        self.header("Kalite Takip Sistemi")

        frame = tk.Frame(self.root, bg=self.colors["bg"])
        frame.pack(expand=True)

        self.orange_button(frame, "1. CMM ÖLÇÜM GİRİŞİ", self.show_cmm_module).pack(pady=10)
        self.orange_button(frame, "2. İSKARTA GİRİŞİ", self.show_iskarta_module).pack(pady=10)
        self.orange_button(frame, "3. KALİTE ONAYI", self.show_kalite_onay_module).pack(pady=10)
        self.orange_button(frame, "4. PERFORMANS ANALİZİ", self.show_performans_module).pack(pady=10)

    # --------------- CMM Module ---------------
    def show_cmm_module(self):
        self.clear()
        self.header("CMM ÖLÇÜM GİRİŞİ")

        form = tk.Frame(self.root, bg=self.colors["bg"], padx=40, pady=10)
        form.pack(fill="x")

        entries = {}
        def add_row(label, key, default=""):
            row = tk.Frame(form, bg=self.colors["bg"])
            row.pack(fill="x", pady=6)
            tk.Label(row, text=label, width=28, anchor="w",
                     bg=self.colors["bg"], fg=self.colors["text"], font=("Arial", 12)).pack(side="left")
            e = tk.Entry(row, font=("Arial", 12), width=35, bg="white")
            e.insert(0, default)
            e.pack(side="left")
            entries[key] = e

        add_row("Parça İşleme Kodu:", "isleme_kodu")
        add_row("Parça Döküm Kodu:", "dokum_kodu")
        add_row("Parça İzlenebilirlik Numarası:", "izlenebilirlik_no")
        add_row("Ölçüm Tarihi:", "olcum_tarihi", datetime.now().strftime("%d.%m.%Y"))
        add_row("CMM Operatörü:", "operator_adi")
        add_row("CMM Operatörü Sicil No:", "operator_sicil")

        # Uygunluk
        row = tk.Frame(form, bg=self.colors["bg"])
        row.pack(fill="x", pady=6)
        tk.Label(row, text="Uygunluk Ölçüm Sonucu:", width=28, anchor="w",
                 bg=self.colors["bg"], fg=self.colors["text"], font=("Arial", 12)).pack(side="left")
        uygunluk_var = tk.StringVar(value="Uygun")
        tk.Radiobutton(row, text="Uygun", variable=uygunluk_var, value="Uygun",
                       bg=self.colors["bg"]).pack(side="left", padx=10)
        tk.Radiobutton(row, text="Uygun Değil", variable=uygunluk_var, value="Uygun Değil",
                       bg=self.colors["bg"]).pack(side="left", padx=10)

        # Uygunsuzluk nedeni (yalnızca 'Uygun Değil' seçilince aktif)
        row2 = tk.Frame(form, bg=self.colors["bg"])
        row2.pack(fill="x", pady=6)
        tk.Label(row2, text="Uygun Değilse Nedeni:", width=28, anchor="w",
                 bg=self.colors["bg"], fg=self.colors["text"], font=("Arial", 12)).pack(side="left")
        neden_text = scrolledtext.ScrolledText(row2, width=50, height=4, state="disabled")
        neden_text.pack(side="left")
        def toggle_neden(*_):
            if uygunluk_var.get() == "Uygun Değil":
                neden_text.configure(state="normal", bg="white")
            else:
                neden_text.delete("1.0", "end")
                neden_text.configure(state="disabled", bg=self.colors["light_gray"])
        uygunluk_var.trace_add("write", toggle_neden)
        toggle_neden()

        # Vardiya (opsiyonel)
        row3 = tk.Frame(form, bg=self.colors["bg"])
        row3.pack(fill="x", pady=6)
        tk.Label(row3, text="Vardiya:", width=28, anchor="w",
                 bg=self.colors["bg"], fg=self.colors["text"], font=("Arial", 12)).pack(side="left")
        vardiya_e = tk.Entry(row3, font=("Arial", 12), width=35, bg="white")
        vardiya_e.pack(side="left")
        entries["vardiya"] = vardiya_e

        # Butonlar
        btns = tk.Frame(self.root, bg=self.colors["bg"], pady=15)
        btns.pack()
        self.white_button(btns, "KAYDET", lambda: self.save_cmm(entries, uygunluk_var.get(), neden_text.get("1.0","end").strip()), color="success").pack(side="left", padx=10)
        self.white_button(btns, "ANA MENÜ", self.show_main_menu, color="primary").pack(side="left", padx=10)

    def save_cmm(self, entries, uygunluk, neden):
        data = {k: e.get().strip() for k, e in entries.items()}
        required = ["isleme_kodu","dokum_kodu","izlenebilirlik_no","olcum_tarihi","operator_adi","operator_sicil"]
        for key in required:
            if not data.get(key):
                messagebox.showerror("Hata", f"Lütfen '{key.replace('_',' ').title()}' alanını doldurun.")
                return
        if uygunluk == "Uygun Değil" and not neden:
            messagebox.showerror("Hata", "Uygun değilse nedeni girilmelidir.")
            return

        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO cmm_olcum (isleme_kodu, dokum_kodu, izlenebilirlik_no, olcum_tarihi,
                                   operator_adi, operator_sicil, vardiya, uygunluk, uygunsuzluk_nedeni)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            data["isleme_kodu"], data["dokum_kodu"], data["izlenebilirlik_no"], data["olcum_tarihi"],
            data["operator_adi"], data["operator_sicil"], data.get("vardiya",""),
            uygunluk, neden if uygunluk=="Uygun Değil" else None
        ))
        self.conn.commit()
        messagebox.showinfo("Başarılı", "CMM ölçüm kaydı eklendi.")

    # --------------- İskarta Module ---------------
    def show_iskarta_module(self):
        self.clear()
        self.header("İSKARTA GİRİŞİ")

        container = tk.Frame(self.root, bg=self.colors["bg"], padx=10, pady=10)
        container.pack(fill="both", expand=True)

        # Sol: CMM'de 'Uygun Değil' olanlar (referans listesi)
        left = tk.LabelFrame(container, text="CMM 'Uygun Değil' Referans Listesi", bg=self.colors["bg"], fg=self.colors["text"])
        left.pack(side="left", fill="both", expand=True, padx=(0,10))

        cols = ("id","izlenebilirlik_no","isleme_kodu","operator_adi","vardiya","olcum_tarihi")
        tree = ttk.Treeview(left, columns=cols, show="headings", height=16)
        for c in cols:
            tree.heading(c, text=c.replace("_"," ").title())
            tree.column(c, width=150 if c!="id" else 60, anchor="center")
        tree.pack(fill="both", expand=True, padx=6, pady=6)

        cur = self.conn.cursor()
        cur.execute("""
            SELECT id, izlenebilirlik_no, isleme_kodu, operator_adi, COALESCE(vardiya,''), olcum_tarihi
            FROM cmm_olcum
            WHERE uygunluk='Uygun Değil'
            ORDER BY datetime(kayit_tarihi) DESC
            LIMIT 200;
        """)
        for r in cur.fetchall():
            tree.insert("", "end", values=r)

        # Sağ: Manuel iskarta formu
        right = tk.LabelFrame(container, text="İskarta Giriş Formu (Manuel)", bg=self.colors["bg"], fg=self.colors["text"])
        right.pack(side="left", fill="both", expand=True)

        entries = {}
        def row(parent, label, key, width=36):
            f = tk.Frame(parent, bg=self.colors["bg"])
            f.pack(fill="x", pady=5, padx=6)
            tk.Label(f, text=label, width=24, anchor="w", bg=self.colors["bg"], fg=self.colors["text"]).pack(side="left")
            e = tk.Entry(f, width=width, font=("Arial", 12), bg="white")
            e.pack(side="left")
            entries[key] = e
        row(right, "Parça İşleme Kodu:", "isleme_kodu")
        row(right, "Parça Döküm Kodu:", "dokum_kodu")
        row(right, "Operatörün Adı:", "operator_adi")
        row(right, "Sicil No:", "sicil_no")
        row(right, "İzlenebilirlik Numarası:", "izlenebilirlik_no")
        row(right, "Operatörün Bulunduğu Kısım:", "operator_kisim")

        f2 = tk.Frame(right, bg=self.colors["bg"])
        f2.pack(fill="x", pady=5, padx=6)
        tk.Label(f2, text="İskarta Sebebi:", width=24, anchor="w", bg=self.colors["bg"], fg=self.colors["text"]).pack(side="left")
        sebep = scrolledtext.ScrolledText(f2, width=44, height=4)
        sebep.pack(side="left")

        btns = tk.Frame(right, bg=self.colors["bg"], pady=10)
        btns.pack()
        def save_iskarta():
            data = {k: e.get().strip() for k, e in entries.items()}
            reason = sebep.get("1.0","end").strip()
            req = ["isleme_kodu","dokum_kodu","operator_adi","sicil_no","izlenebilirlik_no","operator_kisim"]
            for k in req:
                if not data.get(k):
                    messagebox.showerror("Hata", f"'{k.replace('_',' ').title()}' boş olamaz.")
                    return
            if not reason:
                messagebox.showerror("Hata", "İskarta sebebi boş olamaz.")
                return
            cur = self.conn.cursor()
            cur.execute("""
                INSERT INTO iskarta_giris (isleme_kodu,dokum_kodu,operator_adi,sicil_no,
                                           izlenebilirlik_no,operator_kisim,hata_tipi,iskarta_sebebi)
                VALUES (?,?,?,?,?,?,?,?);
            """, (data["isleme_kodu"], data["dokum_kodu"], data["operator_adi"], data["sicil_no"],
                  data["izlenebilirlik_no"], data["operator_kisim"], reason, reason))
            self.conn.commit()
            messagebox.showinfo("Başarılı","İskarta kaydı eklendi.")
        self.white_button(btns, "KAYDET", save_iskarta, color="success").pack(side="left", padx=6)
        self.white_button(btns, "ANA MENÜ", self.show_main_menu, color="primary").pack(side="left", padx=6)

    # --------------- Kalite Onay Module ---------------
    def show_kalite_onay_module(self):
        self.clear()
        self.header("KALİTE ONAYI")

        container = tk.Frame(self.root, bg=self.colors["bg"], padx=10, pady=10)
        container.pack(fill="both", expand=True)

        # Bekleyen kayıtlar (CMM: 'Uygun Değil' + onaylanmamış) + (İskarta: onaylanmamış)
        cols = ("tip","kayıt_id","izlenebilirlik_no","isleme_kodu","dokum_kodu","operator","tarih")
        tree = ttk.Treeview(container, columns=cols, show="headings", height=18)
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=150 if c not in ("kayıt_id","tip") else 90, anchor="center")
        tree.pack(fill="both", expand=True)

        cur = self.conn.cursor()
        # CMM pending
        cur.execute("""
            SELECT 'CMM' as tip, c.id, c.izlenebilirlik_no, c.isleme_kodu, c.dokum_kodu, c.operator_adi, c.olcum_tarihi
            FROM cmm_olcum c
            WHERE c.uygunluk='Uygun Değil'
              AND NOT EXISTS (SELECT 1 FROM kalite_onay k WHERE k.kaynak_tablo='cmm_olcum' AND k.kaynak_id=c.id)
            ORDER BY datetime(c.kayit_tarihi) DESC
            LIMIT 300;
        """)
        rows = cur.fetchall()
        for r in rows:
            tree.insert("", "end", values=r)
        # İskarta pending
        cur.execute("""
            SELECT 'ISKARTA' as tip, i.id, i.izlenebilirlik_no, i.isleme_kodu, i.dokum_kodu, i.operator_adi, i.kayit_tarihi
            FROM iskarta_giris i
            WHERE NOT EXISTS (SELECT 1 FROM kalite_onay k WHERE k.kaynak_tablo='iskarta_giris' AND k.kaynak_id=i.id)
            ORDER BY datetime(i.kayit_tarihi) DESC
            LIMIT 300;
        """)
        for r in cur.fetchall():
            tree.insert("", "end", values=r)

        btns = tk.Frame(self.root, bg=self.colors["bg"], pady=10)
        btns.pack()
        self.white_button(btns, "SEÇİLENİ ONAYLA", lambda: self.open_onay_dialog(tree), color="success").pack(side="left", padx=6)
        self.white_button(btns, "ANA MENÜ", self.show_main_menu, color="primary").pack(side="left", padx=6)

    def open_onay_dialog(self, tree):
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Uyarı", "Lütfen bir kayıt seçin.")
            return
        vals = tree.item(sel[0])["values"]
        tip, rid, iz_no, isleme, dokum, oper, tarih = vals

        dialog = tk.Toplevel(self.root)
        dialog.title("Kalite Onayı")
        dialog.configure(bg=self.colors["bg"])
        dialog.grab_set()

        tk.Label(dialog, text=f"Tip: {tip} | Kayıt ID: {rid}", bg=self.colors["bg"], fg=self.colors["text"], font=("Arial", 12, "bold")).pack(pady=6)
        tk.Label(dialog, text=f"İzlenebilirlik: {iz_no} | Parça: {isleme} / {dokum}", bg=self.colors["bg"], fg=self.colors["text"]).pack()

        f = tk.Frame(dialog, bg=self.colors["bg"], pady=8)
        f.pack()
        tk.Label(f, text="Onay Veren Adı:", bg=self.colors["bg"], fg=self.colors["text"]).grid(row=0, column=0, sticky="e", padx=6, pady=4)
        onay_adi = tk.Entry(f, width=28); onay_adi.grid(row=0,column=1, padx=6, pady=4)
        tk.Label(f, text="Onay Veren Sicil:", bg=self.colors["bg"], fg=self.colors["text"]).grid(row=1, column=0, sticky="e", padx=6, pady=4)
        onay_sicil = tk.Entry(f, width=28); onay_sicil.grid(row=1,column=1, padx=6, pady=4)

        b = tk.Frame(dialog, bg=self.colors["bg"], pady=10)
        b.pack()
        def do_onay(karar):
            name = onay_adi.get().strip()
            sicil = onay_sicil.get().strip()
            if not name or not sicil:
                messagebox.showerror("Hata", "Onay veren bilgileri eksiksiz girilmeli!")
                return
            # İzlenebilirlik uyarısı: sadece İskartalık verilince
            if karar == "İskartalık":
                self.show_izlenebilirlik_uyari(iz_no)

            cur = self.conn.cursor()
            cur.execute("""
                INSERT INTO kalite_onay (kaynak_tablo, kaynak_id, onay_veren_adi, onay_veren_sicil, karar)
                VALUES (?, ?, ?, ?, ?);
            """, ("cmm_olcum" if tip=="CMM" else "iskarta_giris", int(rid), name, sicil, karar))
            self.conn.commit()
            messagebox.showinfo("Başarılı", f"Kayıt '{karar}' olarak onaylandı.")
            dialog.destroy()
            self.show_kalite_onay_module()

        tk.Button(b, text="TEKRAR İŞLE", command=lambda: do_onay("Tekrar İşle"),
                  bg=self.colors["primary"], fg="white", relief="flat", width=16, height=2, font=("Arial", 12, "bold")).pack(side="left", padx=8)
        tk.Button(b, text="İSKARTALIK", command=lambda: do_onay("İskartalık"),
                  bg=self.colors["danger"], fg="white", relief="flat", width=16, height=2, font=("Arial", 12, "bold")).pack(side="left", padx=8)
        tk.Button(b, text="İptal", command=dialog.destroy,
                  bg="gray", fg="white", relief="flat", width=10, height=2).pack(side="left", padx=8)

    def parse_iz_no(self, iz):
        """
        'TK-1240' ya da '08129' gibi değerlerden (prefix, number) çıkar.
        number bulunamazsa None döner.
        """
        if iz is None:
            return ("", None)
        m = re.search(r"^(.*?)(\d+)$", str(iz).strip())
        if not m:
            return (iz, None)
        return (m.group(1), int(m.group(2)))

    def show_izlenebilirlik_uyari(self, current_iz):
        """
        Son 'İskartalık' verilen kaydı bul, aynı prefiksteyse aralıktaki
        izlenebilirlik numaralarını öner.
        """
        cur = self.conn.cursor()
        # en son iskarta verilen (CMM veya İskarta kaynaklı) izlenebilirlik
        cur.execute("""
            SELECT coalesce(c.izlenebilirlik_no, i.izlenebilirlik_no) AS iz_no, k.onay_tarihi
            FROM kalite_onay k
            LEFT JOIN cmm_olcum c ON (k.kaynak_tablo='cmm_olcum' AND c.id=k.kaynak_id)
            LEFT JOIN iskarta_giris i ON (k.kaynak_tablo='iskarta_giris' AND i.id=k.kaynak_id)
            WHERE k.karar='İskartalık'
            ORDER BY datetime(k.onay_tarihi) DESC
            LIMIT 1;
        """)
        row = cur.fetchone()
        if not row or not row[0]:
            return  # önce iskarta yoksa uyarı göstermeyelim

        last_iz = row[0]
        pre1, n1 = self.parse_iz_no(last_iz)
        pre2, n2 = self.parse_iz_no(current_iz)
        if n1 is None or n2 is None or pre1 != pre2:
            return  # sayısal karşılaştırma mümkün değilse

        if n2 - n1 <= 1:
            return  # aralık yoksa

        # Aradaki izlenebilirlikleri üret
        ara = [f"{pre2}{i:0{len(str(n2))}d}" if pre2 else str(i) for i in range(n1+1, n2)]
        # Basit uyarı penceresi
        top = tk.Toplevel(self.root)
        top.title("⚠️ İzlenebilirlik Uyarısı")
        top.configure(bg=self.colors["bg"])
        msg = (f"İSKARTA TESPİT EDİLDİ\n\n"
               f"Son iskarta parça: {last_iz}\n"
               f"Yeni iskarta parça: {current_iz}\n\n"
               f"Aradaki {len(ara)} parça kontrol edilmeli:")
        tk.Label(top, text=msg, justify="left", bg=self.colors["bg"], fg=self.colors["text"],
                 font=("Arial", 12)).pack(padx=12, pady=8, anchor="w")
        box = scrolledtext.ScrolledText(top, width=46, height=8)
        box.pack(padx=12, pady=6, fill="both", expand=True)
        box.insert("end", ", ".join(ara))
        box.configure(state="disabled")
        tk.Button(top, text="Tamam", command=top.destroy, bg=self.colors["primary"], fg="white",
                  relief="flat", width=12, height=2).pack(pady=8)

    # --------------- Performans Analizi ---------------
    def show_performans_module(self):
        self.clear()
        self.header("PERFORMANS ANALİZİ")

        # Üst filtreler (gün/ay/yıl basit seçim)
        filt = tk.Frame(self.root, bg=self.colors["bg"])
        filt.pack(pady=6)

        per_var = tk.StringVar(value="Günlük")
        ttk.Combobox(filt, textvariable=per_var, values=["Günlük","Aylık","Yıllık"], width=12, state="readonly").pack(side="left", padx=6)

        def draw():
            for widget in chart.winfo_children():
                widget.destroy()

            period = per_var.get()
            cur = self.conn.cursor()

            # CMM sayıları (Uygun/Uygun Değil)
            if period == "Günlük":
                grp = "%d.%m.%Y"
                where_clause = "strftime('%d.%m.%Y', kayit_tarihi)=strftime('%d.%m.%Y','now')"
            elif period == "Aylık":
                grp = "%m.%Y"
                where_clause = "strftime('%m.%Y', kayit_tarihi)=strftime('%m.%Y','now')"
            else:
                grp = "%Y"
                where_clause = "strftime('%Y', kayit_tarihi)=strftime('%Y','now')"

            # CMM toplam
            cur.execute(f"SELECT COUNT(*), SUM(CASE WHEN uygunluk='Uygun Değil' THEN 1 ELSE 0 END) FROM cmm_olcum WHERE {where_clause};")
            cmm_total, cmm_nok = cur.fetchone()
            cmm_total = cmm_total or 0
            cmm_nok = cmm_nok or 0

            # İskarta sayısı
            cur.execute(f"SELECT COUNT(*) FROM iskarta_giris WHERE {where_clause.replace('kayit_tarihi','kayit_tarihi')};")
            iskarta_total = cur.fetchone()[0] or 0

            # Basit pasta grafikleri
            fig1 = plt.Figure(figsize=(3.8,3.2))
            ax1 = fig1.add_subplot(111)
            vals = [cmm_total - cmm_nok, cmm_nok]
            labs = ["CMM Uygun", "CMM Uygun Değil"]
            ax1.pie(vals if sum(vals)>0 else [1], labels=labs if sum(vals)>0 else ["Veri yok"], autopct="%1.0f%%")
            ax1.set_title("CMM Sonuç Dağılımı")

            canvas1 = FigureCanvasTkAgg(fig1, master=chart)
            canvas1.draw()
            canvas1.get_tk_widget().pack(side="left", padx=10)

            fig2 = plt.Figure(figsize=(3.8,3.2))
            ax2 = fig2.add_subplot(111)
            vals2 = [iskarta_total, (cmm_total - iskarta_total)]
            labs2 = ["İskarta Kayıtları", "Diğer Kayıtlar"]
            ax2.pie(vals2 if sum(vals2)>0 else [1], labels=labs2 if sum(vals2)>0 else ["Veri yok"], autopct="%1.0f%%")
            ax2.set_title("İskarta Oranı")

            canvas2 = FigureCanvasTkAgg(fig2, master=chart)
            canvas2.draw()
            canvas2.get_tk_widget().pack(side="left", padx=10)

        tk.Button(filt, text="GÖSTER", command=draw, bg=self.colors["primary"], fg="white",
                  relief="flat", width=12, height=2).pack(side="left", padx=6)
        tk.Button(filt, text="ANA MENÜ", command=self.show_main_menu, bg="white", fg=self.colors["text"],
                  relief="solid", bd=2, width=12, height=2).pack(side="left", padx=6)

        chart = tk.Frame(self.root, bg=self.colors["bg"])
        chart.pack(fill="both", expand=True, pady=10)

    # --------------- Run ---------------
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = KaliteTakipSistemi()
    app.run()
