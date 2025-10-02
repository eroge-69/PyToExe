#!/usr/bin/env python
# coding: utf-8

# In[73]:


import os, csv, textwrap
from io import BytesIO
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PyPDF2 import PdfReader, PdfWriter

# ---------- Ayarlar ----------
TEMPLATE_PDF = "DanismanFormu.pdf"
OUTPUT_DIR = "output"
RECORDS_CSV ="records.csv"

coords = {
    "danisman":      (250, (29.7-6.3)/0.036),
    "ogrenci_ad":    (250, (29.7-7.3)/0.036),
    "ogrenci_no":    (250, (29.7-8.4)/0.036),
    "sinif":         (250, (29.7-9.4)/0.036),
    "email":         (250, (29.7-10.4)/0.036),
    "telefon":       (250, (29.7-11.4)/0.036),
    "adres":         (250, (29.7-12.4)/0.036),
    "konu":          (250, (29.7-13.5)/0.036),
    "oneriler":      (50,  (29.7-14.8)/0.036),
    "tarih":         (250, (29.7-26.8)/0.036),
    "danisman_imza": (250, (29.7-27.8)/0.036),
    "ogrenci_imza":  (250, (29.7-28.8)/0.036)
}
FIELD_ORDER = [
    "danisman", 
    "ogrenci_ad", 
    "ogrenci_no", 
    "sinif", 
    "email", 
    "telefon",
    "adres", 
    "konu", 
    "oneriler", 
    "tarih", 
    "pdf_file"
   
]
def append_record(csv_path, record):
    header = FIELD_ORDER
    exists = os.path.exists(csv_path)
    with open(csv_path, "a", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=header)
        if not exists:
            writer.writeheader()
        writer.writerow({key: record.get(key, "") for key in header})

pdfmetrics.registerFont(TTFont("DejaVuSans", "DejaVuSans.ttf"))
FONT_NAME = "DejaVuSans"
FONT_SIZE = 10
MULTILINE_FONT_SIZE = 9
LINE_SPACING = 14
SIGNATURE_MAX_WIDTH = 120
SIGNATURE_MAX_HEIGHT = 40

def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def place_image_on_canvas(c, img_path, x, y):
    img = Image.open(img_path)
    img_w, img_h = img.size
    scale = min(SIGNATURE_MAX_WIDTH / img_w, SIGNATURE_MAX_HEIGHT / img_h, 1.0)
    draw_w, draw_h = img_w * scale, img_h * scale
    if img.format is None:
        img = img.convert("RGB")
    bi = BytesIO()
    img.save(bi, format="PNG")
    bi.seek(0)
    c.drawImage(bi, x, y, width=draw_w, height=draw_h, preserveAspectRatio=True, mask='auto')

def create_overlay(page_width, page_height, data, coords, sig_paths=None):
    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=(page_width, page_height))
    c.setFont(FONT_NAME, FONT_SIZE)

    for key in ("danisman","ogrenci_ad","ogrenci_no","sinif","email","telefon","adres","konu","oneriler","tarih"):
        if key in coords:
            x, y = coords[key]
            c.drawString(x, y, str(data.get(key, "")))

    if "oneriler" in coords:
        x_o, y_o = coords["oneriler"]
        text_obj = c.beginText(x_o, y_o)
        text_obj.setFont(FONT_NAME, MULTILINE_FONT_SIZE)
        text_obj.setLeading(LINE_SPACING)
        metin = str(data.get("oneriler", "")[:2000])
        satirlar = []
        for line in metin.splitlines():
            satirlar.extend(textwrap.wrap(line, width=90))
        for line in satirlar:
            text_obj.textLine(line)
        c.drawText(text_obj)

    for role in ("danisman", "ogrenci"):
        sig_key = f"{role}_imza"
        if sig_paths and sig_paths.get(role) and sig_key in coords:
            try:
                x, y = coords[sig_key]
                place_image_on_canvas(c, sig_paths[role], x, y)
            except Exception:
                c.drawString(x, y, data.get(sig_key, ""))
        elif sig_key in coords:
            c.drawString(coords[sig_key][0], coords[sig_key][1], data.get(sig_key, ""))

    c.save()
    packet.seek(0)
    return packet

