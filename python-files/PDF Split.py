import os
import tkinter as tk
from tkinter import filedialog, messagebox
from pypdf import PdfReader, PdfWriter


def diviser_pdf_par_blocs(pdf_source, n, dossier_sortie, prefixe_sortie="extrait"):
    reader = PdfReader(pdf_source)
    total_pages = len(reader.pages)

    os.makedirs(dossier_sortie, exist_ok=True)

    for i in range(0, total_pages, n):
        writer = PdfWriter()
        for j in range(i, min(i + n, total_pages)):
            writer.add_page(reader.pages[j])

        output_filename = os.path.join(
            dossier_sortie,
            f"{prefixe_sortie}_{(i // n) + 1}.pdf"
        )

        with open(output_filename, "wb") as f:
            writer.write(f)

    messagebox.showinfo("Succès", f"Découpage terminé !\nFichiers enregistrés dans :\n{dossier_sortie}")


# --- Interface graphique ---
def choisir_pdf():
    chemin = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if chemin:
        entree_pdf.delete(0, tk.END)
        entree_pdf.insert(0, chemin)


def choisir_dossier():
    dossier = filedialog.askdirectory()
    if dossier:
        entree_dossier.delete(0, tk.END)
        entree_dossier.insert(0, dossier)


def lancer_decoupage():
    pdf_source = entree_pdf.get()
    dossier_sortie = entree_dossier.get()
    try:
        n = int(entree_n.get())
        assert n > 0
    except:
        messagebox.showerror("Erreur", "Veuillez entrer un entier > 0 pour n.")
        return

    if not os.path.isfile(pdf_source):
        messagebox.showerror("Erreur", "Fichier PDF source introuvable.")
        return
    if not dossier_sortie:
        messagebox.showerror("Erreur", "Veuillez choisir un dossier de sortie.")
        return

    diviser_pdf_par_blocs(pdf_source, n, dossier_sortie)


# Création de la fenêtre
racine = tk.Tk()
racine.title("Découpeur de PDF par blocs de pages")
racine.geometry("500x220")

# Widgets
tk.Label(racine, text="Fichier PDF source :").pack(pady=5)
cadre_pdf = tk.Frame(racine)
cadre_pdf.pack()
entree_pdf = tk.Entry(cadre_pdf, width=50)
entree_pdf.pack(side=tk.LEFT, padx=5)
tk.Button(cadre_pdf, text="Parcourir", command=choisir_pdf).pack(side=tk.LEFT)

tk.Label(racine, text="Nombre de pages par fichier :").pack(pady=5)
entree_n = tk.Entry(racine, width=10)
entree_n.pack()

tk.Label(racine, text="Dossier de sortie :").pack(pady=5)
cadre_dossier = tk.Frame(racine)
cadre_dossier.pack()
entree_dossier = tk.Entry(cadre_dossier, width=50)
entree_dossier.pack(side=tk.LEFT, padx=5)
tk.Button(cadre_dossier, text="Choisir", command=choisir_dossier).pack(side=tk.LEFT)

tk.Button(racine, text="Lancer le découpage", command=lancer_decoupage, bg="green", fg="white").pack(pady=15)

racine.mainloop()
