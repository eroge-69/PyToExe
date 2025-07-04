import pandas as pd
import os
from typing import List, Optional
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog, QTextEdit, QLineEdit, QLabel
from PyQt5.QtCore import Qt
import sys

def find_header_row(df: pd.DataFrame) -> int:
    """Trouve la ligne contenant les en-têtes de colonnes"""
    keywords = ['art', 'désignation', 'designation', 'unité', 'unite', 'qté', 'qte']
    
    for idx, row in df.iterrows():
        if idx > 10:  # Ne pas chercher trop loin
            break
        
        row_values = [str(val).lower().strip() for val in row.values if pd.notna(val)]
        matches = sum(1 for keyword in keywords if any(keyword in val for val in row_values))
        
        if matches >= 2:
            return idx
    
    return 0

def clean_column_names(columns: List[str]) -> List[str]:
    """Nettoie les noms de colonnes"""
    cleaned = []
    for col in columns:
        if pd.notna(col) and str(col).strip():
            clean_col = (str(col)
                        .strip()
                        .lower()
                        .replace('"', '')
                        .replace('.', '')
                        .replace('é', 'e')
                        .replace('è', 'e')
                        .replace('à', 'a')
                        .replace('ç', 'c')
                        .replace('apacite', 'apacité')  # Correction pour apacité
                        .replace(' ', '_'))
            cleaned.append(clean_col)
        else:
            cleaned.append(f'col_{len(cleaned)}')
    
    return cleaned

def escape_sql_string(value) -> str:
    """Échappe les caractères spéciaux pour SQL"""
    if pd.isna(value) or value == '' or str(value).strip() == '':
        return 'NULL'
    return f"'{str(value).replace(chr(39), chr(39) + chr(39))}'"

def is_section_header(article_value) -> bool:
    """Détermine si une ligne est un en-tête de section"""
    if pd.isna(article_value):
        return False
    
    article_clean = str(article_value).strip()
    return (len(article_clean) >= 2 and 
            article_clean[1] == '.' and 
            article_clean[0].isalpha())

def is_article_item(article_value) -> bool:
    """Détermine si une ligne est un article"""
    if pd.isna(article_value):
        return False
    
    article_clean = str(article_value).strip()
    return '.' in article_clean and any(c.isdigit() for c in article_clean)

def generate_sql_queries(df: pd.DataFrame, arret_id: int = 1) -> List[str]:
    """Génère les requêtes SQL à partir du DataFrame"""
    current_section = ""
    sql_queries = []
    
    column_mapping = {
        'no_art': 'article',
        'noart': 'article',
        'article': 'article',
        'col_0': 'article',
        'designation': 'designation',
        'col_1': 'designation',
        'unite': 'unite',
        'col_2': 'unite',
        'qte': 'quantite',
        'quantite': 'quantite',
        'col_3': 'quantite'
    }
    
    article_col = None
    designation_col = None
    unite_col = None
    quantite_col = None
    
    for col in df.columns:
        if col in column_mapping:
            if column_mapping[col] == 'article' and article_col is None:
                article_col = col
            elif column_mapping[col] == 'designation' and designation_col is None:
                designation_col = col
            elif column_mapping[col] == 'unite' and unite_col is None:
                unite_col = col
            elif column_mapping[col] == 'quantite' and quantite_col is None:
                quantite_col = col
    
    if article_col is None or designation_col is None:
        cols = df.columns.tolist()
        article_col = cols[0] if len(cols) > 0 else None
        designation_col = cols[1] if len(cols) > 1 else None
        unite_col = cols[2] if len(cols) > 2 else None
        quantite_col = cols[3] if len(cols) > 3 else None
    
    for index, row in df.iterrows():
        article_value = row.get(article_col)
        
        if pd.isna(article_value) and pd.isna(row.get(designation_col)):
            continue
        
        if is_section_header(article_value):
            current_section = str(row.get(designation_col, '')).strip()
            continue
        
        if is_article_item(article_value):
            article = str(article_value).strip()
            designation = str(row.get(designation_col, '')).strip()
            unite = str(row.get(unite_col, '')).strip() if unite_col else ''
            quantite = row.get(quantite_col, 0) if quantite_col else 0
            
            if not designation or designation == 'nan':
                continue
            
            try:
                quantite = float(quantite) if pd.notna(quantite) and quantite != '' else 0
            except (ValueError, TypeError):
                quantite = 0
            
            sql_query = f"""INSERT INTO articles_arret_tech 
(arret_id, section, article, designation, unite, quantite)
VALUES 
({arret_id}, {escape_sql_string(current_section)}, {escape_sql_string(article)}, {escape_sql_string(designation)}, {escape_sql_string(unite)}, {quantite});"""
            
            sql_queries.append(sql_query)
    
    return sql_queries

class ExcelToSQLConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Excel to SQL Converter")
        self.setGeometry(100, 100, 600, 400)
        
        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        
        # Excel file selection
        self.excel_label = QLabel("Fichier Excel sélectionné : Aucun")
        self.layout.addWidget(self.excel_label)
        
        self.select_button = QPushButton("Choisir fichier Excel")
        self.select_button.clicked.connect(self.select_excel_file)
        self.layout.addWidget(self.select_button)
        
        # Arret ID input
        self.arret_id_label = QLabel("Arret ID :")
        self.layout.addWidget(self.arret_id_label)
        self.arret_id_input = QLineEdit("1")
        self.arret_id_input.setPlaceholderText("Entrez l'ID de l'arrêt (par défaut: 1)")
        self.layout.addWidget(self.arret_id_input)
        
        # Convert button
        self.convert_button = QPushButton("Convertir en SQL")
        self.convert_button.clicked.connect(self.convert_to_sql)
        self.layout.addWidget(self.convert_button)
        
        # Log output
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.layout.addWidget(self.log_text)
        
        self.excel_file = None
    
    def log_message(self, message):
        """Ajoute un message au journal avec timestamp"""
        timestamp = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        self.log_text.append(f"[{timestamp}] {message}")
    
    def select_excel_file(self):
        """Ouvre une boîte de dialogue pour sélectionner un fichier Excel"""
        file_name, _ = QFileDialog.getOpenFileName(self, "Sélectionner un fichier Excel", "", "Fichiers Excel (*.xlsx *.xls)")
        if file_name:
            self.excel_file = file_name
            self.excel_label.setText(f"Fichier Excel sélectionné : {os.path.basename(file_name)}")
            self.log_message(f"Fichier sélectionné : {file_name}")
    
    def convert_to_sql(self):
        """Traite le fichier Excel et génère le fichier SQL"""
        if not self.excel_file:
            self.log_message("❌ Erreur : Aucun fichier Excel sélectionné")
            return
        
        try:
            # Lire arret_id depuis l'entrée
            try:
                arret_id = int(self.arret_id_input.text()) if self.arret_id_input.text().strip() else 1
            except ValueError:
                arret_id = 1
                self.log_message("⚠️ Arret ID invalide, utilisation de la valeur par défaut (1)")
            
            # Vérifier l'existence du fichier
            if not os.path.exists(self.excel_file):
                raise FileNotFoundError(f"Le fichier {self.excel_file} n'existe pas")
            
            self.log_message(f"Lecture du fichier : {self.excel_file}")
            df_temp = pd.read_excel(self.excel_file, header=None)
            
            if df_temp.empty:
                raise ValueError("Le fichier Excel est vide")
            
            self.log_message(f"Nombre de lignes lues : {len(df_temp)}")
            
            # Trouver la ligne d'en-têtes
            header_row = find_header_row(df_temp)
            self.log_message(f"Ligne d'en-têtes détectée : {header_row + 1}")
            
            # Relire avec la bonne ligne d'en-têtes
            if header_row > 0:
                df = pd.read_excel(self.excel_file, header=header_row)
            else:
                df = df_temp.copy()
                df.columns = [f'col_{i}' for i in range(len(df.columns))]
            
            # Nettoyer les noms de colonnes
            if header_row > 0:
                df.columns = clean_column_names(df.columns.tolist())
            
            self.log_message(f"Colonnes finales : {df.columns.tolist()}")
            self.log_message(f"Nombre de lignes de données : {len(df)}")
            
            # Afficher un aperçu des premières lignes
            self.log_message("\n=== APERÇU DES DONNÉES ===")
            self.log_message(df.head().to_string())
            
            # Générer les requêtes SQL
            sql_queries = generate_sql_queries(df, arret_id)
            
            if not sql_queries:
                self.log_message("Aucune requête SQL générée. Vérifiez le format des données.")
                return
            
            # Générer le nom du fichier de sortie
            output_file = os.path.splitext(self.excel_file)[0] + '_queries.sql'
            
            # Sauvegarder dans un fichier
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("-- Requêtes d'insertion générées automatiquement\n")
                f.write(f"-- Source: {self.excel_file}\n")
                f.write(f"-- Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                for query in sql_queries:
                    f.write(query + '\n\n')
            
            self.log_message(f"✅ {len(sql_queries)} requêtes SQL générées avec succès dans '{output_file}'")
        
        except FileNotFoundError as e:
            self.log_message(f"❌ Erreur : {e}")
        except Exception as e:
            self.log_message(f"❌ Erreur inattendue : {e}")
            import traceback
            self.log_message(traceback.format_exc())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExcelToSQLConverter()
    window.show()
    sys.exit(app.exec_())