# BellSekolah_Pro.py
# ==============================================================
# Aplikasi Bell Sekolah Pro (Full Terintegrasi)
# Versi: 1.0
# ==============================================================
# Copyright (c) 2025
# All rights reserved.
# ==============================================================

# -*- coding: utf-8 -*-
import os, json, time, threading
from pathlib import Path
from datetime import datetime, date
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk
from PIL import Image, ImageTk

# ---- Audio: pygame ----
try:
    import pygame
    HAVE_PYGAME = True
except Exception:
    HAVE_PYGAME = False

APP_NAME = "Bel Sekolah Otomatis — Custom UI"
BASE_DIR = Path(__file__).parent
CFG_FILE = BASE_DIR / "settings.json"
JADWAL_FILE = BASE_DIR / "jadwal.json"
ASSETS_DIR = BASE_DIR / "assets"

HARI_LIST = ["Senin","Selasa","Rabu","Kamis","Jumat","Sabtu","Ujian"]

DEFAULT_CFG = {
    "appearance": "System",   # System | Light | Dark
    "accent": "blue",         # blue | green | dark-blue
    "header": {
        "school_name": "Nama Sekolah",
        "school_address": "Alamat Sekolah",
        "logo_path": "",
        "font_family": "Segoe UI",
        "font_size": 22,
        "font_color": "#FFFFFF",
        "bg_color": "#1f2937"
    },
    "running_text": {
        "bg_color": "#0b0b0b",
        "items": [
            {"text": "Selamat datang di Aplikasi Bel Sekolah Otomatis", "font_family":"Segoe UI", "font_size":16, "font_color":"#ffffff", "speed":2},
            {"text": "Disiplin waktu adalah kunci sukses!", "font_family":"Segoe UI", "font_size":16, "font_color":"#ffffff", "speed":2}
        ]
    },
    "clock": {
        "mode_24h": True,
        "time_font_family": "Segoe UI Black",
        "time_font_size": 44,
        "time_color": "#10B981",
        "date_font_family": "Segoe UI",
        "date_font_size": 16,
        "date_color": "#d1d5db"
    },
    "app": {
        "auto_bell_enabled": True
    },
    # Footer sederhana
    "footer": {
        "show": True,
        "text": "© 2025 Nama Sekolah. All rights reserved.",
        "font_family": "Segoe UI",
        "font_size": 12,
        "font_color": "#9CA3AF",
        "bg_color": "transparent"
    },
    # Mapping file audio untuk tombol cepat
    "quick_sounds": {
        "info": "",
        "btn1": "", "btn2": "", "btn3": "", "btn4": "", "btn5": "",
        "btn6": "", "btn7": "", "btn8": "", "btn9": "", "btn10": ""
    }
}

DEFAULT_JADWAL = {h: [] for h in HARI_LIST}

# ---------------- IO Helpers ----------------
def load_json(path, default):
    p = Path(path)
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    return json.loads(json.dumps(default))

