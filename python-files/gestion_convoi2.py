#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# -*- coding: utf-8 -*-
"""
Script pour l'Optimisation de l'Assignation des Rapatriés dans des Bus
Version : 11.4 (Réintégration du résumé par bus dans la feuille de résumé)
"""

import pandas as pd
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, ttk
from datetime import datetime
import traceback
import os

# --- CONFIGURATION ET LOGIQUE MÉTIER (INCHANGÉES) ---
VULNERABILITES_PRIORITAIRES = ['PMR', 'MED', 'PREG', 'HANDICAP']
CHAMPS_REQUIS = {
    'id_groupe': 'ID du Groupe/Famille',
    'nom_complet': 'Nom complet de la personne',
    'age': 'Âge',
    'lien_parente': 'Lien de parenté (pour chef de ménage)',
    'id_volrep': 'Numéro Volrep',
    'besoins_specifiques': 'Détail des besoins spécifiques'
}
def valider_et_preparer_donnees(fichier_excel, capacite_bus, column_map, log_callback):
    log_callback(f"--- Chargement du fichier '{fichier_excel}' ---")
    try:
        df_individus = pd.read_excel(fichier_excel, header=int(column_map['ligne_entetes']))
    except Exception as e:
        log_callback(f"ERREUR CRITIQUE lors de la lecture du fichier : {e}")
        return None, None, None
    colonnes_fichier = df_individus.columns.tolist()
    for nom_attendu, nom_reel in column_map.items():
        if nom_attendu != 'ligne_entetes' and nom_reel not in colonnes_fichier:
            log_callback(f"ERREUR : La colonne '{nom_reel}' (mappée pour '{CHAMPS_REQUIS.get(nom_attendu)}') est introuvable.")
            return None, None, None
    df_individus = df_individus.dropna(subset=[column_map['id_groupe']]).copy()
    log_callback("\n--- Démarrage de la validation des données ---")
    familles_data = {}
    groupes_non_assignables = []
    groupes = df_individus.groupby(column_map['id_groupe'])
    for id_groupe, df_groupe in groupes:
        taille_calculee = len(df_groupe)
        if taille_calculee > capacite_bus:
            chef_menage_alerte = 'Non défini'
            if column_map['lien_parente'] in df_groupe.columns and not df_groupe[df_groupe[column_map['lien_parente']].str.contains('focal point', case=False, na=False)].empty:
                 chef_menage_alerte = df_groupe[df_groupe[column_map['lien_parente']].str.contains('focal point', case=False, na=False)][column_map['nom_complet']].iloc[0]
            groupes_non_assignables.append({'ID Groupe': id_groupe, 'Chef de Ménage': chef_menage_alerte, 'Taille': taille_calculee, 'Raison': f'Taille ({taille_calculee}) > Capacité Bus ({capacite_bus})'})
            log_callback(f"  - ALERTE : Groupe {id_groupe} (taille: {taille_calculee}) trop grand.")
            continue
        chef_menage = 'Non défini'
        if column_map['lien_parente'] in df_groupe.columns and not df_groupe[df_groupe[column_map['lien_parente']].str.contains('focal point', case=False, na=False)].empty:
            chef_menage = df_groupe[df_groupe[column_map['lien_parente']].str.contains('focal point', case=False, na=False)][column_map['nom_complet']].iloc[0]
        enfants_0_4 = df_groupe[(df_groupe[column_map['age']] >= 0) & (df_groupe[column_map['age']] <= 4)].shape[0]
        enfants_5_11 = df_groupe[(df_groupe[column_map['age']] >= 5) & (df_groupe[column_map['age']] <= 11)].shape[0]
        enfants_12_17 = df_groupe[(df_groupe[column_map['age']] >= 12) & (df_groupe[column_map['age']] <= 17)].shape[0]
        adultes_18_59 = df_groupe[(df_groupe[column_map['age']] >= 18) & (df_groupe[column_map['age']] <= 59)].shape[0]
        pers_agees_60_plus = df_groupe[(df_groupe[column_map['age']] >= 60)].shape[0]
        volrep_number = df_groupe[column_map['id_volrep']].iloc[0] if column_map['id_volrep'] in df_groupe.columns else 'N/A'
        specific_needs = ', '.join(df_groupe[column_map['besoins_specifiques']].dropna().unique().tolist()) if column_map['besoins_specifiques'] in df_groupe.columns else ''
        vulns_groupe = df_groupe[column_map['besoins_specifiques']].astype(str).unique()
        est_prioritaire = any(any(code_prio in v for code_prio in VULNERABILITES_PRIORITAIRES) for v in vulns_groupe)
        familles_data[id_groupe] = {'taille': taille_calculee, 'prioritaire': est_prioritaire, 'chef_menage': chef_menage, 'volrep_number': volrep_number, 'enfants_0_4': enfants_0_4, 'enfants_5_11': enfants_5_11, 'enfants_12_17': enfants_12_17, 'adultes_18_59': adultes_18_59, 'pers_agees_60_plus': pers_agees_60_plus, 'specific_needs': specific_needs}
    log_callback("--- Validation des données terminée. ---")
    return familles_data, df_individus, groupes_non_assignables
