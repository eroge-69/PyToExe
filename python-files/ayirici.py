import os
from PyPDF2 import PdfReader, PdfWriter

# 📁 Çalışma klasöründeki ilk PDF dosyasını bul
pdf_files = [f for f in os.listdir() if f.lower().endswith(".pdf")]
if not pdf_files:
    print("❌ Klasörde PDF dosyası bulunamadı.")
    exit()

input_pdf = pdf_files[0]  # İlk PDF dosyasını al
original_file_name = os.path.splitext(input_pdf)[0]  # Uzantısız hali
output_folder = "ayrilanlar"

# 📁 Çıktı klasörünü oluştur
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

reader = PdfReader(input_pdf)
print(f"📄 İşlenen dosya: {input_pdf}")

# 🔁 Sayfa sayfa ayır
for page_number, page in enumerate(reader.pages):
    writer = PdfWriter()
    writer.add_page(page)

    text = page.extract_text()
    lines = text.split("\n")

    name = None
    for i, line in enumerate(lines):
        if "KG Gebäudereinigung" in line and i + 1 < len(lines):
            name = lines[i + 1].strip()
            break

    if not name:
        name = f"Seite_{page_number + 1}"

    # ❌ Geçersiz karakterleri temizle
    invalid_chars = r'\/:*?"<>|'
    for c in invalid_chars:
        name = name.replace(c, "")

    # ✅ Örnek çıktı: "Murat Özdes Kicci Juli 2025.pdf"
    output_name = f"{name} {original_file_name}.pdf"
    output_path = os.path.join(output_folder, output_name)

    with open(output_path, "wb") as f:
        writer.write(f)

    print(f"✅ {output_name} kaydedildi.")

input("\nTüm sayfalar ayrıldı. Kapatmak için Enter'a bas...")