def merge_overlay_to_pdf(template_path, overlay_stream, output_path, page_number=0):
    reader = PdfReader(template_path)
    writer = PdfWriter()
    overlay_reader = PdfReader(overlay_stream)
    overlay_page = overlay_reader.pages[0]
    base_page = reader.pages[page_number]
    base_page.merge_page(overlay_page)
    writer.add_page(base_page)
    for p in reader.pages[1:]:
        writer.add_page(p)
    with open(output_path, "wb") as f:
        writer.write(f)

def append_record(csv_path, record):
    header = list(record.keys())  # Tüm alanları otomatik al
    exists = os.path.exists(csv_path)
    with open(csv_path, "a", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=header)
        if not exists:
            writer.writeheader()
        writer.writerow(record)

class FillFormApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("KTÜ İnşaat Mühendisliği Bölümü Öğrenci Danışmanlık Formu")
        self.geometry("720x700")
        self.resizable(False, False)
        self.sig_paths = {"danisman": None, "ogrenci": None}
        self.create_widgets()

    def create_widgets(self):
        frm = ttk.Frame(self, padding=12)
        frm.pack(fill=tk.BOTH, expand=True)

        labels = [
            ("Danışman Adı Soyadı","danisman"),
            ("Öğrenci Adı Soyadı", "ogrenci_ad"),
            ("Öğrenci Numarası", "ogrenci_no"),
            ("Öğrenci Sınıfı", "sinif"),
            ("Öğrenci E-posta", "email"),
            ("Öğrenci Telefon", "telefon"),
            ("Öğrenci Yazışma Adresi", "adres"),
            ("Görüşme Konusu", "konu"),
            ("Görüşmeye İlişkin Öneri / Çözüm / Yardım", "oneriler"),
            ("Görüşme Tarihi", "tarih"),
        ]

        self.vars = {}
        r = 0
        for lbl, key in labels:
            ttk.Label(frm, text=lbl).grid(row=r, column=0, sticky="w", pady=4)
            if key == "oneriler":
                txt = tk.Text(frm, width=60, height=8)
                txt.grid(row=r, column=1, rowspan=2, sticky="w", padx=6)
                txt.bind("<KeyRelease>", lambda e: self.karakter_kontrol("oneriler"))
                self.vars[key] = txt
                self.char_label = ttk.Label(frm, text="Kalan karakter: 2000", foreground="gray")
                self.char_label.grid(row=r+2, column=1, sticky="w", padx=6)
                r += 3
            else:
                ent = ttk.Entry(frm, width=50)
                ent.grid(row=r, column=1, sticky="w", padx=6)
                self.vars[key] = ent
                r += 1

        ttk.Button(frm, text="Danışman İmza", command=self.load_sig_d).grid(row=r, column=1, sticky="w")
        r += 1
        ttk.Button(frm, text="Öğrenci İmza", command=self.load_sig_s).grid(row=r, column=1, sticky="w")
        r += 1

        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=r, column=0, columnspan=2, pady=12)
        ttk.Button(btn_frame, text="Önizleme", command=self.preview).grid(row=0, column=0, padx=6)
        ttk.Button(btn_frame, text="Kaydet", command=self.fill_and_save).grid(row=0, column=1, padx=6)
        #ttk.Button(btn_frame, text="Dosyadan Yükle", command=self.load_from_file).grid(row=0, column=2, padx=6)
        ttk.Button(btn_frame, text="Çıkış", command=self.on_exit).grid(row=0, column=3, padx=6)
        ttk.Button(btn_frame, text="Kayıttan Yükle", command=self.load_from_csv).grid(row=0, column=4, padx=6)
        ttk.Button(btn_frame, text="Kayıtları Listele", command=self.show_records).grid(row=0, column=5, padx=6)

        self.vars["tarih"].insert(0, datetime.now().strftime("%d/%m/%Y"))
    
    def karakter_kontrol(self, key):
        widget = self.vars[key]
        metin = widget.get("1.0", "end-1c")
        kalan = 2000 - len(metin)
        if kalan < 0:
            widget.delete("1.0", "end")
            widget.insert("1.0", metin[:2000])
            kalan = 0
            messagebox.showwarning("Sınır Aşıldı", "En fazla 2000 karakter girebilirsiniz.")
        self.char_label.config(text=f"Kalan karakter: {kalan}", foreground="red" if kalan == 0 else "gray")

    def on_exit(self):
        metin = self.vars["oneriler"].get("1.0", "end-1c").strip()
        if metin:
            cevap = messagebox.askyesno("Çıkış", "Öneriler alanı dolu. Yine de çıkmak istiyor musunuz?")
        else:
            cevap = messagebox.askyesno("Çıkış", "Formdan çıkmak istiyor musunuz?")
        if cevap:
            self.destroy()

    def load_sig_d(self):
        path = filedialog.askopenfilename(filetypes=[("Resim Dosyaları", "*.png;*.jpg;*.jpeg;*.bmp")])
        if path:
            self.sig_paths["danisman"] = path
            messagebox.showinfo("İmza", f"Danışman imzası yüklendi:\n{os.path.basename(path)}")

    def load_sig_s(self):
        path = filedialog.askopenfilename(filetypes=[("Resim Dosyaları", "*.png;*.jpg;*.jpeg;*.bmp")])
        if path:
            self.sig_paths["ogrenci"] = path
            messagebox.showinfo("İmza", f"Öğrenci imzası yüklendi:\n{os.path.basename(path)}")

    def collect_data(self):
        data = {}
        for k, w in self.vars.items():
            if isinstance(w, tk.Text):
                data[k] = w.get("1.0", tk.END).strip()
            else:
                data[k] = w.get().strip()
        if not data.get("ogrenci_no") or not data.get("ogrenci_ad"):
            raise ValueError("Öğrenci adı ve numarası girilmelidir.")
        data["danisman_imza"] = data.get("danisman", "")
        data["ogrenci_imza"] = data.get("ogrenci_ad", "")
        return data

    def preview(self):
        try:
            data = self.collect_data()
            reader = PdfReader(TEMPLATE_PDF)
            page0 = reader.pages[0]
            pw = float(page0.mediabox.width)
            ph = float(page0.mediabox.height)
            overlay = create_overlay(pw, ph, data, coords, sig_paths=self.sig_paths)
            tmp_out = os.path.join(OUTPUT_DIR, "preview.pdf")
            ensure_output_dir()
            merge_overlay_to_pdf(TEMPLATE_PDF, overlay, tmp_out)
            messagebox.showinfo("Önizleme", f"Önizleme oluşturuldu:\n{tmp_out}")
        except Exception as e:
            messagebox.showerror("Hata", str(e))

    def fill_and_save(self):
        try:
            data = self.collect_data()
            reader = PdfReader(TEMPLATE_PDF)
            page0 = reader.pages[0]
            pw = float(page0.mediabox.width)
            ph = float(page0.mediabox.height)
            overlay = create_overlay(pw, ph, data, coords, sig_paths=self.sig_paths)
            ensure_output_dir()
            tarih_sanitized = data["tarih"].replace("/", "-").replace(".", "-")
            student_no_sanitized = "".join(c for c in data["ogrenci_no"] if c.isalnum())
            out_name = f"{student_no_sanitized}_{tarih_sanitized}.pdf"
            out_path = os.path.join(OUTPUT_DIR, out_name)
            merge_overlay_to_pdf(TEMPLATE_PDF, overlay, out_path)
        
            rec = {
                    "danisman": data.get("danisman"),
                    "ogrenci_ad": data.get("ogrenci_ad"),
                    "ogrenci_no": data.get("ogrenci_no"),
                    "sinif": data.get("sinif"),
                    "email": data.get("email"),
                    "telefon": data.get("telefon"),
                    "adres": data.get("adres"),
                    "konu": data.get("konu"),
                    "oneriler": data.get("oneriler"),
                    "tarih": data.get("tarih"),
                    "pdf_file": out_path
}

            append_record(RECORDS_CSV, rec)
            messagebox.showinfo("Başarılı", f"PDF kaydedildi:\n{out_path}\nKayıt CSV'ye eklendi.")
        except Exception as e:
            messagebox.showerror("Hata", str(e))

    def load_from_csv(self):
        no = simpledialog.askstring("Öğrenci No", "Yüklemek istediğiniz öğrenci numarasını girin:")
        if not no:
            return
        
        if not os.path.exists(RECORDS_CSV):
            messagebox.showerror("Kayıt Yok", "Henüz kayıtlı bir CSV dosyası bulunamadı.")
            return
        
        with open(RECORDS_CSV, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            kayit = next((r for r in reader if r.get("ogrenci_no", "") == no), None)
        
        if not kayit:
            messagebox.showerror("Bulunamadı", f"{no} numaralı öğrenciye ait kayıt bulunamadı.")
            return
        
        # CSV’den forma yaz
        for key in self.vars:
            value = kayit.get(key, "")
            if isinstance(self.vars[key], tk.Text):
                self.vars[key].delete("1.0", "end")
                self.vars[key].insert("1.0", value)
            else:
                self.vars[key].delete(0, "end")
                self.vars[key].insert(0, value)
        
        # Tek bilgi mesajı
        messagebox.showinfo("Yükleme Başarılı", f"{no} numaralı öğrenciye ait kayıt forma aktarıldı.")
        
    def normalize_fieldname(h):
        if h is None:
            return None
        return h.replace("\ufeff", "").strip().lower()
    
    def detect_delimiter(path):
        with open(path, "r", encoding="utf-8", newline='') as f:
            sample = f.read(8192)
            try:
                dialect = csv.Sniffer().sniff(sample, delimiters=[",",";","\t","|"])
                return dialect.delimiter
            except Exception:
                return ","
    
    def show_records(self):
        if not os.path.exists(RECORDS_CSV):
            messagebox.showerror("Kayıt Yok", "Henüz kayıtlı bir CSV dosyası bulunamadı.")
            return
    
        # Delimiter tespiti (kullanıcı doğruladı: comma, yine de kontrol)
        delim = detect_delimiter(RECORDS_CSV)
        print("Detected CSV delimiter:", repr(delim))
    
        win = tk.Toplevel(self)
        win.title("Kayıtlar")
        win.geometry("1000x500")
    
        tree = ttk.Treeview(win, columns=FIELD_ORDER, show="headings")
        for key in FIELD_ORDER:
            tree.heading(key, text=key.replace("_", " ").title())
            tree.column(key, width=120, anchor="w")
        tree.pack(fill=tk.BOTH, expand=True)
    
        vsb = ttk.Scrollbar(win, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(win, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
    
        with open(RECORDS_CSV, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=delim)
            if reader.fieldnames is None:
                messagebox.showerror("CSV Hatası", "CSV dosyasında başlık satırı bulunamadı.")
                return
    
            # Normalize header list and debug print
            csv_fields_raw = reader.fieldnames
            csv_fields = [normalize_fieldname(h) for h in csv_fields_raw]
            print("CSV başlıkları (raw):", csv_fields_raw)
            print("CSV başlıkları (normalized):", csv_fields)
    
            # Mapping: expected -> actual_header_name or None
            mapping = {}
            for expected in FIELD_ORDER:
                expected_norm = expected.lower()
                if expected_norm in csv_fields:
                    mapping[expected] = csv_fields_raw[csv_fields.index(expected_norm)]
                else:
                    mapping[expected] = None
            print("FIELD_ORDER mapping:", mapping)
    
            # Eğer önemli alanlar eşleşmiyorsa uyar
            missing = [k for k, v in mapping.items() if v is None]
            if missing:
                print("Eşleşmeyen alanlar:", missing)
                messagebox.showwarning("Başlık Uyumsuzluğu", f"Aşağıdaki alanlar CSV başlıklarıyla eşleşmiyor: {missing}\nKonsolu kontrol et.")
    
            # Satırları güvenli şekilde ekle
            row_count = 0
            for row in reader:
                values = []
                for key in FIELD_ORDER:
                    actual = mapping.get(key)
                    if actual:
                        values.append(row.get(actual, ""))
                    else:
                        values.append(row.get(key, ""))  # fallback
                tree.insert("", "end", values=values)
                row_count += 1
    
            print(f"Treeview'e eklenen satır sayısı: {row_count}")
            if row_count == 0:
                messagebox.showinfo("Boş Liste", "CSV bulundu ama içinde veri satırı yok veya tüm satırlar boş.")

import shutil

def auto_fix_missing_header(csv_path, expected_fields=FIELD_ORDER, backup=True, encoding='utf-8'):
    if not os.path.exists(csv_path):
        print("CSV bulunamadı:", csv_path)
        return False

    # Yedek oluştur
    if backup:
        bak = csv_path + ".bak"
        shutil.copy2(csv_path, bak)
        print("Yedek oluşturuldu:", bak)

    # Dosyayı liste-of-lists olarak oku (var olan delimiter'i tespit et)
    with open(csv_path, "r", encoding=encoding, newline='') as f:
        sample = f.read(8192)
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=[",",";","\t","|"])
        delim = dialect.delimiter
    except Exception:
        delim = ","

    rows = []
    with open(csv_path, "r", encoding=encoding, newline='') as f:
        reader = csv.reader(f, delimiter=delim)
        for row in reader:
            rows.append(row)

    if not rows:
        print("CSV boş:", csv_path)
        return False

    first = rows[0]
    # Eğer ilk satır expected_fields ile eşleşiyorsa zaten başlık var
    first_normalized = [str(x).replace("\ufeff", "").strip().lower() for x in first]
    expected_norm = [e.lower() for e in expected_fields]
    if all(f in expected_norm for f in first_normalized) and len(first) >= len(expected_fields):
        print("CSV zaten başlık içeriyor. Değişiklik yapılmadı.")
        return True

    # Eğer sütun sayısı beklenenle eşleşiyorsa, tek yapacağımız ilk satırı başlık olarak değiştirmek
    if len(first) == len(expected_fields):
        new_rows = [expected_fields] + rows
        with open(csv_path, "w", encoding=encoding, newline='') as f:
            writer = csv.writer(f, delimiter=',')
            for r in new_rows:
                writer.writerow(r)
        print("Başlık eklendi ve dosya güncellendi:", csv_path)
        return True

    # Eğer sütun sayısı farklıysa, deneysel eşleme: her satırı expected_fields uzunluğuna genişlet veya kırp
    corrected = []
    for r in rows:
        row_copy = list(r)
        if len(row_copy) < len(expected_fields):
            # eksik hücreler için boş string ekle
            row_copy += [""] * (len(expected_fields) - len(row_copy))
        elif len(row_copy) > len(expected_fields):
            # fazla sütunları birleştir: son sütunlarda virgüller yüzünden bölünmüş olabilir
            row_copy = row_copy[:len(expected_fields)-1] + [",".join(row_copy[len(expected_fields)-1:])]
        corrected.append(row_copy)

    new_rows = [expected_fields] + corrected
    with open(csv_path, "w", encoding=encoding, newline='') as f:
        writer = csv.writer(f, delimiter=',')
        for r in new_rows:
            writer.writerow(r)

    print("CSV başlığı onarıldı (tolerant mod). Yedek:", csv_path + ".bak")
    return True
def main():
    ensure_output_dir()
    app = FillFormApp()
    app.mainloop()

if __name__ == "__main__":
    main()


# In[ ]:




