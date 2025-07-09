import sys
import os
import shutil
import pandas as pd
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem, QTextEdit,
    QHeaderView, QSizePolicy, QProgressBar, QStackedWidget, QListWidget, QListWidgetItem, QFrame,
    QGraphicsDropShadowEffect, QScrollArea, QSpacerItem
)
from PyQt6.QtGui import QFont, QColor, QPalette, QIcon, QPixmap, QPainter
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QCoreApplication

# --- Ajout pour supprimer le DeprecationWarning de sip (souvent lié à PyQt6 et Python) ---
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module='sip')
# --- Fin de l'ajout ---

# --- Worker Thread for Heavy Operations ---
class WorkerThread(QThread):
    """
    Gère les opérations de traitement de données lourdes (lecture Excel, calculs) dans un thread séparé
    pour maintenir la réactivité de l'interface graphique.
    """
    finished = pyqtSignal(object) # Émet un dictionnaire de résultats
    log_message = pyqtSignal(str)
    status_update = pyqtSignal(str)

    def __init__(self, excel_file_path, sheet_name):
        super().__init__()
        self.excel_file_path = excel_file_path
        self.sheet_name = sheet_name

    def run(self):
        annual_output_csv_filename = 'annual_climatic_ranges.csv'
        
        # Définition des colonnes nécessaires et de leurs noms d'affichage
        columns_needed = {
            'Temperature sous abrit °c': 'Température (°C)',
            'Humidité %': 'Humidité (%)',
            'Force du Vent m/s': 'Vitesse du vent (m/s)',
            'Pression mer': 'Pression au niveau de la mer (hPa)',
            'tension de vapeur (ew)': 'Tension de vapeur',
            'Temperature mouillé': 'Température humide',
            'Temperature de point de rose': 'Température du point de rosée',
            'Pression Station': 'Pression station',
            'Précipitation': 'Précipitation (mm)'
        }

        self.status_update.emit("Statut: Traitement en cours...")
        self.log_message.emit("Démarrage du calcul...\n")

        output_dir = 'climatic_output_pyqt'
        # Assure que le répertoire de sortie est propre avant de démarrer un nouveau calcul
        if os.path.exists(output_dir):
            try:
                shutil.rmtree(output_dir)
                self.log_message.emit(f"Dossier de sortie existant vidé: {output_dir}\n")
            except OSError as e:
                self.log_message.emit(f"Erreur lors du nettoyage du dossier de sortie: {e}\n")
                # Ne pas bloquer l'exécution, mais continuer avec un avertissement
        os.makedirs(output_dir, exist_ok=True)


        try:
            if not os.path.exists(self.excel_file_path):
                raise FileNotFoundError(f"Le fichier n'a pas été trouvé à l'emplacement : {self.excel_file_path}")

            df = pd.read_excel(self.excel_file_path, sheet_name=self.sheet_name)
            self.log_message.emit(f"Fichier Excel chargé avec succès : {self.excel_file_path} (Feuille : {self.sheet_name})\n")

            # --- Section Critique de Conversion de Type pour les Colonnes de Date/Heure ---
            # Assure que 'annee', 'mois', 'joure' sont des entiers, en supprimant les lignes avec des entrées invalides.
            for date_col in ['annee', 'mois', 'joure']:
                if date_col not in df.columns:
                    raise ValueError(f"La colonne '{date_col}' est manquante dans le fichier Excel! Veuillez vérifier le fichier et le nom de la feuille. Les colonnes requises sont 'annee', 'mois', 'joure'.")
                
                df[date_col] = pd.to_numeric(df[date_col], errors='coerce')
                
                if df[date_col].isnull().any():
                    self.log_message.emit(f"Avertissement: Des valeurs non numériques ou manquantes trouvées dans la colonne '{date_col}'. Les lignes affectées ({df[date_col].isnull().sum()} lignes) seront ignorées pour les calculs basés sur cette colonne.\n")
                    df = df.dropna(subset=[date_col]) # Supprime les lignes où ces colonnes critiques sont NaN
                
                # Après avoir nettoyé les NaN, convertir en type entier
                if not df.empty: # Convertir seulement si le DataFrame n'est pas vide après la suppression des NaN
                    df[date_col] = df[date_col].astype(int)
                else:
                    self.log_message.emit("Erreur critique: Le DataFrame est vide après le nettoyage des colonnes de date. Impossible de poursuivre les calculs.\n")
                    raise ValueError("Données insuffisantes pour les calculs après le nettoyage des colonnes de date.")


            # --- Assure que les autres 'columns_needed' sont numériques et gère les codes d'erreur ---
            for col_original, col_display in columns_needed.items():
                if col_original not in df.columns:
                    raise ValueError(f"La colonne '{col_original}' ('{col_display}') est manquante dans le fichier Excel! Veuillez vérifier le fichier et le nom de la feuille.")
                
                # Convertir en numérique, forçant les erreurs en NaN
                df[col_original] = pd.to_numeric(df[col_original], errors='coerce')
                
                # Remplace les codes d'erreur spécifiques par NaN
                initial_na_count = df[col_original].isnull().sum()
                df[col_original] = df[col_original].mask(df[col_original].isin([5555, -9999]), pd.NA)
                replaced_na_count = df[col_original].isnull().sum() - initial_na_count
                if replaced_na_count > 0:
                    self.log_message.emit(f"Info: {replaced_na_count} valeurs '-9999' ou '5555' remplacées par des valeurs manquantes dans la colonne '{col_display}'.\n")

                # Assure qu'ils sont de type float pour permettre les valeurs NaN et les opérations numériques ultérieures
                df[col_original] = df[col_original].astype(float)


            # --- Calcul des Plages Annuelles ---
            annual_range_cols = ['annee'] + list(columns_needed.keys())
            
            # Filtre le df pour inclure uniquement les colonnes pertinentes pour le calcul des plages annuelles
            df_for_annual = df[annual_range_cols]
            # Supprime les lignes avec des valeurs NaN dans les colonnes utilisées pour le calcul min/max
            # Cela garantit que min/max ne sont pas affectés par les NaN
            df_for_annual = df_for_annual.dropna(subset=list(columns_needed.keys()))

            full_annual_output_path = None # Initialiser à None
            if df_for_annual.empty:
                self.log_message.emit("Avertissement: Aucune donnée valide disponible pour le calcul des plages annuelles après le nettoyage. Un fichier CSV annuel vide sera créé.\n")
                full_annual_output_path = os.path.join(output_dir, annual_output_csv_filename)
                pd.DataFrame(columns=['annee'] + list(columns_needed.values())).to_csv(full_annual_output_path, index=False) # Crée un fichier vide avec en-têtes
            else:
                # --- CORRECTION ICI : Appliquer min() et max() après dropna() au lieu de skipna=True ---
                annual_min = df_for_annual.groupby('annee')[list(columns_needed.keys())].min() # Sans skipna
                annual_max = df_for_annual.groupby('annee')[list(columns_needed.keys())].max() # Sans skipna
                # --- FIN DE LA CORRECTION ---

                annual_range = annual_max - annual_min
                annual_range = annual_range.rename(columns=columns_needed) # Renomme les colonnes pour l'affichage
                
                full_annual_output_path = os.path.join(output_dir, annual_output_csv_filename)
                annual_range.to_csv(full_annual_output_path)
                self.log_message.emit(f"✅ Plages climatiques annuelles sauvegardées dans : {full_annual_output_path}\n")

            # --- Calcul des Statistiques Mensuelles (Min, Max, Amx) ---
            monthly_data_map = {} # Dictionnaire pour stocker {nom_variable_display: chemin_fichier}
            for i, (col_original, col_display) in enumerate(columns_needed.items()):
                # Supprime les NA uniquement pour la variable spécifique analysée pour les statistiques mensuelles
                # On utilise .copy() pour éviter SettingWithCopyWarning
                var_df = df[['annee', 'mois', 'joure', col_original]].dropna().copy()
                monthly_stats = {}

                for month in range(1, 13):
                    month_data = var_df[var_df['mois'] == month].sort_values(by=['annee', 'mois', 'joure'])
                    if month_data.empty:
                        # Si aucune donnée pour le mois, les stats sont NaN
                        monthly_stats[month] = {
                            'Min': pd.NA,
                            'Max': pd.NA,
                            'Amx': pd.NA
                        }
                        continue

                    min_val = month_data[col_original].min(skipna=True)
                    max_val = month_data[col_original].max(skipna=True)
                    
                    # Calcule l'amplitude maximale (Amx) comme l'écart absolu maximum entre valeurs consécutives (tri-horaires)
                    # Assurez-vous qu'il y a au moins deux points de données pour calculer une différence
                    if len(month_data) > 1:
                        # Convertir la série en numérique pour s'assurer que .diff() fonctionne correctement
                        diffs = pd.to_numeric(month_data[col_original], errors='coerce').diff().abs()
                        max_amplitude = diffs.max(skipna=True)
                    else:
                        max_amplitude = pd.NA # Pas d'amplitude si une seule donnée

                    monthly_stats[month] = {
                        'Min': min_val,
                        'Max': max_val,
                        'Amx': max_amplitude
                    }

                months_list = list(range(1, 13))
                result_df = pd.DataFrame({
                    'Mois': months_list,
                    'Min': [monthly_stats.get(m, {}).get('Min', pd.NA) for m in months_list],
                    'Max': [monthly_stats.get(m, {}).get('Max', pd.NA) for m in months_list],
                    'Amx': [monthly_stats.get(m, {}).get('Amx', pd.NA) for m in months_list],
                })

                # --- Nettoyage du nom de fichier : Remplace les espaces, parenthèses et barres obliques ---
                sanitized_col_display = col_display.replace(' ', '_').replace('(', '').replace(')', '').replace('/', '_')
                monthly_csv_filename = f"statistiques_mensuelles_{sanitized_col_display}.csv"
                # --- Fin du nettoyage du nom de fichier ---

                full_monthly_output_path = os.path.join(output_dir, monthly_csv_filename)
                result_df.to_csv(full_monthly_output_path, index=False)
                # Store original display name with its path for the UI
                monthly_data_map[col_display] = full_monthly_output_path
                self.log_message.emit(f"✅ Statistiques mensuelles pour '{col_display}' sauvegardées dans : {full_monthly_output_path}\n")

                # Émet la progression vers l'interface graphique
                progress = int(((i + 1) / len(columns_needed)) * 100)
                self.status_update.emit(f"Statut: Calcul en cours... {progress}%")


            self.status_update.emit("Statut: Calcul terminé avec succès ! Fichiers disponibles pour affichage et téléchargement.")
            # Émet les résultats comme un dictionnaire pour une consommation plus facile
            results_dict = {
                'annual_file': full_annual_output_path,
                'monthly_files_map': monthly_data_map
            }
            self.finished.emit(results_dict)

        except FileNotFoundError as fnfe:
            self.status_update.emit(f"❌ Erreur: Fichier introuvable!")
            self.log_message.emit(f"❌ Erreur Fichier: {fnfe}\nAssurez-vous que le chemin du fichier Excel est correct.\n")
            self.finished.emit({'annual_file': None, 'monthly_files_map': {}})
        except pd.errors.EmptyDataError as ede:
            self.status_update.emit(f"❌ Erreur: Fichier vide ou illisible!")
            self.log_message.emit(f"❌ Erreur de données: {ede}\nLe fichier Excel est vide ou ne contient pas de données valides.\n")
            self.finished.emit({'annual_file': None, 'monthly_files_map': {}})
        except KeyError as ke:
            self.status_update.emit(f"❌ Erreur: Colonne manquante!")
            self.log_message.emit(f"❌ Erreur de colonne: {ke}\nUne colonne essentielle est manquante. Veuillez vérifier les noms des colonnes dans votre fichier Excel (e.g., 'annee', 'mois', 'joure' ou les variables climatiques).\n")
            self.finished.emit({'annual_file': None, 'monthly_files_map': {}})
        except Exception as e:
            # Gère toute autre exception pendant le calcul
            self.status_update.emit(f"❌ Erreur lors du calcul !")
            self.log_message.emit(f"❌ Erreur inattendue : {e}\n")
            # En cas d'erreur, émet des valeurs vides ou None
            self.finished.emit({'annual_file': None, 'monthly_files_map': {}})
            # Nettoie le répertoire de sortie si une erreur s'est produite
            if os.path.exists(output_dir):
                try:
                    shutil.rmtree(output_dir)
                    self.log_message.emit(f"Dossier de sortie nettoyé suite à une erreur : {e}\n") # Fixed: Was using 'err' instead of 'e'
                except OSError as err_cleanup:
                    self.log_message.emit(f"Erreur lors du nettoyage du dossier de sortie : {err_cleanup}\n")

