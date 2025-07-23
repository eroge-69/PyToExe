import sys
import fitz  # PyMuPDF
import glob
def reorder_pdf(input_path, output_path):
    """
    Riordina le pagine di un PDF double-sided:
    - Suddivide il PDF in due metà (fronti e retro)
    - Intercala le pagine: fronte1, retro1, fronte2, retro2, ...
    Gestisce PDF con numero dispari di pagine, lasciando l'ultima pagina rimasta in fondo.
    """
    doc = fitz.open(input_path)
    new_doc = fitz.open()
    n_pages = doc.page_count

    # Intercala partendo dagli estremi
    for i in range((n_pages + 1) // 2):
        # Pagina dalla parte iniziale
        new_doc.insert_pdf(doc, from_page=i, to_page=i)
        # Pagina corrispondente dalla fine, solo se diversa
        j = n_pages - 1 - i
        if j != i:
            new_doc.insert_pdf(doc, from_page=j, to_page=j)

    new_doc.save(output_path)
    new_doc.close()
    doc.close()

    new_doc.save(output_path)
    new_doc.close()
    doc.close()



# Cerca tutti i .pdf nella cartella attuale
input_pdf = glob.glob("*.pdf")[0]
reorder_pdf(input_pdf, 'RISULTATO.pdf')
print(f"PDF riordinato salvato correttamente")
