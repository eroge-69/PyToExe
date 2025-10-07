# analiza_trichoskopia.py
# Wersja "dokładna" - GUI, analiza obrazu, PDF. Zapisz w tym samym folderze co logo.png.
import os
import json
import math
import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageOps
import cv2
import numpy as np
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet

# ---------- KONFIGURACJA ----------
CONFIG_FILE = "config.json"
LOGO_FILE = "logo.png"

DEFAULT_CONFIG = {
    "pixel_to_micron": 0.25,   # domyślna przybliżona wartość (dla 50x powinna być ok)
    "cluster_distance_px": 25  # dystans (px) do grupowania włosów w jednostkę mieszkową (można skalibrować)
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            # uzupełnij brakujące pola
            for k,v in DEFAULT_CONFIG.items():
                if k not in cfg:
                    cfg[k] = v
            return cfg
        except Exception:
            return DEFAULT_CONFIG.copy()
    else:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
        return DEFAULT_CONFIG.copy()

CONFIG = load_config()

def px_to_micron(px):
    return px * float(CONFIG.get("pixel_to_micron", 0.25))

# ---------- ANALIZA OBRAZU (dokładna heurystyka) ----------
def analyze_image(path):
    """
    Dokładniejsza analiza:
    - adaptacyjne progowanie po wstępnym przetworzeniu (bilateral, equalize)
    - morfologia (closing + opening)
    - znajdowanie konturów włosów
    - pomiar grubości przez distance transform (2 * max_dist w obrębie konturu)
    - grupowanie centroidów włosów by zasymulować follicular units
    Zwraca metryki i obraz preview (PIL).
    """
    img_cv = cv2.imread(path)
    if img_cv is None:
        raise ValueError("Nie można wczytać pliku: " + path)
    # resize jeśli obraz bardzo duży (przyspieszenie) - zachowaj proporcje
    max_dim = 1600
    h0, w0 = img_cv.shape[:2]
    scale = 1.0
    if max(h0, w0) > max_dim:
        scale = max_dim / max(h0, w0)
        img_cv = cv2.resize(img_cv, (int(w0*scale), int(h0*scale)), interpolation=cv2.INTER_AREA)

    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    # redukcja szumu, zachowanie krawędzi
    blur = cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)
    # lokalne wyrównanie kontrastu
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    eq = clahe.apply(blur)

    # adaptacyjne progowanie - włosy są ciemne -> binary: włos = 255
    th = cv2.adaptiveThreshold(eq, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                               cv2.THRESH_BINARY_INV, 15, 7)

    # oczyszczanie: morfologia
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    close = cv2.morphologyEx(th, cv2.MORPH_CLOSE, kernel, iterations=2)
    open_ = cv2.morphologyEx(close, cv2.MORPH_OPEN, kernel, iterations=1)

    # usuń bardzo małe obiekty (artefakty)
    nb_components, output, stats, _ = cv2.connectedComponentsWithStats(open_, connectivity=8)
    sizes = stats[1:, cv2.CC_STAT_AREA] if nb_components > 1 else []
    min_size = 20  # px - minimalny obszar do uznania jako fragment włosa (można skalibrować)
    cleaned = np.zeros(output.shape, dtype=np.uint8)
    for i in range(1, nb_components):
        if stats[i, cv2.CC_STAT_AREA] >= min_size:
            cleaned[output == i] = 255

    # distance transform (na binarze z włosami jako 255)
    # cv2.distanceTransform wymaga 8-bit typu CV_8U
    dist = cv2.distanceTransform(cleaned, cv2.DIST_L2, 5)

    # znajdź kontury na "cleaned"
    contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    hairs = []
    overlay = img_cv.copy()

    for cnt in contours:
        x,y,w,h = cv2.boundingRect(cnt)
        # filtrujemy drobne kontury (artefakty)
        if w < 3 and h < 3:
            continue
        # wewnątrz konturu szukamy max distance -> połowa szerokości (w px)
        # utwórz maskę dla konturu
        mask = np.zeros(cleaned.shape, dtype=np.uint8)
        cv2.drawContours(mask, [cnt], -1, 255, -1)
        # pobierz max z transformation w obrębie maski
        max_dist = float(np.max(dist[mask==255]))  # odległość w pikselach do tła
        if max_dist <= 0.1:
            continue
        thickness_px = max(1.0, 2.0 * max_dist)  # przybliżona szerokość włosa w px
        length_px = max(w,h)
        # dopuszczenie tylko obiektów odpowiedniej długości
        if length_px < 8:
            continue
        # centroid
        M = cv2.moments(cnt)
        if M["m00"] != 0:
            cx = M["m10"]/M["m00"]
            cy = M["m01"]/M["m00"]
        else:
            cx, cy = x + w/2, y + h/2

        hairs.append({
            "x": x, "y": y, "w": w, "h": h,
            "thickness_px": thickness_px,
            "length_px": length_px,
            "cx": cx, "cy": cy
        })
        # rysuj prostokąt na overlay i grubość
        cv2.rectangle(overlay, (x,y), (x+w, y+h), (0,180,0), 1)
        cv2.circle(overlay, (int(cx), int(cy)), 1, (255,0,0), -1)

    # konwersja grubości do µm
    thickness_um_list = [px_to_micron(h["thickness_px"]) for h in hairs]
    total = len(thickness_um_list)
    cienkie = sum(1 for t in thickness_um_list if t < 30)
    srednie = sum(1 for t in thickness_um_list if 30 <= t <= 50)
    grube = sum(1 for t in thickness_um_list if t > 50)
    avg_thickness = float(np.mean(thickness_um_list)) if thickness_um_list else 0.0

    # clusterowanie centroidów - prosty algorytm aglomeracyjny
    centroids = [(h["cx"], h["cy"]) for h in hairs]
    clusters = []
    dist_threshold = CONFIG.get("cluster_distance_px", 25)  # px; można skalibrować w config.json
    # adaptacja progu do rozmiaru obrazu (jeśli obraz jest mały, zmniejsz pr.
    img_diag = math.hypot(img_cv.shape[0], img_cv.shape[1])
    if img_diag < 800:
        dist_threshold = max(10, int(dist_threshold * 0.6))
    elif img_diag > 2000:
        dist_threshold = int(dist_threshold * 1.5)

    for c in centroids:
        placed = False
        for cl in clusters:
            # sprawdzamy odległość od każdego członka klastra
            for member in cl:
                if math.hypot(member[0]-c[0], member[1]-c[1]) <= dist_threshold:
                    cl.append(c)
                    placed = True
                    break
            if placed:
                break
        if not placed:
            clusters.append([c])

    single = sum(1 for cl in clusters if len(cl) == 1)
    double = sum(1 for cl in clusters if len(cl) == 2)
    triple_plus = sum(1 for cl in clusters if len(cl) >= 3)

    # estimate empty follicles - heurystyka: porównujemy oczekiwaną gęstość do wykrytej
    # Tutaj dla prostoty dajemy aproksymację: jeśli liczba włosów < 50 -> możliwe puste mieszki
    empty_estimate = 0
    if total < 50:
        empty_estimate = int((50 - total) * 0.3)

    # przygotuj obraz preview w kolorze RGB (PIL)
    overlay_rgb = cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB)
    pil_preview = Image.fromarray(overlay_rgb)

    metrics = {
        "liczba_włosów": total,
        "średnia_grubość_um": round(avg_thickness,2),
        "cienkie": cienkie,
        "srednie": srednie,
        "grube": grube,
        "single_units": single,
        "double_units": double,
        "triple_plus": triple_plus,
        "empty_estimate": empty_estimate,
        "preview_image": pil_preview
    }
    return metrics

