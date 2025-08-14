# gestion_studio.py
# -*- coding: utf-8 -*-
"""
Application de gestion avancée pour :
- Personnel
- Accords avec d'autres créateurs
- État des lieux des lignes de bus

Ajouts demandés
- Rôle **Mappeur** :
    * Personnel & Accords : lecture seule (pas d'ajout, pas de modification, pas de suppression)
    * Lignes de bus : ajout & modification autorisés, suppression interdite
    * Export : autorisé uniquement pour l'onglet Lignes de bus
    * Sauvegarde de la base : interdit
- Journal d'audit (SQLite) + visionneuse (menu Admin)

Technos : PySide6 (Qt), SQLite (QSQLITE), bcrypt (hash)
"""

import sys
import os
import sqlite3
from datetime import datetime

import bcrypt
from PySide6.QtCore import Qt, QSortFilterProxyModel, QRegularExpression, QModelIndex
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QTabWidget, QMessageBox, QTableView, QFileDialog, QLabel, QProgressBar, QStatusBar,
    QCheckBox, QDialog, QFormLayout, QComboBox, QDialogButtonBox
)
from PySide6.QtSql import QSqlDatabase, QSqlTableModel

APP_TITLE = "Gestion Studio — Personnel · Accords · Lignes de bus"
DB_NAME = "gestion.db"

# --------- AUDIT ---------
def log_action(utilisateur: str, action: str):
    """Enregistre une action dans la table journal_audit."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO journal_audit (date_heure, utilisateur, action)
        VALUES (?, ?, ?)
        """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), utilisateur, action))
        conn.commit()
        conn.close()
    except Exception:
        pass  # éviter de bloquer l'app si le log échoue


