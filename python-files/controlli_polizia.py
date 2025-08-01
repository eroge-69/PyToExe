import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import datetime
import os

# --- DATABASE INIT ---
conn = sqlite3.connect("controlli_polizia.db")
c = conn.cursor()

# Tabelle
c.execute("""CREATE TABLE IF NOT EXISTS anagrafica (
    id INTEGER PRIMARY KEY,
    nome TEXT,
    cognome TEXT,
    data_nascita TEXT,
    luogo_nascita TEXT,
    codice_fiscale TEXT UNIQUE,
    segnalato INTEGER DEFAULT 0,
    note TEXT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS documenti (
    id INTEGER PRIMARY KEY,
    codice_fiscale TEXT,
    tipo_documento TEXT,
    numero TEXT,
    rilasciato_da TEXT,
    scadenza TEXT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS veicoli (
    id INTEGER PRIMARY KEY,
    codice_fiscale TEXT,
    targa TEXT,
    marca TEXT,
    modello TEXT,
    assicurazione TEXT,
    revisione TEXT
)""")

conn.commit()

# (Inserire il resto del codice qui come nel canvas)
