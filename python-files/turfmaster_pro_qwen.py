# ---- ui.py ----
"""
ui.py - Interface utilisateur pour le modèle M3+ Version 3.1

Cette interface présente les résultats avec une transparence scientifique rigoureuse,
mettant en avant les insights Arioneo sur la vitesse en course et la gestion de l'incertitude.

Conformément à la Version 3.1 du modèle M3+ :
1. L'interface reconnaît explicitement les limites des théories et les exceptions observées
2. Les visualisations mettent en avant les profils de vitesse et les patterns de course
3. Le niveau de confiance est affiché explicitement avec des explications
4. Les paris sont présentés avec leur edge ajusté par l'incertitude
"""

import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QTableWidget, QTableWidgetItem,
                            QSplitter, QGroupBox, QScrollArea, QComboBox, QCheckBox,
                            QProgressBar, QFrame, QSizePolicy, QStackedWidget)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor, QPalette, QBrush, QLinearGradient
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from database import DatabaseManager
from features import FeatureEngineer
from training import ModelTrainer
from risk_management import BankrollManager
from updaters import ContextualDriftMonitor
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SpeedProfileCanvas(FigureCanvas):
    """Canvas pour visualiser les profils de vitesse avec insights Arioneo"""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)
        self.setParent(parent)
        
        fig.tight_layout()
        self.compute_initial_figure()
    
    def compute_initial_figure(self):
        """Initialise avec un graphique vide"""
        self.axes.clear()
        self.axes.set_title('Profil de vitesse (km/h)')
        self.axes.set_xlabel('Distance (m)')
        self.axes.set_ylabel('Vitesse')
        self.axes.grid(True, linestyle='--', alpha=0.7)
        self.draw()
    
    def plot_speed_profile(self, speed_profile: np.ndarray, distance_m: int, 
                          race_style: str = "standard", vincennes_layout: bool = False):
        """
        Affiche le profil de vitesse avec annotations Arioneo
        
        Args:
            speed_profile: Profil de vitesse en m/s
            distance_m: Distance de la course en mètres
            race_style: Style de course détecté
            vincennes_layout: Si le tracé est celui de Vincennes
        """
        self.axes.clear()
        
        # Convertir en km/h
        speed_kmh = speed_profile * 3.6
        
        # Créer les points x (distance)
        x = np.linspace(0, distance_m, len(speed_kmh))
        
        # Tracer le profil de vitesse
        self.axes.plot(x, speed_kmh, 'b-', linewidth=2.5)
        
        # Ajouter des lignes verticales pour les segments clés
        segments = [
            ('Début course', 0),
            ('Milieu course', distance_m/2),
            ('Derniers 600m', distance_m-600),
            ('Derniers 400m', distance_m-400),
            ('Derniers 200m', distance_m-200),
            ('Arrivée', distance_m)
        ]
        
        for label, pos in segments:
            if 0 <= pos <= distance_m:
                self.axes.axvline(x=pos, color='gray', linestyle='--', alpha=0.5)
                if label != 'Début course' and label != 'Arrivée':
                    self.axes.text(pos, max(speed_kmh)*0.95, label, 
                                  ha='center', rotation=90, fontsize=8)
        
        # Ajouter des annotations selon le style de course
        if race_style == "early_speed":
            self.axes.axvspan(0, distance_m-600, facecolor='red', alpha=0.1)
            self.axes.text(distance_m*0.25, max(speed_kmh)*0.8, 
                          "Départ rapide\nRisque de décélération", 
                          ha='center', color='red', fontsize=9)
        elif race_style == "late_finisher":
            self.axes.axvspan(distance_m-400, distance_m, facecolor='green', alpha=0.1)
            self.axes.text(distance_m*0.85, max(speed_kmh)*0.8, 
                          "Accélération tardive\nAvantage stratégique", 
                          ha='center', color='green', fontsize=9)
        
        # Ajouter des annotations spécifiques à Vincennes
        if vincennes_layout:
            self.axes.text(distance_m*0.1, max(speed_kmh)*0.2, 
                          "Virages serrés\n+11% de temps vs ligne droite", 
                          ha='left', color='purple', fontsize=9,
                          bbox=dict(facecolor='white', alpha=0.7, edgecolor='purple'))
        
        # Configurer le graphique
        self.axes.set_title(f'Profil de vitesse - {distance_m}m')
        self.axes.set_xlabel('Distance (m)')
        self.axes.set_ylabel('Vitesse (km/h)')
        self.axes.grid(True, linestyle='--', alpha=0.7)
        
        self.draw()

