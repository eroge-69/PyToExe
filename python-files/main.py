\
import os
import sys
import json
import threading
import datetime as dt
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter import PhotoImage
import platform

# Audio via pygame
import pygame

# Exporters
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.lib.units import cm
from PIL import Image

# Tray icon
try:
    import pystray
except Exception:
    pystray = None

APP_TITLE = "School Bell - Windows"
DATA_FILE = "schedule.json"
DEFAULT_BELL_DURATION_SEC = 120  # 2 minutes
WARNING_BEFORE_MIN = 5

DAYS = ["Senin","Selasa","Rabu","Kamis","Jumat","Sabtu"]
PERIODS = [f"JP{i}" for i in range(1,10)]  # JP1..JP9

def resource_path(rel):
    # For PyInstaller bundle
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, rel)

ASSETS_DIR = resource_path("assets")
DEFAULT_BELL = os.path.join(ASSETS_DIR, "sample_bell.wav")
DEFAULT_WARNING = os.path.join(ASSETS_DIR, "sample_warning.wav")
ICON_PATH = os.path.join(ASSETS_DIR, "bell_icon.png")

class BellPlayer:
    def __init__(self):
        pygame.mixer.init()
        self.current_channel = None
        self.stop_timer = None
        self.volume = 0.7
        pygame.mixer.music.set_volume(self.volume)

    def set_volume(self, v):
        self.volume = max(0.0, min(1.0, v))
        pygame.mixer.music.set_volume(self.volume)

    def play_file(self, path, duration=DEFAULT_BELL_DURATION_SEC):
        try:
            if self.stop_timer and self.stop_timer.is_alive():
                self.stop_playback()

            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
            self.stop_timer = threading.Timer(duration, self.stop_playback)
            self.stop_timer.start()
        except Exception as e:
            messagebox.showerror("Gagal Memutar", f"Tidak bisa memutar file:\n{path}\n\n{e}")

    def stop_playback(self):
        try:
            pygame.mixer.music.stop()
        except:
            pass

