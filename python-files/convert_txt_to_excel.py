
import pandas as pd
import re
import os
import sys

def txt_to_excel(input_txt):
    filename = os.path.splitext(os.path.basename(input_txt))[0]
    output_excel = filename + ".xlsx"

    with open(input_txt, "r", encoding="utf-8") as file:
        lines = file.readlines()

    data_lines = [line.strip() for line in lines if line.count('|') == 9]
    rows = [line.split('|') for line in data_lines]

    columns = [
        "Nom et Prénom", "Adresse", "Code Postal", "Ville",
        "Montant", "N° Bordereau", "Code Bar", "Code Bureau", "Code Envoi"
    ]

    df = pd.DataFrame(rows, columns=columns)
    df.to_excel(output_excel, index=False)
    print(f"✅ Converted: {output_excel}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Drag and drop a .txt file onto this script or run it with a file path.")
    else:
        txt_to_excel(sys.argv[1])
