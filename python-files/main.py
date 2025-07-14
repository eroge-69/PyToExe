import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QPushButton, QLineEdit, QLabel, QTextEdit, 
                             QProgressBar, QComboBox, QSpinBox, QGroupBox, QGridLayout,
                             QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog,
                             QMessageBox, QTabWidget, QCheckBox, QSplitter)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor
import pandas as pd
from datetime import datetime


class GoogleMapsScraperUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.scraped_data = []
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Google Maps Scraper - Extracteur de Données")
        self.setGeometry(100, 100, 1200, 800)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        
        # Titre de l'application
        title_label = QLabel("Google Maps Scraper")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)
        
        # Splitter pour diviser l'interface
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Panel de gauche - Configuration
        left_panel = self.create_config_panel()
        splitter.addWidget(left_panel)
        
        # Panel de droite - Résultats
        right_panel = self.create_results_panel()
        splitter.addWidget(right_panel)
        
        # Définir les proportions du splitter
        splitter.setSizes([400, 800])
        
        # Barre de statut
        self.statusBar().showMessage("Prêt à scraper Google Maps")
        
        # Appliquer le style
        self.apply_style()
        
    def create_config_panel(self):
        """Créer le panel de configuration à gauche"""
        config_widget = QWidget()
        config_layout = QVBoxLayout(config_widget)
        
        # Groupe de recherche
        search_group = QGroupBox("Paramètres de Recherche")
        search_layout = QGridLayout(search_group)
        
        # Mots-clés de recherche
        search_layout.addWidget(QLabel("Mots-clés:"), 0, 0)
        self.keywords_input = QLineEdit()
        self.keywords_input.setPlaceholderText("Ex: restaurants, hôtels, garages...")
        search_layout.addWidget(self.keywords_input, 0, 1)
        
        # Localisation
        search_layout.addWidget(QLabel("Localisation:"), 1, 0)
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("Ex: Paris, France")
        search_layout.addWidget(self.location_input, 1, 1)
        
        # Nombre de résultats
        search_layout.addWidget(QLabel("Nombre max:"), 2, 0)
        self.max_results_spin = QSpinBox()
        self.max_results_spin.setRange(10, 1000)
        self.max_results_spin.setValue(100)
        search_layout.addWidget(self.max_results_spin, 2, 1)
        
        config_layout.addWidget(search_group)
        
        # Groupe de configuration avancée
        advanced_group = QGroupBox("Configuration Avancée")
        advanced_layout = QGridLayout(advanced_group)
        
        # Utiliser des proxies
        self.use_proxy_checkbox = QCheckBox("Utiliser des proxies")
        advanced_layout.addWidget(self.use_proxy_checkbox, 0, 0, 1, 2)
        
        # Proxy
        advanced_layout.addWidget(QLabel("Proxy:"), 1, 0)
        self.proxy_input = QLineEdit()
        self.proxy_input.setPlaceholderText("IP:Port ou laisser vide")
        self.proxy_input.setEnabled(False)
        advanced_layout.addWidget(self.proxy_input, 1, 1)
        
        # Délai entre requêtes
        advanced_layout.addWidget(QLabel("Délai (sec):"), 2, 0)
        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(1, 10)
        self.delay_spin.setValue(3)
        advanced_layout.addWidget(self.delay_spin, 2, 1)
        
        # Mode headless
        self.headless_checkbox = QCheckBox("Mode invisible (headless)")
        self.headless_checkbox.setChecked(True)
        advanced_layout.addWidget(self.headless_checkbox, 3, 0, 1, 2)
        
        config_layout.addWidget(advanced_group)
        
        # Connecter les événements
        self.use_proxy_checkbox.toggled.connect(self.proxy_input.setEnabled)
        
        # Boutons de contrôle
        buttons_layout = QVBoxLayout()
        
        self.start_button = QPushButton("Démarrer le Scraping")
        self.start_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; padding: 10px; }")
        self.start_button.clicked.connect(self.start_scraping)
        buttons_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Arrêter")
        self.stop_button.setStyleSheet("QPushButton { background-color: #f44336; color: white; font-weight: bold; padding: 10px; }")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_scraping)
        buttons_layout.addWidget(self.stop_button)
        
        self.export_button = QPushButton("Exporter les Données")
        self.export_button.setStyleSheet("QPushButton { background-color: #2196F3; color: white; font-weight: bold; padding: 10px; }")
        self.export_button.clicked.connect(self.export_data)
        buttons_layout.addWidget(self.export_button)
        
        config_layout.addLayout(buttons_layout)
        
        # Barre de progression
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        config_layout.addWidget(self.progress_bar)
        
        # Espace flexible
        config_layout.addStretch()
        
        return config_widget
        
    def create_results_panel(self):
        """Créer le panel des résultats à droite"""
        results_widget = QWidget()
        results_layout = QVBoxLayout(results_widget)
        
        # Onglets pour les résultats
        self.tabs = QTabWidget()
        results_layout.addWidget(self.tabs)
        
        # Onglet tableau de données
        self.create_data_table_tab()
        
        # Onglet logs
        self.create_logs_tab()
        
        return results_widget
        
    def create_data_table_tab(self):
        """Créer l'onglet du tableau de données"""
        data_tab = QWidget()
        data_layout = QVBoxLayout(data_tab)
        
        # Informations sur les données
        info_layout = QHBoxLayout()
        self.data_count_label = QLabel("Données extraites: 0")
        self.data_count_label.setStyleSheet("font-weight: bold; color: #2196F3;")
        info_layout.addWidget(self.data_count_label)
        info_layout.addStretch()
        
        # Bouton de rafraîchissement
        refresh_button = QPushButton("Actualiser")
        refresh_button.clicked.connect(self.refresh_table)
        info_layout.addWidget(refresh_button)
        
        data_layout.addLayout(info_layout)
        
        # Tableau des données
        self.data_table = QTableWidget()
        self.setup_data_table()
        data_layout.addWidget(self.data_table)
        
        self.tabs.addTab(data_tab, "Données Extraites")
        
    def create_logs_tab(self):
        """Créer l'onglet des logs"""
        logs_tab = QWidget()
        logs_layout = QVBoxLayout(logs_tab)
        
        # Zone de texte pour les logs
        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        self.logs_text.setStyleSheet("background-color: #f5f5f5; font-family: Consolas, monospace;")
        logs_layout.addWidget(self.logs_text)
        
        # Bouton pour effacer les logs
        clear_logs_button = QPushButton("Effacer les Logs")
        clear_logs_button.clicked.connect(self.clear_logs)
        logs_layout.addWidget(clear_logs_button)
        
        self.tabs.addTab(logs_tab, "Logs")
        
    def setup_data_table(self):
        """Configurer le tableau de données"""
        columns = ["Nom", "Adresse", "Téléphone", "Site Web", "Note", "Nb Avis", "Catégorie"]
        self.data_table.setColumnCount(len(columns))
        self.data_table.setHorizontalHeaderLabels(columns)
        
        # Ajuster la largeur des colonnes
        header = self.data_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Nom
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Adresse
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Téléphone
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Site Web
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Note
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Nb Avis
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Catégorie
        
    def apply_style(self):
        """Appliquer le style à l'application"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QLineEdit, QSpinBox {
                padding: 5px;
                border: 1px solid #cccccc;
                border-radius: 3px;
            }
            QLineEdit:focus, QSpinBox:focus {
                border: 2px solid #2196F3;
            }
            QPushButton {
                padding: 8px;
                border: none;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                opacity: 0.8;
            }
            QPushButton:pressed {
                opacity: 0.6;
            }
            QTableWidget {
                gridline-color: #cccccc;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #e0e0e0;
                padding: 5px;
                border: 1px solid #cccccc;
                font-weight: bold;
            }
        """)
        
    def log_message(self, message):
        """Ajouter un message aux logs"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.logs_text.append(formatted_message)
        
    def clear_logs(self):
        """Effacer les logs"""
        self.logs_text.clear()
        
    def refresh_table(self):
        """Actualiser le tableau avec les données"""
        self.data_table.setRowCount(len(self.scraped_data))
        
        for row, data in enumerate(self.scraped_data):
            self.data_table.setItem(row, 0, QTableWidgetItem(data.get('nom', '')))
            self.data_table.setItem(row, 1, QTableWidgetItem(data.get('adresse', '')))
            self.data_table.setItem(row, 2, QTableWidgetItem(data.get('telephone', '')))
            self.data_table.setItem(row, 3, QTableWidgetItem(data.get('site_web', '')))
            self.data_table.setItem(row, 4, QTableWidgetItem(str(data.get('note', ''))))
            self.data_table.setItem(row, 5, QTableWidgetItem(str(data.get('nb_avis', ''))))
            self.data_table.setItem(row, 6, QTableWidgetItem(data.get('categorie', '')))
            
        self.data_count_label.setText(f"Données extraites: {len(self.scraped_data)}")
        
    def start_scraping(self):
        """Démarrer le processus de scraping"""
        keywords = self.keywords_input.text().strip()
        location = self.location_input.text().strip()
        
        if not keywords or not location:
            QMessageBox.warning(self, "Attention", "Veuillez remplir les mots-clés et la localisation.")
            return
            
        self.log_message(f"Démarrage du scraping pour '{keywords}' à '{location}'")
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Barre de progression indéterminée
        
        # TODO: Intégrer le moteur de scraping ici
        self.log_message("Moteur de scraping en cours de développement...")
        
        # Simulation de données pour l'interface
        self.simulate_scraping()
        
    def simulate_scraping(self):
        """Simuler le processus de scraping pour tester l'interface"""
        # Données d'exemple
        sample_data = [
            {
                'nom': 'Restaurant Le Gourmet',
                'adresse': '123 Rue de la Paix, 75001 Paris',
                'telephone': '01 42 86 87 88',
                'site_web': 'www.legourmet.fr',
                'note': '4.5',
                'nb_avis': '156',
                'categorie': 'Restaurant français'
            },
            {
                'nom': 'Café Central',
                'adresse': '45 Avenue des Champs-Élysées, 75008 Paris',
                'telephone': '01 43 59 60 61',
                'site_web': 'www.cafecentral.fr',
                'note': '4.2',
                'nb_avis': '89',
                'categorie': 'Café'
            }
        ]
        
        # Ajouter les données simulées
        self.scraped_data.extend(sample_data)
        self.refresh_table()
        self.log_message(f"Ajout de {len(sample_data)} établissements")
        
        # Arrêter la simulation
        QTimer.singleShot(3000, self.stop_scraping)
        
    def stop_scraping(self):
        """Arrêter le processus de scraping"""
        self.log_message("Arrêt du scraping")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setVisible(False)
        
    def export_data(self):
        """Exporter les données vers un fichier"""
        if not self.scraped_data:
            QMessageBox.information(self, "Information", "Aucune donnée à exporter.")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Exporter les données", 
            f"google_maps_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV Files (*.csv);;Excel Files (*.xlsx);;JSON Files (*.json)"
        )
        
        if file_path:
            try:
                df = pd.DataFrame(self.scraped_data)
                
                if file_path.endswith('.csv'):
                    df.to_csv(file_path, index=False, encoding='utf-8')
                elif file_path.endswith('.xlsx'):
                    df.to_excel(file_path, index=False)
                elif file_path.endswith('.json'):
                    df.to_json(file_path, orient='records', indent=2, force_ascii=False)
                    
                self.log_message(f"Données exportées vers: {file_path}")
                QMessageBox.information(self, "Succès", f"Données exportées avec succès vers:\n{file_path}")
                
            except Exception as e:
                self.log_message(f"Erreur lors de l'exportation: {str(e)}")
                QMessageBox.critical(self, "Erreur", f"Erreur lors de l'exportation:\n{str(e)}")


def main():
    app = QApplication(sys.argv)
    
    # Définir l'icône de l'application (optionnel)
    app.setApplicationName("Google Maps Scraper")
    app.setApplicationVersion("1.0")
    
    window = GoogleMapsScraperUI()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

