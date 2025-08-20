
import tkinter as tk
from tkinter import filedialog, messagebox
import pymupdf  # PyMuPDF
import re
import pandas as pd
import os

def extraire_dmos_activites(pdf_path):
    doc = pymupdf.open(pdf_path)
    dmos_data = []

    for page in doc:
        text = page.get_text()
        activity_match = re.search(r"(?m)^\s*(\d{2})\s*$", text)
        activity_number = activity_match.group(1) if activity_match else "Non spécifié"
        dmos_matches = re.findall(r"135 Ma FW P 2-2-1 [A-Z]{2} \d+[a-z]? \d{4}", text)

        for dmos in dmos_matches:
            dmos_data.append({"Activité": activity_number, "DMOS": dmos})

    df = pd.DataFrame(dmos_data)
    df.index += 1
    df.reset_index(inplace=True)
    df.rename(columns={"index": "Ordre"}, inplace=True)

    output_excel = os.path.splitext(pdf_path)[0] + "_dmos.xlsx"
    df.to_excel(output_excel, index=False)
    return output_excel

def choisir_fichier():
    fichier_pdf = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if fichier_pdf:
        try:
            fichier_excel = extraire_dmos_activites(fichier_pdf)
            messagebox.showinfo("Succès", f"Fichier Excel généré :
{fichier_excel}")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

fenetre = tk.Tk()
fenetre.title("Extraction DMOS - Instructions de Fabrication")
fenetre.geometry("400x200")

label = tk.Label(fenetre, text="Cliquez pour choisir un fichier PDF à analyser", pady=20)
label.pack()

bouton = tk.Button(fenetre, text="Choisir un fichier PDF", command=choisir_fichier)
bouton.pack()

fenetre.mainloop()
