import customtkinter as ctk
import tkinter.messagebox as messagebox
import json
import os

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class LaserCalcApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("LaserCalc - Calculateur Gravure et Découpe Laser")
        self.geometry("900x600")

        self.graveurs_file = "graveurs.json"
        self.materiaux_file = "materiaux.json"

        self.graveurs = self.load_data(self.graveurs_file)
        self.materiaux = self.load_data(self.materiaux_file)

        self.tabview = ctk.CTkTabview(self, width=850, height=550)
        self.tabview.pack(padx=20, pady=20)

        self.tabview.add("Graveurs")
        self.tabview.add("Matériaux")
        self.tabview.add("Calculateur")

        self.setup_graveurs_tab()
        self.setup_materiaux_tab()
        self.setup_calculateur_tab()

    def load_data(self, filename):
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save_data(self, filename, data):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def setup_graveurs_tab(self):
        tab = self.tabview.tab("Graveurs")
        self.graveur_listbox = ctk.CTkTextbox(tab, width=600, height=400)
        self.graveur_listbox.pack(pady=10)
        self.update_graveur_listbox()

        btn_frame = ctk.CTkFrame(tab)
        btn_frame.pack(pady=10)

        ctk.CTkButton(btn_frame, text="Ajouter", command=self.add_graveur).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Modifier", command=self.modify_graveur).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Supprimer", command=self.delete_graveur).pack(side="left", padx=5)

    def update_graveur_listbox(self):
        self.graveur_listbox.delete("1.0", "end")
        for i, g in enumerate(self.graveurs):
            self.graveur_listbox.insert("end", f"{i+1}. {g['nom']} - {g['puissance']}W - {g['vitesse']}mm/s\n")

    def add_graveur(self):
        self.open_graveur_editor()

    def modify_graveur(self):
        index = self.get_selected_index(self.graveur_listbox)
        if index is not None:
            self.open_graveur_editor(index)

    def delete_graveur(self):
        index = self.get_selected_index(self.graveur_listbox)
        if index is not None:
            del self.graveurs[index]
            self.save_data(self.graveurs_file, self.graveurs)
            self.update_graveur_listbox()

    def open_graveur_editor(self, index=None):
        editor = ctk.CTkToplevel(self)
        editor.title("Éditeur de Graveur")
        editor.geometry("400x300")

        nom = ctk.CTkEntry(editor, placeholder_text="Nom")
        nom.pack(pady=5)
        puissance = ctk.CTkEntry(editor, placeholder_text="Puissance (W)")
        puissance.pack(pady=5)
        vitesse = ctk.CTkEntry(editor, placeholder_text="Vitesse (mm/s)")
        vitesse.pack(pady=5)

        if index is not None:
            g = self.graveurs[index]
            nom.insert(0, g["nom"])
            puissance.insert(0, str(g["puissance"]))
            vitesse.insert(0, str(g["vitesse"]))

        def save():
            try:
                data = {
                    "nom": nom.get(),
                    "puissance": float(puissance.get()),
                    "vitesse": float(vitesse.get())
                }
                if index is not None:
                    self.graveurs[index] = data
                else:
                    self.graveurs.append(data)
                self.save_data(self.graveurs_file, self.graveurs)
                self.update_graveur_listbox()
                editor.destroy()
            except ValueError:
                messagebox.showerror("Erreur", "Veuillez entrer des valeurs numériques valides.")

        ctk.CTkButton(editor, text="Enregistrer", command=save).pack(pady=10)

    def setup_materiaux_tab(self):
        tab = self.tabview.tab("Matériaux")
        self.materiau_listbox = ctk.CTkTextbox(tab, width=600, height=400)
        self.materiau_listbox.pack(pady=10)
        self.update_materiau_listbox()

        btn_frame = ctk.CTkFrame(tab)
        btn_frame.pack(pady=10)

        ctk.CTkButton(btn_frame, text="Ajouter", command=self.add_materiau).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Modifier", command=self.modify_materiau).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Supprimer", command=self.delete_materiau).pack(side="left", padx=5)

    def update_materiau_listbox(self):
        self.materiau_listbox.delete("1.0", "end")
        for i, m in enumerate(self.materiaux):
            self.materiau_listbox.insert("end", f"{i+1}. {m['nom']} - {m['type']} - {m['epaisseur']}mm - {m['conso_kw']}kW/h\n")

    def add_materiau(self):
        self.open_materiau_editor()

    def modify_materiau(self):
        index = self.get_selected_index(self.materiau_listbox)
        if index is not None:
            self.open_materiau_editor(index)

    def delete_materiau(self):
        index = self.get_selected_index(self.materiau_listbox)
        if index is not None:
            del self.materiaux[index]
            self.save_data(self.materiaux_file, self.materiaux)
            self.update_materiau_listbox()

    def open_materiau_editor(self, index=None):
        editor = ctk.CTkToplevel(self)
        editor.title("Éditeur de Matériau")
        editor.geometry("400x500")

        nom = ctk.CTkEntry(editor, placeholder_text="Nom")
        nom.pack(pady=5)
        type_ = ctk.CTkEntry(editor, placeholder_text="Type")
        type_.pack(pady=5)
        epaisseur = ctk.CTkEntry(editor, placeholder_text="Épaisseur (mm)")
        epaisseur.pack(pady=5)
        densite = ctk.CTkEntry(editor, placeholder_text="Densité (g/cm³)")
        densite.pack(pady=5)
        conso_kw = ctk.CTkEntry(editor, placeholder_text="Conso kW/h par mm")
        conso_kw.pack(pady=5)
        vitesse = ctk.CTkEntry(editor, placeholder_text="Vitesse recommandée (mm/s)")
        vitesse.pack(pady=5)
        puissance = ctk.CTkEntry(editor, placeholder_text="Puissance recommandée (W)")
        puissance.pack(pady=5)
        commentaires = ctk.CTkTextbox(editor, width=300, height=100)
        commentaires.pack(pady=5)

        if index is not None:
            m = self.materiaux[index]
            nom.insert(0, m["nom"])
            type_.insert(0, m["type"])
            epaisseur.insert(0, str(m["epaisseur"]))
            densite.insert(0, str(m["densite"]))
            conso_kw.insert(0, str(m["conso_kw"]))
            vitesse.insert(0, str(m["vitesse"]))
            puissance.insert(0, str(m["puissance"]))
            commentaires.insert("1.0", m["commentaires"])

        def save():
            try:
                data = {
                    "nom": nom.get(),
                    "type": type_.get(),
                    "epaisseur": float(epaisseur.get()),
                    "densite": float(densite.get()),
                    "conso_kw": float(conso_kw.get()),
                    "vitesse": float(vitesse.get()),
                    "puissance": float(puissance.get()),
                    "commentaires": commentaires.get("1.0", "end").strip()
                }
                if index is not None:
                    self.materiaux[index] = data
                else:
                    self.materiaux.append(data)
                self.save_data(self.materiaux_file, self.materiaux)
                self.update_materiau_listbox()
                editor.destroy()
            except ValueError:
                messagebox.showerror("Erreur", "Veuillez entrer des valeurs numériques valides.")

        ctk.CTkButton(editor, text="Enregistrer", command=save).pack(pady=10)

    def setup_calculateur_tab(self):
        tab = self.tabview.tab("Calculateur")

        self.graveur_select = ctk.CTkComboBox(tab, values=[g["nom"] for g in self.graveurs], width=300)
        self.graveur_select.pack(pady=5)
        self.materiau_select = ctk.CTkComboBox(tab, values=[m["nom"] for m in self.materiaux], width=300)
        self.materiau_select.pack(pady=5)

        self.duree_entry = ctk.CTkEntry(tab, placeholder_text="Durée (heures)", width=300)
        self.duree_entry.pack(pady=5)

        self.result_label = ctk.CTkLabel(tab, text="Consommation estimée : ", font=("Arial", 16))
        self.result_label.pack(pady=10)

        ctk.CTkButton(tab, text="Calculer", command=self.calculer_conso).pack(pady=5)

    def calculer_conso(self):
        try:
            graveur_nom = self.graveur_select.get()
            materiau_nom = self.materiau_select.get()
            duree = float(self.duree_entry.get())

            graveur = next((g for g in self.graveurs if g["nom"] == graveur_nom), None)
            materiau = next((m for m in self.materiaux if m["nom"] == materiau_nom), None)

            if graveur and materiau:
                puissance_kw = graveur["puissance"] / 1000
                consommation = puissance_kw * duree * materiau["conso_kw"]
                self.result_label.configure(text=f"Consommation estimée : {consommation:.2f} kW/h")
            else:
                messagebox.showerror("Erreur", "Sélection invalide.")
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer une durée valide.")

    def get_selected_index(self, textbox):
        try:
            index = int(textbox.index("insert").split(".")[0]) - 1
            return index if index < len(textbox.get("1.0", "end").splitlines()) else None
        except:
            return None

if __name__ == "__main__":
    app = LaserCalcApp()
    app.mainloop()
