# -*- coding: utf-8 -*-
"""
PPTX -> JPG (placeholder-tekstin korvaus)
v6 — Projektin tallennus ja lataus
- Tiedosto-valikko: Uusi projekti, Avaa projekti…, Tallenna projekti, Tallenna nimellä…
- Projektit tallennetaan UTF-8 JSON-muodossa (*.pptjpgproj), sisältäen:
  * pohja-PPTX:n polku, tulostuskansio
  * placeholder-teksti, leveys (px)
  * Näytä PowerPoint, Sulje PowerPoint lopuksi
  * aiherivien lista
- Mukana v5:n parannukset (COM-sulku, SaveAs(ppSaveAsJPG)-fallback, polkujen normalisointi)
Vaatii: Windows + Microsoft PowerPoint + pywin32
"""
import gc
import os
import re
import json
import shutil
import tempfile
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

try:
    import win32com.client  # type: ignore
    import pythoncom  # type: ignore
except Exception:
    win32com = None
    pythoncom = None

APP_TITLE = "PPTX -> useita JPG-versioita (aihetekstillä)"
DEFAULT_FIND_TEXT = "Tähän aihe"
DEFAULT_WIDTH = 1920
PP_SAVE_AS_JPG = 17  # ppSaveAsJPG
PP_ALERTS_NONE = 1   # ppAlertsNone


def sanitize_filename(name: str) -> str:
    name = name.strip()
    name = re.sub(r'[<>:"/\\\\|?*]+', "_", name)
    name = re.sub(r"\\s+", " ", name)
    return name[:150] if len(name) > 150 else name


def to_win_path(p: str) -> str:
    p = os.path.abspath(p)
    return p.replace("/", "\\")


def ensure_output_dir(path_dir: str):
    path_dir = to_win_path(path_dir)
    os.makedirs(path_dir, exist_ok=True)
    testfile = os.path.join(path_dir, "_write_test.tmp")
    with open(testfile, "wb") as f:
        f.write(b"ok")
    os.remove(testfile)
    return path_dir


def log_safe(textbox: tk.Text, msg: str) -> None:
    textbox.configure(state="normal")
    textbox.insert("end", msg + "\n")
    textbox.see("end")
    textbox.configure(state="disabled")


