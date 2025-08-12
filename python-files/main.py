#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Heizlastberechnung Desktop-Anwendung
Professionelle Software für Heizlastberechnungen nach DIN EN 12831

Autor: Ulli Bauer - HLS-Ingenieur
Version: 1.0.0
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import os
import json
from datetime import datetime
import math
from typing import Dict, List, Optional, Tuple
import webbrowser
from pathlib import Path

# Konstanten für die Berechnung
CLIMATE_DATA = {
    # PLZ-Bereiche und zugehörige Außentemperaturen (°C)
    "0": -14,  # Dresden, Chemnitz
    "1": -12,  # Berlin, Brandenburg
    "2": -12,  # Hamburg, Schleswig-Holstein
    "3": -12,  # Hannover, Niedersachsen
    "4": -12,  # Düsseldorf, NRW
    "5": -12,  # Köln, NRW
    "6": -12,  # Frankfurt, Hessen
    "7": -12,  # Stuttgart, Baden-Württemberg
    "8": -16,  # München, Bayern (Alpenvorland)
    "9": -16,  # Nürnberg, Bayern
}

# Standard U-Werte nach Baujahr
U_VALUES_BY_YEAR = {
    "vor_1978": {
        "außenwand": 1.4,
        "fenster": 2.8,
        "dach": 1.0,
        "kellerdecke": 1.2,
        "tür": 3.0
    },
    "1978_1995": {
        "außenwand": 0.8,
        "fenster": 2.5,
        "dach": 0.6,
        "kellerdecke": 0.8,
        "tür": 2.5
    },
    "1995_2009": {
        "außenwand": 0.5,
        "fenster": 1.8,
        "dach": 0.4,
        "kellerdecke": 0.6,
        "tür": 2.0
    },
    "ab_2009": {
        "außenwand": 0.3,
        "fenster": 1.3,
        "dach": 0.2,
        "kellerdecke": 0.4,
        "tür": 1.8
    },
    "passivhaus": {
        "außenwand": 0.15,
        "fenster": 0.8,
        "dach": 0.1,
        "kellerdecke": 0.2,
        "tür": 0.8
    }
}

# Standard-Raumtemperaturen
ROOM_TEMPERATURES = {
    "Wohnzimmer": 20,
    "Schlafzimmer": 18,
    "Kinderzimmer": 20,
    "Küche": 20,
    "Bad": 24,
    "WC": 18,
    "Flur": 18,
    "Diele": 18,
    "Arbeitszimmer": 20,
    "Keller": 15,
    "Dachboden": 15,
    "Garage": 5
}

class DatabaseManager:
    """Verwaltet die SQLite-Datenbank für die Anwendung."""
    
    def __init__(self, db_path: str = "heizlast.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialisiert die Datenbank mit allen notwendigen Tabellen."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Projekte-Tabelle
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                address TEXT,
                postal_code TEXT,
                city TEXT,
                building_type TEXT,
                building_year INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Räume-Tabelle
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                name TEXT NOT NULL,
                room_type TEXT,
                area REAL,
                volume REAL,
                height REAL,
                design_temperature REAL,
                air_change_rate REAL DEFAULT 0.5,
                FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
            )
        ''')
        
        # Bauteile-Tabelle
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS building_elements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_id INTEGER,
                element_type TEXT,
                area REAL,
                u_value REAL,
                orientation TEXT,
                description TEXT,
                FOREIGN KEY (room_id) REFERENCES rooms (id) ON DELETE CASCADE
            )
        ''')
        
        # Berechnungsergebnisse-Tabelle
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS calculation_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                room_id INTEGER,
                transmission_loss REAL,
                ventilation_loss REAL,
                total_heat_load REAL,
                specific_heat_load REAL,
                calculation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE,
                FOREIGN KEY (room_id) REFERENCES rooms (id) ON DELETE CASCADE
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def execute_query(self, query: str, params: tuple = ()) -> List[tuple]:
        """Führt eine SQL-Abfrage aus und gibt die Ergebnisse zurück."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.commit()
        conn.close()
        return results
    
    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """Führt eine INSERT-Abfrage aus und gibt die ID des neuen Datensatzes zurück."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(query, params)
        last_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return last_id

