import sys, os, io, sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, Image
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from barcode import Code128
from barcode.writer import ImageWriter

def resource_path(relative_path: str) -> str:
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ----- BAZA PODATAKA -----
def inicijalizuj_bazu():
    conn = sqlite3.connect("roletne.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS nalozi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            naziv TEXT,
            datum TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS roletne (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nalog_id INTEGER,
            redni_broj INTEGER,
            tip TEXT,
            sirina REAL,
            visina REAL,
            kolicina INTEGER,
            kutija137 TEXT,
            kutija165 TEXT,
            boja TEXT,
            lamela_cm REAL,
            lamela_kom INTEGER,
            vodilica_cm REAL,
            vodilica_kom INTEGER,
            FOREIGN KEY(nalog_id) REFERENCES nalozi(id)
        )
    """)
    conn.commit()
    conn.close()

def upisi_u_bazu(naziv, datum):
    conn = sqlite3.connect("roletne.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO nalozi (naziv, datum) VALUES (?, ?)", (naziv, datum))
    nalog_id = cur.lastrowid
    for i, e in enumerate(entries):
        try:
            if e["tip"].get() == "PODJELA":
                continue
            cur.execute("""
                INSERT INTO roletne (nalog_id, redni_broj, tip, sirina, visina, kolicina,
                    kutija137, kutija165, boja, lamela_cm, lamela_kom, vodilica_cm, vodilica_kom)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                nalog_id, i + 1, e["tip"].get(), float(e["sirina"].get()), float(e["visina"].get()),
                int(e["kolicina"].get()), e["kutija137"].get(), e["kutija165"].get(), e["boja"].get(),
                float(e["lamela_cm"].cget("text")), int(e["lamela_kom"].cget("text")),
                float(e["vodilica_cm"].cget("text")), int(e["vodilica_kom"].cget("text"))
            ))
        except Exception:
            continue
    conn.commit()
    conn.close()

def obrisi_nalog_iz_baze(nalog_id):
    conn = sqlite3.connect("roletne.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM roletne WHERE nalog_id = ?", (nalog_id,))
    cur.execute("DELETE FROM nalozi WHERE id = ?", (nalog_id,))
    conn.commit()
    conn.close()

def ucitaj_nalog_iz_baze(nalog_id):
    conn = sqlite3.connect("roletne.db")
    cur = conn.cursor()
    cur.execute("SELECT naziv FROM nalozi WHERE id = ?", (nalog_id,))
    naziv = cur.fetchone()[0]
    naziv_naloga_var.set(naziv)

    cur.execute("SELECT tip, sirina, visina, kolicina, kutija137, kutija165, boja FROM roletne WHERE nalog_id = ?", (nalog_id,))
    podaci = cur.fetchall()
    for i in range(20):
        if i < len(podaci):
            tip, sirina, visina, kolicina, k137, k165, boja = podaci[i]
            entries[i]["tip"].set(tip)
            entries[i]["sirina"].delete(0, tk.END)
            entries[i]["sirina"].insert(0, str(sirina))
            entries[i]["visina"].delete(0, tk.END)
            entries[i]["visina"].insert(0, str(visina))
            entries[i]["kolicina"].delete(0, tk.END)
            entries[i]["kolicina"].insert(0, str(kolicina))
            entries[i]["kutija137"].set(k137)
            entries[i]["kutija165"].set(k165)
            entries[i]["boja"].set(boja)
        else:
            entries[i]["tip"].set("OBICNA")
            entries[i]["sirina"].delete(0, tk.END)
            entries[i]["visina"].delete(0, tk.END)
            entries[i]["kolicina"].delete(0, tk.END)
            entries[i]["kutija137"].set("DA")
            entries[i]["kutija165"].set("NE")
            entries[i]["boja"].set("bijela")
    conn.close()
    izracunaj()