# --- Classes d'Interface Graphique (Pages du Dashboard) ---

class HomePage(QWidget):
    """
    Page d'accueil simple du dashboard avec des tuiles informatives et cliquables.
    """
    # Signal pour demander le changement de page
    switch_page_requested = pyqtSignal(object, QPushButton)

    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setSpacing(30)
        self.setLayout(main_layout)

        welcome_label = QLabel("Bienvenue sur l'Application d'Analyse Climatique")
        welcome_label.setFont(QFont("Roboto", 24, QFont.Weight.Bold))
        welcome_label.setStyleSheet("color: #2C3E50; margin-bottom: 20px;")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(welcome_label)

        info_label = QLabel("Votre outil complet pour analyser les données météorologiques et climatiques.")
        info_label.setFont(QFont("Roboto", 14))
        info_label.setStyleSheet("color: #7F8C8D; margin-bottom: 30px;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(info_label)

        # Tuiles du Dashboard (Maintenant des QPushButton pour la cliquabilité)
        tiles_layout = QHBoxLayout()
        tiles_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tiles_layout.setSpacing(20)

        # Tuile 1: Configuration
        self.tile_config = self._create_dashboard_tile("Configuration", "Préparez vos données Excel pour l'analyse.", "data_icon.png")
        tiles_layout.addWidget(self.tile_config)

        # Tuile 2: Analyse
        self.tile_analyze = self._create_dashboard_tile("Analyse", "Lancez les calculs de plages annuelles et mensuelles.", "chart_icon.png")
        tiles_layout.addWidget(self.tile_analyze)

        # Tuile 3: Résultats
        self.tile_results = self._create_dashboard_tile("Résultats", "Visualisez et téléchargez vos rapports d'analyse.", "report_icon.png")
        tiles_layout.addWidget(self.tile_results)
        
        main_layout.addLayout(tiles_layout)
        main_layout.addStretch()

    def _create_dashboard_tile(self, title, description, icon_name):
        """Crée un widget 'tuile' cliquable (basé sur QPushButton)."""
        tile_button = QPushButton() # Utilise QPushButton comme base
        tile_button.setFixedSize(280, 220) # Taille fixe agrandie
        tile_button.setObjectName("dashboardTile") # Nom d'objet pour le style CSS
        
        # Désactiver la focus policy pour ne pas avoir de bordure de focus
        tile_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        tile_layout = QVBoxLayout()
        tile_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tile_layout.setSpacing(10) # Espacement entre les éléments de la tuile
        tile_button.setLayout(tile_layout) # Le layout est défini sur le bouton

        icon_path = os.path.join(os.path.dirname(__file__), "icons", icon_name)
        if os.path.exists(icon_path):
            icon_label = QLabel()
            icon_pixmap = QPixmap(icon_path).scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation) # Icône plus grande
            icon_label.setPixmap(icon_pixmap)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            tile_layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Roboto", 16, QFont.Weight.Bold)) # Texte du titre plus grand
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: inherit;") # Hérite de la couleur du bouton
        tile_layout.addWidget(title_label)

        desc_label = QLabel(description)
        desc_label.setFont(QFont("Roboto", 11)) # Texte de description plus grand
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: inherit;") # Hérite de la couleur du bouton
        tile_layout.addWidget(desc_label)

        tile_layout.addStretch() # Pousse le contenu vers le haut

        return tile_button