class Scheduler:
    def __init__(self, app):
        self.app = app
        self.thread = None
        self.stop_flag = threading.Event()

    def start(self):
        if self.thread and self.thread.is_alive():
            return
        self.stop_flag.clear()
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_flag.set()

    def run(self):
        while not self.stop_flag.is_set():
            now = dt.datetime.now()
            day_idx = now.weekday()  # 0=Mon
            if day_idx <= 5:  # Senin..Sabtu
                day_name = DAYS[day_idx]
                entries = self.app.state["schedule"].get(day_name, [])
                for e in entries:
                    try:
                        start = dt.datetime.strptime(e["start"], "%H:%M").time()
                    except:
                        continue
                    start_dt = now.replace(hour=start.hour, minute=start.minute, second=0, microsecond=0)
                    warn_dt = start_dt - dt.timedelta(minutes=WARNING_BEFORE_MIN)

                    # Warning 5 minutes before
                    if abs((now - warn_dt).total_seconds()) < 1.0 and e.get("type","period") == "period":
                        self.app.warn_before_period(day_name, e)

                    # Start of entry
                    if abs((now - start_dt).total_seconds()) < 1.0:
                        self.app.start_entry(day_name, e)

            self.stop_flag.wait(1.0)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1150x720")
        self.resizable(True, True)

        self.icon_img = None
        if os.path.exists(ICON_PATH):
            try:
                self.icon_img = tk.PhotoImage(file=ICON_PATH)
                self.iconphoto(False, self.icon_img)
            except:
                pass

        self.player = BellPlayer()
        # state now supports "type": "period" or "break"
        default_day = []
        for i in range(9):
            default_day.append({"type":"period","label":PERIODS[i], "start":"07:00","end":"07:45","music": ""})
        self.state = {
            "school_name": "Nama Sekolah",
            "kop_text": "Alamat/Telepon/Website",
            "kop_logo": "",  # path
            "schedule": {d: json.loads(json.dumps(default_day)) for d in DAYS},
            "warning_sound": DEFAULT_WARNING,
            "default_bell": DEFAULT_BELL,
            "autostart": False,
            "volume": 0.7
        }
        self.load_state()

        self.scheduler = Scheduler(self)

        self.build_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Minimize-to-tray support
        self.tray_icon = None
        self.bind("<Unmap>", self.on_minimize)

    # ---------- Persistence ----------
    def load_state(self):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
                # Backward compatibility: if entries lack "type", treat as period
                for d, arr in raw.get("schedule", {}).items():
                    for e in arr:
                        if "type" not in e:
                            e["type"] = "period"
                self.state.update(raw)
        except:
            pass

    def save_state(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Gagal Menyimpan", str(e))

    # ---------- UI ----------
    def build_ui(self):
        top = ttk.Frame(self)
        top.pack(fill="x", padx=10, pady=8)

        ttk.Label(top, text="Nama Sekolah:").pack(side="left")
        self.school_var = tk.StringVar(value=self.state["school_name"])
        ttk.Entry(top, textvariable=self.school_var, width=40).pack(side="left", padx=6)

        ttk.Label(top, text="Kop (teks):").pack(side="left", padx=(16,0))
        self.kop_var = tk.StringVar(value=self.state["kop_text"])
        ttk.Entry(top, textvariable=self.kop_var, width=40).pack(side="left", padx=6)

        ttk.Button(top, text="Pilih Logo Kop...", command=self.choose_logo).pack(side="left", padx=6)

        # Tabs per hari
        self.notebook = ttk.Notebook(self)
        self.tabs = {}
        for day in DAYS:
            tab = ttk.Frame(self.notebook)
            self.build_day_tab(tab, day)
            self.notebook.add(tab, text=day)
            self.tabs[day] = tab
        self.notebook.pack(fill="both", expand=True, padx=10, pady=8)

        bottom = ttk.Frame(self)
        bottom.pack(fill="x", padx=10, pady=8)

        self.volume = tk.DoubleVar(value=self.state.get("volume",0.7))
        ttk.Label(bottom, text="Volume:").pack(side="left")
        vol = ttk.Scale(bottom, from_=0.0, to=1.0, variable=self.volume, command=self.on_volume)
        vol.pack(side="left", padx=6, fill="x", expand=True)

        ttk.Button(bottom, text="Bunyikan Bel Sekarang", command=self.manual_ring).pack(side="left", padx=6)
        ttk.Button(bottom, text="Cetak/Ekspor Jadwal (DOCX/PDF)", command=self.export_all).pack(side="left", padx=6)
        ttk.Button(bottom, text="Mulai Penjadwalan", command=self.scheduler.start).pack(side="left", padx=6)
        ttk.Button(bottom, text="Hentikan Penjadwalan", command=self.scheduler.stop).pack(side="left", padx=6)

        self.autostart_var = tk.BooleanVar(value=self.state.get("autostart", False))
        ttk.Checkbutton(bottom, text="Auto Start saat Booting Windows", variable=self.autostart_var, command=self.toggle_autostart).pack(side="left", padx=6)

    def build_day_tab(self, parent, day):
        frm = ttk.Frame(parent)
        frm.pack(fill="both", expand=True, padx=6, pady=6)

        # Buttons
        tools = ttk.Frame(frm)
        tools.pack(fill="x", pady=4)
        ttk.Button(tools, text=f"Salin {day} ke...", command=lambda d=day: self.copy_day_to(d)).pack(side="left")
        ttk.Button(tools, text=f"Ekspor {day} ke Word", command=lambda d=day: self.export_day_docx(d)).pack(side="left", padx=6)
        ttk.Button(tools, text=f"Tambah Istirahat", command=lambda d=day: self.add_break_after_selection(d)).pack(side="left", padx=6)
        ttk.Button(tools, text=f"Hapus Baris", command=lambda d=day: self.delete_row(d)).pack(side="left", padx=6)

        cols = ("Tipe","JP/Istirahat","Mulai","Selesai","Musik")
        tree = ttk.Treeview(frm, columns=cols, show="headings", height=14)
        widths = (110,100,120,120,660)
        for c, w in zip(cols, widths):
            tree.heading(c, text=c)
            tree.column(c, width=w, anchor="center" if c not in ("Musik",) else "w")
        tree.pack(fill="both", expand=True)

        # Populate
        for e in self.state["schedule"][day]:
            lab = e["label"]
            tree.insert("", "end", values=("Istirahat" if e.get("type")=="break" else "Pelajaran", lab, e["start"], e["end"], e["music"] or "-"))

        # Editor row
        editor = ttk.Frame(frm)
        editor.pack(fill="x", pady=6)

        ttk.Label(editor, text="Pilih Baris:").grid(row=0, column=0, padx=4, pady=2)
        ttk.Button(editor, text="Ubah Waktu", command=lambda d=day,t=tree: self.edit_time(d,t)).grid(row=0, column=1, padx=4)
        ttk.Button(editor, text="Pilih Musik", command=lambda d=day,t=tree: self.choose_music(d,t)).grid(row=0, column=2, padx=4)
        ttk.Button(editor, text="Hapus Musik", command=lambda d=day,t=tree: self.clear_music(d,t)).grid(row=0, column=3, padx=4)

        ttk.Button(editor, text="Uji Putar Musik", command=lambda d=day,t=tree: self.test_play(d,t)).grid(row=0, column=4, padx=16)

        parent.tree = tree  # keep reference

    def refresh_day(self, day):
        tab = self.tabs[day]
        tree = tab.tree
        for i in tree.get_children():
            tree.delete(i)
        for e in self.state["schedule"][day]:
            tree.insert("", "end", values=("Istirahat" if e.get("type")=="break" else "Pelajaran", e["label"], e["start"], e["end"], e["music"] or "-"))

    # ---------- Actions ----------
    def choose_logo(self):
        path = filedialog.askopenfilename(title="Pilih Logo (PNG/JPG)", filetypes=[("Images","*.png;*.jpg;*.jpeg")])
        if path:
            self.state["kop_logo"] = path
            self.save_state()

    def on_volume(self, _evt=None):
        self.player.set_volume(self.volume.get())
        self.state["volume"] = self.volume.get()
        self.save_state()

    def get_selected_row_index(self, day, tree):
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Pilih Baris", "Silakan pilih baris JP/Istirahat terlebih dahulu.")
            return None
        item = tree.item(sel[0])
        label = item["values"][1]
        # locate index by label + time if duplicates
        arr = self.state["schedule"][day]
        for i, e in enumerate(arr):
            if e["label"] == label and item["values"][2] == e["start"] and item["values"][3] == e["end"]:
                return i
        # fallback by label only
        for i, e in enumerate(arr):
            if e["label"] == label:
                return i
        return None

    def edit_time(self, day, tree):
        idx = self.get_selected_row_index(day, tree)
        if idx is None: return
        e = self.state["schedule"][day][idx]

        win = tk.Toplevel(self)
        win.title(f"Ubah Waktu - {day} {e['label']}")
        ttk.Label(win, text="Mulai (HH:MM)").grid(row=0,column=0,padx=6,pady=6)
        ttk.Label(win, text="Selesai (HH:MM)").grid(row=1,column=0,padx=6,pady=6)
        sv = tk.StringVar(value=e["start"])
        ev = tk.StringVar(value=e["end"])
        ttk.Entry(win, textvariable=sv).grid(row=0,column=1,padx=6,pady=6)
        ttk.Entry(win, textvariable=ev).grid(row=1,column=1,padx=6,pady=6)
        def ok():
            self.state["schedule"][day][idx]["start"] = sv.get()
            self.state["schedule"][day][idx]["end"] = ev.get()
            self.save_state()
            self.refresh_day(day)
            win.destroy()
        ttk.Button(win, text="Simpan", command=ok).grid(row=2,column=0,columnspan=2,pady=8)

    def choose_music(self, day, tree):
        idx = self.get_selected_row_index(day, tree)
        if idx is None: return
        path = filedialog.askopenfilename(title="Pilih Musik", filetypes=[("Audio","*.mp3;*.wav;*.ogg;*.flac;*.m4a;*.aac;*.wma")])
        if path:
            self.state["schedule"][day][idx]["music"] = path
            self.save_state()
            self.refresh_day(day)

    def clear_music(self, day, tree):
        idx = self.get_selected_row_index(day, tree)
        if idx is None: return
        self.state["schedule"][day][idx]["music"] = ""
        self.save_state()
        self.refresh_day(day)

    def test_play(self, day, tree):
        idx = self.get_selected_row_index(day, tree)
        if idx is None: return
        path = self.state["schedule"][day][idx]["music"] or self.state["default_bell"]
        self.player.play_file(path)

    def add_break_after_selection(self, day):
        tab = self.tabs[day]
        tree = tab.tree
        idx = self.get_selected_row_index(day, tree)
        if idx is None:
            messagebox.showwarning("Pilih Baris", "Pilih baris untuk menyisipkan istirahat setelahnya.")
            return
        # default 15 minutes break, start = end of selected
        selected = self.state["schedule"][day][idx]
        start = selected.get("end","")
        # guess end time +15
        try:
            t = dt.datetime.strptime(start, "%H:%M")
            end = (t + dt.timedelta(minutes=15)).strftime("%H:%M")
        except:
            end = start
        new_row = {"type":"break","label":"Istirahat","start":start, "end":end, "music": ""}
        self.state["schedule"][day].insert(idx+1, new_row)
        self.save_state()
        self.refresh_day(day)

    def delete_row(self, day):
        tab = self.tabs[day]
        tree = tab.tree
        idx = self.get_selected_row_index(day, tree)
        if idx is None: return
        del self.state["schedule"][day][idx]
        self.save_state()
        self.refresh_day(day)

    def copy_day_to(self, from_day):
        win = tk.Toplevel(self)
        win.title(f"Salin {from_day} ke...")
        ttk.Label(win, text="Pilih target hari:").pack(padx=10,pady=10)
        target = tk.StringVar()
        cb = ttk.Combobox(win, values=[d for d in DAYS if d!=from_day], textvariable=target, state="readonly")
        cb.pack(padx=10,pady=6)
        def do_copy():
            tgt = target.get()
            if not tgt:
                return
            self.state["schedule"][tgt] = json.loads(json.dumps(self.state["schedule"][from_day]))
            self.save_state()
            self.refresh_day(tgt)
            messagebox.showinfo("Berhasil", f"Jadwal {from_day} disalin ke {tgt}.")
            win.destroy()
        ttk.Button(win, text="Salin", command=do_copy).pack(pady=10)

    def manual_ring(self):
        # Use default bell
        path = self.state.get("default_bell", DEFAULT_BELL)
        self.player.play_file(path)

    # ---------- Scheduling callbacks ----------
    def warn_before_period(self, day, entry):
        # Play warning tone and popup
        sound = self.state.get("warning_sound", DEFAULT_WARNING)
        try:
            self.player.play_file(sound, duration=3)  # short beep
        except:
            pass
        self.after(0, lambda: messagebox.showinfo("Peringatan", f"5 menit sebelum jam pelajaran ({day} {entry['label']})"))

    def start_entry(self, day, entry):
        # For both period & break
        path = entry.get("music") or self.state.get("default_bell", DEFAULT_BELL)
        self.player.play_file(path, duration=DEFAULT_BELL_DURATION_SEC)

    # ---------- Export ----------
    def export_day_docx(self, day):
        save_path = filedialog.asksaveasfilename(defaultextension=".docx", initialfile=f"Jadwal_{day}.docx",
                                                 filetypes=[("Word Document","*.docx")])
        if not save_path:
            return
        self._export_docx(save_path, [day])
        messagebox.showinfo("Selesai", f"Dokumen tersimpan:\n{save_path}")

    def export_all(self):
        folder = filedialog.askdirectory(title="Pilih folder simpan")
        if not folder:
            return
        docx_path = os.path.join(folder, "Jadwal_Sekolah_AllDays.docx")
        pdf_path = os.path.join(folder, "Jadwal_Sekolah_AllDays.pdf")
        self._export_docx(docx_path, DAYS)
        self._export_pdf(pdf_path, DAYS)
        messagebox.showinfo("Selesai", f"Tersimpan:\n{docx_path}\n{pdf_path}")

    def _export_docx(self, path, day_list):
        doc = Document()
        # Header with logo + text
        table = doc.add_table(rows=1, cols=2)
        row = table.rows[0]
        cell_logo, cell_text = row.cells
        if self.state.get("kop_logo") and os.path.exists(self.state["kop_logo"]):
            try:
                cell_logo.paragraphs[0].add_run().add_picture(self.state["kop_logo"], width=Inches(1.2))
            except:
                cell_logo.text = ""
        else:
            cell_logo.text = ""

        p = cell_text.paragraphs[0]
        run = p.add_run(self.school_var.get())
        run.bold = True
        run.font.size = Pt(16)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p2 = cell_text.add_paragraph(self.kop_var.get())
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph("")

        for day in day_list:
            doc.add_heading(day, level=2)
            t = doc.add_table(rows=1, cols=5)
            hdr = t.rows[0].cells
            hdr[0].text = "Tipe"
            hdr[1].text = "JP/Istirahat"
            hdr[2].text = "Mulai"
            hdr[3].text = "Selesai"
            hdr[4].text = "Musik"
            for e in self.state["schedule"][day]:
                row = t.add_row().cells
                row[0].text = "Istirahat" if e.get("type")=="break" else "Pelajaran"
                row[1].text = e["label"]
                row[2].text = e["start"]
                row[3].text = e["end"]
                row[4].text = os.path.basename(e["music"]) if e["music"] else "-"
            doc.add_paragraph("")
        doc.save(path)

    def _export_pdf(self, path, day_list):
        c = pdfcanvas.Canvas(path, pagesize=A4)
        W, H = A4

        def draw_header(y):
            x = 2*cm
            # Logo
            if self.state.get("kop_logo") and os.path.exists(self.state["kop_logo"]):
                try:
                    c.drawImage(self.state["kop_logo"], x, y-1.8*cm, width=2.8*cm, height=2.8*cm, preserveAspectRatio=True, mask='auto')
                except:
                    pass
            # Text
            c.setFont("Helvetica-Bold", 14)
            c.drawCentredString(W/2, y+0.5*cm, self.school_var.get())
            c.setFont("Helvetica", 10)
            c.drawCentredString(W/2, y-0.1*cm, self.kop_var.get())
            c.line(1.5*cm, y-0.5*cm, W-1.5*cm, y-0.5*cm)

        y = H - 2*cm
        draw_header(y)
        y -= 1.5*cm
        for day in day_list:
            c.setFont("Helvetica-Bold", 12)
            c.drawString(2*cm, y, day)
            y -= 0.5*cm
            # table header
            c.setFont("Helvetica-Bold", 10)
            c.drawString(2*cm, y, "Tipe")
            c.drawString(4.5*cm, y, "JP/Istirahat")
            c.drawString(8.0*cm, y, "Mulai")
            c.drawString(10.0*cm, y, "Selesai")
            c.drawString(12.0*cm, y, "Musik")
            y -= 0.4*cm
            c.setFont("Helvetica", 10)
            for e in self.state["schedule"][day]:
                c.drawString(2*cm, y, "Istirahat" if e.get("type")=="break" else "Pelajaran")
                c.drawString(4.5*cm, y, e["label"])
                c.drawString(8.0*cm, y, e["start"])
                c.drawString(10.0*cm, y, e["end"])
                music = os.path.basename(e["music"]) if e["music"] else "-"
                c.drawString(12.0*cm, y, music[:40])
                y -= 0.35*cm
                if y < 3*cm:
                    c.showPage()
                    y = H - 2*cm
                    draw_header(y)
                    y -= 1.5*cm
            y -= 0.3*cm
            if y < 3*cm:
                c.showPage()
                y = H - 2*cm
                draw_header(y)
                y -= 1.5*cm
        c.save()

    # ---------- Autostart ----------
    def toggle_autostart(self):
        want = self.autostart_var.get()
        try:
            if platform.system() == "Windows":
                import winreg
                run_key = r"Software\Microsoft\Windows\CurrentVersion\Run"
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, run_key, 0, winreg.KEY_SET_VALUE)
                app_name = "SchoolBellApp"
                exe_path = sys.executable
                if getattr(sys, 'frozen', False):
                    # Running as EXE
                    exe_path = sys.executable
                else:
                    # Running as script
                    exe_path = f'"{sys.executable}" "{os.path.abspath(__file__)}"'
                if want:
                    winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, exe_path)
                else:
                    try:
                        winreg.DeleteValue(key, app_name)
                    except FileNotFoundError:
                        pass
                winreg.CloseKey(key)
                self.state["autostart"] = want
                self.save_state()
                messagebox.showinfo("Auto Start", "Pengaturan auto start diperbarui.")
            else:
                messagebox.showwarning("Tidak Didukung", "Auto Start hanya untuk Windows.")
        except Exception as e:
            messagebox.showerror("Gagal Auto Start", str(e))

    # ---------- Tray ----------
    def on_minimize(self, event):
        if self.state is None:  # not ready
            return
        if self.state.get("minimize_to_tray", True) and self.state.get("tray_shown", False) is False and self.state.get("window_minimized", False) is False:
            # When minimized, hide window and show tray icon
            if self.state.get("window_minimized", False):
                return
        if self.state.get("minimize_to_tray", True) and self.state.get("window_minimized", False) is False and self.state.get("tray_shown", False) is False:
            if self.state.get("auto_tray_initialized", False) is False:
                self.after(100, self.show_tray_icon)

    def show_tray_icon(self):
        if pystray is None:
            return
        try:
            from PIL import Image
            image = Image.open(ICON_PATH) if os.path.exists(ICON_PATH) else Image.new("RGBA",(64,64),(255,255,0,255))
            menu = pystray.Menu(
                pystray.MenuItem("Buka Aplikasi", self.tray_open),
                pystray.MenuItem("Bunyikan Bel Sekarang", self.tray_ring),
                pystray.MenuItem("Keluar", self.tray_quit)
            )
            self.withdraw()
            self.state["window_minimized"] = True
            self.tray_icon = pystray.Icon("SchoolBell", image, "School Bell", menu)
            self.state["tray_shown"] = True
            threading.Thread(target=self.tray_icon.run, daemon=True).start()
        except Exception as e:
            # If tray fails, ignore
            pass

    def tray_open(self, icon, item):
        self.after(0, self.deiconify)
        if self.tray_icon:
            try:
                self.tray_icon.stop()
            except:
                pass
            self.tray_icon = None
        self.state["tray_shown"] = False
        self.state["window_minimized"] = False

    def tray_ring(self, icon, item):
        self.manual_ring()

    def tray_quit(self, icon, item):
        self.after(0, self.on_close)

    def on_close(self):
        # stop tray
        if self.tray_icon:
            try:
                self.tray_icon.stop()
            except:
                pass
            self.tray_icon = None
        self.scheduler.stop()
        self.save_state()
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()
