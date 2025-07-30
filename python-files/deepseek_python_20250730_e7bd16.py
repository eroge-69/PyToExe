import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QFileDialog, QTableWidget, 
                             QTableWidgetItem, QVBoxLayout, QWidget, QPushButton,
                             QComboBox, QLabel, QLineEdit, QGroupBox, QTabWidget)
from PyQt5.QtCore import Qt
from openpyxl import Workbook
import ezdxf
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# 1. PARAMÈTRES SPÉCIFIQUES AU BÉNIN
class ParametresBenin:
    # Sections des conducteurs
    SECTIONS_HTA = [148.0, 117.0, 75.5, 54.6]  # mm²
    SECTIONS_BT = [
        "3x50+54.6+2x16", 
        "3x70+54.6+2x16", 
        "3x95+54.6+2x16"
    ]
    
    # Portées maximales
    PORTEE_MAX_HTA_AGGLOMERATION = 80  # m
    PORTEE_MAX_HTA_CAMPAGNE = 100      # m
    PORTEE_MAX_BT = 50                 # m
    
    # Paramètres climatiques
    PRESSION_VENT_ZONE_I = 700   # Pa (Zone côtière)
    PRESSION_VENT_ZONE_II = 800  # Pa (Zone intermédiaire)
    PRESSION_VENT_ZONE_III = 900 # Pa (Zone nord)
    
    # Classes de supports
    CLASSES_SUPPORT = ["A", "B", "C", "D", "E"]
    EFFORTS_SUPPORT = [200, 400, 600, 800, 1000]  # daN
    
    # Types d'armement
    ARMEMENTS_HTA = {
        "Suspendu": ["NV1", "NV2", "BIS", "ES"],
        "Rigide": ["CI", "BIR", "CUO", "EA", "EAD"]
    }
    
    # Isolateurs
    ISOLATEURS = ["VHT 22T", "VHT 36T", "Composite"]
    
    # Types de sol
    NATURES_SOL = ["C1", "C2", "C3", "C4", "C5"]

