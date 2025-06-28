import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QComboBox, QPushButton, QTextEdit, QGroupBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy, QTabWidget,
    QDialog, QFormLayout, QDialogButtonBox, QMessageBox
)
from PyQt5.QtCore import Qt, QSettings, QDate
from PyQt5.QtGui import QFont, QDoubleValidator, QIcon


class ProductManagerDialog(QDialog):
    def __init__(self, products, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestion des Produits")
        self.setGeometry(300, 300, 500, 400)

        self.products = products
        self.modified = False

        layout = QVBoxLayout()

        # Tableau des produits
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Produit", "Cartouches/Carton", "Prix Usine Cartouche"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.populate_table()
        layout.addWidget(self.table)

        # Boutons d'action
        button_layout = QHBoxLayout()

        add_button = QPushButton("Ajouter")
        add_button.clicked.connect(self.add_product)
        button_layout.addWidget(add_button)

        edit_button = QPushButton("Modifier")
        edit_button.clicked.connect(self.edit_product)
        button_layout.addWidget(edit_button)

        remove_button = QPushButton("Supprimer")
        remove_button.clicked.connect(self.remove_product)
        button_layout.addWidget(remove_button)

        layout.addLayout(button_layout)

        # Boutons de dialogue
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def populate_table(self):
        self.table.setRowCount(len(self.products))

        for row, (name, details) in enumerate(self.products.items()):
            self.table.setItem(row, 0, QTableWidgetItem(name))
            self.table.setItem(row, 1, QTableWidgetItem(str(details["cartouches_par_carton"])))
            self.table.setItem(row, 2, QTableWidgetItem(f"{details['prix_usine_cartouche']:.2f}"))

    def add_product(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Ajouter un Produit")
        layout = QFormLayout()
        name_input = QLineEdit()
        layout.addRow("Nom du produit:", name_input)

        cartouches_input = QLineEdit()
        cartouches_input.setValidator(QDoubleValidator(1, 1000, 2))
        layout.addRow("Cartouches par carton:", cartouches_input)

        prix_input = QLineEdit()
        prix_input.setValidator(QDoubleValidator(0.01, 10000, 2))
        layout.addRow("Prix usine par cartouche:", prix_input)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addRow(button_box)

        dialog.setLayout(layout)

        if dialog.exec_() == QDialog.Accepted:
            name = name_input.text().strip()
            if name:
                try:
                    cartouches = int(cartouches_input.text())
                    prix = float(prix_input.text())
                    self.products[name] = {
                        "cartouches_par_carton": cartouches,
                        "prix_usine_cartouche": prix
                    }
                    self.modified = True
                    self.populate_table()
                except ValueError:
                    QMessageBox.warning(self, "Erreur", "Veuillez entrer des valeurs numériques valides")

    def edit_product(self):
        selected = self.table.currentRow()
        if selected < 0:
            return

        old_name = self.table.item(selected, 0).text()
        details = self.products[old_name]

        dialog = QDialog(self)
        dialog.setWindowTitle("Modifier le Produit")
        layout = QFormLayout()

        name_input = QLineEdit(old_name)
        layout.addRow("Nom du produit:", name_input)

        cartouches_input = QLineEdit(str(details["cartouches_par_carton"]))
        cartouches_input.setValidator(QDoubleValidator(1, 1000, 2))
        layout.addRow("Cartouches par carton:", cartouches_input)

        prix_input = QLineEdit(str(details["prix_usine_cartouche"]))
        prix_input.setValidator(QDoubleValidator(0.01, 10000, 2))
        layout.addRow("Prix usine par cartouche:", prix_input)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addRow(button_box)

        dialog.setLayout(layout)

        if dialog.exec_() == QDialog.Accepted:
            new_name = name_input.text().strip()
            if new_name:
                try:
                    cartouches = int(cartouches_input.text())
                    prix = float(prix_input.text())

                    # Si le nom a changé, supprimer l'ancienne entrée
                    if new_name != old_name:
                        del self.products[old_name]

                    self.products[new_name] = {
                        "cartouches_par_carton": cartouches,
                        "prix_usine_cartouche": prix
                    }
                    self.modified = True
                    self.populate_table()
                except ValueError:
                    QMessageBox.warning(self, "Erreur", "Veuillez entrer des valeurs numériques valides")

    def remove_product(self):
        selected = self.table.currentRow()
        if selected < 0:
            return

        name = self.table.item(selected, 0).text()
        reply = QMessageBox.question(
            self, "Confirmation",
            f"Êtes-vous sûr de vouloir supprimer le produit '{name}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            del self.products[name]
            self.modified = True
            self.populate_table()


class CigaretteCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rayane Serine - Calculatrice de Cigarettes")
        self.setGeometry(100, 100, 1200, 800)

        # Charger les produits
        self.load_products()

        # Historique des calculs
        self.historique = []

        # Initialisation des variables
        self.user_modified_y = False
        self.current_values = {
            'produit': "",
            'o': "",
            'y': "",
            't': "",
            'z': "",
            'l': "",
            'd': ""
        }

        # Setup UI
        self.init_ui()
        self.load_settings()

    def load_products(self):
        settings = QSettings("RayaneSerine", "CigaretteCalculator")
        products_json = settings.value("products", "{}")

        try:
            self.products = json.loads(products_json)
        except:
            # Valeurs par défaut si erreur de chargement
            self.products = {
                "Malboro": {"cartouches_par_carton": 50, "prix_usine_cartouche": 95},
                "Winston": {"cartouches_par_carton": 50, "prix_usine_cartouche": 90},
                "Chema": {"cartouches_par_carton": 25, "prix_usine_cartouche": 45},
                "Chique": {"cartouches_par_carton": 25, "prix_usine_cartouche": 40}
            }

    def save_products(self):
        settings = QSettings("RayaneSerine", "CigaretteCalculator")
        settings.setValue("products", json.dumps(self.products))

    def init_ui(self):
        # Widget principal et layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Onglets
        tab_widget = QTabWidget()
        calcul_tab = QWidget()
        recherche_tab = QWidget()
        historique_tab = QWidget()
        database_tab = QWidget()

        tab_widget.addTab(calcul_tab, "Calculatrice")
        tab_widget.addTab(recherche_tab, "Recherche de Cartons")
        tab_widget.addTab(historique_tab, "Historique")
        tab_widget.addTab(database_tab, "Base de Données")

        # Configuration des onglets
        self.setup_calcul_tab(calcul_tab)
        self.setup_recherche_tab(recherche_tab)
        self.setup_historique_tab(historique_tab)
        self.setup_database_tab(database_tab)

        main_layout.addWidget(tab_widget)
        self.setCentralWidget(main_widget)

        # Appliquer les styles
        self.apply_styles()

    def setup_calcul_tab(self, tab):
        layout = QHBoxLayout(tab)
        layout.setSpacing(20)
        layout.setContentsMargins(10, 10, 10, 10)

        # Panel gauche - Entrées de données
        input_group = QGroupBox("Entrées de Données")
        input_layout = QGridLayout()
        input_layout.setSpacing(15)
        input_layout.setColumnStretch(1, 1)

        # Sélection du produit
        input_layout.addWidget(QLabel("Produit:"), 0, 0)
        self.product_combo = QComboBox()
        self.product_combo.addItems(self.products.keys())
        self.product_combo.currentTextChanged.connect(self.on_product_changed)
        input_layout.addWidget(self.product_combo, 0, 1)

        # Prix cartouche usine (o)
        input_layout.addWidget(QLabel("Prix cartouche usine (o):"), 1, 0)
        self.o_input = QLineEdit()
        self.o_input.setPlaceholderText("Entrez le prix...")
        self.o_input.textChanged.connect(self.on_input_changed)
        input_layout.addWidget(self.o_input, 1, 1)

        # Nombre cartouches par carton (y)
        input_layout.addWidget(QLabel("Cartouches par carton (y):"), 2, 0)
        self.y_input = QLineEdit()
        self.y_input.setPlaceholderText("Entrez la quantité...")
        self.y_input.textChanged.connect(self.on_y_changed)
        input_layout.addWidget(self.y_input, 2, 1)

        # Prix carton usine (t)
        input_layout.addWidget(QLabel("Prix carton usine (t):"), 3, 0)
        self.t_input = QLineEdit()
        self.t_input.setPlaceholderText("Entrez le prix...")
        self.t_input.textChanged.connect(self.on_input_changed)
        input_layout.addWidget(self.t_input, 3, 1)

        # Coup informel (z)
        input_layout.addWidget(QLabel("Coût informel par carton (z):"), 4, 0)
        self.z_input = QLineEdit()
        self.z_input.setPlaceholderText("Entrez le coût...")
        self.z_input.textChanged.connect(self.on_input_changed)
        input_layout.addWidget(self.z_input, 4, 1)

        # Prix carton informel (l)
        input_layout.addWidget(QLabel("Prix carton informel (l):"), 5, 0)
        self.l_input = QLineEdit()
        self.l_input.setPlaceholderText("Entrez le prix...")
        self.l_input.textChanged.connect(self.on_input_changed)
        input_layout.addWidget(self.l_input, 5, 1)

        # Prix cartouche informel (d)
        input_layout.addWidget(QLabel("Prix cartouche informel (d):"), 6, 0)
        self.d_input = QLineEdit()
        self.d_input.setPlaceholderText("Entrez le prix...")
        self.d_input.textChanged.connect(self.on_input_changed)
        input_layout.addWidget(self.d_input, 6, 1)

        input_group.setLayout(input_layout)

        # Panel droit - Étapes de calcul
        result_group = QGroupBox("Étapes de Calcul")
        result_layout = QVBoxLayout()
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setFont(QFont("Consolas", 11))
        self.result_text.setStyleSheet("background-color: #f8f8f8;")
        result_layout.addWidget(self.result_text)
        result_group.setLayout(result_layout)

        # Bouton Calculer
        calc_button = QPushButton("Calculer Tout")
        calc_button.setFixedHeight(45)
        calc_button.setStyleSheet(
            "QPushButton {"
            "   background-color: #4CAF50;"
            "   color: white;"
            "   font-size: 16px;"
            "   font-weight: bold;"
            "   border-radius: 5px;"
            "}"
            "QPushButton:hover {"
            "   background-color: #45a049;"
            "}"
        )
        calc_button.clicked.connect(self.calculer_complet)

        # Bouton Sauvegarder
        save_button = QPushButton("Sauvegarder dans BD")
        save_button.setFixedHeight(45)
        save_button.setStyleSheet(
            "QPushButton {"
            "   background-color: #2196F3;"
            "   color: white;"
            "   font-size: 16px;"
            "   font-weight: bold;"
            "   border-radius: 5px;"
            "}"
            "QPushButton:hover {"
            "   background-color: #0b7dda;"
            "}"
        )
        save_button.clicked.connect(self.sauvegarder_donnees)

        button_layout = QVBoxLayout()
        button_layout.addWidget(calc_button)
        button_layout.addWidget(save_button)

        # Ajout des widgets au layout
        layout.addWidget(input_group, 1)
        layout.addWidget(result_group, 1)
        layout.addLayout(button_layout)

    def setup_recherche_tab(self, tab):
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)

        # Groupe de recherche
        search_group = QGroupBox("Recherche de Cartons par Cartouche")
        search_layout = QGridLayout()

        search_layout.addWidget(QLabel("Nom de cartouche:"), 0, 0)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Entrez le nom de la cartouche...")
        search_layout.addWidget(self.search_input, 0, 1)

        search_layout.addWidget(QLabel("Prix max par cartouche:"), 1, 0)
        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("Entrez le prix maximum...")
        search_layout.addWidget(self.price_input, 1, 1)

        search_button = QPushButton("Rechercher")
        search_button.setFixedHeight(40)
        search_button.setStyleSheet(
            "QPushButton {"
            "   background-color: #2196F3;"
            "   color: white;"
            "   font-size: 14px;"
            "   border-radius: 5px;"
            "}"
            "QPushButton:hover {"
            "   background-color: #0b7dda;"
            "}"
        )
        search_button.clicked.connect(self.rechercher_cartons)
        search_layout.addWidget(search_button, 2, 0, 1, 2)

        search_group.setLayout(search_layout)
        layout.addWidget(search_group)

        # Tableau des résultats
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels([
            "Produit", "Cartouches/Carton", "Prix Usine Cartouche",
            "Prix Usine Carton", "Coût Informel", "Prix Final Cartouche"
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.results_table, 1)

        # Bouton d'export
        export_button = QPushButton("Exporter les Résultats")
        export_button.setFixedHeight(40)
        export_button.setStyleSheet(
            "QPushButton {"
            "   background-color: #FF9800;"
            "   color: white;"
            "   font-size: 14px;"
            "   border-radius: 5px;"
            "}"
            "QPushButton:hover {"
            "   background-color: #e68a00;"
            "}"
        )
        export_button.clicked.connect(self.exporter_resultats)
        layout.addWidget(export_button)

    def setup_historique_tab(self, tab):
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Tableau d'historique
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(8)
        self.history_table.setHorizontalHeaderLabels([
            "Date", "Produit", "Cartouches", "Prix Usine C.", "Prix Usine Ct.",
            "Coût Inf.", "Prix Final Ct.", "Prix Final C."
        ])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.history_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)

        layout.addWidget(self.history_table)

        # Boutons d'historique
        button_layout = QHBoxLayout()

        clear_button = QPushButton("Effacer l'historique")
        clear_button.setStyleSheet(
            "QPushButton {"
            "   background-color: #f44336;"
            "   color: white;"
            "   font-size: 14px;"
            "   border-radius: 5px;"
            "}"
            "QPushButton:hover {"
            "   background-color: #d32f2f;"
            "}"
        )
        clear_button.clicked.connect(self.effacer_historique)

        export_hist_button = QPushButton("Exporter l'historique")
        export_hist_button.setStyleSheet(
            "QPushButton {"
            "   background-color: #9C27B0;"
            "   color: white;"
            "   font-size: 14px;"
            "   border-radius: 5px;"
            "}"
            "QPushButton:hover {"
            "   background-color: #7b1fa2;"
            "}"
        )
        export_hist_button.clicked.connect(self.exporter_historique)

        button_layout.addWidget(clear_button)
        button_layout.addWidget(export_hist_button)
        layout.addLayout(button_layout)

    def setup_database_tab(self, tab):
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)

        # Gestion des produits
        product_group = QGroupBox("Gestion des Produits")
        product_layout = QVBoxLayout()

        self.product_table = QTableWidget()
        self.product_table.setColumnCount(3)
        self.product_table.setHorizontalHeaderLabels(["Produit", "Cartouches/Carton", "Prix Usine Cartouche"])
        self.product_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.product_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.populate_product_table()
        product_layout.addWidget(self.product_table)

        # Boutons de gestion
        button_layout = QHBoxLayout()

        manage_button = QPushButton("Gérer les Produits")
        manage_button.clicked.connect(self.gerer_produits)
        button_layout.addWidget(manage_button)

        refresh_button = QPushButton("Actualiser")
        refresh_button.clicked.connect(self.populate_product_table)
        button_layout.addWidget(refresh_button)

        product_layout.addLayout(button_layout)
        product_group.setLayout(product_layout)
        layout.addWidget(product_group)

        # Gestion des valeurs
        value_group = QGroupBox("Valeurs Sauvegardées")
        value_layout = QVBoxLayout()

        self.value_table = QTableWidget()
        self.value_table.setColumnCount(7)
        self.value_table.setHorizontalHeaderLabels([
            "Produit", "o", "y", "t", "z", "l", "d"
        ])
        self.value_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.value_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.populate_value_table()
        value_layout.addWidget(self.value_table)

        # Boutons de gestion
        value_button_layout = QHBoxLayout()

        load_button = QPushButton("Charger")
        load_button.clicked.connect(self.charger_valeur)
        value_button_layout.addWidget(load_button)

        delete_button = QPushButton("Supprimer")
        delete_button.clicked.connect(self.supprimer_valeur)
        value_button_layout.addWidget(delete_button)

        value_layout.addLayout(value_button_layout)
        value_group.setLayout(value_layout)
        layout.addWidget(value_group)

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
            }

            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #ddd;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #f9f9f9;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
                color: #333;
            }

            QLabel {
                font-size: 14px;
                color: #444;
            }

            QLineEdit, QComboBox {
                font-size: 14px;
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
            }

            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
            }

            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                gridline-color: #eee;
            }

            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 5px;
                border: 1px solid #ddd;
                font-weight: bold;
            }

            QTabWidget::pane {
                border: 1px solid #ddd;
                border-radius: 4px;
                background: #f9f9f9;
            }

            QTabBar::tab {
                background: #e0e0e0;
                border: 1px solid #ccc;
                border-bottom-color: #ddd;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 16px;
                margin-right: 2px;
            }

            QTabBar::tab:selected {
                background: #f9f9f9;
                border-bottom-color: #f9f9f9;
            }
        """)

    def on_product_changed(self, product_name):
        self.current_values['produit'] = product_name
        if not self.user_modified_y:
            default_y = str(self.products.get(product_name, {}).get("cartouches_par_carton", ""))
            self.y_input.setText(default_y)
            self.current_values['y'] = default_y

        # Mettre à jour le prix usine par défaut
        default_o = str(self.products.get(product_name, {}).get("prix_usine_cartouche", ""))
        if not self.o_input.text().strip():
            self.o_input.setText(default_o)
            self.current_values['o'] = default_o

    def on_y_changed(self, text):
        self.user_modified_y = True
        self.current_values['y'] = text

    def on_input_changed(self, text):
        sender = self.sender()
        if sender == self.o_input:
            self.current_values['o'] = text
        elif sender == self.t_input:
            self.current_values['t'] = text
        elif sender == self.z_input:
            self.current_values['z'] = text
        elif sender == self.l_input:
            self.current_values['l'] = text
        elif sender == self.d_input:
            self.current_values['d'] = text

    def calculer_complet(self):
        # Effacer les résultats précédents
        self.result_text.clear()

        # Obtenir les valeurs actuelles
        valeurs = {k: v.strip() for k, v in self.current_values.items()}
        connues = {}
        for cle, valeur in valeurs.items():
            if cle == 'produit':
                continue
            if valeur != "":
                try:
                    connues[cle] = float(valeur)
                except ValueError:
                    self.result_text.append(
                        f"<span style='color:red'>Erreur: La valeur de {cle} n'est pas un nombre valide</span>")
                    return

        # Vérifier les valeurs minimales
        for cle, valeur in connues.items():
            if valeur < 0:
                self.result_text.append(
                    f"<span style='color:red'>Erreur: La valeur de {cle} ne peut pas être négative</span>")
                return

        # Afficher les valeurs initiales
        self.result_text.append("<b>Valeurs initiales fournies :</b>")
        for cle, valeur in valeurs.items():
            if cle == 'produit':
                if valeur != "":
                    self.result_text.append(f"  • Produit = {valeur}")
            elif valeur != "":
                self.result_text.append(f"  • {cle.upper()} = {valeur}")

        self.result_text.append("\n<b>Étapes de calcul :</b>")

        # Logique de calcul complète
        etapes = []
        calculees = {}

        # Calculer toutes les valeurs possibles
        # 1. t = o * y
        if 'o' in connues and 'y' in connues and 't' not in connues:
            t = connues['o'] * connues['y']
            etapes.append(f"1. Prix carton usine (t) = Prix cartouche usine (o) × Cartouches par carton (y)")
            etapes.append(f"   t = {connues['o']} × {connues['y']} = {t:.2f}")
            calculees['t'] = t
            self.t_input.setText(f"{t:.2f}")

        # 2. o = t / y
        if 't' in connues and 'y' in connues and 'o' not in connues:
            if connues['y'] != 0:
                o = connues['t'] / connues['y']
                etapes.append(f"2. Prix cartouche usine (o) = Prix carton usine (t) ÷ Cartouches par carton (y)")
                etapes.append(f"   o = {connues['t']} ÷ {connues['y']} = {o:.2f}")
                calculees['o'] = o
                self.o_input.setText(f"{o:.2f}")
            else:
                etapes.append(
                    "<span style='color:red'>Erreur: Division par zéro! Cartouches par carton (y) ne peut pas être zéro.</span>")

        # 3. y = t / o
        if 't' in connues and 'o' in connues and 'y' not in connues:
            if connues['o'] != 0:
                y = connues['t'] / connues['o']
                etapes.append(f"3. Cartouches par carton (y) = Prix carton usine (t) ÷ Prix cartouche usine (o)")
                etapes.append(f"   y = {connues['t']} ÷ {connues['o']} = {y:.2f}")
                calculees['y'] = y
                self.y_input.setText(f"{y:.2f}")
            else:
                etapes.append(
                    "<span style='color:red'>Erreur: Division par zéro! Prix cartouche usine (o) ne peut pas être zéro.</span>")

        # 4. l = t + z
        if 't' in connues and 'z' in connues and 'l' not in connues:
            l = connues['t'] + connues['z']
            etapes.append(f"4. Prix carton informel (l) = Prix carton usine (t) + Coût informel (z)")
            etapes.append(f"   l = {connues['t']} + {connues['z']} = {l:.2f}")
            calculees['l'] = l
            self.l_input.setText(f"{l:.2f}")

        # 5. z = l - t
        if 'l' in connues and 't' in connues and 'z' not in connues:
            z = connues['l'] - connues['t']
            etapes.append(f"5. Coût informel (z) = Prix carton informel (l) - Prix carton usine (t)")
            etapes.append(f"   z = {connues['l']} - {connues['t']} = {z:.2f}")
            calculees['z'] = z
            self.z_input.setText(f"{z:.2f}")

        # 6. t = l - z
        if 'l' in connues and 'z' in connues and 't' not in connues:
            t = connues['l'] - connues['z']
            etapes.append(f"6. Prix carton usine (t) = Prix carton informel (l) - Coût informel (z)")
            etapes.append(f"   t = {connues['l']} - {connues['z']} = {t:.2f}")
            calculees['t'] = t
            self.t_input.setText(f"{t:.2f}")

        # 7. d = l / y
        if 'l' in connues and 'y' in connues and 'd' not in connues:
            if connues['y'] != 0:
                d = connues['l'] / connues['y']
                etapes.append(f"7. Prix cartouche informel (d) = Prix carton informel (l) ÷ Cartouches par carton (y)")
                etapes.append(f"   d = {connues['l']} ÷ {connues['y']} = {d:.2f}")
                calculees['d'] = d
                self.d_input.setText(f"{d:.2f}")
            else:
                etapes.append(
                    "<span style='color:red'>Erreur: Division par zéro! Cartouches par carton (y) ne peut pas être zéro.</span>")

        # 8. l = d * y
        if 'd' in connues and 'y' in connues and 'l' not in connues:
            l = connues['d'] * connues['y']
            etapes.append(f"8. Prix carton informel (l) = Prix cartouche informel (d) × Cartouches par carton (y)")
            etapes.append(f"   l = {connues['d']} × {connues['y']} = {l:.2f}")
            calculees['l'] = l
            self.l_input.setText(f"{l:.2f}")

        # Mettre à jour les valeurs connues avec les calculées
        connues.update(calculees)

        # Afficher les étapes de calcul
        if etapes:
            for etape in etapes:
                if etape.startswith("<span"):
                    self.result_text.append(etape)
                else:
                    self.result_text.append(etape)
        else:
            self.result_text.append("Aucun calcul effectué. Veuillez fournir plus de valeurs.")

        # Afficher les valeurs calculées
        if calculees:
            self.result_text.append("\n<b>Valeurs calculées :</b>")
            for cle, val in calculees.items():
                self.result_text.append(f"  • {cle.upper()} = {val:.2f}")

        # Ajouter à l'historique
        if calculees or connues:
            historique_entry = {
                'date': QDate.currentDate().toString(Qt.ISODate),
                'produit': self.current_values['produit'],
                'o': self.o_input.text(),
                'y': self.y_input.text(),
                't': self.t_input.text(),
                'z': self.z_input.text(),
                'l': self.l_input.text(),
                'd': self.d_input.text()
            }
            self.historique.append(historique_entry)
            self.mettre_a_jour_historique()

    def rechercher_cartons(self):
        terme = self.search_input.text().strip().lower()
        prix_max = self.price_input.text().strip()

        try:
            prix_max = float(prix_max) if prix_max else float('inf')
        except ValueError:
            prix_max = float('inf')

        resultats = []

        for produit, details in self.products.items():
            if terme and terme not in produit.lower():
                continue

            # Calculer les prix
            o = details['prix_usine_cartouche']
            y = details['cartouches_par_carton']
            t = o * y
            d = o  # Par défaut, sans coût informel

            # Si un prix max est spécifié, vérifier
            if d > prix_max:
                continue

            resultats.append({
                'produit': produit,
                'y': y,
                'o': o,
                't': t,
                'z': 0,  # Coût informel non appliqué
                'd': d
            })

        # Afficher les résultats dans le tableau
        self.results_table.setRowCount(len(resultats))

        for ligne, resultat in enumerate(resultats):
            self.results_table.setItem(ligne, 0, QTableWidgetItem(resultat['produit']))
            self.results_table.setItem(ligne, 1, QTableWidgetItem(str(resultat['y'])))
            self.results_table.setItem(ligne, 2, QTableWidgetItem(f"{resultat['o']:.2f}"))
            self.results_table.setItem(ligne, 3, QTableWidgetItem(f"{resultat['t']:.2f}"))
            self.results_table.setItem(ligne, 4, QTableWidgetItem(f"{resultat['z']:.2f}"))
            self.results_table.setItem(ligne, 5, QTableWidgetItem(f"{resultat['d']:.2f}"))

    def exporter_resultats(self):
        # Cette fonction exporterait normalement les résultats
        # Dans cette version, nous affichons un message
        self.result_text.append(
            "\n<b>Fonctionnalité d'export:</b> Les résultats seraient exportés vers un fichier CSV.")
        QMessageBox.information(self, "Export", "Les résultats seraient exportés vers un fichier CSV.")

    def mettre_a_jour_historique(self):
        self.history_table.setRowCount(len(self.historique))

        for ligne, entry in enumerate(self.historique):
            self.history_table.setItem(ligne, 0, QTableWidgetItem(entry['date']))
            self.history_table.setItem(ligne, 1, QTableWidgetItem(entry['produit']))
            self.history_table.setItem(ligne, 2, QTableWidgetItem(entry['y']))
            self.history_table.setItem(ligne, 3, QTableWidgetItem(entry['o']))
            self.history_table.setItem(ligne, 4, QTableWidgetItem(entry['t']))
            self.history_table.setItem(ligne, 5, QTableWidgetItem(entry['z']))
            self.history_table.setItem(ligne, 6, QTableWidgetItem(entry['l']))
            self.history_table.setItem(ligne, 7, QTableWidgetItem(entry['d']))

    def effacer_historique(self):
        self.historique = []
        self.history_table.setRowCount(0)

    def exporter_historique(self):
        # Cette fonction exporterait normalement l'historique
        # Dans cette version, nous affichons un message
        self.result_text.append("\n<b>Fonctionnalité d'export:</b> L'historique serait exporté vers un fichier CSV.")
        QMessageBox.information(self, "Export", "L'historique serait exporté vers un fichier CSV.")

    def gerer_produits(self):
        dialog = ProductManagerDialog(self.products, self)
        if dialog.exec_() == QDialog.Accepted and dialog.modified:
            self.save_products()
            self.product_combo.clear()
            self.product_combo.addItems(self.products.keys())
            self.populate_product_table()

    def populate_product_table(self):
        self.product_table.setRowCount(len(self.products))

        for row, (name, details) in enumerate(self.products.items()):
            self.product_table.setItem(row, 0, QTableWidgetItem(name))
            self.product_table.setItem(row, 1, QTableWidgetItem(str(details["cartouches_par_carton"])))
            self.product_table.setItem(row, 2, QTableWidgetItem(f"{details['prix_usine_cartouche']:.2f}"))

    def populate_value_table(self):
        settings = QSettings("RayaneSerine", "CigaretteCalculator")
        saved_values = settings.value("saved_values", "{}")

        try:
            values_db = json.loads(saved_values)
        except:
            values_db = {}

        self.value_table.setRowCount(len(values_db))

        for row, (name, values) in enumerate(values_db.items()):
            self.value_table.setItem(row, 0, QTableWidgetItem(name))
            self.value_table.setItem(row, 1, QTableWidgetItem(values.get('o', '')))
            self.value_table.setItem(row, 2, QTableWidgetItem(values.get('y', '')))
            self.value_table.setItem(row, 3, QTableWidgetItem(values.get('t', '')))
            self.value_table.setItem(row, 4, QTableWidgetItem(values.get('z', '')))
            self.value_table.setItem(row, 5, QTableWidgetItem(values.get('l', '')))
            self.value_table.setItem(row, 6, QTableWidgetItem(values.get('d', '')))

    def charger_valeur(self):
        selected = self.value_table.currentRow()
        if selected < 0:
            return

        name = self.value_table.item(selected, 0).text()

        settings = QSettings("RayaneSerine", "CigaretteCalculator")
        saved_values = json.loads(settings.value("saved_values", "{}"))

        if name in saved_values:
            values = saved_values[name]
            self.product_combo.setCurrentText(name)
            self.o_input.setText(values.get('o', ''))
            self.y_input.setText(values.get('y', ''))
            self.t_input.setText(values.get('t', ''))
            self.z_input.setText(values.get('z', ''))
            self.l_input.setText(values.get('l', ''))
            self.d_input.setText(values.get('d', ''))

            # Mettre à jour les valeurs courantes
            self.current_values = {
                'produit': name,
                'o': values.get('o', ''),
                'y': values.get('y', ''),
                't': values.get('t', ''),
                'z': values.get('z', ''),
                'l': values.get('l', ''),
                'd': values.get('d', '')
            }

    def supprimer_valeur(self):
        selected = self.value_table.currentRow()
        if selected < 0:
            return

        name = self.value_table.item(selected, 0).text()
        reply = QMessageBox.question(
            self, "Confirmation",
            f"Êtes-vous sûr de vouloir supprimer les valeurs sauvegardées pour '{name}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            settings = QSettings("RayaneSerine", "CigaretteCalculator")
            saved_values = json.loads(settings.value("saved_values", "{}"))

            if name in saved_values:
                del saved_values[name]
                settings.setValue("saved_values", json.dumps(saved_values))
                self.populate_value_table()

    def sauvegarder_donnees(self):
        name = self.current_values['produit']
        if not name:
            QMessageBox.warning(self, "Erreur", "Veuillez d'abord sélectionner un produit")
            return

        settings = QSettings("RayaneSerine", "CigaretteCalculator")
        saved_values = json.loads(settings.value("saved_values", "{}"))

        saved_values[name] = {
            'o': self.o_input.text(),
            'y': self.y_input.text(),
            't': self.t_input.text(),
            'z': self.z_input.text(),
            'l': self.l_input.text(),
            'd': self.d_input.text()
        }

        settings.setValue("saved_values", json.dumps(saved_values))
        self.populate_value_table()

        QMessageBox.information(self, "Succès", f"Les valeurs pour '{name}' ont été sauvegardées")

    def load_settings(self):
        settings = QSettings("RayaneSerine", "CigaretteCalculator")

        # Restaurer la géométrie de la fenêtre
        self.restoreGeometry(settings.value("geometry", b""))

        # Restaurer le produit
        product = settings.value("product", "Malboro")
        if product in self.products:
            self.product_combo.setCurrentText(product)

        # Restaurer les valeurs d'entrée
        self.o_input.setText(settings.value("o", ""))
        self.y_input.setText(settings.value("y", ""))
        self.t_input.setText(settings.value("t", ""))
        self.z_input.setText(settings.value("z", ""))
        self.l_input.setText(settings.value("l", ""))
        self.d_input.setText(settings.value("d", ""))

        # Mettre à jour les valeurs courantes
        self.current_values = {
            'produit': product,
            'o': settings.value("o", ""),
            'y': settings.value("y", ""),
            't': settings.value("t", ""),
            'z': settings.value("z", ""),
            'l': settings.value("l", ""),
            'd': settings.value("d", "")
        }

        # Vérifier si y a été modifié
        saved_y = settings.value("y", "")
        default_y = str(self.products.get(product, {}).get("cartouches_par_carton", ""))
        self.user_modified_y = (saved_y != "" and saved_y != default_y)

    def closeEvent(self, event):
        settings = QSettings("RayaneSerine", "CigaretteCalculator")

        # Sauvegarder la géométrie de la fenêtre
        settings.setValue("geometry", self.saveGeometry())

        # Sauvegarder le produit
        settings.setValue("product", self.product_combo.currentText())

        # Sauvegarder les valeurs d'entrée
        settings.setValue("o", self.o_input.text())
        settings.setValue("y", self.y_input.text())
        settings.setValue("t", self.t_input.text())
        settings.setValue("z", self.z_input.text())
        settings.setValue("l", self.l_input.text())
        settings.setValue("d", self.d_input.text())

        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CigaretteCalculator()
    window.show()
    sys.exit(app.exec_())