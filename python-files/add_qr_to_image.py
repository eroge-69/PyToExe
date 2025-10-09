import time
import os
import shutil
import xml.etree.ElementTree as ET
from PIL import Image
import qrcode
import re

def clean_filename(filename):
    # Entfernt "_copyX" oder "copyX" aus dem Dateinamen
    name, ext = os.path.splitext(filename)
    cleaned_name = re.sub(r'(_)?copy\d+', '', name, flags=re.IGNORECASE)
    return cleaned_name + ext

def read_config(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    source = root.find('./paths/source').text
    target = root.find('./paths/target').text
    success_folder = root.find('./paths/success_folder').text
    error_folder = root.find('./paths/error_folder').text
    base_url = root.find('./qr_data/base_url').text
    qr_size = int(root.find('./qr_data/qr_size').text)
    x_offset = int(root.find('./qr_data/qr_position/x_offset').text)
    y_offset = int(root.find('./qr_data/qr_position/y_offset').text)
    source_format = root.find('./qr_data/file_formats/source_format').text
    qr_format = root.find('./qr_data/file_formats/qr_format').text
    check_interval = int(root.find('./settings/check_interval').text)
    return source, target, success_folder, error_folder, base_url, qr_size, x_offset, y_offset, source_format, qr_format, check_interval

def add_qr_to_image(input_path, output_path, base_url, qr_size, x_offset, y_offset, qr_format):
    try:
        # QR-Code generieren
        cleaned_filename = clean_filename(filename)
        qr_data = f"{base_url}{cleaned_filename.replace(cleaned_filename.split('.')[-1], qr_format.strip('.'))}"
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(qr_data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill="black", back_color="white")

        # QR-Code Größe anpassen
        qr_img = qr_img.resize((qr_size, qr_size))

        # Bild öffnen
        base_img = Image.open(input_path).convert("RGB")

        # QR-Code auf das Bild zeichnen
        qr_position = (base_img.width - qr_img.width - x_offset, base_img.height - qr_img.height - y_offset)
        base_img.paste(qr_img, qr_position)

        # Neues Bild speichern
        base_img.save(output_path)  # Zieldatei bleibt gleich

        # Rückmeldung ausgeben
        print(f"Bild verarbeitet: {filename}")
        print(f"QR-Code-Link: {qr_data}\n")
        return True
    except Exception as e:
        print(f"Fehler bei der Verarbeitung von {input_path}: {e}")
        return False

def process_files():
    # Konfigurationsdatei einlesen
    config_file = "config.xml"  # Passe den Pfad zur XML-Datei an
    source_dir, target_dir, success_folder, error_folder, base_url, qr_size, x_offset, y_offset, source_format, qr_format, check_interval = read_config(config_file)

    # Verarbeitete Dateien tracken
    processed_files = set()

    while True:
        try:
            # Dateien im Quellordner überprüfen
            for filename in os.listdir(source_dir):
                if filename.lower().endswith(source_format) and filename not in processed_files:
                    input_path = os.path.join(source_dir, filename)
                    output_name = filename  # Zieldateiname bleibt gleich
                    output_path = os.path.join(target_dir, output_name)

                    # QR-Code hinzufügen und Bild speichern
                    success = add_qr_to_image(input_path, output_path, base_url, qr_size, x_offset, y_offset, qr_format)

                    # Verschiebe Quelldatei je nach Ergebnis
                    if success:
                        shutil.move(input_path, os.path.join(success_folder, filename))
                    else:
                        shutil.move(input_path, os.path.join(error_folder, filename))

                    # Datei als verarbeitet markieren
                    processed_files.add(filename)

            # Wartezeit basierend auf der XML-Datei
            time.sleep(check_interval)

        except KeyboardInterrupt:
            print("Programm beendet.")
            break

if __name__ == "__main__":
    process_files()