def assigner_familles_aux_bus(familles, capacite_bus, log_callback):
    log_callback("--- Démarrage de l'assignation des familles aux bus ---")
    familles_prio = {id_f: data for id_f, data in familles.items() if data['prioritaire']}
    familles_non_prio = {id_f: data for id_f, data in familles.items() if not data['prioritaire']}
    familles_prio_triees = sorted(familles_prio.items(), key=lambda item: item[1]['taille'], reverse=True)
    familles_non_prio_triees = sorted(familles_non_prio.items(), key=lambda item: item[1]['taille'], reverse=True)
    liste_familles_a_placer = familles_prio_triees + familles_non_prio_triees
    bus_liste = []
    for id_groupe, data in liste_familles_a_placer:
        taille_famille = data['taille']
        bus_trouve = False
        for un_bus in bus_liste:
            if un_bus['places_restantes'] >= taille_famille:
                un_bus['groupes'].append(id_groupe)
                un_bus['places_restantes'] -= taille_famille
                bus_trouve = True
                break
        if not bus_trouve:
            nouveau_bus = {'id_bus': len(bus_liste) + 1, 'capacite': capacite_bus, 'groupes': [id_groupe], 'places_restantes': capacite_bus - taille_famille}
            bus_liste.append(nouveau_bus)
    log_callback(f"--- Assignation terminée. {len(bus_liste)} bus sont nécessaires. ---")
    return bus_liste