# ----- FUNKCIJE ZA FORMU -----
def novi_nalog():
    naziv_naloga_var.set("")
    utrosak_text.set("")
    for e in entries:
        e["tip"].set("OBICNA")
        e["sirina"].delete(0, tk.END)
        e["visina"].delete(0, tk.END)
        e["kolicina"].delete(0, tk.END)
        e["kutija137"].set("DA")
        e["kutija165"].set("NE")
        e["boja"].set("bijela")
        e["lamela_cm"].config(text="0")
        e["lamela_kom"].config(text="0")
        e["vodilica_cm"].config(text="0")
        e["vodilica_kom"].config(text="0")

def izracunaj():
    global lamela_po_bojama, vodilica_po_bojama, zavrsna_lamela_po_bojama
    global deklo137_po_bojama, deklo165_po_bojama
    global ukupno_roletni, ukupno_lamela_kom, ukupno_osovina_cm
    global kotur137, kotur165
    global ukupno_motor_taster, ukupno_motor_dalj

    for i in range(20):
        try:
            tip = entries[i]["tip"].get()
            if tip == "PODJELA":
                for key in ("lamela_cm", "lamela_kom", "vodilica_cm", "vodilica_kom"):
                    entries[i][key].config(text="—")
                continue

            sirina = float(entries[i]["sirina"].get())
            visina = float(entries[i]["visina"].get())
            kolicina = int(entries[i]["kolicina"].get())

            if visina > 150:
                entries[i]["kutija165"].set("DA")
                entries[i]["kutija137"].set("NE")
                vodilica_cm = visina - 16.5
            else:
                entries[i]["kutija165"].set("NE")
                entries[i]["kutija137"].set("DA")
                vodilica_cm = visina - 14

            lamela_cm = sirina - 7.5
            broj_lamela = round(visina / 3.9)

            entries[i]["lamela_cm"].config(text=f"{lamela_cm:.1f}")
            entries[i]["lamela_kom"].config(text=f"{broj_lamela * kolicina}")
            entries[i]["vodilica_cm"].config(text=f"{vodilica_cm:.1f}")
            entries[i]["vodilica_kom"].config(text=f"{2 * kolicina}")
        except Exception:
            for key in ("lamela_cm", "lamela_kom", "vodilica_cm", "vodilica_kom"):
                entries[i][key].config(text="0")

    prikazi_utrosak()

