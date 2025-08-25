import os
from PyPDF2 import PdfReader

def extract_field_value(pdf_path, field_name="megnevezés"):
    """Megadott űrlapmező értékének kiolvasása a PDF-ből"""
    try:
        reader = PdfReader(pdf_path)
        if reader.get_fields():
            fields = reader.get_fields()
            if field_name in fields:
                value = fields[field_name].get("/V")
                if value:
                    # szóközök és tiltott karakterek cseréje
                    return str(value).strip().replace(" ", "_").replace("/", "-")
    except Exception as e:
        print(f"Hiba a(z) {pdf_path} fájlnál: {e}")
    return None

def rename_pdfs_in_folder():
    folder = os.path.dirname(os.path.abspath(__file__))  # aktuális mappa
    for filename in os.listdir(folder):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(folder, filename)
            field_value = extract_field_value(pdf_path, "megnevezés")

            if field_value:
                base, ext = os.path.splitext(filename)
                new_name = f"{base}_{field_value}{ext}"
                new_path = os.path.join(folder, new_name)

                # ha még nem létezik a célfájl, nevezze át
                if not os.path.exists(new_path):
                    os.rename(pdf_path, new_path)
                    print(f"Átnevezve: {filename} → {new_name}")
                else:
                    print(f"⚠ {new_name} már létezik, kihagyva.")
            else:
                print(f"❌ Nincs 'megnevezés' mező a(z) {filename} fájlban.")

if __name__ == "__main__":
    rename_pdfs_in_folder()
