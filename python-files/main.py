import os
import shutil
import ezdxf
from tkinter import Tk, filedialog

def process_folder(folder_path):
    dest_folder = os.path.join(folder_path, "aangepast")
    os.makedirs(dest_folder, exist_ok=True)
    print(f"Gekozen map: {folder_path}")
    print(f"Aangemaakte kopiemap: {dest_folder}")

    for fname in os.listdir(folder_path):
        if fname.lower().endswith(".dxf"):
            src = os.path.join(folder_path, fname)
            dst = os.path.join(dest_folder, fname)
            try:
                shutil.copy2(src, dst)
                doc = ezdxf.readfile(dst)
                msp = doc.modelspace()
                for e in msp:
                    if e.dxf.layer == "3":
                        e.dxf.layer = "0"
                        e.dxf.color = 2
                doc.saveas(dst)
                print(f"Verwerk bestand: {fname} → voltooid")
            except Exception as e:
                print(f"Fout bij {fname}: {e}")

    print("Klaar! Aangepaste bestanden staan in de submap ‘aangepast’.")
    input("Druk op Enter om te sluiten...")

if __name__ == "__main__":
    Tk().withdraw()
    folder = filedialog.askdirectory(title="Selecteer map met DXF‑bestanden")
    if folder:
        process_folder(folder)
