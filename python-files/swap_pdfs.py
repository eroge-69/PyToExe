import os
from PyPDF2 import PdfReader, PdfWriter

def swap_pages_in_two_page_pdfs():
    # Pfad zum aktuellen Ordner
    folder = os.path.dirname(os.path.abspath(__file__))

    # Alle Dateien im Ordner durchgehen
    for filename in os.listdir(folder):
        if filename.lower().endswith(".pdf"):
            filepath = os.path.join(folder, filename)

            # PDF laden
            reader = PdfReader(filepath)

            # Nur PDFs mit genau 2 Seiten bearbeiten
            if len(reader.pages) == 2:
                writer = PdfWriter()

                # Seiten tauschen: erst die zweite, dann die erste hinzufügen
                writer.add_page(reader.pages[1])
                writer.add_page(reader.pages[0])

                # Neuen Dateinamen erzeugen
                new_filename = os.path.splitext(filename)[0] + "_swapped.pdf"
                new_filepath = os.path.join(folder, new_filename)

                # Neue PDF speichern
                with open(new_filepath, "wb") as f:
                    writer.write(f)

                print(f"Seiten getauscht: {filename} -> {new_filename}")
            else:
                print(f"Übersprungen (nicht 2 Seiten): {filename}")

if __name__ == "__main__":
    swap_pages_in_two_page_pdfs()