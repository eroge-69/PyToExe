# -*- coding: utf-8 -*-
# =========================
# HZV-Listen Parser (GUI)
# =========================

import os
import re
import unicodedata
import tkinter as tk
from PIL import Image, ImageDraw, ImageTk
from tkinter import filedialog, messagebox, font

import pandas as pd

# PyPDF2: kompatibel zu 1.x (PdfFileReader). Falls 3.x im Einsatz, ggf. PdfReader verwenden.
import PyPDF2


# -------------------------
# Hilfsfunktionen (Parsing)
# -------------------------

def normalize_unicode(s: str) -> str:
    """Normalisiert Unicode (NFC), damit z.B. 'Süd' -> 'Süd' wird."""
    return unicodedata.normalize("NFC", s)


def extract_info_from_filename(filename: str):
    """
    Liefert (kassenname, jahr) aus Dateinamen wie
    '0091573_Patiententeilnahmestatus_HZV_BKK_LV_Süd_BW_2025_3.pdf'
    oder alten Varianten. Entfernt 'BW', normalisiert Unicode, wandelt - zu _.
    """
    base = os.path.basename(filename)
    if base.lower().endswith(".pdf"):
        base = base[:-4]

    base = normalize_unicode(base)
    parts = base.split("_")
    if len(parts) < 3:
        return None, None

    jahr = parts[-2]

    # nach 'HZV' suchen
    try:
        idx = parts.index("HZV") + 1
    except ValueError:
        try:
            idx = [p.lower() for p in parts].index("hzv") + 1
        except ValueError:
            return None, jahr

    kassenteile = parts[idx:-2]  # alles zwischen HZV und (Jahr, Quartal)
    kassenteile = [p for p in kassenteile if p != "BW"]  # BW entfernen

    kasse_raw = "_".join(kassenteile)
    kasse_norm = kasse_raw.replace("-", "_")
    kasse_norm = normalize_unicode(kasse_norm)

    # Bekannte Normalisierungen/Mapping
    mapping = {
        "AOK_BW": "AOK",
        "AOK_BW_IVP": "AOK_IVP",
        "BKK-VAG": "BKK_VAG",
        "BKK_VAG": "BKK_VAG",
        "BKK_GWQ": "BKK_GWQ",
        "Bosch_BKK": "Bosch_BKK",
        "EK": "EK",
        "IKK_classic": "IKK_classic",
        "Knappschaft": "Knappschaft",
        "LKK": "LKK",
        # neue Bezeichnung:
        "BKK_LV_Süd": "BKK_LV_Süd",
        "BKK_LV_Sud": "BKK_LV_Süd",  # falls ohne Umlaut
    }

    kassenname = mapping.get(kasse_norm, kasse_norm)
    return kassenname, jahr


def extract_quartal(filename: str):
    """Extrahiert das Quartal (1-4) am Ende des Dateinamens."""
    base = os.path.basename(filename)
    m = re.search(r"_([1-4])(?:\.pdf)?$", base)
    return m.group(1) if m else None


def parse_enrollment_line(line: str):
    """
    Extrahiert (name, vorname, geburtsdatum, versichertennummer, fa_vertrag)
    aus einer Einschreibungszeile. Funktioniert mit/ohne Komma zwischen Name/Vorname.
    Ignoriert alles nach der Versichertennummer (z.B. Beginndatum/Endedatum).
    """
    # Grob: [Nr] [Nameblock] [Geburtsdatum] [KV-Nr]
    m = re.search(
        r"^\s*\d+\s+(?P<nameblock>.+?)\s+(?P<geb>\d{2}\.\d{2}\.\d{4})\s+(?P<kvn>[A-Z]\w+)",
        line
    )
    if not m:
        return None

    nameblock = m.group("nameblock").strip()
    geb = m.group("geb")
    kvn = m.group("kvn")

    # Nameblock bevorzugt am Komma splitten, sonst Heuristik (erstes Wort Nachname)
    if "," in nameblock:
        last_raw, first_raw = [x.strip() for x in nameblock.split(",", 1)]
    else:
        parts = nameblock.split()
        if len(parts) >= 2:
            last_raw = parts[0]
            first_raw = " ".join(parts[1:])
        else:
            last_raw = nameblock
            first_raw = ""

    fa_vertrag = "Ja" if re.search(r"\bJa\b", line) else "Nein"
    return last_raw, first_raw, geb, kvn, fa_vertrag


