import tkinter as tk
from tkinter import filedialog
from PIL import Image
import pyheif
import os

def convert_heic_to_jpg(heic_path, jpg_path):
    heif_file = pyheif.read(heic_path)
    image = Image.frombytes(
        heif_file.mode,
        heif_file.size,
        heif_file.data,
        "raw",
        heif_file.mode,
        heif_file.stride,
    )
    image.save(jpg_path, "JPEG")

def main():
    root = tk.Tk()
    root.withdraw()  # Nasconde la finestra principale

    file_paths = filedialog.askopenfilenames(
        title="Seleziona immagini HEIC",
        filetypes=[("HEIC files", "*.heic")]
    )

    if not file_paths:
        print("Nessun file selezionato.")
        return

    dest_folder = filedialog.askdirectory(
        title="Scegli la cartella dove salvare le immagini convertite"
    )

    if not dest_folder:
        print("Nessuna cartella di destinazione selezionata.")
        return

    for heic_path in file_paths:
        file_name = os.path.splitext(os.path.basename(heic_path))[0]
        jpg_path = os.path.join(dest_folder, file_name + ".jpg")
        try:
            convert_heic_to_jpg(heic_path, jpg_path)
            print(f"Convertito: {heic_path} -> {jpg_path}")
        except Exception as e:
            print(f"Errore nella conversione di {heic_path}: {e}")

if __name__ == "__main__":
    main()
