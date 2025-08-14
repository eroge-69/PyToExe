import os
import re
from tkinter import Tk, filedialog

def convert_csv_folder_to_txt():
    # Ukrycie głównego okna Tkintera
    root = Tk()
    root.withdraw()

    # Wybór folderu
    folder_path = filedialog.askdirectory(title="Wybierz folder z plikami CSV")
    if not folder_path:
        print("Nie wybrano folderu.")
        return

    # Utworzenie folderu output
    output_folder = os.path.join(folder_path, "output")
    os.makedirs(output_folder, exist_ok=True)

    # Pobranie wszystkich plików CSV w folderze
    csv_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.csv')]

    if not csv_files:
        print("Nie znaleziono plików CSV w wybranym folderze.")
        return

    for csv_file in csv_files:
        csv_path = os.path.join(folder_path, csv_file)

        # Wczytanie zawartości CSV
        with open(csv_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        new_lines = []
        for line in lines:
            # Usunięcie wszystkich ciągów średników o długości 2 lub więcej w każdej linii
            line = re.sub(r';{2,}', '', line)
            new_lines.append(line)

        # Zapis do pliku TXT w folderze output
        txt_path = os.path.join(output_folder, os.path.splitext(csv_file)[0] + ".txt")
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)

        print(f"Plik {csv_file} został przetworzony i zapisany jako {os.path.basename(txt_path)} w folderze 'output'")

if __name__ == "__main__":
    convert_csv_folder_to_txt()