def parse_termination_line(line: str):
    """
    Extrahiert (grund, name, vorname, geburtsdatum, versichertennummer, beginndatum, endedatum)
    aus einer Beendigungszeile. Der Grund steht vor der Laufnummer.
    Akzeptiert komplexe Namensvarianten.
    """
    m = re.search(
        r"(?P<grund>.+?)"                       # Grund (lazy bis zur Nr.)
        r"(\d+)\s+"                             # Laufnummer
        r"(?P<nach>[\w\s'’.-]+?),\s+"           # Nachname (inkl. O'..., De ..., Bindestriche)
        r"(?P<vor>[\w\s'’.-]+)\s+"              # Vorname(n)
        r"(?P<geb>\d{2}\.\d{2}\.\d{4})\s+"      # Geburtsdatum
        r"(?P<kvn>[A-Z]\w+)\s+"                 # Versichertennr.
        r"(?P<beg>\d{2}\.\d{2}\.\d{4})\s+"      # Beginndatum
        r"(?P<end>\d{2}\.\d{2}\.\d{4})",        # Endedatum
        line
    )
    if not m:
        return None
    g = m.groupdict()
    return (
        g["grund"].strip(),
        g["nach"].strip(),
        g["vor"].strip(),
        g["geb"],
        g["kvn"],
        g["beg"],
        g["end"],
    )


# -------------------------
# Gemeinsame Extraktion
# -------------------------

def extract_sections_from_pdf_text(full_text: str):
    """
    Teilt den PDF-Text an der Kern-Formulierung für Einschreibungen.
    Liefert (before_keyword, after_keyword), so wie es bisher genutzt wurde.
    """
    keyphrase = 'Diese Liste beinhaltet alle bestätigten eingeschriebenen Patienten für dieses Quartal.'
    before_keyword, _, after_keyword = full_text.partition(keyphrase)
    return before_keyword, after_keyword


# -------------------------
# Kassen-spezifische Parser
# -------------------------

def parse_aok(after_keyword: str, before_keyword: str, filename: str,
              einschreibungen: list, beendigungen: list):
    kassenname, jahr = extract_info_from_filename(filename)
    quartal = extract_quartal(filename)

    # Einschreibungen
    keyword = "Informationen zum PraCMan-Teilnahmestatus Ihrer Patienten"
    before, _, _ = after_keyword.partition(keyword)
    lines = before.strip().split("\n")[2:]  # Header überspringen

    for line in lines:
        parsed = parse_enrollment_line(line)
        if parsed:
            name, vorname, geburtsdatum, versichertennummer, fa_vertrag = parsed
            einschreibungen.append({
                'Kasse': kassenname, 'Jahr': jahr, 'Quartal': quartal,
                'Versichertennummer': versichertennummer,
                'Name': name, 'Vorname': vorname,
                'Geburtstdatum': geburtsdatum,
                'FA-Vertrag': fa_vertrag
            })
        else:
            if re.search(r"\b[A-Z]\w+\b", line):
                print("Ungeparst (AOK):", line)

    # Beendigungen
    keyword_end = "Diese Liste beinhaltet alle in Prüfung befindlichen Teilnahmeerklärungen"
    before_end, _, _ = before_keyword.partition(keyword_end)
    keyword_endphrase = "Diese Liste beinhaltet alle beendeten Versicherteneinschreibungen."
    before_keyphrase, _, after_keyphrase = before_end.partition(keyword_endphrase)
    end_lines = after_keyphrase.strip().split("\n")[1:]  # Header 1
    for line in end_lines[2:]:  # Header 2
        parsed = parse_termination_line(line)
        if parsed:
            grund, name, vorname, geburtsdatum, kvn, beg, endd = parsed
            beendigungen.append({
                'Kasse': kassenname, 'Jahr': jahr, 'Quartal': quartal,
                'Versichertennummer': kvn,
                'Name': name, 'Vorname': vorname,
                'Geburtstdatum': geburtsdatum,
                'Beginn-Datum': beg, 'End-Datum': endd, 'Grund': grund
            })
        else:
            if re.search(r"\b[A-Z]\w+\b", line):
                print("Ungeparst (AOK End):", line)