# ---------- GENEROWANIE WNIOSKU ----------
def generate_conclusion(metrics_frontal, metrics_temporal, metrics_occipital):
    comments = []
    def pct_cienkie(m):
        total = m["liczba_włosów"] or 1
        return round(100 * m["cienkie"] / total, 1)
    pct_fr = pct_cienkie(metrics_frontal)
    pct_te = pct_cienkie(metrics_temporal)
    pct_oc = pct_cienkie(metrics_occipital)

    if pct_fr > 30:
        comments.append(f"Frontal: podwyższony odsetek cienkich włosów ({pct_fr}%) — możliwa miniaturyzacja.")
    if pct_te > 30:
        comments.append(f"Temporal: podwyższony odsetek cienkich włosów ({pct_te}%).")
    if pct_oc > 30:
        comments.append(f"Occipital: podwyższony odsetek cienkich włosów ({pct_oc}%).")

    nums = [metrics_frontal["liczba_włosów"], metrics_temporal["liczba_włosów"], metrics_occipital["liczba_włosów"]]
    if nums[0] < nums[2] * 0.7:
        comments.append("Frontal ma zauważalnie mniejszą liczbę włosów w porównaniu do occipital — możliwy obraz utraty.")
    if metrics_frontal["empty_estimate"] > 10:
        comments.append("Szacunkowa liczba pustych mieszków jest podwyższona w obszarze frontal.")
    if not comments:
        comments.append("Brak wyraźnych cech patologicznych w analizowanych kadrach; zalecana obserwacja kontrolna.")
    return " ".join(comments)

