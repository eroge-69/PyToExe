import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime
import os
import sys

class PcVueConverter:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Convertisseur PcVue XML vers Excel")
        self.root.geometry("500x300")
        self.root.resizable(False, False)
        
        # Variables
        self.xml_file_path = tk.StringVar()
        self.progress_var = tk.DoubleVar()
        
        self.setup_ui()
        
    def setup_ui(self):
        # Titre
        title_label = tk.Label(self.root, text="Convertisseur PcVue XML → Excel", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=20)
        
        # Zone de sélection de fichier
        file_frame = tk.Frame(self.root)
        file_frame.pack(pady=10, padx=20, fill="x")
        
        tk.Label(file_frame, text="Fichier XML d'export PcVue:", font=("Arial", 10)).pack(anchor="w")
        
        path_frame = tk.Frame(file_frame)
        path_frame.pack(fill="x", pady=5)
        
        self.path_entry = tk.Entry(path_frame, textvariable=self.xml_file_path, 
                                  state="readonly", font=("Arial", 9))
        self.path_entry.pack(side="left", fill="x", expand=True)
        
        browse_btn = tk.Button(path_frame, text="Parcourir", command=self.browse_file,
                              bg="#4CAF50", fg="white", font=("Arial", 9))
        browse_btn.pack(side="right", padx=(5, 0))
        
        # Barre de progression
        self.progress_frame = tk.Frame(self.root)
        self.progress_frame.pack(pady=20, padx=20, fill="x")
        
        tk.Label(self.progress_frame, text="Progression:", font=("Arial", 10)).pack(anchor="w")
        self.progress_bar = ttk.Progressbar(self.progress_frame, variable=self.progress_var, 
                                           maximum=100, length=400)
        self.progress_bar.pack(pady=5)
        
        # Bouton de conversion
        convert_btn = tk.Button(self.root, text="Convertir en Excel", 
                               command=self.convert_file, font=("Arial", 12, "bold"),
                               bg="#2196F3", fg="white", height=2, width=20)
        convert_btn.pack(pady=20)
        
        # Zone d'informations
        self.info_text = tk.Text(self.root, height=6, width=60, font=("Arial", 9))
        self.info_text.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Scrollbar pour le texte
        scrollbar = tk.Scrollbar(self.info_text)
        scrollbar.pack(side="right", fill="y")
        self.info_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.info_text.yview)
        
        self.log("Application prête. Sélectionnez un fichier XML PcVue.")
    
    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Sélectionner le fichier XML PcVue",
            filetypes=[("Fichiers XML", "*.xml"), ("Tous les fichiers", "*.*")]
        )
        if file_path:
            self.xml_file_path.set(file_path)
            self.log(f"Fichier sélectionné: {os.path.basename(file_path)}")
    
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.info_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.info_text.see(tk.END)
        self.root.update()
    
    def parse_xml_alarms(self, xml_file):
        """Parse le XML et extrait les alarmes"""
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            alarms_data = []
            site_info = {}
            
            # Recherche des informations du site
            for obj_instance in root.findall(".//ObjectInstance"):
                params = obj_instance.find("ParametersList")
                if params is not None:
                    param_dict = {}
                    for param in params.findall("ParameterInstance"):
                        name = param.get("Name")
                        value_elem = param.find("Value")
                        if value_elem is not None:
                            param_dict[name] = value_elem.text
                    
                    # Si c'est les infos du site
                    if "Autoroute" in param_dict:
                        site_info = param_dict
            
            # Recherche des alarmes (ObjectInstanceType=1)
            for obj_instance in root.findall(".//ObjectInstance[@ObjectInstanceType='1']"):
                obj_name = obj_instance.get("Name")
                
                # Extraction du chemin hiérarchique
                path_parts = []
                current = obj_instance
                while current is not None:
                    parent = current.getparent()
                    if parent is not None and parent.tag == "TemplateInstance":
                        branch = parent.find("Branch")
                        if branch is not None and branch.text:
                            path_parts.insert(0, branch.text)
                    current = parent.getparent() if parent is not None else None
                
                hierarchy_path = " > ".join(path_parts[1:]) if len(path_parts) > 1 else ""
                
                # Extraction des paramètres de l'alarme
                params = obj_instance.find("ParametersList")
                if params is not None:
                    alarm_data = {
                        "Nom_Alarme": obj_name,
                        "Chemin_Hierarchique": hierarchy_path,
                        "Site": site_info.get("Trigramme", ""),
                        "Autoroute": site_info.get("Autoroute", ""),
                        "Description_Site": site_info.get("Description_Site", ""),
                        "District": site_info.get("District", ""),
                        "PR": site_info.get("PR", ""),
                        "Sens": site_info.get("Sens", "")
                    }
                    
                    # Extraction des paramètres spécifiques à l'alarme
                    for param in params.findall("ParameterInstance"):
                        param_name = param.get("Name")
                        value_elem = param.find("Value")
                        is_overwritten = param.find("IsOverwritten")
                        
                        if value_elem is not None:
                            alarm_data[param_name] = value_elem.text
                            
                        # Marquer si la valeur est surchargée
                        if is_overwritten is not None:
                            alarm_data[f"{param_name}_Modifie"] = "Oui"
                    
                    alarms_data.append(alarm_data)
            
            return alarms_data, site_info
            
        except Exception as e:
            raise Exception(f"Erreur lors du parsing XML: {str(e)}")
    
    def create_excel_report(self, alarms_data, site_info, output_file):
        """Crée le rapport Excel"""
        try:
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                
                # Onglet Résumé
                self.progress_var.set(20)
                self.log("Création de l'onglet Résumé...")
                
                if alarms_data:
                    # Statistiques générales
                    total_alarms = len(alarms_data)
                    active_alarms = sum(1 for alarm in alarms_data 
                                      if alarm.get("Activation_Alarme") == "1")
                    priorities = {}
                    for alarm in alarms_data:
                        prio = alarm.get("Priorite", "Non définie")
                        priorities[prio] = priorities.get(prio, 0) + 1
                    
                    resume_data = [
                        ["Information", "Valeur"],
                        ["Site", site_info.get("Trigramme", "")],
                        ["Autoroute", site_info.get("Autoroute", "")],
                        ["Description", site_info.get("Description_Site", "")],
                        ["District", site_info.get("District", "")],
                        ["PR", site_info.get("PR", "")],
                        ["Sens", site_info.get("Sens", "")],
                        ["", ""],
                        ["Total alarmes", total_alarms],
                        ["Alarmes actives", active_alarms],
                        ["Alarmes inactives", total_alarms - active_alarms],
                        ["", ""],
                        ["Répartition par priorité", ""]
                    ]
                    
                    for prio, count in priorities.items():
                        resume_data.append([f"  {prio}", count])
                    
                    resume_df = pd.DataFrame(resume_data)
                    resume_df.to_excel(writer, sheet_name="Résumé", index=False, header=False)
                
                # Onglet Alarmes détaillées
                self.progress_var.set(50)
                self.log("Création de l'onglet Alarmes...")
                
                if alarms_data:
                    alarms_df = pd.DataFrame(alarms_data)
                    
                    # Réorganiser les colonnes pour une meilleure lisibilité
                    priority_cols = ["Nom_Alarme", "Description", "Priorite", "Activation_Alarme", 
                                   "API", "Bit", "Temporisation", "Utilisateur"]
                    context_cols = ["Chemin_Hierarchique", "Site", "Autoroute", "District"]
                    
                    ordered_cols = []
                    for col in priority_cols + context_cols:
                        if col in alarms_df.columns:
                            ordered_cols.append(col)
                    
                    # Ajouter les autres colonnes
                    for col in alarms_df.columns:
                        if col not in ordered_cols:
                            ordered_cols.append(col)
                    
                    alarms_df = alarms_df[ordered_cols]
                    alarms_df.to_excel(writer, sheet_name="Alarmes", index=False)
                
                # Onglet Paramètres techniques
                self.progress_var.set(80)
                self.log("Création de l'onglet Paramètres techniques...")
                
                if alarms_data:
                    tech_data = []
                    for alarm in alarms_data:
                        tech_data.append({
                            "Alarme": alarm.get("Nom_Alarme", ""),
                            "API": alarm.get("API", ""),
                            "Bit": alarm.get("Bit", ""),
                            "Temporisation": alarm.get("Temporisation", ""),
                            "Bit_Modifie": alarm.get("Bit_Modifie", "Non"),
                            "Activation": "Activée" if alarm.get("Activation_Alarme") == "1" else "Désactivée"
                        })
                    
                    tech_df = pd.DataFrame(tech_data)
                    tech_df.to_excel(writer, sheet_name="Paramètres techniques", index=False)
                
                self.progress_var.set(100)
                self.log(f"Fichier Excel créé: {os.path.basename(output_file)}")
                
        except Exception as e:
            raise Exception(f"Erreur lors de la création Excel: {str(e)}")
    
    def convert_file(self):
        if not self.xml_file_path.get():
            messagebox.showerror("Erreur", "Veuillez sélectionner un fichier XML")
            return
        
        try:
            self.progress_var.set(0)
            self.log("Début de la conversion...")
            
            # Parse du fichier XML
            self.progress_var.set(10)
            self.log("Analyse du fichier XML...")
            alarms_data, site_info = self.parse_xml_alarms(self.xml_file_path.get())
            
            if not alarms_data:
                self.log("Aucune alarme trouvée dans le fichier XML")
                messagebox.showwarning("Attention", "Aucune alarme trouvée dans le fichier XML")
                return
            
            self.log(f"Trouvé {len(alarms_data)} alarme(s)")
            
            # Génération du nom de fichier de sortie
            input_file = self.xml_file_path.get()
            output_dir = os.path.dirname(input_file)
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(output_dir, f"{base_name}_Alarmes_{timestamp}.xlsx")
            
            # Création du fichier Excel
            self.create_excel_report(alarms_data, site_info, output_file)
            
            self.log("Conversion terminée avec succès!")
            
            # Proposer d'ouvrir le fichier
            result = messagebox.askyesno("Conversion terminée", 
                                       f"Fichier créé avec succès!\n\n{output_file}\n\nVoulez-vous l'ouvrir?")
            if result:
                os.startfile(output_file)
                
        except Exception as e:
            self.log(f"ERREUR: {str(e)}")
            messagebox.showerror("Erreur de conversion", str(e))
        finally:
            self.progress_var.set(0)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    try:
        app = PcVueConverter()
        app.run()
    except Exception as e:
        messagebox.showerror("Erreur fatale", f"Impossible de démarrer l'application:\n{str(e)}")
        sys.exit(1)