def parse_block_simple_enroll(before_text: str, filename: str,
                              einschreibungen: list, kassen_marker: str):
    """
    Für Kassen, deren Einschreibungen einfach im 'before' Block nach
    'Bitte prüfen Sie dieses Stammdatenblatt' kommen.
    """
    kassenname, jahr = extract_info_from_filename(filename)
    quartal = extract_quartal(filename)

    before, _, _ = before_text.partition("Bitte prüfen Sie dieses Stammdatenblatt")
    lines = before.strip().split("\n")[1:]  # Header überspringen

    for line in lines:
        parsed = parse_enrollment_line(line)
        if parsed:
            name, vorname, geburtsdatum, versichertennummer, fa_vertrag = parsed
            einschreibungen.append({
                'Kasse': kassenname, 'Jahr': jahr, 'Quartal': quartal,
                'Versichertennummer': versichertennummer,
                'Name': name, 'Vorname': vorname,
                'Geburtstdatum': geburtsdatum,
                'FA-Vertrag': fa_vertrag
            })
        else:
            if re.search(r"\b[A-Z]\w+\b", line):
                print(f"Ungeparst ({kassen_marker}):", line)


def parse_block_ends(before_keyword: str, filename: str, beendigungen: list, kassen_marker: str):
    """
    Standard-Endlisten-Parser, identisch zu AOK-Ende (falls vorhanden).
    """
    kassenname, jahr = extract_info_from_filename(filename)
    quartal = extract_quartal(filename)

    keyword_end = "Diese Liste beinhaltet alle in Prüfung befindlichen Teilnahmeerklärungen"
    before_end, _, _ = before_keyword.partition(keyword_end)
    keyword_endphrase = "Diese Liste beinhaltet alle beendeten Versicherteneinschreibungen."
    before_keyphrase, _, after_keyphrase = before_end.partition(keyword_endphrase)
    end_lines = after_keyphrase.strip().split("\n")[1:]

    for line in end_lines[2:]:
        parsed = parse_termination_line(line)
        if parsed:
            grund, name, vorname, geburtsdatum, kvn, beg, endd = parsed
            beendigungen.append({
                'Kasse': kassenname, 'Jahr': jahr, 'Quartal': quartal,
                'Versichertennummer': kvn,
                'Name': name, 'Vorname': vorname,
                'Geburtstdatum': geburtsdatum,
                'Beginn-Datum': beg, 'End-Datum': endd, 'Grund': grund
            })
        else:
            if re.search(r"\b[A-Z]\w+\b", line):
                print(f"Ungeparst ({kassen_marker} End):", line)


# Spezifische Wrapper für einzelne Kassen

def aok(after_keyword, before_keyword, filename, einschreibungen, beendigungen):
    parse_aok(after_keyword, before_keyword, filename, einschreibungen, beendigungen)


def aok_pracman(after_keyword, before_keyword, filename, einschreibungen, beendigungen):
    # Enthält meist nur eine Spezialliste; wenn nötig, hier eigenen Block lassen.
    # Für jetzt nutzen wir die Standard-"Bitte prüfen..."-Liste vor dem Hinweis.
    before, _, _ = after_keyword.partition(
        "abgerechnet werden, wenn sie nicht auf der Liste „Zu beendende PraCMan-Teilnehmer“ enthalten sind."
    )
    # Danach folgt nochmals ein Hinweis – wir nehmen nur die Zeilen vorher:
    parse_block_simple_enroll(before, filename, einschreibungen, "AOK_PraCMan")


