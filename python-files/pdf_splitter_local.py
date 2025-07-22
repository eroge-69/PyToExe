# pdf_splitter_local.py

import pypdf
import fitz # PyMuPDF
import re
import os
import glob
import sys # Für Kommandozeilenargumente oder Eingabe

# --- Funktion zur PDF-Verarbeitung (aus deinem Colab-Skript) ---
def split_and_rename_pdf_pages(input_pdf_path, output_folder):
    """
    Teilt ein PDF in einzelne Seiten auf und benennt diese basierend auf
    den gefundenen Informationen (Nr. 9XXXX, Chargen-Nr., Barcode, Bündel, Flaschen-Nr., Pack No., Cylinder No.).
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    doc = None
    reader = None
    generated_filenames = [] # Zum Sammeln der Namen der generierten Dateien

    try:
        doc = fitz.open(input_pdf_path)
        reader = pypdf.PdfReader(input_pdf_path)
        num_pages = len(reader.pages)

        print(f"\nVerarbeite PDF: {os.path.basename(input_pdf_path)}")

        for i in range(num_pages):
            page_text = doc[i].get_text("text")

            nr_9_data = None
            chargen_nr_data = None
            no_9xxx_data = None
            secondary_id_data = None

            match_nr_9 = re.search(r"Nr\.:\s*(9\d+)", page_text)
            if match_nr_9:
                nr_9_data = match_nr_9.group(1).strip()
            else:
                match_chargen_nr = re.search(r"Chargen-Nr\.\s*:\s*(\d+)", page_text, re.IGNORECASE)
                if match_chargen_nr:
                    chargen_nr_data = match_chargen_nr.group(1).strip()
                else:
                    match_no_9xxx = re.search(r"No\.:\s*(9\d+)", page_text, re.IGNORECASE)
                    if match_no_9xxx:
                        no_9xxx_data = match_no_9xxx.group(1).strip()

            lines = page_text.splitlines()

            keywords_for_primary_match = ["Barcode", "Bündel", "Flaschen\\s*-\\s*Nr\\.\\s*:", "Pack No\\.\\s*:", "Cylinder No\\.\\s*:"]
            keywords_for_chargen_nr = ["Bündel", "Flaschen\\s*-\\s*Nr\\.\\s*:", "Pack No\\.\\s*:", "Cylinder No\\.\\s*:"]

            if nr_9_data or no_9xxx_data:
                search_keywords = keywords_for_primary_match
                lines_to_skip = 3
            elif chargen_nr_data:
                search_keywords = keywords_for_chargen_nr
                lines_to_skip = 1
            else:
                search_keywords = []

            for keyword_regex in search_keywords:
                found_keyword = False
                current_search_pattern = keyword_regex

                for line_idx, line in enumerate(lines):
                    if re.search(current_search_pattern, line, re.IGNORECASE):
                        found_keyword = True
                        skipped_non_empty_lines = 0
                        for next_line_idx in range(line_idx + 1, len(lines)):
                            potential_line = lines[next_line_idx].strip()
                            if potential_line:
                                skipped_non_empty_lines += 1
                            if skipped_non_empty_lines == lines_to_skip:
                                secondary_id_data = potential_line
                                break
                        break
                if secondary_id_data:
                    break

            output_pdf_name_parts = []

            if nr_9_data:
                output_pdf_name_parts.append(f"{nr_9_data}")
            elif chargen_nr_data:
                output_pdf_name_parts.append(f"{chargen_nr_data}")
            elif no_9xxx_data:
                output_pdf_name_parts.append(f"{no_9xxx_data}")

            if secondary_id_data:
                output_pdf_name_parts.append(f"{secondary_id_data}")

            if output_pdf_name_parts:
                combined_name = " - ".join(output_pdf_name_parts)
                clean_name = re.sub(r'[\\/:*?"<>|]', ' - ', combined_name)[:200]
                output_pdf_name = f"{clean_name}.pdf"
            else:
                original_file_base = os.path.splitext(os.path.basename(input_pdf_path))[0]
                output_pdf_name = f"Unbekannt_{original_file_base}_Seite_{i+1}.pdf"
                print(f"   Keine bekannte Information auf Seite {i+1} gefunden.")

            output_pdf_path = os.path.join(output_folder, output_pdf_name)

            writer = pypdf.PdfWriter()
            writer.add_page(reader.pages[i])

            with open(output_pdf_path, "wb") as output_file:
                writer.write(output_file)
            
            generated_filenames.append(output_pdf_name)
            print(f"   Seite {i+1} gespeichert als: {output_pdf_path}")

    except Exception as e:
        print(f"Fehler bei der Verarbeitung von {os.path.basename(input_pdf_path)}: {e}")
    finally:
        if 'doc' in locals() and doc:
            doc.close()
        if 'reader' in locals() and reader:
            del reader
        if 'doc' in locals():
            del doc
    return generated_filenames


# --- Hauptausführungsblock für lokale PC-Nutzung ---
if __name__ == "__main__":
    input_pdf_paths = []

    # Prüfe, ob Dateien per Drag & Drop auf die EXE gezogen wurden
    if len(sys.argv) > 1:
        # Die Argumente (sys.argv[1:]) sind die Pfade der auf die EXE gezogenen Dateien
        input_pdf_paths = [arg for arg in sys.argv[1:] if arg.lower().endswith('.pdf')]
    else:
        # Wenn keine Dateien gezogen wurden, fordere den Benutzer zur Eingabe auf
        print("Bitte geben Sie den vollständigen Pfad zur PDF-Datei(en) ein (mehrere Pfade durch Leerzeichen getrennt):")
        user_input = input("PDF-Pfad(e): ")
        input_pdf_paths = [p.strip() for p in user_input.split() if p.strip().lower().endswith('.pdf')]

    if not input_pdf_paths:
        print("Keine gültigen PDF-Pfade angegeben. Beende das Programm.")
        input("Drücken Sie Enter zum Beenden...") # Damit das Fenster offen bleibt
        sys.exit()

    # Erstelle den Ausgabeordner im selben Verzeichnis wie das Skript/die EXE
    # Dies ist besser, als immer in feste Ordner zu schreiben
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    main_output_folder = os.path.join(script_dir, "verarbeitete_dokumente")

    if not os.path.exists(main_output_folder):
        os.makedirs(main_output_folder)

    print(f"\nAusgabeordner: {main_output_folder}")

    for pdf_path in input_pdf_paths:
        if os.path.exists(pdf_path) and pdf_path.lower().endswith('.pdf'):
            split_and_rename_pdf_pages(pdf_path, main_output_folder)
        else:
            print(f"Warnung: Datei '{pdf_path}' existiert nicht oder ist keine PDF und wird übersprungen.")

    print("\nVerarbeitung aller PDFs abgeschlossen.")
    print(f"Die verarbeiteten PDFs finden Sie im Ordner: '{main_output_folder}'")
    input("Drücken Sie Enter zum Beenden...") # Damit das Konsolenfenster nicht sofort schließt