def prikazi_utrosak():
    global lamela_po_bojama, vodilica_po_bojama, zavrsna_lamela_po_bojama
    global deklo137_po_bojama, deklo165_po_bojama
    global ukupno_roletni, ukupno_lamela_kom, ukupno_osovina_cm
    global kotur137, kotur165
    global ukupno_motor_taster, ukupno_motor_dalj

    lamela_po_bojama = {}
    vodilica_po_bojama = {}
    zavrsna_lamela_po_bojama = {}

    deklo137_po_bojama = {}
    deklo165_po_bojama = {}

    ukupno_roletni = 0
    ukupno_lamela_kom = 0
    ukupno_osovina_cm = 0
    kotur137 = kotur165 = 0
    ukupno_motor_taster = 0
    ukupno_motor_dalj = 0

    for e in entries:
        try:
            if e["tip"].get() == "PODJELA":
                continue

            boja = e["boja"].get()
            sirina = float(e["sirina"].get())
            visina = float(e["visina"].get())
            kolicina = int(e["kolicina"].get())

            lamela_cm = sirina - 7.5
            broj_lamela = round(visina / 3.9)
            vodilica_cm = visina - (16.5 if visina > 150 else 14)

            ukupno_roletni += kolicina
            ukupno_lamela_kom += broj_lamela * kolicina
            ukupno_osovina_cm += (sirina - 5) * kolicina

            lamela_po_bojama[boja] = lamela_po_bojama.get(boja, 0) + lamela_cm * broj_lamela * kolicina
            vodilica_po_bojama[boja] = vodilica_po_bojama.get(boja, 0) + vodilica_cm * 2 * kolicina
            zavrsna_lamela_po_bojama[boja] = zavrsna_lamela_po_bojama.get(boja, 0) + lamela_cm * kolicina

            if e["kutija137"].get() == "DA":
                deklo137_po_bojama[boja] = deklo137_po_bojama.get(boja, 0) + 2 * kolicina
                kotur137 += 2 * kolicina
            if e["kutija165"].get() == "DA":
                deklo165_po_bojama[boja] = deklo165_po_bojama.get(boja, 0) + 2 * kolicina
                kotur165 += 2 * kolicina

            tip = e["tip"].get()
            if tip == "M TASTER":
                ukupno_motor_taster += kolicina
            elif tip == "M DALJ":
                ukupno_motor_dalj += kolicina

        except Exception:
            continue

    tekst = ""
    boje_redoslijed = ["bijela", "siva", "antracit", "coko", "hrast"]
    for boja in boje_redoslijed:
        if boja in lamela_po_bojama:
            tekst += (f"BOJA: {boja}\n"
                      f"  LAMELA: {lamela_po_bojama[boja] / 100:.2f} m\n"
                      f"  VODILICA: {vodilica_po_bojama.get(boja,0) / 100:.2f} m\n"
                      f"  ZAVRSNA LAMELA: {zavrsna_lamela_po_bojama.get(boja,0) / 100:.2f} m\n"
                      f"  DEKLO 137: {deklo137_po_bojama.get(boja,0)} kom\n"
                      f"  DEKLO 165: {deklo165_po_bojama.get(boja,0)} kom\n\n")

    tekst += (
        f"OSOVINA: {ukupno_osovina_cm / 100:.2f} m\n"
        f"CEP LAMELE: {ukupno_lamela_kom * 2} kom\n"
        f"KOTUR 137: {kotur137} kom\n"
        f"KOTUR 165: {kotur165} kom\n"
        f"CETKICA VODILICE: {sum(vodilica_po_bojama.values()) / 100:.2f} m\n"
        f"CETKICA ZAVRSNE: {sum(zavrsna_lamela_po_bojama.values()) / 100:.2f} m\n"
        f"VEZNIK LAMELE: {ukupno_roletni * 5} kom\n"
        f"LEZAJ: {ukupno_roletni * 2} kom\n"
        f"CEP OSOVINE: {ukupno_roletni * 2} kom\n"
        f"UVODNIK LAMELE: {ukupno_roletni * 2} kom\n"
        f"CEP ZAVRSNE: {ukupno_roletni * 2} kom\n"
        f"MOTOR TASTER: {ukupno_motor_taster} kom\n"
        f"MOTOR DALJ: {ukupno_motor_dalj} kom"
    )

    utrosak_text.set(tekst)