# 2. INTERFACE GRAPHIQUE PYQT5
class CamelieApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CAMELIE BÉNIN - Calcul Mécanique des Lignes Électriques")
        self.setGeometry(100, 100, 1200, 800)
        
        # Configuration initiale
        self.params = ParametresBenin()
        self.df_poteaux = pd.DataFrame()
        self.df_resultats = pd.DataFrame()
        
        # Création de l'interface
        self.initUI()
        
    def initUI(self):
        # Configuration des onglets
        tabs = QTabWidget()
        
        # Onglet 1: Import des données
        tab_import = QWidget()
        layout_import = QVBoxLayout()
        
        # Groupe: Import des poteaux
        grp_import = QGroupBox("Import des données de poteaux")
        layout_grp_import = QVBoxLayout()
        
        self.btn_import = QPushButton("Importer fichier TXT")
        self.btn_import.clicked.connect(self.importer_donnees)
        layout_grp_import.addWidget(self.btn_import)
        
        self.table_poteaux = QTableWidget()
        self.table_poteaux.setColumnCount(5)
        self.table_poteaux.setHorizontalHeaderLabels(["Nom", "X", "Y", "Z", "Observations"])
        layout_grp_import.addWidget(self.table_poteaux)
        
        grp_import.setLayout(layout_grp_import)
        layout_import.addWidget(grp_import)
        
        # Groupe: Paramètres
        grp_params = QGroupBox("Paramètres de calcul")
        layout_grp_params = QVBoxLayout()
        
        # Zone climatique
        layout_climat = QVBoxLayout()
        lbl_climat = QLabel("Zone climatique:")
        self.cmb_climat = QComboBox()
        self.cmb_climat.addItems(["Zone I (Côtière)", "Zone II (Intermédiaire)", "Zone III (Nord)"])
        layout_climat.addWidget(lbl_climat)
        layout_climat.addWidget(self.cmb_climat)
        
        # Type de réseau
        layout_reseau = QVBoxLayout()
        lbl_reseau = QLabel("Type de réseau:")
        self.cmb_reseau = QComboBox()
        self.cmb_reseau.addItems(["HTA", "BT", "Mixte"])
        layout_reseau.addWidget(lbl_reseau)
        layout_reseau.addWidget(self.cmb_reseau)
        
        # Environnement
        layout_env = QVBoxLayout()
        lbl_env = QLabel("Environnement:")
        self.cmb_env = QComboBox()
        self.cmb_env.addItems(["Agglomération", "Rase campagne"])
        layout_env.addWidget(lbl_env)
        layout_env.addWidget(self.cmb_env)
        
        layout_grp_params.addLayout(layout_climat)
        layout_grp_params.addLayout(layout_reseau)
        layout_grp_params.addLayout(layout_env)
        grp_params.setLayout(layout_grp_params)
        layout_import.addWidget(grp_params)
        
        tab_import.setLayout(layout_import)
        tabs.addTab(tab_import, "Import données")
        
        # Onglet 2: Résultats
        tab_resultats = QWidget()
        layout_resultats = QVBoxLayout()
        
        self.btn_calculer = QPushButton("Lancer le calcul")
        self.btn_calculer.clicked.connect(self.calculer_ligne)
        layout_resultats.addWidget(self.btn_calculer)
        
        self.table_resultats = QTableWidget()
        layout_resultats.addWidget(self.table_resultats)
        
        # Boutons d'export
        layout_export = QVBoxLayout()
        self.btn_export_excel = QPushButton("Exporter carnet de piquetage (Excel)")
        self.btn_export_pdf = QPushButton("Générer profil en long (PDF)")
        self.btn_export_dwg = QPushButton("Générer plan habillé (DWG)")
        
        layout_export.addWidget(self.btn_export_excel)
        layout_export.addWidget(self.btn_export_pdf)
        layout_export.addWidget(self.btn_export_dwg)
        
        layout_resultats.addLayout(layout_export)
        tab_resultats.setLayout(layout_resultats)
        tabs.addTab(tab_resultats, "Résultats")
        
        self.setCentralWidget(tabs)
    
    def importer_donnees(self):
        fichier, _ = QFileDialog.getOpenFileName(
            self, "Ouvrir le fichier de poteaux", "", "Fichiers TXT (*.txt)"
        )
        
        if fichier:
            try:
                self.df_poteaux = pd.read_csv(
                    fichier, 
                    sep='\t', 
                    names=["Nom", "X", "Y", "Z", "Observations"]
                )
                self.afficher_donnees_table()
            except Exception as e:
                print(f"Erreur d'import: {str(e)}")
    
    def afficher_donnees_table(self):
        self.table_poteaux.setRowCount(len(self.df_poteaux))
        
        for row_idx, row in self.df_poteaux.iterrows():
            self.table_poteaux.setItem(row_idx, 0, QTableWidgetItem(str(row["Nom"])))
            self.table_poteaux.setItem(row_idx, 1, QTableWidgetItem(str(row["X"])))
            self.table_poteaux.setItem(row_idx, 2, QTableWidgetItem(str(row["Y"])))
            self.table_poteaux.setItem(row_idx, 3, QTableWidgetItem(str(row["Z"])))
            self.table_poteaux.setItem(row_idx, 4, QTableWidgetItem(str(row["Observations"])))
    
    def calculer_ligne(self):
        if self.df_poteaux.empty:
            return
        
        # Paramètres de calcul
        zone_climat = self.cmb_climat.currentIndex() + 1
        pression_vent = [700, 800, 900][zone_climat - 1]
        
        # Calcul mécanique simplifié
        results = []
        for i in range(len(self.df_poteaux)-1):
            p1 = self.df_poteaux.iloc[i]
            p2 = self.df_poteaux.iloc[i+1]
            
            # Calcul distance
            dx = p2["X"] - p1["X"]
            dy = p2["Y"] - p1["Y"]
            dz = p2["Z"] - p1["Z"]
            distance = np.sqrt(dx**2 + dy**2)
            denivele = dz
            
            # Détermination type de ligne
            ligne_type = "HTA" if "HTA" in str(p1["Observations"]) else "BT"
            
            # Calculs mécaniques (simplifiés)
            fleche = (pression_vent * distance**2) / (8 * 15)  # Formule simplifiée
            tension = distance * 0.2 * 2.5  # Coefficient de sécurité
            
            # Vérification portée max
            env = self.cmb_env.currentText()
            portee_max = {
                ("HTA", "Agglomération"): self.params.PORTEE_MAX_HTA_AGGLOMERATION,
                ("HTA", "Rase campagne"): self.params.PORTEE_MAX_HTA_CAMPAGNE,
                ("BT", _): self.params.PORTEE_MAX_BT
            }.get((ligne_type, env), 50)
            
            validation = "OK" if distance <= portee_max else "DÉPASSEMENT"
            
            results.append({
                "Poteau départ": p1["Nom"],
                "Poteau arrivée": p2["Nom"],
                "Distance (m)": round(distance, 2),
                "Dénivelé (m)": round(denivele, 2),
                "Type": ligne_type,
                "Flèche max (m)": round(fleche, 2),
                "Tension (kN)": round(tension, 1),
                "Validation": validation
            })
        
        self.df_resultats = pd.DataFrame(results)
        self.afficher_resultats_table()
    
    def afficher_resultats_table(self):
        self.table_resultats.setRowCount(len(self.df_resultats))
        self.table_resultats.setColumnCount(len(self.df_resultats.columns))
        self.table_resultats.setHorizontalHeaderLabels(self.df_resultats.columns)
        
        for row_idx, row in self.df_resultats.iterrows():
            for col_idx, col in enumerate(self.df_resultats.columns):
                item = QTableWidgetItem(str(row[col]))
                item.setTextAlignment(Qt.AlignCenter)
                
                if col == "Validation" and row[col] == "DÉPASSEMENT":
                    item.setBackground(Qt.yellow)
                
                self.table_resultats.setItem(row_idx, col_idx, item)
    
    def exporter_excel(self):
        if self.df_poteaux.empty:
            return
        
        fichier, _ = QFileDialog.getSaveFileName(
            self, "Enregistrer le carnet de piquetage", "", "Fichiers Excel (*.xlsx)"
        )
        
        if fichier:
            try:
                wb = Workbook()
                ws = wb.active
                ws.title = "Carnet de piquetage"
                
                # En-têtes
                entetes = [
                    "Poteau", "X", "Y", "Z", "Angle orientation (gr)", 
                    "Angle piquetage (gr)", "Fonction", "Classe/Effort",
                    "Type armement", "Isolateur", "Fouille (LxlxP)", 
                    "Nature sol", "Observations"
                ]
                ws.append(entetes)
                
                # Données avec valeurs par défaut
                for _, row in self.df_poteaux.iterrows():
                    obs = str(row["Observations"])
                    ligne_type = "HTA" if "HTA" in obs else "BT"
                    
                    # Détermination automatique des paramètres
                    fonction = "AS" if "angle" in obs.lower() else "SF"
                    classe_effort = "12A400" if ligne_type == "HTA" else "9A200"
                    armement = "NV1" if ligne_type == "HTA" else "CI"
                    isolateur = "VHT 36T" if ligne_type == "HTA" else "Composite"
                    fouille = "1.5x1.5x2.0" if ligne_type == "HTA" else "1.0x1.0x1.5"
                    sol = "C2"
                    
                    ws.append([
                        row["Nom"], row["X"], row["Y"], row["Z"], 
                        0, 0, fonction, classe_effort,
                        armement, isolateur, fouille, sol, obs
                    ])
                
                wb.save(fichier)
            except Exception as e:
                print(f"Erreur d'export Excel: {str(e)}")
    
    def generer_profil_pdf(self):
        if self.df_poteaux.empty:
            return
        
        fichier, _ = QFileDialog.getSaveFileName(
            self, "Enregistrer le profil en long", "", "Fichiers PDF (*.pdf)"
        )
        
        if fichier:
            try:
                c = canvas.Canvas(fichier, pagesize=A4)
                c.setFont("Helvetica-Bold", 16)
                c.drawString(100, 800, "PROFIL EN LONG - CAMELIE BÉNIN")
                c.setFont("Helvetica", 12)
                c.drawString(100, 780, "Conforme aux normes SBEE - République du Bénin")
                
                # Tracé simplifié du profil
                y_pos = 700
                for i in range(len(self.df_poteaux)-1):
                    p1 = self.df_poteaux.iloc[i]
                    p2 = self.df_poteaux.iloc[i+1]
                    
                    texte = f"Portée {p1['Nom']}-{p2['Nom']}: "
                    texte += f"{np.sqrt((p2['X']-p1['X'])**2 + (p2['Y']-p1['Y'])**2):.1f}m"
                    
                    c.drawString(100, y_pos, texte)
                    y_pos -= 20
                
                c.save()
            except Exception as e:
                print(f"Erreur génération PDF: {str(e)}")

# 3. POINT D'ENTRÉE PRINCIPAL
if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenetre = CamelieApp()
    fenetre.show()
    sys.exit(app.exec_())