def save_json(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

# --------------- Marquee -------------------
class Marquee(ctk.CTkFrame):
    def __init__(self, master, get_items, height=32, bg="#000000"):
        super().__init__(master, fg_color=bg, height=height)
        self.grid_propagate(False)
        self.canvas = tk.Canvas(self, height=height, highlightthickness=0, bd=0, bg=bg)
        self.canvas.pack(fill="both", expand=True)
        self.get_items = get_items
        self._item_idx = 0
        self._text_id = None
        self._x = 0
        self._running = True
        self._style = {"font": ("Segoe UI", 16), "fill": "#fff", "speed": 2}
        self.after(200, self._loop)

    def set_bg(self, color):
        self.canvas.configure(bg=color)
        self.configure(fg_color=color)

    def stop(self):
        self._running = False

    def _draw_current(self):
        items = self.get_items() or []
        if not items:
            self.canvas.delete("all"); self._text_id = None; return
        it = items[self._item_idx % len(items)]
        text = it.get("text","")
        font = (it.get("font_family","Segoe UI"), int(it.get("font_size",16)))
        fill = it.get("font_color","#ffffff")
        speed = max(1, int(it.get("speed",2)))
        self._style = {"font": font, "fill": fill, "speed": speed}
        self.canvas.delete("all")
        x = self.canvas.winfo_width()
        y = self.canvas.winfo_height()//2
        self._text_id = self.canvas.create_text(x, y, text=text, anchor="w", font=font, fill=fill)
        self._x = x

    def _loop(self):
        if not self._running: return
        items = self.get_items() or []
        if not items:
            self.after(600, self._loop); return
        if self._text_id is None:
            self._draw_current()
        speed = self._style["speed"]
        self._x -= speed
        self.canvas.move(self._text_id, -speed, 0)
        bbox = self.canvas.bbox(self._text_id)
        if bbox and bbox[2] < 0:
            self._item_idx += 1
            self._text_id = None
            self.after(150, self._loop); return
        self.after(20, self._loop)

# -------------- Settings Window ---------------
class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.title("Pengaturan")
        self.geometry("920x640")
        self.transient(app)
        self.grab_set()

        # clone current config
        self.cfg = json.loads(json.dumps(app.cfg))

        tab = ctk.CTkTabview(self)
        tab.pack(fill="both", expand=True, padx=12, pady=12)

        self.tab_header = tab.add("Header")
        self.tab_running = tab.add("Running Text")
        self.tab_clock = tab.add("Jam & Tanggal")
        self.tab_theme = tab.add("Tema")
        self.tab_footer = tab.add("Footer")
        self.tab_quick = tab.add("Informasi & Tombol")

        self._build_header_tab(self.tab_header)
        self._build_running_tab(self.tab_running)
        self._build_clock_tab(self.tab_clock)
        self._build_theme_tab(self.tab_theme)
        self._build_footer_tab(self.tab_footer)
        self._build_quick_tab(self.tab_quick)

        footer = ctk.CTkFrame(self)
        footer.pack(fill="x", padx=12, pady=(0,12))
        ctk.CTkButton(footer, text="Batal", command=self.destroy).pack(side="right", padx=6)
        ctk.CTkButton(footer, text="Simpan", command=self._save).pack(side="right")

    # ---- small helpers ----
    def _color_btn(self, master, text, var):
        row = ctk.CTkFrame(master)
        row.pack(fill="x", pady=4)
        ctk.CTkLabel(row, text=text, anchor="w").pack(side="left", padx=6)
        ent = ctk.CTkEntry(row, width=120)
        ent.insert(0, var.get())
        ent.pack(side="left")
        def pick():
            from tkinter import colorchooser
            c = colorchooser.askcolor()[1]
            if c:
                var.set(c); ent.delete(0,"end"); ent.insert(0,c)
        ctk.CTkButton(row, text="Pilih", command=pick, width=70).pack(side="left", padx=6)
        return ent

    # ---- Header tab ----
    def _build_header_tab(self, parent):
        h = self.cfg.get("header",{})
        grid = ctk.CTkFrame(parent)
        grid.pack(fill="both", expand=True, padx=8, pady=8)

        # kiri
        left = ctk.CTkFrame(grid)
        left.pack(side="left", fill="both", expand=True, padx=(0,8))

        self.ent_school = ctk.CTkEntry(left, placeholder_text="Nama Sekolah")
        self.ent_school.insert(0, h.get("school_name",""))
        self.ent_school.pack(fill="x", pady=6)

        self.ent_addr = ctk.CTkEntry(left, placeholder_text="Alamat Sekolah")
        self.ent_addr.insert(0, h.get("school_address",""))
        self.ent_addr.pack(fill="x", pady=6)

        row_logo = ctk.CTkFrame(left); row_logo.pack(fill="x", pady=6)
        self.logo_path = tk.StringVar(value=h.get("logo_path",""))
        ent_logo = ctk.CTkEntry(row_logo); ent_logo.insert(0, self.logo_path.get()); ent_logo.pack(side="left", fill="x", expand=True)
        def pick_logo():
            p = filedialog.askopenfilename(title="Pilih Logo", filetypes=[("Gambar","*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
            if p:
                self.logo_path.set(p); ent_logo.delete(0,"end"); ent_logo.insert(0,p)
        ctk.CTkButton(row_logo, text="📂", command=pick_logo, width=44).pack(side="left", padx=6)

        row_font = ctk.CTkFrame(left); row_font.pack(fill="x", pady=6)
        ctk.CTkLabel(row_font, text="Ukuran Font:").pack(side="left", padx=4)
        self.spn_size = ctk.CTkSlider(row_font, from_=12, to=48, number_of_steps=36)
        self.spn_size.set(int(h.get("font_size",22)))
        self.spn_size.pack(side="left", fill="x", expand=True, padx=8)

        self.col_font = tk.StringVar(value=h.get("font_color","#FFFFFF"))
        self.col_bg = tk.StringVar(value=h.get("bg_color","#1f2937"))
        self._color_btn(left, "Warna Teks Header", self.col_font)
        self._color_btn(left, "Warna Latar Header", self.col_bg)

        # kanan preview
        right = ctk.CTkFrame(grid)
        right.pack(side="left", fill="both", expand=True)
        self.prev = ctk.CTkFrame(right, height=120, fg_color=self.col_bg.get())
        self.prev.pack(fill="x", pady=8)
        self.prev.pack_propagate(False)
        self.prev_label1 = ctk.CTkLabel(self.prev, text=h.get("school_name","Nama Sekolah"),
                                        font=ctk.CTkFont(size=int(h.get("font_size",22)), weight="bold"),
                                        text_color=self.col_font.get())
        self.prev_label1.pack(anchor="w", padx=16, pady=(12,0))
        self.prev_label2 = ctk.CTkLabel(self.prev, text=h.get("school_address","Alamat Sekolah"), text_color="#cbd5e1")
        self.prev_label2.pack(anchor="w", padx=16)

        def sync_preview(*_):
            self.prev.configure(fg_color=self.col_bg.get())
            self.prev_label1.configure(text=self.ent_school.get().strip() or "Nama Sekolah",
                                       text_color=self.col_font.get(),
                                       font=ctk.CTkFont(size=int(self.spn_size.get()), weight="bold"))
            self.prev_label2.configure(text=self.ent_addr.get().strip() or "Alamat Sekolah")
        for w in [self.ent_school, self.ent_addr]:
            w.bind("<KeyRelease>", sync_preview)
        self.prev.bind("<Configure>", sync_preview)

    # ---- Running Text tab ----
    def _build_running_tab(self, parent):
        rt = self.cfg.get("running_text",{})
        container = ctk.CTkFrame(parent); container.pack(fill="both", expand=True, padx=8, pady=8)

        left = ctk.CTkFrame(container); left.pack(side="left", fill="both", expand=True, padx=(0,8))
        ctk.CTkLabel(left, text="Daftar Teks (diputar bergantian)").pack(anchor="w", pady=(0,6))
        self.lst = tk.Listbox(left, height=10)
        self.lst.pack(fill="both", expand=True)
        for it in rt.get("items", []):
            self.lst.insert("end", it.get("text","(teks)"))

        btns = ctk.CTkFrame(left); btns.pack(fill="x", pady=6)
        ctk.CTkButton(btns, text="Tambah", command=self._rt_add).pack(side="left")
        ctk.CTkButton(btns, text="Edit", command=self._rt_edit).pack(side="left", padx=6)
        ctk.CTkButton(btns, text="Hapus", command=self._rt_del).pack(side="left")

        right = ctk.CTkFrame(container); right.pack(side="left", fill="y")
        self.rt_bg = tk.StringVar(value=rt.get("bg_color","#000000"))
        self._color_btn(right, "Warna Latar Marquee", self.rt_bg)

    def _rt_dialog(self, item=None):
        win = ctk.CTkToplevel(self)
        win.title("Item Running Text"); win.geometry("420x300"); win.grab_set(); win.transient(self)
        ent_text = ctk.CTkEntry(win, placeholder_text="Isi teks"); ent_text.pack(fill="x", padx=12, pady=8)
        spn_size = ctk.CTkSlider(win, from_=10, to=48, number_of_steps=38); spn_size.set(16); spn_size.pack(fill="x", padx=12, pady=8)
        col = tk.StringVar(value="#ffffff")
        row = ctk.CTkFrame(win); row.pack(fill="x", padx=12, pady=8)
        ctk.CTkLabel(row, text="Kecepatan (1–5)").pack(side="left")
        spn_speed = ctk.CTkSlider(row, from_=1, to=5, number_of_steps=4); spn_speed.set(2); spn_speed.pack(side="left", fill="x", expand=True, padx=8)
        def pick_color():
            from tkinter import colorchooser
            c = colorchooser.askcolor()[1]
            if c: col.set(c)
        ctk.CTkButton(win, text="Pilih Warna Teks", command=pick_color).pack(pady=6)

        if item:
            ent_text.insert(0, item.get("text",""))
            spn_size.set(int(item.get("font_size",16)))
            col.set(item.get("font_color","#ffffff"))
            spn_speed.set(int(item.get("speed",2)))

        res = {}
        def ok():
            res.update({"text": ent_text.get().strip() or "(teks)",
                        "font_family":"Segoe UI",
                        "font_size": int(spn_size.get() or 16),
                        "font_color": col.get() or "#ffffff",
                        "speed": int(spn_speed.get() or 2)})
            win.destroy()
        ctk.CTkButton(win, text="Simpan", command=ok).pack(side="right", padx=12, pady=10)
        ctk.CTkButton(win, text="Batal", command=win.destroy).pack(side="right", pady=10)
        win.wait_window()
        return res if res else None

    def _rt_add(self):
        it = self._rt_dialog()
        if it:
            self.cfg["running_text"]["items"].append(it)
            self.lst.insert("end", it["text"])

    def _rt_edit(self):
        sel = self.lst.curselection()
        if not sel: return
        idx = sel[0]
        cur = self.cfg["running_text"]["items"][idx]
        it = self._rt_dialog(cur)
        if it:
            self.cfg["running_text"]["items"][idx] = it
            self.lst.delete(idx); self.lst.insert(idx, it["text"])

    def _rt_del(self):
        sel = self.lst.curselection()
        if not sel: return
        idx = sel[0]
        del self.cfg["running_text"]["items"][idx]
        self.lst.delete(idx)

    # ---- Clock tab ----
    def _build_clock_tab(self, parent):
        c = self.cfg.get("clock",{})
        box = ctk.CTkFrame(parent); box.pack(fill="x", padx=12, pady=12)
        self.var_24 = tk.BooleanVar(value=c.get("mode_24h", True))
        ctk.CTkSwitch(box, text="Format 24 Jam (Off = 12 Jam)", variable=self.var_24).pack(anchor="w", pady=6, padx=6)

        row1 = ctk.CTkFrame(parent); row1.pack(fill="x", padx=12, pady=6)
        ctk.CTkLabel(row1, text="Ukuran Jam").pack(side="left", padx=6)
        self.sl_time_size = ctk.CTkSlider(row1, from_=24, to=120, number_of_steps=96)
        self.sl_time_size.set(int(c.get("time_font_size",44)))
        self.sl_time_size.pack(side="left", fill="x", expand=True, padx=6)
        self.time_color = tk.StringVar(value=c.get("time_color","#10B981"))
        self._color_btn(parent, "Warna Jam", self.time_color)

        row2 = ctk.CTkFrame(parent); row2.pack(fill="x", padx=12, pady=6)
        ctk.CTkLabel(row2, text="Ukuran Tanggal").pack(side="left", padx=6)
        self.sl_date_size = ctk.CTkSlider(row2, from_=12, to=64, number_of_steps=52)
        self.sl_date_size.set(int(c.get("date_font_size",16)))
        self.sl_date_size.pack(side="left", fill="x", expand=True, padx=6)
        self.date_color = tk.StringVar(value=c.get("date_color","#d1d5db"))
        self._color_btn(parent, "Warna Tanggal", self.date_color)

    # ---- Theme tab ----
    def _build_theme_tab(self, parent):
        row = ctk.CTkFrame(parent); row.pack(fill="x", padx=12, pady=12)
        ctk.CTkLabel(row, text="Mode Tampilan").pack(side="left", padx=6)
        self.mode_opt = ctk.CTkOptionMenu(row, values=["System","Light","Dark"])
        self.mode_opt.set(self.cfg.get("appearance","System"))
        self.mode_opt.pack(side="left")
        row2 = ctk.CTkFrame(parent); row2.pack(fill="x", padx=12, pady=8)
        ctk.CTkLabel(row2, text="Aksen Warna").pack(side="left", padx=6)
        self.accent_opt = ctk.CTkOptionMenu(row2, values=["blue","green","dark-blue"])
        self.accent_opt.set(self.cfg.get("accent","blue"))
        self.accent_opt.pack(side="left")

    # ---- Footer tab ----
    def _build_footer_tab(self, parent):
        f = self.cfg.get("footer", {})
        box = ctk.CTkFrame(parent); box.pack(fill="both", expand=True, padx=12, pady=12)

        self.footer_show = tk.BooleanVar(value=f.get("show", True))
        ctk.CTkSwitch(box, text="Tampilkan Copyright (Footer)", variable=self.footer_show)\
            .pack(anchor="w", pady=(0,10), padx=6)

        ctk.CTkLabel(box, text="Teks Copyright").pack(anchor="w", padx=6)
        self.ent_footer_text = ctk.CTkEntry(box, placeholder_text="© 2025 Nama Sekolah. All rights reserved.")
        self.ent_footer_text.insert(0, f.get("text", "© 2025 Nama Sekolah. All rights reserved."))
        self.ent_footer_text.pack(fill="x", pady=6, padx=6)

        row_size = ctk.CTkFrame(box); row_size.pack(fill="x", padx=6, pady=6)
        ctk.CTkLabel(row_size, text="Ukuran Font").pack(side="left")
        self.sl_footer_size = ctk.CTkSlider(row_size, from_=8, to=24, number_of_steps=16)
        self.sl_footer_size.set(int(f.get("font_size", 12)))
        self.sl_footer_size.pack(side="left", fill="x", expand=True, padx=8)

        self.footer_txt_color = tk.StringVar(value=f.get("font_color", "#9CA3AF"))
        self._color_btn(box, "Warna Teks", self.footer_txt_color)

        self.footer_bg_color = tk.StringVar(value=f.get("bg_color", "transparent"))
        self._color_btn(box, "Warna Latar Footer", self.footer_bg_color)

    # ---- Quick Sounds tab (tanpa tabel; per baris ada pilih & uji putar) ----
    def _build_quick_tab(self, parent):
        qs = self.cfg.get("quick_sounds", {})
        box = ctk.CTkScrollableFrame(parent, label_text="Pilih audio untuk tombol cepat")
        box.pack(fill="both", expand=True, padx=12, pady=12)

        self._qs_vars = {}
        items = [("ℹ Informasi", "info")]
        for i in range(1, 11):
            items.append((f"Tombol {i}", f"btn{i}"))

        for label, key in items:
            row = ctk.CTkFrame(box); row.pack(fill="x", pady=6)
            ctk.CTkLabel(row, text=label, width=130).pack(side="left", padx=(6,6))
            var = tk.StringVar(value=qs.get(key, ""))
            ent = ctk.CTkEntry(row); ent.insert(0, var.get()); ent.pack(side="left", fill="x", expand=True)
            def pick(v=var, e=ent):
                p = filedialog.askopenfilename(title="Pilih Audio", filetypes=[("Audio", "*.wav;*.mp3;*.ogg;*.flac"), ("Semua", "*.*")])
                if p:
                    v.set(p); e.delete(0,"end"); e.insert(0,p)
            ctk.CTkButton(row, text="📂", width=44, command=pick).pack(side="left", padx=6)
            def test(v=var):
                self._play_test(v.get())
            ctk.CTkButton(row, text="▶", width=44, command=test).pack(side="left")
            self._qs_vars[key] = var

    def _play_test(self, path):
        if not path:
            messagebox.showinfo("Uji Putar", "Belum ada file audio yang dipilih.")
            return
        if not HAVE_PYGAME:
            messagebox.showwarning("Audio", "Modul 'pygame' belum terpasang. Jalankan: pip install pygame")
            return
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
        except Exception:
            pass
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
        except Exception as e:
            messagebox.showerror("Gagal Memutar", f"Gagal memutar file:\n{e}")

    def _save(self):
        # header
        self.cfg["header"]["school_name"] = self.ent_school.get().strip()
        self.cfg["header"]["school_address"] = self.ent_addr.get().strip()
        self.cfg["header"]["logo_path"] = self.logo_path.get().strip()
        self.cfg["header"]["font_size"] = int(self.spn_size.get())
        self.cfg["header"]["font_color"] = self.col_font.get()
        self.cfg["header"]["bg_color"] = self.col_bg.get()

        # running text
        self.cfg["running_text"]["bg_color"] = self.rt_bg.get()

        # clock
        self.cfg["clock"]["mode_24h"] = bool(self.var_24.get())
        self.cfg["clock"]["time_font_size"] = int(self.sl_time_size.get())
        self.cfg["clock"]["time_color"] = self.time_color.get()
        self.cfg["clock"]["date_font_size"] = int(self.sl_date_size.get())
        self.cfg["clock"]["date_color"] = self.date_color.get()

        # theme
        self.cfg["appearance"] = self.mode_opt.get()
        self.cfg["accent"] = self.accent_opt.get()

        # footer
        self.cfg.setdefault("footer", {})
        self.cfg["footer"]["show"] = bool(self.footer_show.get())
        self.cfg["footer"]["text"] = self.ent_footer_text.get().strip()
        self.cfg["footer"]["font_size"] = int(self.sl_footer_size.get())
        self.cfg["footer"]["font_color"] = self.footer_txt_color.get()
        self.cfg["footer"]["bg_color"] = self.footer_bg_color.get()

        # quick sounds
        qs = self.cfg.setdefault("quick_sounds", {})
        for k, var in self._qs_vars.items():
            qs[k] = var.get().strip()

        save_json(CFG_FILE, self.cfg)
        self.app.reload_config()
        self.destroy()

# -------------- Jadwal Dialog ---------------
class JadwalDialog(ctk.CTkToplevel):
    def __init__(self, master, data=None):
        super().__init__(master)
        self.title("Entri Jadwal")
        self.geometry("520x260")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        form = ctk.CTkFrame(self)
        form.pack(fill="both", expand=True, padx=12, pady=10)

        # ========== Jam (HH:MM) ==========
        ctk.CTkLabel(form, text="Jam (HH:MM)").grid(row=0, column=0, sticky="w", pady=6)

        jam_box = ctk.CTkFrame(form, fg_color="transparent")
        jam_box.grid(row=0, column=1, columnspan=3, sticky="w")

        self.ent_hh = ctk.CTkEntry(jam_box, width=48, justify="center")
        self.ent_hh.pack(side="left")
        ctk.CTkLabel(jam_box, text=":").pack(side="left", padx=4)
        self.ent_mm = ctk.CTkEntry(jam_box, width=48, justify="center")
        self.ent_mm.pack(side="left")

        vcmd = (self.register(self._only_2digits), "%P")
        self.ent_hh.configure(validate="key", validatecommand=vcmd)
        self.ent_mm.configure(validate="key", validatecommand=vcmd)
        self.ent_hh.bind("<KeyRelease>", self._auto_to_mm)
        self.ent_mm.bind("<KeyRelease>", self._auto_to_ket)

        # ========== Keterangan ==========
        ctk.CTkLabel(form, text="Keterangan").grid(row=1, column=0, sticky="w", pady=6)
        self.ent_ket = ctk.CTkEntry(form)
        self.ent_ket.grid(row=1, column=1, columnspan=3, sticky="we", pady=6)

        # ========== File Audio ==========
        ctk.CTkLabel(form, text="File Audio").grid(row=2, column=0, sticky="w", pady=6)
        self.var_audio = tk.StringVar(value="")
        self.ent_audio = ctk.CTkEntry(form)
        self.ent_audio.grid(row=2, column=1, sticky="we", pady=6)
        ctk.CTkButton(form, text="📂", width=48, command=self._pick_audio).grid(row=2, column=2, padx=6, pady=6)

        # ========== Tombol ==========
        btns = ctk.CTkFrame(form, fg_color="transparent")
        btns.grid(row=3, column=0, columnspan=3, pady=12)
        ctk.CTkButton(btns, text="Batal", command=self.destroy, width=90).pack(side="right", padx=6)
        ctk.CTkButton(btns, text="Simpan", command=self._ok, width=90).pack(side="right")

        form.columnconfigure(1, weight=1)

        if data:
            try:
                hh, mm = (data.get("jam","").split(":") + ["",""])[:2]
            except Exception:
                hh, mm = "", ""
            self.ent_hh.insert(0, hh)
            self.ent_mm.insert(0, mm)
            self.ent_ket.insert(0, data.get("keterangan",""))
            self.var_audio.set(data.get("audio",""))
            self.ent_audio.delete(0, "end"); self.ent_audio.insert(0, self.var_audio.get())

        self.result = None

    def _only_2digits(self, P: str) -> bool:
        return (P == "") or (P.isdigit() and len(P) <= 2)

    def _auto_to_mm(self, _):
        val = self.ent_hh.get()
        if len(val) == 2:
            if val.isdigit() and 0 <= int(val) <= 23:
                self.ent_mm.focus_set()
                self.ent_mm.select_range(0, "end")
            else:
                messagebox.showwarning("Format Salah", "Jam (HH) harus 00–23.")
                self.ent_hh.focus_set()
                self.ent_hh.select_range(0, "end")

    def _auto_to_ket(self, _):
        val = self.ent_mm.get()
        if len(val) == 2 and val.isdigit() and 0 <= int(val) <= 59:
            self.ent_ket.focus_set()

    def _pick_audio(self):
        p = filedialog.askopenfilename(
            title="Pilih Audio",
            filetypes=[("Audio", "*.wav;*.mp3;*.ogg;*.flac"), ("Semua", "*.*")]
        )
        if p:
            self.var_audio.set(p)
            self.ent_audio.delete(0, "end")
            self.ent_audio.insert(0, p)

    def _ok(self):
        hh = self.ent_hh.get().strip()
        mm = self.ent_mm.get().strip()
        ket = self.ent_ket.get().strip()
        aud = self.ent_audio.get().strip()

        if not (hh and mm and ket and aud):
            messagebox.showwarning("Input Tidak Lengkap", "Semua field wajib diisi.")
            return
        if not (hh.isdigit() and 0 <= int(hh) <= 23):
            messagebox.showwarning("Format Salah", "Jam (HH) harus 00–23.")
            self.ent_hh.focus_set(); return
        if not (mm.isdigit() and 0 <= int(mm) <= 59):
            messagebox.showwarning("Format Salah", "Menit (MM) harus 00–59.")
            self.ent_mm.focus_set(); return

        self.result = {
            "jam": f"{int(hh):02d}:{int(mm):02d}",
            "keterangan": ket.upper(),
            "audio": aud
        }
        self.destroy()

# -------------- Main App -------------------
class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Load data
        self.cfg = load_json(CFG_FILE, DEFAULT_CFG)
        self.jadwal = load_json(JADWAL_FILE, DEFAULT_JADWAL)

        # Apply appearance
        ctk.set_appearance_mode(self.cfg.get("appearance","System"))
        ctk.set_default_color_theme(self.cfg.get("accent","blue"))

        # Init audio
        self._init_audio()

        self.title(APP_NAME)
        self.geometry("1120x720")
        self.minsize(980, 620)

        # Header
        self._build_header()

        # Marquee
        rt = self.cfg.get("running_text",{})
        self.marquee = Marquee(self, get_items=lambda: self.cfg.get("running_text",{}).get("items",[]),
                               height=36, bg=rt.get("bg_color","#000000"))
        self.marquee.pack(fill="x", padx=12, pady=(6,8))

        # Clock & Date
        self._build_clock_row()

        # Control bar (indicator + quick buttons)
        self._build_control_bar()

        # Tabs jadwal
        self._build_tabs()

        # Footer
        self._build_footer()

        # Auto-bell memory
        self._played_marks = set()  # berisi string "YYYY-MM-DD HH:MM|path"
        self._tick_clock()
        self._schedule_loop()

    # -------- Audio helpers --------
    def _init_audio(self):
        self.audio_ok = False
        if HAVE_PYGAME:
            try:
                pygame.mixer.init()
                self.audio_ok = True
            except Exception:
                self.audio_ok = False

    def play_audio(self, path):
        if not path:
            messagebox.showinfo("Audio", "File audio belum dipilih.")
            return
        if not self.audio_ok:
            messagebox.showwarning("Audio", "Audio belum siap. Pastikan 'pygame' terpasang dan tidak ada aplikasi lain yang memonopoli device audio.")
            return
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
        except Exception:
            pass
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
        except Exception as e:
            messagebox.showerror("Gagal Memutar", f"Gagal memutar file:\n{e}")

    def stop_audio(self):
        if self.audio_ok:
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass

    # -------- UI build parts --------
    def _build_header(self):
        h = self.cfg.get("header",{})
        self.header = ctk.CTkFrame(self, corner_radius=0)
        self.header.pack(fill="x")
        self.header.configure(fg_color=h.get("bg_color","#1f2937"))

        # left: logo
        self.logo_label = ctk.CTkLabel(self.header, text="")
        self.logo_label.pack(side="left", padx=(12,10), pady=10)
        self._load_logo(h.get("logo_path",""))

        # middle: texts
        text_box = ctk.CTkFrame(self.header, fg_color="transparent")
        text_box.pack(side="left", fill="both", expand=True, pady=6)
        self.var_school = tk.StringVar(value=h.get("school_name",""))
        self.var_addr = tk.StringVar(value=h.get("school_address",""))
        self.lbl_school = ctk.CTkLabel(text_box, textvariable=self.var_school,
                                       font=ctk.CTkFont(size=int(h.get("font_size",22)), weight="bold"),
                                       text_color=h.get("font_color","#ffffff"))
        self.lbl_school.pack(anchor="w")
        self.lbl_addr = ctk.CTkLabel(text_box, textvariable=self.var_addr,
                                     font=ctk.CTkFont(size=max(12,int(h.get("font_size",22))-6)),
                                     text_color="#d1d5db")
        self.lbl_addr.pack(anchor="w")

        # right: settings + switch
        right = ctk.CTkFrame(self.header, fg_color="transparent")
        right.pack(side="right", padx=10, pady=10)
        ctk.CTkButton(right, text="Pengaturan", command=self.open_settings, width=120).pack(side="right", padx=(6,0))
        self.bell_enabled = tk.BooleanVar(value=self.cfg.get("app",{}).get("auto_bell_enabled", True))
        ctk.CTkSwitch(right, text="ON/OF", variable=self.bell_enabled, command=self._toggle_bell).pack(side="right", padx=12)

    def _build_clock_row(self):
        c = self.cfg.get("clock",{})
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=12)
        self.lbl_time = ctk.CTkLabel(row, text="00:00:00",
                                     font=ctk.CTkFont(size=int(c.get("time_font_size",44)), weight="bold"),
                                     text_color=c.get("time_color","#10B981"))
        self.lbl_time.pack(side="left", padx=(6,16))
        self.lbl_date = ctk.CTkLabel(row, text="", font=ctk.CTkFont(size=int(c.get("date_font_size",16))),
                                     text_color=c.get("date_color","#d1d5db"))
        self.lbl_date.pack(side="left")

    def _build_control_bar(self):
        ctrl = ctk.CTkFrame(self, fg_color="transparent")
        ctrl.pack(fill="x", padx=12, pady=(2,0))

        # indicator hari
        hari_map = {0:"Senin",1:"Selasa",2:"Rabu",3:"Kamis",4:"Jumat",5:"Sabtu",6:"Minggu"}
        hari_ini = hari_map[datetime.today().weekday()]
        self.lbl_indicator = ctk.CTkLabel(ctrl, text=f"📅 Hari ini: {hari_ini}", text_color="#a3e635")
        self.lbl_indicator.pack(side="left", padx=6)

        spacer = ctk.CTkLabel(ctrl, text="")  # spacer grow
        spacer.pack(side="left", fill="x", expand=True)

        # Quick buttons on right: ℹ, 1..10, Stop
        qb = ctk.CTkFrame(ctrl, fg_color="transparent")
        qb.pack(side="right")

        # INFO
        ctk.CTkButton(qb, text="ℹ", width=36, command=lambda: self._play_quick("info")).pack(side="left", padx=(0,6))
        # 1..10
        for i in range(1, 11):
            ctk.CTkButton(qb, text=f"{i}", width=32, command=lambda k=f"btn{i}": self._play_quick(k)).pack(side="left", padx=2)
        # Stop
        ctk.CTkButton(qb, text="⏹", width=40, command=self.stop_audio).pack(side="left", padx=(8,0))

    def _build_tabs(self):
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=12, pady=8)

        style = ttk.Style(self.nb)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        # keep table compact
        def _tree_theme():
            mode = ctk.get_appearance_mode()
            if mode == "Dark":
                bg = "#0f172a"; fg="#e5e7eb"; select="#334155"; hdr="#1f2937"
            else:
                bg = "#ffffff"; fg="#111827"; select="#e5e7eb"; hdr="#f3f4f6"
            style.configure("Treeview", background=bg, fieldbackground=bg, foreground=fg,
                            rowheight=26, font=("Segoe UI", 12))
            style.map("Treeview", background=[("selected", select)])
            style.configure("Treeview.Heading", background=hdr, foreground=fg, font=("Segoe UI Semibold", 13))
            style.configure("TNotebook.Tab", padding=[12, 6], font=("Segoe UI", 14, "bold"))
        _tree_theme()
        self.bind("<<ThemeChanged>>", lambda e: _tree_theme())

        self.tables = {}
        for hari in HARI_LIST:
            tab = ctk.CTkFrame(self.nb, fg_color="transparent")
            self.nb.add(tab, text=hari)
            self._build_day_table(tab, hari)

        # auto-select today's tab if exists
        hari_map = {0:"Senin",1:"Selasa",2:"Rabu",3:"Kamis",4:"Jumat",5:"Sabtu",6:"Minggu"}
        hari_ini = hari_map[datetime.today().weekday()]
        if hari_ini in HARI_LIST:
            idx = HARI_LIST.index(hari_ini)
            self.nb.select(idx)

    def _build_day_table(self, parent, hari):
        area = ctk.CTkFrame(parent, fg_color="transparent")
        area.pack(fill="both", expand=True)

        # height kecil agar app tidak terlalu tinggi
        tree = ttk.Treeview(area, columns=("jam","ket","audio"), show="headings", height=10)
        tree.heading("jam", text="Jam"); tree.column("jam", width=110, anchor="center")
        tree.heading("ket", text="Keterangan"); tree.column("ket", width=340, anchor="w")
        tree.heading("audio", text="File Audio"); tree.column("audio", width=460, anchor="w")
        tree.pack(fill="both", expand=True, padx=4, pady=4)

        for it in sorted(self.jadwal.get(hari, []), key=lambda x: x.get("jam","00:00")):
            tree.insert("", "end", values=(it.get("jam",""), it.get("keterangan",""), it.get("audio","")))

        btns = ctk.CTkFrame(area, fg_color="transparent")
        btns.pack(fill="x", pady=6)
        ctk.CTkButton(btns, text="Tambah", command=lambda h=hari: self._jadwal_add(h)).pack(side="left")
        ctk.CTkButton(btns, text="Edit", command=lambda h=hari: self._jadwal_edit(h)).pack(side="left", padx=6)
        ctk.CTkButton(btns, text="Hapus", command=lambda h=hari: self._jadwal_del(h)).pack(side="left")

        self.tables[hari] = tree

    # -------- actions ----------
    def _load_logo(self, path, size=(72,72)):
        if not path or not Path(path).exists():
            self.logo_label.configure(text="No Logo", image="")
            return
        try:
            img = Image.open(path).convert("RGBA")
            img.thumbnail(size, Image.LANCZOS)
            self._logo_imgtk = ImageTk.PhotoImage(img)
            self.logo_label.configure(image=self._logo_imgtk, text="")
        except Exception:
            self.logo_label.configure(text="No Logo", image="")

    def _tick_clock(self):
        c = self.cfg.get("clock",{})
        t = time.localtime()
        s_time = time.strftime("%H:%M:%S" if c.get("mode_24h",True) else "%I:%M:%S %p", t)
        self.lbl_time.configure(text=s_time)

        day_name_id = {'Monday':'Senin','Tuesday':'Selasa','Wednesday':'Rabu','Thursday':'Kamis','Friday':'Jumat','Saturday':'Sabtu','Sunday':'Minggu'}
        month_name_id = {'January':'Januari','February':'Februari','March':'Maret','April':'April','May':'Mei','June':'Juni','July':'Juli','August':'Agustus','September':'September','October':'Oktober','November':'November','December':'Desember'}
        eng_day = time.strftime('%A', t); eng_month = time.strftime('%B', t)
        s_date = f"{day_name_id.get(eng_day, eng_day)}, {time.strftime('%d', t)} {month_name_id.get(eng_month, eng_month)} {time.strftime('%Y', t)}"
        self.lbl_date.configure(text=s_date)
        self.after(500, self._tick_clock)

    def _toggle_bell(self):
        self.cfg.setdefault("app", {})["auto_bell_enabled"] = bool(self.bell_enabled.get())
        save_json(CFG_FILE, self.cfg)

    def _jadwal_add(self, hari):
        dlg = JadwalDialog(self)
        self.wait_window(dlg)
        if dlg.result:
            self.jadwal[hari].append(dlg.result)
            self._refresh_day(hari)
            save_json(JADWAL_FILE, self.jadwal)

    def _jadwal_edit(self, hari):
        tree = self.tables[hari]
        sel = tree.selection()
        if not sel: return
        idx = tree.index(sel[0])
        data = self.jadwal[hari][idx]
        dlg = JadwalDialog(self, data)
        self.wait_window(dlg)
        if dlg.result:
            self.jadwal[hari][idx] = dlg.result
            self._refresh_day(hari)
            save_json(JADWAL_FILE, self.jadwal)

    def _jadwal_del(self, hari):
        tree = self.tables[hari]
        sel = tree.selection()
        if not sel: return
        idx = tree.index(sel[0])
        del self.jadwal[hari][idx]
        self._refresh_day(hari)
        save_json(JADWAL_FILE, self.jadwal)

    def _refresh_day(self, hari):
        tree = self.tables[hari]
        for i in tree.get_children():
            tree.delete(i)
        for it in sorted(self.jadwal.get(hari, []), key=lambda x: x.get("jam","00:00")):
            tree.insert("", "end", values=(it.get("jam",""), it.get("keterangan",""), it.get("audio","")))

    def open_settings(self):
        SettingsWindow(self)

    def reload_config(self):
        # re-load & re-apply
        self.cfg = load_json(CFG_FILE, DEFAULT_CFG)
        ctk.set_appearance_mode(self.cfg.get("appearance","System"))
        ctk.set_default_color_theme(self.cfg.get("accent","blue"))

        h = self.cfg.get("header",{})
        self.header.configure(fg_color=h.get("bg_color","#1f2937"))
        self._load_logo(h.get("logo_path",""))
        self.var_school.set(h.get("school_name",""))
        self.var_addr.set(h.get("school_address",""))
        self.lbl_school.configure(font=ctk.CTkFont(size=int(h.get("font_size",22)), weight="bold"),
                                  text_color=h.get("font_color","#ffffff"))

        # marquee
        self.marquee.set_bg(self.cfg.get("running_text",{}).get("bg_color","#000000"))

        # clock
        c = self.cfg.get("clock",{})
        self.lbl_time.configure(font=ctk.CTkFont(size=int(c.get("time_font_size",44)), weight="bold"),
                                text_color=c.get("time_color","#10B981"))
        self.lbl_date.configure(font=ctk.CTkFont(size=int(c.get("date_font_size",16))),
                                text_color=c.get("date_color","#d1d5db"))

        # footer
        f = self.cfg.get("footer", {})
        self.footer.configure(fg_color=f.get("bg_color", "transparent"))
        self.lbl_footer.configure(text=f.get("text",""),
                                  font=ctk.CTkFont(size=int(f.get("font_size",12))),
                                  text_color=f.get("font_color", "#9CA3AF"))
        if f.get("show", True):
            if not self.footer.winfo_manager():
                self.footer.pack(fill="x", padx=12, pady=(0,12))
        else:
            self.footer.pack_forget()

    # ---- Footer UI ----
    def _build_footer(self):
        f = self.cfg.get("footer", {})
        self.footer = ctk.CTkFrame(self, fg_color=f.get("bg_color", "transparent"))
        self.footer.pack(fill="x", padx=12, pady=(0,12))
        self.lbl_footer = ctk.CTkLabel(self.footer,
            text=f.get("text", "© 2025 Nama Sekolah. All rights reserved."),
            font=ctk.CTkFont(size=int(f.get("font_size",12))),
            text_color=f.get("font_color", "#9CA3AF")
        )
        self.lbl_footer.pack(side="left", padx=6, pady=6)
        if not f.get("show", True):
            self.footer.pack_forget()

    # ---- Quick play from top-right buttons ----
    def _play_quick(self, key):
        path = self.cfg.get("quick_sounds", {}).get(key, "")
        if not path:
            # fallback: untuk "info", jika kosong—beri info
            label = "Informasi" if key == "info" else key.upper()
            messagebox.showinfo("Audio", f"Belum ada file audio untuk '{label}'. Buka Pengaturan → Informasi & Tombol.")
            return
        self.play_audio(path)

    # ---- Auto-bell scheduler ----
    def _schedule_loop(self):
        # dijalankan via after setiap 1s
        try:
            if self.bell_enabled.get():
                now = datetime.now()
                key_minute = now.strftime("%Y-%m-%d %H:%M")

                # pilih hari sesuai tab / kalender
                hari_map_py = {0:"Senin",1:"Selasa",2:"Rabu",3:"Kamis",4:"Jumat",5:"Sabtu",6:"Minggu"}
                hari_ini = hari_map_py[now.weekday()]
                active_day = hari_ini if hari_ini in HARI_LIST else "Senin"

                # cek jadwal
                for it in self.jadwal.get(active_day, []):
                    jam = it.get("jam","")
                    aud = it.get("audio","")
                    if jam and aud:
                        mark = f"{key_minute}|{aud}"
                        if (jam == now.strftime("%H:%M")) and (mark not in self._played_marks):
                            self._played_marks.add(mark)
                            self.play_audio(aud)
            else:
                # jika OFF, tidak melakukan apa-apa
                pass
        finally:
            # bersihkan mark hari kemarin agar set tidak membengkak
            self._cleanup_marks()
            self.after(1000, self._schedule_loop)

    def _cleanup_marks(self):
        # hapus entry bukan hari ini
        today = date.today().strftime("%Y-%m-%d")
        to_del = [m for m in self._played_marks if not m.startswith(today)]
        for m in to_del:
            self._played_marks.discard(m)

# -------------- MAIN -----------------
if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