# --- MODIFICATION : La fonction de génération inclut maintenant TOUS les résumés ---
def generer_manifeste_excel(bus_assignes, familles_data, groupes_non_assignables, fichier_sortie, convoi_info, log_callback):
    log_callback(f"\n--- Génération du fichier de manifeste '{fichier_sortie}' ---")
    try:
        logo_path = 'logo_unhcr.png'
        if not os.path.exists(logo_path):
            log_callback(f"AVERTISSEMENT : Le fichier logo '{logo_path}' est introuvable. Le manifeste sera généré sans logo.")
            logo_path = None

        with pd.ExcelWriter(fichier_sortie, engine='xlsxwriter') as writer:
            # --- Création de la feuille de résumé ---
            total_passagers = sum(familles_data[id_groupe]['taille'] for un_bus in bus_assignes for id_groupe in un_bus['groupes'])
            total_familles = sum(len(un_bus['groupes']) for un_bus in bus_assignes)
            
            resume_data = {
                'Statistique': ['Date du Convoi', 'Lieu de Départ', 'Lieu d\'Arrivée', 'Capacité par Bus', 'Nombre de Bus Utilisés', 'Total Familles Assignées', 'Total Passagers Assignés'],
                'Valeur': [convoi_info['date'], convoi_info['depart'], convoi_info['arrivee'], convoi_info['capacite'], len(bus_assignes), total_familles, total_passagers]
            }
            df_resume = pd.DataFrame(resume_data)
            df_resume.to_excel(writer, sheet_name='Resume Convoi', startrow=1, index=False)
            worksheet_resume = writer.sheets['Resume Convoi']
            worksheet_resume.set_column('A:B', 30)

            # --- AJOUT : Création du résumé par bus ---
            start_row_bus_summary = len(df_resume) + 3
            worksheet_resume.write(f'A{start_row_bus_summary}', 'Résumé par Bus')
            bus_summary_data = [
                {'Bus #': b['id_bus'], 'Passagers': b['capacite'] - b['places_restantes'], 'Places Restantes': b['places_restantes'], 'Nb Familles': len(b['groupes'])} 
                for b in bus_assignes
            ]
            df_bus_summary = pd.DataFrame(bus_summary_data)
            df_bus_summary.to_excel(writer, sheet_name='Resume Convoi', startrow=start_row_bus_summary, index=False)
            # --- FIN DE L'AJOUT ---

            if groupes_non_assignables:
                start_row_non_assignable = start_row_bus_summary + len(df_bus_summary) + 3
                worksheet_resume.write(f'A{start_row_non_assignable}', 'Familles NON Assignées (Action Manuelle Requise)')
                pd.DataFrame(groupes_non_assignables).to_excel(writer, sheet_name='Resume Convoi', startrow=start_row_non_assignable + 1, index=False)
                worksheet_resume.set_column('D:D', 40)

            # --- Génération des manifestes par bus ---
            for un_bus in bus_assignes:
                nom_onglet = f'Bus {un_bus["id_bus"]}'
                
                manifeste_data = []
                for id_groupe in un_bus['groupes']:
                    famille_info = familles_data[id_groupe]
                    manifeste_data.append({
                        '#': '', 'No Volrep': famille_info['volrep_number'], 'Noms Chef de Menage': famille_info['chef_menage'],
                        'Taille Menage': famille_info['taille'], 'Totals': famille_info['taille'], 'Enfants 0 - 4': famille_info['enfants_0_4'],
                        '5 - 11': famille_info['enfants_5_11'], '12 - 17': famille_info['enfants_12_17'], 'Adultes 18 - 59': famille_info['adultes_18_59'],
                        'Pers. Agees 60 +': famille_info['pers_agees_60_plus'], 'Besoins Specifics *': famille_info['specific_needs']
                    })
                
                df_manifeste = pd.DataFrame(manifeste_data)
                df_manifeste['#'] = range(1, len(df_manifeste) + 1)
                df_manifeste.to_excel(writer, sheet_name=nom_onglet, startrow=11, index=False)
                
                worksheet = writer.sheets[nom_onglet]
                
                if logo_path:
                    worksheet.insert_image('A1', logo_path, {'x_scale': 0.5, 'y_scale': 0.5})

                worksheet.write('B2', 'DISTRIBUTION')
                worksheet.write('G4', '- 1 COPY FOR DEPARTURE AIRPORT (WHITE)')
                worksheet.write('M4', 'MANIFEST #')
                worksheet.write('P4', f"HCR/{datetime.now().year}/Bus{un_bus['id_bus']:02d}")
                worksheet.write('G5', '- 1 COPY FOR DESTINATION AIRPORT (YELLOW)')
                worksheet.write('G6', '- 1 COPY FOR AC CAPTAIN')
                worksheet.write('G7', '- 1 COPY FOR IMMIGRATION PURPOSES')

                worksheet.write('B9', 'VEHICLE REGISTRATION',); worksheet.write('C9', convoi_info['immatriculation'])
                worksheet.write('F9', 'TRANSPORTER'); worksheet.write('G9', convoi_info['transporteur'])
                worksheet.write('J9', 'CONVOY NO'); worksheet.write('K9', convoi_info['num_convoi'])
                worksheet.write('N9', 'DRIVER'); worksheet.write('O9', convoi_info['chauffeur'])
                
                worksheet.write('B10', f"Date: {convoi_info['date']}")
                worksheet.write('J10', f"DEPARTURE: {convoi_info['depart']}")
                worksheet.write('P10', f"DESTINATION: {convoi_info['arrivee']}")

                total_passagers_bus = df_manifeste['Taille Menage'].sum()
                start_row_summary = 11 + len(df_manifeste) + 2
                worksheet.write(start_row_summary, 0, '--- RÉSUMÉ DU BUS ---')
                worksheet.write(start_row_summary + 1, 0, 'Capacité totale:'); worksheet.write(start_row_summary + 1, 1, convoi_info['capacite'])
                worksheet.write(start_row_summary + 2, 0, 'Total passagers:'); worksheet.write(start_row_summary + 2, 1, total_passagers_bus)
                worksheet.write(start_row_summary + 3, 0, 'Places restantes:'); worksheet.write(start_row_summary + 3, 1, un_bus['places_restantes'])
                
                for i, col in enumerate(df_manifeste.columns):
                    max_len = max(df_manifeste[col].astype(str).map(len).max(), len(col)) + 2
                    worksheet.set_column(i, i, max_len)

        log_callback("--- Manifeste complet (avec tous les résumés et logo) généré avec succès ! ---")
    except Exception as e:
        log_callback(f"ERREUR CRITIQUE lors de la création du fichier Excel : {e}")
        raise e

