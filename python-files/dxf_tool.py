import ezdxf
import tkinter as tk
from tkinter import filedialog

# GUI-Fenster zur Dateiauswahl
root = tk.Tk()
root.withdraw()  # Versteckt das Hauptfenster

file_paths = filedialog.askopenfilenames(
    title="DXF-Dateien auswählen",
    filetypes=[("DXF files", "*.dxf")],
)

if not file_paths:
    print("Keine Dateien ausgewählt. Skript beendet.")
else:
    # Neue DXF-Zeichnung erstellen
    merged_doc = ezdxf.new()
    merged_msp = merged_doc.modelspace()

    for file in file_paths:
        doc = ezdxf.readfile(file)
        msp = doc.modelspace()
        
        for entity in msp.query("*"):  # Alle Objekte übernehmen
            merged_msp.add_entity(entity.copy())

    # Speichern der Datei
    output_path = filedialog.asksaveasfilename(
        title="Speicherort für zusammengeführte Datei",
        defaultextension=".dxf",
        filetypes=[("DXF files", "*.dxf")],
    )

    if output_path:
        merged_doc.saveas(output_path)
        print(f"Dateien erfolgreich zusammengefügt und gespeichert als: {output_path}")
    else:
        print("Speichern abgebrochen.")
