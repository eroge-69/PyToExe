import os
import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
from openpyxl import load_workbook
from Script_Reader import extract_infos
import pdfplumber

class ExpertiseApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Application Expertises")
        self.geometry("600x400")

        self.files = []

        # Label
        self.label = tk.Label(self, text="Aucun fichier sélectionné", anchor='w')
        self.label.pack(fill='x', padx=10, pady=(10, 0))

        # Bouton d'ajout de fichiers
        self.btn_add = tk.Button(self, text="Ajouter des fichiers", command=self.add_files)
        self.btn_add.pack(pady=10)

        # Liste des fichiers sélectionnés
        self.listbox = tk.Listbox(self, height=10)
        self.listbox.pack(fill='both', expand=True, padx=10)

        # Bouton suppression fichier
        self.btn_remove = tk.Button(self, text="Supprimer le fichier sélectionné", command=self.remove_selected_file)
        self.btn_remove.pack(pady=(0, 10))

        # Bouton de conversion
        self.btn_convert = tk.Button(self, text="Convertir en Excel", command=self.convert_to_excel, state=tk.DISABLED)
        self.btn_convert.pack(pady=15)

    def add_files(self):
        files = filedialog.askopenfilenames(
            title="Sélectionnez les fichiers PDF à traiter",
            filetypes=[("Fichiers PDF", "*.pdf")]
        )
        if files:
            for f in files:
                if f not in self.files:
                    self.files.append(f)
                    self.listbox.insert(tk.END, os.path.basename(f))
            self.label.config(text=f"{len(self.files)} fichier(s) sélectionné(s)")
            self.btn_convert.config(state=tk.NORMAL)

    def remove_selected_file(self):
        selected = self.listbox.curselection()
        if not selected:
            messagebox.showwarning("Aucun fichier sélectionné", "Veuillez sélectionner un fichier à retirer.")
            return

        index = selected[0]
        self.files.pop(index)
        self.listbox.delete(index)

        if not self.files:
            self.label.config(text="Aucun fichier sélectionné")
            self.btn_convert.config(state=tk.DISABLED)
        else:
            self.label.config(text=f"{len(self.files)} fichier(s) sélectionné(s)")

    def convert_to_excel(self):
        if not self.files:
            messagebox.showwarning("Attention", "Aucun fichier sélectionné.")
            return

        template_path = os.path.join("Template standard", "Base Expertises template.xlsx")
        if not os.path.exists(template_path):
            messagebox.showerror("Erreur", f"Template Excel introuvable : {template_path}")
            return

        # Choix du fichier de sauvegarde
        today_str = datetime.datetime.now().strftime("%Y%m%d")
        save_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Fichier Excel", "*.xlsx")],
            initialfile=f"Expertises_{today_str}.xlsx",
            title="Enregistrer le fichier Excel"
        )
        if not save_path:
            messagebox.showinfo("Annulé", "Sauvegarde annulée par l'utilisateur.")
            return

        try:
            wb = load_workbook(template_path)
            ws = wb.active

            #  Date unique en B2
            ws["B2"] = datetime.datetime.now().date()

            start_row = 4  #  Début des lignes à la ligne 4

            for i, file_path in enumerate(self.files):
                with pdfplumber.open(file_path) as pdf:
                    pages = [page.extract_text() for page in pdf.pages]
                    text = "\n".join(pages)

                filename = os.path.basename(file_path)
                data = extract_infos(text, filename)

                current_row = start_row + i
                ws[f"C{current_row}"] = data.get('Nom actif', 'NON TROUVÉ')
                ws[f"D{current_row}"] = data.get('Adresse', 'NON TROUVÉ')
                ws[f"E{current_row}"] = data.get('ville', 'NON TROUVÉ')  # corrigé de 'Town' à 'ville'
                ws[f"H{current_row}"] = data.get('Societe prop', 'NON TROUVÉ')
                ws[f"AQ{current_row}"] = data.get('Valeur vénale hors fiscalité', 'NON TROUVÉ')
                ws[f"AS{current_row}"] = data.get('Valeur vénale fiscalité incluse', 'NON TROUVÉ')
                ws[f"K{current_row}"] = data.get('Surface utile', 'NON TROUVÉ')
                ws[f"N{current_row}"] = data.get("Taux d'occupation", 'NON TROUVÉ')

                ws[f"AG{current_row}"] = data.get('Vente en bloc', 'NON TROUVÉ')  # NOUVELLE LIGNE
                ws[f"AF{current_row}"] = data.get('abattement_occupation', 'NON TROUVÉ')  # NOUVELLE LIGNE

                ws[f"P{current_row}"] = data.get('Loyer effectif net/an', 'NON TROUVÉ')
                ws[f"S{current_row}"] = data.get('Valeur locative globale/an', 'NON TROUVÉ')
                ws[f"AR{current_row}"] = data.get('valeur_fiscalite', 'NON TROUVÉ')  # NOUVELLE LIGNE
                ws[f"AM{current_row}"] = data.get('taux_rendement', 'NON TROUVÉ')     # NOUVELLE LIGNE
                ws[f"AC{current_row}"] = data.get('capex_2025', 'NON TROUVÉ')         # NOUVELLE LIGNE

                #------------------ not checked  (dir belek )---------------

                ws[f"AI{current_row}"] = data.get('Valeur_vénale_Capitalisation', 'NON TROUVÉ')         # NOUVELLE LIGNE

                ws[f"AP{current_row}"] = data.get('valeur_venale_dcf', 'NON TROUVÉ')         # NOUVELLE LIGNE
                ws[f"AJ{current_row}"] = data.get('taux_rdt_consideré_(cap_rate)', 'NON TROUVÉ')
                ws[f"AN{current_row}"] = data.get('taux_actualisation', 'NON TROUVÉ')
                ws[f"AW{current_row}"] = data.get('valeur_venale_comparaison', 'NON TROUVÉ')
        

            wb.save(save_path)
            messagebox.showinfo("Succès", f"Fichier Excel généré : {save_path}")

            # Reset
            self.files.clear()
            self.listbox.delete(0, tk.END)
            self.label.config(text="Aucun fichier sélectionné")
            self.btn_convert.config(state=tk.DISABLED)

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la génération :\n{str(e)}")


if __name__ == "__main__":
    app = ExpertiseApp()
    app.mainloop()
