import os
import pandas as pd

def find_excel_file():
    # Cherche le premier fichier Excel (.xlsx) dans le dossier courant
    for filename in os.listdir():
        if filename.endswith(".xlsx"):
            return filename
    return None

def split_excel_to_txt(file_path):
    # Charge le fichier Excel
    df = pd.read_excel(file_path, header=None)

    # Trouve les lignes contenant "AND"
    and_indices = df[df.apply(lambda row: row.astype(str).str.contains("AND").any(), axis=1)].index.tolist()

    # Ajoute les points de découpe : début, séparateurs, fin
    split_points = [0] + and_indices + [len(df)]

    # Sauvegarde chaque bloc dans un fichier txt
    for i in range(len(split_points)-1):
        part_df = df.iloc[split_points[i]+1 : split_points[i+1]]
        part_df.to_csv(f"part{i+1}.txt", sep='\t', index=False, header=False)
        print(f"✅ Fichier créé : part{i+1}.txt")

def main():
    excel_file = find_excel_file()
    if excel_file:
        print(f"📁 Fichier détecté : {excel_file}")
        split_excel_to_txt(excel_file)
    else:
        print("⚠️ Aucun fichier Excel trouvé dans ce dossier.")

main()