def aok_ivp(after_keyword, before_keyword, filename, einschreibungen, beendigungen):
    parse_block_simple_enroll(after_keyword, filename, einschreibungen, "AOK_IVP")
    parse_block_ends(before_keyword, filename, beendigungen, "AOK_IVP")


def bkk_vag_or_lv_sued(after_keyword, before_keyword, filename, einschreibungen, beendigungen):
    # Alter Name BKK-VAG oder neuer BKK_LV_Süd – der Parser ist gleich
    parse_block_simple_enroll(after_keyword, filename, einschreibungen, "BKK_LV_Süd")
    parse_block_ends(before_keyword, filename, beendigungen, "BKK_LV_Süd")


def bkk_gwq(after_keyword, before_keyword, filename, einschreibungen, beendigungen):
    parse_block_simple_enroll(after_keyword, filename, einschreibungen, "BKK_GWQ")
    parse_block_ends(before_keyword, filename, beendigungen, "BKK_GWQ")


def ek(after_keyword, before_keyword, filename, einschreibungen, beendigungen):
    parse_block_simple_enroll(after_keyword, filename, einschreibungen, "EK")


def ikk(after_keyword, before_keyword, filename, einschreibungen, beendigungen):
    parse_block_simple_enroll(after_keyword, filename, einschreibungen, "IKK_classic")
    parse_block_ends(before_keyword, filename, beendigungen, "IKK_classic")


def bosch(after_keyword, before_keyword, filename, einschreibungen, beendigungen):
    parse_block_simple_enroll(after_keyword, filename, einschreibungen, "Bosch_BKK")


def knappschaft(after_keyword, before_keyword, filename, einschreibungen, beendigungen):
    parse_block_simple_enroll(after_keyword, filename, einschreibungen, "Knappschaft")


def lkk(after_keyword, before_keyword, filename, einschreibungen, beendigungen):
    parse_block_simple_enroll(after_keyword, filename, einschreibungen, "LKK")


# -------------------------
# PDF lesen & verarbeiten
# -------------------------

