import sys
import json
import os
import openpyxl
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QComboBox, QPushButton, QTextEdit, QGroupBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy, QTabWidget,
    QDialog, QFormLayout, QDialogButtonBox, QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt, QSettings, QDate, QRegExp
from PyQt5.QtGui import QFont, QDoubleValidator, QIcon, QRegExpValidator, QValidator


class DecimalValidator(QValidator):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.regex = QRegExp(r'^\d*\.?\d*$')  # Allows numbers with optional decimal point

    def validate(self, input_text, pos):
        if self.regex.exactMatch(input_text):
            return (QValidator.Acceptable, input_text, pos)
        return (QValidator.Invalid, input_text, pos)


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
            self.table.setItem(row, 1, QTableWidgetItem(f"{details['cartouches_par_carton']:.3f}"))
            self.table.setItem(row, 2, QTableWidgetItem(f"{details['prix_usine_cartouche']:.3f}"))

    def add_product(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Ajouter un Produit")
        layout = QFormLayout()
        name_input = QLineEdit()
        layout.addRow("Nom du produit:", name_input)

        cartouches_input = QLineEdit()
        cartouches_input.setValidator(DecimalValidator())
        cartouches_input.setPlaceholderText("Ex: 50.000")
        layout.addRow("Cartouches par carton:", cartouches_input)

        prix_input = QLineEdit()
        prix_input.setValidator(DecimalValidator())
        prix_input.setPlaceholderText("Ex: 95.500")
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
                    cartouches = float(cartouches_input.text())
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

        cartouches_input = QLineEdit(f"{details['cartouches_par_carton']:.3f}")
        cartouches_input.setValidator(DecimalValidator())
        layout.addRow("Cartouches par carton:", cartouches_input)

        prix_input = QLineEdit(f"{details['prix_usine_cartouche']:.3f}")
        prix_input.setValidator(DecimalValidator())
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
                    cartouches = float(cartouches_input.text())
                    prix = float(prix_input.text())

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

        self.load_products()
        self.historique = []
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

        self.init_ui()
        self.load_settings()

    def load_products(self):
        settings = QSettings("RayaneSerine", "CigaretteCalculator")
        products_json = settings.value("products", "{}")

        try:
            self.products = json.loads(products_json)
        except:
            self.products = {
                "Malboro": {"cartouches_par_carton": 50.0, "prix_usine_cartouche": 95.0},
                "Winston": {"cartouches_par_carton": 50.0, "prix_usine_cartouche": 90.0},
                "Chema": {"cartouches_par_carton": 25.0, "prix_usine_cartouche": 45.0},
                "Chique": {"cartouches_par_carton": 25.0, "prix_usine_cartouche": 40.0}
            }

    def save_products(self):
        settings = QSettings("RayaneSerine", "CigaretteCalculator")
        settings.setValue("products", json.dumps(self.products))

    def init_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        tab_widget = QTabWidget()
        calcul_tab = QWidget()
        recherche_tab = QWidget()
        historique_tab = QWidget()
        database_tab = QWidget()

        tab_widget.addTab(calcul_tab, "Calculatrice")
        tab_widget.addTab(recherche_tab, "Recherche de Cartons")
        tab_widget.addTab(historique_tab, "Historique")
        tab_widget.addTab(database_tab, "Base de Données")

        self.setup_calcul_tab(calcul_tab)
        self.setup_recherche_tab(recherche_tab)
        self.setup_historique_tab(historique_tab)
        self.setup_database_tab(database_tab)

        main_layout.addWidget(tab_widget)
        self.setCentralWidget(main_widget)
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
        input_layout.addWidget(QLabel("->Prix cartouche usine (o):"), 1, 0)
        self.o_input = QLineEdit()
        self.o_input.setPlaceholderText("Entrez le prix...")
        self.o_input.setValidator(DecimalValidator())
        input_layout.addWidget(self.o_input, 1, 1)

        # Nombre cartouches par carton (y)
        input_layout.addWidget(QLabel("->nombre Cartouches en carton (y):"), 2, 0)
        self.y_input = QLineEdit()
        self.y_input.setPlaceholderText("Entrez la quantité...")
        self.y_input.setValidator(DecimalValidator())
        input_layout.addWidget(self.y_input, 2, 1)

        # Prix carton usine (t)
        input_layout.addWidget(QLabel("Prix carton en usine (t):"), 3, 0)
        self.t_input = QLineEdit()
        self.t_input.setPlaceholderText("Entrez le prix...")
        self.t_input.setValidator(DecimalValidator())
        input_layout.addWidget(self.t_input, 3, 1)

        # Coup informel (z)
        input_layout.addWidget(QLabel("-->Coût informel de hmed (z)<--:"), 4, 0)
        self.z_input = QLineEdit()
        self.z_input.setPlaceholderText("Entrez le coût...")
        self.z_input.setValidator(DecimalValidator())
        input_layout.addWidget(self.z_input, 4, 1)

        # Prix carton informel (l)
        input_layout.addWidget(QLabel("Prix carton en informel (l):"), 5, 0)
        self.l_input = QLineEdit()
        self.l_input.setPlaceholderText("Entrez le prix...")
        self.l_input.setValidator(DecimalValidator())
        input_layout.addWidget(self.l_input, 5, 1)

        # Prix cartouche informel (d)
        input_layout.addWidget(QLabel("!! Prix cartouche informel (d) !!:"), 6, 0)
        self.d_input = QLineEdit()
        self.d_input.setPlaceholderText("Entrez le prix...")
        self.d_input.setValidator(DecimalValidator())
        input_layout.addWidget(self.d_input, 6, 1)
        input_group.setLayout(input_layout)

        # Panel droit - Étapes de calcul
        result_group = QGroupBox(" 🥶 Étapes de Calcul 🥶")
        result_layout = QVBoxLayout()
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setFont(QFont("Consolas", 11))
        self.result_text.setStyleSheet("background-color: #f0caad;")
        result_layout.addWidget(self.result_text)
        result_group.setLayout(result_layout)

        # Boutons d'action
        button_layout = QVBoxLayout()

        # Layout pour les boutons Calculer et Reset
        calc_reset_layout = QHBoxLayout()

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

        reset_button = QPushButton("Réinitialiser")
        reset_button.setFixedHeight(45)
        reset_button.setStyleSheet(
            "QPushButton {"
            "   background-color: #f44336;"
            "   color: white;"
            "   font-size: 16px;"
            "   font-weight: bold;"
            "   border-radius: 5px;"
            "}"
            "QPushButton:hover {"
            "   background-color: #d32f2f;"
            "}"
        )
        reset_button.clicked.connect(self.reset_calculator)

        calc_reset_layout.addWidget(calc_button)
        calc_reset_layout.addWidget(reset_button)
        button_layout.addLayout(calc_reset_layout)

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
        button_layout.addWidget(save_button)

        # Ajout des widgets au layout
        layout.addWidget(input_group, 1)
        layout.addWidget(result_group, 1)
        layout.addLayout(button_layout)

    def reset_calculator(self):
        self.product_combo.setCurrentIndex(0)
        self.o_input.clear()
        self.y_input.clear()
        self.t_input.clear()
        self.z_input.clear()
        self.l_input.clear()
        self.d_input.clear()
        self.result_text.clear()

        self.current_values = {
            'produit': "",
            'o': "",
            'y': "",
            't': "",
            'z': "",
            'l': "",
            'd': ""
        }
        self.user_modified_y = False

    def on_product_changed(self, product_name):
        if not product_name:
            return

        self.current_values['produit'] = product_name

        # Update y (cartouches par carton)
        if not self.user_modified_y:
            default_y = f"{self.products[product_name]['cartouches_par_carton']:.3f}"
            self.y_input.setText(default_y)
            self.current_values['y'] = default_y

        # Update o (prix usine cartouche)
        default_o = f"{self.products[product_name]['prix_usine_cartouche']:.3f}"
        self.o_input.setText(default_o)
        self.current_values['o'] = default_o

    def calculer_complet(self):
        # Effacer les résultats précédents
        self.result_text.clear()

        # Obtenir les valeurs actuelles
        valeurs = {
            'produit': self.product_combo.currentText(),
            'o': self.o_input.text().strip(),
            'y': self.y_input.text().strip(),
            't': self.t_input.text().strip(),
            'z': self.z_input.text().strip(),
            'l': self.l_input.text().strip(),
            'd': self.d_input.text().strip()
        }

        connues = {}

        # Vérifier d'abord que nous avons au moins un produit sélectionné
        if not valeurs['produit']:
            self.result_text.append("<span style='color:red'>Erreur: Veuillez sélectionner un produit</span>")
            return

        # Convertir les valeurs en nombres
        for cle, valeur in valeurs.items():
            if cle == 'produit':
                continue
            if valeur != "":
                try:
                    # Remplacer les virgules par des points pour la conversion
                    valeur = valeur.replace(',', '.')
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

        # Afficher les valeurs initiales fournies
        self.result_text.append("<b>Valeurs initiales fournies :</b>")
        for cle, valeur in valeurs.items():
            if cle == 'produit':
                if valeur != "":
                    self.result_text.append(f"  • Produit = {valeur}")
            elif valeur != "":
                self.result_text.append(f"  • {cle.upper()} = {valeur}")

        self.result_text.append("\n<b>Étapes de calcul :</b>")

        # Logique de calcul complète avec toutes les combinaisons possibles
        calculees = {}
        etapes = []

        # Liste de toutes les relations possibles (y compris les inverses)
        relations = [
            # Relations de base
            {'vars': ['o', 'y'], 'calc': 't', 'formule': 't = o × y', 'operation': lambda o, y: o * y},
            {'vars': ['t', 'y'], 'calc': 'o', 'formule': 'o = t ÷ y',
             'operation': lambda t, y: t / y if y != 0 else None},
            {'vars': ['t', 'o'], 'calc': 'y', 'formule': 'y = t ÷ o',
             'operation': lambda t, o: t / o if o != 0 else None},

            # Relations informelles
            {'vars': ['t', 'z'], 'calc': 'l', 'formule': 'l = t + z', 'operation': lambda t, z: t + z},
            {'vars': ['l', 't'], 'calc': 'z', 'formule': 'z = l - t', 'operation': lambda l, t: l - t},
            {'vars': ['l', 'z'], 'calc': 't', 'formule': 't = l - z', 'operation': lambda l, z: l - z},

            # Relations cartouche informelle
            {'vars': ['l', 'y'], 'calc': 'd', 'formule': 'd = l ÷ y',
             'operation': lambda l, y: l / y if y != 0 else None},
            {'vars': ['d', 'y'], 'calc': 'l', 'formule': 'l = d × y', 'operation': lambda d, y: d * y},
            {'vars': ['l', 'd'], 'calc': 'y', 'formule': 'y = l ÷ d',
             'operation': lambda l, d: l / d if d != 0 else None},

            # Nouvelles relations inverses
            {'vars': ['d', 'o'], 'calc': 'marge', 'formule': 'marge = d - o', 'operation': lambda d, o: d - o},
            {'vars': ['d', 'y'], 'calc': 'l', 'formule': 'l = d × y', 'operation': lambda d, y: d * y},
            {'vars': ['l', 't'], 'calc': 'z', 'formule': 'z = l - t', 'operation': lambda l, t: l - t},
        ]

        # Effectuer tous les calculs possibles en plusieurs passes
        changed = True
        passes = 0
        max_passes = 5  # Pour éviter les boucles infinies

        while changed and passes < max_passes:
            changed = False
            passes += 1

            for rel in relations:
                # Vérifier si on a toutes les variables nécessaires et que la variable à calculer n'est pas déjà connue
                if all(v in connues for v in rel['vars']) and rel['calc'] not in connues:

                    # Récupérer les valeurs
                    values = [connues[v] for v in rel['vars']]

                    # Effectuer le calcul
                    try:
                        result = rel['operation'](*values)
                        if result is not None:  # Vérifier pour les divisions par zéro
                            connues[rel['calc']] = result
                            etapes.append(
                                f"{len(etapes) + 1}. {rel['formule']} = {' × '.join(str(v) for v in values) if '×' in rel['formule'] else ' ÷ '.join(str(v) for v in values) if '÷' in rel['formule'] else ' + '.join(str(v) for v in values) if '+' in rel['formule'] else ' - '.join(str(v) for v in values)} = {result:.3f}")
                            changed = True
                    except:
                        pass

        # Mettre à jour les champs avec les valeurs calculées
        for var in ['o', 'y', 't', 'z', 'l', 'd']:
            if var in connues:
                getattr(self, f"{var}_input").setText(f"{connues[var]:.3f}")

        # Afficher les étapes de calcul
        if etapes:
            for etape in etapes:
                self.result_text.append(etape)
        else:
            self.result_text.append("Aucun calcul effectué. Veuillez fournir plus de valeurs.")

        # Afficher les valeurs calculées
        if connues:
            self.result_text.append("\n<b>Valeurs calculées :</b>")
            for cle in ['o', 'y', 't', 'z', 'l', 'd']:
                if cle in connues and cle not in valeurs:
                    self.result_text.append(f"  • {cle.upper()} = {connues[cle]:.3f}")

        # Calculer et afficher les marges si possible
        if 'd' in connues and 'o' in connues:
            marge = connues['d'] - connues['o']
            self.result_text.append(f"\n<b>Marge par cartouche:</b> {marge:.3f}")

            if 'y' in connues:
                marge_totale = marge * connues['y']
                self.result_text.append(f"<b>Marge totale par carton:</b> {marge_totale:.3f}")

        # Ajouter à l'historique si des calculs ont été effectués
        if connues:
            historique_entry = {
                'date': QDate.currentDate().toString(Qt.ISODate),
                'produit': valeurs['produit'],
                'o': self.o_input.text(),
                'y': self.y_input.text(),
                't': self.t_input.text(),
                'z': self.z_input.text(),
                'l': self.l_input.text(),
                'd': self.d_input.text()
            }
            self.historique.append(historique_entry)
            self.mettre_a_jour_historique()

    def setup_recherche_tab(self, tab):
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)

        search_group = QGroupBox("Recherche de Cartons par Cartouche")
        search_layout = QGridLayout()

        search_layout.addWidget(QLabel("Nom de cartouche:"), 0, 0)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Entrez le nom de la cartouche...")
        search_layout.addWidget(self.search_input, 0, 1)

        search_layout.addWidget(QLabel("Prix max par cartouche:"), 1, 0)
        self.price_input = QLineEdit()
        self.price_input.setValidator(DecimalValidator())
        self.price_input.setPlaceholderText("Ex: 200.500")
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

        product_group = QGroupBox("Gestion des Produits")
        product_layout = QVBoxLayout()

        self.product_table = QTableWidget()
        self.product_table.setColumnCount(3)
        self.product_table.setHorizontalHeaderLabels(["Produit", "Cartouches/Carton", "Prix Usine Cartouche"])
        self.product_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.product_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.populate_product_table()
        product_layout.addWidget(self.product_table)

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

            o = details['prix_usine_cartouche']
            y = details['cartouches_par_carton']
            t = o * y
            d = o  # Default without informal cost

            if d > prix_max:
                continue

            resultats.append({
                'produit': produit,
                'y': y,
                'o': o,
                't': t,
                'z': 0,
                'd': d
            })

        self.results_table.setRowCount(len(resultats))

        for ligne, resultat in enumerate(resultats):
            self.results_table.setItem(ligne, 0, QTableWidgetItem(resultat['produit']))
            self.results_table.setItem(ligne, 1, QTableWidgetItem(f"{resultat['y']:.3f}"))
            self.results_table.setItem(ligne, 2, QTableWidgetItem(f"{resultat['o']:.3f}"))
            self.results_table.setItem(ligne, 3, QTableWidgetItem(f"{resultat['t']:.3f}"))
            self.results_table.setItem(ligne, 4, QTableWidgetItem(f"{resultat['z']:.3f}"))
            self.results_table.setItem(ligne, 5, QTableWidgetItem(f"{resultat['d']:.3f}"))

    def exporter_resultats(self):
        if self.results_table.rowCount() == 0:
            QMessageBox.warning(self, "Erreur", "Aucune donnée à exporter")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exporter les résultats", "", "Fichiers Excel (*.xlsx);;Tous les fichiers (*)")

        if not file_path:
            return

        try:
            workbook = openpyxl.Workbook()
            sheet = workbook.active
            sheet.title = "Résultats de recherche"

            headers = []
            for col in range(self.results_table.columnCount()):
                headers.append(self.results_table.horizontalHeaderItem(col).text())
            sheet.append(headers)

            for row in range(self.results_table.rowCount()):
                row_data = []
                for col in range(self.results_table.columnCount()):
                    item = self.results_table.item(row, col)
                    row_data.append(item.text() if item else "")
                sheet.append(row_data)

            workbook.save(file_path)
            QMessageBox.information(self, "Succès", f"Les résultats ont été exportés vers {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue lors de l'export:\n{str(e)}")

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
        reply = QMessageBox.question(
            self, "Confirmation",
            "Êtes-vous sûr de vouloir effacer tout l'historique?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.historique = []
            self.history_table.setRowCount(0)

    def exporter_historique(self):
        if not self.historique:
            QMessageBox.warning(self, "Erreur", "L'historique est vide")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exporter l'historique", "", "Fichiers Excel (*.xlsx);;Tous les fichiers (*)")

        if not file_path:
            return

        try:
            workbook = openpyxl.Workbook()
            sheet = workbook.active
            sheet.title = "Historique des calculs"

            headers = [
                "Date", "Produit", "Cartouches", "Prix Usine C.", "Prix Usine Ct.",
                "Coût Inf.", "Prix Final Ct.", "Prix Final C."
            ]
            sheet.append(headers)

            for entry in self.historique:
                row_data = [
                    entry['date'],
                    entry['produit'],
                    entry['y'],
                    entry['o'],
                    entry['t'],
                    entry['z'],
                    entry['l'],
                    entry['d']
                ]
                sheet.append(row_data)

            workbook.save(file_path)
            QMessageBox.information(self, "Succès", f"L'historique a été exporté vers {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue lors de l'export:\n{str(e)}")

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
            self.product_table.setItem(row, 1, QTableWidgetItem(f"{details['cartouches_par_carton']:.3f}"))
            self.product_table.setItem(row, 2, QTableWidgetItem(f"{details['prix_usine_cartouche']:.3f}"))

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

        self.restoreGeometry(settings.value("geometry", b""))

        product = settings.value("product", "Malboro")
        if product in self.products:
            self.product_combo.setCurrentText(product)

        self.o_input.setText(settings.value("o", ""))
        self.y_input.setText(settings.value("y", ""))
        self.t_input.setText(settings.value("t", ""))
        self.z_input.setText(settings.value("z", ""))
        self.l_input.setText(settings.value("l", ""))
        self.d_input.setText(settings.value("d", ""))

        self.current_values = {
            'produit': product,
            'o': settings.value("o", ""),
            'y': settings.value("y", ""),
            't': settings.value("t", ""),
            'z': settings.value("z", ""),
            'l': settings.value("l", ""),
            'd': settings.value("d", "")
        }

        saved_y = settings.value("y", "")
        default_y = str(self.products.get(product, {}).get("cartouches_par_carton", ""))
        self.user_modified_y = (saved_y != "" and saved_y != default_y)

    def closeEvent(self, event):
        settings = QSettings("RayaneSerine", "CigaretteCalculator")

        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("product", self.product_combo.currentText())
        settings.setValue("o", self.o_input.text())
        settings.setValue("y", self.y_input.text())
        settings.setValue("t", self.t_input.text())
        settings.setValue("z", self.z_input.text())
        settings.setValue("l", self.l_input.text())
        settings.setValue("d", self.d_input.text())

        super().closeEvent(event)

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CigaretteCalculator()
    window.show()
    sys.exit(app.exec_())