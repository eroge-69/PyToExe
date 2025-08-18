import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import json
from datetime import datetime, date, timedelta
from collections import defaultdict
import os
from tkcalendar import DateEntry
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv
import sqlite3
import shutil

# --- Classe pour créer des info-bulles ---
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget; self.text = text; self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip); self.widget.bind("<Leave>", self.hide_tooltip)
    def show_tooltip(self, event):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25; y += self.widget.winfo_rooty() + 25
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True); self.tooltip_window.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tooltip_window, text=self.text, justify='left', background="#ffffe0", relief='solid', borderwidth=1, font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)
    def hide_tooltip(self, event):
        if self.tooltip_window: self.tooltip_window.destroy()
        self.tooltip_window = None

# --- Fenêtre de dialogue pour l'édition ---
class EditDialog(tk.Toplevel):
    def __init__(self, parent, entry_data, all_projects):
        super().__init__(parent)
        self.title("Modifier l'entrée"); self.geometry("500x450"); self.transient(parent); self.grab_set()
        self.parent = parent; self.entry_data = entry_data; self.all_projects = all_projects
        main_frame = ttk.Frame(self, padding=15); main_frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(main_frame, text="Date:").grid(row=0, column=0, sticky="w", pady=(0,2))
        self.date_entry = DateEntry(main_frame, width=15, date_pattern='dd/mm/yyyy', locale='fr_FR')
        self.date_entry.grid(row=1, column=0, sticky="w", pady=(0, 15))
        ttk.Label(main_frame, text="Projet:").grid(row=2, column=0, sticky="w", pady=(0,2))
        self.combo_projet = ttk.Combobox(main_frame, values=self.all_projects, state="readonly")
        self.combo_projet.grid(row=3, column=0, sticky="ew", pady=(0, 15))
        ttk.Label(main_frame, text="Jours:").grid(row=4, column=0, sticky="w", pady=(0,2))
        self.spin_jours = ttk.Spinbox(main_frame, from_=1, to=31, increment=0.25)
        self.spin_jours.grid(row=5, column=0, sticky="w", pady=(0, 15))
        ttk.Label(main_frame, text="Description:").grid(row=6, column=0, sticky="w", pady=(0,2))
        self.text_description = tk.Text(main_frame, height=8)
        self.text_description.grid(row=7, column=0, sticky="nsew")
        main_frame.rowconfigure(7, weight=1); main_frame.columnconfigure(0, weight=1)
        self.date_entry.set_date(datetime.strptime(entry_data['date'], "%Y-%m-%d"))
        self.combo_projet.set(entry_data['projet']); self.spin_jours.set(entry_data['jours'])
        self.text_description.insert("1.0", entry_data['description'])
        button_frame = ttk.Frame(self, padding=(0, 10, 0, 10)); button_frame.pack(fill=tk.X)
        btn_save = ttk.Button(button_frame, text="Sauvegarder", command=self.save_changes); btn_save.pack(side=tk.RIGHT, padx=5)
        btn_cancel = ttk.Button(button_frame, text="Annuler", command=self.destroy); btn_cancel.pack(side=tk.RIGHT)
    def save_changes(self):
        updated_data = {"id": self.entry_data['id'], "date": self.date_entry.get_date().strftime("%Y-%m-%d"), "projet": self.combo_projet.get(), "jours": float(self.spin_jours.get()), "description": self.text_description.get("1.0", tk.END).strip()}
        if updated_data['jours'] <= 0 or not updated_data['projet'] or updated_data['jours'] % 0.25 != 0:
            messagebox.showerror("Erreur", "Données invalides.", parent=self); return
        self.parent.modifier_entree_db(updated_data)
        self.parent.edit_successful = True
        messagebox.showinfo("Succès", "L'entrée a été mise à jour.", parent=self.parent); self.destroy()