def process_files(input_folder, output_folder, progress_cb=None, status_cb=None):
    """
    Führt die Verarbeitung durch und meldet Fortschritt/Fortschrittstext über
    optionale Callbacks:
      progress_cb(done, total)
      status_cb(text)
    """
    einschreibungen = []
    beendigungen = []

    try:
        # Alle PDFs ermitteln (stabil für Progress)
        pdfs = [f for f in os.listdir(input_folder) if f.lower().endswith(".pdf")]
        total = len(pdfs)
        done = 0

        for filename in pdfs:
            if status_cb:
                status_cb(f"Öffne: {filename} ({done+1}/{total})")

            filepath = os.path.join(input_folder, filename)

            # PDF lesen
            with open(filepath, 'rb') as f:
                pdfReader = PyPDF2.PdfFileReader(f)
                texts = []
                for p in range(pdfReader.numPages):
                    texts.append(pdfReader.getPage(p).extractText())
                full_text = "".join(texts)

            full_text = normalize_unicode(full_text)
            before_keyword, after_keyword = extract_sections_from_pdf_text(full_text)

            fn = normalize_unicode(filename)

            # Routing je Kasse (wie in deinem letzten Stand)
            if re.search(r"AOK_BW_\d", fn) and not re.search(r"AOK_BW_IVP", fn):
                if status_cb: status_cb("Kasse: AOK")
                aok(after_keyword, before_keyword, filename, einschreibungen, beendigungen)
                aok_pracman(after_keyword, before_keyword, filename, einschreibungen, beendigungen)

            elif re.search(r"AOK_BW_IVP", fn):
                if status_cb: status_cb("Kasse: AOK_IVP")
                aok_ivp(after_keyword, before_keyword, filename, einschreibungen, beendigungen)

            elif re.search(r"(?:BKK[-_]?VAG|BKK[-_]LV[-_]S(?:u|ü)d)", fn, flags=re.IGNORECASE):
                if status_cb: status_cb("Kasse: BKK_LV_Süd (ehem. BKK-VAG)")
                bkk_vag_or_lv_sued(after_keyword, before_keyword, filename, einschreibungen, beendigungen)


            elif re.search(r"BKK_GWQ", fn):
                if status_cb: status_cb("Kasse: BKK_GWQ")
                bkk_gwq(after_keyword, before_keyword, filename, einschreibungen, beendigungen)

            elif re.search(r"_EK_", fn):
                if status_cb: status_cb("Kasse: EK")
                ek(after_keyword, before_keyword, filename, einschreibungen, beendigungen)

            elif re.search(r"IKK", fn, flags=re.IGNORECASE):
                if status_cb: status_cb("Kasse: IKK_classic")
                ikk(after_keyword, before_keyword, filename, einschreibungen, beendigungen)

            elif re.search(r"Bosch", fn, flags=re.IGNORECASE):
                if status_cb: status_cb("Kasse: Bosch_BKK")
                bosch(after_keyword, before_keyword, filename, einschreibungen, beendigungen)

            elif re.search(r"Knappschaft", fn, flags=re.IGNORECASE):
                if status_cb: status_cb("Kasse: Knappschaft")
                knappschaft(after_keyword, before_keyword, filename, einschreibungen, beendigungen)

            elif re.search(r"LKK", fn, flags=re.IGNORECASE):
                if status_cb: status_cb("Kasse: LKK")
                lkk(after_keyword, before_keyword, filename, einschreibungen, beendigungen)
            else:
                if status_cb: status_cb(f"Keine Zuordnung: {filename}")
                print("Datei nicht zugeordnet:", filename)

            # Fortschritt updaten
            done += 1
            if progress_cb:
                progress_cb(done, total)

        # Ergebnisse speichern
        df_e = pd.DataFrame(einschreibungen)
        df_b = pd.DataFrame(beendigungen)

        if not os.path.exists(output_folder):
            os.makedirs(output_folder, exist_ok=True)

        path_e_csv = os.path.join(output_folder, "einschreibungen.csv")
        path_e_xlsx = os.path.join(output_folder, "einschreibungen.xlsx")
        path_b_csv = os.path.join(output_folder, "beendigungen.csv")
        path_b_xlsx = os.path.join(output_folder, "beendigungen.xlsx")

        if status_cb: status_cb("Speichere Dateien …")
        df_e.to_csv(path_e_csv, index=False, encoding="utf-8-sig")
        df_e.to_excel(path_e_xlsx, index=False)
        df_b.to_csv(path_b_csv, index=False, encoding="utf-8-sig")
        df_b.to_excel(path_b_xlsx, index=False)

        if status_cb: status_cb(f"Fertig! Dateien gespeichert in: {output_folder}")
        return True

    except FileNotFoundError as e:
        if status_cb: status_cb("Fehler: Datei nicht gefunden.")
        messagebox.showerror("Fehler", "Ein Fehler ist aufgetreten: " + str(e))
        return False
    except Exception as e:
        if status_cb: status_cb("Unerwarteter Fehler.")
        messagebox.showerror("Unerwarteter Fehler", str(e))
        return False


# -------------------------
# GUI
# -------------------------

def browse_folder(prompt):
    d = filedialog.askdirectory(title=prompt)
    if not d:
        messagebox.showwarning("Warnung", "Kein Ordner ausgewählt. Bitte versuchen Sie es erneut.")
        return None
    return d


def start_processing():
    input_folder = browse_folder("Bitte wählen Sie den Ordner mit den PDF-Dateien aus.")
    if not input_folder:
        return

    output_folder = browse_folder("Bitte wählen Sie den Zielordner für die CSV/XLSX-Dateien aus.")
    if not output_folder:
        return

    ok = process_files(input_folder, output_folder)
    if ok:
        messagebox.showinfo("Fertig", "Die Verarbeitung ist abgeschlossen.")


import threading
from tkinter import ttk