# --------- UTIL DB ---------
def ensure_db(path: str):
    """Crée la base et les tables si nécessaire et injecte un admin par défaut si besoin."""
    first_time = not os.path.exists(path)
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS personnel (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        poste TEXT,
        email TEXT,
        telephone TEXT,
        disponibilite TEXT,
        actif INTEGER DEFAULT 1,
        notes TEXT
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS accords (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        partenaire TEXT NOT NULL,
        objet TEXT,
        date_debut TEXT,
        date_fin TEXT,
        statut TEXT,
        montant_estime REAL,
        notes TEXT
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS lignes_bus (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT NOT NULL,
        nom TEXT,
        chef_projet TEXT,
        progression INTEGER DEFAULT 0,
        phase TEXT,
        date_cible TEXT,
        priorite TEXT,
        notes TEXT
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS utilisateurs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom_utilisateur TEXT UNIQUE NOT NULL,
        mot_de_passe TEXT NOT NULL,
        role TEXT NOT NULL
    );
    """)
    # Journal d'audit
    cur.execute("""
    CREATE TABLE IF NOT EXISTS journal_audit (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date_heure TEXT NOT NULL,
        utilisateur TEXT NOT NULL,
        action TEXT NOT NULL
    );
    """)
    conn.commit()

    # Admin par défaut si table vide
    cur.execute("SELECT COUNT(*) FROM utilisateurs")
    count = cur.fetchone()[0]
    if count == 0:
        username = "admin"
        password = "admin123"
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        cur.execute("INSERT INTO utilisateurs (nom_utilisateur, mot_de_passe, role) VALUES (?, ?, ?)",
                    (username, hashed, "Admin"))
        conn.commit()
    conn.close()
    return first_time

def connect_qt_sql(db_path: str):
    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName(db_path)
    if not db.open():
        raise RuntimeError("Impossible d'ouvrir la base SQLite")
    return db

# --------- DIALOGUES ---------
class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Connexion")
        self.resize(380, 160)

        self.user = QLineEdit()
        self.user.setPlaceholderText("Nom d'utilisateur")
        self.pwd = QLineEdit()
        self.pwd.setEchoMode(QLineEdit.Password)
        self.pwd.setPlaceholderText("Mot de passe")

        form = QFormLayout()
        form.addRow("Utilisateur", self.user)
        form.addRow("Mot de passe", self.pwd)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        lay = QVBoxLayout(self)
        lay.addLayout(form)
        lay.addWidget(self.buttons)

    def get_credentials(self):
        return self.user.text().strip(), self.pwd.text()

class UserEditorDialog(QDialog):
    """Ajout / édition d'utilisateur par Admin."""
    def __init__(self, username="", role="Mappeur", set_password=True, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Utilisateur")
        self.resize(420, 200)
        self.name = QLineEdit(username)
        self.role = QComboBox()
        # Liste des rôles disponibles
        self.role.addItems(["Admin", "Mappeur", "Beta Testeur"])
        if role:
            idx = self.role.findText(role)
            if idx >= 0:
                self.role.setCurrentIndex(idx)
        self.pwd = QLineEdit()
        self.pwd.setEchoMode(QLineEdit.Password)
        self.set_password = set_password

        form = QFormLayout()
        form.addRow("Nom d'utilisateur", self.name)
        form.addRow("Rôle", self.role)
        if set_password:
            form.addRow("Mot de passe", self.pwd)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        lay = QVBoxLayout(self)
        lay.addLayout(form)
        lay.addWidget(self.buttons)

    def data(self):
        return self.name.text().strip(), self.role.currentText(), self.pwd.text()

class ChangePasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Changer mon mot de passe")
        self.resize(420, 180)
        self.old = QLineEdit(); self.old.setEchoMode(QLineEdit.Password)
        self.new = QLineEdit(); self.new.setEchoMode(QLineEdit.Password)
        self.conf = QLineEdit(); self.conf.setEchoMode(QLineEdit.Password)

        form = QFormLayout()
        form.addRow("Ancien mot de passe", self.old)
        form.addRow("Nouveau mot de passe", self.new)
        form.addRow("Confirmer", self.conf)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        lay = QVBoxLayout(self)
        lay.addLayout(form)
        lay.addWidget(self.buttons)

    def data(self):
        return self.old.text(), self.new.text(), self.conf.text()

# --------- BASE TAB ---------
class BaseTab(QWidget):
    """Onglet générique, avec capacités réglables par sous-classe."""
    def __init__(self, table_name: str, headers: dict, role: str, parent=None):
        super().__init__(parent)
        self.table_name = table_name
        self.headers = headers
        self.role = role  # Admin, Mappeur, Beta Testeur

        # Capacités par défaut (peuvent être modifiées en sous-classe)
        caps = self.get_capabilities_for_role(role)
        self.allow_add = caps["add"]
        self.allow_edit = caps["edit"]
        self.allow_delete = caps["delete"]
        self.allow_export = caps["export"]

        self.model = QSqlTableModel(self)
        self.model.setTable(self.table_name)
        strategy = QSqlTableModel.OnFieldChange if self.allow_edit else QSqlTableModel.OnManualSubmit
        self.model.setEditStrategy(strategy)
        self.model.select()
        for idx, field in enumerate(self.headers.keys()):
            self.model.setHeaderData(idx, Qt.Horizontal, self.headers[field])

        self.proxy = QSortFilterProxyModel(self)
        self.proxy.setSourceModel(self.model)
        self.proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)

        main = QVBoxLayout(self)
        toolbar = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Rechercher...")
        self.search.textChanged.connect(self.apply_filter)

        self.btn_add = QPushButton("Ajouter")
        self.btn_delete = QPushButton("Supprimer")
        self.btn_export_csv = QPushButton("Export CSV")
        self.btn_export_xlsx = QPushButton("Export Excel")
        self.chk_show_active = None  # optionnel selon table

        toolbar.addWidget(QLabel("🔎"))
        toolbar.addWidget(self.search)
        toolbar.addStretch(1)
        toolbar.addWidget(self.btn_add)
        toolbar.addWidget(self.btn_delete)
        toolbar.addWidget(self.btn_export_csv)
        toolbar.addWidget(self.btn_export_xlsx)

        self.table = QTableView()
        self.table.setModel(self.proxy)
        self.table.setSortingEnabled(True)
        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.setAlternatingRowColors(True)
        if not self.allow_edit:
            self.table.setEditTriggers(QTableView.NoEditTriggers)
        else:
            self.table.setEditTriggers(QTableView.DoubleClicked | QTableView.SelectedClicked)
        self.table.horizontalHeader().setStretchLastSection(True)

        main.addLayout(toolbar)
        main.addWidget(self.table)

        # Connexions
        self.btn_add.clicked.connect(self.add_row)
        self.btn_delete.clicked.connect(self.delete_rows)
        self.btn_export_csv.clicked.connect(lambda: self.export_data("csv"))
        self.btn_export_xlsx.clicked.connect(lambda: self.export_data("xlsx"))

        # Permissions UI
        self.btn_add.setEnabled(self.allow_add)
        self.btn_delete.setEnabled(self.allow_delete)
        self.btn_export_csv.setEnabled(self.allow_export)
        self.btn_export_xlsx.setEnabled(self.allow_export)

        # Audit des changements (modification/insert/suppression)
        self.model.dataChanged.connect(self._on_data_changed)
        self.model.rowsInserted.connect(self._on_rows_inserted)
        self.model.rowsRemoved.connect(self._on_rows_removed)

    # ---- Permissions par rôle (par défaut : Admin full / autres lecture) ----
    def get_capabilities_for_role(self, role: str):
        if role == "Admin":
            return {"add": True, "edit": True, "delete": True, "export": True}
        # Beta Testeur = lecture seule par défaut
        return {"add": False, "edit": False, "delete": False, "export": False}

    def apply_filter(self, text: str):
        self.proxy.setFilterRegularExpression(QRegularExpression(text))

    def add_row(self):
        if not self.allow_add:
            QMessageBox.warning(self, "Ajout", "Vous n'avez pas l'autorisation d'ajouter.")
            return
        r = self.model.rowCount()
        if self.model.insertRow(r):
            idx = self.model.index(r, 0)
            self.table.scrollToBottom()
            self.table.setCurrentIndex(self.proxy.mapFromSource(idx))
            log_action(getattr(self.window(), "username", "?"), f"Ajout dans {self.table_name} (ligne {r+1})")

    def delete_rows(self):
        if not self.allow_delete:
            QMessageBox.warning(self, "Suppression", "Vous n'avez pas l'autorisation de supprimer.")
            return
        indexes = self.table.selectionModel().selectedRows()
        if not indexes:
            QMessageBox.information(self, "Suppression", "Sélectionne au moins une ligne.")
            return
        if QMessageBox.question(self, "Confirmer", f"Supprimer {len(indexes)} ligne(s) ?") != QMessageBox.Yes:
            return
        for i in sorted(indexes, key=lambda s: s.row(), reverse=True):
            self.model.removeRow(self.proxy.mapToSource(i).row())
        self.model.select()
        log_action(getattr(self.window(), "username", "?"), f"Suppression dans {self.table_name} ({len(indexes)} lignes)")

    def export_data(self, kind="csv"):
        if not self.allow_export:
            QMessageBox.warning(self, "Export", "Vous n'avez pas l'autorisation d'exporter.")
            return
        default_name = f"{self.table_name}_{datetime.now().date()}.{kind}"
        path, _ = QFileDialog.getSaveFileName(self, "Exporter", default_name,
                                              "CSV (*.csv);;Excel (*.xlsx)")
        if not path:
            return
        import pandas as pd
        fields = ",".join(self.headers.keys())
        conn = sqlite3.connect(DB_NAME)
        df = pd.read_sql_query(f"SELECT {fields} FROM {self.table_name}", conn)
        conn.close()
        if kind == "csv" or path.lower().endswith(".csv"):
            df.to_csv(path, index=False)
        else:
            try:
                df.to_excel(path, index=False)
            except Exception as e:
                QMessageBox.warning(self, "Export Excel", f"Erreur export Excel : {e}\nExport CSV proposé à la place.")
                import os as _os
                alt = _os.path.splitext(path)[0] + ".csv"
                df.to_csv(alt, index=False)
        QMessageBox.information(self, "Export", f"Export terminé :\n{path}")
        log_action(getattr(self.window(), "username", "?"), f"Export {self.table_name} vers {path}")

    # --- Hooks d'audit ---
    def _on_data_changed(self, *args):
        if self.allow_edit:
            log_action(getattr(self.window(), "username", "?"), f"Modification dans {self.table_name}")

    def _on_rows_inserted(self, *args):
        # déjà loggé dans add_row, mais on garde au cas d'insertion externe
        if self.allow_add:
            log_action(getattr(self.window(), "username", "?"), f"Insertion dans {self.table_name}")

    def _on_rows_removed(self, *args):
        if self.allow_delete:
            log_action(getattr(self.window(), "username", "?"), f"Suppression dans {self.table_name}")

# --------- TABS ---------
class PersonnelTab(BaseTab):
    def __init__(self, role: str, parent=None):
        self._role = role
        headers = {
            "id": "ID",
            "nom": "Nom",
            "poste": "Poste",
            "email": "Email",
            "telephone": "Téléphone",
            "disponibilite": "Disponibilité",
            "actif": "Actif",
            "notes": "Notes"
        }
        super().__init__("personnel", headers, role, parent)
        # Filtre "actifs uniquement"
        self.chk_show_active = QCheckBox("Actifs uniquement")
        self.chk_show_active.setChecked(False)
        self.chk_show_active.stateChanged.connect(self.toggle_active_filter)
        self.layout().insertWidget(1, self.chk_show_active)
        # Toujours autorisé
        self.chk_show_active.setEnabled(True)

    def get_capabilities_for_role(self, role: str):
        if role == "Admin":
            return {"add": True, "edit": True, "delete": True, "export": True}
        if role == "Mappeur":
            # Lecture seule
            return {"add": False, "edit": False, "delete": False, "export": False}
        # Beta Testeur = lecture seule
        return {"add": False, "edit": False, "delete": False, "export": False}

    def toggle_active_filter(self):
        if self.chk_show_active.isChecked():
            self.model.setFilter("actif = 1")
        else:
            self.model.setFilter("")
        self.model.select()

class AccordsTab(BaseTab):
    def __init__(self, role: str, parent=None):
        headers = {
            "id": "ID",
            "partenaire": "Partenaire",
            "objet": "Objet",
            "date_debut": "Début",
            "date_fin": "Fin",
            "statut": "Statut",
            "montant_estime": "Montant estimé",
            "notes": "Notes"
        }
        super().__init__("accords", headers, role, parent)

    def get_capabilities_for_role(self, role: str):
        if role == "Admin":
            return {"add": True, "edit": True, "delete": True, "export": True}
        if role == "Mappeur":
            return {"add": False, "edit": False, "delete": False, "export": False}
        return {"add": False, "edit": False, "delete": False, "export": False}

class LignesTab(BaseTab):
    def __init__(self, role: str, parent=None):
        headers = {
            "id": "ID",
            "code": "Code",
            "nom": "Nom de la ligne",
            "chef_projet": "Chef de projet",
            "progression": "Progression (%)",
            "phase": "Phase",
            "date_cible": "Date cible",
            "priorite": "Priorité",
            "notes": "Notes"
        }
        super().__init__("lignes_bus", headers, role, parent)

        # Indicateur d'avancement moyen
        box = QHBoxLayout()
        self.progress_label = QLabel("Avancement moyen :")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        box.addWidget(self.progress_label)
        box.addWidget(self.progress_bar)
        self.layout().insertLayout(1, box)

        self.model.dataChanged.connect(self.refresh_progress)
        self.model.modelReset.connect(self.refresh_progress)
        self.model.rowsInserted.connect(self.refresh_progress)
        self.model.rowsRemoved.connect(self.refresh_progress)
        self.refresh_progress()

    def get_capabilities_for_role(self, role: str):
        if role == "Admin":
            return {"add": True, "edit": True, "delete": True, "export": True}
        if role == "Mappeur":
            # Ajout + modification OK, suppression NON, export OUI
            return {"add": True, "edit": True, "delete": False, "export": True}
        # Beta Testeur : lecture seule
        return {"add": False, "edit": False, "delete": False, "export": False}

    def refresh_progress(self, *args):
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT AVG(progression) FROM lignes_bus")
        row = cur.fetchone()
        conn.close()
        avg = int(row[0]) if row and row[0] is not None else 0
        self.progress_bar.setValue(avg)

# --------- VISIONNEUSE DU JOURNAL ---------
class AuditViewer(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Journal d'audit")
        self.resize(800, 500)

        self.model = QSqlTableModel(self)
        self.model.setTable("journal_audit")
        self.model.setEditStrategy(QSqlTableModel.OnManualSubmit)
        self.model.select()
        self.model.setHeaderData(0, Qt.Horizontal, "ID")
        self.model.setHeaderData(1, Qt.Horizontal, "Date/Heure")
        self.model.setHeaderData(2, Qt.Horizontal, "Utilisateur")
        self.model.setHeaderData(3, Qt.Horizontal, "Action")

        self.proxy = QSortFilterProxyModel(self)
        self.proxy.setSourceModel(self.model)
        self.proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Filtrer par texte, utilisateur, action...")
        self.search.textChanged.connect(self._apply_filter)

        self.table = QTableView()
        self.table.setModel(self.proxy)
        self.table.setSortingEnabled(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QTableView.NoEditTriggers)

        self.btn_export = QPushButton("Exporter le journal en CSV")
        self.btn_export.clicked.connect(self.export_csv)

        lay = QVBoxLayout(self)
        lay.addWidget(self.search)
        lay.addWidget(self.table)
        lay.addWidget(self.btn_export)

    def _apply_filter(self, text: str):
        self.proxy.setFilterRegularExpression(QRegularExpression(text))

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Exporter le journal", f"journal_{datetime.now().date()}.csv", "CSV (*.csv)")
        if not path:
            return
        import pandas as pd
        conn = sqlite3.connect(DB_NAME)
        df = pd.read_sql_query("SELECT * FROM journal_audit ORDER BY id DESC", conn)
        conn.close()
        df.to_csv(path, index=False)
        QMessageBox.information(self, "Export", f"Journal exporté :\n{path}")
        log_action(getattr(self.parent(), "username", "?"), f"Export journal d'audit vers {path}")

# --------- MAIN WINDOW ---------
class MainWindow(QMainWindow):
    def __init__(self, username: str, role: str):
        super().__init__()
        self.username = username
        self.role = role

        self.setWindowTitle(f"{APP_TITLE} — Connecté : {self.username} ({self.role})")
        self.resize(1200, 720)

        tabs = QTabWidget()
        tabs.addTab(PersonnelTab(role), "👤 Personnel")
        tabs.addTab(AccordsTab(role), "🤝 Accords")
        tabs.addTab(LignesTab(role), "🚌 Lignes de bus")
        self.setCentralWidget(tabs)

        menubar = self.menuBar()
        fichier = menubar.addMenu("&Fichier")

        action_export_all_csv = QAction("Exporter tout en CSV...", self)
        action_export_all_csv.triggered.connect(self.export_all_csv)
        fichier.addAction(action_export_all_csv)
        # Mappeur n'a pas le droit d'exporter tout
        if self.role in ("Mappeur", "Beta Testeur"):
            action_export_all_csv.setEnabled(False)

        action_backup = QAction("Créer une sauvegarde de la base...", self)
        action_backup.triggered.connect(self.backup_db)
        fichier.addAction(action_backup)
        # Pas de sauvegarde pour Mappeur / Beta Testeur
        if self.role in ("Mappeur", "Beta Testeur"):
            action_backup.setEnabled(False)

        action_open_db_dir = QAction("Ouvrir le dossier de la base...", self)
        action_open_db_dir.triggered.connect(self.open_db_dir)
        fichier.addAction(action_open_db_dir)

        fichier.addSeparator()
        action_quit = QAction("Quitter", self)
        action_quit.triggered.connect(self.close)
        fichier.addAction(action_quit)

        usermenu = menubar.addMenu("&Utilisateur")
        action_change_pwd = QAction("Changer mon mot de passe...", self)
        action_change_pwd.triggered.connect(self.change_my_password)
        usermenu.addAction(action_change_pwd)

        if self.role == "Admin":
            admin = menubar.addMenu("&Admin")
            action_manage_users = QAction("Gérer les utilisateurs...", self)
            action_manage_users.triggered.connect(self.manage_users)
            admin.addAction(action_manage_users)

            action_audit = QAction("Consulter le journal d'audit...", self)
            action_audit.triggered.connect(self.open_audit_viewer)
            admin.addAction(action_audit)

        self.setStatusBar(QStatusBar())

    # ----- Actions Fichier -----
    def export_all_csv(self):
        dest = QFileDialog.getExistingDirectory(self, "Dossier d'export")
        if not dest:
            return
        import pandas as pd
        conn = sqlite3.connect(DB_NAME)
        for table in ["personnel", "accords", "lignes_bus"]:
            df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
            out = os.path.join(dest, f"{table}.csv")
            df.to_csv(out, index=False)
        conn.close()
        QMessageBox.information(self, "Export", f"CSV exportés dans :\n{dest}")
        log_action(self.username, f"Export global CSV vers {dest}")

    def backup_db(self):
        path, _ = QFileDialog.getSaveFileName(self, "Sauvegarder la base", f"backup_{datetime.now().strftime('%Y%m%d_%H%M')}.db", "SQLite (*.db)")
        if not path:
            return
        try:
            with open(DB_NAME, "rb") as src, open(path, "wb") as dst:
                dst.write(src.read())
            QMessageBox.information(self, "Sauvegarde", f"Sauvegarde créée :\n{path}")
            log_action(self.username, f"Sauvegarde de la base vers {path}")
        except Exception as e:
            QMessageBox.warning(self, "Erreur", str(e))

    def open_db_dir(self):
        folder = os.path.abspath(".")
        QMessageBox.information(self, "Dossier", f"Dossier actuel :\n{folder}")

    # ----- Gestion utilisateurs -----
    def manage_users(self):
        while True:
            choice = QMessageBox.question(self, "Utilisateurs",
                                          "Voulez-vous (Oui) gérer les utilisateurs maintenant ?\n"
                                          "Cliquez 'Non' pour quitter la gestion.",
                                          QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if choice == QMessageBox.No:
                break

            action = QMessageBox.question(self, "Action",
                                          "Ajouter (Oui) / Modifier (No) ?\n(Appuyez sur Annuler pour Supprimer)",
                                          QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                                          QMessageBox.Yes)
            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()

            if action == QMessageBox.Yes:
                dlg = UserEditorDialog(set_password=True, parent=self)
                if dlg.exec() == QDialog.Accepted:
                    username, role, pwd = dlg.data()
                    if not username or not pwd:
                        QMessageBox.warning(self, "Ajout", "Nom d'utilisateur et mot de passe requis.")
                    else:
                        hashed = bcrypt.hashpw(pwd.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
                        try:
                            cur.execute("INSERT INTO utilisateurs (nom_utilisateur, mot_de_passe, role) VALUES (?, ?, ?)",
                                        (username, hashed, role))
                            conn.commit()
                            QMessageBox.information(self, "Ajout", f"Utilisateur '{username}' ajouté.")
                            log_action(self.username, f"Ajout utilisateur {username} ({role})")
                        except sqlite3.IntegrityError:
                            QMessageBox.warning(self, "Ajout", "Nom d'utilisateur déjà existant.")
                conn.close()

            elif action == QMessageBox.No:
                username, ok = QInputDialog_getText(self, "Modifier", "Nom d'utilisateur à modifier :")
                if not ok or not username:
                    conn.close()
                    continue
                what = QMessageBox.question(self, "Modifier",
                                            "Modifier le Rôle (Oui) / Mot de passe (Non) ?",
                                            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                if what == QMessageBox.Yes:
                    dlg = UserEditorDialog(username=username, set_password=False, parent=self)
                    if dlg.exec() == QDialog.Accepted:
                        _, role, _ = dlg.data()
                        cur.execute("UPDATE utilisateurs SET role=? WHERE nom_utilisateur=?", (role, username))
                        conn.commit()
                        QMessageBox.information(self, "Modification", f"Rôle de '{username}' mis à jour : {role}")
                        log_action(self.username, f"Changement de rôle pour {username} → {role}")
                else:
                    dlg = UserEditorDialog(username=username, role="", set_password=True, parent=self)
                    dlg.setWindowTitle("Changer mot de passe")
                    if dlg.exec() == QDialog.Accepted:
                        _, _, pwd = dlg.data()
                        if pwd:
                            hashed = bcrypt.hashpw(pwd.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
                            cur.execute("UPDATE utilisateurs SET mot_de_passe=? WHERE nom_utilisateur=?", (hashed, username))
                            conn.commit()
                            QMessageBox.information(self, "Modification", f"Mot de passe de '{username}' mis à jour.")
                            log_action(self.username, f"Réinitialisation mot de passe pour {username}")
                conn.close()

            else:
                username, ok = QInputDialog_getText(self, "Supprimer", "Nom d'utilisateur à supprimer :")
                if not ok or not username:
                    conn.close()
                    continue
                if username == self.username:
                    QMessageBox.warning(self, "Suppression", "Impossible de supprimer l'utilisateur actuellement connecté.")
                    conn.close()
                    continue
                if QMessageBox.question(self, "Confirmer", f"Supprimer l'utilisateur '{username}' ?") == QMessageBox.Yes:
                    cur.execute("DELETE FROM utilisateurs WHERE nom_utilisateur=?", (username,))
                    conn.commit()
                    QMessageBox.information(self, "Suppression", f"Utilisateur '{username}' supprimé.")
                    log_action(self.username, f"Suppression utilisateur {username}")
                conn.close()

    def change_my_password(self):
        dlg = ChangePasswordDialog(self)
        if dlg.exec() != QDialog.Accepted:
            return
        old, new, conf = dlg.data()
        if not new or new != conf:
            QMessageBox.warning(self, "Mot de passe", "Les nouveaux mots de passe ne correspondent pas.")
            return
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT mot_de_passe FROM utilisateurs WHERE nom_utilisateur=?", (self.username,))
        row = cur.fetchone()
        if not row:
            conn.close()
            QMessageBox.warning(self, "Erreur", "Utilisateur introuvable.")
            return
        if not bcrypt.checkpw(old.encode("utf-8"), row[0].encode("utf-8")):
            conn.close()
            QMessageBox.warning(self, "Mot de passe", "Ancien mot de passe incorrect.")
            return
        hashed = bcrypt.hashpw(new.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        cur.execute("UPDATE utilisateurs SET mot_de_passe=? WHERE nom_utilisateur=?", (hashed, self.username))
        conn.commit()
        conn.close()
        QMessageBox.information(self, "Mot de passe", "Mot de passe mis à jour.")
        log_action(self.username, "Changement de mon mot de passe")

    def open_audit_viewer(self):
        dlg = AuditViewer(self)
        dlg.exec()

# Petit utilitaire pour QInputDialog.getText avec import paresseux
def QInputDialog_getText(parent, title, label):
    from PySide6.QtWidgets import QInputDialog
    text, ok = QInputDialog.getText(parent, title, label)
    return text, ok

# --------- MAIN ---------
def main():
    first_time = ensure_db(DB_NAME)
    app = QApplication(sys.argv)
    connect_qt_sql(DB_NAME)

    # Écran de connexion
    username = None
    role = None
    for _ in range(5):
        dlg = LoginDialog()
        if dlg.exec() != QDialog.Accepted:
            sys.exit(0)
        u, p = dlg.get_credentials()
        if not u or not p:
            QMessageBox.warning(None, "Connexion", "Entrez un utilisateur et un mot de passe.")
            continue
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT mot_de_passe, role FROM utilisateurs WHERE nom_utilisateur=?", (u,))
        row = cur.fetchone()
        conn.close()
        if row and bcrypt.checkpw(p.encode("utf-8"), row[0].encode("utf-8")):
            username, role = u, row[1]
            log_action(username, "Connexion réussie")
            break
        else:
            QMessageBox.warning(None, "Connexion", "Identifiants invalides.")

    if username is None:
        sys.exit(0)

    win = MainWindow(username, role)
    win.show()

    if first_time:
        QMessageBox.information(win, "Bienvenue",
                                "Base créée et utilisateur admin par défaut ajouté :\n"
                                "Utilisateur : admin\nMot de passe : admin123\n"
                                "Pense à le modifier depuis le menu Utilisateur.")

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