class ConfidenceIndicator(QWidget):
    """Indicateur visuel du niveau de confiance du modèle"""
    
    def __init__(self, confidence: float = 0.5, parent=None):
        super().__init__(parent)
        self.confidence = confidence
        self.setMinimumSize(200, 30)
    
    def paintEvent(self, event):
        from PyQt5.QtGui import QPainter, QLinearGradient, QBrush, QColor, QPen
        from PyQt5.QtCore import QRectF
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Fond avec dégradé
        gradient = QLinearGradient(0, 0, self.width(), 0)
        gradient.setColorAt(0, QColor(255, 100, 100))  # Rouge pour faible confiance
        gradient.setColorAt(0.5, QColor(255, 200, 100))  # Orange pour confiance moyenne
        gradient.setColorAt(1, QColor(100, 200, 100))  # Vert pour haute confiance
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 5, 5)
        
        # Barre de confiance
        confidence_width = int(self.width() * self.confidence)
        painter.setBrush(QColor(50, 50, 50, 100))
        painter.setPen(QPen(QColor(30, 30, 30), 1))
        painter.drawRoundedRect(0, 0, confidence_width, self.height(), 3, 3)
        
        # Texte
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(self.font())
        confidence_text = f"Confiance: {self.confidence:.0%}"
        text_rect = painter.fontMetrics().boundingRect(confidence_text)
        painter.drawText(
            (self.width() - text_rect.width()) // 2,
            (self.height() + text_rect.height() // 2) // 2,
            confidence_text
        )
        
        painter.end()

class TheoryValidationWidget(QWidget):
    """Widget affichant la validation des théories Arioneo"""
    
    def __init__(self, theory_validator, race_id, parent=None):
        super().__init__(parent)
        self.theory_validator = theory_validator
        self.race_id = race_id
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Titre
        title = QLabel("Validation des théories Arioneo")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(10)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Si pas de données
        if not self.race_id:
            layout.addWidget(QLabel("Sélectionnez une course pour voir la validation des théories"))
            self.setLayout(layout)
            return
        
        # Récupérer les données de validation
        try:
            race_data = self.theory_validator.db.get_race_data(self.race_id)
            if not race_data:
                layout.addWidget(QLabel("Données de course non disponibles"))
                self.setLayout(layout)
                return
            
            # Identifier les exceptions
            exceptions = self.theory_validator.identify_exceptions(self.race_id)
            
            # Afficher le statut global
            theory_statuses = self.theory_validator.get_all_theory_statuses()
            valid_count = sum(1 for status in theory_statuses if status and status['weight'] > 0.6)
            total_count = len(theory_statuses)
            
            status_label = QLabel(f"{valid_count}/{total_count} théories validées pour cette course")
            status_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
            layout.addWidget(status_label)
            
            # Afficher chaque théorie
            for status in theory_statuses:
                if not status:
                    continue
                
                theory_group = QGroupBox(status['name'].replace('_', ' ').title())
                theory_layout = QVBoxLayout()
                
                # Description
                desc_label = QLabel(f"« {status['description']} »")
                desc_label.setWordWrap(True)
                desc_label.setStyleSheet("font-style: italic; color: #7f8c8d; margin-bottom: 5px;")
                theory_layout.addWidget(desc_label)
                
                # Statut
                status_layout = QHBoxLayout()
                
                # Poids visuel
                weight_bar = QProgressBar()
                weight_bar.setRange(0, 100)
                weight_bar.setValue(int(status['weight'] * 100))
                weight_bar.setTextVisible(False)
                weight_bar.setFixedHeight(10)
                
                # Couleur selon le poids
                if status['weight'] > 0.7:
                    weight_bar.setStyleSheet("QProgressBar {border: 1px solid grey; border-radius: 3px; text-align: center;}"
                                          "QProgressBar::chunk {background-color: #27ae60; width: 10px;}")
                elif status['weight'] > 0.4:
                    weight_bar.setStyleSheet("QProgressBar {border: 1px solid grey; border-radius: 3px; text-align: center;}"
                                          "QProgressBar::chunk {background-color: #f39c12; width: 10px;}")
                else:
                    weight_bar.setStyleSheet("QProgressBar {border: 1px solid grey; border-radius: 3px; text-align: center;}"
                                          "QProgressBar::chunk {background-color: #e74c3c; width: 10px;}")
                
                status_layout.addWidget(QLabel("Validité:"))
                status_layout.addWidget(weight_bar, 1)
                status_layout.addWidget(QLabel(f"{status['weight']:.0%}"))
                
                theory_layout.addLayout(status_layout)
                
                # Dernière validation
                if status['last_validation']:
                    last_val = status['last_validation'].strftime("%Y-%m-%d")
                    theory_layout.addWidget(QLabel(f"Dernière validation: {last_val}", 
                                                styleSheet="color: #7f8c8d; font-size: 9pt;"))
                
                # Exceptions pour cette théorie
                exception_count = 0
                for exception in exceptions:
                    if exception['theory'] == status['name']:
                        exception_count += len(exception['horses'])
                
                if exception_count > 0:
                    exception_label = QLabel(f"{exception_count} exception(s) identifiée(s) pour cette course")
                    exception_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
                    theory_layout.addWidget(exception_label)
                
                theory_group.setLayout(theory_layout)
                layout.addWidget(theory_group)
            
            # Afficher les exceptions si présentes
            if exceptions:
                exceptions_group = QGroupBox("Exceptions identifiées")
                exceptions_layout = QVBoxLayout()
                
                for exception in exceptions:
                    if exception['count'] > 0:
                        exc_label = QLabel(f"• {exception['description']} - {exception['count']} chevaux concernés")
                        exc_label.setWordWrap(True)
                        exc_label.setStyleSheet("color: #e74c3c;")
                        exceptions_layout.addWidget(exc_label)
                        
                        # Détails des chevaux
                        for horse in exception['horses'][:2]:  # Afficher seulement 2 chevaux pour ne pas surcharger
                            horse_label = QLabel(f"  - {horse['name']} (pos: {horse['position']}) : {horse['theory_prediction']}")
                            horse_label.setStyleSheet("font-size: 9pt; margin-left: 15px;")
                            exceptions_layout.addWidget(horse_label)
                        
                        if len(exception['horses']) > 2:
                            exceptions_layout.addWidget(QLabel(f"  ... et {len(exception['horses'])-2} autres", 
                                                            styleSheet="font-size: 9pt; margin-left: 15px;"))
                
                exceptions_group.setLayout(exceptions_layout)
                layout.addWidget(exceptions_group)
        
        except Exception as e:
            logger.error(f"Erreur lors de la validation des théories: {str(e)}")
            layout.addWidget(QLabel("Erreur lors de la validation des théories"))
        
        self.setLayout(layout)

class TurfMasterApp(QMainWindow):
    """Application principale avec interface scientifiquement rigoureuse"""
    
    def __init__(self, db_manager=None, feature_engineer=None, 
                model_trainer=None, bankroll_manager=None, 
                theory_validator=None, drift_monitor=None):
        super().__init__()
        self.setWindowTitle("TurfMaster Pro - Modèle M3+ Version 3.1")
        self.setGeometry(100, 100, 1400, 900)
        
        # Initialisation des modules
        self.db_manager = db_manager or DatabaseManager()
        self.feature_engineer = feature_engineer or FeatureEngineer()
        self.model_trainer = model_trainer or ModelTrainer(self.db_manager, theory_validator, None)
        self.bankroll_manager = bankroll_manager or BankrollManager()
        self.theory_validator = theory_validator
        self.drift_monitor = drift_monitor or ContextualDriftMonitor(self.db_manager, theory_validator)
        
        # Variables d'état
        self.current_race_id = None
        self.current_model_id = None
        self.current_confidence = 0.7
        
        self.init_ui()
        self.setup_styles()
    
    def setup_styles(self):
        """Configure les styles de l'application"""
        # Palette de couleurs inspirée des courses hippiques
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(245, 245, 245))
        palette.setColor(QPalette.WindowText, QColor(44, 62, 80))
        palette.setColor(QPalette.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.AlternateBase, QColor(240, 240, 240))
        palette.setColor(QPalette.ToolTipBase, QColor(44, 62, 80))
        palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
        palette.setColor(QPalette.Text, QColor(44, 62, 80))
        palette.setColor(QPalette.Button, QColor(52, 152, 219))
        palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.Highlight, QColor(52, 152, 219))
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        self.setPalette(palette)
        
        # Style sheet personnalisé
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QTabWidget::pane {
                border: 1px solid #dcdcdc;
                background: white;
            }
            QTabBar::tab {
                background: #e0e0e0;
                border: 1px solid #dcdcdc;
                padding: 8px 15px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom-color: white;
            }
            QGroupBox {
                border: 1px solid #dcdcdc;
                border-radius: 5px;
                margin-top: 1ex;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                background: white;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c6391;
            }
            QTableWidget {
                gridline-color: #e0e0e0;
                selection-background-color: #3498db;
            }
            QLabel.title {
                font-size: 16pt;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }
            QLabel.subtitle {
                font-size: 12pt;
                color: #34495e;
                margin: 5px 0;
            }
            QProgressBar {
                border: 1px solid grey;
                border-radius: 3px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                width: 10px;
            }
        """)
    
    def init_ui(self):
        """Initialise l'interface utilisateur"""
        # Créer un widget central avec splitter
        central_widget = QSplitter(Qt.Horizontal)
        
        # Panneau de gauche pour la navigation
        left_panel = self.create_left_panel()
        central_widget.addWidget(left_panel)
        
        # Panneau de droite pour le contenu
        self.right_panel = QStackedWidget()
        
        # Onglets principaux
        self.analysis_tab = self.create_analysis_tab()
        self.models_tab = self.create_models_tab()
        self.drift_monitor_tab = self.create_drift_monitor_tab()
        self.risk_management_tab = self.create_risk_management_tab()
        
        # Ajouter les onglets au stacked widget
        self.right_panel.addWidget(self.analysis_tab)
        self.right_panel.addWidget(self.models_tab)
        self.right_panel.addWidget(self.drift_monitor_tab)
        self.right_panel.addWidget(self.risk_management_tab)
        
        central_widget.addWidget(self.right_panel)
        central_widget.setSizes([200, 1200])
        
        self.setCentralWidget(central_widget)
        self.statusBar().showMessage("Prêt - Modèle M3+ Version 3.1")
    
    def create_left_panel(self):
        """Crée le panneau de navigation de gauche"""
        panel = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Logo et titre
        title = QLabel("TurfMaster Pro\nModèle M3+ 3.1")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title.setFont(title_font)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Boutons de navigation
        nav_buttons = [
            ("Analyse Course", 0),
            ("Gestion Modèles", 1),
            ("Monitoring Drift", 2),
            ("Gestion du Risque", 3)
        ]
        
        for text, index in nav_buttons:
            btn = QPushButton(text)
            btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
            btn.setMinimumHeight(40)
            btn.clicked.connect(lambda checked, idx=index: self.right_panel.setCurrentIndex(idx))
            layout.addWidget(btn)
        
        # Informations système
        system_group = QGroupBox("État du système")
        system_layout = QVBoxLayout()
        
        # Niveau de confiance global
        self.confidence_indicator = ConfidenceIndicator(self.current_confidence)
        system_layout.addWidget(self.confidence_indicator)
        
        # Statut des modèles
        self.models_status = QLabel("Modèles: Tous opérationnels")
        self.models_status.setWordWrap(True)
        system_layout.addWidget(self.models_status)
        
        # Alertes
        self.alerts_label = QLabel("Alertes: Aucune")
        self.alerts_label.setStyleSheet("color: #27ae60;")
        system_layout.addWidget(self.alerts_label)
        
        system_group.setLayout(system_layout)
        layout.addWidget(system_group)
        
        # Bouton de mise à jour
        update_btn = QPushButton("Vérifier les mises à jour")
        update_btn.setStyleSheet("background-color: #27ae60;")
        update_btn.clicked.connect(self.check_for_updates)
        layout.addWidget(update_btn)
        
        layout.addStretch()
        panel.setLayout(layout)
        return panel
    
    def create_analysis_tab(self):
        """Crée l'onglet d'analyse de course"""
        tab = QWidget()
        main_layout = QVBoxLayout()
        
        # Sélecteur de course
        race_selector = QGroupBox("Sélection de la course")
        race_layout = QHBoxLayout()
        
        # Sélecteur d'hippodrome
        hippodrome_combo = QComboBox()
        hippodrome_combo.addItems(["Vincennes", "Longchamp", "Deauville", "Chantilly", "Meydan"])
        race_layout.addWidget(QLabel("Hippodrome:"))
        race_layout.addWidget(hippodrome_combo, 1)
        
        # Sélecteur de distance
        distance_combo = QComboBox()
        distance_combo.addItems(["1600m", "2100m", "2700m", "2850m", "3600m"])
        race_layout.addWidget(QLabel("Distance:"))
        race_layout.addWidget(distance_combo, 1)
        
        # Bouton de sélection
        select_btn = QPushButton("Sélectionner")
        select_btn.clicked.connect(lambda: self.load_race(hippodrome_combo.currentText(), 
                                                        distance_combo.currentText()))
        race_layout.addWidget(select_btn)
        
        race_selector.setLayout(race_layout)
        main_layout.addWidget(race_selector)
        
        # Informations de course
        self.race_info = QLabel("Sélectionnez une course pour commencer l'analyse")
        self.race_info.setStyleSheet("font-weight: bold; color: #2c3e50; font-size: 14pt;")
        main_layout.addWidget(self.race_info)
        
        # Splitter pour le contenu principal
        content_splitter = QSplitter(Qt.Vertical)
        
        # Panneau supérieur: visualisation
        top_panel = QWidget()
        top_layout = QHBoxLayout()
        
        # Visualisation du profil de vitesse
        speed_group = QGroupBox("Profil de vitesse et stratégie")
        speed_layout = QVBoxLayout()
        
        self.speed_canvas = SpeedProfileCanvas(width=8, height=4, dpi=100)
        speed_layout.addWidget(self.speed_canvas)
        
        # Contrôles pour le profil de vitesse
        speed_controls = QHBoxLayout()
        self.race_style_combo = QComboBox()
        self.race_style_combo.addItems(["Standard", "Early Speed", "Late Finisher"])
        speed_controls.addWidget(QLabel("Style de course:"))
        speed_controls.addWidget(self.race_style_combo, 1)
        
        self.vincennes_check = QCheckBox("Tracé de Vincennes")
        self.vincennes_check.setChecked(True)
        speed_controls.addWidget(self.vincennes_check)
        
        speed_layout.addLayout(speed_controls)
        speed_group.setLayout(speed_layout)
        top_layout.addWidget(speed_group, 2)
        
        # Informations sur la confiance et les théories
        theory_panel = QWidget()
        theory_layout = QVBoxLayout()
        
        # Indicateur de confiance
        confidence_group = QGroupBox("Niveau de confiance du modèle")
        confidence_layout = QVBoxLayout()
        
        self.confidence_label = QLabel("Confiance: --")
        self.confidence_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: #2c3e50;")
        confidence_layout.addWidget(self.confidence_label)
        
        self.confidence_explanation = QLabel("Le niveau de confiance est calculé en fonction de la complétude des données, "
                                           "de la cohérence avec les théories établies et du nombre d'exceptions observées.")
        self.confidence_explanation.setWordWrap(True)
        confidence_layout.addWidget(self.confidence_explanation)
        
        confidence_group.setLayout(confidence_layout)
        theory_layout.addWidget(confidence_group)
        
        # Validation des théories
        self.theory_validation = TheoryValidationWidget(self.theory_validator, None)
        theory_layout.addWidget(self.theory_validation)
        
        theory_layout.addStretch()
        theory_panel.setLayout(theory_layout)
        
        top_layout.addWidget(theory_panel, 1)
        top_panel.setLayout(top_layout)
        content_splitter.addWidget(top_panel)
        
        # Panneau inférieur: résultats
        bottom_panel = QWidget()
        bottom_layout = QHBoxLayout()
        
        # Tableau des prédictions
        predictions_group = QGroupBox("Prédictions et paris")
        predictions_layout = QVBoxLayout()
        
        # Contrôles
        predictions_controls = QHBoxLayout()
        self.bet_type_combo = QComboBox()
        self.bet_type_combo.addItems(["Gagnant", "Placé", "Trio", "Quarté"])
        predictions_controls.addWidget(QLabel("Type de pari:"))
        predictions_controls.addWidget(self.bet_type_combo, 1)
        
        self.run_analysis_btn = QPushButton("Lancer l'analyse")
        self.run_analysis_btn.setStyleSheet("background-color: #27ae60; font-weight: bold;")
        self.run_analysis_btn.clicked.connect(self.run_full_analysis)
        self.run_analysis_btn.setEnabled(False)
        predictions_controls.addWidget(self.run_analysis_btn)
        
        predictions_layout.addLayout(predictions_controls)
        
        # Tableau
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(8)
        self.results_table.setHorizontalHeaderLabels([
            "Cheval ID", "Cote", "P(Win)", "Intervalle", "Edge", "Score Risque", "Mise (€)", "Justification"
        ])
        predictions_layout.addWidget(self.results_table, 1)
        
        predictions_group.setLayout(predictions_layout)
        bottom_layout.addWidget(predictions_group, 2)
        
        # Détails du cheval sélectionné
        horse_details = QGroupBox("Détails du cheval sélectionné")
        horse_layout = QVBoxLayout()
        
        self.horse_name_label = QLabel("Aucun cheval sélectionné")
        self.horse_name_label.setStyleSheet("font-weight: bold; font-size: 14pt; color: #2c3e50;")
        horse_layout.addWidget(self.horse_name_label)
        
        # Caractéristiques clés
        features_group = QGroupBox("Caractéristiques clés")
        features_layout = QVBoxLayout()
        
        self.resistance_label = QLabel("Résistance: --")
        features_layout.addWidget(self.resistance_label)
        
        self.acceleration_label = QLabel("Accélération tardive: --")
        features_layout.addWidget(self.acceleration_label)
        
        self.turn_efficiency_label = QLabel("Efficacité dans les virages: --")
        features_layout.addWidget(self.turn_efficiency_label)
        
        self.shoeing_label = QLabel("Déferrage: --")
        features_layout.addWidget(self.shoeing_label)
        
        features_group.setLayout(features_layout)
        horse_layout.addWidget(features_group)
        
        # Insights Arioneo spécifiques
        insights_group = QGroupBox("Insights Arioneo")
        insights_layout = QVBoxLayout()
        
        self.insight_label1 = QLabel("...")
        self.insight_label1.setWordWrap(True)
        insights_layout.addWidget(self.insight_label1)
        
        self.insight_label2 = QLabel("...")
        self.insight_label2.setWordWrap(True)
        insights_layout.addWidget(self.insight_label2)
        
        insights_group.setLayout(insights_layout)
        horse_layout.addWidget(insights_group)
        
        horse_details.setLayout(horse_layout)
        bottom_layout.addWidget(horse_details, 1)
        
        bottom_panel.setLayout(bottom_layout)
        content_splitter.addWidget(bottom_panel)
        
        content_splitter.setSizes([400, 400])
        main_layout.addWidget(content_splitter, 1)
        
        tab.setLayout(main_layout)
        return tab
    
    def create_models_tab(self):
        """Crée l'onglet de gestion des modèles"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("Gestion des Modèles Spécialisés", styleSheet="font-size: 16pt; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)
        
        # Sélecteur de contexte
        context_group = QGroupBox("Contexte du modèle")
        context_layout = QHBoxLayout()
        
        self.model_hippodrome = QComboBox()
        self.model_hippodrome.addItems(["Vincennes", "Longchamp", "Deauville", "Chantilly", "Meydan"])
        context_layout.addWidget(QLabel("Hippodrome:"))
        context_layout.addWidget(self.model_hippodrome, 1)
        
        self.model_discipline = QComboBox()
        self.model_discipline.addItems(["Trot", "Plat", "Obstacle"])
        context_layout.addWidget(QLabel("Discipline:"))
        context_layout.addWidget(self.model_discipline, 1)
        
        self.model_distance = QComboBox()
        self.model_distance.addItems(["1600m", "2100m", "2700m", "2850m", "3600m"])
        context_layout.addWidget(QLabel("Distance:"))
        context_layout.addWidget(self.model_distance, 1)
        
        self.model_going = QComboBox()
        self.model_going.addItems(["Bon (G)", "Souple (S)", "Lourd (L)"])
        context_layout.addWidget(QLabel("Going:"))
        context_layout.addWidget(self.model_going, 1)
        
        context_group.setLayout(context_layout)
        layout.addWidget(context_group)
        
        # Informations sur le modèle
        model_info = QGroupBox("Informations sur le modèle")
        model_layout = QHBoxLayout()
        
        # Statut et métriques
        status_group = QGroupBox("Statut")
        status_layout = QVBoxLayout()
        
        self.model_status = QLabel("Statut: Aucun modèle sélectionné")
        self.model_status.setStyleSheet("font-weight: bold;")
        status_layout.addWidget(self.model_status)
        
        self.model_metrics = QLabel("LogLoss: --\nBrier: --\nCRPS: --")
        status_layout.addWidget(self.model_metrics)
        
        self.model_last_update = QLabel("Dernière mise à jour: --")
        status_layout.addWidget(self.model_last_update)
        
        status_group.setLayout(status_layout)
        model_layout.addWidget(status_group, 1)
        
        # Visualisation des performances
        perf_group = QGroupBox("Performances récentes")
        perf_layout = QVBoxLayout()
        
        self.perf_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self.perf_axes = self.perf_canvas.figure.add_subplot(111)
        perf_layout.addWidget(self.perf_canvas)
        
        self.update_model_performance_chart()
        
        perf_group.setLayout(perf_layout)
        model_layout.addWidget(perf_group, 2)
        
        model_info.setLayout(model_layout)
        layout.addWidget(model_info)
        
        # Contrôles
        controls_layout = QHBoxLayout()
        
        self.train_btn = QPushButton("Entraîner/Réentraîner")
        self.train_btn.setStyleSheet("background-color: #27ae60;")
        self.train_btn.clicked.connect(self.train_model)
        controls_layout.addWidget(self.train_btn)
        
        self.validate_btn = QPushButton("Valider les performances")
        self.validate_btn.clicked.connect(self.validate_model)
        controls_layout.addWidget(self.validate_btn)
        
        self.deploy_btn = QPushButton("Déployer le modèle")
        self.deploy_btn.setStyleSheet("background-color: #2980b9;")
        self.deploy_btn.clicked.connect(self.deploy_model)
        self.deploy_btn.setEnabled(False)
        controls_layout.addWidget(self.deploy_btn)
        
        layout.addLayout(controls_layout)
        
        # Historique des mises à jour
        history_group = QGroupBox("Historique des mises à jour")
        history_layout = QVBoxLayout()
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(["Date", "Version", "LogLoss", "Statut"])
        self.history_table.setRowCount(5)
        
        # Remplir avec des données factices
        for i in range(5):
            self.history_table.setItem(i, 0, QTableWidgetItem(f"2023-08-{25-i:02d}"))
            self.history_table.setItem(i, 1, QTableWidgetItem(f"3.1.{i+1}"))
            self.history_table.setItem(i, 2, QTableWidgetItem(f"{0.55 - i*0.02:.2f}"))
            status = "Déployé" if i == 0 else "Validé" if i == 1 else "En test"
            self.history_table.setItem(i, 3, QTableWidgetItem(status))
        
        history_layout.addWidget(self.history_table)
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)
        
        tab.setLayout(layout)
        return tab
    
    def create_drift_monitor_tab(self):
        """Crée l'onglet de monitoring des drifts"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("Monitoring des Drifts Contextuels", styleSheet="font-size: 16pt; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)
        
        # Sélecteur de contexte
        context_group = QGroupBox("Contexte à surveiller")
        context_layout = QHBoxLayout()
        
        self.drift_hippodrome = QComboBox()
        self.drift_hippodrome.addItems(["Tous", "Vincennes", "Longchamp", "Deauville", "Chantilly", "Meydan"])
        context_layout.addWidget(QLabel("Hippodrome:"))
        context_layout.addWidget(self.drift_hippodrome, 1)
        
        self.drift_discipline = QComboBox()
        self.drift_discipline.addItems(["Tous", "Trot", "Plat", "Obstacle"])
        context_layout.addWidget(QLabel("Discipline:"))
        context_layout.addWidget(self.drift_discipline, 1)
        
        self.drift_distance = QComboBox()
        self.drift_distance.addItems(["Tous", "1600m", "2100m", "2700m", "2850m", "3600m"])
        context_layout.addWidget(QLabel("Distance:"))
        context_layout.addWidget(self.drift_distance, 1)
        
        self.drift_going = QComboBox()
        self.drift_going.addItems(["Tous", "Bon (G)", "Souple (S)", "Lourd (L)"])
        context_layout.addWidget(QLabel("Going:"))
        context_layout.addWidget(self.drift_going, 1)
        
        context_group.setLayout(context_layout)
        layout.addWidget(context_group)
        
        # Analyse globale
        global_group = QGroupBox("Analyse globale du drift")
        global_layout = QHBoxLayout()
        
        # Indicateur de drift global
        drift_indicator = QWidget()
        drift_layout = QVBoxLayout()
        
        self.drift_score = QLabel("PSI: --")
        self.drift_score.setStyleSheet("font-size: 24pt; font-weight: bold; color: #2c3e50;")
        drift_layout.addWidget(self.drift_score)
        
        self.drift_status = QLabel("Statut: Stable")
        self.drift_status.setStyleSheet("font-size: 14pt; color: #27ae60;")
        drift_layout.addWidget(self.drift_status)
        
        self.drift_trend = QLabel("Tendance: Aucun changement significatif")
        self.drift_trend.setWordWrap(True)
        drift_layout.addWidget(self.drift_trend)
        
        drift_layout.addStretch()
        drift_indicator.setLayout(drift_layout)
        global_layout.addWidget(drift_indicator, 1)
        
        # Graphique de tendance
        self.drift_canvas = FigureCanvas(Figure(figsize=(6, 4)))
        self.drift_axes = self.drift_canvas.figure.add_subplot(111)
        self.update_drift_trend_chart()
        global_layout.addWidget(self.drift_canvas, 2)
        
        global_group.setLayout(global_layout)
        layout.addWidget(global_group)
        
        # Contextes à risque
        risk_group = QGroupBox("Contextes nécessitant une attention")
        risk_layout = QVBoxLayout()
        
        self.risk_table = QTableWidget()
        self.risk_table.setColumnCount(6)
        self.risk_table.setHorizontalHeaderLabels([
            "Contexte", "PSI", "Pattern", "Exceptions", "Dernière MAJ", "Action"
        ])
        self.risk_table.setRowCount(3)
        
        # Remplir avec des données factices
        contexts = [
            ("Trot/Vincennes/2850m/Bon", "0.28", "Late Bloomer", "2", "2023-08-25", "Mise à jour recommandée"),
            ("Plat/Deauville/1600m/Souple", "0.22", "Early Pace", "0", "2023-08-20", "Surveillance"),
            ("Obstacle/Longchamp/3600m/Lourd", "0.18", "Standard", "1", "2023-08-18", "Aucune action")
        ]
        
        for i, ctx in enumerate(contexts):
            for j, item in enumerate(ctx):
                table_item = QTableWidgetItem(item)
                if j == 5 and "recommandée" in item:
                    table_item.setForeground(QColor("#e74c3c"))
                self.risk_table.setItem(i, j, table_item)
        
        risk_layout.addWidget(self.risk_table)
        risk_group.setLayout(risk_layout)
        layout.addWidget(risk_group)
        
        # Boutons d'action
        action_layout = QHBoxLayout()
        
        self.monitor_btn = QPushButton("Analyser le drift")
        self.monitor_btn.setStyleSheet("background-color: #27ae60;")
        self.monitor_btn.clicked.connect(self.analyze_drift)
        action_layout.addWidget(self.monitor_btn)
        
        self.update_models_btn = QPushButton("Mettre à jour les modèles concernés")
        self.update_models_btn.setStyleSheet("background-color: #2980b9;")
        self.update_models_btn.setEnabled(False)
        self.update_models_btn.clicked.connect(self.update_risk_models)
        action_layout.addWidget(self.update_models_btn)
        
        layout.addLayout(action_layout)
        
        tab.setLayout(layout)
        return tab
    
    def create_risk_management_tab(self):
        """Crée l'onglet de gestion du risque"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("Gestion du Risque et Optimisation du Portefeuille", 
                      styleSheet="font-size: 16pt; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)
        
        # Sélecteur de course
        race_group = QGroupBox("Course à analyser")
        race_layout = QHBoxLayout()
        
        self.risk_hippodrome = QComboBox()
        self.risk_hippodrome.addItems(["Vincennes", "Longchamp", "Deauville", "Chantilly", "Meydan"])
        race_layout.addWidget(QLabel("Hippodrome:"))
        race_layout.addWidget(self.risk_hippodrome, 1)
        
        self.risk_distance = QComboBox()
        self.risk_distance.addItems(["1600m", "2100m", "2700m", "2850m", "3600m"])
        race_layout.addWidget(QLabel("Distance:"))
        race_layout.addWidget(self.risk_distance, 1)
        
        self.risk_going = QComboBox()
        self.risk_going.addItems(["Bon (G)", "Souple (S)", "Lourd (L)"])
        race_layout.addWidget(QLabel("Going:"))
        race_layout.addWidget(self.risk_going, 1)
        
        self.analyze_risk_btn = QPushButton("Analyser le risque")
        self.analyze_risk_btn.setStyleSheet("background-color: #27ae60;")
        self.analyze_risk_btn.clicked.connect(self.analyze_risk)
        race_layout.addWidget(self.analyze_risk_btn)
        
        race_group.setLayout(race_layout)
        layout.addWidget(race_group)
        
        # Analyse du risque
        risk_analysis = QGroupBox("Analyse détaillée du risque")
        risk_layout = QHBoxLayout()
        
        # Niveau de risque global
        risk_indicator = QWidget()
        risk_indicator_layout = QVBoxLayout()
        
        self.risk_level = QLabel("Risque: --")
        self.risk_level.setStyleSheet("font-size: 24pt; font-weight: bold; color: #2c3e50;")
        risk_indicator_layout.addWidget(self.risk_level)
        
        self.risk_description = QLabel("Description du niveau de risque")
        self.risk_description.setWordWrap(True)
        risk_indicator_layout.addWidget(self.risk_description)
        
        risk_indicator_layout.addStretch()
        risk_indicator.setLayout(risk_indicator_layout)
        risk_layout.addWidget(risk_indicator, 1)
        
        # Graphique de répartition du risque
        self.risk_canvas = FigureCanvas(Figure(figsize=(5, 4)))
        self.risk_axes = self.risk_canvas.figure.add_subplot(111)
        self.update_risk_distribution_chart()
        risk_layout.addWidget(self.risk_canvas, 2)
        
        risk_analysis.setLayout(risk_layout)
        layout.addWidget(risk_analysis)
        
        # Optimisation du portefeuille
        portfolio_group = QGroupBox("Optimisation du portefeuille")
        portfolio_layout = QVBoxLayout()
        
        # Contrôles
        portfolio_controls = QHBoxLayout()
        
        self.bet_type_portfolio = QComboBox()
        self.bet_type_portfolio.addItems(["Gagnant", "Placé", "Trio", "Quarté"])
        portfolio_controls.addWidget(QLabel("Type de pari:"))
        portfolio_controls.addWidget(self.bet_type_portfolio, 1)
        
        self.bankroll_input = QLabel("Bankroll: 1000.00 €")
        portfolio_controls.addWidget(self.bankroll_input)
        
        self.risk_aversion = QComboBox()
        self.risk_aversion.addItems(["Faible (0.3)", "Moyenne (0.5)", "Élevée (0.7)"])
        self.risk_aversion.setCurrentIndex(1)
        portfolio_controls.addWidget(QLabel("Aversion au risque:"))
        portfolio_controls.addWidget(self.risk_aversion, 1)
        
        self.optimize_btn = QPushButton("Optimiser le portefeuille")
        self.optimize_btn.setStyleSheet("background-color: #27ae60;")
        self.optimize_btn.clicked.connect(self.optimize_portfolio)
        portfolio_controls.addWidget(self.optimize_btn)
        
        portfolio_layout.addLayout(portfolio_controls)
        
        # Tableau des paris optimisés
        self.portfolio_table = QTableWidget()
        self.portfolio_table.setColumnCount(7)
        self.portfolio_table.setHorizontalHeaderLabels([
            "Type de pari", "Combinaison", "Cote", "P(Edge)", "Edge", "Mise (€)", "ROI attendu"
        ])
        self.portfolio_table.setRowCount(10)
        portfolio_layout.addWidget(self.portfolio_table, 1)
        
        # Résumé du portefeuille
        summary_layout = QHBoxLayout()
        
        self.total_exposure = QLabel("Exposition totale: -- €")
        self.total_exposure.setStyleSheet("font-weight: bold;")
        summary_layout.addWidget(self.total_exposure)
        
        self.expected_roi = QLabel("ROI attendu: -- %")
        self.expected_roi.setStyleSheet("font-weight: bold;")
        summary_layout.addWidget(self.expected_roi)
        
        self.diversification = QLabel("Diversification: --")
        self.diversification.setStyleSheet("font-weight: bold;")
        summary_layout.addWidget(self.diversification)
        
        portfolio_layout.addLayout(summary_layout)
        
        portfolio_group.setLayout(portfolio_layout)
        layout.addWidget(portfolio_group)
        
        # Historique des performances
        history_group = QGroupBox("Historique des performances")
        history_layout = QVBoxLayout()
        
        self.performance_table = QTableWidget()
        self.performance_table.setColumnCount(5)
        self.performance_table.setHorizontalHeaderLabels([
            "Date", "Exposition", "ROI", "Sharp Ratio", "Max Drawdown"
        ])
        self.performance_table.setRowCount(10)
        
        # Remplir avec des données factices
        for i in range(10):
            self.performance_table.setItem(i, 0, QTableWidgetItem(f"2023-08-{25-i:02d}"))
            self.performance_table.setItem(i, 1, QTableWidgetItem(f"{50 + i*5} €"))
            self.performance_table.setItem(i, 2, QTableWidgetItem(f"{3.5 - i*0.2:.1f}%"))
            self.performance_table.setItem(i, 3, QTableWidgetItem(f"{1.2 - i*0.05:.2f}"))
            self.performance_table.setItem(i, 4, QTableWidgetItem(f"{-5.0 - i*0.3:.1f}%"))
        
        history_layout.addWidget(self.performance_table)
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)
        
        tab.setLayout(layout)
        return tab
    
    def load_race(self, hippodrome: str, distance: str):
        """Charge les données d'une course sélectionnée"""
        self.current_race_id = f"{hippodrome.lower()}_{distance}"
        distance_m = int(distance.replace('m', ''))
        
        # Mettre à jour l'interface
        self.race_info.setText(f"Course sélectionnée: {hippodrome} - {distance}")
        self.run_analysis_btn.setEnabled(True)
        
        # Mettre à jour le profil de vitesse
        self.update_speed_profile(hippodrome, distance_m)
        
        # Mettre à jour la validation des théories
        self.theory_validation.race_id = self.current_race_id
        self.theory_validation.init_ui()
        
        logger.info(f"Course chargée: {self.current_race_id}")
    
    def update_speed_profile(self, hippodrome: str, distance_m: int):
        """Met à jour le profil de vitesse en fonction du contexte"""
        # Générer un profil de vitesse réaliste
        x = np.linspace(0, distance_m, 1000)
        
        # Différents patterns selon l'hippodrome et la distance
        vincennes_layout = "vincennes" in hippodrome.lower()
        
        if distance_m <= 1600:
            # Courtes distances: accélération précoce puis décélération
            y = 12.0 - 0.002 * (x - distance_m/2)**2
            if vincennes_layout:
                # À Vincennes, les virages serrés affectent la vitesse
                y = y * 0.89  # 11% plus lent comme indiqué par Arioneo
            race_style = "early_speed"
        else:
            # Longues distances: vitesse plus stable puis accélération tardive
            y = 11.5 + 0.0005 * x - 0.0000002 * x**2
            race_style = "late_finisher"
        
        # Mettre à jour le graphique
        self.speed_canvas.plot_speed_profile(y, distance_m, race_style, vincennes_layout)
        
        # Mettre à jour le sélecteur de style
        self.race_style_combo.setCurrentText(race_style.replace('_', ' ').title())
        self.vincennes_check.setChecked(vincennes_layout)
    
    def run_full_analysis(self):
        """Exécute l'analyse complète de la course"""
        if not self.current_race_id:
            return
        
        logger.info(f"\n--- Lancement de l'analyse complète pour {self.current_race_id} ---")
        self.statusBar().showMessage("Analyse en cours...")
        
        # Simuler le chargement des données
        self.race_info.setText(f"Analyse en cours pour {self.current_race_id}...")
        
        # 1. Récupérer les données de la course
        race_data = self.db_manager.get_race_data(self.current_race_id)
        if not race_data:
            # Pour la démo, créer des données factices
            race_data = {
                'race_info': {
                    'race_id': self.current_race_id,
                    'hippodrome': self.current_race_id.split('_')[0].capitalize(),
                    'distance_m': int(self.current_race_id.split('_')[1].replace('m', '')),
                    'going_code': 'G',
                    'field_size': 16
                },
                'horses': [{
                    'horse_id': f'H{i}',
                    'name': f'Cheval {i}',
                    'age': 5,
                    'sex': 'M' if i % 2 == 0 else 'F',
                    'trainer_id': f'T{i%3}',
                    'jockey_id': f'J{i%4}',
                    'odds': round(5 + np.random.exponential(10), 1),
                    'shoeing_change': bool(i % 3 == 0),
                    'tracking_data': {
                        'speed_profile': np.random.normal(11.5, 0.5, 1000).tolist()
                    },
                    'recent_form': [np.random.randint(1, 10) for _ in range(5)]
                } for i in range(1, 17)]
            }
        
        # 2. Calculer les features
        predictions = {}
        for horse in race_data['horses']:
            features = self.feature_engineer.calculate_all_features(horse, race_data['race_info'])
            predictions[horse['horse_id']] = features
        
        # 3. Simuler les prédictions du modèle
        for horse_id, features in predictions.items():
            # Calculer une probabilité de victoire réaliste
            base_prob = 0.15
            
            # Ajuster selon le Resistance Score (Arioneo)
            if 'performance' in features and 'base_metrics' in features['performance']:
                resistance = features['performance']['base_metrics'].get('resistance_score', 0.8)
                late_acceleration = features['performance']['base_metrics'].get('late_race_acceleration_index', 0.9)
                
                # Selon Arioneo: "Les chevaux gagnants à l'arrivée sont les chevaux capables de tenir leur vitesse le plus longtemps possible"
                if resistance > 0.85:
                    base_prob += 0.05
                if late_acceleration > 1.05:
                    base_prob += 0.03
            
            # Ajuster selon le contexte spécifique
            vincennes_layout = "vincennes" in race_data['race_info']['hippodrome'].lower()
            if vincennes_layout and 'performance' in features and 'base_metrics' in features['performance']:
                turn_efficiency = features['performance']['base_metrics'].get('vincennes_turn_efficiency', 0.85)
                # À Vincennes, l'efficacité dans les virages est critique
                if turn_efficiency > 0.9:
                    base_prob += 0.04
            
            # Ajouter de l'incertitude
            p_win_mean = min(0.9, max(0.02, base_prob + np.random.normal(0, 0.05)))
            p_win_variance = 0.01 + np.random.exponential(0.02)
            
            # Calculer l'edge
            odds = horse['odds']
            edge = (p_win_mean * (odds - 1)) - (1 - p_win_mean)
            
            # Stocker les résultats
            predictions[horse_id].update({
                'p_win_mean': p_win_mean,
                'p_win_variance': p_win_variance,
                'edge': edge,
                'odds': odds
            })
        
        # 4. Calculer le niveau de confiance
        self.current_confidence = self.calculate_confidence(predictions, race_data)
        self.confidence_indicator.confidence = self.current_confidence
        self.confidence_indicator.update()
        self.confidence_label.setText(f"Confiance: {self.current_confidence:.0%}")
        
        # Mettre à jour la validation des théories
        self.theory_validation.race_id = self.current_race_id
        self.theory_validation.init_ui()
        
        # 5. Optimiser les mises
        stakes = self.bankroll_manager.optimize_stakes(
            {hid: {
                'p_win_mean': pred['p_win_mean'],
                'p_win_variance': pred['p_win_variance'],
                'odds': pred['odds'],
                'shoeing_change': race_data['horses'][i-1]['shoeing_change']
            } for i, (hid, pred) in enumerate(predictions.items())},
            race_data['race_info'],
            self.current_confidence
        )
        
        # 6. Afficher les résultats
        bet_type = self.bet_type_combo.currentText()
        self.display_results(predictions, stakes, bet_type, race_data)
        
        self.statusBar().showMessage(f"Analyse terminée - Confiance: {self.current_confidence:.0%}")
        logger.info("--- Analyse terminée et affichée ---")
    
    def calculate_confidence(self, predictions: dict, race_data: dict) -> float:
        """
        Calcule le niveau de confiance du modèle pour cette course
        
        Returns:
            Niveau de confiance (0.0-1.0)
        """
        # Complétude des données
        data_completeness = 0.7  # Dans un système réel, cela viendrait des données
        
        # Cohérence avec les théories
        theory_consistency = 0.8  # Dans un système réel, cela viendrait du theory validator
        
        # Nombre d'exceptions
        exceptions = 2  # Dans un système réel, cela viendrait du theory validator
        exception_penalty = min(0.3, exceptions * 0.1)
        
        # Calculer la confiance
        confidence = (
            data_completeness * 0.4 +
            theory_consistency * 0.4 -
            exception_penalty * 0.2
        )
        
        return max(0.1, min(1.0, confidence))
    
    def display_results(self, predictions: dict, stakes: dict, bet_type: str, race_data: dict):
        """Affiche les résultats de l'analyse"""
        # Déterminer le nombre de colonnes à afficher selon le type de pari
        if bet_type == "Gagnant":
            self.results_table.setColumnCount(8)
            self.results_table.setHorizontalHeaderLabels([
                "Cheval ID", "Cote", "P(Win)", "Intervalle", "Edge", "Score Risque", "Mise (€)", "Justification"
            ])
        elif bet_type == "Placé":
            self.results_table.setColumnCount(8)
            self.results_table.setHorizontalHeaderLabels([
                "Cheval ID", "Cote", "P(Place)", "Intervalle", "Edge", "Score Risque", "Mise (€)", "Justification"
            ])
        else:  # Trio ou Quarté
            self.results_table.setColumnCount(7)
            self.results_table.setHorizontalHeaderLabels([
                "Combinaison", "Cote", "P(Combo)", "Edge", "Score Risque", "Mise (€)", "Justification"
            ])
        
        # Remplir le tableau
        if bet_type in ["Gagnant", "Placé"]:
            # Afficher les chevaux individuels
            self.results_table.setRowCount(len(predictions))
            
            for i, (horse_id, pred) in enumerate(predictions.items()):
                # Déterminer si ce cheval est concerné par le type de pari
                if bet_type == "Gagnant" or (bet_type == "Placé" and pred['p_win_mean'] > 0.05):
                    # Intervalle de confiance
                    ci_lower = max(0.0, pred['p_win_mean'] - 1.96 * np.sqrt(pred['p_win_variance']))
                    ci_upper = min(1.0, pred['p_win_mean'] + 1.96 * np.sqrt(pred['p_win_variance']))
                    
                    # Score de risque
                    risk_score = min(1.0, pred['p_win_variance'] * 10.0)
                    
                    # Justification
                    justification = []
                    
                    # Resistance Score (Arioneo)
                    if 'performance' in pred and 'base_metrics' in pred['performance']:
                        resistance = pred['performance']['base_metrics'].get('resistance_score', 0.8)
                        if resistance > 0.85:
                            justification.append("Bonne résistance (Arioneo)")
                        if 'late_race_acceleration_index' in pred['performance']['base_metrics']:
                            late_accel = pred['performance']['base_metrics']['late_race_acceleration_index']
                            if late_accel > 1.05:
                                justification.append("Accélération tardive forte")
                    
                    # Vincennes specifics
                    vincennes_layout = "vincennes" in race_data['race_info']['hippodrome'].lower()
                    if vincennes_layout and 'performance' in pred and 'base_metrics' in pred['performance']:
                        turn_eff = pred['performance']['base_metrics'].get('vincennes_turn_efficiency', 0.85)
                        if turn_eff > 0.9:
                            justification.append("Bon dans les virages (Vincennes)")
                    
                    # Déferrage
                    horse_data = next((h for h in race_data['horses'] if h['horse_id'] == horse_id), None)
                    if horse_data and horse_data.get('shoeing_change', False):
                        justification.append("Déferré (avantage selon Arioneo)")
                    
                    # Remplir le tableau
                    self.results_table.setItem(i, 0, QTableWidgetItem(horse_id))
                    self.results_table.setItem(i, 1, QTableWidgetItem(f"{pred['odds']:.1f}"))
                    self.results_table.setItem(i, 2, QTableWidgetItem(f"{pred['p_win_mean']:.3f}"))
                    self.results_table.setItem(i, 3, QTableWidgetItem(f"[{ci_lower:.3f}-{ci_upper:.3f}]"))
                    self.results_table.setItem(i, 4, QTableWidgetItem(f"{pred['edge']:+.2f}"))
                    self.results_table.setItem(i, 5, QTableWidgetItem(f"{risk_score:.3f}"))
                    self.results_table.setItem(i, 6, QTableWidgetItem(f"{stakes.get(horse_id, 0.0):.2f}"))
                    
                    # Justification
                    justification_text = "\n".join(justification[:2])  # Limiter à 2 points
                    if len(justification) > 2:
                        justification_text += f"\n(+{len(justification)-2} autres)"
                    self.results_table.setItem(i, 7, QTableWidgetItem(justification_text))
        else:
            # Afficher les combinaisons pour Trio/Quarté
            # Dans un système réel, cela viendrait du bankroll manager
            # Ici, pour la démo, on simule quelques combinaisons
            combinations = [
                ("H1-H2-H3", 150.0, 0.08, 0.2, 0.15, 5.0, "Trio solide avec chevaux résistants"),
                ("H2-H4-H7", 250.0, 0.05, 0.1, 0.2, 3.0, "Trio avec accélération tardive"),
                ("H1-H5-H9", 350.0, 0.03, 0.05, 0.25, 2.0, "Trio risqué mais edge positif")
            ]
            
            self.results_table.setRowCount(len(combinations))
            for i, combo in enumerate(combinations):
                for j, value in enumerate(combo):
                    if j == 2:  # Probabilité
                        self.results_table.setItem(i, j, QTableWidgetItem(f"{value:.3f}"))
                    elif j == 3:  # Edge
                        self.results_table.setItem(i, j, QTableWidgetItem(f"{value:+.2f}"))
                    elif j == 4:  # Score de risque
                        self.results_table.setItem(i, j, QTableWidgetItem(f"{value:.2f}"))
                    elif j == 5:  # Mise
                        self.results_table.setItem(i, j, QTableWidgetItem(f"{value:.2f}"))
                    else:
                        self.results_table.setItem(i, j, QTableWidgetItem(str(value)))
        
        # Connecter l'événement de sélection de ligne
        self.results_table.cellClicked.connect(self.display_horse_details)
        
        logger.info("Résultats affichés avec succès")
    
    def display_horse_details(self, row: int, column: int):
        """Affiche les détails du cheval sélectionné"""
        # Récupérer l'ID du cheval
        horse_id_item = self.results_table.item(row, 0)
        if not horse_id_item:
            return
        
        horse_id = horse_id_item.text()
        self.horse_name_label.setText(f"Détails - {horse_id}")
        
        # Récupérer les données du cheval
        race_data = self.db_manager.get_race_data(self.current_race_id)
        horse_data = next((h for h in race_data['horses'] if h['horse_id'] == horse_id), None)
        if not horse_data:
            return
        
        # Récupérer les features
        features = self.feature_engineer.calculate_all_features(horse_data, race_data['race_info'])
        
        # Mettre à jour les caractéristiques clés
        if 'performance' in features and 'base_metrics' in features['performance']:
            base_metrics = features['performance']['base_metrics']
            
            # Resistance Score
            resistance = base_metrics.get('resistance_score', 0.8)
            self.resistance_label.setText(f"Résistance: {resistance:.2f} {'✅' if resistance > 0.85 else '⚠️'}")
            
            # Late Race Acceleration Index
            late_accel = base_metrics.get('late_race_acceleration_index', 0.9)
            self.acceleration_label.setText(f"Accélération tardive: {late_accel:.2f} {'✅' if late_accel > 1.05 else '⚠️'}")
            
            # Vincennes Turn Efficiency
            if "vincennes" in race_data['race_info']['hippodrome'].lower() and 'vincennes_turn_efficiency' in base_metrics:
                turn_eff = base_metrics['vincennes_turn_efficiency']
                self.turn_efficiency_label.setText(f"Efficacité dans les virages: {turn_eff:.2f} {'✅' if turn_eff > 0.9 else '⚠️'}")
            else:
                self.turn_efficiency_label.setText("Efficacité dans les virages: N/A")
        
        # Déferrage
        self.shoeing_label.setText(f"Déferrage: {'Oui ✅' if horse_data.get('shoeing_change', False) else 'Non'}")
        
        # Mettre à jour les insights Arioneo
        vincennes_layout = "vincennes" in race_data['race_info']['hippodrome'].lower()
        
        if vincennes_layout:
            self.insight_label1.setText("À Vincennes, les courses avec virage sont en moyenne 11% plus lente que les courses en ligne droite (Arioneo)")
        else:
            self.insight_label1.setText("Sur les courtes distances, les derniers 600-400m sont courus plus rapidement que les derniers 400-200m (Arioneo)")
        
        # Deuxième insight selon le style
        if 'performance' in features and 'base_metrics' in features['performance']:
            late_accel = features['performance']['base_metrics'].get('late_race_acceleration_index', 0.9)
            if late_accel > 1.05:
                self.insight_label2.setText("Sur les 200 derniers mètres, 3 km/h d'écart entre deux chevaux induit environ 10 mètres d'écart (Arioneo)")
            else:
                self.insight_label2.setText("Les chevaux gagnants sont ceux capables de tenir leur vitesse le plus longtemps possible (Arioneo)")
        else:
            self.insight_label2.setText("Les stratégies de course varient selon l'hippodrome et le type de piste (Arioneo)")
    
    def update_model_performance_chart(self):
        """Met à jour le graphique des performances du modèle"""
        self.perf_axes.clear()
        
        # Données factices pour la démo
        dates = [f"J-{i}" for i in range(7, 0, -1)]
        logloss = [0.58, 0.57, 0.56, 0.55, 0.54, 0.53, 0.52]
        crps = [0.18, 0.17, 0.16, 0.15, 0.14, 0.13, 0.12]
        
        # Créer les barres
        x = np.arange(len(dates))
        width = 0.35
        
        self.perf_axes.bar(x - width/2, logloss, width, label='LogLoss', color='#3498db')
        self.perf_axes.bar(x + width/2, crps, width, label='CRPS', color='#27ae60')
        
        # Configurer le graphique
        self.perf_axes.set_ylabel('Score')
        self.perf_axes.set_title('Performances récentes du modèle')
        self.perf_axes.set_xticks(x)
        self.perf_axes.set_xticklabels(dates)
        self.perf_axes.legend()
        self.perf_axes.grid(axis='y', linestyle='--', alpha=0.7)
        
        self.perf_canvas.draw()
    
    def update_drift_trend_chart(self):
        """Met à jour le graphique de tendance du drift"""
        self.drift_axes.clear()
        
        # Données factices pour la démo
        dates = [f"2023-08-{25-i:02d}" for i in range(10)]
        psi_values = [0.15, 0.16, 0.17, 0.18, 0.19, 0.20, 0.21, 0.22, 0.23, 0.24]
        
        # Tracer le PSI
        self.drift_axes.plot(dates, psi_values, 'o-', linewidth=2, markersize=6)
        
        # Ajouter une ligne de seuil
        self.drift_axes.axhline(y=0.25, color='r', linestyle='--', label='Seuil de drift')
        
        # Configurer le graphique
        self.drift_axes.set_ylabel('PSI')
        self.drift_axes.set_title('Évolution du Population Stability Index (PSI)')
        self.drift_axes.set_xticklabels(dates, rotation=45, ha='right')
        self.drift_axes.legend()
        self.drift_axes.grid(True, linestyle='--', alpha=0.7)
        
        self.drift_canvas.draw()
        
        # Mettre à jour les indicateurs
        current_psi = psi_values[-1]
        self.drift_score.setText(f"PSI: {current_psi:.2f}")
        
        if current_psi > 0.25:
            self.drift_status.setText("Statut: Drift détecté !")
            self.drift_status.setStyleSheet("font-size: 14pt; color: #e74c3c;")
            self.drift_trend.setText("Tendance: Augmentation continue du PSI - nécessite une mise à jour des modèles")
            self.update_models_btn.setEnabled(True)
        elif current_psi > 0.20:
            self.drift_status.setText("Statut: Surveillance requise")
            self.drift_status.setStyleSheet("font-size: 14pt; color: #f39c12;")
            self.drift_trend.setText("Tendance: Légère augmentation du PSI - surveiller les prochaines courses")
            self.update_models_btn.setEnabled(False)
        else:
            self.drift_status.setText("Statut: Stable")
            self.drift_status.setStyleSheet("font-size: 14pt; color: #27ae60;")
            self.drift_trend.setText("Tendance: Aucun changement significatif")
            self.update_models_btn.setEnabled(False)
    
    def update_risk_distribution_chart(self):
        """Met à jour le graphique de répartition du risque"""
        self.risk_axes.clear()
        
        # Données factices pour la démo
        risk_factors = ['Resistance', 'Accélération', 'Virages', 'Déferrage', 'Forme']
        values = [0.7, 0.6, 0.8, 0.5, 0.9]
        
        # Créer le graphique radar
        angles = np.linspace(0, 2 * np.pi, len(risk_factors), endpoint=False).tolist()
        values += values[:1]  # Fermer le graphique
        angles += angles[:1]
        
        self.risk_axes = self.risk_canvas.figure.add_subplot(111, polar=True)
        self.risk_axes.plot(angles, values, 'o-', linewidth=2, color='#3498db')
        self.risk_axes.fill(angles, values, alpha=0.25, color='#3498db')
        self.risk_axes.set_thetagrids(np.degrees(angles[:-1]), risk_factors)
        self.risk_axes.set_rlabel_position(0)
        self.risk_axes.set_ylim(0, 1)
        self.risk_axes.grid(True)
        
        self.risk_canvas.draw()
        
        # Mettre à jour les indicateurs de risque
        avg_risk = np.mean(values[:-1])
        self.risk_level.setText(f"Risque: {avg_risk:.0%}")
        
        if avg_risk < 0.4:
            self.risk_level.setStyleSheet("font-size: 24pt; font-weight: bold; color: #27ae60;")
            self.risk_description.setText("Risque faible - Conditions favorables pour les paris")
        elif avg_risk < 0.7:
            self.risk_level.setStyleSheet("font-size: 24pt; font-weight: bold; color: #f39c12;")
            self.risk_description.setText("Risque modéré - Analyse plus approfondie recommandée")
        else:
            self.risk_level.setStyleSheet("font-size: 24pt; font-weight: bold; color: #e74c3c;")
            self.risk_description.setText("Risque élevé - Prudence recommandée dans les paris")
    
    def analyze_drift(self):
        """Analyse le drift contextuel"""
        self.statusBar().showMessage("Analyse du drift en cours...")
        logger.info("Analyse du drift contextuel en cours...")
        
        # Dans un système réel, cela utiliserait le drift monitor
        # Ici, pour la démo, on simule
        time.sleep(0.5)
        
        # Mettre à jour le graphique
        self.update_drift_trend_chart()
        
        # Mettre à jour le tableau des contextes à risque
        self.risk_table.setItem(0, 5, QTableWidgetItem("Mise à jour recommandée"))
        self.risk_table.item(0, 5).setForeground(QColor("#e74c3c"))
        
        self.statusBar().showMessage("Analyse du drift terminée")
        logger.info("Analyse du drift terminée")
    
    def update_risk_models(self):
        """Met à jour les modèles à risque"""
        self.statusBar().showMessage("Mise à jour des modèles en cours...")
        logger.info("Mise à jour des modèles à risque en cours...")
        
        # Dans un système réel, cela utiliserait le model updater
        # Ici, pour la démo, on simule
        time.sleep(1.0)
        
        # Mettre à jour l'interface
        self.risk_table.setItem(0, 5, QTableWidgetItem("Mis à jour"))
        self.risk_table.item(0, 5).setForeground(QColor("#27ae60"))
        self.risk_table.setItem(0, 4, QTableWidgetItem(datetime.now().strftime("%Y-%m-%d")))
        
        self.statusBar().showMessage("Modèles mis à jour avec succès")
        logger.info("Modèles mis à jour avec succès")
    
    def analyze_risk(self):
        """Analyse le risque pour la gestion du portefeuille"""
        self.statusBar().showMessage("Analyse du risque en cours...")
        logger.info("Analyse du risque en cours...")
        
        # Dans un système réel, cela utiliserait le bankroll manager
        # Ici, pour la démo, on simule
        time.sleep(0.5)
        
        # Mettre à jour le graphique
        self.update_risk_distribution_chart()
        
        self.statusBar().showMessage("Analyse du risque terminée")
        logger.info("Analyse du risque terminée")
    
    def optimize_portfolio(self):
        """Optimise le portefeuille de paris"""
        self.statusBar().showMessage("Optimisation du portefeuille en cours...")
        logger.info("Optimisation du portefeuille en cours...")
        
        # Dans un système réel, cela utiliserait le bankroll manager
        # Ici, pour la démo, on simule
        time.sleep(0.5)
        
        # Remplir le tableau
        bet_type = self.bet_type_portfolio.currentText()
        if bet_type == "Gagnant":
            combinations = [
                ("Gagnant", "H1", "5.2", "0.18", "+0.84", "12.50", "+9.3%"),
                ("Gagnant", "H3", "8.7", "0.12", "+0.04", "5.20", "+0.2%"),
                ("Gagnant", "H7", "12.5", "0.08", "-0.04", "0.00", "-0.5%")
            ]
        elif bet_type == "Placé":
            combinations = [
                ("Placé", "H1", "2.3", "0.35", "+0.81", "25.00", "+20.3%"),
                ("Placé", "H2", "2.8", "0.28", "+0.78", "18.75", "+14.7%"),
                ("Placé", "H3", "3.5", "0.22", "+0.77", "12.50", "+9.6%")
            ]
        elif bet_type == "Trio":
            combinations = [
                ("Trio", "H1-H2-H3", "150.0", "0.08", "+12.00", "5.00", "+6.0%"),
                ("Trio", "H2-H4-H7", "250.0", "0.05", "+2.50", "3.00", "+0.8%"),
                ("Trio", "H1-H5-H9", "350.0", "0.03", "-3.50", "0.00", "-1.1%")
            ]
        else:  # Quarté
            combinations = [
                ("Quarté", "H1-H2-H3-H4", "1200.0", "0.02", "+14.40", "2.00", "+0.3%"),
                ("Quarté", "H1-H2-H3-H7", "850.0", "0.03", "+15.30", "1.50", "+0.2%"),
                ("Quarté", "H1-H2-H4-H7", "650.0", "0.04", "+10.40", "1.00", "+0.1%")
            ]
        
        self.portfolio_table.setRowCount(len(combinations))
        for i, combo in enumerate(combinations):
            for j, value in enumerate(combo):
                self.portfolio_table.setItem(i, j, QTableWidgetItem(value))
        
        # Mettre à jour le résumé
        self.total_exposure.setText("Exposition totale: 48.75 €")
        self.expected_roi.setText("ROI attendu: +45.10 €")
        self.diversification.setText("Diversification: Élevée")
        
        self.statusBar().showMessage("Portefeuille optimisé")
        logger.info("Portefeuille optimisé")
    
    def train_model(self):
        """Entraîne ou réentraîne un modèle"""
        self.statusBar().showMessage("Entraînement du modèle en cours...")
        logger.info("Entraînement du modèle en cours...")
        
        # Dans un système réel, cela utiliserait le model trainer
        # Ici, pour la démo, on simule
        time.sleep(1.5)
        
        # Mettre à jour l'interface
        hippodrome = self.model_hippodrome.currentText()
        discipline = self.model_discipline.currentText()
        distance = self.model_distance.currentText()
        going = self.model_going.currentText()
        
        model_id = f"{discipline.lower()}_{hippodrome.lower()}_{distance}_{going}"
        
        self.model_status.setText(f"Statut: {model_id} entraîné avec succès")
        self.model_status.setStyleSheet("font-weight: bold; color: #27ae60;")
        self.model_metrics.setText("LogLoss: 0.52\nBrier: 0.12\nCRPS: 0.11")
        self.model_last_update.setText(f"Dernière mise à jour: {datetime.now().strftime('%Y-%m-%d')}")
        
        # Ajouter à l'historique
        row_position = self.history_table.rowCount()
        self.history_table.insertRow(0)
        self.history_table.setItem(0, 0, QTableWidgetItem(datetime.now().strftime("%Y-%m-%d")))
        self.history_table.setItem(0, 1, QTableWidgetItem("3.1.4"))
        self.history_table.setItem(0, 2, QTableWidgetItem("0.52"))
        self.history_table.setItem(0, 3, QTableWidgetItem("En test"))
        
        # Mettre à jour le graphique
        self.update_model_performance_chart()
        
        self.deploy_btn.setEnabled(True)
        self.statusBar().showMessage(f"Modèle {model_id} entraîné avec succès")
        logger.info(f"Modèle {model_id} entraîné avec succès")
    
    def validate_model(self):
        """Valide les performances du modèle"""
        self.statusBar().showMessage("Validation du modèle en cours...")
        logger.info("Validation du modèle en cours...")
        
        # Dans un système réel, cela utiliserait le model trainer
        # Ici, pour la démo, on simule
        time.sleep(0.8)
        
        # Mettre à jour l'interface
        self.model_status.setText("Statut: Validé - Prêt au déploiement")
        self.model_status.setStyleSheet("font-weight: bold; color: #27ae60;")
        self.deploy_btn.setEnabled(True)
        
        self.statusBar().showMessage("Modèle validé avec succès")
        logger.info("Modèle validé avec succès")
    
    def deploy_model(self):
        """Déploie le modèle validé"""
        self.statusBar().showMessage("Déploiement du modèle en cours...")
        logger.info("Déploiement du modèle en cours...")
        
        # Dans un système réel, cela utiliserait le model updater
        # Ici, pour la démo, on simule
        time.sleep(0.5)
        
        # Mettre à jour l'interface
        self.model_status.setText("Statut: Déployé avec succès")
        self.model_status.setStyleSheet("font-weight: bold; color: #27ae60;")
        self.deploy_btn.setEnabled(False)
        
        # Mettre à jour l'historique
        self.history_table.item(0, 3).setText("Déployé")
        
        self.statusBar().showMessage("Modèle déployé avec succès")
        logger.info("Modèle déployé avec succès")
    
    def check_for_updates(self):
        """Vérifie les mises à jour logicielles"""
        self.statusBar().showMessage("Vérification des mises à jour...")
        logger.info("Vérification des mises à jour logicielles...")
        
        # Dans un système réel, cela utiliserait l'auto updater
        # Ici, pour la démo, on simule
        time.sleep(0.3)
        
        # Simuler une mise à jour disponible
        self.alerts_label.setText("Alertes: Nouvelle version disponible (3.2.0)")
        self.alerts_label.setStyleSheet("color: #e67e22;")
        
        self.statusBar().showMessage("Nouvelle version disponible: 3.2.0")
        logger.info("Nouvelle version disponible: 3.2.0")

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    from updaters import TheoryValidator
    
    app = QApplication(sys.argv)
    
    # Créer les dépendances
    db_manager = DatabaseManager()
    theory_validator = TheoryValidator(db_manager)
    
    window = TurfMasterApp(
        db_manager=db_manager,
        theory_validator=theory_validator
    )
    window.show()
    
    sys.exit(app.exec_())