# ---------- Canvas-Button mit „runden Ecken“ & Glossy-Look ----------

class RoundedButton(tk.Label):
    """
    Einfarbiger, weich gerenderter Button mit runden Ecken auf Basis von Pillow.
    - color / hover_color: Hexfarbe (z.B. "#6C8CF5")
    - radius: Eckenradius in px
    """
    def __init__(self, master, text, command=None,
                 width=280, height=44, radius=18,
                 color="#6C8CF5", hover_color="#7D9BF7",
                 text_color="white", font=("Arial", 12, "bold"),
                 **kwargs):
        super().__init__(master, bd=0, bg=master["bg"], **kwargs)
        self.master = master
        self.text = text
        self.command = command
        self.w = width
        self.h = height
        self.r = radius
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = font

        self._build_images(self.w)  # statt: self._img_normal = ..., self._img_hover = ...

        self.config(image=self._img_normal, compound="center", fg=self.text_color, font=self.font, text=self.text)
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", lambda e: self.config(image=self._img_hover))
        self.bind("<Leave>", lambda e: self.config(image=self._img_normal))

    def _build_images(self, width):
        self.w = int(width)
        self._img_normal = self._make_image(self.color)
        self._img_hover  = self._make_image(self.hover_color)
        self.config(image=self._img_normal)  # Bild aktualisieren

    def set_width(self, width):
        """Ändert die Breite und rendert die Bilder neu (für responsive Layouts)."""
        width = int(max(120, width))  # Mindestbreite
        if width != self.w:
            self._build_images(width)
    
    def _make_image(self, fill_hex):
        # Hochskalieren für Anti-Aliasing
        scale = 3
        W, H, R = self.w * scale, self.h * scale, self.r * scale
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Runde Fläche zeichnen
        draw.rounded_rectangle((0, 0, W-1, H-1), radius=R, fill=fill_hex)

        # Downsampling -> weiche Kanten
        img = img.resize((self.w, self.h), Image.LANCZOS)
        return ImageTk.PhotoImage(img)

    def _on_click(self, _):
        if callable(self.command):
            self.command()



# ---------- GUI-Logik ----------

import threading
from tkinter import ttk

