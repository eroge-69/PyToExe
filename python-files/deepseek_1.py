import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import sqlite3
import os
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import calendar
from tkcalendar import DateEntry
import seaborn as sns
import numpy as np
from PIL import Image, ImageTk
import re

class ModernFarmManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AgroManager Pro")
        self.root.geometry("1400x800")
        self.root.state('zoomed')
        
        # Palette de couleurs moderne
        self.colors = {
            'primary': '#4e73df',
            'primary-light': '#859eff',
            'success': '#1cc88a',
            'success-light': '#4ddba8',
            'warning': '#f6c23e',
            'warning-light': '#f8d26e',
            'danger': '#e74a3b',
            'danger-light': '#ed7c71',
            'info': '#36b9cc',
            'info-light': '#6bcfdd',
            'animal': '#20c997',
            'animal-light': '#5dd8b5',
            'health': '#6f42c1',
            'health-light': '#9f7aea',
            'dark': '#2e384d',
            'darker': '#1a202c',
            'light': '#f8f9fc',
            'lighter': '#ffffff',
            'gray': '#e3e6f0',
            'text': '#3a3b45',
            'text-light': '#858796'
        }
        
        # Configuration du style
        self.setup_styles()
        
        # Initialiser les statistiques
        self.total_sales = 0
        self.total_purchases = 0
        self.inventory_count = 0
        self.crop_count = 0
        self.animal_count = 0
        self.profit = 0
        
        # Initialisation des données
        self.setup_icons()
        self.setup_db()
        self.load_data()
        self.update_stats()
        
        # Interface
        self.create_gui()
        self.setup_menu()
        
    def setup_styles(self):
        """Configure les styles modernes de l'interface"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurer les styles de base
        style.configure('.', background=self.colors['light'], 
                       foreground=self.colors['text'], 
                       font=('Segoe UI', 10))
        
        # Configurations spécifiques
        style.configure('TFrame', background=self.colors['light'])
        style.configure('Header.TLabel', font=('Segoe UI', 14, 'bold'), 
                       foreground=self.colors['dark'], background=self.colors['light'])
        style.configure('Card.TFrame', background=self.colors['lighter'], 
                       relief='flat', borderwidth=0)
        style.configure('Card.TLabel', background=self.colors['lighter'])
        style.configure('CardValue.TLabel', font=('Segoe UI', 18, 'bold'), 
                       background=self.colors['lighter'])
        style.configure('CardTitle.TLabel', font=('Segoe UI', 10), 
                       foreground=self.colors['text-light'], background=self.colors['lighter'])
        
        style.configure('TButton', font=('Segoe UI', 10), padding=8, 
                       background=self.colors['primary'], foreground='white')
        style.map('TButton', 
                 background=[('active', self.colors['primary-light'])])
        
        style.configure('Nav.TButton', font=('Segoe UI', 10), padding=10, 
                       anchor='w', background=self.colors['darker'], 
                       foreground='white', borderwidth=0)
        style.map('Nav.TButton', 
                 background=[('active', self.colors['dark'])])
        
        style.configure('Treeview', font=('Segoe UI', 10), rowheight=30, 
                       fieldbackground=self.colors['lighter'])
        style.configure('Treeview.Heading', font=('Segoe UI', 10, 'bold'), 
                       background=self.colors['gray'], foreground=self.colors['text'])
        style.map('Treeview', background=[('selected', self.colors['primary-light'])])
        
        # Configurer le style des onglets
        style.configure('TNotebook', background=self.colors['light'], borderwidth=0)
        style.configure('TNotebook.Tab', font=('Segoe UI', 10, 'bold'), 
                       padding=[15, 5], background=self.colors['gray'], 
                       lightcolor=self.colors['gray'], borderwidth=0)
        style.map('TNotebook.Tab', 
                 background=[('selected', self.colors['lighter'])],
                 expand=[('selected', [1, 1, 1, 0])])
    
    def setup_icons(self):
        """Définit les icônes modernes pour l'interface"""
        self.icons = {
            "dashboard": "📊", "purchases": "🛒", "crops": "🌱",
            "inventory": "📦", "sales": "💰", "fields": "🌾",
            "animals": "🐄", "health": "💉", "feeding": "🥕",
            "add": "➕", "edit": "✏️", "delete": "🗑️",
            "refresh": "🔄", "chart": "📈", "save": "💾",
            "export": "📤", "user": "👤", "settings": "⚙️",
            "notification": "🔔", "logout": "🚪"
        }
    
    def setup_db(self):
        """Initialise la base de données"""
        os.makedirs("db", exist_ok=True)
        self.conn = sqlite3.connect('db/farm_management.db')
        self.cursor = self.conn.cursor()
        
        # Création des tables
        tables = [
            """CREATE TABLE IF NOT EXISTS purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                item TEXT NOT NULL,
                category TEXT NOT NULL,
                quantity REAL NOT NULL,
                unit TEXT NOT NULL,
                amount REAL NOT NULL,
                supplier TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                product TEXT NOT NULL,
                quantity REAL NOT NULL,
                unit TEXT NOT NULL,
                price_per_unit REAL NOT NULL,
                total REAL NOT NULL,
                customer TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item TEXT NOT NULL,
                category TEXT NOT NULL,
                quantity REAL NOT NULL,
                unit TEXT NOT NULL,
                last_update TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS crops (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                planting_date TEXT NOT NULL,
                harvest_date TEXT,
                field_location TEXT NOT NULL,
                status TEXT NOT NULL
            )""",
            """CREATE TABLE IF NOT EXISTS animals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                animal_type TEXT NOT NULL,
                breed TEXT,
                quantity INTEGER NOT NULL,
                location TEXT NOT NULL,
                status TEXT NOT NULL
            )""",
            """CREATE TABLE IF NOT EXISTS animal_health (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                animal_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                condition TEXT NOT NULL,
                treatment TEXT,
                veterinarian TEXT,
                notes TEXT,
                FOREIGN KEY (animal_id) REFERENCES animals (id)
            )""",
            """CREATE TABLE IF NOT EXISTS feeding (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                animal_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                food_type TEXT NOT NULL,
                quantity REAL NOT NULL,
                unit TEXT NOT NULL,
                notes TEXT,
                FOREIGN KEY (animal_id) REFERENCES animals (id)
            )""",
            """CREATE TABLE IF NOT EXISTS fields (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                location TEXT NOT NULL,
                size REAL NOT NULL,
                unit TEXT NOT NULL,
                crop_id INTEGER,
                status TEXT NOT NULL,
                FOREIGN KEY (crop_id) REFERENCES crops (id)
            )"""
        ]
        
        for table in tables:
            self.cursor.execute(table)
        
        self.conn.commit()
    
    def load_data(self):
        """Charge les données depuis la base de données"""
        try:
            # Charger les achats
            self.purchases = pd.read_sql_query("SELECT * FROM purchases", self.conn)
            if not self.purchases.empty and 'date' in self.purchases.columns:
                self.purchases['date'] = pd.to_datetime(self.purchases['date'])
            
            # Charger les ventes
            self.sales = pd.read_sql_query("SELECT * FROM sales", self.conn)
            if not self.sales.empty and 'date' in self.sales.columns:
                self.sales['date'] = pd.to_datetime(self.sales['date'])
            
            # Charger l'inventaire
            self.inventory = pd.read_sql_query("SELECT * FROM inventory", self.conn)
            
            # Charger les cultures
            self.crops = pd.read_sql_query("SELECT * FROM crops", self.conn)
            if not self.crops.empty and 'planting_date' in self.crops.columns:
                self.crops['planting_date'] = pd.to_datetime(self.crops['planting_date'])
            if not self.crops.empty and 'harvest_date' in self.crops.columns:
                self.crops['harvest_date'] = pd.to_datetime(self.crops['harvest_date'])
            
            # Charger les animaux
            self.animals = pd.read_sql_query("SELECT * FROM animals", self.conn)
            
            # Charger la santé animale
            self.animal_health = pd.read_sql_query("SELECT * FROM animal_health", self.conn)
            if not self.animal_health.empty and 'date' in self.animal_health.columns:
                self.animal_health['date'] = pd.to_datetime(self.animal_health['date'])
            
            # Charger l'alimentation
            self.feeding = pd.read_sql_query("SELECT * FROM feeding", self.conn)
            if not self.feeding.empty and 'date' in self.feeding.columns:
                self.feeding['date'] = pd.to_datetime(self.feeding['date'])
            
            # Charger les champs
            self.fields = pd.read_sql_query("SELECT * FROM fields", self.conn)
            
        except pd.io.sql.DatabaseError as e:
            messagebox.showerror("Erreur de base de données", f"Erreur lors du chargement des données : {str(e)}")
            # Créer des DataFrames vides en cas d'erreur
            self.purchases = pd.DataFrame()
            self.sales = pd.DataFrame()
            self.inventory = pd.DataFrame()
            self.crops = pd.DataFrame()
            self.animals = pd.DataFrame()
            self.animal_health = pd.DataFrame()
            self.feeding = pd.DataFrame()
            self.fields = pd.DataFrame()
    
    def update_stats(self):
        """Met à jour les statistiques"""
        self.total_sales = self.sales['total'].sum() if not self.sales.empty and 'total' in self.sales.columns else 0
        self.total_purchases = self.purchases['amount'].sum() if not self.purchases.empty and 'amount' in self.purchases.columns else 0
        self.inventory_count = self.inventory['quantity'].sum() if not self.inventory.empty and 'quantity' in self.inventory.columns else 0
        self.crop_count = self.crops.shape[0]
        self.animal_count = self.animals['quantity'].sum() if not self.animals.empty and 'quantity' in self.animals.columns else 0
        self.profit = self.total_sales - self.total_purchases
    
    def create_gui(self):
        """Crée l'interface graphique moderne"""
        # Conteneur principal avec fond moderne
        main_container = ttk.Frame(self.root, style='TFrame')
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Barre latérale moderne
        self.create_modern_sidebar(main_container)
        
        # Zone de contenu principale
        self.content_area = ttk.Frame(main_container, style='Card.TFrame')
        self.content_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, 
                              padx=20, pady=20, ipadx=10, ipady=10)
        
        # Barre d'état moderne
        self.status_bar = ttk.Label(self.root, text="Prêt • AgroManager Pro", 
                                   relief=tk.FLAT, anchor=tk.W, 
                                   background=self.colors['darker'], 
                                   foreground='white', font=('Segoe UI', 9))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Afficher le tableau de bord par défaut
        self.show_dashboard()
    
    def create_modern_sidebar(self, parent):
        """Crée une barre latérale moderne"""
        sidebar = ttk.Frame(parent, width=250, style='TFrame')
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=0, pady=0)
        sidebar.config(style='TFrame')
        
        # En-tête de la barre latérale
        header_frame = ttk.Frame(sidebar, style='TFrame')
        header_frame.pack(fill=tk.X, pady=(20, 15), padx=15)
        
        # Logo moderne
        ttk.Label(header_frame, text="AgroManager", 
                 font=("Segoe UI", 18, "bold"), 
                 foreground=self.colors['lighter'], 
                 background=self.colors['darker']).pack(fill=tk.X, pady=10, padx=10)
        
        # Boutons de navigation modernes
        nav_buttons = [
            ("Tableau de Bord", "dashboard", self.show_dashboard),
            ("Achats", "purchases", self.show_purchases),
            ("Cultures", "crops", self.show_crops),
            ("Animaux", "animals", self.show_animals),
            ("Alimentation", "feeding", self.show_feeding),
            ("Santé Animale", "health", self.show_animal_health),
            ("Inventaire", "inventory", self.show_inventory),
            ("Ventes", "sales", self.show_sales),
            ("Champs", "fields", self.show_fields)
        ]
        
        for text, icon, command in nav_buttons:
            btn = ttk.Button(sidebar, text=f"  {self.icons[icon]} {text}", 
                            style='Nav.TButton', command=command)
            btn.pack(fill=tk.X, pady=2, ipady=8, padx=5)
        
        # Séparateur moderne
        separator = ttk.Frame(sidebar, height=2, style='TFrame')
        separator.pack(fill=tk.X, pady=15, padx=10)
        
        # Boutons utilitaires
        ttk.Button(sidebar, text=f"  {self.icons['refresh']} Actualiser", 
                  style='Nav.TButton', command=self.refresh_data).pack(fill=tk.X, pady=2, ipady=8, padx=5)
        
        ttk.Button(sidebar, text=f"  {self.icons['settings']} Paramètres", 
                  style='Nav.TButton', command=self.show_settings).pack(fill=tk.X, pady=2, ipady=8, padx=5)
        
        ttk.Button(sidebar, text=f"  {self.icons['logout']} Déconnexion", 
                  style='Nav.TButton', command=self.root.quit).pack(fill=tk.X, pady=20, ipady=8, padx=5)
    
    def setup_menu(self):
        """Configure la barre de menu moderne"""
        menu_bar = tk.Menu(self.root, bg=self.colors['lighter'], 
                          fg=self.colors['text'], bd=0, relief='flat')
        
        # Menu Fichier
        file_menu = tk.Menu(menu_bar, tearoff=0, bg=self.colors['lighter'], 
                           fg=self.colors['text'], activebackground=self.colors['primary-light'])
        file_menu.add_command(label="Exporter les données...", command=self.export_data)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.root.quit)
        menu_bar.add_cascade(label="Fichier", menu=file_menu)
        
        # Menu Édition
        edit_menu = tk.Menu(menu_bar, tearoff=0, bg=self.colors['lighter'], 
                           fg=self.colors['text'], activebackground=self.colors['primary-light'])
        edit_menu.add_command(label="Ajouter un achat", command=self.add_purchase)
        edit_menu.add_command(label="Ajouter une culture", command=self.add_crop)
        edit_menu.add_command(label="Ajouter un animal", command=self.add_animal)
        edit_menu.add_command(label="Ajouter au stock", command=self.add_inventory)
        edit_menu.add_command(label="Enregistrer une vente", command=self.add_sale)
        edit_menu.add_command(label="Ajouter une santé animale", command=self.add_animal_health)
        edit_menu.add_command(label="Ajouter un champ", command=self.add_field)
        menu_bar.add_cascade(label="Édition", menu=edit_menu)
        
        # Menu Aide
        help_menu = tk.Menu(menu_bar, tearoff=0, bg=self.colors['lighter'], 
                           fg=self.colors['text'], activebackground=self.colors['primary-light'])
        help_menu.add_command(label="À propos", command=self.show_about)
        menu_bar.add_cascade(label="Aide", menu=help_menu)
        
        self.root.config(menu=menu_bar)
    
    def clear_content(self):
        """Vide la zone de contenu"""
        for widget in self.content_area.winfo_children():
            widget.destroy()
    
    def refresh_data(self):
        """Actualise les données depuis la base de données"""
        self.load_data()
        self.update_stats()
        current_title = self.root.title()
        if "Tableau de Bord" in current_title:
            self.show_dashboard()
        elif "Animaux" in current_title:
            self.show_animals()
        elif "Alimentation" in current_title:
            self.show_feeding()
        elif "Achats" in current_title:
            self.show_purchases()
        elif "Cultures" in current_title:
            self.show_crops()
        elif "Santé Animale" in current_title:
            self.show_animal_health()
        elif "Inventaire" in current_title:
            self.show_inventory()
        elif "Ventes" in current_title:
            self.show_sales()
        elif "Champs" in current_title:
            self.show_fields()
        
        self.status_bar.config(text="Données actualisées avec succès")
    
    def show_dashboard(self):
        """Affiche le tableau de bord moderne"""
        self.clear_content()
        self.root.title("AgroManager Pro - Tableau de Bord")
        
        # Titre moderne
        header = ttk.Frame(self.content_area)
        header.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(header, text="Tableau de Bord", style='Header.TLabel').pack(side=tk.LEFT)
        
        # Bouton d'actualisation moderne
        refresh_btn = ttk.Button(header, text=f"{self.icons['refresh']} Actualiser", 
                                command=self.refresh_data, width=15)
        refresh_btn.pack(side=tk.RIGHT)
        
        # Cartes de statistiques modernes
        stats_frame = ttk.Frame(self.content_area)
        stats_frame.pack(fill=tk.X, pady=10)
        
        stats = [
            (f"{self.total_sales:,.2f} €", "Ventes Totales", "sales", 'success'),
            (f"{self.total_purchases:,.2f} €", "Achats Totaux", "purchases", 'danger'),
            (f"{self.inventory_count}", "Produits en Stock", "inventory", 'warning'),
            (f"{self.crop_count}", "Cultures Actives", "crops", 'success'),
            (f"{self.animal_count}", "Animaux", "animals", 'animal'),
            (f"{self.profit:,.2f} €", "Bénéfice Net", "sales", 'primary')
        ]
        
        for value, label, icon, color_key in stats:
            color = self.colors[color_key]
            bg_color = self.colors[color_key + '-light']
            
            card = ttk.Frame(stats_frame, style='Card.TFrame', padding=15)
            card.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=8, ipadx=5)
            
            # Icône avec fond de couleur
            icon_frame = ttk.Frame(card, width=50, height=50, 
                                  style='Card.TFrame')
            icon_frame.pack_propagate(False)
            icon_frame.pack(pady=(0, 10))
            
            # Correction: Utiliser la couleur claire pour le fond
            ttk.Label(icon_frame, text=self.icons[icon], font=("Segoe UI", 18), 
                     background=bg_color,
                     foreground=color, padding=10).pack(expand=True)
            
            # Valeur et titre
            ttk.Label(card, text=value, style='CardValue.TLabel', 
                     foreground=color).pack()
            ttk.Label(card, text=label, style='CardTitle.TLabel').pack()
        
        # Graphiques modernes
        charts_frame = ttk.Frame(self.content_area)
        charts_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        # Titre des graphiques
        ttk.Label(charts_frame, text="Analyses", style='Header.TLabel').pack(anchor=tk.W, pady=(0, 10))
        
        # Conteneur pour les graphiques
        charts_container = ttk.Frame(charts_frame)
        charts_container.pack(fill=tk.BOTH, expand=True)
        
        # Graphique 1: Ventes par mois
        chart1_frame = ttk.Frame(charts_container, style='Card.TFrame', padding=15)
        chart1_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8)
        
        if not self.sales.empty and 'date' in self.sales.columns and 'total' in self.sales.columns:
            # Appliquer un style seaborn moderne
            sns.set_theme(style="whitegrid")
            
            # Copie des données pour éviter les modifications sur l'original
            sales_data = self.sales.copy()
            
            # Gestion des valeurs manquantes
            sales_data = sales_data.dropna(subset=['date', 'total'])
            
            if not sales_data.empty:
                sales_data['date'] = pd.to_datetime(sales_data['date'])
                sales_data['month'] = sales_data['date'].dt.month
                sales_data['year'] = sales_data['date'].dt.year
                
                # Regrouper par année et mois
                monthly_sales = sales_data.groupby(['year', 'month'])['total'].sum().reset_index()
                
                # Créer une colonne de date pour le tri
                monthly_sales['date'] = pd.to_datetime(
                    monthly_sales['year'].astype(str) + '-' + 
                    monthly_sales['month'].astype(str) + '-01'
                )
                monthly_sales = monthly_sales.sort_values('date')
                
                # Formater les étiquettes
                monthly_sales['period'] = monthly_sales['month'].apply(lambda x: calendar.month_abbr[x]) + ' ' + monthly_sales['year'].astype(str)
                
                fig1 = plt.Figure(figsize=(6, 4), dpi=100)
                ax1 = fig1.add_subplot(111)
                
                # Utiliser une palette de couleurs moderne
                colors = sns.color_palette("Blues_d", len(monthly_sales))
                sns.barplot(x='period', y='total', data=monthly_sales, ax=ax1, palette=colors)
                
                # Style moderne
                ax1.set_title('Ventes Mensuelles', fontsize=12, fontweight='bold')
                ax1.set_xlabel('')
                ax1.set_ylabel('Montant (€)')
                ax1.tick_params(axis='x', rotation=45)
                ax1.grid(True, linestyle='--', alpha=0.7)
                
                canvas1 = FigureCanvasTkAgg(fig1, master=chart1_frame)
                canvas1.draw()
                canvas1.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            else:
                ttk.Label(chart1_frame, text="Données de vente incomplètes").pack(expand=True)
        else:
            ttk.Label(chart1_frame, text="Aucune donnée de vente disponible").pack(expand=True)
        
        # Graphique 2: Dépenses par catégorie
        chart2_frame = ttk.Frame(charts_container, style='Card.TFrame', padding=15)
        chart2_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8)
        
        if not self.purchases.empty and 'category' in self.purchases.columns and 'amount' in self.purchases.columns:
            # Appliquer un style seaborn moderne
            sns.set_theme(style="whitegrid")
            
            # Copie des données pour éviter les modifications sur l'original
            purchases_data = self.purchases.copy()
            
            # Gestion des valeurs manquantes
            purchases_data = purchases_data.dropna(subset=['category', 'amount'])
            
            if not purchases_data.empty:
                expenses_by_cat = purchases_data.groupby('category')['amount'].sum()
                
                # Filtrer les petites catégories
                threshold = expenses_by_cat.sum() * 0.05  # 5% du total
                main_categories = expenses_by_cat[expenses_by_cat >= threshold]
                other = expenses_by_cat[expenses_by_cat < threshold].sum()
                
                if other > 0:
                    main_categories['Autres'] = other
                
                # Créer le graphique
                fig2 = plt.Figure(figsize=(6, 4), dpi=100)
                ax2 = fig2.add_subplot(111)
                
                # Utiliser une palette de couleurs moderne
                colors = sns.color_palette("pastel", len(main_categories))
                main_categories.plot(kind='pie', ax=ax2, autopct='%1.1f%%', 
                                   colors=colors, wedgeprops={'linewidth': 1, 'edgecolor': 'white'},
                                   textprops={'fontsize': 9})
                
                # Style moderne
                ax2.set_title('Dépenses par Catégorie', fontsize=12, fontweight='bold')
                ax2.set_ylabel('')
                
                canvas2 = FigureCanvasTkAgg(fig2, master=chart2_frame)
                canvas2.draw()
                canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            else:
                ttk.Label(chart2_frame, text="Données d'achat incomplètes").pack(expand=True)
        else:
            ttk.Label(chart2_frame, text="Aucune donnée d'achat disponible").pack(expand=True)
    
    # ======================================================================
    # SECTION ANIMAUX
    # ======================================================================
    
    def show_animals(self):
        """Affiche la gestion moderne des animaux"""
        self.clear_content()
        self.root.title("AgroManager Pro - Gestion des Animaux")
        
        # Titre moderne
        header = ttk.Frame(self.content_area)
        header.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(header, text="Gestion des Animaux", style='Header.TLabel').pack(side=tk.LEFT)
        
        # Boutons d'action modernes
        btn_frame = ttk.Frame(header)
        btn_frame.pack(side=tk.RIGHT)
        
        ttk.Button(btn_frame, text=f"{self.icons['add']} Ajouter", 
                  command=self.add_animal, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text=f"{self.icons['edit']} Modifier", 
                  command=self.edit_animal, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text=f"{self.icons['delete']} Supprimer", 
                  command=self.delete_animal, width=12).pack(side=tk.LEFT, padx=5)
        
        # Tableau moderne des animaux
        if not self.animals.empty:
            self.create_modern_table(
                self.animals, 
                ["animal_type", "breed", "quantity", "location", "status"],
                ["Type", "Race", "Quantité", "Emplacement", "Statut"],
                self.colors['animal-light']
            )
        else:
            ttk.Label(self.content_area, text="Aucun animal enregistré", 
                     font=('Segoe UI', 11)).pack(expand=True)
    
    def add_animal(self):
        """Ouvre une fenêtre moderne pour ajouter un animal"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Ajouter un animal")
        dialog.geometry("500x500")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.colors['light'])
        
        # Style pour la fenêtre de dialogue
        dialog.style = ttk.Style()
        dialog.style.configure('Dialog.TFrame', background=self.colors['light'])
        dialog.style.configure('Dialog.TLabel', background=self.colors['light'], 
                              foreground=self.colors['text'], font=('Segoe UI', 10))
        dialog.style.configure('Dialog.TCombobox', fieldbackground=self.colors['lighter'])
        
        # Formulaire moderne
        form_frame = ttk.Frame(dialog, style='Dialog.TFrame', padding=25)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(form_frame, text="Ajouter un animal", 
                 font=('Segoe UI', 14, 'bold'), style='Dialog.TLabel').grid(row=0, column=0, columnspan=2, pady=10)
        
        # Type d'animal
        ttk.Label(form_frame, text="Type d'animal:", style='Dialog.TLabel').grid(row=1, column=0, padx=5, pady=8, sticky=tk.W)
        animal_type_combo = ttk.Combobox(form_frame, values=["Bovin", "Ovin", "Volaille", "Porcin", "Autre"], 
                                        style='Dialog.TCombobox')
        animal_type_combo.grid(row=1, column=1, padx=5, pady=8, sticky=tk.EW)
        animal_type_combo.current(0)
        
        # Race
        ttk.Label(form_frame, text="Race:", style='Dialog.TLabel').grid(row=2, column=0, padx=5, pady=8, sticky=tk.W)
        breed_entry = ttk.Entry(form_frame, style='Dialog.TCombobox')
        breed_entry.grid(row=2, column=1, padx=5, pady=8, sticky=tk.EW)
        
        # Quantité
        ttk.Label(form_frame, text="Quantité:", style='Dialog.TLabel').grid(row=3, column=0, padx=5, pady=8, sticky=tk.W)
        quantity_entry = ttk.Entry(form_frame, style='Dialog.TCombobox')
        quantity_entry.grid(row=3, column=1, padx=5, pady=8, sticky=tk.EW)
        
        # Emplacement
        ttk.Label(form_frame, text="Emplacement:", style='Dialog.TLabel').grid(row=4, column=0, padx=5, pady=8, sticky=tk.W)
        location_entry = ttk.Entry(form_frame, style='Dialog.TCombobox')
        location_entry.grid(row=4, column=1, padx=5, pady=8, sticky=tk.EW)
        
        # Boutons modernes
        btn_frame = ttk.Frame(form_frame, style='Dialog.TFrame')
        btn_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        cancel_btn = ttk.Button(btn_frame, text="Annuler", command=dialog.destroy,
                               style='TButton')
        cancel_btn.pack(side=tk.RIGHT, padx=10)
        
        save_btn = ttk.Button(btn_frame, text="Enregistrer", 
                             command=lambda: self.save_animal(
                                 animal_type_combo.get(),
                                 breed_entry.get(),
                                 quantity_entry.get(),
                                 location_entry.get(),
                                 dialog
                             ), style='TButton')
        save_btn.pack(side=tk.RIGHT)
    
    def save_animal(self, animal_type, breed, quantity, location, dialog):
        """Enregistre un nouvel animal dans la base de données"""
        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError("La quantité doit être un nombre positif")
            
            self.cursor.execute(
                "INSERT INTO animals (animal_type, breed, quantity, location, status) VALUES (?, ?, ?, ?, ?)",
                (animal_type, breed, quantity, location, "Actif")
            )
            self.conn.commit()
            messagebox.showinfo("Succès", "Animal ajouté avec succès")
            dialog.destroy()
            self.refresh_data()
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer une quantité valide")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue : {str(e)}")
    
    def edit_animal(self):
        """Modifie l'animal sélectionné"""
        if not hasattr(self, 'current_tree') or not self.current_tree.selection():
            messagebox.showwarning("Sélection", "Veuillez sélectionner un animal")
            return
        
        selected_item = self.current_tree.selection()[0]
        item_values = self.current_tree.item(selected_item, 'values')
        
        # Ouvrir une fenêtre de modification avec les valeurs actuelles
        dialog = tk.Toplevel(self.root)
        dialog.title("Modifier l'animal")
        dialog.geometry("500x500")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.colors['light'])
        
        # Style pour la fenêtre de dialogue
        dialog.style = ttk.Style()
        dialog.style.configure('Dialog.TFrame', background=self.colors['light'])
        dialog.style.configure('Dialog.TLabel', background=self.colors['light'], 
                              foreground=self.colors['text'], font=('Segoe UI', 10))
        dialog.style.configure('Dialog.TCombobox', fieldbackground=self.colors['lighter'])
        
        # Formulaire moderne
        form_frame = ttk.Frame(dialog, style='Dialog.TFrame', padding=25)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(form_frame, text="Modifier l'animal", 
                 font=('Segoe UI', 14, 'bold'), style='Dialog.TLabel').grid(row=0, column=0, columnspan=2, pady=10)
        
        # Type d'animal
        ttk.Label(form_frame, text="Type d'animal:", style='Dialog.TLabel').grid(row=1, column=0, padx=5, pady=8, sticky=tk.W)
        animal_type_combo = ttk.Combobox(form_frame, values=["Bovin", "Ovin", "Volaille", "Porcin", "Autre"], 
                                        style='Dialog.TCombobox')
        animal_type_combo.grid(row=1, column=1, padx=5, pady=8, sticky=tk.EW)
        animal_type_combo.set(item_values[0])
        
        # Race
        ttk.Label(form_frame, text="Race:", style='Dialog.TLabel').grid(row=2, column=0, padx=5, pady=8, sticky=tk.W)
        breed_entry = ttk.Entry(form_frame, style='Dialog.TCombobox')
        breed_entry.grid(row=2, column=1, padx=5, pady=8, sticky=tk.EW)
        breed_entry.insert(0, item_values[1])
        
        # Quantité
        ttk.Label(form_frame, text="Quantité:", style='Dialog.TLabel').grid(row=3, column=0, padx=5, pady=8, sticky=tk.W)
        quantity_entry = ttk.Entry(form_frame, style='Dialog.TCombobox')
        quantity_entry.grid(row=3, column=1, padx=5, pady=8, sticky=tk.EW)
        quantity_entry.insert(0, item_values[2])
        
        # Emplacement
        ttk.Label(form_frame, text="Emplacement:", style='Dialog.TLabel').grid(row=4, column=0, padx=5, pady=8, sticky=tk.W)
        location_entry = ttk.Entry(form_frame, style='Dialog.TCombobox')
        location_entry.grid(row=4, column=1, padx=5, pady=8, sticky=tk.EW)
        location_entry.insert(0, item_values[3])
        
        # Boutons modernes
        btn_frame = ttk.Frame(form_frame, style='Dialog.TFrame')
        btn_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        cancel_btn = ttk.Button(btn_frame, text="Annuler", command=dialog.destroy,
                               style='TButton')
        cancel_btn.pack(side=tk.RIGHT, padx=10)
        
        save_btn = ttk.Button(btn_frame, text="Enregistrer", 
                             command=lambda: self.update_animal(
                                 self.animals.iloc[int(selected_item[1:])-1]['id'],
                                 animal_type_combo.get(),
                                 breed_entry.get(),
                                 quantity_entry.get(),
                                 location_entry.get(),
                                 dialog
                             ), style='TButton')
        save_btn.pack(side=tk.RIGHT)
    
    def update_animal(self, animal_id, animal_type, breed, quantity, location, dialog):
        """Met à jour un animal dans la base de données"""
        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError("La quantité doit être un nombre positif")
            
            self.cursor.execute(
                "UPDATE animals SET animal_type=?, breed=?, quantity=?, location=? WHERE id=?",
                (animal_type, breed, quantity, location, animal_id)
            )
            self.conn.commit()
            messagebox.showinfo("Succès", "Animal modifié avec succès")
            dialog.destroy()
            self.refresh_data()
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer une quantité valide")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue : {str(e)}")
    
    def delete_animal(self):
        """Supprime l'animal sélectionné"""
        if not hasattr(self, 'current_tree') or not self.current_tree.selection():
            messagebox.showwarning("Sélection", "Veuillez sélectionner un animal")
            return
        
        selected_item = self.current_tree.selection()[0]
        animal_id = self.animals.iloc[int(selected_item[1:])-1]['id']
        
        if messagebox.askyesno("Confirmer", "Êtes-vous sûr de vouloir supprimer cet animal ?"):
            try:
                self.cursor.execute("DELETE FROM animals WHERE id=?", (animal_id,))
                self.conn.commit()
                messagebox.showinfo("Succès", "Animal supprimé avec succès")
                self.refresh_data()
            except Exception as e:
                messagebox.showerror("Erreur", f"Une erreur est survenue : {str(e)}")
    
    # ======================================================================
    # SECTION ALIMENTATION
    # ======================================================================
    
    def show_feeding(self):
        """Affiche la gestion moderne de l'alimentation"""
        self.clear_content()
        self.root.title("AgroManager Pro - Alimentation Animale")
        
        # Titre moderne
        header = ttk.Frame(self.content_area)
        header.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(header, text="Alimentation Animale", style='Header.TLabel').pack(side=tk.LEFT)
        
        # Boutons d'action modernes
        btn_frame = ttk.Frame(header)
        btn_frame.pack(side=tk.RIGHT)
        
        ttk.Button(btn_frame, text=f"{self.icons['add']} Ajouter", 
                  command=self.add_feeding, width=12).pack(side=tk.LEFT, padx=5)
        
        # Tableau moderne de l'alimentation
        if not self.feeding.empty:
            self.create_modern_table(
                self.feeding, 
                ["date", "food_type", "quantity", "animal_id"],
                ["Date", "Type d'aliment", "Quantité", "Animal"],
                self.colors['success-light']
            )
        else:
            ttk.Label(self.content_area, text="Aucune donnée d'alimentation", 
                     font=('Segoe UI', 11)).pack(expand=True)
    
    def add_feeding(self):
        """Ouvre une fenêtre moderne pour ajouter une alimentation"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Ajouter une alimentation")
        dialog.geometry("500x500")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.colors['light'])
        
        # Style pour la fenêtre de dialogue
        dialog.style = ttk.Style()
        dialog.style.configure('Dialog.TFrame', background=self.colors['light'])
        dialog.style.configure('Dialog.TLabel', background=self.colors['light'], 
                              foreground=self.colors['text'], font=('Segoe UI', 10))
        dialog.style.configure('Dialog.TCombobox', fieldbackground=self.colors['lighter'])
        
        # Formulaire moderne
        form_frame = ttk.Frame(dialog, style='Dialog.TFrame', padding=25)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(form_frame, text="Ajouter une alimentation", 
                 font=('Segoe UI', 14, 'bold'), style='Dialog.TLabel').grid(row=0, column=0, columnspan=2, pady=10)
        
        # Date
        ttk.Label(form_frame, text="Date:", style='Dialog.TLabel').grid(row=1, column=0, padx=5, pady=8, sticky=tk.W)
        date_entry = DateEntry(form_frame, date_pattern='yyyy-mm-dd', 
                              background='darkblue', foreground='white', 
                              borderwidth=2, year=datetime.now().year, 
                              month=datetime.now().month, day=datetime.now().day)
        date_entry.grid(row=1, column=1, padx=5, pady=8, sticky=tk.EW)
        
        # Type d'aliment
        ttk.Label(form_frame, text="Type d'aliment:", style='Dialog.TLabel').grid(row=2, column=0, padx=5, pady=8, sticky=tk.W)
        food_combo = ttk.Combobox(form_frame, values=["Fourrage", "Céréales", "Complément minéral", "Autre"], 
                                 style='Dialog.TCombobox')
        food_combo.grid(row=2, column=1, padx=5, pady=8, sticky=tk.EW)
        food_combo.current(0)
        
        # Quantité
        ttk.Label(form_frame, text="Quantité (kg):", style='Dialog.TLabel').grid(row=3, column=0, padx=5, pady=8, sticky=tk.W)
        quantity_entry = ttk.Entry(form_frame, style='Dialog.TCombobox')
        quantity_entry.grid(row=3, column=1, padx=5, pady=8, sticky=tk.EW)
        
        # Notes
        ttk.Label(form_frame, text="Notes:", style='Dialog.TLabel').grid(row=4, column=0, padx=5, pady=8, sticky=tk.W)
        notes_entry = tk.Text(form_frame, height=4, width=30, font=('Segoe UI', 10))
        notes_entry.grid(row=4, column=1, padx=5, pady=8, sticky=tk.EW)
        
        # Boutons modernes
        btn_frame = ttk.Frame(form_frame, style='Dialog.TFrame')
        btn_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        cancel_btn = ttk.Button(btn_frame, text="Annuler", command=dialog.destroy,
                               style='TButton')
        cancel_btn.pack(side=tk.RIGHT, padx=10)
        
        save_btn = ttk.Button(btn_frame, text="Enregistrer", 
                             command=lambda: self.save_feeding(
                                 date_entry.get(),
                                 food_combo.get(),
                                 quantity_entry.get(),
                                 notes_entry.get("1.0", tk.END),
                                 dialog
                             ), style='TButton')
        save_btn.pack(side=tk.RIGHT)
    
    def save_feeding(self, date, food_type, quantity, notes, dialog):
        """Enregistre une nouvelle alimentation dans la base de données"""
        try:
            quantity = float(quantity)
            if quantity <= 0:
                raise ValueError("La quantité doit être un nombre positif")
            
            # Ici on suppose qu'on ajoute pour le premier animal
            # Dans une version complète, on aurait une sélection d'animal
            animal_id = 1 if self.animals.empty else self.animals.iloc[0]['id']
            
            self.cursor.execute(
                "INSERT INTO feeding (animal_id, date, food_type, quantity, unit, notes) VALUES (?, ?, ?, ?, ?, ?)",
                (animal_id, date, food_type, quantity, "kg", notes.strip())
            )
            self.conn.commit()
            messagebox.showinfo("Succès", "Alimentation enregistrée avec succès")
            dialog.destroy()
            self.refresh_data()
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer une quantité valide")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue : {str(e)}")
    
    # ======================================================================
    # SECTION VENTES
    # ======================================================================
    
    def show_sales(self):
        """Affiche la gestion des ventes avec fonctionnalités complètes"""
        self.clear_content()
        self.root.title("AgroManager Pro - Gestion des Ventes")
        
        # Titre moderne
        header = ttk.Frame(self.content_area)
        header.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(header, text="Gestion des Ventes", style='Header.TLabel').pack(side=tk.LEFT)
        
        # Boutons d'action modernes
        btn_frame = ttk.Frame(header)
        btn_frame.pack(side=tk.RIGHT)
        
        ttk.Button(btn_frame, text=f"{self.icons['add']} Ajouter", 
                  command=self.add_sale, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text=f"{self.icons['edit']} Modifier", 
                  command=self.edit_sale, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text=f"{self.icons['delete']} Supprimer", 
                  command=self.delete_sale, width=12).pack(side=tk.LEFT, padx=5)
        
        # Tableau moderne des ventes
        if not self.sales.empty:
            # Convertir les dates en format lisible
            sales_display = self.sales.copy()
            sales_display['date'] = pd.to_datetime(sales_display['date']).dt.strftime('%d/%m/%Y')
            
            self.create_modern_table(
                sales_display, 
                ["date", "product", "quantity", "unit", "price_per_unit", "total", "customer"],
                ["Date", "Produit", "Quantité", "Unité", "Prix unitaire", "Total", "Client"],
                self.colors['warning-light']
            )
        else:
            ttk.Label(self.content_area, text="Aucune vente enregistrée", 
                     font=('Segoe UI', 11)).pack(expand=True)
    
    def add_sale(self):
        """Ouvre une fenêtre pour ajouter une vente"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Ajouter une vente")
        dialog.geometry("500x550")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.colors['light'])
        
        # Style pour la fenêtre de dialogue
        dialog.style = ttk.Style()
        dialog.style.configure('Dialog.TFrame', background=self.colors['light'])
        dialog.style.configure('Dialog.TLabel', background=self.colors['light'], 
                              foreground=self.colors['text'], font=('Segoe UI', 10))
        dialog.style.configure('Dialog.TCombobox', fieldbackground=self.colors['lighter'])
        
        # Formulaire moderne
        form_frame = ttk.Frame(dialog, style='Dialog.TFrame', padding=25)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(form_frame, text="Ajouter une vente", 
                 font=('Segoe UI', 14, 'bold'), style='Dialog.TLabel').grid(row=0, column=0, columnspan=2, pady=10)
        
        # Champs du formulaire
        date_entry = self.create_form_field(form_frame, "Date", 1, entry_type="date")
        product_entry = self.create_form_field(form_frame, "Produit", 2)
        quantity_entry = self.create_form_field(form_frame, "Quantité", 3)
        unit_combo = self.create_form_field(
            form_frame, "Unité", 4, 
            values=["kg", "L", "unité", "sac", "carton"],
            entry_type="combobox"
        )
        price_entry = self.create_form_field(form_frame, "Prix unitaire (€)", 5)
        customer_entry = self.create_form_field(form_frame, "Client", 6)
        
        # Boutons
        self.create_form_buttons(
            form_frame, 7,
            save_command=lambda: self.save_sale(
                date_entry.get(),
                product_entry.get(),
                quantity_entry.get(),
                unit_combo.get(),
                price_entry.get(),
                customer_entry.get(),
                dialog
            ),
            cancel_command=dialog.destroy
        )
    
    def save_sale(self, date, product, quantity, unit, price, customer, dialog):
        """Enregistre une nouvelle vente dans la base de données"""
        try:
            # Validation des données
            if not all([date, product, quantity, unit, price]):
                raise ValueError("Tous les champs obligatoires doivent être remplis")
            
            quantity = float(quantity)
            price = float(price)
            total = quantity * price
            
            if quantity <= 0 or price <= 0:
                raise ValueError("Les valeurs numériques doivent être positives")
            
            # Insertion dans la base de données
            self.cursor.execute(
                "INSERT INTO sales (date, product, quantity, unit, price_per_unit, total, customer) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (date, product, quantity, unit, price, total, customer)
            )
            self.conn.commit()
            
            messagebox.showinfo("Succès", "Vente enregistrée avec succès")
            dialog.destroy()
            self.refresh_data()
        except ValueError as ve:
            messagebox.showerror("Erreur de validation", str(ve))
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue : {str(e)}")
    
    def edit_sale(self):
        """Modifie la vente sélectionnée"""
        if not hasattr(self, 'current_tree') or not self.current_tree.selection():
            messagebox.showwarning("Sélection", "Veuillez sélectionner une vente")
            return
        
        selected_item = self.current_tree.selection()[0]
        sale = self.sales.iloc[int(selected_item[1:])-1]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Modifier une vente")
        dialog.geometry("500x550")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.colors['light'])
        
        # Style pour la fenêtre de dialogue
        dialog.style = ttk.Style()
        dialog.style.configure('Dialog.TFrame', background=self.colors['light'])
        dialog.style.configure('Dialog.TLabel', background=self.colors['light'], 
                              foreground=self.colors['text'], font=('Segoe UI', 10))
        dialog.style.configure('Dialog.TCombobox', fieldbackground=self.colors['lighter'])
        
        # Formulaire moderne
        form_frame = ttk.Frame(dialog, style='Dialog.TFrame', padding=25)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(form_frame, text="Modifier une vente", 
                 font=('Segoe UI', 14, 'bold'), style='Dialog.TLabel').grid(row=0, column=0, columnspan=2, pady=10)
        
        # Champs du formulaire avec valeurs actuelles
        date_entry = self.create_form_field(
            form_frame, "Date", 1, 
            sale['date'], entry_type="date"
        )
        product_entry = self.create_form_field(
            form_frame, "Produit", 2, 
            sale['product']
        )
        quantity_entry = self.create_form_field(
            form_frame, "Quantité", 3, 
            str(sale['quantity'])
        )
        unit_combo = self.create_form_field(
            form_frame, "Unité", 4, sale['unit'],
            values=["kg", "L", "unité", "sac", "carton"],
            entry_type="combobox"
        )
        price_entry = self.create_form_field(
            form_frame, "Prix unitaire (€)", 5, 
            str(sale['price_per_unit'])
        )
        customer_entry = self.create_form_field(
            form_frame, "Client", 6, 
            sale['customer']
        )
        
        # Boutons
        self.create_form_buttons(
            form_frame, 7,
            save_command=lambda: self.update_sale(
                sale['id'],
                date_entry.get(),
                product_entry.get(),
                quantity_entry.get(),
                unit_combo.get(),
                price_entry.get(),
                customer_entry.get(),
                dialog
            ),
            cancel_command=dialog.destroy
        )
    
    def update_sale(self, sale_id, date, product, quantity, unit, price, customer, dialog):
        """Met à jour une vente dans la base de données"""
        try:
            # Validation des données
            if not all([date, product, quantity, unit, price]):
                raise ValueError("Tous les champs obligatoires doivent être remplis")
            
            quantity = float(quantity)
            price = float(price)
            total = quantity * price
            
            if quantity <= 0 or price <= 0:
                raise ValueError("Les valeurs numériques doivent être positives")
            
            # Mise à jour dans la base de données
            self.cursor.execute(
                "UPDATE sales SET date=?, product=?, quantity=?, unit=?, price_per_unit=?, total=?, customer=? "
                "WHERE id=?",
                (date, product, quantity, unit, price, total, customer, sale_id)
            )
            self.conn.commit()
            
            messagebox.showinfo("Succès", "Vente mise à jour avec succès")
            dialog.destroy()
            self.refresh_data()
        except ValueError as ve:
            messagebox.showerror("Erreur de validation", str(ve))
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue : {str(e)}")
    
    def delete_sale(self):
        """Supprime la vente sélectionnée"""
        if not hasattr(self, 'current_tree') or not self.current_tree.selection():
            messagebox.showwarning("Sélection", "Veuillez sélectionner une vente")
            return
        
        selected_item = self.current_tree.selection()[0]
        sale_id = self.sales.iloc[int(selected_item[1:])-1]['id']
        
        if messagebox.askyesno("Confirmer", "Êtes-vous sûr de vouloir supprimer cette vente ?"):
            try:
                self.cursor.execute("DELETE FROM sales WHERE id=?", (sale_id,))
                self.conn.commit()
                messagebox.showinfo("Succès", "Vente supprimée avec succès")
                self.refresh_data()
            except Exception as e:
                messagebox.showerror("Erreur", f"Une erreur est survenue : {str(e)}")
    
    # ======================================================================
    # SECTION CHAMPS
    # ======================================================================
    
    def show_fields(self):
        """Affiche la gestion des champs avec fonctionnalités complètes"""
        self.clear_content()
        self.root.title("AgroManager Pro - Gestion des Champs")
        
        # Titre moderne
        header = ttk.Frame(self.content_area)
        header.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(header, text="Gestion des Champs", style='Header.TLabel').pack(side=tk.LEFT)
        
        # Boutons d'action modernes
        btn_frame = ttk.Frame(header)
        btn_frame.pack(side=tk.RIGHT)
        
        ttk.Button(btn_frame, text=f"{self.icons['add']} Ajouter", 
                  command=self.add_field, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text=f"{self.icons['edit']} Modifier", 
                  command=self.edit_field, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text=f"{self.icons['delete']} Supprimer", 
                  command=self.delete_field, width=12).pack(side=tk.LEFT, padx=5)
        
        # Tableau moderne des champs
        if not self.fields.empty:
            self.create_modern_table(
                self.fields, 
                ["name", "location", "size", "unit", "status"],
                ["Nom", "Emplacement", "Taille", "Unité", "Statut"],
                self.colors['info-light']
            )
        else:
            ttk.Label(self.content_area, text="Aucun champ enregistré", 
                     font=('Segoe UI', 11)).pack(expand=True)
    
    def add_field(self):
        """Ouvre une fenêtre pour ajouter un champ"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Ajouter un champ")
        dialog.geometry("500x500")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.colors['light'])
        
        # Style pour la fenêtre de dialogue
        dialog.style = ttk.Style()
        dialog.style.configure('Dialog.TFrame', background=self.colors['light'])
        dialog.style.configure('Dialog.TLabel', background=self.colors['light'], 
                              foreground=self.colors['text'], font=('Segoe UI', 10))
        dialog.style.configure('Dialog.TCombobox', fieldbackground=self.colors['lighter'])
        
        # Formulaire moderne
        form_frame = ttk.Frame(dialog, style='Dialog.TFrame', padding=25)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(form_frame, text="Ajouter un champ", 
                 font=('Segoe UI', 14, 'bold'), style='Dialog.TLabel').grid(row=0, column=0, columnspan=2, pady=10)
        
        # Champs du formulaire
        name_entry = self.create_form_field(form_frame, "Nom", 1)
        location_entry = self.create_form_field(form_frame, "Emplacement", 2)
        size_entry = self.create_form_field(form_frame, "Taille", 3)
        unit_combo = self.create_form_field(
            form_frame, "Unité", 4, 
            values=["hectare", "acre", "m²"],
            entry_type="combobox"
        )
        status_combo = self.create_form_field(
            form_frame, "Statut", 5, 
            values=["Disponible", "En culture", "En jachère", "En préparation"],
            entry_type="combobox"
        )
        
        # Boutons
        self.create_form_buttons(
            form_frame, 6,
            save_command=lambda: self.save_field(
                name_entry.get(),
                location_entry.get(),
                size_entry.get(),
                unit_combo.get(),
                status_combo.get(),
                dialog
            ),
            cancel_command=dialog.destroy
        )
    
    def save_field(self, name, location, size, unit, status, dialog):
        """Enregistre un nouveau champ dans la base de données"""
        try:
            # Validation des données
            if not all([name, location, size, unit, status]):
                raise ValueError("Tous les champs obligatoires doivent être remplis")
            
            size = float(size)
            if size <= 0:
                raise ValueError("La taille doit être un nombre positif")
            
            # Insertion dans la base de données
            self.cursor.execute(
                "INSERT INTO fields (name, location, size, unit, status) "
                "VALUES (?, ?, ?, ?, ?)",
                (name, location, size, unit, status)
            )
            self.conn.commit()
            
            messagebox.showinfo("Succès", "Champ ajouté avec succès")
            dialog.destroy()
            self.refresh_data()
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer une taille valide")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue : {str(e)}")
    
    def edit_field(self):
        """Modifie le champ sélectionné"""
        if not hasattr(self, 'current_tree') or not self.current_tree.selection():
            messagebox.showwarning("Sélection", "Veuillez sélectionner un champ")
            return
        
        selected_item = self.current_tree.selection()[0]
        field = self.fields.iloc[int(selected_item[1:])-1]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Modifier un champ")
        dialog.geometry("500x500")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.colors['light'])
        
        # Style pour la fenêtre de dialogue
        dialog.style = ttk.Style()
        dialog.style.configure('Dialog.TFrame', background=self.colors['light'])
        dialog.style.configure('Dialog.TLabel', background=self.colors['light'], 
                              foreground=self.colors['text'], font=('Segoe UI', 10))
        dialog.style.configure('Dialog.TCombobox', fieldbackground=self.colors['lighter'])
        
        # Formulaire moderne
        form_frame = ttk.Frame(dialog, style='Dialog.TFrame', padding=25)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(form_frame, text="Modifier un champ", 
                 font=('Segoe UI', 14, 'bold'), style='Dialog.TLabel').grid(row=0, column=0, columnspan=2, pady=10)
        
        # Champs du formulaire avec valeurs actuelles
        name_entry = self.create_form_field(
            form_frame, "Nom", 1, 
            field['name']
        )
        location_entry = self.create_form_field(
            form_frame, "Emplacement", 2, 
            field['location']
        )
        size_entry = self.create_form_field(
            form_frame, "Taille", 3, 
            str(field['size'])
        )
        unit_combo = self.create_form_field(
            form_frame, "Unité", 4, field['unit'],
            values=["hectare", "acre", "m²"],
            entry_type="combobox"
        )
        status_combo = self.create_form_field(
            form_frame, "Statut", 5, field['status'],
            values=["Disponible", "En culture", "En jachère", "En préparation"],
            entry_type="combobox"
        )
        
        # Boutons
        self.create_form_buttons(
            form_frame, 6,
            save_command=lambda: self.update_field(
                field['id'],
                name_entry.get(),
                location_entry.get(),
                size_entry.get(),
                unit_combo.get(),
                status_combo.get(),
                dialog
            ),
            cancel_command=dialog.destroy
        )
    
    def update_field(self, field_id, name, location, size, unit, status, dialog):
        """Met à jour un champ dans la base de données"""
        try:
            # Validation des données
            if not all([name, location, size, unit, status]):
                raise ValueError("Tous les champs obligatoires doivent être remplis")
            
            size = float(size)
            if size <= 0:
                raise ValueError("La taille doit être un nombre positif")
            
            # Mise à jour dans la base de données
            self.cursor.execute(
                "UPDATE fields SET name=?, location=?, size=?, unit=?, status=? "
                "WHERE id=?",
                (name, location, size, unit, status, field_id)
            )
            self.conn.commit()
            
            messagebox.showinfo("Succès", "Champ mis à jour avec succès")
            dialog.destroy()
            self.refresh_data()
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer une taille valide")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue : {str(e)}")
    
    def delete_field(self):
        """Supprime le champ sélectionné"""
        if not hasattr(self, 'current_tree') or not self.current_tree.selection():
            messagebox.showwarning("Sélection", "Veuillez sélectionner un champ")
            return
        
        selected_item = self.current_tree.selection()[0]
        field_id = self.fields.iloc[int(selected_item[1:])-1]['id']
        
        if messagebox.askyesno("Confirmer", "Êtes-vous sûr de vouloir supprimer ce champ ?"):
            try:
                self.cursor.execute("DELETE FROM fields WHERE id=?", (field_id,))
                self.conn.commit()
                messagebox.showinfo("Succès", "Champ supprimé avec succès")
                self.refresh_data()
            except Exception as e:
                messagebox.showerror("Erreur", f"Une erreur est survenue : {str(e)}")
    
    # ======================================================================
    # AUTRES SECTIONS (PURCHASES, CROPS, ANIMAL HEALTH, INVENTORY)
    # ======================================================================
    
    def show_purchases(self):
        """Affiche la gestion des achats avec fonctionnalités complètes"""
        self.clear_content()
        self.root.title("AgroManager Pro - Gestion des Achats")
        
        # Titre moderne
        header = ttk.Frame(self.content_area)
        header.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(header, text="Gestion des Achats", style='Header.TLabel').pack(side=tk.LEFT)
        
        # Boutons d'action modernes
        btn_frame = ttk.Frame(header)
        btn_frame.pack(side=tk.RIGHT)
        
        ttk.Button(btn_frame, text=f"{self.icons['add']} Ajouter", 
                  command=self.add_purchase, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text=f"{self.icons['edit']} Modifier", 
                  command=self.edit_purchase, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text=f"{self.icons['delete']} Supprimer", 
                  command=self.delete_purchase, width=12).pack(side=tk.LEFT, padx=5)
        
        # Tableau moderne des achats
        if not self.purchases.empty:
            self.create_modern_table(
                self.purchases, 
                ["date", "item", "category", "quantity", "unit", "amount", "supplier"],
                ["Date", "Article", "Catégorie", "Quantité", "Unité", "Montant", "Fournisseur"],
                self.colors['primary-light']
            )
        else:
            ttk.Label(self.content_area, text="Aucun achat enregistré", 
                     font=('Segoe UI', 11)).pack(expand=True)
    
    def show_crops(self):
        """Affiche la gestion des cultures avec fonctionnalités complètes"""
        self.clear_content()
        self.root.title("AgroManager Pro - Gestion des Cultures")
        
        # Titre moderne
        header = ttk.Frame(self.content_area)
        header.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(header, text="Gestion des Cultures", style='Header.TLabel').pack(side=tk.LEFT)
        
        # Boutons d'action modernes
        btn_frame = ttk.Frame(header)
        btn_frame.pack(side=tk.RIGHT)
        
        ttk.Button(btn_frame, text=f"{self.icons['add']} Ajouter", 
                  command=self.add_crop, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text=f"{self.icons['edit']} Modifier", 
                  command=self.edit_crop, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text=f"{self.icons['delete']} Supprimer", 
                  command=self.delete_crop, width=12).pack(side=tk.LEFT, padx=5)
        
        # Tableau moderne des cultures
        if not self.crops.empty:
            # Convertir les dates en format lisible
            crops_display = self.crops.copy()
            crops_display['planting_date'] = pd.to_datetime(crops_display['planting_date']).dt.strftime('%d/%m/%Y')
            crops_display['harvest_date'] = pd.to_datetime(crops_display['harvest_date']).dt.strftime('%d/%m/%Y')
            
            self.create_modern_table(
                crops_display, 
                ["name", "type", "planting_date", "harvest_date", "field_location", "status"],
                ["Nom", "Type", "Date plantation", "Date récolte", "Emplacement", "Statut"],
                self.colors['success-light']
            )
        else:
            tttk.Label(self.content_area, text="Aucune culture enregistrée", 
                     font=('Segoe UI', 11)).pack(expand=True)
    
    def show_animal_health(self):
        """Affiche la gestion de la santé animale avec fonctionnalités complètes"""
        self.clear_content()
        self.root.title("AgroManager Pro - Santé Animale")
        
        # Titre moderne
        header = ttk.Frame(self.content_area)
        header.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(header, text="Santé Animale", style='Header.TLabel').pack(side=tk.LEFT)
        
        # Boutons d'action modernes
        btn_frame = ttk.Frame(header)
        btn_frame.pack(side=tk.RIGHT)
        
        ttk.Button(btn_frame, text=f"{self.icons['add']} Ajouter", 
                  command=self.add_animal_health, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text=f"{self.icons['edit']} Modifier", 
                  command=self.edit_animal_health, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text=f"{self.icons['delete']} Supprimer", 
                  command=self.delete_animal_health, width=12).pack(side=tk.LEFT, padx=5)
        
        # Tableau moderne de la santé animale
        if not self.animal_health.empty:
            # Convertir les dates en format lisible
            health_display = self.animal_health.copy()
            health_display['date'] = pd.to_datetime(health_display['date']).dt.strftime('%d/%m/%Y')
            
            self.create_modern_table(
                health_display, 
                ["animal_id", "date", "condition", "treatment", "veterinarian"],
                ["Animal ID", "Date", "Condition", "Traitement", "Vétérinaire"],
                self.colors['health-light']
            )
        else:
            ttk.Label(self.content_area, text="Aucun enregistrement de santé animale", 
                     font=('Segoe UI', 11)).pack(expand=True)
    
    def show_inventory(self):
        """Affiche la gestion de l'inventaire avec fonctionnalités complètes"""
        self.clear_content()
        self.root.title("AgroManager Pro - Gestion de l'Inventaire")
        
        # Titre moderne
        header = ttk.Frame(self.content_area)
        header.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(header, text="Gestion de l'Inventaire", style='Header.TLabel').pack(side=tk.LEFT)
        
        # Boutons d'action modernes
        btn_frame = ttk.Frame(header)
        btn_frame.pack(side=tk.RIGHT)
        
        ttk.Button(btn_frame, text=f"{self.icons['add']} Ajouter", 
                  command=self.add_inventory, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text=f"{self.icons['edit']} Modifier", 
                  command=self.edit_inventory, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text=f"{self.icons['delete']} Supprimer", 
                  command=self.delete_inventory, width=12).pack(side=tk.LEFT, padx=5)
        
        # Tableau moderne de l'inventaire
        if not self.inventory.empty:
            self.create_modern_table(
                self.inventory, 
                ["item", "category", "quantity", "unit", "last_update"],
                ["Article", "Catégorie", "Quantité", "Unité", "Dernière mise à jour"],
                self.colors['info-light']
            )
        else:
            ttk.Label(self.content_area, text="L'inventaire est vide", 
                     font=('Segoe UI', 11)).pack(expand=True)
    
    # ======================================================================
    # MÉTHODES DE CRÉATION DE TABLEAUX ET FORMULAIRES
    # ======================================================================
    
    def create_modern_table(self, data, columns, headers, accent_color):
        """Crée un tableau moderne dans la zone de contenu"""
        if data.empty:
            ttk.Label(self.content_area, text="Aucune donnée disponible", 
                     font=('Segoe UI', 11)).pack(expand=True)
            return
        
        # Conteneur pour le tableau
        table_container = ttk.Frame(self.content_area, style='Card.TFrame', padding=10)
        table_container.pack(fill=tk.BOTH, expand=True)
        
        # Créer un Treeview avec barre de défilement
        tree_frame = ttk.Frame(table_container)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode='browse')
        
        # Configurer les colonnes
        for col, header in zip(columns, headers):
            tree.heading(col, text=header, anchor=tk.CENTER)
            tree.column(col, width=150, anchor=tk.CENTER)
        
        # Style alterné des lignes
        tree.tag_configure('oddrow', background=self.colors['light'])
        tree.tag_configure('evenrow', background=self.colors['lighter'])
        
        # Ajouter les données
        for i, (_, row) in enumerate(data.iterrows()):
            values = [row[col] if not pd.isna(row[col]) else "" for col in columns]
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            tree.insert("", tk.END, values=values, tags=(tag,))
        
        # Ajouter une barre de défilement
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Barre d'info en bas du tableau
        info_frame = ttk.Frame(table_container, style='Card.TFrame')
        info_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Label(info_frame, text=f"{len(data)} enregistrements", 
                 style='CardTitle.TLabel').pack(side=tk.LEFT)
        
        # Stocker une référence au treeview
        self.current_tree = tree
        self.current_data = data
    
    def create_form_field(self, parent, label, row, default="", entry_type="entry", values=None):
        """Crée un champ de formulaire avec label et widget d'entrée"""
        ttk.Label(parent, text=label + ":", style='Dialog.TLabel').grid(
            row=row, column=0, padx=5, pady=8, sticky=tk.W)
        
        if entry_type == "entry":
            entry = ttk.Entry(parent, style='Dialog.TCombobox')
            if default:
                entry.insert(0, default)
            entry.grid(row=row, column=1, padx=5, pady=8, sticky=tk.EW)
            return entry
        
        elif entry_type == "combobox":
            combo = ttk.Combobox(parent, values=values, style='Dialog.TCombobox')
            if default:
                combo.set(default)
            else:
                combo.current(0)
            combo.grid(row=row, column=1, padx=5, pady=8, sticky=tk.EW)
            return combo
        
        elif entry_type == "date":
            date_entry = DateEntry(parent, date_pattern='yyyy-mm-dd', 
                                  background='darkblue', foreground='white', 
                                  borderwidth=2, year=datetime.now().year, 
                                  month=datetime.now().month, day=datetime.now().day)
            if default:
                date_entry.set_date(default)
            date_entry.grid(row=row, column=1, padx=5, pady=8, sticky=tk.EW)
            return date_entry
        
        elif entry_type == "text":
            text_widget = tk.Text(parent, height=4, width=30, font=('Segoe UI', 10))
            if default:
                text_widget.insert("1.0", default)
            text_widget.grid(row=row, column=1, padx=5, pady=8, sticky=tk.EW)
            return text_widget
    
    def create_form_buttons(self, parent, row, save_command, cancel_command):
        """Crée les boutons de formulaire standard"""
        btn_frame = ttk.Frame(parent, style='Dialog.TFrame')
        btn_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        cancel_btn = ttk.Button(btn_frame, text="Annuler", command=cancel_command,
                               style='TButton')
        cancel_btn.pack(side=tk.RIGHT, padx=10)
        
        save_btn = ttk.Button(btn_frame, text="Enregistrer", 
                             command=save_command, style='TButton')
        save_btn.pack(side=tk.RIGHT)
    
    # ======================================================================
    # MÉTHODES POUR LES ACHATS
    # ======================================================================
    
    def add_purchase(self):
        """Ouvre une fenêtre pour ajouter un achat"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Ajouter un achat")
        dialog.geometry("500x550")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.colors['light'])
        
        # Style pour la fenêtre de dialogue
        dialog.style = ttk.Style()
        dialog.style.configure('Dialog.TFrame', background=self.colors['light'])
        dialog.style.configure('Dialog.TLabel', background=self.colors['light'], 
                              foreground=self.colors['text'], font=('Segoe UI', 10))
        dialog.style.configure('Dialog.TCombobox', fieldbackground=self.colors['lighter'])
        
        # Formulaire moderne
        form_frame = ttk.Frame(dialog, style='Dialog.TFrame', padding=25)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(form_frame, text="Ajouter un achat", 
                 font=('Segoe UI', 14, 'bold'), style='Dialog.TLabel').grid(row=0, column=0, columnspan=2, pady=10)
        
        # Champs du formulaire
        date_entry = self.create_form_field(form_frame, "Date", 1, entry_type="date")
        item_entry = self.create_form_field(form_frame, "Article", 2)
        category_combo = self.create_form_field(
            form_frame, "Catégorie", 3, 
            values=["Alimentation", "Médicaments", "Équipement", "Semences", "Autre"],
            entry_type="combobox"
        )
        quantity_entry = self.create_form_field(form_frame, "Quantité", 4)
        unit_combo = self.create_form_field(
            form_frame, "Unité", 5, 
            values=["kg", "L", "unité", "sac", "carton"],
            entry_type="combobox"
        )
        amount_entry = self.create_form_field(form_frame, "Montant (€)", 6)
        supplier_entry = self.create_form_field(form_frame, "Fournisseur", 7)
        
        # Boutons
        self.create_form_buttons(
            form_frame, 8,
            save_command=lambda: self.save_purchase(
                date_entry.get(),
                item_entry.get(),
                category_combo.get(),
                quantity_entry.get(),
                unit_combo.get(),
                amount_entry.get(),
                supplier_entry.get(),
                dialog
            ),
            cancel_command=dialog.destroy
        )
    
    def save_purchase(self, date, item, category, quantity, unit, amount, supplier, dialog):
        """Enregistre un nouvel achat dans la base de données"""
        try:
            # Validation des données
            if not all([date, item, category, quantity, unit, amount]):
                raise ValueError("Tous les champs obligatoires doivent être remplis")
            
            quantity = float(quantity)
            amount = float(amount)
            
            if quantity <= 0 or amount <= 0:
                raise ValueError("Les valeurs numériques doivent être positives")
            
            # Insertion dans la base de données
            self.cursor.execute(
                "INSERT INTO purchases (date, item, category, quantity, unit, amount, supplier) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (date, item, category, quantity, unit, amount, supplier)
            )
            self.conn.commit()
            
            messagebox.showinfo("Succès", "Achat enregistré avec succès")
            dialog.destroy()
            self.refresh_data()
        except ValueError as ve:
            messagebox.showerror("Erreur de validation", str(ve))
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue : {str(e)}")
    
    def edit_purchase(self):
        """Modifie l'achat sélectionné"""
        if not hasattr(self, 'current_tree') or not self.current_tree.selection():
            messagebox.showwarning("Sélection", "Veuillez sélectionner un achat")
            return
        
        selected_item = self.current_tree.selection()[0]
        purchase = self.purchases.iloc[int(selected_item[1:])-1]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Modifier un achat")
        dialog.geometry("500x550")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.colors['light'])
        
        # Style pour la fenêtre de dialogue
        dialog.style = ttk.Style()
        dialog.style.configure('Dialog.TFrame', background=self.colors['light'])
        dialog.style.configure('Dialog.TLabel', background=self.colors['light'], 
                              foreground=self.colors['text'], font=('Segoe UI', 10))
        dialog.style.configure('Dialog.TCombobox', fieldbackground=self.colors['lighter'])
        
        # Formulaire moderne
        form_frame = ttk.Frame(dialog, style='Dialog.TFrame', padding=25)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(form_frame, text="Modifier un achat", 
                 font=('Segoe UI', 14, 'bold'), style='Dialog.TLabel').grid(row=0, column=0, columnspan=2, pady=10)
        
        # Champs du formulaire avec valeurs actuelles
        date_entry = self.create_form_field(
            form_frame, "Date", 1, 
            purchase['date'], entry_type="date"
        )
        item_entry = self.create_form_field(
            form_frame, "Article", 2, 
            purchase['item']
        )
        category_combo = self.create_form_field(
            form_frame, "Catégorie", 3, purchase['category'],
            values=["Alimentation", "Médicaments", "Équipement", "Semences", "Autre"],
            entry_type="combobox"
        )
        quantity_entry = self.create_form_field(
            form_frame, "Quantité", 4, 
            str(purchase['quantity'])
        )
        unit_combo = self.create_form_field(
            form_frame, "Unité", 5, purchase['unit'],
            values=["kg", "L", "unité", "sac", "carton"],
            entry_type="combobox"
        )
        amount_entry = self.create_form_field(
            form_frame, "Montant (€)", 6, 
            str(purchase['amount'])
        )
        supplier_entry = self.create_form_field(
            form_frame, "Fournisseur", 7, 
            purchase['supplier']
        )
        
        # Boutons
        self.create_form_buttons(
            form_frame, 8,
            save_command=lambda: self.update_purchase(
                purchase['id'],
                date_entry.get(),
                item_entry.get(),
                category_combo.get(),
                quantity_entry.get(),
                unit_combo.get(),
                amount_entry.get(),
                supplier_entry.get(),
                dialog
            ),
            cancel_command=dialog.destroy
        )
    
    def update_purchase(self, purchase_id, date, item, category, quantity, unit, amount, supplier, dialog):
        """Met à jour un achat dans la base de données"""
        try:
            # Validation des données
            if not all([date, item, category, quantity, unit, amount]):
                raise ValueError("Tous les champs obligatoires doivent être remplis")
            
            quantity = float(quantity)
            amount = float(amount)
            
            if quantity <= 0 or amount <= 0:
                raise ValueError("Les valeurs numériques doivent être positives")
            
            # Mise à jour dans la base de données
            self.cursor.execute(
                "UPDATE purchases SET date=?, item=?, category=?, quantity=?, unit=?, amount=?, supplier=? "
                "WHERE id=?",
                (date, item, category, quantity, unit, amount, supplier, purchase_id)
            )
            self.conn.commit()
            
            messagebox.showinfo("Succès", "Achat mis à jour avec succès")
            dialog.destroy()
            self.refresh_data()
        except ValueError as ve:
            messagebox.showerror("Erreur de validation", str(ve))
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue : {str(e)}")
    
    def delete_purchase(self):
        """Supprime l'achat sélectionné"""
        if not hasattr(self, 'current_tree') or not self.current_tree.selection():
            messagebox.showwarning("Sélection", "Veuillez sélectionner un achat")
            return
        
        selected_item = self.current_tree.selection()[0]
        purchase_id = self.purchases.iloc[int(selected_item[1:])-1]['id']
        
        if messagebox.askyesno("Confirmer", "Êtes-vous sûr de vouloir supprimer cet achat ?"):
            try:
                self.cursor.execute("DELETE FROM purchases WHERE id=?", (purchase_id,))
                self.conn.commit()
                messagebox.showinfo("Succès", "Achat supprimé avec succès")
                self.refresh_data()
            except Exception as e:
                messagebox.showerror("Erreur", f"Une erreur est survenue : {str(e)}")
    
    # ======================================================================
    # MÉTHODES POUR LES CULTURES
    # ======================================================================
    
    def add_crop(self):
        """Ouvre une fenêtre pour ajouter une culture"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Ajouter une culture")
        dialog.geometry("500x550")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.colors['light'])
        
        # Style pour la fenêtre de dialogue
        dialog.style = ttk.Style()
        dialog.style.configure('Dialog.TFrame', background=self.colors['light'])
        dialog.style.configure('Dialog.TLabel', background=self.colors['light'], 
                              foreground=self.colors['text'], font=('Segoe UI', 10))
        dialog.style.configure('Dialog.TCombobox', fieldbackground=self.colors['lighter'])
        
        # Formulaire moderne
        form_frame = ttk.Frame(dialog, style='Dialog.TFrame', padding=25)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(form_frame, text="Ajouter une culture", 
                 font=('Segoe UI', 14, 'bold'), style='Dialog.TLabel').grid(row=0, column=0, columnspan=2, pady=10)
        
        # Champs du formulaire
        name_entry = self.create_form_field(form_frame, "Nom", 1)
        type_combo = self.create_form_field(
            form_frame, "Type", 2, 
            values=["Céréale", "Légume", "Fruit", "Plante médicinale", "Autre"],
            entry_type="combobox"
        )
        planting_date = self.create_form_field(form_frame, "Date de plantation", 3, entry_type="date")
        harvest_date = self.create_form_field(form_frame, "Date de récolte", 4, entry_type="date")
        location_entry = self.create_form_field(form_frame, "Emplacement", 5)
        status_combo = self.create_form_field(
            form_frame, "Statut", 6, 
            values=["Planifié", "En cours", "Récolté", "Abandonné"],
            entry_type="combobox"
        )
        
        # Boutons
        self.create_form_buttons(
            form_frame, 7,
            save_command=lambda: self.save_crop(
                name_entry.get(),
                type_combo.get(),
                planting_date.get(),
                harvest_date.get(),
                location_entry.get(),
                status_combo.get(),
                dialog
            ),
            cancel_command=dialog.destroy
        )
    
    def save_crop(self, name, crop_type, planting_date, harvest_date, location, status, dialog):
        """Enregistre une nouvelle culture dans la base de données"""
        try:
            # Validation des données
            if not all([name, crop_type, planting_date, location, status]):
                raise ValueError("Tous les champs obligatoires doivent être remplis")
            
            # Insertion dans la base de données
            self.cursor.execute(
                "INSERT INTO crops (name, type, planting_date, harvest_date, field_location, status) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (name, crop_type, planting_date, harvest_date, location, status)
            )
            self.conn.commit()
            
            messagebox.showinfo("Succès", "Culture enregistrée avec succès")
            dialog.destroy()
            self.refresh_data()
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue : {str(e)}")
    
    def edit_crop(self):
        """Modifie la culture sélectionnée"""
        if not hasattr(self, 'current_tree') or not self.current_tree.selection():
            messagebox.showwarning("Sélection", "Veuillez sélectionner une culture")
            return
        
        selected_item = self.current_tree.selection()[0]
        crop = self.crops.iloc[int(selected_item[1:])-1]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Modifier une culture")
        dialog.geometry("500x550")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.colors['light'])
        
        # Style pour la fenêtre de dialogue
        dialog.style = ttk.Style()
        dialog.style.configure('Dialog.TFrame', background=self.colors['light'])
        dialog.style.configure('Dialog.TLabel', background=self.colors['light'], 
                              foreground=self.colors['text'], font=('Segoe UI', 10))
        dialog.style.configure('Dialog.TCombobox', fieldbackground=self.colors['lighter'])
        
        # Formulaire moderne
        form_frame = ttk.Frame(dialog, style='Dialog.TFrame', padding=25)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(form_frame, text="Modifier une culture", 
                 font=('Segoe UI', 14, 'bold'), style='Dialog.TLabel').grid(row=0, column=0, columnspan=2, pady=10)
        
        # Champs du formulaire avec valeurs actuelles
        name_entry = self.create_form_field(form_frame, "Nom", 1, crop['name'])
        type_combo = self.create_form_field(
            form_frame, "Type", 2, crop['type'],
            values=["Céréale", "Légume", "Fruit", "Plante médicinale", "Autre"],
            entry_type="combobox"
        )
        planting_date = self.create_form_field(
            form_frame, "Date de plantation", 3, 
            crop['planting_date'], entry_type="date"
        )
        harvest_date = self.create_form_field(
            form_frame, "Date de récolte", 4, 
            crop['harvest_date'], entry_type="date"
        )
        location_entry = self.create_form_field(form_frame, "Emplacement", 5, crop['field_location'])
        status_combo = self.create_form_field(
            form_frame, "Statut", 6, crop['status'],
            values=["Planifié", "En cours", "Récolté", "Abandonné"],
            entry_type="combobox"
        )
        
        # Boutons
        self.create_form_buttons(
            form_frame, 7,
            save_command=lambda: self.update_crop(
                crop['id'],
                name_entry.get(),
                type_combo.get(),
                planting_date.get(),
                harvest_date.get(),
                location_entry.get(),
                status_combo.get(),
                dialog
            ),
            cancel_command=dialog.destroy
        )
    
    def update_crop(self, crop_id, name, crop_type, planting_date, harvest_date, location, status, dialog):
        """Met à jour une culture dans la base de données"""
        try:
            # Validation des données
            if not all([name, crop_type, planting_date, location, status]):
                raise ValueError("Tous les champs obligatoires doivent être remplis")
            
            # Mise à jour dans la base de données
            self.cursor.execute(
                "UPDATE crops SET name=?, type=?, planting_date=?, harvest_date=?, field_location=?, status=? "
                "WHERE id=?",
                (name, crop_type, planting_date, harvest_date, location, status, crop_id)
            )
            self.conn.commit()
            
            messagebox.showinfo("Succès", "Culture mise à jour avec succès")
            dialog.destroy()
            self.refresh_data()
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue : {str(e)}")
    
    def delete_crop(self):
        """Supprime la culture sélectionnée"""
        if not hasattr(self, 'current_tree') or not self.current_tree.selection():
            messagebox.showwarning("Sélection", "Veuillez sélectionner une culture")
            return
        
        selected_item = self.current_tree.selection()[0]
        crop_id = self.crops.iloc[int(selected_item[1:])-1]['id']
        
        if messagebox.askyesno("Confirmer", "Êtes-vous sûr de vouloir supprimer cette culture ?"):
            try:
                self.cursor.execute("DELETE FROM crops WHERE id=?", (crop_id,))
                self.conn.commit()
                messagebox.showinfo("Succès", "Culture supprimée avec succès")
                self.refresh_data()
            except Exception as e:
                messagebox.showerror("Erreur", f"Une erreur est survenue : {str(e)}")
    
    # ======================================================================
    # MÉTHODES POUR LA SANTÉ ANIMALE
    # ======================================================================
    
    def add_animal_health(self):
        """Ouvre une fenêtre pour ajouter un enregistrement de santé animale"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Ajouter un enregistrement de santé animale")
        dialog.geometry("500x600")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.colors['light'])
        
        # Style pour la fenêtre de dialogue
        dialog.style = ttk.Style()
        dialog.style.configure('Dialog.TFrame', background=self.colors['light'])
        dialog.style.configure('Dialog.TLabel', background=self.colors['light'], 
                              foreground=self.colors['text'], font=('Segoe UI', 10))
        dialog.style.configure('Dialog.TCombobox', fieldbackground=self.colors['lighter'])
        
        # Formulaire moderne
        form_frame = ttk.Frame(dialog, style='Dialog.TFrame', padding=25)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(form_frame, text="Santé Animale", 
                 font=('Segoe UI', 14, 'bold'), style='Dialog.TLabel').grid(row=0, column=0, columnspan=2, pady=10)
        
        # Champs du formulaire
        animal_ids = [str(id) for id in self.animals['id']] if not self.animals.empty else ["1"]
        animal_combo = self.create_form_field(
            form_frame, "Animal ID", 1, 
            values=animal_ids,
            entry_type="combobox"
        )
        date_entry = self.create_form_field(form_frame, "Date", 2, entry_type="date")
        condition_entry = self.create_form_field(
            form_frame, "Condition", 3, 
            values=["Sain", "Malade", "Blessé", "En traitement", "Rétabli"],
            entry_type="combobox"
        )
        treatment_entry = self.create_form_field(form_frame, "Traitement", 4)
        vet_entry = self.create_form_field(form_frame, "Vétérinaire", 5)
        notes_entry = self.create_form_field(form_frame, "Notes", 6, entry_type="text")
        
        # Boutons
        self.create_form_buttons(
            form_frame, 7,
            save_command=lambda: self.save_animal_health(
                animal_combo.get(),
                date_entry.get(),
                condition_entry.get(),
                treatment_entry.get(),
                vet_entry.get(),
                notes_entry.get("1.0", tk.END).strip(),
                dialog
            ),
            cancel_command=dialog.destroy
        )
    
    def save_animal_health(self, animal_id, date, condition, treatment, veterinarian, notes, dialog):
        """Enregistre un nouvel enregistrement de santé animale"""
        try:
            # Validation des données
            if not all([animal_id, date, condition]):
                raise ValueError("Les champs obligatoires doivent être remplis")
            
            animal_id = int(animal_id)
            
            # Insertion dans la base de données
            self.cursor.execute(
                "INSERT INTO animal_health (animal_id, date, condition, treatment, veterinarian, notes) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (animal_id, date, condition, treatment, veterinarian, notes)
            )
            self.conn.commit()
            
            messagebox.showinfo("Succès", "Enregistrement de santé ajouté avec succès")
            dialog.destroy()
            self.refresh_data()
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer un ID d'animal valide")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue : {str(e)}")
    
    def edit_animal_health(self):
        """Modifie l'enregistrement de santé sélectionné"""
        if not hasattr(self, 'current_tree') or not self.current_tree.selection():
            messagebox.showwarning("Sélection", "Veuillez sélectionner un enregistrement")
            return
        
        selected_item = self.current_tree.selection()[0]
        health_record = self.animal_health.iloc[int(selected_item[1:])-1]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Modifier un enregistrement de santé")
        dialog.geometry("500x600")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.colors['light'])
        
        # Style pour la fenêtre de dialogue
        dialog.style = ttk.Style()
        dialog.style.configure('Dialog.TFrame', background=self.colors['light'])
        dialog.style.configure('Dialog.TLabel', background=self.colors['light'], 
                              foreground=self.colors['text'], font=('Segoe UI', 10))
        dialog.style.configure('Dialog.TCombobox', fieldbackground=self.colors['lighter'])
        
        # Formulaire moderne
        form_frame = ttk.Frame(dialog, style='Dialog.TFrame', padding=25)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(form_frame, text="Modifier la santé animale", 
                 font=('Segoe UI', 14, 'bold'), style='Dialog.TLabel').grid(row=0, column=0, columnspan=2, pady=10)
        
        # Champs du formulaire avec valeurs actuelles
        animal_ids = [str(id) for id in self.animals['id']] if not self.animals.empty else ["1"]
        animal_combo = self.create_form_field(
            form_frame, "Animal ID", 1, str(health_record['animal_id']),
            values=animal_ids,
            entry_type="combobox"
        )
        date_entry = self.create_form_field(
            form_frame, "Date", 2, 
            health_record['date'], entry_type="date"
        )
        condition_entry = self.create_form_field(
            form_frame, "Condition", 3, health_record['condition'],
            values=["Sain", "Malade", "Blessé", "En traitement", "Rétabli"],
            entry_type="combobox"
        )
        treatment_entry = self.create_form_field(
            form_frame, "Traitement", 4, health_record.get('treatment', '')
        )
        vet_entry = self.create_form_field(
            form_frame, "Vétérinaire", 5, health_record.get('veterinarian', '')
        )
        notes_entry = self.create_form_field(
            form_frame, "Notes", 6, 
            health_record.get('notes', ''), entry_type="text"
        )
        
        # Boutons
        self.create_form_buttons(
            form_frame, 7,
            save_command=lambda: self.update_animal_health(
                health_record['id'],
                animal_combo.get(),
                date_entry.get(),
                condition_entry.get(),
                treatment_entry.get(),
                vet_entry.get(),
                notes_entry.get("1.0", tk.END).strip(),
                dialog
            ),
            cancel_command=dialog.destroy
        )
    
    def update_animal_health(self, record_id, animal_id, date, condition, treatment, veterinarian, notes, dialog):
        """Met à jour un enregistrement de santé animale"""
        try:
            # Validation des données
            if not all([animal_id, date, condition]):
                raise ValueError("Les champs obligatoires doivent être remplis")
            
            animal_id = int(animal_id)
            
            # Mise à jour dans la base de données
            self.cursor.execute(
                "UPDATE animal_health SET animal_id=?, date=?, condition=?, treatment=?, veterinarian=?, notes=? "
                "WHERE id=?",
                (animal_id, date, condition, treatment, veterinarian, notes, record_id)
            )
            self.conn.commit()
            
            messagebox.showinfo("Succès", "Enregistrement de santé mis à jour avec succès")
            dialog.destroy()
            self.refresh_data()
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer un ID d'animal valide")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue : {str(e)}")
    
    def delete_animal_health(self):
        """Supprime l'enregistrement de santé sélectionné"""
        if not hasattr(self, 'current_tree') or not self.current_tree.selection():
            messagebox.showwarning("Sélection", "Veuillez sélectionner un enregistrement")
            return
        
        selected_item = self.current_tree.selection()[0]
        record_id = self.animal_health.iloc[int(selected_item[1:])-1]['id']
        
        if messagebox.askyesno("Confirmer", "Êtes-vous sûr de vouloir supprimer cet enregistrement ?"):
            try:
                self.cursor.execute("DELETE FROM animal_health WHERE id=?", (record_id,))
                self.conn.commit()
                messagebox.showinfo("Succès", "Enregistrement supprimé avec succès")
                self.refresh_data()
            except Exception as e:
                messagebox.showerror("Erreur", f"Une erreur est survenue : {str(e)}")
    
    # ======================================================================
    # MÉTHODES POUR L'INVENTAIRE
    # ======================================================================
    
    def add_inventory(self):
        """Ouvre une fenêtre pour ajouter un élément à l'inventaire"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Ajouter à l'inventaire")
        dialog.geometry("500x500")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.colors['light'])
        
        # Style pour la fenêtre de dialogue
        dialog.style = ttk.Style()
        dialog.style.configure('Dialog.TFrame', background=self.colors['light'])
        dialog.style.configure('Dialog.TLabel', background=self.colors['light'], 
                              foreground=self.colors['text'], font=('Segoe UI', 10))
        dialog.style.configure('Dialog.TCombobox', fieldbackground=self.colors['lighter'])
        
        # Formulaire moderne
        form_frame = ttk.Frame(dialog, style='Dialog.TFrame', padding=25)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(form_frame, text="Ajouter à l'inventaire", 
                 font=('Segoe UI', 14, 'bold'), style='Dialog.TLabel').grid(row=0, column=0, columnspan=2, pady=10)
        
        # Champs du formulaire
        item_entry = self.create_form_field(form_frame, "Article", 1)
        category_combo = self.create_form_field(
            form_frame, "Catégorie", 2, 
            values=["Alimentation", "Médicaments", "Équipement", "Semences", "Outillage", "Autre"],
            entry_type="combobox"
        )
        quantity_entry = self.create_form_field(form_frame, "Quantité", 3)
        unit_combo = self.create_form_field(
            form_frame, "Unité", 4, 
            values=["kg", "L", "unité", "sac", "carton", "paquet"],
            entry_type="combobox"
        )
        
        # Boutons
        self.create_form_buttons(
            form_frame, 5,
            save_command=lambda: self.save_inventory(
                item_entry.get(),
                category_combo.get(),
                quantity_entry.get(),
                unit_combo.get(),
                dialog
            ),
            cancel_command=dialog.destroy
        )
    
    def save_inventory(self, item, category, quantity, unit, dialog):
        """Enregistre un nouvel élément dans l'inventaire"""
        try:
            # Validation des données
            if not all([item, category, quantity, unit]):
                raise ValueError("Tous les champs obligatoires doivent être remplis")
            
            quantity = float(quantity)
            if quantity <= 0:
                raise ValueError("La quantité doit être positive")
            
            # Date actuelle
            now = datetime.now().strftime("%Y-%m-%d")
            
            # Insertion dans la base de données
            self.cursor.execute(
                "INSERT INTO inventory (item, category, quantity, unit, last_update) "
                "VALUES (?, ?, ?, ?, ?)",
                (item, category, quantity, unit, now)
            )
            self.conn.commit()
            
            messagebox.showinfo("Succès", "Élément ajouté à l'inventaire avec succès")
            dialog.destroy()
            self.refresh_data()
        except ValueError as ve:
            messagebox.showerror("Erreur de validation", str(ve))
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue : {str(e)}")
    
    def edit_inventory(self):
        """Modifie l'élément d'inventaire sélectionné"""
        if not hasattr(self, 'current_tree') or not self.current_tree.selection():
            messagebox.showwarning("Sélection", "Veuillez sélectionner un élément")
            return
        
        selected_item = self.current_tree.selection()[0]
        inventory_item = self.inventory.iloc[int(selected_item[1:])-1]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Modifier l'inventaire")
        dialog.geometry("500x500")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.colors['light'])
        
        # Style pour la fenêtre de dialogue
        dialog.style = ttk.Style()
        dialog.style.configure('Dialog.TFrame', background=self.colors['light'])
        dialog.style.configure('Dialog.TLabel', background=self.colors['light'], 
                              foreground=self.colors['text'], font=('Segoe UI', 10))
        dialog.style.configure('Dialog.TCombobox', fieldbackground=self.colors['lighter'])
        
        # Formulaire moderne
        form_frame = ttk.Frame(dialog, style='Dialog.TFrame', padding=25)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(form_frame, text="Modifier l'inventaire", 
                 font=('Segoe UI', 14, 'bold'), style='Dialog.TLabel').grid(row=0, column=0, columnspan=2, pady=10)
        
        # Champs du formulaire avec valeurs actuelles
        item_entry = self.create_form_field(
            form_frame, "Article", 1, 
            inventory_item['item']
        )
        category_combo = self.create_form_field(
            form_frame, "Catégorie", 2, inventory_item['category'],
            values=["Alimentation", "Médicaments", "Équipement", "Semences", "Outillage", "Autre"],
            entry_type="combobox"
        )
        quantity_entry = self.create_form_field(
            form_frame, "Quantité", 3, 
            str(inventory_item['quantity'])
        )
        unit_combo = self.create_form_field(
            form_frame, "Unité", 4, inventory_item['unit'],
            values=["kg", "L", "unité", "sac", "carton", "paquet"],
            entry_type="combobox"
        )
        
        # Boutons
        self.create_form_buttons(
            form_frame, 5,
            save_command=lambda: self.update_inventory(
                inventory_item['id'],
                item_entry.get(),
                category_combo.get(),
                quantity_entry.get(),
                unit_combo.get(),
                dialog
            ),
            cancel_command=dialog.destroy
        )
    
    def update_inventory(self, item_id, item, category, quantity, unit, dialog):
        """Met à jour un élément dans l'inventaire"""
        try:
            # Validation des données
            if not all([item, category, quantity, unit]):
                raise ValueError("Tous les champs obligatoires doivent être remplis")
            
            quantity = float(quantity)
            if quantity <= 0:
                raise ValueError("La quantité doit être positive")
            
            # Date actuelle
            now = datetime.now().strftime("%Y-%m-%d")
            
            # Mise à jour dans la base de données
            self.cursor.execute(
                "UPDATE inventory SET item=?, category=?, quantity=?, unit=?, last_update=? "
                "WHERE id=?",
                (item, category, quantity, unit, now, item_id)
            )
            self.conn.commit()
            
            messagebox.showinfo("Succès", "Élément d'inventaire mis à jour avec succès")
            dialog.destroy()
            self.refresh_data()
        except ValueError as ve:
            messagebox.showerror("Erreur de validation", str(ve))
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue : {str(e)}")
    
    def delete_inventory(self):
        """Supprime l'élément d'inventaire sélectionné"""
        if not hasattr(self, 'current_tree') or not self.current_tree.selection():
            messagebox.showwarning("Sélection", "Veuillez sélectionner un élément")
            return
        
        selected_item = self.current_tree.selection()[0]
        item_id = self.inventory.iloc[int(selected_item[1:])-1]['id']
        
        if messagebox.askyesno("Confirmer", "Êtes-vous sûr de vouloir supprimer cet élément ?"):
            try:
                self.cursor.execute("DELETE FROM inventory WHERE id=?", (item_id,))
                self.conn.commit()
                messagebox.showinfo("Succès", "Élément supprimé avec succès")
                self.refresh_data()
            except Exception as e:
                messagebox.showerror("Erreur", f"Une erreur est survenue : {str(e)}")
    
    # ======================================================================
    # AUTRES MÉTHODES
    # ======================================================================
    
    def export_data(self):
        """Exporte les données au format Excel"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Fichiers Excel", "*.xlsx"), ("Tous les fichiers", "*.*")],
            title="Exporter les données"
        )
        
        if not file_path:
            return
        
        try:
            with pd.ExcelWriter(file_path) as writer:
                self.purchases.to_excel(writer, sheet_name='Achats', index=False)
                self.sales.to_excel(writer, sheet_name='Ventes', index=False)
                self.inventory.to_excel(writer, sheet_name='Inventaire', index=False)
                self.crops.to_excel(writer, sheet_name='Cultures', index=False)
                self.animals.to_excel(writer, sheet_name='Animaux', index=False)
                self.animal_health.to_excel(writer, sheet_name='Santé Animale', index=False)
                self.feeding.to_excel(writer, sheet_name='Alimentation', index=False)
                self.fields.to_excel(writer, sheet_name='Champs', index=False)
            
            messagebox.showinfo("Export réussi", "Données exportées avec succès")
        except Exception as e:
            messagebox.showerror("Erreur", f"Échec de l'export : {str(e)}")
    
    def show_settings(self):
        """Affiche les paramètres de l'application"""
        messagebox.showinfo("Paramètres", "Cette fonctionnalité est en cours de développement")
    
    def show_about(self):
        """Affiche la boîte de dialogue À propos"""
        about_text = (
            "AgroManager Pro\n"
            "Version 3.0\n\n"
            "Application complète de gestion agricole\n"
            "Développée avec Python, Tkinter et SQLite\n\n"
            "Fonctionnalités incluses:\n"
            "- Gestion des animaux et santé animale\n"
            "- Suivi des cultures et des champs\n"
            "- Gestion des achats et des ventes\n"
            "- Inventaire et statistiques\n\n"
            "© 2023 AgroManager Solutions. Tous droits réservés."
        )
        messagebox.showinfo("À propos", about_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernFarmManagementApp(root)
    root.mainloop()