# --- Fenêtre des paramètres ---
class SettingsWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Paramètres"); self.geometry("500x400"); self.transient(parent); self.grab_set()
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        projets_tab = ttk.Frame(notebook); notebook.add(projets_tab, text="Gestion des Projets")
        self.creer_onglet_projets(projets_tab)
        prefs_tab = ttk.Frame(notebook); notebook.add(prefs_tab, text="Préférences")
        ttk.Label(prefs_tab, text="Options de préférences à venir...", padding=20).pack()
        about_tab = ttk.Frame(notebook); notebook.add(about_tab, text="À propos")
        ttk.Label(about_tab, text="Suivi de Projets", font=("Helvetica", 14, "bold"), padding=(20, 20, 20, 5)).pack()
        ttk.Label(about_tab, text=f"Version: 16.0", padding=(20, 0, 20, 20)).pack()

    def creer_onglet_projets(self, tab):
        frame = ttk.Frame(tab, padding=10); frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(frame, text="Liste des projets existants:").pack(anchor="w")
        list_frame = ttk.Frame(frame); list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.project_listbox = tk.Listbox(list_frame, height=10); self.project_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.project_listbox.yview)
        self.project_listbox.config(yscrollcommand=scrollbar.set); scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.rafraichir_liste_projets()
        button_frame = ttk.Frame(frame); button_frame.pack(fill=tk.X, pady=(10, 0))
        btn_add = ttk.Button(button_frame, text="Ajouter...", command=self.ajouter_projet); btn_add.pack(side=tk.LEFT, padx=(0, 5))
        btn_remove = ttk.Button(button_frame, text="Supprimer", command=self.supprimer_projet); btn_remove.pack(side=tk.LEFT)

    def rafraichir_liste_projets(self):
        self.project_listbox.delete(0, tk.END)
        for projet in self.parent.charger_projets_db(): self.project_listbox.insert(tk.END, projet)

    def ajouter_projet(self):
        nouveau_projet = simpledialog.askstring("Ajouter un Projet", "Nom du nouveau projet:", parent=self)
        if nouveau_projet and nouveau_projet.strip():
            if self.parent.ajouter_projet_db(nouveau_projet.strip()):
                self.rafraichir_liste_projets(); self.parent.rafraichir_combobox_projets()
            else: messagebox.showwarning("Doublon", "Ce projet existe déjà.", parent=self)

    def supprimer_projet(self):
        selection = self.project_listbox.curselection()
        if not selection: messagebox.showwarning("Aucune sélection", "Veuillez sélectionner un projet.", parent=self); return
        projet_selectionne = self.project_listbox.get(selection[0])
        if messagebox.askyesno("Confirmation", f"Supprimer le projet '{projet_selectionne}' ?", parent=self):
            resultat = self.parent.supprimer_projet_db(projet_selectionne)
            if resultat == "utilisé": messagebox.showerror("Erreur", "Impossible de supprimer un projet utilisé.", parent=self)
            else: self.rafraichir_liste_projets(); self.parent.rafraichir_combobox_projets()

