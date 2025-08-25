import re, os
from tkinter import Tk, filedialog
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer
from reportlab.lib import colors
from reportlab.lib.units import mm

# --- Klasör seçici ---
Tk().withdraw()
folder = filedialog.askdirectory(title="Bir klasor sec (.MPF dosyalari olan)")
if not folder:
    print("❌ Klasor secilmedi!")
    exit()

pdf_file = os.path.join(folder, "BIRLESIK_SON_OLCULER.pdf")

# --- Tablo Başlıkları ---
headers = ["TREN NO","IS EMRI","AKS (Dingil ID)",
           "CAP SOL","CAP SAG",
           "SD SOL","SD SAG",
           "QR SOL","QR SAG",
           "SH SOL","SH SAG",
           "RS SOL","RS SAG",
           "AS SOL","AS SAG"]

rows = []

# --- Klasördeki tüm .MPF dosyalarını işle ---
for fname in os.listdir(folder):
    if fname.lower().endswith(".mpf"):
        fpath = os.path.join(folder, fname)
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
            if "Matricola veicolo" in ln:  # Tren numarası
                tren_id = re.findall(r"\d+", ln)
                tren_no = tren_id[0] if tren_id else ""

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

# 🔹 Aks numarasına göre küçükten büyüğe sırala
rows_sorted = sorted(rows, key=lambda x: int(x[2]) if x[2].isdigit() else 9999)

# --- PDF oluştur (yatay sayfa, ortalanmış tablo) ---
table_data = [headers] + rows_sorted

doc = SimpleDocTemplate(pdf_file, pagesize=landscape(A4),
                        leftMargin=6*mm, rightMargin=6*mm,
                        topMargin=6*mm, bottomMargin=6*mm)

# sütun genişlikleri
col_widths = [22*mm,22*mm,20*mm] + [16*mm]*12

t = Table(table_data, repeatRows=1, colWidths=col_widths, hAlign="CENTER")
t.setStyle(TableStyle([
    ("GRID", (0,0), (-1,-1), 0.4, colors.black),      # hücre ızgaraları
    ("BOX", (0,0), (-1,-1), 1.0, colors.black),       # dış çerçeve
    ("BACKGROUND", (0,0), (-1,0), colors.lightblue),  # başlık arka planı
    ("ALIGN", (0,0), (-1,-1), "CENTER"),              # ortalama
    ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
    ("FONTSIZE", (0,0), (-1,-1), 7),
]))

doc.build([Spacer(1,5*mm), t, Spacer(1,5*mm)])
print("✅ Ortalanmış ve kenarlıklı PDF hazır:", pdf_file)