# ---------- GENEROWANIE PDF ----------
def generate_pdf(patient_name, date_exam, metrics_list, user_comment, logo_path, output_filename="Raport.pdf"):
    # nazwa pliku jak chcemy: Raport_ImieNazwisko.pdf
    safe_name = patient_name.replace(" ", "_")
    if not output_filename.lower().endswith(".pdf"):
        output_filename = f"Raport_{safe_name}_{date_exam}.pdf"
    doc = SimpleDocTemplate(output_filename, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # nagłówek (belka)
    header_html = f"<b>Raport trichoskopowy</b> &nbsp;&nbsp;&nbsp; Pacjent: <b>{patient_name}</b> &nbsp;&nbsp;&nbsp; Data badania: <b>{date_exam}</b> &nbsp;&nbsp;&nbsp; Wygenerowano: {datetime.date.today().isoformat()}"
    elements.append(Paragraph(header_html, styles["Normal"]))
    elements.append(Spacer(1, 0.4*cm))

    # obrazy (miniatury) w jednej linii
    imgs = []
    for i,m in enumerate(metrics_list):
        temp_path = f"__preview_{i}.png"
        m["preview_image"].save(temp_path)
        rlimg = RLImage(temp_path, width=5*cm, height=5*cm)
        imgs.append(rlimg)
    table_imgs = Table([imgs], colWidths=[6*cm,6*cm,6*cm], hAlign="CENTER")
    elements.append(table_imgs)
    elements.append(Spacer(1, 0.5*cm))

    # tabela wyników
    header = ["Parametr", "Frontal", "Temporal", "Occipital"]
    data = [header]
    rows = [
        ("Średnia liczba włosów [N]","liczba_włosów"),
        ("Średnia grubość łodygi [µm]","średnia_grubość_um"),
        ("Cienkie (<30µm) [N]","cienkie"),
        ("Średnie (30-50µm) [N]","srednie"),
        ("Grube (>50µm) [N]","grube"),
        ("Pojedyncze jednostki [N]","single_units"),
        ("Podwójne jednostki [N]","double_units"),
        ("Potrójne+ jednostki [N]","triple_plus"),
        ("Szac. puste mieszki [N]","empty_estimate"),
    ]
    for label, key in rows:
        vals = []
        for m in metrics_list:
            vals.append(str(m.get(key, 0)))
        data.append([label] + vals)

    table = Table(data, colWidths=[7*cm,3*cm,3*cm,3*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0), colors.HexColor("#d9edf7")),
        ('GRID',(0,0),(-1,-1),0.5, colors.black),
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
        ('ALIGN',(1,1),(-1,-1),'CENTER'),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.5*cm))

    # wnioski automatyczne i komentarz
    auto_conc = generate_conclusion(metrics_list[0], metrics_list[1], metrics_list[2])
    elements.append(Paragraph("<b>Wnioski (automatyczne):</b>", styles["Heading3"]))
    elements.append(Paragraph(auto_conc, styles["Normal"]))
    elements.append(Spacer(1, 0.3*cm))
    elements.append(Paragraph("<b>Twój komentarz (edytowalny):</b>", styles["Heading4"]))
    elements.append(Paragraph(user_comment.replace("\n", "<br/>"), styles["Normal"]))

    # stopka z logo (lewy dolny) i danymi (prawy dolny)
    elements.append(Spacer(1, 1.2*cm))
    # przygotuj dane stopki w tabeli 2 kolumny
    footer_parts = []
    if logo_path and os.path.exists(logo_path):
        try:
            footer_logo = RLImage(logo_path, width=3*cm, height=3*cm)
        except Exception:
            footer_logo = Paragraph("", styles["Normal"])
    else:
        footer_logo = Paragraph("", styles["Normal"])
    footer_text = Paragraph("TRYCHOLOG Monika Semborska<br/>semborska.trychologia@gmail.com<br/>IG: @semborska.trychologia", styles["Normal"])
    footer_table = Table([[footer_logo, footer_text]], colWidths=[3*cm,12*cm])
    footer_table.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
    elements.append(footer_table)

    doc.build(elements)

    # usuń tymczasowe obrazy preview
    for i in range(len(metrics_list)):
        tp = f"__preview_{i}.png"
        if os.path.exists(tp):
            try:
                os.remove(tp)
            except:
                pass