def main():
    root = tk.Tk()
    root.title("HZV-Listen Verarbeitung")
    root.geometry("720x360")
    root.minsize(680, 340)
    root.configure(bg="#f7f9fc")

    # State
    input_dir_var = tk.StringVar(value="")
    output_dir_var = tk.StringVar(value="")
    status_var = tk.StringVar(value="Bitte Ordner auswählen und Start drücken.")
    progress_var = tk.DoubleVar(value=0.0)

    # Container
    wrap = tk.Frame(root, bg=root["bg"])
    wrap.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

    # Pfad-Labels
    path_font = ("Arial", 10)
    lbl_in = tk.Label(wrap, text="Listenordner: (nicht gewählt)", bg=wrap["bg"], fg="#333",
                      font=path_font, anchor="w")
    lbl_in.pack(fill=tk.X, pady=(0, 6))
    lbl_out = tk.Label(wrap, text="Speicherort: (nicht gewählt)", bg=wrap["bg"], fg="#333",
                       font=path_font, anchor="w")
    lbl_out.pack(fill=tk.X, pady=(0, 12))

    # Aktionen
    def choose_input():
        d = filedialog.askdirectory(title="Bitte wählen Sie den Ordner mit den PDF-Dateien aus.")
        if d:
            input_dir_var.set(d)
            lbl_in.config(text=f"Listenordner: {d}")

    def choose_output():
        d = filedialog.askdirectory(title="Bitte wählen Sie den Zielordner für die CSV/XLSX-Dateien aus.")
        if d:
            output_dir_var.set(d)
            lbl_out.config(text=f"Speicherort: {d}")

    # Progressbar
    ttk_style = ttk.Style()
    ttk_style.theme_use("default")
    ttk_style.configure(
        "Horizontal.TProgressbar",
        troughcolor="#e9edf3",
        background="#4FACFE",
        bordercolor="#e9edf3",
        lightcolor="#4FACFE",
        darkcolor="#4FACFE",
    )
    pbar = ttk.Progressbar(
        wrap, style="Horizontal.TProgressbar",
        orient="horizontal", mode="determinate",
        maximum=100, variable=progress_var
    )
    pbar.pack(fill=tk.X, pady=(8, 6))

    # Status
    status = tk.Label(wrap, textvariable=status_var, bg=wrap["bg"], fg="#555", anchor="w")
    status.pack(fill=tk.X, pady=(0, 12))

    # Button-Leiste
    btn_row = tk.Frame(wrap, bg=wrap["bg"])
    btn_row.pack(fill=tk.X)

    btn_in = RoundedButton(
        btn_row, "1) Listenordner auswählen",
        command=choose_input,
        width=300, color="#6C8CF5", hover_color="#7D9BF7"
    )
    btn_in.grid(row=0, column=0, padx=(0, 12), pady=6, sticky="w")

    btn_out = RoundedButton(
        btn_row, "2) Speicherort wählen",
        command=choose_output,
        width=300, color="#6C8CF5", hover_color="#7D9BF7"
    )
    btn_out.grid(row=0, column=1, padx=(0, 0), pady=6, sticky="e")

    # EINZIGER Start-Button
    btn_start = RoundedButton(
        wrap, "3) Start", command=lambda: start(),
        width=680, color="#33C481", hover_color="#4ED296"
    )
    btn_start.pack(fill=tk.X, pady=12)

    # ---------- Helper zum (De-)Aktivieren ----------
    def set_widgets_enabled(enabled: bool):
        if enabled:
            btn_in.bind("<Button-1>", btn_in._on_click)
            btn_out.bind("<Button-1>", btn_out._on_click)
            btn_start.bind("<Button-1>", lambda e: start())
        else:
            btn_in.unbind("<Button-1>")
            btn_out.unbind("<Button-1>")
            btn_start.unbind("<Button-1>")

    # ---------- Progress-Callbacks (thread-safe) ----------
    def progress_cb(done, total):
        pct = 0 if total == 0 else done / total * 100.0
        root.after(0, lambda: progress_var.set(pct))

    def status_cb(txt):
        root.after(0, lambda: status_var.set(txt))

    # ---------- Start-Aktion (Thread) ----------
    def start():
        inp = input_dir_var.get().strip()
        outp = output_dir_var.get().strip()
        if not inp or not os.path.isdir(inp):
            messagebox.showerror("Fehler", "Bitte gültigen Listenordner wählen.")
            return
        if not outp or not os.path.isdir(outp):
            messagebox.showerror("Fehler", "Bitte gültigen Speicherort wählen.")
            return

        set_widgets_enabled(False)
        progress_var.set(0)
        status_var.set("Starte Verarbeitung …")

        def run():
            ok = process_files(inp, outp, progress_cb=progress_cb, status_cb=status_cb)
            def finish():
                set_widgets_enabled(True)
                if ok:
                    messagebox.showinfo("Fertig", "Die Verarbeitung ist abgeschlossen.")
            root.after(0, finish)

        threading.Thread(target=run, daemon=True).start()

    # ---------- Responsive Breiten ----------
    def on_resize(_event=None):
        # Innenbreite des Containers:
        full_w = max(400, wrap.winfo_width())
        gap = 12  # Abstand zwischen 1) und 2)

        # Start-Button: volle Innenbreite
        btn_start.set_width(full_w)

        # 1) und 2): exakt halbe Breite von Start, symmetrisch
        half = int((full_w - gap) / 2)
        btn_in.set_width(half)
        btn_out.set_width(half)

        # Grid-Spalten so setzen, dass rechtsbündig/links bündig klappt
        btn_row.grid_columnconfigure(0, weight=1)
        btn_row.grid_columnconfigure(1, weight=1)

    root.bind("<Configure>", on_resize)
    root.after(0, on_resize)
    root.mainloop()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        messagebox.showerror("Unerwarteter Fehler", str(e))
        raise
