import re, os, shutil
from tkinter import Tk, filedialog
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer
from reportlab.lib import colors
from reportlab.lib.units import mm
from datetime import datetime

# --- Klasör seçici ---
Tk().withdraw()
folder = filedialog.askdirectory(title="Bir klasor sec (.MPF dosyalari olan)")
if not folder:
    print("❌ Klasor secilmedi!")
    raise SystemExit

# --- Tablo Başlıkları ---
headers = ["TREN NO","IS EMRI","AKS (Dingil ID)",
           "CAP SOL","CAP SAG",
           "SD SOL","SD SAG",
           "QR SOL","QR SAG",
           "SH SOL","SH SAG",
           "RS SOL","RS SAG",
           "AS SOL","AS SAG"]

rows = []
tren_no_global = ""   # ilk bulunan SetID için
processed_mpf_files = []

# --- Klasördeki tüm .MPF dosyalarını işle ---
for fname in os.listdir(folder):
    if fname.lower().endswith(".mpf"):
        fpath = os.path.join(folder, fname)
        processed_mpf_files.append(fpath)

        # Dosyayı oku (UTF-8 değilse karakter hatalarını yut)
        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.read().splitlines()

        tren_no, aks, is_emri = "", "", ""
        cap_sol = cap_sag = ""
        sd_sol = sd_sag = ""
        qr_sol = qr_sag = ""
        sh_sol = sh_sag = ""
        rs_sol = rs_sag = ""
        as_sol = as_sag = ""

        include_section = False
        for ln in lines:
            # Kimlik bilgileri
            if "Matricola sala" in ln:  # Aks numarası
                aks = re.findall(r"\d+", ln)
                aks = aks[0] if aks else ""
            if "Ordine di lavoro" in ln:  # İş emri
                is_emri = ln.split(":")[-1].strip()
            if "Matricola veicolo" in ln:  # Tren/Set ID
                tren_id = re.findall(r"\d+", ln)
                tren_no = tren_id[0] if tren_id else ""
                if not tren_no_global:
                    tren_no_global = tren_no  # ilk bulunan SetID

            # Son Ölçüler bölümü
            if "MISURE FINALI" in ln or "SON OLCULER" in ln:
                include_section = True
                continue
            if not include_section:
                continue

            nums = re.findall(r"[-+]?\d*\.\d+|\d+", ln)

            if "Diametro ruota" in ln and len(nums) == 2:
                cap_sol, cap_sag = nums
            if "Spessore bordino" in ln and len(nums) == 2:
                sd_sol, sd_sag = nums
            if "Quota trasversale" in ln and len(nums) == 2:
                qr_sol, qr_sag = nums
            if "Altezza bordino" in ln and len(nums) == 2:
                sh_sol, sh_sag = nums
            if "Oscillazione radiale" in ln and len(nums) == 2:
                rs_sol, rs_sag = nums
            if "Oscillazione assiale" in ln and len(nums) == 2:
                as_sol, as_sag = nums
                # ✅ Satır tamamlandı
                rows.append([
                    tren_no, is_emri, aks,
                    cap_sol, cap_sag,
                    sd_sol, sd_sag,
                    qr_sol, qr_sag,
                    sh_sol, sh_sag,
                    rs_sol, rs_sag,
                    as_sol, as_sag
                ])
                include_section = False  # reset

if not processed_mpf_files:
    print("❌ Klasörde .mpf dosyası bulunamadı.")
    raise SystemExit

# 🔹 Aks numarasına göre küçükten büyüğe sırala
def _ax_key(x):
    try:
        return int(x[2])
    except:
        return 999999
rows_sorted = sorted(rows, key=_ax_key)

# --- PDF ve MPF yeni isimlerle kaydet ---
set_id = tren_no_global if tren_no_global else "SET"
tarih = datetime.now().strftime("%Y-%m-%d_%H%M")

# PDF dosyası
pdf_file = os.path.join(folder, f"{set_id}_{tarih}.pdf")

# Tüm mpf dosyalarını yeni isimlerle kopyala: {SET}_{TARIH}_1.mpf, _2.mpf ...
for idx, mpf_path in enumerate(processed_mpf_files, start=1):
    base, ext = os.path.splitext(os.path.basename(mpf_path))
    yeni_mpf = os.path.join(folder, f"{set_id}_{tarih}_{idx}{ext}")
    shutil.copy2(mpf_path, yeni_mpf)

# --- PDF oluştur (yatay sayfa, ortalanmış tablo) ---
table_data = [headers] + rows_sorted

doc = SimpleDocTemplate(
    pdf_file,
    pagesize=landscape(A4),
    leftMargin=6*mm, rightMargin=6*mm,
    topMargin=6*mm, bottomMargin=6*mm
)

# sütun genişlikleri
col_widths = [22*mm,22*mm,20*mm] + [16*mm]*12

t = Table(table_data, repeatRows=1, colWidths=col_widths, hAlign="CENTER")
t.setStyle(TableStyle([
    ("GRID", (0,0), (-1,-1), 0.4, colors.black),
    ("BOX", (0,0), (-1,-1), 1.0, colors.black),
    ("BACKGROUND", (0,0), (-1,0), colors.lightblue),
    ("ALIGN", (0,0), (-1,-1), "CENTER"),
    ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
    ("FONTSIZE", (0,0), (-1,-1), 7),
]))

doc.build([Spacer(1,5*mm), t, Spacer(1,5*mm)])
print("✅ PDF ve tum MPF dosyalari kaydedildi:", pdf_file)