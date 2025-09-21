import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime

class OSINTResearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OSINT Research Manager - Local")
        self.root.geometry("1100x750")
        self.root.minsize(900, 600)
        
        # Configuration du dossier de données
        self.data_dir = os.path.join(os.path.expanduser("~"), "OSINT_Research_Data")
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        self.current_project = None
        self.current_subject = None
        self.projects = self.load_projects_list()
        
        # Configuration des styles
        self.setup_styles()
        self.setup_ui()
        
    def setup_styles(self):
        style = ttk.Style()
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'), background='#2c3e50', foreground='white')
        style.configure('Title.TLabel', font=('Arial', 14, 'bold'), foreground='#2c3e50')
        style.configure('Section.TLabel', font=('Arial', 11, 'bold'), foreground='#34495e')
        
    def setup_ui(self):
        # Configuration de la grille principale
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Sidebar
        self.setup_sidebar()
        
        # Main content area
        self.setup_main_content()
        
    def setup_sidebar(self):
        sidebar = ttk.Frame(self.root, width=250, padding="10")
        sidebar.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.W))
        sidebar.grid_propagate(False)
        
        # Titre sidebar
        ttk.Label(sidebar, text="Gestion des Projets", style='Title.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 15))
        
        # Nouveau projet
        ttk.Label(sidebar, text="Nouveau projet:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.project_name = ttk.Entry(sidebar, width=20)
        self.project_name.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(sidebar, text="Créer projet", command=self.create_project).grid(row=3, column=0, pady=(0, 20))
        
        # Liste des projets
        ttk.Label(sidebar, text="Projets existants:").grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        
        project_frame = ttk.Frame(sidebar)
        project_frame.grid(row=5, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        project_frame.columnconfigure(0, weight=1)
        project_frame.rowconfigure(0, weight=1)
        
        self.projects_list = tk.Listbox(project_frame, height=8, bg='white', selectbackground='#3498db')
        self.projects_list.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.projects_list.bind('<<ListboxSelect>>', self.on_project_select)
        
        project_scroll = ttk.Scrollbar(project_frame, orient=tk.VERTICAL, command=self.projects_list.yview)
        project_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.projects_list.config(yscrollcommand=project_scroll.set)
        
        self.refresh_projects_list()
        
        # Sujets
        ttk.Label(sidebar, text="Sujets dans le projet:").grid(row=6, column=0, sticky=tk.W, pady=(10, 5))
        
        subject_frame = ttk.Frame(sidebar)
        subject_frame.grid(row=7, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        subject_frame.columnconfigure(0, weight=1)
        subject_frame.rowconfigure(0, weight=1)
        
        self.subjects_list = tk.Listbox(subject_frame, height=8, bg='white', selectbackground='#3498db')
        self.subjects_list.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.subjects_list.bind('<<ListboxSelect>>', self.on_subject_select)
        
        subject_scroll = ttk.Scrollbar(subject_frame, orient=tk.VERTICAL, command=self.subjects_list.yview)
        subject_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.subjects_list.config(yscrollcommand=subject_scroll.set)
        
        # Nouveau sujet
        ttk.Label(sidebar, text="Nouveau sujet:").grid(row=8, column=0, sticky=tk.W, pady=(10, 5))
        self.subject_name = ttk.Entry(sidebar, width=20)
        self.subject_name.grid(row=9, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(sidebar, text="Ajouter sujet", command=self.add_subject).grid(row=10, column=0, pady=(0, 20))
        
        # Boutons d'action
        ttk.Button(sidebar, text="Sauvegarder", command=self.save_data).grid(row=11, column=0, pady=(0, 5))
        ttk.Button(sidebar, text="Supprimer sujet", command=self.delete_subject).grid(row=12, column=0, pady=(0, 5))
        ttk.Button(sidebar, text="Supprimer projet", command=self.delete_project).grid(row=13, column=0, pady=(0, 5))
        
        sidebar.columnconfigure(0, weight=1)
        
    def setup_main_content(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=1, sticky=(tk.N, tk.S, tk.E, tk.W))
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Header
        self.header_label = ttk.Label(main_frame, text="Sélectionnez un projet et un sujet", style='Header.TLabel', padding=10)
        self.header_label.grid(row=0, column=0, sticky=(tk.E, tk.W), pady=(0, 10))
        
        # Notebook
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        
        # Création des onglets
        self.identity_frame = ttk.Frame(self.notebook, padding="10")
        self.contact_frame = ttk.Frame(self.notebook, padding="10")
        self.online_frame = ttk.Frame(self.notebook, padding="10")
        self.notes_frame = ttk.Frame(self.notebook, padding="10")
        
        self.notebook.add(self.identity_frame, text="Identité")
        self.notebook.add(self.contact_frame, text="Coordonnées")
        self.notebook.add(self.online_frame, text="En ligne")
        self.notebook.add(self.notes_frame, text="Notes")
        
        # Configuration des onglets
        self.setup_identity_tab()
        self.setup_contact_tab()
        self.setup_online_tab()
        self.setup_notes_tab()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Prêt - Sélectionnez ou créez un projet")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, padding=5)
        status_bar.grid(row=2, column=0, sticky=(tk.E, tk.W), pady=(10, 0))
        
    def setup_identity_tab(self):
        ttk.Label(self.identity_frame, text="Informations d'Identité", style='Title.TLabel').grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))
        
        fields = [
            ("Prénom:", "first_name"),
            ("Nom:", "last_name"),
            ("Pseudonyme:", "alias"),
            ("Date de naissance:", "birth_date"),
            ("Lieu de naissance:", "birth_place"),
            ("Nationalité:", "nationality"),
            ("Sexe:", "gender")
        ]
        
        self.identity_fields = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(self.identity_frame, text=label).grid(row=i+1, column=0, sticky=tk.W, pady=2, padx=5)
            entry = ttk.Entry(self.identity_frame, width=30)
            entry.grid(row=i+1, column=1, sticky=(tk.W, tk.E), pady=2, padx=5)
            self.identity_fields[key] = entry
        
        ttk.Label(self.identity_frame, text="Description physique:").grid(row=8, column=0, sticky=tk.W, pady=(15, 5), padx=5)
        self.identity_fields["physical_desc"] = scrolledtext.ScrolledText(self.identity_frame, width=50, height=4)
        self.identity_fields["physical_desc"].grid(row=9, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        self.identity_frame.columnconfigure(1, weight=1)
        
    def setup_contact_tab(self):
        ttk.Label(self.contact_frame, text="Coordonnées", style='Title.TLabel').grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))
        
        fields = [
            ("Téléphone:", "phone"),
            ("Email:", "email"),
            ("Adresse:", "address"),
            ("Ville:", "city"),
            ("Code postal:", "postal_code"),
            ("Pays:", "country")
        ]
        
        self.contact_fields = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(self.contact_frame, text=label).grid(row=i+1, column=0, sticky=tk.W, pady=2, padx=5)
            if key == "address":
                entry = scrolledtext.ScrolledText(self.contact_frame, width=40, height=3)
                entry.grid(row=i+1, column=1, sticky=(tk.W, tk.E), pady=2, padx=5)
            else:
                entry = ttk.Entry(self.contact_frame, width=30)
                entry.grid(row=i+1, column=1, sticky=(tk.W, tk.E), pady=2, padx=5)
            self.contact_fields[key] = entry
        
        ttk.Label(self.contact_frame, text="Autres contacts:").grid(row=7, column=0, sticky=tk.W, pady=(15, 5), padx=5)
        self.contact_fields["other_contact"] = scrolledtext.ScrolledText(self.contact_frame, width=50, height=3)
        self.contact_fields["other_contact"].grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        self.contact_frame.columnconfigure(1, weight=1)
        
    def setup_online_tab(self):
        ttk.Label(self.online_frame, text="Présence en Ligne", style='Title.TLabel').grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))
        
        fields = [
            ("Site web:", "website"),
            ("Facebook:", "facebook"),
            ("Twitter:", "twitter"),
            ("Instagram:", "instagram"),
            ("LinkedIn:", "linkedin")
        ]
        
        self.online_fields = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(self.online_frame, text=label).grid(row=i+1, column=0, sticky=tk.W, pady=2, padx=5)
            entry = ttk.Entry(self.online_frame, width=30)
            entry.grid(row=i+1, column=1, sticky=(tk.W, tk.E), pady=2, padx=5)
            self.online_fields[key] = entry
        
        ttk.Label(self.online_frame, text="Autres réseaux:").grid(row=6, column=0, sticky=tk.W, pady=(15, 5), padx=5)
        self.online_fields["other_social"] = scrolledtext.ScrolledText(self.online_frame, width=50, height=2)
        self.online_fields["other_social"].grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        ttk.Label(self.online_frame, text="Pseudos en ligne:").grid(row=8, column=0, sticky=tk.W, pady=(15, 5), padx=5)
        self.online_fields["online_aliases"] = scrolledtext.ScrolledText(self.online_frame, width=50, height=2)
        self.online_fields["online_aliases"].grid(row=9, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        self.online_frame.columnconfigure(1, weight=1)
        
    def setup_notes_tab(self):
        ttk.Label(self.notes_frame, text="Notes de Recherche", style='Title.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 15))
        
        ttk.Label(self.notes_frame, text="Notes:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.research_notes = scrolledtext.ScrolledText(self.notes_frame, width=70, height=15)
        self.research_notes.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        ttk.Label(self.notes_frame, text="Sources:").grid(row=3, column=0, sticky=tk.W, pady=(15, 5))
        self.sources_text = scrolledtext.ScrolledText(self.notes_frame, width=70, height=8)
        self.sources_text.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.notes_frame.columnconfigure(0, weight=1)
        self.notes_frame.rowconfigure(2, weight=1)
        self.notes_frame.rowconfigure(4, weight=1)
        
    def create_project(self):
        name = self.project_name.get().strip()
        if not name:
            messagebox.showerror("Erreur", "Veuillez entrer un nom pour le projet")
            return
            
        project_file = os.path.join(self.data_dir, f"{name}.json")
        if os.path.exists(project_file):
            messagebox.showerror("Erreur", "Un projet avec ce nom existe déjà")
            return
            
        project_data = {
            "name": name,
            "created": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat(),
            "subjects": {}
        }
        
        with open(project_file, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, ensure_ascii=False, indent=2)
            
        self.refresh_projects_list()
        self.project_name.delete(0, tk.END)
        self.status_var.set(f"Projet '{name}' créé avec succès")
        
    def load_projects_list(self):
        projects = []
        if os.path.exists(self.data_dir):
            for file in os.listdir(self.data_dir):
                if file.endswith('.json'):
                    projects.append(file[:-5])
        return sorted(projects)
        
    def refresh_projects_list(self):
        self.projects_list.delete(0, tk.END)
        self.projects = self.load_projects_list()
        for project in self.projects:
            self.projects_list.insert(tk.END, project)
            
    def on_project_select(self, event):
        selection = self.projects_list.curselection()
        if not selection:
            return
            
        project_name = self.projects_list.get(selection[0])
        self.load_project(project_name)
        
    def load_project(self, project_name):
        project_file = os.path.join(self.data_dir, f"{project_name}.json")
        
        try:
            with open(project_file, 'r', encoding='utf-8') as f:
                self.project_data = json.load(f)
                
            self.current_project = project_name
            self.header_label.config(text=f"Projet: {project_name}")
            self.refresh_subjects_list()
            self.status_var.set(f"Projet '{project_name}' chargé")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger le projet: {str(e)}")
            
    def refresh_subjects_list(self):
        self.subjects_list.delete(0, tk.END)
        if self.current_project and "subjects" in self.project_data:
            for subject in self.project_data["subjects"]:
                self.subjects_list.insert(tk.END, subject)
                
    def add_subject(self):
        if not self.current_project:
            messagebox.showerror("Erreur", "Veuillez d'abord sélectionner ou créer un projet")
            return
            
        subject_name = self.subject_name.get().strip()
        if not subject_name:
            messagebox.showerror("Erreur", "Veuillez entrer un nom pour le sujet")
            return
            
        if subject_name in self.project_data["subjects"]:
            messagebox.showerror("Erreur", "Un sujet avec ce nom existe déjà dans ce projet")
            return
            
        # Structure de données pour un nouveau sujet
        self.project_data["subjects"][subject_name] = {
            "identity": {key: "" for key in self.identity_fields},
            "contact": {key: "" for key in self.contact_fields},
            "online": {key: "" for key in self.online_fields},
            "notes": "",
            "sources": "",
            "created": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat()
        }
        
        self.save_data()
        self.refresh_subjects_list()
        self.subject_name.delete(0, tk.END)
        self.status_var.set(f"Sujet '{subject_name}' ajouté")
        
    def on_subject_select(self, event):
        selection = self.subjects_list.curselection()
        if not selection:
            return
            
        subject_name = self.subjects_list.get(selection[0])
        self.load_subject(subject_name)
        
    def load_subject(self, subject_name):
        if not self.current_project or subject_name not in self.project_data["subjects"]:
            return
            
        self.current_subject = subject_name
        subject_data = self.project_data["subjects"][subject_name]
        
        # Charger les données d'identité
        for key, widget in self.identity_fields.items():
            if key in subject_data["identity"]:
                if isinstance(widget, tk.Text):
                    widget.delete(1.0, tk.END)
                    widget.insert(1.0, subject_data["identity"][key])
                else:
                    widget.delete(0, tk.END)
                    widget.insert(0, subject_data["identity"][key])
        
        # Charger les données de contact
        for key, widget in self.contact_fields.items():
            if key in subject_data["contact"]:
                if isinstance(widget, tk.Text):
                    widget.delete(1.0, tk.END)
                    widget.insert(1.0, subject_data["contact"][key])
                else:
                    widget.delete(0, tk.END)
                    widget.insert(0, subject_data["contact"][key])
        
        # Charger les données en ligne
        for key, widget in self.online_fields.items():
            if key in subject_data["online"]:
                if isinstance(widget, tk.Text):
                    widget.delete(1.0, tk.END)
                    widget.insert(1.0, subject_data["online"][key])
                else:
                    widget.delete(0, tk.END)
                    widget.insert(0, subject_data["online"][key])
        
        # Charger les notes et sources
        self.research_notes.delete(1.0, tk.END)
        self.research_notes.insert(1.0, subject_data.get("notes", ""))
        
        self.sources_text.delete(1.0, tk.END)
        self.sources_text.insert(1.0, subject_data.get("sources", ""))
        
        self.status_var.set(f"Sujet '{subject_name}' chargé")
        self.header_label.config(text=f"Projet: {self.current_project} | Sujet: {subject_name}")
        
    def save_data(self):
        if not self.current_project:
            messagebox.showerror("Erreur", "Aucun projet sélectionné")
            return
            
        # Sauvegarder les données du sujet actuel s'il y en a un
        if self.current_subject:
            subject_data = self.project_data["subjects"][self.current_subject]
            
            # Sauvegarder l'identité
            for key, widget in self.identity_fields.items():
                if isinstance(widget, tk.Text):
                    subject_data["identity"][key] = widget.get(1.0, tk.END).strip()
                else:
                    subject_data["identity"][key] = widget.get().strip()
            
            # Sauvegarder les contacts
            for key, widget in self.contact_fields.items():
                if isinstance(widget, tk.Text):
                    subject_data["contact"][key] = widget.get(1.0, tk.END).strip()
                else:
                    subject_data["contact"][key] = widget.get().strip()
            
            # Sauvegarder les infos en ligne
            for key, widget in self.online_fields.items():
                if isinstance(widget, tk.Text):
                    subject_data["online"][key] = widget.get(1.0, tk.END).strip()
                else:
                    subject_data["online"][key] = widget.get().strip()
            
            # Sauvegarder les notes et sources
            subject_data["notes"] = self.research_notes.get(1.0, tk.END).strip()
            subject_data["sources"] = self.sources_text.get(1.0, tk.END).strip()
            subject_data["last_modified"] = datetime.now().isoformat()
        
        # Mettre à jour la date de modification du projet
        self.project_data["last_modified"] = datetime.now().isoformat()
        
        # Sauvegarder le fichier
        project_file = os.path.join(self.data_dir, f"{self.current_project}.json")
        try:
            with open(project_file, 'w', encoding='utf-8') as f:
                json.dump(self.project_data, f, ensure_ascii=False, indent=2)
                
            self.status_var.set("Données sauvegardées avec succès")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde: {str(e)}")
            
    def delete_subject(self):
        if not self.current_project or not self.current_subject:
            messagebox.showerror("Erreur", "Veuillez sélectionner un sujet à supprimer")
            return
            
        if messagebox.askyesno("Confirmation", f"Êtes-vous sûr de vouloir supprimer le sujet '{self.current_subject}'?"):
            del self.project_data["subjects"][self.current_subject]
            self.save_data()
            self.refresh_subjects_list()
            self.current_subject = None
            self.clear_fields()
            self.header_label.config(text=f"Projet: {self.current_project}")
            self.status_var.set("Sujet supprimé")
            
    def delete_project(self):
        selection = self.projects_list.curselection()
        if not selection:
            messagebox.showerror("Erreur", "Veuillez sélectionner un projet à supprimer")
            return
            
        project_name = self.projects_list.get(selection[0])
        if messagebox.askyesno("Confirmation", f"Êtes-vous sûr de vouloir supprimer le projet '{project_name}'?"):
            project_file = os.path.join(self.data_dir, f"{project_name}.json")
            try:
                os.remove(project_file)
                self.refresh_projects_list()
                if self.current_project == project_name:
                    self.current_project = None
                    self.current_subject = None
                    self.clear_fields()
                    self.header_label.config(text="Sélectionnez un projet et un sujet")
                self.status_var.set("Projet supprimé")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la suppression: {str(e)}")
                
    def clear_fields(self):
        # Effacer tous les champs
        for widget in self.identity_fields.values():
            if isinstance(widget, tk.Text):
                widget.delete(1.0, tk.END)
            else:
                widget.delete(0, tk.END)
                
        for widget in self.contact_fields.values():
            if isinstance(widget, tk.Text):
                widget.delete(1.0, tk.END)
            else:
                widget.delete(0, tk.END)
                
        for widget in self.online_fields.values():
            if isinstance(widget, tk.Text):
                widget.delete(1.0, tk.END)
            else:
                widget.delete(0, tk.END)
                
        self.research_notes.delete(1.0, tk.END)
        self.sources_text.delete(1.0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = OSINTResearchApp(root)
    root.mainloop()