class HeatingLoadCalculator:
    """Berechnet die Heizlast nach DIN EN 12831."""
    
    @staticmethod
    def get_outside_temperature(postal_code: str) -> float:
        """Ermittelt die Außentemperatur basierend auf der PLZ."""
        if not postal_code:
            return -12  # Standard-Wert
        
        first_digit = postal_code[0] if postal_code else "1"
        return CLIMATE_DATA.get(first_digit, -12)
    
    @staticmethod
    def calculate_transmission_loss(area: float, u_value: float, temp_diff: float) -> float:
        """Berechnet den Transmissionswärmeverlust."""
        return area * u_value * temp_diff
    
    @staticmethod
    def calculate_ventilation_loss(volume: float, air_change_rate: float, temp_diff: float) -> float:
        """Berechnet den Lüftungswärmeverlust."""
        # Luftdichte: 1.2 kg/m³, spezifische Wärmekapazität: 1005 J/(kg·K)
        return volume * air_change_rate * 1.2 * 1005 * temp_diff / 3600
    
    @classmethod
    def calculate_room_heat_load(cls, room_data: dict, building_elements: List[dict], 
                               outside_temp: float) -> dict:
        """Berechnet die Heizlast für einen Raum."""
        design_temp = room_data.get('design_temperature', 20)
        temp_diff = design_temp - outside_temp
        
        # Transmissionswärmeverluste
        transmission_loss = 0
        for element in building_elements:
            transmission_loss += cls.calculate_transmission_loss(
                element['area'], element['u_value'], temp_diff
            )
        
        # Lüftungswärmeverluste
        volume = room_data.get('volume', 0)
        air_change_rate = room_data.get('air_change_rate', 0.5)
        ventilation_loss = cls.calculate_ventilation_loss(volume, air_change_rate, temp_diff)
        
        # Gesamtheizlast
        total_heat_load = transmission_loss + ventilation_loss
        
        # Spezifische Heizlast
        area = room_data.get('area', 1)
        specific_heat_load = total_heat_load / area if area > 0 else 0
        
        return {
            'transmission_loss': round(transmission_loss, 2),
            'ventilation_loss': round(ventilation_loss, 2),
            'total_heat_load': round(total_heat_load, 2),
            'specific_heat_load': round(specific_heat_load, 2)
        }

