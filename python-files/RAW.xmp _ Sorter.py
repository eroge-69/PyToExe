import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox

# Datei-Endungen, die zum .xmp dazugehören können
MATCH_EXTENSIONS = [".nef", ".jpg", ".jpeg"]

def main():
    # GUI-Setup
    root = tk.Tk()
    root.withdraw()

    start_folder = filedialog.askdirectory(title="Startordner wählen (RAW + XMP)")
    if not start_folder:
        messagebox.showerror("Fehler", "Kein Startordner ausgewählt.")
        return

    target_folder = filedialog.askdirectory(title="Zielordner wählen")
    if not target_folder:
        messagebox.showerror("Fehler", "Kein Zielordner ausgewählt.")
        return

    moved_files = 0
    xmp_files = [f for f in os.listdir(start_folder) if f.lower().endswith(".xmp")]

    for xmp in xmp_files:
        basename = os.path.splitext(xmp)[0]

        # Suche passende Bilddateien (.nef, .jpg, .jpeg)
        for ext in MATCH_EXTENSIONS:
            image_file = f"{basename}{ext}"
            src_image_path = os.path.join(start_folder, image_file)
            src_xmp_path = os.path.join(start_folder, xmp)

            if os.path.exists(src_image_path):
                # Zielpfade
                dst_image_path = os.path.join(target_folder, image_file)
                dst_xmp_path = os.path.join(target_folder, xmp)

                # Verschieben
                shutil.move(src_image_path, dst_image_path)
                shutil.move(src_xmp_path, dst_xmp_path)

                moved_files += 1
                print(f"Verschoben: {image_file} + {xmp}")
                break  # nur eine passende Datei verschieben

    messagebox.showinfo("Fertig!", f"{moved_files} Bildpaare wurden verschoben.")

if __name__ == "__main__":
    main()