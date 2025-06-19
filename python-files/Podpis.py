from pyhanko.pdf_utils.reader import PdfFileReader
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.sign import signers
import tkinter as tk
from tkinter import filedialog
import os
import sys

def select_file(title, filetypes):
    """Otevře dialog pro výběr souboru."""
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title=title, filetypes=filetypes)
    root.destroy()
    return file_path

def check_keywords_in_pdf(pdf_path):
    """Zkontroluje, zda PDF má v metadatech Keywords obsahující 'CEZ:CEZd'."""
    with open(pdf_path, 'rb') as f:
        reader = PdfFileReader(f)
        info = reader.trailer['/Info'] if '/Info' in reader.trailer else None
        if not info:
            print("PDF nemá metadata (Info).")
            return False
        info_obj = info.get_object()
        keywords = info_obj.get('/Keywords')
        if not keywords:
            print("Keywords v metadatech nejsou.")
            return False
        if "CEZ:CEZd" in keywords:
            print("✅ Keyword OK")
            return True
        else:
            print("❌ Keyword Chyba")
            return False

def sign_pdf_document():
    cert_filename = "mycert.pfx"
    cert_path = os.path.join(os.path.dirname(__file__), cert_filename)
    cert_password = b"LukSpp2025"  # 👈 zde zadej svoje heslo jako bajty

    if not os.path.isfile(cert_path):
        print(f"❌ Certifikát {cert_filename} nebyl nalezen.")
        sys.exit()

    print("🗂️ Vyberte PDF dokument k podepsání...")
    input_pdf_path = select_file(
        "Vyberte PDF dokument",
        [("PDF soubory", "*.pdf"), ("Všechny soubory", "*.*")]
    )
    if not input_pdf_path:
        print("❌ Výběr PDF byl zrušen.")
        sys.exit()

    # Nejprve zkontrolujeme keywords v PDF
    if not check_keywords_in_pdf(input_pdf_path):
        print("Podepisování zrušeno kvůli nevyhovujícím keywords.")
        sys.exit()

    try:
        # Načti certifikát
        signer = signers.SimpleSigner.load_pkcs12(
            pfx_file=cert_path,
            passphrase=cert_password
        )
        print("✅ Certifikát úspěšně načten.")

        # Otevři PDF a podepiš
        with open(input_pdf_path, 'rb') as doc_input:
            w = IncrementalPdfFileWriter(doc_input)
            signature_meta = signers.PdfSignatureMetadata(
                field_name="External_Signature_0"
            )
            print("✍️ Podepisuji dokument...")
            out = signers.sign_pdf(w, signature_meta, signer=signer)
            base, _ = os.path.splitext(input_pdf_path)
            output_pdf_path = f"{base}_signed.pdf"

            if out.getbuffer().nbytes == 0:
                print("⚠️ Výstupní PDF je prázdné – zkontroluj, zda pole není již podepsané.")
            else:
                with open(output_pdf_path, 'wb') as doc_output:
                    doc_output.write(out.getvalue())
                print(f"✅ Dokument byl podepsán a uložen jako: {output_pdf_path}")

    except Exception as e:
        print(f"❌ Chyba: {e}")

if __name__ == "__main__":
    sign_pdf_document()
