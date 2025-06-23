#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trieur de Documents par Client et Société
Interface graphique pour classer automatiquement les documents selon le format:
NOM SOC AAAA-MM-DD Objet

Exemple: HASSID Rachel ASE 25-04-23 Fact NOV24.pdf
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import re
import shutil
from datetime import datetime
from pathlib import Path

class DocumentSorter:
    def __init__(self):
        self.source_folder = "C:/path/to/documents"
        self.destination_base = "S:/Commercial"
        
        # Configuration des sociétés
        self.societe_config = {
            "ASE": {
                "path": "ASE (75-93-94)/1 Clients",
                "name": "ASE"
            },
            "ADS": {
                "path": "ADS/1 Clients", 
                "name": "ADS"
            },
            "ASP": {
                "path": "ASP/1 Clients",
                "name": "ASP"
            },
            "ALT": {
                "path": "ALT/1 Clients",
                "name": "ALT"
            }
        }
        
        # Extensions supportées
        self.supported_extensions = {
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', 
            '.ppt', '.pptx', '.png', '.jpg', '.jpeg', 
            '.txt', '.zip', '.rar'
        }
        
        self.current_processed_data = {}
        self.setup_gui()
        
    def setup_gui(self):
        """Création de l'interface graphique"""
        self.root = tk.Tk()
        self.root.title("Trieur de Documents par Client et Société")
        self.root.geometry("1000x750")
        self.root.resizable(True, True)
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configuration des poids pour redimensionnement
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # === SECTION CONFIGURATION ===
        config_frame = ttk.LabelFrame(main_frame, text="Configuration", padding="10")
        config_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        config_frame.columnconfigure(1, weight=1)
        
        # Dossier source
        ttk.Label(config_frame, text="Dossier source:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.source_var = tk.StringVar(value=self.source_folder)
        self.source_entry = ttk.Entry(config_frame, textvariable=self.source_var, width=60)
        self.source_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(config_frame, text="...", command=self.browse_source).grid(row=0, column=2)
        
        # Dossier destination
        ttk.Label(config_frame, text="Dossier Commercial:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.dest_var = tk.StringVar(value=self.destination_base)
        self.dest_entry = ttk.Entry(config_frame, textvariable=self.dest_var, width=60)
        self.dest_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 5), pady=(5, 0))
        ttk.Button(config_frame, text="...", command=self.browse_destination).grid(row=1, column=2, pady=(5, 0))
        
        # Format info
        format_text = "Format: NOM SOC AAAA-MM-DD Objet (ex: HASSID Rachel ASE 25-04-23 Fact NOV24)"
        ttk.Label(config_frame, text=format_text, foreground="blue").grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))
        
        extensions_text = f"Extensions: {', '.join(sorted(self.supported_extensions))}"
        ttk.Label(config_frame, text=extensions_text, foreground="darkgreen").grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=(2, 0))
        
        # Bouton analyser
        self.analyze_btn = ttk.Button(config_frame, text="ANALYSER LES DOCUMENTS", command=self.analyze_documents)
        self.analyze_btn.grid(row=0, column=3, rowspan=2, padx=(10, 0), sticky=(tk.N, tk.S))
        
        # === SECTION APERÇU ===
        preview_frame = ttk.Frame(main_frame)
        preview_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.columnconfigure(1, weight=1)
        preview_frame.rowconfigure(1, weight=1)
        
        # Documents valides
        ttk.Label(preview_frame, text="Documents à classer:").grid(row=0, column=0, sticky=tk.W)
        self.preview_listbox = tk.Listbox(preview_frame, height=8)
        self.preview_listbox.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        preview_scroll = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.preview_listbox.yview)
        preview_scroll.grid(row=1, column=0, sticky=(tk.E, tk.N, tk.S))
        self.preview_listbox.configure(yscrollcommand=preview_scroll.set)
        
        # Documents en erreur
        ttk.Label(preview_frame, text="Documents non conformes:").grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        self.errors_listbox = tk.Listbox(preview_frame, height=8, foreground="red")
        self.errors_listbox.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        
        errors_scroll = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.errors_listbox.yview)
        errors_scroll.grid(row=1, column=1, sticky=(tk.E, tk.N, tk.S))
        self.errors_listbox.configure(yscrollcommand=errors_scroll.set)
        
        # Bouton traitement
        self.process_btn = ttk.Button(preview_frame, text="CLASSER LES DOCUMENTS", command=self.process_documents, state=tk.DISABLED)
        self.process_btn.grid(row=2, column=0, columnspan=2, pady=(10, 0))
        
        # === SECTION LOG ===
        log_frame = ttk.LabelFrame(main_frame, text="Journal des opérations", padding="5")
        log_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, wrap=tk.WORD, font=('Consolas', 9))
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configuration du redimensionnement
        main_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Message initial
        self.log("Interface prête. Configurez les chemins et cliquez sur 'Analyser les documents'.")
        self.log("Format attendu: NOM SOC AAAA-MM-DD Objet")
        self.log("Sociétés configurées: ASE, ADS, ASP, ALT")
    
    def log(self, message):
        """Ajouter un message au log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def browse_source(self):
        """Parcourir pour sélectionner le dossier source"""
        folder = filedialog.askdirectory(title="Sélectionnez le dossier source")
        if folder:
            self.source_var.set(folder)
            self.source_folder = folder
    
    def browse_destination(self):
        """Parcourir pour sélectionner le dossier de destination"""
        folder = filedialog.askdirectory(title="Sélectionnez le dossier Commercial de base")
        if folder:
            self.dest_var.set(folder)
            self.destination_base = folder
    
    def parse_document_name(self, filename):
        """Analyser le nom d'un fichier selon le format attendu"""
        base_name = Path(filename).stem
        
        # Pattern: NOM SOC AAAA-MM-DD Objet
        pattern = r'^(.+?)\s+(ASE|ADS|ASP|ALT)\s+(\d{2}-\d{2}-\d{2})\s+(.+)$'
        match = re.match(pattern, base_name)
        
        if match:
            return {
                'success': True,
                'client_name': match.group(1).strip(),
                'societe': match.group(2).strip(),
                'date': match.group(3).strip(),
                'objet': match.group(4).strip(),
                'full_name': base_name
            }
        
        return {
            'success': False,
            'client_name': '',
            'societe': '',
            'date': '',
            'objet': '',
            'full_name': base_name,
            'error': 'Format non reconnu'
        }
    
    def find_client_folder(self, base_path, client_name):
        """Trouver le dossier client existant"""
        if not os.path.exists(base_path):
            return None
        
        client_words = client_name.upper().split()
        
        # Recherche exacte ou partielle
        for folder in os.listdir(base_path):
            folder_path = os.path.join(base_path, folder)
            if os.path.isdir(folder_path):
                folder_upper = folder.upper()
                
                # Vérifier si tous les mots significatifs sont présents
                all_words_found = True
                for word in client_words:
                    if len(word) > 2 and word not in folder_upper:
                        all_words_found = False
                        break
                
                if all_words_found:
                    return folder
                
                # Recherche plus souple
                for word in client_words:
                    if len(word) > 3 and word in folder_upper:
                        return folder
        
        return None
    
    def create_client_folder_name(self, client_name):
        """Créer un nom de dossier client valide"""
        # Nettoyer les caractères interdits
        invalid_chars = '<>:"/\\|?*'
        clean_name = client_name
        for char in invalid_chars:
            clean_name = clean_name.replace(char, '_')
        return clean_name
    
    def get_documents_to_process(self):
        """Analyser tous les documents du dossier source"""
        if not os.path.exists(self.source_folder):
            return {'grouped_documents': {}, 'error_documents': []}
        
        all_files = [f for f in os.listdir(self.source_folder) 
                    if os.path.isfile(os.path.join(self.source_folder, f))]
        
        # Filtrer par extensions supportées
        documents = [f for f in all_files 
                    if Path(f).suffix.lower() in self.supported_extensions]
        
        self.log(f"Fichiers trouvés: {len(all_files)}, Documents supportés: {len(documents)}")
        
        grouped_documents = {}
        error_documents = []
        
        for doc in documents:
            parsed = self.parse_document_name(doc)
            
            if parsed['success']:
                if parsed['societe'] in self.societe_config:
                    group_key = f"{parsed['client_name']}|{parsed['societe']}"
                    
                    if group_key not in grouped_documents:
                        grouped_documents[group_key] = {
                            'client_name': parsed['client_name'],
                            'societe': parsed['societe'],
                            'documents': []
                        }
                    
                    grouped_documents[group_key]['documents'].append({
                        'file': doc,
                        'parsed_info': parsed
                    })
                else:
                    error_documents.append({
                        'file': doc,
                        'error': f"Société '{parsed['societe']}' non configurée"
                    })
            else:
                error_documents.append({
                    'file': doc,
                    'error': parsed['error']
                })
        
        return {
            'grouped_documents': grouped_documents,
            'error_documents': error_documents
        }
    
    def analyze_documents(self):
        """Analyser les documents du dossier source"""
        self.analyze_btn.configure(state=tk.DISABLED, text="ANALYSE...")
        self.root.update()
        
        try:
            self.source_folder = self.source_var.get()
            self.destination_base = self.dest_var.get()
            
            # Vérifications
            if not os.path.exists(self.source_folder):
                messagebox.showerror("Erreur", f"Le dossier source n'existe pas:\n{self.source_folder}")
                return
            
            if not os.path.exists(self.destination_base):
                messagebox.showerror("Erreur", f"Le dossier de destination n'existe pas:\n{self.destination_base}")
                return
            
            self.log("=== DÉBUT DE L'ANALYSE ===")
            self.log(f"Source: {self.source_folder}")
            self.log(f"Destination: {self.destination_base}")
            
            # Analyser
            self.current_processed_data = self.get_documents_to_process()
            
            # Vider les listes
            self.preview_listbox.delete(0, tk.END)
            self.errors_listbox.delete(0, tk.END)
            
            # Remplir la liste des documents valides
            grouped = self.current_processed_data['grouped_documents']
            errors = self.current_processed_data['error_documents']
            
            for group_key, group in grouped.items():
                client_name = group['client_name']
                societe = group['societe']
                count = len(group['documents'])
                self.preview_listbox.insert(tk.END, f"{client_name} [{societe}] ({count} documents)")
            
            # Remplir la liste des erreurs
            for error_doc in errors:
                self.errors_listbox.insert(tk.END, f"{error_doc['file']} - {error_doc['error']}")
            
            self.log(f"Groupes valides: {len(grouped)}")
            self.log(f"Documents en erreur: {len(errors)}")
            
            # Activer le bouton de traitement si nécessaire
            self.process_btn.configure(state=tk.NORMAL if len(grouped) > 0 else tk.DISABLED)
            
        except Exception as e:
            self.log(f"ERREUR lors de l'analyse: {str(e)}")
            messagebox.showerror("Erreur", f"Erreur lors de l'analyse:\n{str(e)}")
        
        finally:
            self.analyze_btn.configure(state=tk.NORMAL, text="ANALYSER LES DOCUMENTS")
    
    def process_documents(self):
        """Traiter et classer les documents"""
        if not self.current_processed_data.get('grouped_documents'):
            messagebox.showwarning("Attention", "Aucun document à traiter. Analysez d'abord les documents.")
            return
        
        # Confirmation
        result = messagebox.askyesno(
            "Confirmation",
            "Êtes-vous sûr de vouloir classer tous ces documents ?\nCette action ne peut pas être annulée."
        )
        
        if not result:
            self.log("Classement annulé par l'utilisateur.")
            return
        
        self.process_btn.configure(state=tk.DISABLED, text="CLASSEMENT EN COURS...")
        self.root.update()
        
        try:
            self.log("=== DÉBUT DU CLASSEMENT ===")
            moved_count = 0
            error_count = 0
            
            grouped = self.current_processed_data['grouped_documents']
            
            for group_key, group in grouped.items():
                client_name = group['client_name']
                societe = group['societe']
                documents = group['documents']
                
                self.log(f"Traitement: {client_name} [{societe}] ({len(documents)} documents)")
                
                # Construire le chemin de base
                societe_config = self.societe_config[societe]
                base_path = os.path.join(self.destination_base, societe_config['path'])
                
                if not os.path.exists(base_path):
                    self.log(f"  [ERREUR] Dossier société inexistant: {base_path}")
                    error_count += len(documents)
                    continue
                
                # Trouver ou créer le dossier client
                client_folder = self.find_client_folder(base_path, client_name)
                if not client_folder:
                    client_folder = self.create_client_folder_name(client_name)
                    self.log(f"  Nouveau dossier client: {client_folder}")
                else:
                    self.log(f"  Dossier client trouvé: {client_folder}")
                
                client_path = os.path.join(base_path, client_folder)
                
                # Créer le dossier si nécessaire
                if not os.path.exists(client_path):
                    try:
                        os.makedirs(client_path, exist_ok=True)
                        self.log(f"  Dossier créé: {client_path}")
                    except Exception as e:
                        self.log(f"  [ERREUR] Création dossier: {str(e)}")
                        error_count += len(documents)
                        continue
                
                # Déplacer chaque document
                for doc_info in documents:
                    doc_name = doc_info['file']
                    source_path = os.path.join(self.source_folder, doc_name)
                    dest_path = os.path.join(client_path, doc_name)
                    
                    try:
                        # Gérer les conflits de noms
                        if os.path.exists(dest_path):
                            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                            name_part = Path(doc_name).stem
                            ext_part = Path(doc_name).suffix
                            new_name = f"{name_part}_{timestamp}{ext_part}"
                            dest_path = os.path.join(client_path, new_name)
                            self.log(f"  Conflit résolu: {new_name}")
                        
                        shutil.move(source_path, dest_path)
                        self.log(f"  [OK] {doc_name}")
                        moved_count += 1
                        
                    except Exception as e:
                        self.log(f"  [ERREUR] {doc_name} - {str(e)}")
                        error_count += 1
                
                self.log("")
            
            # Résumé
            self.log("=== RÉSUMÉ ===")
            self.log(f"Documents déplacés: {moved_count}")
            self.log(f"Erreurs: {error_count}")
            self.log(f"Total traité: {moved_count + error_count}")
            
            # Réanalyser
            self.analyze_documents()
            
        except Exception as e:
            self.log(f"ERREUR CRITIQUE: {str(e)}")
            messagebox.showerror("Erreur", f"Erreur critique:\n{str(e)}")
        
        finally:
            self.process_btn.configure(state=tk.NORMAL, text="CLASSER LES DOCUMENTS")
    
    def run(self):
        """Lancer l'application"""
        self.root.mainloop()

# Point d'entrée
if __name__ == "__main__":
    app = DocumentSorter()
    app.run()