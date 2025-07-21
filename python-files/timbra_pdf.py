import os
import re
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import black
from io import BytesIO

# Funzione per creare il timbro come PDF in memoria
def create_stamp(data_reg, protocollo, codice_fornitore):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    start_x = A4[0] - 9.7 * cm  
    start_y = 0.1 * cm         
    col_width = 3.2 * cm
    row_heights = [1.3 * cm, 1.8 * cm]  # altezza righe

    headers = ["Data registrazione", "Protocollo IVA", "Codice Fornitore"]
    values = [data_reg, protocollo, codice_fornitore]

    current_y = start_y
    for row in reversed(range(2)):
        height = row_heights[row]
        for col in range(3):
            x = start_x + col * col_width
            y = current_y
            c.rect(x, y, col_width, height, stroke=1, fill=0)

            if row == 0:
                # Riga combinata intestazione + valore
                c.setFont("Helvetica-Bold", 10)
                c.drawCentredString(
                    x + col_width / 2,
                    y + height * 0.65,
                    headers[col]
                )
                c.setFont("Helvetica", 16)
                c.drawCentredString(
                    x + col_width / 2,
                    y + height * 0.15,
                    values[col]
                )

            elif row == 1:
                # Intestazioni della seconda riga, per ogni colonna specifica
                if col == 0:
                    c.setFont("Helvetica-Bold", 10)
                    c.drawCentredString(
                        x + col_width / 2,
                        y + height * 0.75,
                        "Conto Contabile"
                    )
                elif col == 1:
                    c.setFont("Helvetica-Bold", 10)
                    c.drawCentredString(
                        x + col_width / 2,
                        y + height * 0.75,
                        "C.d.C."
                    )
                elif col == 2:
                    c.setFont("Helvetica-Bold", 10)
                    c.drawCentredString(
                        x + col_width / 2,
                        y + height * 0.75,
                        "V.d.S."
                    )
                # il resto della cella resta vuoto per scrivere a mano
        current_y += height

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

def add_stamp_to_pdf(pdf_path, data_reg):
    filename = os.path.basename(pdf_path)
    match_prot = re.match(r"(\d{1,5})", filename)
    match_cod = re.findall(r"(\d{1,5})(?!.*\d)", filename)

    if not match_prot or not match_cod:
        raise ValueError(f"Nome file non valido per l'estrazione: {filename}")

    protocollo = match_prot.group(1)
    codice_fornitore = match_cod[-1]

    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    stamp_pdf = PdfReader(create_stamp(data_reg, protocollo, codice_fornitore))
    stamp_page = stamp_pdf.pages[0]

    for i, page in enumerate(reader.pages):
        if i == len(reader.pages) - 1:  # ultima pagina
            page.merge_page(stamp_page)
        writer.add_page(page)

    output_folder = os.path.join(os.path.dirname(pdf_path), "output")
    os.makedirs(output_folder, exist_ok=True)

    output_path = os.path.join(output_folder, filename)
    with open(output_path, "wb") as f:
        writer.write(f)

# Interfaccia grafica

def main():
    root = tk.Tk()
    root.withdraw()

    data_reg = simpledialog.askstring("Data di registrazione", "Inserisci la data di registrazione:")
    if not data_reg:
        messagebox.showerror("Errore", "Data di registrazione non inserita.")
        return

    file_paths = filedialog.askopenfilenames(title="Seleziona i file PDF", filetypes=[("PDF files", "*.pdf")])
    if not file_paths:
        return

    for path in file_paths:
        try:
            add_stamp_to_pdf(path, data_reg)
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nel file {path}: {str(e)}")

    messagebox.showinfo("Fatto", "Tutti i PDF sono stati timbrati correttamente nella cartella 'output'.")

if __name__ == "__main__":
    main()