class InputPage(QWidget):
    """
    Page pour la sélection du fichier Excel et de la feuille.
    """
    file_selected = pyqtSignal(object) # Signal émis quand l'utilisateur clique sur "Démarrer l'Analyse" ou "Aperçu"

    def __init__(self):
        super().__init__()
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(30, 30, 30, 30)

        title_label = QLabel("Configuration des Données")
        title_label.setFont(QFont("Roboto", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #2C3E50; margin-bottom: 20px;")
        self.main_layout.addWidget(title_label)

        # File Path
        file_path_layout = QHBoxLayout()
        file_path_layout.addWidget(QLabel("Chemin du Fichier Excel:"))
        self.excel_path_input = QLineEdit()
        self.excel_path_input.setPlaceholderText("Ex: C:/data/my_file.xlsx")
        file_path_layout.addWidget(self.excel_path_input)
        browse_btn = QPushButton("Parcourir...")
        browse_btn.clicked.connect(self.browse_file)
        file_path_layout.addWidget(browse_btn)
        self.main_layout.addLayout(file_path_layout)
        self.main_layout.addSpacing(15)

        # Sheet Name
        sheet_name_layout = QHBoxLayout()
        sheet_name_layout.addWidget(QLabel("Nom de la Feuille:"))
        self.sheet_name_input = QLineEdit()
        self.sheet_name_input.setPlaceholderText("Ex: MySheet")
        sheet_name_layout.addWidget(self.sheet_name_input)
        self_fill_btn = QPushButton("Suggérer") # Button to suggest sheet names
        self_fill_btn.setToolTip("Tente de remplir le nom de la première feuille.")
        self_fill_btn.setObjectName("suggestButton") # Définir un nom d'objet
        self_fill_btn.clicked.connect(self.suggest_sheet_name)
        sheet_name_layout.addWidget(self_fill_btn)
        self.main_layout.addLayout(sheet_name_layout)
        self.main_layout.addSpacing(25)

        # Action Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch() # Push buttons to the right
        self.preview_btn = QPushButton("Aperçu du Tableau")
        self.preview_btn.setObjectName("actionButton")
        self.preview_btn.clicked.connect(lambda: self.emit_action_request("preview"))
        button_layout.addWidget(self.preview_btn)

        self.calculate_btn = QPushButton("Démarrer l'Analyse")
        self.calculate_btn.setObjectName("actionButton")
        self.calculate_btn.clicked.connect(lambda: self.emit_action_request("calculate"))
        button_layout.addWidget(self.calculate_btn)
        self.main_layout.addLayout(button_layout)
        self.main_layout.addStretch() # Push everything to top

        # Set default values for convenience (adjusted path based on common Linux setup)
        # Assurez-vous que ce chemin est valide sur votre système pour le test
        self.excel_path_input.setText("/home/aounallah/Bureau/sat_sat/msi/Tizi-Ouzou - tri-horaire.xlsx")
        self.sheet_name_input.setText("DAMZ_1991_2020_tri_horaire")

    def browse_file(self):
        """Ouvre une boîte de dialogue pour sélectionner un fichier Excel."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Sélectionner le Fichier Excel", "", "Excel files (*.xlsx *.xls);;All files (*.*)")
        if file_path:
            self.excel_path_input.setText(file_path)
            # Try to auto-fill sheet name if a new file is selected
            self.suggest_sheet_name()

    def suggest_sheet_name(self):
        """Tente de suggérer le nom de la première feuille du fichier Excel sélectionné."""
        excel_path = self.excel_path_input.text()
        if not os.path.exists(excel_path):
            QMessageBox.warning(self, "Fichier introuvable", "Veuillez d'abord sélectionner un fichier Excel valide.")
            return

        try:
            xls = pd.ExcelFile(excel_path)
            if xls.sheet_names:
                self.sheet_name_input.setText(xls.sheet_names[0])
                QMessageBox.information(self, "Nom de feuille suggéré", f"Le nom de la première feuille '{xls.sheet_names[0]}' a été suggéré.")
            else:
                QMessageBox.warning(self, "Aucune feuille", "Aucune feuille trouvée dans ce fichier Excel.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur de lecture", f"Impossible de lire les feuilles du fichier : {e}\nErreur: {e}")

    def get_input_data(self):
        """Retourne le chemin du fichier Excel et le nom de la feuille."""
        return self.excel_path_input.text(), self.sheet_name_input.text()

    def emit_action_request(self, action_type):
        """Émet un signal pour demander une action (preview ou calculate)."""
        excel_path, sheet_name = self.get_input_data()
        if not excel_path or not sheet_name:
            QMessageBox.warning(self, "Entrée Incomplète", "Veuillez spécifier le chemin du fichier et le nom de la feuille.")
            return
        if not os.path.exists(excel_path):
            QMessageBox.warning(self, "Fichier Introuvable", f"Le fichier Excel spécifié n'existe pas : {excel_path}")
            return
        
        # Émet un tuple (type d'action, chemin fichier, nom feuille)
        self.file_selected.emit({"action": action_type, "path": excel_path, "sheet": sheet_name})


class PreviewPage(QWidget):
    """
    Page pour afficher un aperçu des données du tableau Excel.
    """
    def __init__(self):
        super().__init__()
        self.excel_file_path = None
        self.sheet_name = None
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(30, 30, 30, 30)

        title_label = QLabel("Aperçu des Données")
        title_label.setFont(QFont("Roboto", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #2C3E50; margin-bottom: 20px;")
        self.layout.addWidget(title_label)

        self.table_widget = QTableWidget()
        self.table_widget.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.setStyleSheet("""
            QTableWidget {
                gridline-color: #e0e0e0;
                background-color: #ffffff;
                alternate-background-color: #f5f5f5;
                selection-background-color: #bbdefb; /* Light blue for selection */
                selection-color: black;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            QHeaderView::section {
                background-color: #42A5F5; /* Blue 400 */
                color: white;
                font-weight: bold;
                padding: 8px;
                border: 1px solid #bbdefb;
            }
        """)
        self.layout.addWidget(self.table_widget)

    def load_preview(self, excel_file_path, sheet_name):
        """
        Charge et affiche les 50 premières lignes du fichier Excel.
        """
        self.excel_file_path = excel_file_path
        self.sheet_name = sheet_name

        if not self.excel_file_path or not os.path.exists(self.excel_file_path):
            self.display_error("Le chemin du fichier Excel n'est pas valide ou le fichier n'existe pas.")
            return

        try:
            # Lire seulement les 50 premières lignes pour l'aperçu
            df_preview = pd.read_excel(self.excel_file_path, sheet_name=self.sheet_name, nrows=50)
            self.display_dataframe_in_table(df_preview)
        except Exception as e:
            self.display_error(f"Impossible de charger l'aperçu du fichier. Veuillez vérifier le chemin du fichier et le nom de la feuille.\nErreur: {e}")

    def display_dataframe_in_table(self, dataframe):
        """Popule le QTableWidget avec les données d'un DataFrame Pandas."""
        self.table_widget.clearContents()
        self.table_widget.setRowCount(dataframe.shape[0])

        current_columns = [self.table_widget.horizontalHeaderItem(i).text() for i in range(self.table_widget.columnCount())]
        new_columns = list(dataframe.columns.astype(str))

        if current_columns != new_columns:
            self.table_widget.setColumnCount(dataframe.shape[1])
            self.table_widget.setHorizontalHeaderLabels(new_columns)
            header = self.table_widget.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
            header.setStretchLastSection(True)

        for i in range(dataframe.shape[0]):
            for j in range(dataframe.shape[1]):
                item = QTableWidgetItem(str(dataframe.iloc[i, j]))
                self.table_widget.setItem(i, j, item)
        self.table_widget.resizeColumnsToContents()
        self.table_widget.resizeRowsToContents()

    def display_error(self, message):
        """Affiche un message d'erreur et vide le tableau."""
        QMessageBox.critical(self, "Erreur d'aperçu", message)
        self.table_widget.clearContents()
        self.table_widget.setRowCount(0)
        self.table_widget.setColumnCount(0)
        self.table_widget.setHorizontalHeaderLabels([])


class ResultsPage(QWidget):
    """
    Page pour afficher les logs de calcul, la progression, et les liens de téléchargement.
    Les tableaux sont maintenant dans une page séparée.
    """
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(30, 30, 30, 30)

        # 1. Section Statut et Progression
        self.status_label = QLabel("Statut: En attente de calcul.")
        self.status_label.setFont(QFont("Roboto", 14, QFont.Weight.Bold))
        self.status_label.setStyleSheet("color: #2C3E50; margin-bottom: 10px;")
        self.layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #B0BEC5; /* Blue Grey 200 */
                border-radius: 5px;
                text-align: center;
                background-color: #ECEFF1; /* Blue Grey 50 */
                color: #263238; /* Blue Grey 900 */
            }
            QProgressBar::chunk {
                background-color: #64B5F6; /* Blue 300 */
                border-radius: 5px;
            }
        """)
        self.layout.addWidget(self.progress_bar)
        self.layout.addSpacing(20)

        # 2. Section Logs du Calcul
        log_label = QLabel("Logs du Calcul:")
        log_label.setFont(QFont("Roboto", 12, QFont.Weight.Bold))
        log_label.setStyleSheet("color: #2C3E50; margin-bottom: 5px;")
        self.layout.addWidget(log_label)

        self.log_text_edit = QTextEdit()
        self.log_text_edit.setReadOnly(True)
        self.log_text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #F8F9FA; /* Light grey background */
                color: #34495E; /* Dark blue-grey text */
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 9pt;
                border: 1px solid #CFD8DC; /* Light Blue Grey 200 */
                border-radius: 5px;
                padding: 10px;
            }
        """)
        self.layout.addWidget(self.log_text_edit)
        self.layout.addSpacing(20)

        # 3. Section Téléchargement
        download_label = QLabel("Télécharger les Résultats:")
        download_label.setFont(QFont("Roboto", 12, QFont.Weight.Bold))
        download_label.setStyleSheet("color: #2C3E50; margin-bottom: 5px;")
        self.layout.addWidget(download_label)

        self.download_layout = QVBoxLayout()
        self.layout.addLayout(self.download_layout)

        self.download_placeholder = QLabel("Les liens de téléchargement apparaîtront ici après le calcul.")
        self.download_placeholder.setStyleSheet("color: #7F8C8D; font-style: italic;")
        self.download_layout.addWidget(self.download_placeholder)

        self.layout.addStretch() # Pousse le contenu vers le haut

    def update_status(self, message):
        """Met à jour le label de statut et la barre de progression."""
        self.status_label.setText(message)
        if "%" in message:
            try:
                progress_value = int(message.split('%')[0].split()[-1])
                self.progress_bar.setValue(progress_value)
            except ValueError:
                pass # Si ce n'est pas un pourcentage parsable, ne pas mettre à jour la barre
        else:
            self.progress_bar.setValue(0) # Réinitialise la barre de progression pour les messages non-pourcentage

    def append_log(self, message):
        """Ajoute un message à la zone de texte des logs."""
        self.log_text_edit.append(message)
        # Faire défiler vers le bas automatiquement
        self.log_text_edit.verticalScrollBar().setValue(self.log_text_edit.verticalScrollBar().maximum())

    def clear_download_links(self):
        """Supprime tous les boutons de téléchargement existants et réinitialise la section de téléchargement."""
        # Supprimer le placeholder si déjà présent
        if self.download_placeholder:
            self.download_layout.removeWidget(self.download_placeholder)
            self.download_placeholder.deleteLater()
            self.download_placeholder = None

        # Supprimer tous les widgets existants dans le layout de téléchargement (boutons, labels)
        while self.download_layout.count() > 0:
            item = self.download_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater() # Supprime le widget en toute sécurité

        # Recréer le placeholder
        self.download_placeholder = QLabel("Les liens de téléchargement apparaîtront ici après le calcul.")
        self.download_placeholder.setStyleSheet("color: #7F8C8D; font-style: italic;")
        self.download_layout.addWidget(self.download_placeholder)

    def set_download_content(self, annual_file, monthly_files_map):
        """
        Crée les boutons de téléchargement pour les fichiers de résultats.
        """
        self.clear_download_links() # Effacer les anciens boutons

        download_present = False
        if annual_file and isinstance(annual_file, str) and os.path.exists(annual_file):
            annual_label = QLabel("Fichier Annuel:", font=QFont("Roboto", 10, QFont.Weight.Bold))
            annual_label.setStyleSheet("color: #333333;")
            self.download_layout.addWidget(annual_label)

            btn_annual = QPushButton(os.path.basename(annual_file))
            btn_annual.setObjectName("downloadButtonAnnual") # Object name for specific styling
            btn_annual.clicked.connect(lambda: self.save_file_dialog(annual_file))
            self.download_layout.addWidget(btn_annual)
            download_present = True

        if monthly_files_map:
            if download_present: # Add spacing if annual file was present
                self.download_layout.addSpacing(10) 
            monthly_label = QLabel("Fichiers Mensuels:", font=QFont("Roboto", 10, QFont.Weight.Bold))
            monthly_label.setStyleSheet("color: #333333;")
            self.download_layout.addWidget(monthly_label)

            for display_name, mf_path in sorted(monthly_files_map.items()): # Trier pour un ordre cohérent
                if isinstance(mf_path, str) and os.path.exists(mf_path):
                    btn_monthly = QPushButton(f"Stats Mensuelles ({display_name})") # Nom plus descriptif
                    btn_monthly.setObjectName("downloadButtonMonthly")
                    btn_monthly.clicked.connect(lambda f=mf_path: self.save_file_dialog(f))
                    self.download_layout.addWidget(btn_monthly)
                    download_present = True
                else:
                    if not isinstance(mf_path, str):
                        self.append_log(f"Avertissement: Élément inattendu dans la liste des fichiers mensuels (type={type(mf_path).__name__}): {mf_path}\n")
                    else:
                        self.append_log(f"Avertissement: Fichier mensuel attendu non trouvé: {mf_path}\n")
        
        if not download_present:
            pass # Placeholder should remain if no files to download
        else:
            # Remove placeholder if files are present
            if self.download_placeholder:
                self.download_layout.removeWidget(self.download_placeholder)
                self.download_placeholder.deleteLater()
                self.download_placeholder = None

    def save_file_dialog(self, source_path):
        """
        Ouvre une boîte de dialogue d'enregistrement de fichier et copie le fichier source
        vers la destination choisie.
        """
        if not isinstance(source_path, str) or not os.path.exists(source_path):
            QMessageBox.critical(self, "Erreur de Fichier", "Le fichier source n'existe pas ou le chemin est invalide.")
            return

        initial_filename = os.path.basename(source_path)
        dest_path, _ = QFileDialog.getSaveFileName(self, "Sauvegarder le Fichier", initial_filename, "CSV files (*.csv);;All files (*.*)")
        if dest_path:
            try:
                shutil.copy(source_path, dest_path)
                QMessageBox.information(self, "Téléchargement réussi", f"Le fichier a été sauvegardé avec succès à : {dest_path}")
                self.append_log(f"Fichier téléchargé : {dest_path}\n")
            except Exception as e:
                QMessageBox.critical(self, "Erreur de téléchargement", f"Impossible de sauvegarder le fichier : {e}")
                self.append_log(f"❌ Erreur lors du téléchargement de {source_path} vers {dest_path}: {e}\n")


class DataTablePage(QWidget):
    """
    Nouvelle page dédiée à l'affichage des tableaux de résultats annuel et mensuel.
    """
    def __init__(self):
        super().__init__()
        self._monthly_files_map = {} # Pour stocker le mappage nom d'affichage -> chemin_fichier
        
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        main_layout.setContentsMargins(30, 30, 30, 30)

        title_label = QLabel("Tableaux de Résultats")
        title_label.setFont(QFont("Roboto", 20, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #2C3E50; margin-bottom: 20px; text-align: center;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # Layout horizontal pour les deux tableaux (annuel et mensuel)
        tables_h_layout = QHBoxLayout()
        tables_h_layout.setSpacing(30) # Plus d'espace entre les tableaux
        main_layout.addLayout(tables_h_layout)

        # Tableau Annuel (Gauche)
        annual_v_layout = QVBoxLayout()
        annual_label = QLabel("Plages Climatiques Annuelles:")
        annual_label.setFont(QFont("Roboto", 14, QFont.Weight.Bold))
        annual_label.setStyleSheet("color: #34495E; margin-bottom: 10px;")
        annual_v_layout.addWidget(annual_label)
        
        self.annual_table = QTableWidget()
        self._style_table_widget(self.annual_table)
        annual_v_layout.addWidget(self.annual_table)
        tables_h_layout.addLayout(annual_v_layout, 1) # Occupe 1 part de l'espace horizontal

        # Tableaux Mensuels (Droite - Liste + Tableau de données)
        monthly_main_v_layout = QVBoxLayout()
        monthly_label = QLabel("Statistiques Mensuelles (Sélectionnez une variable):")
        monthly_label.setFont(QFont("Roboto", 14, QFont.Weight.Bold))
        monthly_label.setStyleSheet("color: #34495E; margin-bottom: 10px;")
        monthly_main_v_layout.addWidget(monthly_label)
        
        monthly_selection_h_layout = QHBoxLayout()
        self.monthly_variable_list = QListWidget()
        self.monthly_variable_list.setFixedWidth(200) # Largeur fixe pour la liste des variables
        self.monthly_variable_list.itemClicked.connect(self.on_monthly_item_selected)
        self._style_list_widget(self.monthly_variable_list)
        monthly_selection_h_layout.addWidget(self.monthly_variable_list)

        self.monthly_data_table = QTableWidget()
        self._style_table_widget(self.monthly_data_table)
        monthly_selection_h_layout.addWidget(self.monthly_data_table, 2) # Occupe 2 parts de l'espace horizontal restant

        monthly_main_v_layout.addLayout(monthly_selection_h_layout)
        tables_h_layout.addLayout(monthly_main_v_layout, 2) # Occupe 2 parts de l'espace horizontal total

        main_layout.addStretch() # Pousse le contenu vers le haut

    def _style_table_widget(self, table_widget):
        """Applique un style commun aux QTableWidget."""
        table_widget.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table_widget.setAlternatingRowColors(True)
        table_widget.setStyleSheet("""
            QTableWidget {
                gridline-color: #e0e0e0;
                background-color: #ffffff;
                alternate-background-color: #f5f5f5;
                selection-background-color: #bbdefb; /* Light blue for selection */
                selection-color: black;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            QHeaderView::section {
                background-color: #42A5F5; /* Blue 400 */
                color: white;
                font-weight: bold;
                padding: 8px;
                border: 1px solid #bbdefb;
            }
            QTableWidget::item {
                padding: 5px;
            }
        """)
        table_widget.horizontalHeader().setStretchLastSection(True)
        table_widget.verticalHeader().setVisible(False) # Hide row numbers for cleaner look
    
    def _style_list_widget(self, list_widget):
        """Applique un style commun aux QListWidget."""
        list_widget.setStyleSheet("""
            QListWidget {
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                background-color: white;
                selection-background-color: #BBDEFB;
                selection-color: black;
                padding: 5px;
            }
            QListWidget::item {
                padding: 7px;
                margin-bottom: 3px;
                border-bottom: 1px solid #F0F0F0; /* Light separator */
            }
            QListWidget::item:selected {
                background-color: #42A5F5; /* Blue 400 */
                color: white;
                font-weight: bold;
            }
            QListWidget::item:hover:!selected {
                background-color: #E3F2FD; /* Light Blue 50 */
            }
        """)

    def display_dataframe_in_table(self, table_widget, dataframe):
        """Popule le QTableWidget avec les données d'un DataFrame Pandas."""
        table_widget.clearContents()
        table_widget.setRowCount(dataframe.shape[0])
        table_widget.setColumnCount(dataframe.shape[1])
        table_widget.setHorizontalHeaderLabels(list(dataframe.columns.astype(str)))
        
        header = table_widget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setStretchLastSection(True)

        for i in range(dataframe.shape[0]):
            for j in range(dataframe.shape[1]):
                # Gérer les valeurs NaN pour un affichage propre
                value = dataframe.iloc[i, j]
                display_value = "" if pd.isna(value) else str(value)
                item = QTableWidgetItem(display_value)
                table_widget.setItem(i, j, item)
        table_widget.resizeColumnsToContents()
        table_widget.resizeRowsToContents()

    def load_data_and_display(self, annual_file_path, monthly_files_map):
        """
        Charge et affiche les données dans les tableaux annuel et mensuel.
        Appelé par la MainWindow après un calcul réussi.
        """
        # Afficher le tableau annuel
        if annual_file_path and os.path.exists(annual_file_path):
            try:
                df_annual = pd.read_csv(annual_file_path)
                self.display_dataframe_in_table(self.annual_table, df_annual)
            except Exception as e:
                QMessageBox.warning(self, "Erreur de chargement", f"Impossible de charger le tableau annuel : {e}")
                self.annual_table.clearContents()
                self.annual_table.setRowCount(0)
                self.annual_table.setColumnCount(0)
        else:
            self.annual_table.clearContents()
            self.annual_table.setRowCount(0)
            self.annual_table.setColumnCount(0)
            QMessageBox.information(self, "Données Annuelles", "Aucun fichier de données annuelles à afficher.")

        # Populer la liste des variables mensuelles
        self.monthly_variable_list.clear()
        self._monthly_files_map = monthly_files_map
        if monthly_files_map:
            sorted_keys = sorted(monthly_files_map.keys())
            for display_name in sorted_keys:
                item = QListWidgetItem(display_name)
                self.monthly_variable_list.addItem(item)
            # Sélectionner le premier élément par défaut pour l'afficher
            if self.monthly_variable_list.count() > 0:
                self.monthly_variable_list.setCurrentRow(0)
                self.on_monthly_item_selected(self.monthly_variable_list.currentItem())
        else:
            self.monthly_data_table.clearContents()
            self.monthly_data_table.setRowCount(0)
            self.monthly_data_table.setColumnCount(0)
            QMessageBox.information(self, "Données Mensuelles", "Aucun fichier de données mensuelles à afficher.")

    def on_monthly_item_selected(self, item):
        """Charge et affiche le fichier mensuel sélectionné dans le tableau."""
        if item:
            display_name = item.text()
            file_path = self._monthly_files_map.get(display_name)
            if file_path and os.path.exists(file_path):
                try:
                    df_monthly = pd.read_csv(file_path)
                    self.display_dataframe_in_table(self.monthly_data_table, df_monthly)
                except Exception as e:
                    QMessageBox.warning(self, "Erreur de chargement", f"Impossible de charger le tableau mensuel pour '{display_name}': {e}")
                    self.monthly_data_table.clearContents()
                    self.monthly_data_table.setRowCount(0)
                    self.monthly_data_table.setColumnCount(0)
            else:
                QMessageBox.warning(self, "Fichier Manquant", f"Le fichier pour '{display_name}' est introuvable ou invalide.")
                self.monthly_data_table.clearContents()
                self.monthly_data_table.setRowCount(0)
                self.monthly_data_table.setColumnCount(0)


# --- Fenêtre Principale de l'Application (Dashboard) ---

class MainWindow(QWidget):
    """
    La fenêtre principale de l'application, fonctionnant comme un tableau de bord
    avec un menu latéral et des pages interchangeables.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dashboard d'Analyse Climatique")
        self.setGeometry(100, 100, 1200, 800) # Taille plus grande pour un dashboard

        self.worker_thread = None # Référence au thread de travail en arrière-plan

        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        """Configure la disposition et les widgets de la fenêtre principale du dashboard."""
        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0) # Pas de marges pour le layout principal
        self.setLayout(self.main_layout)

        # --- Menu Latéral (Sidebar) ---
        self.sidebar_frame = QFrame()
        self.sidebar_frame.setObjectName("sidebarFrame")
        self.sidebar_frame.setFixedWidth(200)
        self.sidebar_layout = QVBoxLayout()
        self.sidebar_layout.setContentsMargins(10, 20, 10, 10)
        self.sidebar_layout.setSpacing(10)
        self.sidebar_frame.setLayout(self.sidebar_layout)

        # Appliquer l'effet d'ombre au cadre latéral
        shadow_sidebar = QGraphicsDropShadowEffect(self)
        shadow_sidebar.setBlurRadius(20)
        shadow_sidebar.setColor(QColor(0, 0, 0, 90)) # Ombre noire, 90 alpha (légèrement plus sombre pour le côté)
        shadow_sidebar.setOffset(3, 0) # Ombre décalée vers la droite
        self.sidebar_frame.setGraphicsEffect(shadow_sidebar)

        # Logo/Title in sidebar
        app_title = QLabel("Analyse Climatique")
        app_title.setFont(QFont("Roboto", 14, QFont.Weight.Bold))
        app_title.setStyleSheet("color: white; margin-bottom: 20px;")
        app_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sidebar_layout.addWidget(app_title)

        # Navigation Buttons
        self.btn_home = QPushButton("Accueil")
        self.btn_home.setIcon(QIcon(os.path.join(os.path.dirname(__file__), "icons", "home_icon.png")))
        self.btn_home.setObjectName("sidebarButton")
        self.btn_home.clicked.connect(lambda: self.switch_page(self.home_page, self.btn_home))
        self.sidebar_layout.addWidget(self.btn_home)

        self.btn_input = QPushButton("Données & Configuration")
        self.btn_input.setIcon(QIcon(os.path.join(os.path.dirname(__file__), "icons", "data_icon.png")))
        self.btn_input.setObjectName("sidebarButton")
        self.btn_input.clicked.connect(lambda: self.switch_page(self.input_page, self.btn_input))
        self.sidebar_layout.addWidget(self.btn_input)
        
        self.btn_preview = QPushButton("Aperçu du Tableau")
        self.btn_preview.setIcon(QIcon(os.path.join(os.path.dirname(__file__), "icons", "preview_icon.png")))
        self.btn_preview.setObjectName("sidebarButton")
        self.btn_preview.clicked.connect(lambda: self.switch_page(self.preview_page, self.btn_preview))
        self.sidebar_layout.addWidget(self.btn_preview)

        self.btn_results = QPushButton("Logs & Téléchargements") # Renommé
        self.btn_results.setIcon(QIcon(os.path.join(os.path.dirname(__file__), "icons", "results_icon.png")))
        self.btn_results.setObjectName("sidebarButton")
        self.btn_results.clicked.connect(lambda: self.switch_page(self.results_page, self.btn_results))
        self.sidebar_layout.addWidget(self.btn_results)
        
        # Nouveau bouton pour les tableaux
        self.btn_data_tables = QPushButton("Tableaux de Résultats")
        self.btn_data_tables.setIcon(QIcon(os.path.join(os.path.dirname(__file__), "icons", "table_icon.png"))) # Nouvelle icône
        self.btn_data_tables.setObjectName("sidebarButton")
        self.btn_data_tables.clicked.connect(lambda: self.switch_page(self.data_table_page, self.btn_data_tables))
        self.sidebar_layout.addWidget(self.btn_data_tables)


        self.sidebar_layout.addStretch() # Push buttons to the top

        self.main_layout.addWidget(self.sidebar_frame)

        # --- Contenu Principal (Stacked Widget) ---
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)

        # Appliquer l'effet d'ombre au contenu principal
        shadow_content = QGraphicsDropShadowEffect(self)
        shadow_content.setBlurRadius(20)
        shadow_content.setColor(QColor(0, 0, 0, 80)) # Ombre noire, 80 alpha
        shadow_content.setOffset(2, 2) # Ombre décalée vers le bas et la droite
        self.stacked_widget.setGraphicsEffect(shadow_content)


        self.home_page = HomePage()
        self.input_page = InputPage()
        self.preview_page = PreviewPage()
        self.results_page = ResultsPage()
        self.data_table_page = DataTablePage() # Instanciation de la nouvelle page

        self.stacked_widget.addWidget(self.home_page)
        self.stacked_widget.addWidget(self.input_page)
        self.stacked_widget.addWidget(self.preview_page)
        self.stacked_widget.addWidget(self.results_page)
        self.stacked_widget.addWidget(self.data_table_page) # Ajout de la nouvelle page

        # Connect signals from InputPage to MainWindow for actions
        self.input_page.file_selected.connect(self.handle_input_actions)
        
        # Connect home page tiles to switch pages
        self.home_page.tile_config.clicked.connect(lambda: self.switch_page(self.input_page, self.btn_input))
        self.home_page.tile_analyze.clicked.connect(lambda: self.switch_page(self.input_page, self.btn_input)) # La tuile "Analyse" peut aussi pointer vers InputPage pour lancer
        self.home_page.tile_results.clicked.connect(lambda: self.switch_page(self.results_page, self.btn_results))


        # Set initial page and mark button as checked
        self.current_sidebar_button = self.btn_home # Keep track of the currently active button
        self.switch_page(self.home_page, self.btn_home) # Set initial page

    def switch_page(self, page_widget, button):
        """Change la page affichée et met à jour le style du bouton latéral actif."""
        # Désélectionner l'ancien bouton
        if self.current_sidebar_button:
            self.current_sidebar_button.setChecked(False)
        
        # Sélectionner le nouveau bouton
        button.setChecked(True)
        self.current_sidebar_button = button
        
        self.stacked_widget.setCurrentWidget(page_widget)


    def apply_styles(self):
        """Applique des styles CSS modernes à toute l'application."""
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#F5F7FA")) # Light background for main window
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        # Créer un dossier 'icons' et y placer des icônes factices si elles n'existent pas.
        icon_dir = os.path.join(os.path.dirname(__file__), "icons")
        os.makedirs(icon_dir, exist_ok=True)
        
        dummy_icon_paths = {
            "home_icon.png": Qt.GlobalColor.blue,
            "data_icon.png": Qt.GlobalColor.green,
            "preview_icon.png": Qt.GlobalColor.red,
            "results_icon.png": Qt.GlobalColor.yellow,
            "chart_icon.png": Qt.GlobalColor.magenta, # Pour les tuiles d'accueil
            "report_icon.png": Qt.GlobalColor.cyan,   # Pour les tuiles d'accueil
            "table_icon.png": Qt.GlobalColor.darkYellow # Nouvelle icône pour les tables
        }
        for icon_file, color in dummy_icon_paths.items():
            path = os.path.join(icon_dir, icon_file)
            if not os.path.exists(path):
                pixmap = QPixmap(32, 32)
                pixmap.fill(Qt.GlobalColor.transparent) # Fond transparent
                painter = QPainter(pixmap)
                painter.setBrush(color) # Couleur de l'icône
                painter.drawEllipse(4, 4, 24, 24) # Un cercle simple
                painter.end()
                pixmap.save(path)


        self.setStyleSheet("""
            QWidget {
                font-family: 'Roboto', 'Segoe UI', sans-serif;
                font-size: 10pt;
                color: #34495E; /* Dark blue-grey for general text */
            }

            /* Sidebar Styling */
            QFrame#sidebarFrame {
                background-color: #2C3E50; /* Darker blue-grey for sidebar */
                border-right: 1px solid #1E2B38;
            }

            QPushButton#sidebarButton {
                background-color: transparent;
                color: #ECF0F1; /* Light grey text */
                border: none;
                padding: 12px 10px;
                text-align: left;
                font-weight: bold;
                border-radius: 5px;
                qproperty-iconSize: 20px 20px;
                qproperty-checkable: true; 
            }
            QPushButton#sidebarButton:hover {
                background-color: #34495E; /* Slightly lighter on hover */
            }
            QPushButton#sidebarButton:checked {
                background-color: #42A5F5; /* Blue 400 */
                border-left: 3px solid #BBDEFB; /* Light Blue 100 */
            }

            /* Main Content Area Styling */
            QStackedWidget {
                background-color: #FDFEFE; /* Almost white */
                border-radius: 8px;
                margin: 10px;
                padding: 10px;
                border: 1px solid #E0E0E0; /* Light grey border */
            }
            
            /* Home Page Dashboard Tiles Styling */
            QPushButton#dashboardTile {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 20px; /* Increased padding */
                text-align: center;
                color: #34495E; /* Default text color for content inside tile */
            }
            QPushButton#dashboardTile:hover {
                border: 1px solid #42A5F5; /* Highlight on hover */
                background-color: #F8F8F8; /* Slight background change on hover */
            }
            QPushButton#dashboardTile:pressed {
                background-color: #E6EEF4; /* Even lighter background on click */
                border: 1px solid #1976D2; /* Darker blue border on click */
            }


            /* Input Page specific styles */
            QLineEdit {
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
                selection-background-color: #BBDEFB;
            }
            QLineEdit:focus {
                border: 1px solid #42A5F5;
            }

            QPushButton#actionButton {
                background-color: #1976D2; /* Deep Blue */
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 15px;
                font-weight: bold;
                min-width: 120px;
                margin-left: 10px;
            }
            QPushButton#actionButton:hover {
                background-color: #145DA0; /* Darker Blue on hover */
            }
            QPushButton#actionButton:disabled {
                background-color: #A0A0A0; /* Grey when disabled */
                color: #EDEDED;
            }
            
            /* Style pour le bouton "Suggérer" */
            QPushButton#suggestButton {
                background-color: #607D8B; /* Blue Grey 500 */
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 12px;
                font-weight: normal;
                min-width: 80px;
            }
            QPushButton#suggestButton:hover {
                background-color: #455A64; /* Darker Blue Grey on hover */
            }
            QPushButton#suggestButton:disabled {
                background-color: #A0A0A0;
                color: #EDEDED;
            }

            /* Download Buttons Specific Styling */
            QPushButton#downloadButtonAnnual {
                background-color: #28A745; /* Green for annual */
                color: white;
                border-radius: 5px;
                padding: 8px 12px;
                font-weight: bold;
                text-align: center;
            }
            QPushButton#downloadButtonAnnual:hover {
                background-color: #218838;
            }

            QPushButton#downloadButtonMonthly {
                background-color: #17A2B8; /* Info blue for monthly */
                color: white;
                border-radius: 5px;
                padding: 6px 10px;
                font-weight: normal;
                text-align: center;
            }
            QPushButton#downloadButtonMonthly:hover {
                background-color: #138496;
            }

            QMessageBox {
                background-color: #F8F9FA;
                color: #34495E;
                font-size: 10pt;
            }
            QMessageBox QPushButton {
                background-color: #1976D2;
                color: white;
                border-radius: 4px;
                padding: 5px 10px;
            }
            QMessageBox QPushButton:hover {
                background-color: #145DA0;
            }
        """)

    def handle_input_actions(self, data):
        """
        Gère les signaux de la page d'entrée pour lancer l'aperçu ou l'analyse.
        Le dictionnaire 'data' contient le type d'action et les chemins.
        """
        action_type = data["action"]
        excel_path = data["path"]
        sheet_name = data["sheet"]

        if action_type == "preview":
            self.show_table_preview(excel_path, sheet_name)
        elif action_type == "calculate":
            self.start_analysis(excel_path, sheet_name)

    def show_table_preview(self, excel_path, sheet_name):
        """
        Récupère les données d'entrée et demande à la PreviewPage de charger et afficher l'aperçu.
        Puis passe à la page d'aperçu.
        """
        self.preview_page.load_preview(excel_path, sheet_name)
        self.switch_page(self.preview_page, self.btn_preview) # Passe à la page d'aperçu


    def start_analysis(self, excel_path, sheet_name):
        """
        Lance l'analyse climatique dans un thread séparé.
        Passe à la page des résultats et met à jour son état.
        """
        # Préparer la page des résultats et démarrer le thread
        self.results_page.clear_download_links() # Effacer les anciens résultats de téléchargement
        self.results_page.log_text_edit.clear() # Effacer les logs
        self.results_page.progress_bar.setValue(0) # Réinitialiser la barre de progression
        self.results_page.status_label.setText("Statut: Préparation des calculs...")
        
        # Effacer les contenus des tableaux de la page DataTablePage (si des données précédentes y étaient)
        self.data_table_page.annual_table.clearContents()
        self.data_table_page.annual_table.setRowCount(0)
        self.data_table_page.annual_table.setColumnCount(0)
        self.data_table_page.monthly_variable_list.clear()
        self.data_table_page.monthly_data_table.clearContents()
        self.data_table_page.monthly_data_table.setRowCount(0)
        self.data_table_page.monthly_data_table.setColumnCount(0)

        self.switch_page(self.results_page, self.btn_results) # Passer à la page des logs et téléchargements

        # Désactiver les contrôles d'entrée et de calcul pendant l'analyse
        self.input_page.excel_path_input.setEnabled(False)
        self.input_page.sheet_name_input.setEnabled(False)
        self.input_page.preview_btn.setEnabled(False)
        self.input_page.calculate_btn.setEnabled(False)
        self.input_page.findChild(QPushButton, "suggestButton").setEnabled(False) 

        # Créer et démarrer le thread de travail
        self.worker_thread = WorkerThread(excel_path, sheet_name)
        self.worker_thread.log_message.connect(self.results_page.append_log)
        self.worker_thread.status_update.connect(self.results_page.update_status)
        self.worker_thread.finished.connect(self.on_calculation_finished)
        self.worker_thread.start()

    def on_calculation_finished(self, results_dict):
        """
        Slot connecté au signal 'finished' de WorkerThread.
        Met à jour la page des résultats et réactive les contrôles d'entrée.
        """
        annual_file = results_dict.get('annual_file')
        monthly_files_map = results_dict.get('monthly_files_map', {})
        
        # Mettre à jour la page des téléchargements
        self.results_page.set_download_content(annual_file, monthly_files_map)
        
        # Mettre à jour la nouvelle page des tableaux de résultats
        self.data_table_page.load_data_and_display(annual_file, monthly_files_map)

        # Réactiver les contrôles d'entrée et de calcul
        self.input_page.excel_path_input.setEnabled(True)
        self.input_page.sheet_name_input.setEnabled(True)
        self.input_page.preview_btn.setEnabled(True)
        self.input_page.calculate_btn.setEnabled(True)
        self.input_page.findChild(QPushButton, "suggestButton").setEnabled(True)

        # Nettoyer le thread de travail
        if self.worker_thread:
            self.worker_thread.quit() # Demander au thread de quitter
            self.worker_thread.wait() # Attendre que le thread se termine proprement
            self.worker_thread = None # Effacer la référence

# --- Exécution Principale de l'Application ---

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Assurez-vous d'avoir un dossier 'icons' dans le même répertoire que le script.
    # Le code créera des icônes factices si elles n'existent pas.
    icon_dir = os.path.join(os.path.dirname(__file__), "icons")
    os.makedirs(icon_dir, exist_ok=True)
    
    # Créer des icônes factices si elles manquent
    dummy_icon_specs = {
        "home_icon.png": Qt.GlobalColor.blue,
        "data_icon.png": Qt.GlobalColor.green,
        "preview_icon.png": Qt.GlobalColor.red,
        "results_icon.png": Qt.GlobalColor.yellow,
        "chart_icon.png": Qt.GlobalColor.magenta,
        "report_icon.png": Qt.GlobalColor.cyan,
        "table_icon.png": Qt.GlobalColor.darkYellow # Nouvelle icône
    }
    for icon_file, color in dummy_icon_specs.items():
        path = os.path.join(icon_dir, icon_file)
        if not os.path.exists(path):
            pixmap = QPixmap(32, 32)
            pixmap.fill(Qt.GlobalColor.transparent) # Fond transparent
            painter = QPainter(pixmap)
            painter.setBrush(color) # Couleur de l'icône
            painter.drawEllipse(4, 4, 24, 24) # Un cercle simple
            painter.end()
            pixmap.save(path)


    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec())
