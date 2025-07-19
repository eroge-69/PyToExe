import sys
from pdf2image import convert_from_path
import os

def main():
    if len(sys.argv) < 2:
        print("Silakan drag file PDF ke exe ini untuk convert ke JPEG.")
        input("Tekan Enter untuk keluar...")
        return

    pdf_path = sys.argv[1]

    if not os.path.exists(pdf_path):
        print(f"File tidak ditemukan: {pdf_path}")
        input("Tekan Enter untuk keluar...")
        return

    # Lokasi poppler relatif terhadap exe/script
    if getattr(sys, 'frozen', False):
        # Jika exe
        application_path = os.path.dirname(sys.executable)
    else:
        # Jika script python
        application_path = os.path.dirname(__file__)

    poppler_path = os.path.join(application_path, 'poppler', 'bin')
    print(f"Menggunakan Poppler path: {poppler_path}")

    try:
        pages = convert_from_path(pdf_path, dpi=300, poppler_path=poppler_path)

        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_folder = os.path.join(os.path.dirname(pdf_path), pdf_name + "_jpg")

        os.makedirs(output_folder, exist_ok=True)

        for i, page in enumerate(pages):
            out_path = os.path.join(output_folder, f'page_{i+1}.jpg')
            page.save(out_path, 'JPEG')
            print(f"Tersimpan: {out_path}")

        print("Selesai convert PDF ke JPEG.")
    except Exception as e:
        print(f"Terjadi error: {e}")

    input("Tekan Enter untuk keluar...")

if __name__ == '__main__':
    main()
