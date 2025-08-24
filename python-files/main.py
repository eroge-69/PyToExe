import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta
import json
import os
import calendar
from PIL import Image, ImageTk
import base64
import io

# Couleurs pour l'interface
COULEUR_PRINCIPALE = "#3498db"
COULEUR_SECONDAIRE = "#2ecc71"
COULEUR_FOND = "#ecf0f1"
COULEUR_TEXTE = "#2c3e50"

# Couleurs spécifiques pour les tâches
COULEUR_MPITARI = "#1a237e"  # Bleu très foncé
COULEUR_HARENA_VATOSOA = "#388e3c"  # Vert pomme
COULEUR_FAMPIOFOANA = "#f57c00"  # Orange
COULEUR_FIAINANTSIKA = "#6a1b9a"  # Rouge bordeaux
COULEUR_DEFAUT = "#2c3e50"  # Noir

# Logo JW.org en base64 (placeholder - remplacez par votre logo)
LOGO_BASE64 = """
R0lGODlhEAAQAPIAAAAAAJmZmf///wAAAAAAAAAAACH5BAEAAAIALAAAAAAQABAAAAMlGLrc/jDKSa
U4o8Qu6xMZ1oRkAI5sW6Yqy7auC8e0rQMAOw==
"""

class PlanificateurReunion:
    def __init__(self, root):
        self.root = root
        self.root.title("Plannification Mpandray anjara - Fiangonana Amboditsiry")
        self.root.geometry("1000x800")
        self.root.configure(bg=COULEUR_FOND)
        
        # Afficher le logo au démarrage
        self.afficher_logo_demarrage()
        
        # Charger les données
        self.participants = []
        self.planning = {}
        self.charger_donnees()
        
        # Configuration de la langue
        self.langue = "fr"  # Par défaut français
        
        # Textes multilingues
        self.textes = {
            "fr": {
                "title": "Planificateur de Réunion - Amboditsiry",
                "add": "Ajouter Participant",
                "name": "Nom:",
                "category": "Catégorie:",
                "add_btn": "Ajouter",
                "list": "Liste Participants",
                "generate": "Générer Planning",
                "months": "Mois à planifier:",
                "export": "Exporter PDF",
                "lang": "Langue:",
                "save": "Sauvegarder",
                "modify": "Modifier Planning",
                "clear": "Effacer Tout",
                "auto": "Remplissage Auto",
                "categories": [
                    "Anti-panahy",
                    "Mpikarakara Fiangonana",
                    "Rahalahy vita batisa",
                    "Rahalahy Tsy vita batisa",
                    "Ranabavy",
                    "Mpamaky fehitsoratra"
                ],
                "taches": [
                    "MPITARI-DRAHARAHA",
                    "Vavaka fanombohana",
                    "Harena avy ao amin'ny Tenin'Andriamanitra",
                    "Vatosoa Ara-Panahy",
                    "Famakiana baiboly",
                    "Fampiofoanana A",
                    "Fampiofoanana B",
                    "Fampiofoanana C",
                    "FIAINANTSIKA KRISTIANINA A",
                    "FIAINANTSIKA KRISTIANINA B",
                    "FIANARANA BAIBOLY",
                    "Mpamaky fehitsoratra",
                    "Vavaka famaranana"
                ]
            },
            "mg": {
                "title": "Plannification Mpandray anjara - Fiangonana Amboditsiry",
                "add": "Hanampy Mpikambana",
                "name": "Anarana:",
                "category": "Sokajy:",
                "add_btn": "Ampio",
                "list": "Lisitry ny Mpikambana",
                "generate": "Hamorona Planning",
                "months": "Volana hanaovana:",
                "export": "Exporter PDF",
                "lang": "Fiteny:",
                "save": "Hitehirizana",
                "modify": "Hanova Planning",
                "clear": "Hamafa rehetra",
                "auto": "Famenon-auto",
                "categories": [
                    "Anti-panahy",
                    "Mpikarakara Fiangonana",
                    "Rahalahy vita batisa",
                    "Rahalahy Tsy vita batisa",
                    "Ranabavy",
                    "Mpamaky fehitsoratra"
                ],
                "taches": [
                    "MPITARI-DRAHARAHA",
                    "Vavaka fanombohana",
                    "Harena avy ao amin'ny Tenin'Andriamanitra",
                    "Vatosoa Ara-Panahy",
                    "Famakiana baiboly",
                    "Fampiofoanana A",
                    "Fampiofoanana B",
                    "Fampiofoanana C",
                    "FIAINANTSIKA KRISTIANINA A",
                    "FIAINANTSIKA KRISTIANINA B",
                    "FIANARANA BAIBOLY",
                    "Mpamaky fehitsoratra",
                    "Vavaka famaranana"
                ]
            }
        }
        
        self.creer_interface()
        self.afficher_calendrier()
    
    def afficher_logo_demarrage(self):
        splash = tk.Toplevel(self.root)
        splash.title("Démarrage")
        splash.geometry("400x300")
        splash.configure(bg="white")
        
        try:
            # Charger le logo depuis base64
            logo_data = base64.b64decode(LOGO_BASE64)
            logo_image = Image.open(io.BytesIO(logo_data))
            logo_image = logo_image.resize((200, 200), Image.Resampling.LANCZOS)
            self.logo = ImageTk.PhotoImage(logo_image)
            
            tk.Label(splash, image=self.logo, bg="white").pack(pady=20)
        except:
            tk.Label(splash, text="JW.org", font=("Arial", 24, "bold"), 
                    bg="white", fg="black").pack(pady=50)
        
        tk.Label(splash, text="Plannification Mpandray anjara\namin'ny Fivoriana Andavanandro\neto amin'ny fiangonana Amboditsiry", 
                font=("Arial", 12), bg="white", fg=COULEUR_TEXTE, justify=tk.CENTER).pack(pady=10)
        
        splash.after(2000, splash.destroy)
    
    def charger_donnees(self):
        try:
            if os.path.exists("planning_data.json"):
                with open("planning_data.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.participants = data.get("participants", [])
                    self.planning = data.get("planning", {})
        except:
            self.participants = []
            self.planning = {}
    
    def sauvegarder_donnees(self):
        data = {
            "participants": self.participants,
            "planning": self.planning
        }
        with open("planning_data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def changer_langue(self, event=None):
        self.langue = self.combo_langue.get()
        self.mettre_a_jour_interface()
    
    def mettre_a_jour_interface(self):
        txt = self.textes[self.langue]
        self.root.title(txt["title"])
        self.label_nom.config(text=txt["name"])
        self.label_category.config(text=txt["category"])
        self.btn_ajouter.config(text=txt["add_btn"])
        self.btn_liste.config(text=txt["list"])
        self.btn_generer.config(text=txt["generate"])
        self.label_mois.config(text=txt["months"])
        self.btn_exporter.config(text=txt["export"])
        self.label_langue.config(text=txt["lang"])
        self.btn_sauvegarder.config(text=txt["save"])
        self.btn_modifier.config(text=txt["modify"])
        self.btn_effacer.config(text=txt["clear"])
        self.btn_auto.config(text=txt["auto"])
        
        # Mettre à jour les catégories dans la combobox
        self.combo_category['values'] = txt["categories"]
        if self.combo_category.get() not in txt["categories"]:
            self.combo_category.set(txt["categories"][0])
    
    def creer_interface(self):
        # Frame principale
        main_frame = tk.Frame(self.root, bg=COULEUR_FOND)
        main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        # Frame pour l'ajout de participants
        frame_ajout = tk.LabelFrame(main_frame, text=self.textes[self.langue]["add"], 
                                   bg=COULEUR_FOND, fg=COULEUR_TEXTE, font=("Arial", 12, "bold"))
        frame_ajout.pack(fill=tk.X, pady=10)
        
        self.label_nom = tk.Label(frame_ajout, text=self.textes[self.langue]["name"], 
                bg=COULEUR_FOND, fg=COULEUR_TEXTE)
        self.label_nom.grid(row=0, column=0, padx=5, pady=5)
        self.entry_nom = tk.Entry(frame_ajout, width=20)
        self.entry_nom.grid(row=0, column=1, padx=5, pady=5)
        
        self.label_category = tk.Label(frame_ajout, text=self.textes[self.langue]["category"], 
                                  bg=COULEUR_FOND, fg=COULEUR_TEXTE)
        self.label_category.grid(row=0, column=2, padx=5, pady=5)
        
        self.combo_category = ttk.Combobox(frame_ajout, values=self.textes[self.langue]["categories"], width=20)
        self.combo_category.set(self.textes[self.langue]["categories"][0])
        self.combo_category.grid(row=0, column=3, padx=5, pady=5)
        
        self.btn_ajouter = tk.Button(frame_ajout, text=self.textes[self.langue]["add_btn"], 
                                    command=self.ajouter_participant, bg=COULEUR_SECONDAIRE, fg="white")
        self.btn_ajouter.grid(row=0, column=4, padx=5, pady=5)
        
        # Frame pour les boutons
        frame_boutons = tk.Frame(main_frame, bg=COULEUR_FOND)
        frame_boutons.pack(fill=tk.X, pady=10)
        
        self.btn_liste = tk.Button(frame_boutons, text=self.textes[self.langue]["list"], 
                                  command=self.afficher_liste, bg=COULEUR_PRINCIPALE, fg="white")
        self.btn_liste.pack(side=tk.LEFT, padx=5)
        
        self.label_mois = tk.Label(frame_boutons, text=self.textes[self.langue]["months"], 
                                  bg=COULEUR_FOND, fg=COULEUR_TEXTE)
        self.label_mois.pack(side=tk.LEFT, padx=5)
        
        self.spin_mois = tk.Spinbox(frame_boutons, from_=1, to=6, width=5)
        self.spin_mois.pack(side=tk.LEFT, padx=5)
        
        self.btn_generer = tk.Button(frame_boutons, text=self.textes[self.langue]["generate"], 
                                    command=self.generer_planning, bg=COULEUR_SECONDAIRE, fg="white")
        self.btn_generer.pack(side=tk.LEFT, padx=5)
        
        self.btn_auto = tk.Button(frame_boutons, text=self.textes[self.langue]["auto"], 
                                 command=self.remplissage_auto, bg="#e67e22", fg="white")
        self.btn_auto.pack(side=tk.LEFT, padx=5)
        
        self.btn_modifier = tk.Button(frame_boutons, text=self.textes[self.langue]["modify"], 
                                     command=self.modifier_planning, bg="#9b59b6", fg="white")
        self.btn_modifier.pack(side=tk.LEFT, padx=5)
        
        self.btn_effacer = tk.Button(frame_boutons, text=self.textes[self.langue]["clear"], 
                                    command=self.effacer_tout, bg="#e74c3c", fg="white")
        self.btn_effacer.pack(side=tk.LEFT, padx=5)
        
        self.btn_exporter = tk.Button(frame_boutons, text=self.textes[self.langue]["export"], 
                                     command=self.exporter_pdf, bg="#34495e", fg="white")
        self.btn_exporter.pack(side=tk.LEFT, padx=5)
        
        self.btn_sauvegarder = tk.Button(frame_boutons, text=self.textes[self.langue]["save"], 
                                        command=self.sauvegarder_donnees, bg="#27ae60", fg="white")
        self.btn_sauvegarder.pack(side=tk.LEFT, padx=5)
        
        # Langue
        self.label_langue = tk.Label(frame_boutons, text=self.textes[self.langue]["lang"], 
                                    bg=COULEUR_FOND, fg=COULEUR_TEXTE)
        self.label_langue.pack(side=tk.LEFT, padx=5)
        
        self.combo_langue = ttk.Combobox(frame_boutons, values=["fr", "mg"], width=5)
        self.combo_langue.set(self.langue)
        self.combo_langue.bind("<<ComboboxSelected>>", self.changer_langue)
        self.combo_langue.pack(side=tk.LEFT, padx=5)
        
        # Frame pour le calendrier et planning
        frame_calendrier = tk.LabelFrame(main_frame, text="Calendrier & Planning", 
                                        bg=COULEUR_FOND, fg=COULEUR_TEXTE, font=("Arial", 12, "bold"))
        frame_calendrier.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Notebook pour onglets
        self.notebook = ttk.Notebook(frame_calendrier)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Onglet Calendrier
        frame_cal = tk.Frame(self.notebook, bg=COULEUR_FOND)
        self.notebook.add(frame_cal, text="Calendrier")
        
        self.calendrier_text = tk.Text(frame_cal, height=20, width=80, bg="white", fg=COULEUR_TEXTE)
        self.calendrier_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Onglet Planning
        frame_planning = tk.Frame(self.notebook, bg=COULEUR_FOND)
        self.notebook.add(frame_planning, text="Planning")
        
        # Treeview pour le planning
        columns = ("Date", "Tâche", "Participant")
        self.tree_planning = ttk.Treeview(frame_planning, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.tree_planning.heading(col, text=col)
            self.tree_planning.column(col, width=150)
        
        vsb = ttk.Scrollbar(frame_planning, orient="vertical", command=self.tree_planning.yview)
        self.tree_planning.configure(yscrollcommand=vsb.set)
        
        self.tree_planning.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        vsb.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Bind la fermeture de la fenêtre pour sauvegarder
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def get_couleur_tache(self, tache):
        if "MPITARI-DRAHARAHA" in tache:
            return COULEUR_MPITARI
        elif any(x in tache for x in ["Harena", "Vatosoa", "Famakiana"]):
            return COULEUR_HARENA_VATOSOA
        elif "Fampiofoanana" in tache:
            return COULEUR_FAMPIOFOANA
        elif "FIAINANTSIKA" in tache:
            return COULEUR_FIAINANTSIKA
        else:
            return COULEUR_DEFAUT
    
    def ajouter_participant(self):
        nom = self.entry_nom.get().strip()
        category = self.combo_category.get()
        
        if not nom:
            messagebox.showerror("Erreur", "Veuillez entrer un nom")
            return
        
        participant = {"nom": nom, "category": category}
        self.participants.append(participant)
        self.entry_nom.delete(0, tk.END)
        
        msg_fr = f"{nom} ajouté comme {category}!"
        msg_mg = f"{nom} noampiana ho {category}!"
        messagebox.showinfo("Succès", msg_fr if self.langue == "fr" else msg_mg)
        self.sauvegarder_donnees()
    
    def afficher_liste(self):
        liste_window = tk.Toplevel(self.root)
        liste_window.title("Liste des Participants" if self.langue == "fr" else "Lisitry ny Mpikambana")
        liste_window.geometry("400x300")
        
        tree = ttk.Treeview(liste_window, columns=("Nom", "Catégorie"), show="headings")
        tree.heading("Nom", text="Nom" if self.langue == "fr" else "Anarana")
        tree.heading("Catégorie", text="Catégorie" if self.langue == "fr" else "Sokajy")
        
        for p in self.participants:
            tree.insert("", "end", values=(p["nom"], p["category"]))
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def afficher_calendrier(self):
        self.calendrier_text.delete(1.0, tk.END)
        today = datetime.now()
        cal = calendar.month(today.year, today.month)
        self.calendrier_text.insert(tk.END, cal)
        
        # Mettre en évidence les mardis
        self.calendrier_text.tag_configure("mardi", foreground="red", font=("Arial", 10, "bold"))
        
        # Afficher le planning existant
        if self.planning:
            self.calendrier_text.insert(tk.END, "\n\n--- PLANNING ---\n")
            for date, roles in self.planning.items():
                date_obj = datetime.strptime(date, "%Y-%m-%d")
                if date_obj.weekday() == 1:  # Mardi
                    self.calendrier_text.insert(tk.END, f"\n{date} (MARDI):\n", "mardi")
                else:
                    self.calendrier_text.insert(tk.END, f"\n{date}:\n")
                
                for role, personne in roles.items():
                    couleur = self.get_couleur_tache(role)
                    self.calendrier_text.insert(tk.END, f"  {role}: {personne}\n", f"couleur_{couleur}")
    
    def generer_planning(self):
        if not self.participants:
            messagebox.showerror("Erreur", "Ajoutez d'abord des participants!")
            return
        
        try:
            mois = int(self.spin_mois.get())
        except:
            messagebox.showerror("Erreur", "Nombre de mois invalide!")
            return
        
        # Logique de planification automatique
        today = datetime.now()
        
        # Trouver le prochain mardi
        days_ahead = 1 - today.weekday()  # 0 = lundi, 1 = mardi
        if days_ahead <= 0:
            days_ahead += 7
        next_tuesday = today + timedelta(days=days_ahead)
        
        # Générer pour les mois demandés
        for i in range(mois * 4):  # 4 semaines par mois
            current_date = next_tuesday + timedelta(weeks=i)
            date_str = current_date.strftime("%Y-%m-%d")
            
            if date_str not in self.planning:
                self.planning[date_str] = self.generer_assignations_semaine(current_date)
        
        self.mettre_a_jour_affichage_planning()
        self.afficher_calendrier()
        messagebox.showinfo("Succès", "Planning généré avec succès!")
        self.sauvegarder_donnees()
    
    def generer_assignations_semaine(self, date):
        # Implémentation des règles métier complexes
        assignations = {}
        # ... (code d'assignation selon les règles)
        return assignations
    
    def remplissage_auto(self):
        self.generer_planning()
    
    def effacer_tout(self):
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment tout effacer?"):
            self.planning = {}
            self.mettre_a_jour_affichage_planning()
            self.afficher_calendrier()
            self.sauvegarder_donnees()
    
    def modifier_planning(self):
        # Implémentation de la modification
        pass
    
    def mettre_a_jour_affichage_planning(self):
        self.tree_planning.delete(*self.tree_planning.get_children())
        for date, roles in self.planning.items():
            for role, personne in roles.items():
                self.tree_planning.insert("", "end", values=(date, role, personne))
    
    def exporter_pdf(self):
        messagebox.showinfo("Info", "Fonction PDF à implémenter")
    
    def on_closing(self):
        self.sauvegarder_donnees()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PlanificateurReunion(root)
    root.mainloop()