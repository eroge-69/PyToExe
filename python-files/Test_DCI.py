import os
import csv
from tkinter import Tk, filedialog

def lire_dci(filepath):
    data = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if len(line) >= 4:
                dci = line[:4]
                parts = line.split()
                value = parts[-1]
                data.append((dci, value))
    return data

def traitement_dci(files, liaison_rs, folder):
    file1 = os.path.join(folder, files[0])
    file2 = os.path.join(folder, files[1])

    data1 = lire_dci(file1)
    data2 = lire_dci(file2)

    if len(data1) == 0 or len(data2) == 0:
        raise ValueError("Les fichiers doivent contenir au moins deux colonnes.")

    dci1 = [d[0] for d in data1]
    dci2 = [d[0] for d in data2]

    values1 = [d[1] for d in data1]
    values2 = [d[1] for d in data2]

    if dci1 != dci2:
        raise ValueError("Les labels des deux fichiers sont différents. Comparaison impossible.")

    resultats = []
    for i in range(len(dci1)):
        status = "OK" if values1[i] == values2[i] else "KO"
        resultats.append((dci1[i], values1[i], values2[i], status))

    output_file = os.path.join(folder, f'Comparaison_{liaison_rs}_Resultats_DCI.csv')
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            writer.writerow(['DCI', files[0], files[1], 'COMPARAISON'])
            writer.writerows(resultats)
        print(f"Comparaison terminée. Résultats enregistrés dans :\n{output_file}")
    except Exception as e:
        raise IOError(f"Erreur lors de l'écriture du fichier : {e}")

    # Ouvre le fichier (Windows uniquement)
    try:
        os.startfile(output_file)
    except Exception:
        pass


def main():
    # Masquer la fenêtre Tkinter principale
    root = Tk()
    root.withdraw()

    folder = filedialog.askdirectory(title='Sélectionnez le dossier contenant les fichiers .DCI')
    if not folder:
        raise SystemExit('Aucun dossier sélectionné. Script annulé.')

    all_files = [f for f in os.listdir(folder) if f.upper().endswith('.DCI')]
    if len(all_files) not in (2, 4):
        raise ValueError("Le dossier doit contenir exactement deux ou quatre fichiers .DCI.")

    files_utr = sorted([f for f in all_files if f.upper().startswith('UTR-LOC')])
    if len(files_utr) == 2:
        traitement_dci(files_utr, 'UTR-LOC', folder)

    files_gps = sorted([f for f in all_files if f.upper().startswith('INTFGPS')])
    if len(files_gps) == 2:
        traitement_dci(files_gps, 'INTFGPS', folder)


if __name__ == '__main__':
    main()