# --- Classe principale de l'application ---
class TimeTrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.db_name = r"C:\Users\Quentin\Desktop\Mes logiciels\time_tracker.db"
        self.init_db()
        self.title("Suivi de Projets v16.1")
        self.geometry("650x500"); self.minsize(600, 500); self.configure(bg="#F0F0F0"); self.edit_successful = False
        style = ttk.Style(self); style.theme_use('clam')
        style.configure('TLabel', background="#F0F0F0", font=('Helvetica', 11)); style.configure('TButton', font=('Helvetica', 10), padding=5)
        style.configure('TCombobox', font=('Helvetica', 10)); style.configure('TSpinbox', font=('Helvetica', 10))
        style.configure('Success.TButton', foreground='white', background='#28a745', font=('Helvetica', 10, 'bold'))
        style.configure('Info.TButton', background='#0078d7', foreground='white'); style.configure('Mini.TButton', padding=1)
        self.projets_liste = self.charger_projets_db()
        self.creer_widgets()
        self.creer_menu()
    
    def creer_widgets(self):
        main_frame = ttk.Frame(self, padding=20); main_frame.pack(fill=tk.BOTH, expand=True); main_frame.configure(style='TFrame')
        style = ttk.Style(self); style.configure('TFrame', background='#F0F0F0')
        saisie_frame = ttk.LabelFrame(main_frame, text=" Nouvelle Entrée ", padding=15)
        saisie_frame.pack(fill=tk.BOTH, expand=True); saisie_frame.configure(style='TLabelframe')
        style.configure('TLabelframe', background='#F0F0F0', bordercolor="#B0B0B0"); style.configure('TLabelframe.Label', background='#F0F0F0', font=('Helvetica', 12, 'bold'))
        saisie_frame.columnconfigure(0, weight=1); saisie_frame.columnconfigure(1, weight=1); saisie_frame.rowconfigure(5, weight=1)
        ttk.Label(saisie_frame, text="Date de l'entrée:").grid(row=0, column=0, sticky="w", pady=(0,2))
        self.date_entry = DateEntry(saisie_frame, width=15, date_pattern='dd/mm/yyyy', locale='fr_FR', font=('Helvetica', 10))
        self.date_entry.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 15))
        ttk.Label(saisie_frame, text="Nom du Projet:").grid(row=2, column=0, sticky="w", pady=(0,2))
        self.combo_projet = ttk.Combobox(saisie_frame, values=self.projets_liste, state="readonly"); 
        self.combo_projet.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        if self.projets_liste: self.combo_projet.current(0)
        ttk.Label(saisie_frame, text="Nombre de jours travaillés:").grid(row=0, column=1, sticky="w", pady=(0,2), padx=(20,0))
        self.spin_jours = ttk.Spinbox(saisie_frame, from_=0.25, to=31, increment=0.25, width=10); 
        self.spin_jours.grid(row=1, column=1, sticky="w", pady=(0, 15), padx=(20,0))
        
        # --- MODIFICATION ICI ---
        self.spin_jours.set(1)
        
        ttk.Label(saisie_frame, text="Description (facultatif):").grid(row=4, column=0, sticky="w", pady=(5,2))
        self.text_description = tk.Text(saisie_frame, height=7, font=("Helvetica", 10), relief=tk.SOLID, borderwidth=1, bg="white")
        self.text_description.grid(row=5, column=0, columnspan=2, sticky="nsew")
        action_frame = ttk.Frame(main_frame, padding=(0, 20, 0, 0), style='TFrame'); action_frame.pack(fill=tk.X)
        btn_valider = ttk.Button(action_frame, text="✓ Valider l'entrée", command=self.valider_entree, style='Success.TButton'); btn_valider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        btn_vue_semaine = ttk.Button(action_frame, text="Semaine", command=self.afficher_vue_semaine); btn_vue_semaine.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        btn_voir_mois = ttk.Button(action_frame, text="Gérer", command=self.afficher_fenetre_gestion, style='Info.TButton'); btn_voir_mois.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

    def afficher_vue_semaine(self):
        fenetre_semaine = tk.Toplevel(self); fenetre_semaine.title("Vue de la semaine"); fenetre_semaine.geometry("1200x600")
        self.current_week_date = date.today()
        nav_frame = ttk.Frame(fenetre_semaine, padding=10); nav_frame.pack(fill=tk.X)
        label_semaine = ttk.Label(nav_frame, text="", font=("Helvetica", 12, "bold")); label_semaine.pack(pady=5)
        jours_frame = ttk.Frame(fenetre_semaine); jours_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        jours_noms = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        jours_frames = []
        for i, nom_jour in enumerate(jours_noms):
            jours_frame.columnconfigure(i, weight=1)
            frame = ttk.LabelFrame(jours_frame, text=nom_jour)
            frame.grid(row=0, column=i, sticky="nsew", padx=5, pady=5)
            jours_frames.append(frame)
        jours_frame.rowconfigure(0, weight=1)
        def rafraichir_vue_semaine(ref_date):
            start_of_week = ref_date - timedelta(days=ref_date.weekday()); end_of_week = start_of_week + timedelta(days=6)
            self.current_week_date = ref_date
            label_semaine.config(text=f"Semaine du {start_of_week.strftime('%d/%m/%Y')} au {end_of_week.strftime('%d/%m/%Y')}")
            entrees_semaine = self.recuperer_entrees_par_intervalle(start_of_week, end_of_week)
            entrees_par_jour = defaultdict(list)
            for entree in entrees_semaine: entrees_par_jour[entree['date']].append(entree)
            for i, frame in enumerate(jours_frames):
                for widget in frame.winfo_children(): widget.destroy()
                current_day = start_of_week + timedelta(days=i)
                frame.config(text=f"{jours_noms[i]} {current_day.strftime('%d/%m')}")
                day_entries = entrees_par_jour.get(current_day.strftime('%Y-%m-%d'), [])
                if not day_entries: ttk.Label(frame, text="Aucune entrée", foreground="grey").pack(padx=5, pady=5)
                else:
                    for entree in day_entries:
                        entry_text = f"▶ {entree['projet']} ({entree['jours']}j)"; label = ttk.Label(frame, text=entry_text, wraplength=150, anchor="w")
                        label.pack(fill=tk.X, padx=5, pady=2); ToolTip(label, entree['description'])
        def semaine_precedente(): rafraichir_vue_semaine(self.current_week_date - timedelta(weeks=1))
        def semaine_suivante(): rafraichir_vue_semaine(self.current_week_date + timedelta(weeks=1))
        btn_prev = ttk.Button(label_semaine, text="< Sem. Préc.", command=semaine_precedente); btn_prev.pack(side=tk.LEFT, padx=20)
        btn_next = ttk.Button(label_semaine, text="Sem. Suiv. >", command=semaine_suivante); btn_next.pack(side=tk.RIGHT, padx=20)
        rafraichir_vue_semaine(self.current_week_date)

    def creer_menu(self):
        menubar = tk.Menu(self); self.config(menu=menubar)
        fichier_menu = tk.Menu(menubar, tearoff=0); menubar.add_cascade(label="Fichier", menu=fichier_menu)
        fichier_menu.add_command(label="Paramètres...", command=self.ouvrir_fenetre_parametres)
        fichier_menu.add_separator()
        fichier_menu.add_command(label="Tableau de bord...", command=self.afficher_tableau_de_bord)
        export_menu = tk.Menu(fichier_menu, tearoff=0)
        fichier_menu.add_cascade(label="Exporter le rapport...", menu=export_menu)
        export_menu.add_command(label="En format CSV", command=self.lancer_export_csv)
        export_menu.add_command(label="En format TXT", command=self.lancer_export_txt)
        fichier_menu.add_separator()
        fichier_menu.add_command(label="Sauvegarder les données...", command=self.sauvegarder_base_de_donnees)
        fichier_menu.add_command(label="Restaurer une sauvegarde...", command=self.restaurer_base_de_donnees)
        fichier_menu.add_separator()
        fichier_menu.add_command(label="Quitter", command=self.quit)
    
    def ouvrir_fenetre_parametres(self):
        SettingsWindow(self)

    def rafraichir_combobox_projets(self):
        self.projets_liste = self.charger_projets_db()
        self.combo_projet['values'] = self.projets_liste
        if self.projets_liste: self.combo_projet.current(0)
        else: self.combo_projet.set('')

    def sauvegarder_base_de_donnees(self):
        nom_fichier_defaut = f"sauvegarde_edt_{datetime.now().strftime('%Y-%m-%d')}.db"
        filepath = filedialog.asksaveasfilename(
            title="Enregistrer la sauvegarde sous...",
            initialfile=nom_fichier_defaut,
            defaultextension=".db",
            filetypes=[("Fichiers de base de données", "*.db"), ("Tous les fichiers", "*.*")]
        )
        if not filepath: return
        try:
            shutil.copy(self.db_name, filepath)
            messagebox.showinfo("Succès", "Sauvegarde de la base de données terminée avec succès !")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue lors de la sauvegarde :\n{e}")

    def restaurer_base_de_donnees(self):
        confirmation = messagebox.askyesno(
            "ATTENTION",
            "La restauration d'une sauvegarde ÉCRASERA toutes les données actuelles.\n\n"
            "Cette action est irréversible.\n\n"
            "Êtes-vous sûr de vouloir continuer ?",
            icon='warning'
        )
        if not confirmation: return
        
        filepath = filedialog.askopenfilename(
            title="Sélectionner un fichier de sauvegarde à restaurer",
            filetypes=[("Fichiers de base de données", "*.db"), ("Tous les fichiers", "*.*")]
        )
        if not filepath: return
        try:
            shutil.copy(filepath, self.db_name)
            messagebox.showinfo(
                "Restauration terminée",
                "Restauration terminée avec succès.\n\n"
                "Veuillez redémarrer l'application pour appliquer les changements."
            )
            self.quit()
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue lors de la restauration :\n{e}")

    def init_db(self):
        db_directory = os.path.dirname(self.db_name)
        os.makedirs(db_directory, exist_ok=True)
        conn = sqlite3.connect(self.db_name); cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS projets (id INTEGER PRIMARY KEY, nom TEXT NOT NULL UNIQUE)')
        cursor.execute('CREATE TABLE IF NOT EXISTS entrees (id INTEGER PRIMARY KEY, date TEXT NOT NULL, jours REAL NOT NULL, description TEXT, projet_id INTEGER, FOREIGN KEY (projet_id) REFERENCES projets (id))')
        cursor.execute("SELECT COUNT(*) FROM projets")
        if cursor.fetchone()[0] == 0:
            projets_defaut = ["Projet Alpha", "Projet Beta", "Réunion", "Tâche administrative"]
            cursor.executemany("INSERT INTO projets (nom) VALUES (?)", [(p,) for p in projets_defaut])
        conn.commit(); conn.close()
    def charger_projets_db(self):
        conn = sqlite3.connect(self.db_name); cursor = conn.cursor()
        cursor.execute("SELECT nom FROM projets ORDER BY nom ASC");
        projets = [row[0] for row in cursor.fetchall()]
        conn.close(); return projets
    def ajouter_projet_db(self, nom_projet):
        conn = sqlite3.connect(self.db_name); cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO projets (nom) VALUES (?)", (nom_projet,)); conn.commit(); return True
        except sqlite3.IntegrityError: return False
        finally: conn.close()
    def supprimer_projet_db(self, nom_projet):
        conn = sqlite3.connect(self.db_name); cursor = conn.cursor()
        cursor.execute("SELECT id FROM projets WHERE nom = ?", (nom_projet,))
        projet_id_row = cursor.fetchone()
        if projet_id_row:
            cursor.execute("SELECT COUNT(*) FROM entrees WHERE projet_id = ?", (projet_id_row[0],))
            if cursor.fetchone()[0] > 0: conn.close(); return "utilisé"
        cursor.execute("DELETE FROM projets WHERE nom = ?", (nom_projet,)); conn.commit(); conn.close(); return "succès"
    def valider_entree_db(self, entree):
        conn = sqlite3.connect(self.db_name); cursor = conn.cursor()
        cursor.execute("SELECT id FROM projets WHERE nom = ?", (entree['projet'],)); projet_id = cursor.fetchone()[0]
        cursor.execute("INSERT INTO entrees (date, jours, description, projet_id) VALUES (?, ?, ?, ?)", (entree['date'], entree['jours'], entree['description'], projet_id))
        conn.commit(); conn.close()
    def modifier_entree_db(self, entree):
        conn = sqlite3.connect(self.db_name); cursor = conn.cursor()
        cursor.execute("SELECT id FROM projets WHERE nom = ?", (entree['projet'],)); projet_id = cursor.fetchone()[0]
        cursor.execute("UPDATE entrees SET date = ?, jours = ?, description = ?, projet_id = ? WHERE id = ?", (entree['date'], entree['jours'], entree['description'], projet_id, entree['id']))
        conn.commit(); conn.close()
    def supprimer_entree_db(self, entree_id):
        conn = sqlite3.connect(self.db_name); cursor = conn.cursor()
        cursor.execute("DELETE FROM entrees WHERE id = ?", (entree_id,)); conn.commit(); conn.close()
    def recuperer_entrees_par_mois(self, mois, annee):
        conn = sqlite3.connect(self.db_name); cursor = conn.cursor()
        query = "SELECT e.id, e.date, p.nom, e.jours, e.description FROM entrees e JOIN projets p ON e.projet_id = p.id WHERE STRFTIME('%m', e.date) = ? AND STRFTIME('%Y', e.date) = ? ORDER BY e.date ASC"
        cursor.execute(query, (f"{mois:02d}", str(annee)))
        entrees = [{'id': r[0], 'date': r[1], 'projet': r[2], 'jours': r[3], 'description': r[4]} for r in cursor.fetchall()]
        conn.close(); return entrees
    def recuperer_entrees_par_intervalle(self, date_debut, date_fin):
        conn = sqlite3.connect(self.db_name); cursor = conn.cursor()
        query = "SELECT e.id, e.date, p.nom, e.jours, e.description FROM entrees e JOIN projets p ON e.projet_id = p.id WHERE e.date BETWEEN ? AND ? ORDER BY e.date ASC"
        cursor.execute(query, (date_debut.strftime('%Y-%m-%d'), date_fin.strftime('%Y-%m-%d')))
        entrees = [{'id': r[0], 'date': r[1], 'projet': r[2], 'jours': r[3], 'description': r[4]} for r in cursor.fetchall()]
        conn.close(); return entrees
    def valider_entree(self):
        projet = self.combo_projet.get(); date_selectionnee = self.date_entry.get_date()
        try: jours = float(self.spin_jours.get())
        except ValueError: messagebox.showerror("Erreur", "Le nombre de jours doit être numérique."); return
        if jours % 0.25 != 0: messagebox.showerror("Erreur", "Le nombre de jours doit être un multiple de 0.25."); return
        if not projet: messagebox.showerror("Erreur", "Veuillez sélectionner un projet."); return
        if jours <= 0: messagebox.showerror("Erreur", "Le nombre de jours doit être positif."); return
        description = self.text_description.get("1.0", tk.END).strip()
        entree = {"date": date_selectionnee.strftime("%Y-%m-%d"), "projet": projet, "jours": jours, "description": description}
        self.valider_entree_db(entree); messagebox.showinfo("Succès", f"Entrée sauvegardée !")
        self.text_description.delete("1.0", tk.END); self.spin_jours.set(1)
    def afficher_fenetre_gestion(self):
        fenetre_gestion = tk.Toplevel(self); fenetre_gestion.title("Gestion des entrées"); fenetre_gestion.geometry("850x650")
        frame_selection = ttk.Frame(fenetre_gestion, padding="10"); frame_selection.pack(fill=tk.X)
        frame_mois = ttk.LabelFrame(frame_selection, text=" Sélection par mois ", padding=10); frame_mois.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Label(frame_mois, text="Mois:").pack(side=tk.LEFT, padx=(0, 5))
        mois_noms = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
        combo_mois = ttk.Combobox(frame_mois, values=mois_noms, state="readonly", width=12); combo_mois.current(datetime.now().month - 1); combo_mois.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(frame_mois, text="Année:").pack(side=tk.LEFT, padx=(0, 5))
        current_year = datetime.now().year
        spin_annee = ttk.Spinbox(frame_mois, from_=current_year - 10, to=current_year + 10, width=7); spin_annee.set(current_year); spin_annee.pack(side=tk.LEFT, padx=(0, 10))
        frame_periode = ttk.LabelFrame(frame_selection, text=" Sélection par période ", padding=10); frame_periode.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        ttk.Label(frame_periode, text="Du:").pack(side=tk.LEFT, padx=(0, 5))
        date_debut_entry = DateEntry(frame_periode, width=12, date_pattern='dd/mm/yyyy', locale='fr_FR'); date_debut_entry.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(frame_periode, text="Au:").pack(side=tk.LEFT, padx=(0, 5))
        date_fin_entry = DateEntry(frame_periode, width=12, date_pattern='dd/mm/yyyy', locale='fr_FR'); date_fin_entry.pack(side=tk.LEFT)
        frame_tableau = ttk.Frame(fenetre_gestion, padding="10"); frame_tableau.pack(fill=tk.BOTH, expand=True)
        tree = ttk.Treeview(frame_tableau, columns=('date', 'projet', 'jours', 'description'), show='headings')
        tree.heading('date', text='Date'); tree.heading('projet', text='Projet'); tree.heading('jours', text='Jours'); tree.heading('description', text='Description')
        tree.column('date', width=100, anchor=tk.CENTER); tree.column('projet', width=150); tree.column('jours', width=80, anchor=tk.CENTER); tree.column('description', width=450)
        scrollbar = ttk.Scrollbar(frame_tableau, orient=tk.VERTICAL, command=tree.yview); tree.configure(yscroll=scrollbar.set); scrollbar.pack(side=tk.RIGHT, fill=tk.Y); tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.dernier_filtre = {}
        def rafraichir_tableau_visuel(entrees):
            for i in tree.get_children(): tree.delete(i)
            for entree in entrees: tree.insert('', tk.END, iid=entree['id'], values=(entree['date'], entree['projet'], entree['jours'], entree['description']))
        def charger_par_mois():
            mois = combo_mois.current() + 1; annee = int(spin_annee.get()); self.dernier_filtre = {'type': 'mois', 'mois': mois, 'annee': annee}
            entrees = self.recuperer_entrees_par_mois(mois, annee); rafraichir_tableau_visuel(entrees)
        def charger_par_intervalle():
            date_debut = date_debut_entry.get_date(); date_fin = date_fin_entry.get_date(); self.dernier_filtre = {'type': 'intervalle', 'debut': date_debut, 'fin': date_fin}
            entrees = self.recuperer_entrees_par_intervalle(date_debut, date_fin); rafraichir_tableau_visuel(entrees)
        ttk.Button(frame_mois, text="Charger", command=charger_par_mois).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(frame_periode, text="Charger", command=charger_par_intervalle).pack(side=tk.LEFT, padx=(10, 0))
        action_frame_gestion = ttk.Frame(fenetre_gestion, padding=(0,0,0,10)); action_frame_gestion.pack(fill=tk.X)
        btn_modifier = ttk.Button(action_frame_gestion, text="✏️ Modifier", command=lambda: self.modifier_entree_selectionnee(tree))
        btn_modifier.pack(side=tk.LEFT, expand=True, padx=10)
        btn_supprimer = ttk.Button(action_frame_gestion, text="🗑️ Supprimer", command=lambda: self.supprimer_entree_selectionnee(tree, fenetre_gestion))
        btn_supprimer.pack(side=tk.LEFT, expand=True, padx=10)
        charger_par_mois()
    def modifier_entree_selectionnee(self, tree):
        selection = tree.selection();
        if not selection: messagebox.showwarning("Aucune sélection", "Veuillez sélectionner une entrée."); return
        entree_id = int(selection[0])
        conn = sqlite3.connect(self.db_name); cursor = conn.cursor()
        cursor.execute("SELECT e.id, e.date, p.nom, e.jours, e.description FROM entrees e JOIN projets p ON e.projet_id = p.id WHERE e.id = ?", (entree_id,))
        res = cursor.fetchone(); conn.close()
        entree_a_modifier = {'id': res[0], 'date': res[1], 'projet': res[2], 'jours': res[3], 'description': res[4]}
        self.edit_successful = False; dialog = EditDialog(self, entree_a_modifier, self.projets_liste)
        self.wait_window(dialog)
        if self.edit_successful:
            if self.dernier_filtre['type'] == 'mois': entrees = self.recuperer_entrees_par_mois(self.dernier_filtre['mois'], self.dernier_filtre['annee'])
            else: entrees = self.recuperer_entrees_par_intervalle(self.dernier_filtre['debut'], self.dernier_filtre['fin'])
            for i in tree.get_children(): tree.delete(i)
            for entree in entrees: tree.insert('', tk.END, iid=entree['id'], values=(entree['date'], entree['projet'], entree['jours'], entree['description']))
    def supprimer_entree_selectionnee(self, tree, window):
        selection = tree.selection()
        if not selection: messagebox.showwarning("Aucune sélection", "Veuillez sélectionner une entrée.", parent=window); return
        entree_id = int(selection[0])
        if messagebox.askyesno("Confirmation", f"Supprimer cette entrée ?", parent=window):
            self.supprimer_entree_db(entree_id)
            if self.dernier_filtre['type'] == 'mois': entrees = self.recuperer_entrees_par_mois(self.dernier_filtre['mois'], self.dernier_filtre['annee'])
            else: entrees = self.recuperer_entrees_par_intervalle(self.dernier_filtre['debut'], self.dernier_filtre['fin'])
            for i in tree.get_children(): tree.delete(i)
            for entree in entrees: tree.insert('', tk.END, iid=entree['id'], values=(entree['date'], entree['projet'], entree['jours'], entree['description']))
            messagebox.showinfo("Succès", "L'entrée a été supprimée.", parent=window)
    def afficher_tableau_de_bord(self):
        fenetre_dashboard = tk.Toplevel(self); fenetre_dashboard.title("Tableau de bord avancé"); fenetre_dashboard.geometry("850x700")
        frame_controles = ttk.Frame(fenetre_dashboard, padding="10"); frame_controles.pack(fill=tk.X)
        frame_mois = ttk.LabelFrame(frame_controles, text=" Période par mois ", padding=10); frame_mois.pack(side=tk.LEFT, padx=(0, 5))
        mois_noms = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
        combo_mois = ttk.Combobox(frame_mois, values=mois_noms, state="readonly", width=12); combo_mois.current(datetime.now().month - 1); combo_mois.pack(side=tk.LEFT, padx=(0, 10))
        current_year = datetime.now().year
        spin_annee = ttk.Spinbox(frame_mois, from_=current_year - 10, to=current_year + 10, width=7); spin_annee.set(current_year); spin_annee.pack(side=tk.LEFT)
        frame_periode = ttk.LabelFrame(frame_controles, text=" Période personnalisée ", padding=10); frame_periode.pack(side=tk.LEFT, padx=(5, 0))
        date_debut_entry = DateEntry(frame_periode, width=12, date_pattern='dd/mm/yyyy', locale='fr_FR'); date_debut_entry.pack(side=tk.LEFT, padx=(0, 10))
        date_fin_entry = DateEntry(frame_periode, width=12, date_pattern='dd/mm/yyyy', locale='fr_FR'); date_fin_entry.pack(side=tk.LEFT)
        frame_options = ttk.Frame(fenetre_dashboard, padding="10"); frame_options.pack(fill=tk.X)
        chart_type = tk.StringVar(value="pie")
        ttk.Radiobutton(frame_options, text="Circulaire", variable=chart_type, value="pie").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(frame_options, text="Barres", variable=chart_type, value="bar").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(frame_options, text="Courbe (Tendance)", variable=chart_type, value="line").pack(side=tk.LEFT, padx=5)
        frame_graphique = ttk.Frame(fenetre_dashboard, padding=10); frame_graphique.pack(fill=tk.BOTH, expand=True)
        def dessiner_graphique(donnees, titre_periode):
            for widget in frame_graphique.winfo_children(): widget.destroy()
            if not donnees: ttk.Label(frame_graphique, text="Aucune donnée pour cette période.").pack(pady=50); return
            total_jours = sum(e['jours'] for e in donnees)
            fig = Figure(figsize=(8, 5.5), dpi=100); ax = fig.add_subplot(111)
            if chart_type.get() == "line":
                jours_par_date = defaultdict(float)
                for e in donnees: jours_par_date[datetime.strptime(e['date'], '%Y-%m-%d')] += e['jours']
                dates_triees = sorted(jours_par_date.keys()); valeurs = [jours_par_date[d] for d in dates_triees]
                ax.plot(dates_triees, valeurs, marker='o', linestyle='-')
                ax.set_title(f"Tendance pour {titre_periode}\nTotal: {total_jours:.2f} jours"); ax.set_ylabel("Jours travaillés"); fig.autofmt_xdate(rotation=45)
            else:
                projets_agreges = defaultdict(float)
                for e in donnees: projets_agreges[e['projet']] += e['jours']
                if chart_type.get() == "pie": ax.pie(projets_agreges.values(), labels=projets_agreges.keys(), autopct='%1.1f%%', startangle=140)
                else: ax.bar(projets_agreges.keys(), projets_agreges.values()); ax.set_ylabel("Nombre de jours"); fig.autofmt_xdate(rotation=30)
                ax.set_title(f"Répartition pour {titre_periode}\nTotal: {total_jours:.2f} jours")
            fig.tight_layout(pad=2.0); canvas = FigureCanvasTkAgg(fig, master=frame_graphique); canvas.draw(); canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        def charger_par_mois():
            mois = combo_mois.current() + 1; annee = int(spin_annee.get()); donnees = self.recuperer_entrees_par_mois(mois, annee)
            dessiner_graphique(donnees, f"{mois_noms[mois-1]} {annee}")
        def charger_par_intervalle():
            date_debut = date_debut_entry.get_date(); date_fin = date_fin_entry.get_date(); donnees = self.recuperer_entrees_par_intervalle(date_debut, date_fin)
            dessiner_graphique(donnees, f"du {date_debut.strftime('%d/%m/%Y')} au {date_fin.strftime('%d/%m/%Y')}")
        ttk.Button(frame_mois, text="Analyser", command=charger_par_mois).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(frame_periode, text="Analyser", command=charger_par_intervalle).pack(side=tk.LEFT, padx=(10, 0))
        charger_par_mois()
    def lancer_export_csv(self): self.lancer_dialogue_export('csv')
    def lancer_export_txt(self): self.lancer_dialogue_export('txt')
    def lancer_dialogue_export(self, format_export):
        dialog = tk.Toplevel(self); dialog.title("Choisir une période"); dialog.geometry("300x150"); dialog.transient(self); dialog.grab_set()
        ttk.Label(dialog, text="Mois (1-12):").pack(pady=(10,0)); entry_mois = ttk.Entry(dialog); entry_mois.pack(); entry_mois.insert(0, str(datetime.now().month))
        ttk.Label(dialog, text="Année (YYYY):").pack(pady=(10,0)); entry_annee = ttk.Entry(dialog); entry_annee.pack(); entry_annee.insert(0, str(datetime.now().year))
        def on_submit():
            try:
                mois = int(entry_mois.get()); annee = int(entry_annee.get())
                if not 1 <= mois <= 12: raise ValueError
                dialog.destroy()
                if format_export == 'csv': self.proceder_a_exportation_csv(mois, annee)
                else: self.proceder_a_exportation_txt(mois, annee)
            except (ValueError, TypeError): messagebox.showerror("Erreur", "Veuillez entrer une date valide.", parent=dialog)
        ttk.Button(dialog, text="Exporter", command=on_submit).pack(pady=20)
    def proceder_a_exportation_csv(self, mois, annee):
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("Fichiers CSV", "*.csv")], title="Enregistrer le rapport CSV", initialfile=f"Rapport_{annee}_{mois:02d}.csv")
        if not filepath: return
        donnees_a_exporter = self.recuperer_entrees_par_mois(mois, annee)
        if not donnees_a_exporter: messagebox.showinfo("Information", f"Aucune donnée à exporter pour {mois}/{annee}."); return
        try:
            with open(filepath, 'w', encoding='utf-8-sig', newline='') as f:
                entetes = ['Date', 'Projet', 'Jours', 'Description']
                writer = csv.writer(f, delimiter=';'); writer.writerow(entetes)
                for entree in donnees_a_exporter: writer.writerow([entree['date'], entree['projet'], entree['jours'], entree['description']])
            messagebox.showinfo("Succès", f"Rapport CSV exporté avec succès.")
        except Exception as e: messagebox.showerror("Erreur", f"Impossible d'enregistrer le fichier:\n{e}")
    def proceder_a_exportation_txt(self, mois, annee):
        rapport_texte, a_des_donnees = self.generer_texte_rapport(mois, annee)
        if not a_des_donnees: messagebox.showinfo("Information", f"Aucune donnée à exporter pour {mois}/{annee}."); return
        filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Fichiers Texte", "*.txt")], title="Enregistrer le rapport TXT", initialfile=f"Rapport_{annee}_{mois:02d}.txt")
        if not filepath: return
        try:
            with open(filepath, 'w', encoding='utf-8') as f: f.write(rapport_texte)
            messagebox.showinfo("Succès", f"Rapport TXT exporté avec succès.")
        except Exception as e: messagebox.showerror("Erreur", f"Impossible d'enregistrer le fichier:\n{e}")
    def generer_texte_rapport(self, mois, annee):
        donnees_filtrees = self.recuperer_entrees_par_mois(mois, annee)
        if not donnees_filtrees: return "", False
        projets_groupes = defaultdict(lambda: {"total_jours": 0, "descriptions": []})
        for entree in donnees_filtrees:
            projets_groupes[entree['projet']]['total_jours'] += entree['jours']
            if entree['description']: projets_groupes[entree['projet']]['descriptions'].append(entree['description'])
        lignes = [f"RAPPORT D'ACTIVITÉ POUR LE MOIS {mois}/{annee}", "=" * 40, ""]
        for nom_projet, details in projets_groupes.items():
            lignes.append(f"PROJET : {nom_projet}"); lignes.append("-" * 30)
            lignes.append(f"  Nombre total de jours travaillés : {details['total_jours']:.2f} jours")
            if details['descriptions']:
                lignes.append("\n  Détail des descriptions :")
                for i, desc in enumerate(details['descriptions'], start=1):
                    lignes.append(f"    Jour {i}: {'    '.join(desc.splitlines())}")
            lignes.append("\n" + "=" * 40 + "\n")
        return "\n".join(lignes), True
        
if __name__ == "__main__":
    app = TimeTrackerApp()
    app.mainloop()