# ----- PDF GENERISANJE -----
def generisi_pdf(putanja, prikazi_materijal):
    naziv = naziv_naloga_var.get().strip()
    c = canvas.Canvas(putanja, pagesize=A4)
    width, height = A4
    x, y = 40, height - 40

    # Logo
    logo_path = resource_path("logo-bosfor-stil.png")
    if os.path.exists(logo_path):
        c.drawImage(logo_path, x, y - 50, width=120, height=40, mask='auto')
    else:
        c.setFont("Helvetica-Bold", 14)
        c.drawString(x, y - 25, "Bosfor Stil")

    # Barcode
    rv = io.BytesIO()
    Code128(naziv, writer=ImageWriter()).write(rv)
    barcode_img = Image.open(rv).resize((180, 50))
    c.drawImage(ImageReader(barcode_img), x, y - 100, width=180, height=50)

    y -= 120
    c.setFont("Helvetica-Bold", 14)
    c.drawString(x + 220, y + 80, f"Nalog: {naziv}")

    datum_sada = datetime.now().strftime("%d.%m.%Y")
    c.setFont("Helvetica", 12)
    c.drawString(x + 220, y + 60, f"Datum: {datum_sada}")

    y -= 30

    headers1 = ["Red", "Tip", "Sirina", "Visina", "Kolicina", "Kutija137", "Kutija165", "Boja", "Lamela", "", "Vodilica", ""]
    headers2 = ["", "", "", "", "", "", "", "", "(cm)", "(kom)", "(cm)", "(kom)"]
    x_pos = [x + i * 45 for i in range(len(headers1))]

    c.setFont("Helvetica-Bold", 9)
    for i, h in enumerate(headers1): c.drawString(x_pos[i], y, h)
    y -= 15
    for i, h in enumerate(headers2): c.drawString(x_pos[i], y, h)

    y -= 15
    c.setFont("Helvetica", 9)
    for i, e in enumerate(entries):
        tip = e["tip"].get()
        if tip == "PODJELA":
            continue
        try:
            sirina = e["sirina"].get()
            visina = e["visina"].get()
            kolicina = e["kolicina"].get()
            kutija137 = e["kutija137"].get()
            kutija165 = e["kutija165"].get()
            boja = e["boja"].get()
            lamela_cm = e["lamela_cm"].cget("text")
            lamela_kom = e["lamela_kom"].cget("text")
            vodilica_cm = e["vodilica_cm"].cget("text")
            vodilica_kom = e["vodilica_kom"].cget("text")

            data = [str(i + 1), tip, sirina, visina, kolicina, kutija137, kutija165, boja,
                    lamela_cm, lamela_kom, vodilica_cm, vodilica_kom]

            for idx, val in enumerate(data):
                c.drawString(x_pos[idx], y, str(val))
            y -= 15
            if y < 100:
                c.showPage()
                y = height - 40
        except Exception:
            continue

    if prikazi_materijal:
        y -= 20
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x, y, "Utrosak materijala:")
        y -= 20
        c.setFont("Helvetica", 10)
        for line in utrosak_text.get().split('\n'):
            c.drawString(x + 10, y, line)
            y -= 15
            if y < 100:
                c.showPage()
                y = height - 40

    c.save()

# ----- STILIZACIJA -----
def stilizuj_aplikaciju():
    style = ttk.Style()
    style.theme_use('clam')  # ili 'default', 'alt', 'classic', 'vista'...

    # Opšti font i veličina
    style.configure('.', font=('Segoe UI', 10))

    # Style za Button
    style.configure('TButton',
                    background='#4a90e2',
                    foreground='white',
                    padding=6,
                    font=('Segoe UI Semibold', 10))
    style.map('TButton',
              background=[('active', '#357ABD'), ('disabled', '#a9a9a9')],
              foreground=[('disabled', '#d3d3d3')])

    # Style za Combobox
    style.configure('TCombobox',
                    padding=4,
                    foreground='#333333')

    # Style za Treeview (ako koristiš)
    style.configure('Treeview',
                    background='white',
                    foreground='black',
                    fieldbackground='white',
                    font=('Segoe UI', 10))
    style.configure('Treeview.Heading',
                    font=('Segoe UI Semibold', 11, 'bold'),
                    foreground='#4a90e2')

    # Style za Entry
    style.configure('TEntry',
                    padding=4)

# ----- GLAVNI PROZOR -----
root = tk.Tk()
root.title("Konfigurator alu roletni - Bosfor Stil")
root.geometry("1150x680")
root.configure(bg='#f9f9f9')

stilizuj_aplikaciju()

# ----- Okviri -----
frame_header = ttk.Frame(root, padding=10)
frame_header.pack(fill=tk.X, padx=10, pady=5)

frame_table = ttk.Frame(root, padding=10)
frame_table.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

frame_buttons = ttk.Frame(root, padding=10)
frame_buttons.pack(fill=tk.X, padx=10, pady=5)