class ProjectDialog:
    """Dialog für die Erstellung und Bearbeitung von Projekten."""
    
    def __init__(self, parent, db_manager: DatabaseManager, project_data: dict = None):
        self.parent = parent
        self.db_manager = db_manager
        self.project_data = project_data
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Projekt bearbeiten" if project_data else "Neues Projekt")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        
        # Daten laden, falls vorhanden
        if project_data:
            self.load_project_data()
    
    def create_widgets(self):
        """Erstellt die Widgets für den Dialog."""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Projektname
        ttk.Label(main_frame, text="Projektname:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.name_var, width=40).grid(row=0, column=1, pady=5)
        
        # Beschreibung
        ttk.Label(main_frame, text="Beschreibung:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.description_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.description_var, width=40).grid(row=1, column=1, pady=5)
        
        # Adresse
        ttk.Label(main_frame, text="Adresse:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.address_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.address_var, width=40).grid(row=2, column=1, pady=5)
        
        # PLZ
        ttk.Label(main_frame, text="PLZ:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.postal_code_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.postal_code_var, width=40).grid(row=3, column=1, pady=5)
        
        # Stadt
        ttk.Label(main_frame, text="Stadt:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.city_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.city_var, width=40).grid(row=4, column=1, pady=5)
        
        # Gebäudetyp
        ttk.Label(main_frame, text="Gebäudetyp:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.building_type_var = tk.StringVar()
        building_type_combo = ttk.Combobox(main_frame, textvariable=self.building_type_var, width=37)
        building_type_combo['values'] = ('Einfamilienhaus', 'Mehrfamilienhaus', 'Bürogebäude', 'Gewerbe')
        building_type_combo.grid(row=5, column=1, pady=5)
        
        # Baujahr
        ttk.Label(main_frame, text="Baujahr:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.building_year_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.building_year_var, width=40).grid(row=6, column=1, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Speichern", command=self.save_project).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Abbrechen", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def load_project_data(self):
        """Lädt die Projektdaten in die Eingabefelder."""
        self.name_var.set(self.project_data.get('name', ''))
        self.description_var.set(self.project_data.get('description', ''))
        self.address_var.set(self.project_data.get('address', ''))
        self.postal_code_var.set(self.project_data.get('postal_code', ''))
        self.city_var.set(self.project_data.get('city', ''))
        self.building_type_var.set(self.project_data.get('building_type', ''))
        self.building_year_var.set(str(self.project_data.get('building_year', '')))
    
    def save_project(self):
        """Speichert das Projekt in der Datenbank."""
        if not self.name_var.get().strip():
            messagebox.showerror("Fehler", "Bitte geben Sie einen Projektnamen ein.")
            return
        
        try:
            building_year = int(self.building_year_var.get()) if self.building_year_var.get() else None
        except ValueError:
            messagebox.showerror("Fehler", "Bitte geben Sie ein gültiges Baujahr ein.")
            return
        
        project_data = {
            'name': self.name_var.get().strip(),
            'description': self.description_var.get().strip(),
            'address': self.address_var.get().strip(),
            'postal_code': self.postal_code_var.get().strip(),
            'city': self.city_var.get().strip(),
            'building_type': self.building_type_var.get(),
            'building_year': building_year
        }
        
        if self.project_data:  # Bearbeiten
            query = '''UPDATE projects SET name=?, description=?, address=?, postal_code=?, 
                      city=?, building_type=?, building_year=?, updated_at=CURRENT_TIMESTAMP 
                      WHERE id=?'''
            params = (project_data['name'], project_data['description'], project_data['address'],
                     project_data['postal_code'], project_data['city'], project_data['building_type'],
                     project_data['building_year'], self.project_data['id'])
            self.db_manager.execute_query(query, params)
            self.result = self.project_data['id']
        else:  # Neu erstellen
            query = '''INSERT INTO projects (name, description, address, postal_code, city, 
                      building_type, building_year) VALUES (?, ?, ?, ?, ?, ?, ?)'''
            params = (project_data['name'], project_data['description'], project_data['address'],
                     project_data['postal_code'], project_data['city'], project_data['building_type'],
                     project_data['building_year'])
            self.result = self.db_manager.execute_insert(query, params)
        
        self.dialog.destroy()

class RoomDialog:
    """Dialog für die Erstellung und Bearbeitung von Räumen."""
    
    def __init__(self, parent, db_manager: DatabaseManager, project_id: int, room_data: dict = None):
        self.parent = parent
        self.db_manager = db_manager
        self.project_id = project_id
        self.room_data = room_data
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Raum bearbeiten" if room_data else "Neuer Raum")
        self.dialog.geometry("400x350")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        
        if room_data:
            self.load_room_data()
    
    def create_widgets(self):
        """Erstellt die Widgets für den Dialog."""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Raumname
        ttk.Label(main_frame, text="Raumname:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.name_var, width=30).grid(row=0, column=1, pady=5)
        
        # Raumtyp
        ttk.Label(main_frame, text="Raumtyp:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.room_type_var = tk.StringVar()
        room_type_combo = ttk.Combobox(main_frame, textvariable=self.room_type_var, width=27)
        room_type_combo['values'] = list(ROOM_TEMPERATURES.keys())
        room_type_combo.bind('<<ComboboxSelected>>', self.on_room_type_change)
        room_type_combo.grid(row=1, column=1, pady=5)
        
        # Fläche
        ttk.Label(main_frame, text="Fläche (m²):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.area_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.area_var, width=30).grid(row=2, column=1, pady=5)
        
        # Höhe
        ttk.Label(main_frame, text="Höhe (m):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.height_var = tk.StringVar()
        height_entry = ttk.Entry(main_frame, textvariable=self.height_var, width=30)
        height_entry.grid(row=3, column=1, pady=5)
        height_entry.bind('<KeyRelease>', self.calculate_volume)
        
        # Volumen (automatisch berechnet)
        ttk.Label(main_frame, text="Volumen (m³):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.volume_var = tk.StringVar()
        volume_entry = ttk.Entry(main_frame, textvariable=self.volume_var, width=30, state='readonly')
        volume_entry.grid(row=4, column=1, pady=5)
        
        # Solltemperatur
        ttk.Label(main_frame, text="Solltemperatur (°C):").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.design_temperature_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.design_temperature_var, width=30).grid(row=5, column=1, pady=5)
        
        # Luftwechselrate
        ttk.Label(main_frame, text="Luftwechselrate (1/h):").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.air_change_rate_var = tk.StringVar(value="0.5")
        ttk.Entry(main_frame, textvariable=self.air_change_rate_var, width=30).grid(row=6, column=1, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Speichern", command=self.save_room).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Abbrechen", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def on_room_type_change(self, event=None):
        """Wird aufgerufen, wenn der Raumtyp geändert wird."""
        room_type = self.room_type_var.get()
        if room_type in ROOM_TEMPERATURES:
            self.design_temperature_var.set(str(ROOM_TEMPERATURES[room_type]))
    
    def calculate_volume(self, event=None):
        """Berechnet das Volumen basierend auf Fläche und Höhe."""
        try:
            area = float(self.area_var.get() or 0)
            height = float(self.height_var.get() or 0)
            volume = area * height
            self.volume_var.set(f"{volume:.2f}")
        except ValueError:
            self.volume_var.set("")
    
    def load_room_data(self):
        """Lädt die Raumdaten in die Eingabefelder."""
        self.name_var.set(self.room_data.get('name', ''))
        self.room_type_var.set(self.room_data.get('room_type', ''))
        self.area_var.set(str(self.room_data.get('area', '')))
        self.height_var.set(str(self.room_data.get('height', '')))
        self.volume_var.set(str(self.room_data.get('volume', '')))
        self.design_temperature_var.set(str(self.room_data.get('design_temperature', '')))
        self.air_change_rate_var.set(str(self.room_data.get('air_change_rate', '')))
    
    def save_room(self):
        """Speichert den Raum in der Datenbank."""
        if not self.name_var.get().strip():
            messagebox.showerror("Fehler", "Bitte geben Sie einen Raumnamen ein.")
            return
        
        try:
            area = float(self.area_var.get()) if self.area_var.get() else 0
            height = float(self.height_var.get()) if self.height_var.get() else 0
            volume = float(self.volume_var.get()) if self.volume_var.get() else 0
            design_temperature = float(self.design_temperature_var.get()) if self.design_temperature_var.get() else 20
            air_change_rate = float(self.air_change_rate_var.get()) if self.air_change_rate_var.get() else 0.5
        except ValueError:
            messagebox.showerror("Fehler", "Bitte geben Sie gültige Zahlenwerte ein.")
            return
        
        room_data = {
            'name': self.name_var.get().strip(),
            'room_type': self.room_type_var.get(),
            'area': area,
            'height': height,
            'volume': volume,
            'design_temperature': design_temperature,
            'air_change_rate': air_change_rate
        }
        
        if self.room_data:  # Bearbeiten
            query = '''UPDATE rooms SET name=?, room_type=?, area=?, height=?, volume=?, 
                      design_temperature=?, air_change_rate=? WHERE id=?'''
            params = (room_data['name'], room_data['room_type'], room_data['area'],
                     room_data['height'], room_data['volume'], room_data['design_temperature'],
                     room_data['air_change_rate'], self.room_data['id'])
            self.db_manager.execute_query(query, params)
            self.result = self.room_data['id']
        else:  # Neu erstellen
            query = '''INSERT INTO rooms (project_id, name, room_type, area, height, volume, 
                      design_temperature, air_change_rate) VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
            params = (self.project_id, room_data['name'], room_data['room_type'], room_data['area'],
                     room_data['height'], room_data['volume'], room_data['design_temperature'],
                     room_data['air_change_rate'])
            self.result = self.db_manager.execute_insert(query, params)
        
        self.dialog.destroy()

class HeatingLoadApp:
    """Hauptanwendung für die Heizlastberechnung."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Heizlastberechnung - HLS-Ingenieur Ulli Bauer")
        self.root.geometry("1200x800")
        
        # Datenbank initialisieren
        self.db_manager = DatabaseManager()
        
        # Aktuelles Projekt
        self.current_project_id = None
        self.current_project_data = None
        
        # GUI erstellen
        self.create_menu()
        self.create_widgets()
        self.load_projects()
        
        # Stil konfigurieren
        self.configure_style()
    
    def configure_style(self):
        """Konfiguriert das Aussehen der Anwendung."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Farben entsprechend der Webseite
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), foreground='#2196F3')
        style.configure('Heading.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Success.TLabel', foreground='#4CAF50')
        style.configure('Error.TLabel', foreground='#F44336')
    
    def create_menu(self):
        """Erstellt die Menüleiste."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Datei-Menü
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Datei", menu=file_menu)
        file_menu.add_command(label="Neues Projekt", command=self.new_project)
        file_menu.add_separator()
        file_menu.add_command(label="Exportieren", command=self.export_project)
        file_menu.add_command(label="Importieren", command=self.import_project)
        file_menu.add_separator()
        file_menu.add_command(label="Beenden", command=self.root.quit)
        
        # Bearbeiten-Menü
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Bearbeiten", menu=edit_menu)
        edit_menu.add_command(label="Projekt bearbeiten", command=self.edit_project)
        edit_menu.add_command(label="Projekt löschen", command=self.delete_project)
        
        # Berechnung-Menü
        calc_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Berechnung", menu=calc_menu)
        calc_menu.add_command(label="Heizlast berechnen", command=self.calculate_heat_load)
        calc_menu.add_command(label="Ergebnisse exportieren", command=self.export_results)
        
        # Hilfe-Menü
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Hilfe", menu=help_menu)
        help_menu.add_command(label="Über", command=self.show_about)
        help_menu.add_command(label="Hilfe", command=self.show_help)
    
    def create_widgets(self):
        """Erstellt die Hauptwidgets der Anwendung."""
        # Hauptframe
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Linke Seite: Projektliste
        left_frame = ttk.LabelFrame(main_frame, text="Projekte", padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Projektliste
        self.project_listbox = tk.Listbox(left_frame, width=30, height=20)
        self.project_listbox.pack(fill=tk.BOTH, expand=True)
        self.project_listbox.bind('<<ListboxSelect>>', self.on_project_select)
        
        # Buttons für Projekte
        project_buttons = ttk.Frame(left_frame)
        project_buttons.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(project_buttons, text="Neu", command=self.new_project).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(project_buttons, text="Bearbeiten", command=self.edit_project).pack(side=tk.LEFT, padx=5)
        ttk.Button(project_buttons, text="Löschen", command=self.delete_project).pack(side=tk.LEFT, padx=5)
        
        # Rechte Seite: Projektdetails
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Notebook für Tabs
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Projektübersicht
        self.overview_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.overview_frame, text="Übersicht")
        self.create_overview_tab()
        
        # Tab 2: Räume
        self.rooms_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.rooms_frame, text="Räume")
        self.create_rooms_tab()
        
        # Tab 3: Berechnung
        self.calculation_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.calculation_frame, text="Berechnung")
        self.create_calculation_tab()
    
    def create_overview_tab(self):
        """Erstellt den Übersichts-Tab."""
        # Projektinformationen
        info_frame = ttk.LabelFrame(self.overview_frame, text="Projektinformationen", padding="10")
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.project_info_text = tk.Text(info_frame, height=10, state=tk.DISABLED)
        self.project_info_text.pack(fill=tk.BOTH, expand=True)
        
        # Statistiken
        stats_frame = ttk.LabelFrame(self.overview_frame, text="Statistiken", padding="10")
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.stats_text = tk.Text(stats_frame, height=8, state=tk.DISABLED)
        self.stats_text.pack(fill=tk.BOTH, expand=True)
    
    def create_rooms_tab(self):
        """Erstellt den Räume-Tab."""
        # Toolbar
        toolbar = ttk.Frame(self.rooms_frame)
        toolbar.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(toolbar, text="Neuer Raum", command=self.new_room).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="Bearbeiten", command=self.edit_room).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Löschen", command=self.delete_room).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Bauteile", command=self.manage_building_elements).pack(side=tk.LEFT, padx=5)
        
        # Raumliste
        columns = ('Name', 'Typ', 'Fläche', 'Volumen', 'Temperatur')
        self.rooms_tree = ttk.Treeview(self.rooms_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.rooms_tree.heading(col, text=col)
            self.rooms_tree.column(col, width=120)
        
        self.rooms_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
    
    def create_calculation_tab(self):
        """Erstellt den Berechnungs-Tab."""
        # Berechnungsparameter
        params_frame = ttk.LabelFrame(self.calculation_frame, text="Berechnungsparameter", padding="10")
        params_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(params_frame, text="Außentemperatur:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.outside_temp_var = tk.StringVar()
        ttk.Entry(params_frame, textvariable=self.outside_temp_var, width=20).grid(row=0, column=1, pady=5)
        ttk.Label(params_frame, text="°C").grid(row=0, column=2, sticky=tk.W, pady=5)
        
        # Berechnung starten
        calc_button_frame = ttk.Frame(self.calculation_frame)
        calc_button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(calc_button_frame, text="Heizlast berechnen", 
                  command=self.calculate_heat_load).pack(side=tk.LEFT)
        ttk.Button(calc_button_frame, text="Ergebnisse exportieren", 
                  command=self.export_results).pack(side=tk.LEFT, padx=(10, 0))
        
        # Ergebnisse
        results_frame = ttk.LabelFrame(self.calculation_frame, text="Berechnungsergebnisse", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Ergebnistabelle
        result_columns = ('Raum', 'Transmission', 'Lüftung', 'Gesamt', 'Spezifisch')
        self.results_tree = ttk.Treeview(results_frame, columns=result_columns, show='headings')
        
        for col in result_columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=120)
        
        self.results_tree.pack(fill=tk.BOTH, expand=True)
    
    def load_projects(self):
        """Lädt alle Projekte in die Projektliste."""
        self.project_listbox.delete(0, tk.END)
        
        projects = self.db_manager.execute_query("SELECT id, name FROM projects ORDER BY name")
        for project_id, name in projects:
            self.project_listbox.insert(tk.END, name)
            # Speichere die ID als Attribut
            self.project_listbox.insert(tk.END, f"ID:{project_id}")
            self.project_listbox.delete(tk.END)  # Lösche die ID-Zeile wieder
    
    def on_project_select(self, event):
        """Wird aufgerufen, wenn ein Projekt ausgewählt wird."""
        selection = self.project_listbox.curselection()
        if not selection:
            return
        
        project_name = self.project_listbox.get(selection[0])
        
        # Projekt-ID ermitteln
        projects = self.db_manager.execute_query("SELECT * FROM projects WHERE name = ?", (project_name,))
        if projects:
            project_data = projects[0]
            self.current_project_id = project_data[0]
            self.current_project_data = {
                'id': project_data[0],
                'name': project_data[1],
                'description': project_data[2],
                'address': project_data[3],
                'postal_code': project_data[4],
                'city': project_data[5],
                'building_type': project_data[6],
                'building_year': project_data[7]
            }
            
            self.update_project_display()
            self.load_rooms()
            self.update_outside_temperature()
    
    def update_project_display(self):
        """Aktualisiert die Anzeige der Projektinformationen."""
        if not self.current_project_data:
            return
        
        # Projektinformationen
        self.project_info_text.config(state=tk.NORMAL)
        self.project_info_text.delete(1.0, tk.END)
        
        info_text = f"""Projektname: {self.current_project_data['name']}
Beschreibung: {self.current_project_data['description'] or 'Keine Beschreibung'}
Adresse: {self.current_project_data['address'] or 'Keine Adresse'}
PLZ/Stadt: {self.current_project_data['postal_code']} {self.current_project_data['city']}
Gebäudetyp: {self.current_project_data['building_type'] or 'Nicht angegeben'}
Baujahr: {self.current_project_data['building_year'] or 'Nicht angegeben'}"""
        
        self.project_info_text.insert(1.0, info_text)
        self.project_info_text.config(state=tk.DISABLED)
        
        # Statistiken
        self.update_statistics()
    
    def update_statistics(self):
        """Aktualisiert die Projektstatistiken."""
        if not self.current_project_id:
            return
        
        # Anzahl Räume
        rooms = self.db_manager.execute_query(
            "SELECT COUNT(*) FROM rooms WHERE project_id = ?", 
            (self.current_project_id,)
        )
        room_count = rooms[0][0] if rooms else 0
        
        # Gesamtfläche
        total_area = self.db_manager.execute_query(
            "SELECT SUM(area) FROM rooms WHERE project_id = ?", 
            (self.current_project_id,)
        )
        total_area = total_area[0][0] if total_area and total_area[0][0] else 0
        
        # Letzte Berechnung
        last_calc = self.db_manager.execute_query(
            "SELECT MAX(calculation_date) FROM calculation_results WHERE project_id = ?", 
            (self.current_project_id,)
        )
        last_calc_date = last_calc[0][0] if last_calc and last_calc[0][0] else "Noch keine Berechnung"
        
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        
        stats_text = f"""Anzahl Räume: {room_count}
Gesamtfläche: {total_area:.2f} m²
Letzte Berechnung: {last_calc_date}"""
        
        self.stats_text.insert(1.0, stats_text)
        self.stats_text.config(state=tk.DISABLED)
    
    def load_rooms(self):
        """Lädt die Räume des aktuellen Projekts."""
        # Raumliste leeren
        for item in self.rooms_tree.get_children():
            self.rooms_tree.delete(item)
        
        if not self.current_project_id:
            return
        
        rooms = self.db_manager.execute_query(
            "SELECT * FROM rooms WHERE project_id = ? ORDER BY name", 
            (self.current_project_id,)
        )
        
        for room in rooms:
            self.rooms_tree.insert('', tk.END, values=(
                room[2],  # name
                room[3],  # room_type
                f"{room[4]:.2f} m²" if room[4] else "",  # area
                f"{room[6]:.2f} m³" if room[6] else "",  # volume
                f"{room[7]:.1f} °C" if room[7] else ""   # design_temperature
            ))
    
    def update_outside_temperature(self):
        """Aktualisiert die Außentemperatur basierend auf der PLZ."""
        if not self.current_project_data:
            return
        
        postal_code = self.current_project_data.get('postal_code', '')
        outside_temp = HeatingLoadCalculator.get_outside_temperature(postal_code)
        self.outside_temp_var.set(str(outside_temp))
    
    def new_project(self):
        """Erstellt ein neues Projekt."""
        dialog = ProjectDialog(self.root, self.db_manager)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            self.load_projects()
            messagebox.showinfo("Erfolg", "Projekt wurde erfolgreich erstellt.")
    
    def edit_project(self):
        """Bearbeitet das ausgewählte Projekt."""
        if not self.current_project_data:
            messagebox.showwarning("Warnung", "Bitte wählen Sie ein Projekt aus.")
            return
        
        dialog = ProjectDialog(self.root, self.db_manager, self.current_project_data)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            self.load_projects()
            self.update_project_display()
            messagebox.showinfo("Erfolg", "Projekt wurde erfolgreich aktualisiert.")
    
    def delete_project(self):
        """Löscht das ausgewählte Projekt."""
        if not self.current_project_data:
            messagebox.showwarning("Warnung", "Bitte wählen Sie ein Projekt aus.")
            return
        
        if messagebox.askyesno("Bestätigung", 
                              f"Möchten Sie das Projekt '{self.current_project_data['name']}' wirklich löschen?\n"
                              "Alle zugehörigen Räume und Berechnungen werden ebenfalls gelöscht."):
            
            self.db_manager.execute_query("DELETE FROM projects WHERE id = ?", (self.current_project_id,))
            self.current_project_id = None
            self.current_project_data = None
            self.load_projects()
            self.update_project_display()
            self.load_rooms()
            messagebox.showinfo("Erfolg", "Projekt wurde erfolgreich gelöscht.")
    
    def new_room(self):
        """Erstellt einen neuen Raum."""
        if not self.current_project_id:
            messagebox.showwarning("Warnung", "Bitte wählen Sie ein Projekt aus.")
            return
        
        dialog = RoomDialog(self.root, self.db_manager, self.current_project_id)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            self.load_rooms()
            self.update_statistics()
            messagebox.showinfo("Erfolg", "Raum wurde erfolgreich erstellt.")
    
    def edit_room(self):
        """Bearbeitet den ausgewählten Raum."""
        selection = self.rooms_tree.selection()
        if not selection:
            messagebox.showwarning("Warnung", "Bitte wählen Sie einen Raum aus.")
            return
        
        # Raumdaten ermitteln
        room_name = self.rooms_tree.item(selection[0])['values'][0]
        rooms = self.db_manager.execute_query(
            "SELECT * FROM rooms WHERE project_id = ? AND name = ?", 
            (self.current_project_id, room_name)
        )
        
        if rooms:
            room_data = {
                'id': rooms[0][0],
                'name': rooms[0][2],
                'room_type': rooms[0][3],
                'area': rooms[0][4],
                'volume': rooms[0][6],
                'height': rooms[0][5],
                'design_temperature': rooms[0][7],
                'air_change_rate': rooms[0][8]
            }
            
            dialog = RoomDialog(self.root, self.db_manager, self.current_project_id, room_data)
            self.root.wait_window(dialog.dialog)
            
            if dialog.result:
                self.load_rooms()
                self.update_statistics()
                messagebox.showinfo("Erfolg", "Raum wurde erfolgreich aktualisiert.")
    
    def delete_room(self):
        """Löscht den ausgewählten Raum."""
        selection = self.rooms_tree.selection()
        if not selection:
            messagebox.showwarning("Warnung", "Bitte wählen Sie einen Raum aus.")
            return
        
        room_name = self.rooms_tree.item(selection[0])['values'][0]
        
        if messagebox.askyesno("Bestätigung", f"Möchten Sie den Raum '{room_name}' wirklich löschen?"):
            self.db_manager.execute_query(
                "DELETE FROM rooms WHERE project_id = ? AND name = ?", 
                (self.current_project_id, room_name)
            )
            self.load_rooms()
            self.update_statistics()
            messagebox.showinfo("Erfolg", "Raum wurde erfolgreich gelöscht.")
    
    def manage_building_elements(self):
        """Öffnet den Dialog für die Verwaltung von Bauteilen."""
        selection = self.rooms_tree.selection()
        if not selection:
            messagebox.showwarning("Warnung", "Bitte wählen Sie einen Raum aus.")
            return
        
        messagebox.showinfo("Info", "Die Bauteil-Verwaltung wird in einer zukünftigen Version implementiert.")
    
    def calculate_heat_load(self):
        """Berechnet die Heizlast für alle Räume."""
        if not self.current_project_id:
            messagebox.showwarning("Warnung", "Bitte wählen Sie ein Projekt aus.")
            return
        
        try:
            outside_temp = float(self.outside_temp_var.get())
        except ValueError:
            messagebox.showerror("Fehler", "Bitte geben Sie eine gültige Außentemperatur ein.")
            return
        
        # Ergebnisse löschen
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Alte Berechnungsergebnisse löschen
        self.db_manager.execute_query(
            "DELETE FROM calculation_results WHERE project_id = ?", 
            (self.current_project_id,)
        )
        
        # Räume laden
        rooms = self.db_manager.execute_query(
            "SELECT * FROM rooms WHERE project_id = ? ORDER BY name", 
            (self.current_project_id,)
        )
        
        total_heat_load = 0
        
        for room in rooms:
            room_id = room[0]
            room_data = {
                'area': room[4] or 0,
                'volume': room[6] or 0,
                'design_temperature': room[7] or 20,
                'air_change_rate': room[8] or 0.5
            }
            
            # Bauteile laden (falls vorhanden)
            building_elements = self.db_manager.execute_query(
                "SELECT * FROM building_elements WHERE room_id = ?", 
                (room_id,)
            )
            
            # Standard-Bauteile erstellen, falls keine vorhanden
            if not building_elements:
                building_elements = self.create_default_building_elements(room_data)
            else:
                building_elements = [
                    {'area': elem[3], 'u_value': elem[4]} 
                    for elem in building_elements
                ]
            
            # Heizlast berechnen
            result = HeatingLoadCalculator.calculate_room_heat_load(
                room_data, building_elements, outside_temp
            )
            
            # Ergebnis speichern
            self.db_manager.execute_insert(
                '''INSERT INTO calculation_results 
                   (project_id, room_id, transmission_loss, ventilation_loss, 
                    total_heat_load, specific_heat_load) 
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (self.current_project_id, room_id, result['transmission_loss'],
                 result['ventilation_loss'], result['total_heat_load'],
                 result['specific_heat_load'])
            )
            
            # Ergebnis anzeigen
            self.results_tree.insert('', tk.END, values=(
                room[2],  # name
                f"{result['transmission_loss']:.0f} W",
                f"{result['ventilation_loss']:.0f} W",
                f"{result['total_heat_load']:.0f} W",
                f"{result['specific_heat_load']:.0f} W/m²"
            ))
            
            total_heat_load += result['total_heat_load']
        
        # Gesamtergebnis anzeigen
        self.results_tree.insert('', tk.END, values=(
            "GESAMT",
            "",
            "",
            f"{total_heat_load:.0f} W",
            ""
        ))
        
        messagebox.showinfo("Erfolg", f"Heizlastberechnung abgeschlossen.\nGesamtheizlast: {total_heat_load:.0f} W")
    
    def create_default_building_elements(self, room_data: dict) -> List[dict]:
        """Erstellt Standard-Bauteile basierend auf der Raumgröße."""
        area = room_data.get('area', 20)
        
        # Vereinfachte Annahmen für Standard-Bauteile
        building_year = self.current_project_data.get('building_year', 1990)
        
        # U-Werte basierend auf Baujahr
        if building_year < 1978:
            u_values = U_VALUES_BY_YEAR["vor_1978"]
        elif building_year < 1995:
            u_values = U_VALUES_BY_YEAR["1978_1995"]
        elif building_year < 2009:
            u_values = U_VALUES_BY_YEAR["1995_2009"]
        else:
            u_values = U_VALUES_BY_YEAR["ab_2009"]
        
        # Standard-Bauteile (vereinfacht)
        return [
            {'area': area * 0.8, 'u_value': u_values['außenwand']},  # Außenwand
            {'area': area * 0.2, 'u_value': u_values['fenster']},    # Fenster
        ]
    
    def export_results(self):
        """Exportiert die Berechnungsergebnisse."""
        if not self.current_project_id:
            messagebox.showwarning("Warnung", "Bitte wählen Sie ein Projekt aus.")
            return
        
        messagebox.showinfo("Info", "Export-Funktion wird in einer zukünftigen Version implementiert.")
    
    def export_project(self):
        """Exportiert das aktuelle Projekt."""
        if not self.current_project_id:
            messagebox.showwarning("Warnung", "Bitte wählen Sie ein Projekt aus.")
            return
        
        messagebox.showinfo("Info", "Export-Funktion wird in einer zukünftigen Version implementiert.")
    
    def import_project(self):
        """Importiert ein Projekt."""
        messagebox.showinfo("Info", "Import-Funktion wird in einer zukünftigen Version implementiert.")
    
    def show_about(self):
        """Zeigt Informationen über die Anwendung."""
        about_text = """Heizlastberechnung v1.0.0

Professionelle Software für Heizlastberechnungen nach DIN EN 12831

Entwickelt für:
HLS-Ingenieur Ulli Bauer

Kontakt:
E-Mail: kontakt@ullibauer.de
Telefon: +49 176 63161250
Web: www.ullibauer.de

© 2025 Ulli Bauer. Alle Rechte vorbehalten."""
        
        messagebox.showinfo("Über Heizlastberechnung", about_text)
    
    def show_help(self):
        """Zeigt die Hilfe an."""
        help_text = """Hilfe - Heizlastberechnung

1. Projekt erstellen:
   - Klicken Sie auf "Neu" in der Projektliste
   - Geben Sie alle Projektdaten ein
   - Speichern Sie das Projekt

2. Räume hinzufügen:
   - Wählen Sie ein Projekt aus
   - Wechseln Sie zum Tab "Räume"
   - Klicken Sie auf "Neuer Raum"
   - Geben Sie alle Raumdaten ein

3. Heizlast berechnen:
   - Wechseln Sie zum Tab "Berechnung"
   - Prüfen Sie die Außentemperatur
   - Klicken Sie auf "Heizlast berechnen"

4. Ergebnisse anzeigen:
   - Die Ergebnisse werden in der Tabelle angezeigt
   - Exportieren Sie die Ergebnisse bei Bedarf

Für weitere Hilfe kontaktieren Sie:
kontakt@ullibauer.de"""
        
        messagebox.showinfo("Hilfe", help_text)
    
    def run(self):
        """Startet die Anwendung."""
        self.root.mainloop()

def main():
    """Hauptfunktion der Anwendung."""
    app = HeatingLoadApp()
    app.run()

if __name__ == "__main__":
    main()