# ---------- GUI ----------
class App:
    def __init__(self, root):
        self.root = root
        root.title("Analiza trichoskopowa - TRYCHOLOG")
        root.geometry("980x720")
        self.style = ttk.Style(root)

        # ramka górna: dane pacjenta
        frm = ttk.Frame(root, padding=10)
        frm.pack(fill="x")
        ttk.Label(frm, text="Imię:").grid(row=0, column=0, sticky="e")
        self.entry_name = ttk.Entry(frm, width=25)
        self.entry_name.grid(row=0, column=1, padx=5)
        ttk.Label(frm, text="Nazwisko:").grid(row=0, column=2, sticky="e")
        self.entry_surname = ttk.Entry(frm, width=25)
        self.entry_surname.grid(row=0, column=3, padx=5)
        ttk.Label(frm, text="Data badania (RRRR-MM-DD):").grid(row=1, column=0, sticky="e")
        self.entry_date = ttk.Entry(frm, width=20)
        self.entry_date.grid(row=1, column=1, padx=5)
        self.entry_date.insert(0, datetime.date.today().isoformat())

        # ścieżki do zdjęć
        frm2 = ttk.Frame(root, padding=10)
        frm2.pack(fill="x")
        ttk.Label(frm2, text="Frontal:").grid(row=0, column=0, sticky="e")
        self.frontal_var = tk.StringVar()
        ttk.Entry(frm2, textvariable=self.frontal_var, width=70).grid(row=0, column=1)
        ttk.Button(frm2, text="Wybierz", command=self.choose_frontal).grid(row=0, column=2, padx=5)

        ttk.Label(frm2, text="Temporal:").grid(row=1, column=0, sticky="e")
        self.temporal_var = tk.StringVar()
        ttk.Entry(frm2, textvariable=self.temporal_var, width=70).grid(row=1, column=1)
        ttk.Button(frm2, text="Wybierz", command=self.choose_temporal).grid(row=1, column=2, padx=5)

        ttk.Label(frm2, text="Occipital:").grid(row=2, column=0, sticky="e")
        self.occipital_var = tk.StringVar()
        ttk.Entry(frm2, textvariable=self.occipital_var, width=70).grid(row=2, column=1)
        ttk.Button(frm2, text="Wybierz", command=self.choose_occipital).grid(row=2, column=2, padx=5)

        # przyciski
        frm3 = ttk.Frame(root, padding=10)
        frm3.pack(fill="x")
        ttk.Button(frm3, text="Analizuj", command=self.analyze_all).grid(row=0, column=0, padx=5)
        ttk.Button(frm3, text="Generuj PDF", command=self.save_pdf).grid(row=0, column=1, padx=5)

        # panel wyników – tabela uproszczona i komentarz
        frm4 = ttk.Frame(root, padding=10)
        frm4.pack(fill="both", expand=True)
        ttk.Label(frm4, text="Podsumowanie (szybki widok):").pack(anchor="w")
        self.summary_label = ttk.Label(frm4, text="", justify="left")
        self.summary_label.pack(anchor="w", pady=(5,10))

        ttk.Label(frm4, text="Komentarz (możesz edytować):").pack(anchor="w")
        self.comment_text = tk.Text(frm4, height=8)
        self.comment_text.pack(fill="both", expand=True, pady=(5,0))

        self.metrics = [None, None, None]

    def choose_frontal(self):
        p = filedialog.askopenfilename(title="Wybierz zdjęcie frontal", filetypes=[("Obrazy","*.jpg;*.png;*.jpeg;*.bmp")])
        if p:
            self.frontal_var.set(p)

    def choose_temporal(self):
        p = filedialog.askopenfilename(title="Wybierz zdjęcie temporal", filetypes=[("Obrazy","*.jpg;*.png;*.jpeg;*.bmp")])
        if p:
            self.temporal_var.set(p)

    def choose_occipital(self):
        p = filedialog.askopenfilename(title="Wybierz zdjęcie occipital", filetypes=[("Obrazy","*.jpg;*.png;*.jpeg;*.bmp")])
        if p:
            self.occipital_var.set(p)

    def analyze_all(self):
        paths = [self.frontal_var.get(), self.temporal_var.get(), self.occipital_var.get()]
        for p in paths:
            if not p or not os.path.exists(p):
                messagebox.showerror("Błąd", "Uzupełnij wszystkie 3 zdjęcia przed analizą.")
                return
        try:
            # analiza dokładna - może chwilę potrwać
            self.root.config(cursor="watch")
            self.root.update()
            m0 = analyze_image(paths[0])
            m1 = analyze_image(paths[1])
            m2 = analyze_image(paths[2])
            self.metrics = [m0, m1, m2]
            # podsumowanie tekstowe
            summ = f"Frontal: {m0['liczba_włosów']} włosów, śr. grubość {m0['średnia_grubość_um']} µm\n"
            summ += f"Temporal: {m1['liczba_włosów']} włosów, śr. grubość {m1['średnia_grubość_um']} µm\n"
            summ += f"Occipital: {m2['liczba_włosów']} włosów, śr. grubość {m2['średnia_grubość_um']} µm\n"
            self.summary_label.config(text=summ)
            auto = generate_conclusion(m0, m1, m2)
            self.comment_text.delete("1.0", tk.END)
            self.comment_text.insert(tk.END, auto)
            messagebox.showinfo("Gotowe", "Analiza zakończona. Możesz edytować komentarz i kliknąć Generuj PDF.")
        except Exception as e:
            messagebox.showerror("Błąd analizy", str(e))
        finally:
            self.root.config(cursor="")

    def save_pdf(self):
        if not all(self.metrics):
            messagebox.showerror("Błąd", "Przeprowadź analizę zanim zapiszesz PDF.")
            return
        name = self.entry_name.get().strip()
        surname = self.entry_surname.get().strip()
        if not name or not surname:
            messagebox.showerror("Błąd", "Wpisz imię i nazwisko pacjenta.")
            return
        patient = f"{name} {surname}"
        date_exam = self.entry_date.get().strip() or datetime.date.today().isoformat()
        comment = self.comment_text.get("1.0", tk.END).strip()
        # nazwa pliku: Raport_ImieNazwisko.pdf
        safe = (name + surname).replace(" ", "_")
        default_filename = f"Raport_{safe}_{date_exam}.pdf"
        outpath = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile=default_filename,
                                               filetypes=[("PDF","*.pdf")])
        if not outpath:
            return
        generate_pdf(patient, date_exam, self.metrics, comment, LOGO_FILE, output_filename=outpath)
        messagebox.showinfo("Zapisano", f"Raport zapisano jako:\n{outpath}")

def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