def replace_text_in_shapes(shapes, find_text: str, replace_text: str) -> int:
    count_total = 0

    def _walk(items):
        nonlocal count_total
        for shp in items:
            try:
                if shp.Type == 6 and hasattr(shp, "GroupItems"):  # msoGroup
                    _walk(shp.GroupItems)
                elif getattr(shp, "HasTextFrame", 0) == -1 and shp.TextFrame.HasText == -1:
                    tr = shp.TextFrame.TextRange
                    count = tr.Replace(FindWhat=find_text, ReplaceWhat=replace_text,
                                       After=0, MatchCase=False, WholeWords=False)
                    count_total += int(count)
            except Exception:
                pass

    _walk(shapes)
    return count_total


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("980x640")

        # state
        self.pptx_path = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.find_text = tk.StringVar(value=DEFAULT_FIND_TEXT)
        self.width_px = tk.IntVar(value=DEFAULT_WIDTH)
        self.visible_pp = tk.BooleanVar(value=False)
        self.close_pp = tk.BooleanVar(value=True)
        self.project_path = None  # tallennetun projektin sijainti

        self._build_ui()

    # ---------- UI ----------
    def _build_ui(self):
        # menubar
        menubar = tk.Menu(self)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Uusi projekti", command=self.new_project)
        filemenu.add_separator()
        filemenu.add_command(label="Avaa projekti…", command=self.open_project_dialog)
        filemenu.add_separator()
        filemenu.add_command(label="Tallenna projekti", command=self.save_project)
        filemenu.add_command(label="Tallenna nimellä…", command=lambda: self.save_project(ask_path=True))
        filemenu.add_separator()
        filemenu.add_command(label="Poistu", command=self.on_quit)
        menubar.add_cascade(label="Tiedosto", menu=filemenu)
        self.config(menu=menubar)

        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")

        row1 = ttk.Frame(top)
        row1.pack(fill="x", pady=5)
        ttk.Label(row1, text="Pohja-PPTX:").pack(side="left")
        ttk.Entry(row1, textvariable=self.pptx_path).pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(row1, text="Selaa…", command=self.browse_pptx).pack(side="left")

        row2 = ttk.Frame(top)
        row2.pack(fill="x", pady=5)
        ttk.Label(row2, text="Korvattava teksti (placeholder):").pack(side="left")
        ttk.Entry(row2, width=30, textvariable=self.find_text).pack(side="left", padx=5)
        ttk.Label(row2, text="Leveys (px):").pack(side="left", padx=(15, 0))
        ttk.Entry(row2, width=8, textvariable=self.width_px).pack(side="left")
        ttk.Checkbutton(row2, text="Näytä PowerPoint", variable=self.visible_pp).pack(side="left", padx=10)
        ttk.Checkbutton(row2, text="Sulje PowerPoint lopuksi", variable=self.close_pp).pack(side="left", padx=10)

        row3 = ttk.Frame(top)
        row3.pack(fill="x", pady=5)
        ttk.Label(row3, text="Tulostuskansio:").pack(side="left")
        ttk.Entry(row3, textvariable=self.output_dir).pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(row3, text="Valitse…", command=self.browse_output).pack(side="left")

        mid = ttk.Frame(self, padding=10)
        mid.pack(fill="both", expand=True)

        left = ttk.Frame(mid)
        left.pack(side="left", fill="both", expand=True)
        ttk.Label(left, text="Aiheet (yksi per rivi):").pack(anchor="w")
        self.listbox = tk.Listbox(left, height=15, selectmode="extended")
        self.listbox.pack(fill="both", expand=True, pady=5)
        addrow = ttk.Frame(left)
        addrow.pack(fill="x", pady=5)
        self.new_item = tk.StringVar()
        ttk.Entry(addrow, textvariable=self.new_item).pack(side="left", fill="x", expand=True)
        ttk.Button(addrow, text="Lisää", command=self.add_item).pack(side="left", padx=5)
        ttk.Button(addrow, text="Poista valitut", command=self.remove_selected).pack(side="left")

        right = ttk.Frame(mid, width=360)
        right.pack(side="right", fill="both")
        ttk.Label(right, text="Lokit / tila:").pack(anchor="w")
        self.log = tk.Text(right, height=18, state="disabled")
        self.log.pack(fill="both", expand=True, pady=5)

        bottom = ttk.Frame(self, padding=10)
        bottom.pack(fill="x")
        self.progress = ttk.Progressbar(bottom, mode="determinate")
        self.progress.pack(fill="x", side="left", expand=True, padx=(0, 10))
        ttk.Button(bottom, text="Generoi JPG-kuvat", command=self.generate_clicked).pack(side="right")

        # window close handler
        self.protocol("WM_DELETE_WINDOW", self.on_quit)

    # ---------- Project I/O ----------
    def get_project_data(self):
        topics = [self.listbox.get(i) for i in range(self.listbox.size())]
        return {
            "version": 6,
            "pptx_path": self.pptx_path.get(),
            "output_dir": self.output_dir.get(),
            "find_text": self.find_text.get(),
            "width_px": int(self.width_px.get() or DEFAULT_WIDTH),
            "visible_pp": bool(self.visible_pp.get()),
            "close_pp": bool(self.close_pp.get()),
            "topics": topics,
        }

    def apply_project_data(self, data: dict):
        self.pptx_path.set(data.get("pptx_path", ""))
        self.output_dir.set(data.get("output_dir", ""))
        self.find_text.set(data.get("find_text", DEFAULT_FIND_TEXT))
        self.width_px.set(int(data.get("width_px", DEFAULT_WIDTH)))
        self.visible_pp.set(bool(data.get("visible_pp", False)))
        self.close_pp.set(bool(data.get("close_pp", True)))

        self.listbox.delete(0, "end")
        for t in data.get("topics", []):
            self.listbox.insert("end", str(t))

    def new_project(self):
        if not messagebox.askyesno("Uusi projekti", "Tyhjennetään nykyinen projekti?"):
            return
        self.project_path = None
        self.title(APP_TITLE + " — [Uusi]")
        self.pptx_path.set("")
        self.output_dir.set("")
        self.find_text.set(DEFAULT_FIND_TEXT)
        self.width_px.set(DEFAULT_WIDTH)
        self.visible_pp.set(False)
        self.close_pp.set(True)
        self.listbox.delete(0, "end")
        log_safe(self.log, "Uusi projekti luotu.")

    def save_project(self, ask_path: bool=False):
        if self.project_path is None or ask_path:
            initial = self.project_path or "projekti.pptjpgproj"
            path = filedialog.asksaveasfilename(
                title="Tallenna projekti",
                defaultextension=".pptjpgproj",
                initialfile=os.path.basename(initial),
                filetypes=[("PPTX JPG -projektit", "*.pptjpgproj"), ("JSON", "*.json"), ("Kaikki tiedostot", "*.*")],
            )
            if not path:
                return
            self.project_path = path

        data = self.get_project_data()
        try:
            with open(self.project_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.title(APP_TITLE + " — [" + os.path.basename(self.project_path) + "]")
            log_safe(self.log, f"Projekti tallennettu: {self.project_path}")
        except Exception as e:
            messagebox.showerror("Tallennus epäonnistui", str(e))

    def open_project_dialog(self):
        path = filedialog.askopenfilename(
            title="Avaa projekti",
            filetypes=[("PPTX JPG -projektit", "*.pptjpgproj;*.json"), ("Kaikki tiedostot", "*.*")],
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.apply_project_data(data or {})
            self.project_path = path
            self.title(APP_TITLE + " — [" + os.path.basename(self.project_path) + "]")
            log_safe(self.log, f"Projekti avattu: {self.project_path}")
        except Exception as e:
            messagebox.showerror("Avaus epäonnistui", str(e))

    # ---------- File pickers & list ops ----------
    def browse_pptx(self):
        path = filedialog.askopenfilename(
            title="Valitse PPTX",
            filetypes=[("PowerPoint", "*.pptx *.ppt")],
        )
        if path:
            self.pptx_path.set(path)

    def browse_output(self):
        path = filedialog.askdirectory(title="Valitse tulostuskansio")
        if path:
            self.output_dir.set(path)

    def add_item(self):
        text = self.new_item.get().strip()
        if text:
            self.listbox.insert("end", text)
            self.new_item.set("")

    def remove_selected(self):
        sel = list(self.listbox.curselection())
        sel.reverse()
        for i in sel:
            self.listbox.delete(i)

    # ---------- Validation & run ----------
    def validate_inputs(self):
        if not self.pptx_path.get():
            messagebox.showwarning("Puuttuva tiedosto", "Valitse pohja-PPTX.")
            return False
        if not os.path.exists(self.pptx_path.get()):
            messagebox.showerror("Tiedostoa ei löydy", self.pptx_path.get())
            return False
        if not self.output_dir.get():
            messagebox.showwarning("Puuttuva kansio", "Valitse tulostuskansio.")
            return False
        try:
            ensure_output_dir(self.output_dir.get())
        except Exception as e:
            messagebox.showerror("Kirjoitusvirhe", f"Tulostuskansioon ei voi kirjoittaa:\n{e}")
            return False
        if self.listbox.size() == 0:
            messagebox.showwarning("Ei rivejä", "Lisää vähintään yksi aihe.")
            return False
        if win32com is None or pythoncom is None:
            messagebox.showerror(
                "Puuttuva kirjasto",
                "pywin32 ei ole asennettu. Asenna komennolla:\n    py -m pip install pywin32")
            return False
        return True

    def generate_clicked(self):
        if not self.validate_inputs():
            return
        threading.Thread(target=self._generate_worker, daemon=True).start()

    def _generate_worker(self):
        self.progress.configure(maximum=self.listbox.size(), value=0)
        log_safe(self.log, "Käynnistetään PowerPoint…")

        app = pres = base = slide = None
        try:
            pythoncom.CoInitialize()

            app = win32com.client.gencache.EnsureDispatch("PowerPoint.Application")
            try:
                app.DisplayAlerts = PP_ALERTS_NONE
            except Exception:
                pass
            try:
                app.Visible = bool(self.visible_pp.get())
            except Exception:
                pass

            path_abs = to_win_path(self.pptx_path.get())
            pres = app.Presentations.Open(FileName=path_abs, ReadOnly=True, Untitled=False, WithWindow=bool(self.visible_pp.get()))

            slide_w = float(pres.PageSetup.SlideWidth)
            slide_h = float(pres.PageSetup.SlideHeight)
            target_w = int(self.width_px.get())
            target_h = max(1, int(round(target_w * (slide_h / slide_w))))

            base = pres.Slides(1)
            find_text = self.find_text.get()
            out_dir = ensure_output_dir(self.output_dir.get())

            total = self.listbox.size()
            for idx in range(total):
                topic = self.listbox.get(idx).strip()
                if not topic:
                    continue
                safe = sanitize_filename(topic)
                outfile = to_win_path(os.path.join(out_dir, f"{idx+1:02d}_{safe}.jpg"))
                log_safe(self.log, f"[{idx+1}/{total}] Luodaan: {outfile}")

                dup_range = base.Duplicate()
                slide = dup_range.Item(1)
                replaced = replace_text_in_shapes(slide.Shapes, find_text=find_text, replace_text=topic)
                if replaced == 0:
                    log_safe(self.log, "   VAROITUS: Placeholder-tekstiä ei löytynyt tältä dialta.")

                try:
                    slide.Export(outfile, "JPG", target_w, target_h)
                except Exception:
                    tmp_dir = tempfile.mkdtemp(prefix="pptx_jpg_")
                    try:
                        new_pres = app.Presentations.Add()
                        slide.Copy()
                        new_pres.Slides.Paste()
                        new_pres.PageSetup.SlideWidth = pres.PageSetup.SlideWidth
                        new_pres.PageSetup.SlideHeight = pres.PageSetup.SlideHeight
                        new_pres.SaveAs(to_win_path(tmp_dir), PP_SAVE_AS_JPG)
                        new_pres.Close()
                        jpgs = [f for f in os.listdir(tmp_dir) if f.lower().endswith(".jpg")]
                        if not jpgs:
                            raise RuntimeError("Varamenetelmän JPG:tä ei löytynyt.")
                        src = os.path.join(tmp_dir, jpgs[0])
                        shutil.move(src, outfile)
                    finally:
                        shutil.rmtree(tmp_dir, ignore_errors=True)

                slide.Delete()
                slide = None

                self.progress.step(1)
                self.update_idletasks()

            log_safe(self.log, "Valmis ✔")

        except Exception as e:
            log_safe(self.log, f"VIRHE: {e}")

        finally:
            try:
                if pres is not None:
                    pres.Close()
            except Exception:
                pass
            try:
                if app is not None and self.close_pp.get():
                    app.Quit()
            except Exception:
                pass

            slide = base = pres = app = None
            try:
                pythoncom.CoUninitialize()
            except Exception:
                pass
            gc.collect()

    def on_quit(self):
        # yksinkertainen poistumisvarmistus
        self.destroy()


if __name__ == "__main__":
    App().mainloop()