# ----- Naslov i unos naziva naloga -----
ttk.Label(frame_header, text="Naziv naloga:", font=('Segoe UI', 11, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
naziv_naloga_var = tk.StringVar()
entry_naziv = ttk.Entry(frame_header, textvariable=naziv_naloga_var, width=40)
entry_naziv.pack(side=tk.LEFT)

# ----- Tabela sa roletnama -----
canvas_table = tk.Canvas(frame_table, borderwidth=0, highlightthickness=0, bg='#ffffff')
scrollbar_y = ttk.Scrollbar(frame_table, orient="vertical", command=canvas_table.yview)
scrollbar_x = ttk.Scrollbar(frame_table, orient="horizontal", command=canvas_table.xview)
scrollable_frame = ttk.Frame(canvas_table)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas_table.configure(
        scrollregion=canvas_table.bbox("all")
    )
)

canvas_table.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas_table.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

canvas_table.pack(side="left", fill="both", expand=True)
scrollbar_y.pack(side="right", fill="y")
scrollbar_x.pack(side="bottom", fill="x")

# ----- Kreiranje redova -----
tipovi_roletni = ["OBICNA", "M TASTER", "M DALJ", "PODJELA"]
boje_roletni = ["bijela", "siva", "antracit", "coko", "hrast"]
da_ne = ["DA", "NE"]

entries = []
zaglavlje = ["#", "Tip", "Širina", "Visina", "Količina", "Kutija 137", "Kutija 165", "Boja",
             "Lamela (cm)", "Lamela (kom)", "Vodilica (cm)", "Vodilica (kom)"]

# Zaglavlje tabele
for col, text in enumerate(zaglavlje):
    lbl = ttk.Label(scrollable_frame, text=text, font=('Segoe UI Semibold', 10, 'bold'), background='#dce6f1', borderwidth=1, relief="solid", anchor='center')
    lbl.grid(row=0, column=col, sticky='nsew', padx=1, pady=1)

for i in range(20):
    row_entries = {}
    # redni broj
    lbl_br = ttk.Label(scrollable_frame, text=str(i+1), anchor='center', background='white', borderwidth=1, relief="solid")
    lbl_br.grid(row=i+1, column=0, sticky='nsew', padx=1, pady=1)
    row_entries["redni"] = lbl_br

    # Tip
    tip_var = tk.StringVar(value="OBICNA")
    cmb_tip = ttk.Combobox(scrollable_frame, values=tipovi_roletni, textvariable=tip_var, width=10, state="readonly")
    cmb_tip.grid(row=i+1, column=1, sticky='nsew', padx=1, pady=1)

    # Sirina
    ent_sirina = ttk.Entry(scrollable_frame, width=10)
    ent_sirina.grid(row=i+1, column=2, sticky='nsew', padx=1, pady=1)

    # Visina
    ent_visina = ttk.Entry(scrollable_frame, width=10)
    ent_visina.grid(row=i+1, column=3, sticky='nsew', padx=1, pady=1)

    # Kolicina
    ent_kolicina = ttk.Entry(scrollable_frame, width=10)
    ent_kolicina.grid(row=i+1, column=4, sticky='nsew', padx=1, pady=1)

    # Kutija 137
    kutija137_var = tk.StringVar(value="DA")
    cmb_kutija137 = ttk.Combobox(scrollable_frame, values=da_ne, textvariable=kutija137_var, width=5, state="readonly")
    cmb_kutija137.grid(row=i+1, column=5, sticky='nsew', padx=1, pady=1)

    # Kutija 165
    kutija165_var = tk.StringVar(value="NE")
    cmb_kutija165 = ttk.Combobox(scrollable_frame, values=da_ne, textvariable=kutija165_var, width=5, state="readonly")
    cmb_kutija165.grid(row=i+1, column=6, sticky='nsew', padx=1, pady=1)

    # Boja
    boja_var = tk.StringVar(value="bijela")
    cmb_boja = ttk.Combobox(scrollable_frame, values=boje_roletni, textvariable=boja_var, width=10, state="readonly")
    cmb_boja.grid(row=i+1, column=7, sticky='nsew', padx=1, pady=1)

    # Lamela (cm)
    lbl_lamela_cm = ttk.Label(scrollable_frame, text="0", anchor='center', background='white', borderwidth=1, relief="solid")
    lbl_lamela_cm.grid(row=i+1, column=8, sticky='nsew', padx=1, pady=1)

    # Lamela (kom)
    lbl_lamela_kom = ttk.Label(scrollable_frame, text="0", anchor='center', background='white', borderwidth=1, relief="solid")
    lbl_lamela_kom.grid(row=i+1, column=9, sticky='nsew', padx=1, pady=1)

    # Vodilica (cm)
    lbl_vodilica_cm = ttk.Label(scrollable_frame, text="0", anchor='center', background='white', borderwidth=1, relief="solid")
    lbl_vodilica_cm.grid(row=i+1, column=10, sticky='nsew', padx=1, pady=1)

    # Vodilica (kom)
    lbl_vodilica_kom = ttk.Label(scrollable_frame, text="0", anchor='center', background='white', borderwidth=1, relief="solid")
    lbl_vodilica_kom.grid(row=i+1, column=11, sticky='nsew', padx=1, pady=1)

    row_entries.update({
        "tip": tip_var,
        "sirina": ent_sirina,
        "visina": ent_visina,
        "kolicina": ent_kolicina,
        "kutija137": kutija137_var,
        "kutija165": kutija165_var,
        "boja": boja_var,
        "lamela_cm": lbl_lamela_cm,
        "lamela_kom": lbl_lamela_kom,
        "vodilica_cm": lbl_vodilica_cm,
        "vodilica_kom": lbl_vodilica_kom
    })

    entries.append(row_entries)

# Podesi širine kolona da budu jednako raspoređene
for col in range(len(zaglavlje)):
    scrollable_frame.grid_columnconfigure(col, weight=1, uniform='col')

# ----- Tekst za utrošak -----
utrosak_text = tk.StringVar()
label_utrosak = ttk.Label(root, textvariable=utrosak_text, justify="left", background='#f9f9f9', font=('Segoe UI', 10))
label_utrosak.pack(fill=tk.X, padx=10, pady=(5,10))

# ----- Dugmad -----
btn_izracunaj = ttk.Button(frame_buttons, text="Izračunaj", command=izracunaj)
btn_izracunaj.pack(side=tk.LEFT, padx=5)

def stampaj_bez_materijala():
    folder = os.path.join(os.path.expanduser("~"), "Desktop", "konfigurator roletni")
    os.makedirs(folder, exist_ok=True)
    putanja = os.path.join(folder, f"{naziv_naloga_var.get().strip()}_bez_materijala.pdf")
    generisi_pdf(putanja, False)
    # Otvori folder nakon štampe
    if sys.platform == "win32":
        os.startfile(folder)
    elif sys.platform == "darwin":
        os.system(f"open '{folder}'")
    else:
        os.system(f"xdg-open '{folder}'")

btn_stampaj_bez = ttk.Button(frame_buttons, text="Štampaj bez materijala", command=stampaj_bez_materijala)
btn_stampaj_bez.pack(side=tk.LEFT, padx=5)

def prikazi_materijal_i_stampaj():
    folder = os.path.join(os.path.expanduser("~"), "Desktop", "konfigurator roletni")
    os.makedirs(folder, exist_ok=True)
    putanja = os.path.join(folder, f"{naziv_naloga_var.get().strip()}_sa_materijalom.pdf")
    generisi_pdf(putanja, True)
    # Otvori folder nakon štampe
    if sys.platform == "win32":
        os.startfile(folder)
    elif sys.platform == "darwin":
        os.system(f"open '{folder}'")
    else:
        os.system(f"xdg-open '{folder}'")

btn_prikazi_materijal = ttk.Button(frame_buttons, text="Prikaži materijal i štampaj", command=prikazi_materijal_i_stampaj)
btn_prikazi_materijal.pack(side=tk.LEFT, padx=5)

btn_novi = ttk.Button(frame_buttons, text="Novi nalog", command=novi_nalog)
btn_novi.pack(side=tk.RIGHT, padx=5)

# ----- Start -----
inicijalizuj_bazu()

root.mainloop()