# --- INTERFACE GRAPHIQUE (GUI) - VERSION 11.4 ---
# (Aucun changement dans l'interface, elle est déjà complète)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Générateur de Manifestes de Convoi v11.4")
        self.geometry("850x850")
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(4, weight=1)

        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        if messagebox.askokcancel("Quitter", "Voulez-vous vraiment quitter l'application ?"):
            self.destroy()
            os._exit(0)

    def create_widgets(self):
        file_frame = ttk.LabelFrame(self, text="1. Sélection du Fichier de Données", padding="10")
        file_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        file_frame.columnconfigure(1, weight=1)
        ttk.Label(file_frame, text="Chemin du fichier:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.fichier_entree_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.fichier_entree_var, state="readonly").grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(file_frame, text="Parcourir...", command=self.select_and_load_file).grid(row=0, column=2, padx=5, pady=5)
        ttk.Label(file_frame, text="Ligne des en-têtes:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.header_row_var = tk.StringVar(value="1")
        ttk.Entry(file_frame, textvariable=self.header_row_var, width=10).grid(row=1, column=1, padx=5, pady=5, sticky="w")

        self.mapping_frame = ttk.LabelFrame(self, text="2. Mappage des Colonnes", padding="10")
        self.mapping_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.mapping_frame.columnconfigure(1, weight=1)
        self.mapping_widgets = {}
        ttk.Label(self.mapping_frame, text="Veuillez sélectionner un fichier pour commencer.", foreground="grey").grid(row=0, column=0)

        convoi_frame = ttk.LabelFrame(self, text="3. Paramètres & Logistique", padding="10")
        convoi_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        self.date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        self.depart_var = tk.StringVar(value="undefined")
        self.arrivee_var = tk.StringVar(value="undefined")
        self.capacite_var = tk.StringVar(value="50")
        self.immatriculation_var = tk.StringVar(value="undefined")
        self.transporteur_var = tk.StringVar(value="undefined")
        self.num_convoi_var = tk.StringVar(value="undefined")
        self.chauffeur_var = tk.StringVar(value="undefined")
        
        ttk.Label(convoi_frame, text="Date:").grid(row=0, column=0, padx=5, pady=2, sticky="w"); ttk.Entry(convoi_frame, textvariable=self.date_var).grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(convoi_frame, text="Capacité Bus:").grid(row=0, column=2, padx=5, pady=2, sticky="w"); ttk.Entry(convoi_frame, textvariable=self.capacite_var).grid(row=0, column=3, padx=5, pady=2)
        ttk.Label(convoi_frame, text="Départ:").grid(row=1, column=0, padx=5, pady=2, sticky="w"); ttk.Entry(convoi_frame, textvariable=self.depart_var).grid(row=1, column=1, padx=5, pady=2)
        ttk.Label(convoi_frame, text="Arrivée:").grid(row=1, column=2, padx=5, pady=2, sticky="w"); ttk.Entry(convoi_frame, textvariable=self.arrivee_var).grid(row=1, column=3, padx=5, pady=2)
        ttk.Separator(convoi_frame, orient='horizontal').grid(row=2, column=0, columnspan=4, sticky='ew', pady=10)
        ttk.Label(convoi_frame, text="Immatriculation:").grid(row=3, column=0, padx=5, pady=2, sticky="w"); ttk.Entry(convoi_frame, textvariable=self.immatriculation_var).grid(row=3, column=1, padx=5, pady=2)
        ttk.Label(convoi_frame, text="Transporteur:").grid(row=3, column=2, padx=5, pady=2, sticky="w"); ttk.Entry(convoi_frame, textvariable=self.transporteur_var).grid(row=3, column=3, padx=5, pady=2)
        ttk.Label(convoi_frame, text="N° Convoi:").grid(row=4, column=0, padx=5, pady=2, sticky="w"); ttk.Entry(convoi_frame, textvariable=self.num_convoi_var).grid(row=4, column=1, padx=5, pady=2)
        ttk.Label(convoi_frame, text="Chauffeur:").grid(row=4, column=2, padx=5, pady=2, sticky="w"); ttk.Entry(convoi_frame, textvariable=self.chauffeur_var).grid(row=4, column=3, padx=5, pady=2)

        style = ttk.Style(self); style.configure("Accent.TButton", font=("Helvetica", 12, "bold"))
        ttk.Button(self, text="Générer les Manifestes", command=self.run_process, style="Accent.TButton").grid(row=3, column=0, padx=10, pady=10)
        log_frame = ttk.LabelFrame(self, text="Journal d'exécution", padding="10")
        log_frame.grid(row=4, column=0, padx=10, pady=5, sticky="nsew")
        log_frame.columnconfigure(0, weight=1); log_frame.rowconfigure(0, weight=1)
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=10)
        self.log_text.grid(row=0, column=0, sticky="nsew")

    def run_process(self):
        self.log_text.delete('1.0', tk.END)
        self.log("--- Démarrage du processus de génération ---")
        try:
            fichier_entree = self.fichier_entree_var.get()
            if not fichier_entree: messagebox.showerror("Erreur", "Veuillez sélectionner un fichier de données."); return
            column_map = {}
            if not self.mapping_widgets: messagebox.showerror("Erreur", "Veuillez sélectionner un fichier pour activer le mappage."); return
            for key, widget in self.mapping_widgets.items():
                value = widget.get()
                if not value: messagebox.showerror("Erreur de Mappage", f"Le champ '{CHAMPS_REQUIS[key]}' doit être mappé."); return
                column_map[key] = value
            column_map['ligne_entetes'] = int(self.header_row_var.get())

            convoi_info = {
                'capacite': int(self.capacite_var.get()),
                'date': self.date_var.get() or "undefined",
                'depart': self.depart_var.get() or "undefined",
                'arrivee': self.arrivee_var.get() or "undefined",
                'immatriculation': self.immatriculation_var.get() or "undefined",
                'transporteur': self.transporteur_var.get() or "undefined",
                'num_convoi': self.num_convoi_var.get() or "undefined",
                'chauffeur': self.chauffeur_var.get() or "undefined"
            }
            if convoi_info['capacite'] <= 0: raise ValueError("La capacité doit être positive.")
            
            fichier_sortie = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Fichiers Excel", "*.xlsx")], title="Enregistrer le fichier de manifeste sous...", initialfile=f"manifestes_{convoi_info['date']}.xlsx")
            if not fichier_sortie: self.log("Sauvegarde annulée."); return
            
            familles, _, non_assignables = valider_et_preparer_donnees(fichier_entree, convoi_info['capacite'], column_map, self.log)
            
            if familles is not None:
                assignations = assigner_familles_aux_bus(familles, convoi_info['capacite'], self.log)
                generer_manifeste_excel(assignations, familles, non_assignables, fichier_sortie, convoi_info, self.log)
                messagebox.showinfo("Succès", f"Le fichier de manifeste a été généré avec succès !\n\nEmplacement : {fichier_sortie}")
            else:
                messagebox.showerror("Échec", "Le processus a échoué. Vérifiez les erreurs dans le journal.")

        except ValueError as ve: messagebox.showerror("Erreur de Valeur", f"Veuillez vérifier vos saisies.\n\n{ve}")
        except Exception as e:
            self.log(f"ERREUR INATTENDUE : {e}"); traceback.print_exc()
            messagebox.showerror("Erreur Inattendue", f"Une erreur grave est survenue.\n\n{e}")

    def log(self, message): self.log_text.insert(tk.END, message + "\n"); self.log_text.see(tk.END); self.update_idletasks()
    def select_and_load_file(self):
        try:
            try: header_row = int(self.header_row_var.get())
            except (ValueError, TypeError): messagebox.showerror("Erreur", "La ligne des en-têtes doit être un nombre entier (ex: 0, 1, 2...)."); return
            filename = filedialog.askopenfilename(title="Sélectionnez le fichier Excel", filetypes=(("Fichiers Excel", "*.xlsx *.xls"),))
            if not filename: self.log("Sélection de fichier annulée."); return
            self.fichier_entree_var.set(filename)
            self.log(f"Fichier sélectionné : {filename}")
            self.log(f"Tentative de lecture des en-têtes à la ligne : {header_row + 1} (index {header_row})")
            df_peek = pd.read_excel(filename, header=header_row, nrows=0)
            self.update_mapping_ui(df_peek.columns.tolist())
        except Exception as e:
            self.log(f"ERREUR lors de la sélection ou lecture du fichier : {e}"); traceback.print_exc()
            messagebox.showerror("Erreur de Lecture", f"Impossible de lire les en-têtes du fichier.\n\nDétail de l'erreur : {e}")
    def update_mapping_ui(self, columns):
        for widget in self.mapping_frame.winfo_children(): widget.destroy()
        self.mapping_widgets = {}
        for i, (key, label) in enumerate(CHAMPS_REQUIS.items()):
            ttk.Label(self.mapping_frame, text=f"{label}:").grid(row=i, column=0, sticky="w", padx=5, pady=2)
            combo = ttk.Combobox(self.mapping_frame, values=columns, width=50)
            combo.grid(row=i, column=1, sticky="ew", padx=5)
            self.mapping_widgets[key] = combo
            for col in columns:
                if key.replace('_', ' ') in col.lower() or label.split(' ')[0].lower() in col.lower(): combo.set(col); break

if __name__ == "__main__":
    app = App()
    app.mainloop()


# In[ ]:




