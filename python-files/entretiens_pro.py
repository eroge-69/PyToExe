# entretiens_pro.py
import sqlite3, pathlib
from PySide6 import QtWidgets
from entretiens_gui import MainWindow

DB_PATH = pathlib.Path(__file__).parent / "entretiens_pro.db"

# Connexion à la base, création si nécessaire
con = sqlite3.connect(DB_PATH)
cur = con.cursor()

# Création des tables si elles n'existent pas
cur.execute("""CREATE TABLE IF NOT EXISTS classes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT UNIQUE NOT NULL
)""")
cur.execute("""CREATE TABLE IF NOT EXISTS eleves (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    classe_id INTEGER,
    UNIQUE(nom, classe_id),
    FOREIGN KEY(classe_id) REFERENCES classes(id)
)""")
cur.execute("""CREATE TABLE IF NOT EXISTS entretiens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    eleve_id INTEGER,
    date TEXT,
    contenu TEXT,
    created_at TEXT,
    FOREIGN KEY(eleve_id) REFERENCES eleves(id)
)""")
cur.execute("""CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
)""")
con.commit()

# Lancement de l'application
app = QtWidgets.QApplication([])
window = MainWindow(con)
window.show()
app.exec()
