import mysql.connector

from mysql.connector import Error
import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
from datetime import datetime
import hashlib

# Configuration de la base de données
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'iks1'
}

# Palette de couleurs
SIDEBAR_BG = "#2c3e50"
SIDEBAR_FG = "#ffffff"
SIDEBAR_ACTIVE = "#1a252f"
SIDEBAR_HOVER = "#34495e"
CONTENT_BG = "#f5f5f5"
HEADER_BG = "#ffffff"
CARD_BG = "#ffffff"
STAT_BLUE = "#1e88e5"
STAT_GREEN = "#4caf50"
STAT_RED = "#e53935"
TEXT_DARK = "#333333"
TEXT_LIGHT = "#ffffff"
BORDER_COLOR = "#dddddd"
TABLE_HEADER_BG = "#f0f0f0"
TABLE_ROW_EVEN = "#ffffff"
TABLE_ROW_ODD = "#f9f9f9"
TABLE_BORDER = "#e0e0e0"
BTN_SUCCESS = "#4caf50"
BTN_DANGER = "#f44336"
BTN_WARNING = "#ff9800"
BTN_INFO = "#2196f3"

# Fonction de connexion à la base de données
def create_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except Error as e:
        messagebox.showerror("Erreur", f"Erreur de connexion à la base de données: {e}")
        return None

# Fonction de hachage des mots de passe
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

class SampleManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Système de Gestion des Échantillons")
        self.root.geometry("1100x700")
        self.root.minsize(900, 600)
        
        # Configurer la police par défaut
        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(family="Arial", size=10)
        
        # Variables d'état
        self.current_user = None
        self.user_role = None
        self.user_fullname = ""
        self.active_menu = None
        
        # Configurer les styles ttk
        self.configure_styles()
        
        # Afficher l'écran de connexion
        self.show_login_frame()
    
    def configure_styles(self):
        """Configure les styles ttk pour l'application."""
        style = ttk.Style()
        style.theme_use('clam')  # Utiliser un thème de base propre
        
        # Style général
        style.configure(".", font=("Arial", 10))
        
        # Style pour les boutons
        style.configure("TButton", padding=6, relief="flat", background="#1976D2", foreground="white")
        style.map("TButton",
                  background=[('active', '#1565C0'), ('disabled', '#BDBDBD')],
                  foreground=[('disabled', '#757575')])
        
        # Boutons colorés
        style.configure("Success.TButton", background=BTN_SUCCESS)
        style.map("Success.TButton", background=[('active', '#388E3C')])
        
        style.configure("Danger.TButton", background=BTN_DANGER)
        style.map("Danger.TButton", background=[('active', '#D32F2F')])
        
        style.configure("Warning.TButton", background=BTN_WARNING)
        style.map("Warning.TButton", background=[('active', '#F57C00')])
        
        style.configure("Info.TButton", background=BTN_INFO)
        style.map("Info.TButton", background=[('active', '#1976D2')])
        
        # Style pour les entrées
        style.configure("TEntry", padding=6, relief="flat")
        
        # Style pour les labels
        style.configure("TLabel", background=CONTENT_BG)
        style.configure("Header.TLabel", font=("Arial", 14, "bold"))
        style.configure("Sidebar.TLabel", background=SIDEBAR_BG, foreground=SIDEBAR_FG, font=("Arial", 10))
        style.configure("SidebarHeader.TLabel", background=SIDEBAR_BG, foreground=SIDEBAR_FG, font=("Arial", 14, "bold"))
        style.configure("SidebarUser.TLabel", background=SIDEBAR_BG, foreground=SIDEBAR_FG, font=("Arial", 9))
        
        # Style pour les frames
        style.configure("TFrame", background=CONTENT_BG)
        style.configure("Sidebar.TFrame", background=SIDEBAR_BG)
        style.configure("Content.TFrame", background=CONTENT_BG)
        style.configure("Card.TFrame", background=CARD_BG, relief="solid", borderwidth=1)
        style.configure("Header.TFrame", background=HEADER_BG, relief="solid", borderwidth=0)
        
        # Style pour les séparateurs
        style.configure("Sidebar.TSeparator", background=SIDEBAR_FG)
        
        # Style pour le Treeview (tableau)
        style.configure("Treeview", 
                        background=TABLE_ROW_EVEN,
                        fieldbackground=TABLE_ROW_EVEN,
                        foreground=TEXT_DARK,
                        font=("Arial", 9))
        style.configure("Treeview.Heading", 
                        background=TABLE_HEADER_BG,
                        foreground=TEXT_DARK,
                        font=("Arial", 10, "bold"),
                        relief="flat")
        style.map("Treeview", background=[('selected', '#e1f5fe')])
        style.map("Treeview.Heading", background=[('active', '#e0e0e0')])
    
    def show_login_frame(self):
        """Affiche l'écran de connexion."""
        # Nettoyer la fenêtre
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Créer un frame principal pour centrer le contenu
        main_frame = ttk.Frame(self.root)
        main_frame.pack(expand=True, fill="both")
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Frame de connexion
        login_frame = ttk.Frame(main_frame, style="Card.TFrame", padding=20)
        login_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        # Titre
        ttk.Label(login_frame, text="Système de Gestion des Échantillons", 
                 font=("Arial", 16, "bold"), background=CARD_BG).pack(pady=(0, 20))
        
        # Formulaire de connexion
        form_frame = ttk.Frame(login_frame, style="Card.TFrame")
        form_frame.pack(padx=30, pady=10, fill="x")
        
        ttk.Label(form_frame, text="Matricule:", background=CARD_BG).grid(row=0, column=0, sticky="w", pady=5)
        self.matricule_entry = ttk.Entry(form_frame, width=30)
        self.matricule_entry.grid(row=0, column=1, sticky="ew", pady=5, padx=5)
        
        ttk.Label(form_frame, text="Mot de passe:", background=CARD_BG).grid(row=1, column=0, sticky="w", pady=5)
        self.password_entry = ttk.Entry(form_frame, show="*", width=30)
        self.password_entry.grid(row=1, column=1, sticky="ew", pady=5, padx=5)
        
        # Bouton de connexion
        btn_frame = ttk.Frame(login_frame, style="Card.TFrame")
        btn_frame.pack(pady=20)
        
        login_btn = ttk.Button(btn_frame, text="Connexion", command=self.login, width=20)
        login_btn.pack()
        
        # Focus sur le premier champ
        self.matricule_entry.focus_set()
        
        # Permettre la connexion avec la touche Entrée
        self.root.bind('<Return>', lambda event: login_btn.invoke())
    
    def login(self):
        """Gère la connexion de l'utilisateur."""
        matricule = self.matricule_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not matricule or not password:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs")
            return
        
        conn = create_db_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                # Modification ici : on utilise le mot de passe en clair comme dans le code original
                cursor.execute("""
                    SELECT * FROM UTILISATEUR 
                    WHERE MATRICULE = %s AND password = %s
                """, (matricule, password))
                
                user = cursor.fetchone()
                if user:
                    self.current_user = user['MATRICULE']
                    self.user_role = user['ROLE']
                    self.user_fullname = f"{user['NOM']} {user['PRENOM']}"
                    self.log_action(self.current_user, 'connexion', 
                                  f"Connexion de {user['NOM']} {user['PRENOM']}")
                    self.init_dashboard()
                else:
                    messagebox.showerror("Erreur", "Matricule ou mot de passe incorrect")
                
                cursor.close()
                conn.close()
            except Error as e:
                messagebox.showerror("Erreur", f"Erreur lors de la connexion: {e}")
    
    def log_action(self, matricule, action_type, description):
        """Enregistre une action dans l'historique."""
        conn = create_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO HISTORIQUE (MATRICULE, TYPE_ACTION, DESCRIPTION) VALUES (%s, %s, %s)",
                               (matricule, action_type, description))
                conn.commit()
                cursor.close()
                conn.close()
            except Error as e:
                print(f"Erreur lors de l'enregistrement de l'historique: {e}")
    
    def init_dashboard(self):
        """Initialise la structure du dashboard."""
        # Nettoyer la fenêtre
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Créer la structure principale
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(expand=True, fill="both")
        
        # Créer la sidebar
        self.sidebar_frame = ttk.Frame(self.main_frame, style="Sidebar.TFrame", width=200)
        self.sidebar_frame.pack(side="left", fill="y")
        self.sidebar_frame.pack_propagate(False)  # Empêcher le redimensionnement
        
        # Créer la zone de contenu
        self.content_frame = ttk.Frame(self.main_frame, style="Content.TFrame")
        self.content_frame.pack(side="right", fill="both", expand=True)
        
        # Remplir la sidebar
        self.create_sidebar()
        
        # Afficher le tableau de bord par défaut
        self.show_dashboard()
    
    def create_sidebar(self):
        """Crée la barre latérale avec le menu de navigation."""
        # Titre de l'application
        title_frame = ttk.Frame(self.sidebar_frame, style="Sidebar.TFrame")
        title_frame.pack(fill="x", pady=(20, 10))
        ttk.Label(title_frame, text="Gestion", style="SidebarHeader.TLabel").pack(anchor="center")
        ttk.Label(title_frame, text="Échantillons", style="SidebarHeader.TLabel").pack(anchor="center")
        
        # Informations utilisateur
        user_frame = ttk.Frame(self.sidebar_frame, style="Sidebar.TFrame")
        user_frame.pack(fill="x", pady=10)
        ttk.Label(user_frame, text=f"Utilisateur: {self.current_user}", style="SidebarUser.TLabel").pack(anchor="center")
        ttk.Label(user_frame, text=f"Rôle: {self.user_role}", style="SidebarUser.TLabel").pack(anchor="center")
        
        # Séparateur
        ttk.Separator(self.sidebar_frame, orient="horizontal", style="Sidebar.TSeparator").pack(fill="x", pady=10)
        
        # Menu de navigation
        menu_items = [
            ("Tableau de bord", self.show_dashboard),
            ("Stock", self.show_stock),
            ("Historique", self.show_history)
        ]
        
        # Ajouter des options de menu selon le rôle
        if self.user_role == 'admin':
            menu_items.extend([
                ("Gérer demandes", self.show_requests_management),
                ("Suivi échantillons", self.show_sample_tracking),
                ("Historique complet", self.show_full_history)
            ])
        elif self.user_role == 'user':
            menu_items.extend([
                ("Demander échantillon", self.show_sample_request),
                ("Retour échantillon", self.show_return)
            ])
        elif self.user_role == 'livreur':
            menu_items.extend([
                ("Livraisons", self.show_deliveries)
            ])
        
        # Créer les boutons de menu
        self.menu_buttons = {}
        for text, command in menu_items:
            btn = tk.Button(self.sidebar_frame, 
                           text=text, 
                           command=command,
                           bg=SIDEBAR_BG, 
                           fg=SIDEBAR_FG,
                           activebackground=SIDEBAR_ACTIVE,
                           activeforeground=SIDEBAR_FG,
                           bd=0,
                           padx=10,
                           pady=8,
                           anchor="w",
                           width=25,
                           font=("Arial", 10),
                           cursor="hand2")
            btn.pack(fill="x", pady=1)
            self.menu_buttons[text] = btn
        
        # Séparateur avant déconnexion
        ttk.Separator(self.sidebar_frame, orient="horizontal", style="Sidebar.TSeparator").pack(fill="x", pady=10, side="bottom")
        
        # Bouton de déconnexion
        logout_btn = tk.Button(self.sidebar_frame, 
                              text="Déconnexion", 
                              command=self.logout,
                              bg=SIDEBAR_BG, 
                              fg=SIDEBAR_FG,
                              activebackground=SIDEBAR_ACTIVE,
                              activeforeground=SIDEBAR_FG,
                              bd=0,
                              padx=10,
                              pady=8,
                              anchor="w",
                              width=25,
                              font=("Arial", 10),
                              cursor="hand2")
        logout_btn.pack(fill="x", pady=1, side="bottom")
    
    def set_active_menu(self, menu_name):
        """Met à jour l'apparence du menu actif."""
        for name, btn in self.menu_buttons.items():
            if name == menu_name:
                btn.config(bg=SIDEBAR_ACTIVE)
                self.active_menu = name
            else:
                btn.config(bg=SIDEBAR_BG)
    
    def clear_content(self):
        """Nettoie la zone de contenu."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def create_header(self, title):
        """Crée l'en-tête de la zone de contenu."""
        header_frame = ttk.Frame(self.content_frame, style="Header.TFrame")
        header_frame.pack(fill="x")
        
        ttk.Label(header_frame, text=title, background=HEADER_BG, font=("Arial", 12)).pack(anchor="w", padx=20, pady=10)
        
        return header_frame
    
    def show_dashboard(self):
        """Affiche le tableau de bord."""
        self.set_active_menu("Tableau de bord")
        self.clear_content()
        
        # Créer l'en-tête
        self.create_header("Tableau de bord")
        
        # Message de bienvenue
        welcome_frame = ttk.Frame(self.content_frame, style="Content.TFrame")
        welcome_frame.pack(fill="x", padx=20, pady=10)
        ttk.Label(welcome_frame, text=f"Bienvenue {self.current_user}", 
                 font=("Arial", 16, "bold"), background=CONTENT_BG).pack(anchor="center")
        
        # Cartes statistiques
        stats_frame = ttk.Frame(self.content_frame, style="Content.TFrame")
        stats_frame.pack(fill="x", padx=20, pady=10)
        
        # Récupérer les statistiques depuis la base de données
        stats = self.get_dashboard_stats()
        
        # Créer les cartes
        self.create_stat_card(stats_frame, "Échantillons", stats['samples'], STAT_BLUE)
        self.create_stat_card(stats_frame, "Demandes", stats['requests'], STAT_GREEN)
        self.create_stat_card(stats_frame, "Livraisons", stats['deliveries'], STAT_RED)
        
        # Section activités récentes
        activities_frame = ttk.Frame(self.content_frame, style="Content.TFrame")
        activities_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ttk.Label(activities_frame, text="Activités récentes", 
                 font=("Arial", 14, "bold"), background=CONTENT_BG).pack(anchor="w", pady=(0, 10))
        
        # Tableau des activités
        self.create_activities_table(activities_frame)
    
    def get_dashboard_stats(self):
        """Récupère les statistiques pour le tableau de bord."""
        stats = {
            'samples': 0,
            'requests': 0,
            'deliveries': 0
        }
        
        conn = create_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Nombre d'échantillons
                cursor.execute("SELECT COUNT(*) FROM ECHANTILLON")
                stats['samples'] = cursor.fetchone()[0]
                
                # Nombre de demandes
                cursor.execute("SELECT COUNT(*) FROM DEMANDE")
                stats['requests'] = cursor.fetchone()[0]
                
                # Nombre de livraisons
                cursor.execute("SELECT COUNT(*) FROM livraison")
                stats['deliveries'] = cursor.fetchone()[0]
                
                cursor.close()
                conn.close()
            except Error as e:
                print(f"Erreur lors de la récupération des statistiques: {e}")
        
        return stats
    
    def create_stat_card(self, parent, title, value, color):
        """Crée une carte statistique."""
        card = ttk.Frame(parent, style="Card.TFrame")
        card.pack(side="left", fill="both", expand=True, padx=10)
        
        ttk.Label(card, text=title, 
                 font=("Arial", 12), background=CARD_BG).pack(anchor="center", pady=(15, 5))
        
        ttk.Label(card, text=str(value), 
                 font=("Arial", 24, "bold"), foreground=color, background=CARD_BG).pack(anchor="center", pady=(5, 15))
    
    def create_activities_table(self, parent):
        """Crée le tableau des activités récentes."""
        # Cadre pour le tableau
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill="both", expand=True)
        
        # Créer le tableau
        columns = ('date', 'type', 'description')
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', style="Treeview")
        
        # Définir les en-têtes
        tree.heading('date', text='Date')
        tree.heading('type', text='Type')
        tree.heading('description', text='Description')
        
        # Définir les largeurs de colonnes
        tree.column('date', width=150)
        tree.column('type', width=100)
        tree.column('description', width=500)
        
        # Ajouter une scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)
        
        # Remplir le tableau avec les données
        self.populate_activities_table(tree)
    
    def populate_activities_table(self, tree):
        """Remplit le tableau des activités récentes avec les données de la base."""
        # Vider le tableau
        for i in tree.get_children():
            tree.delete(i)
        
        conn = create_db_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                
                # Récupérer les activités récentes
                query = """
                SELECT DATE_ACTION, TYPE_ACTION, DESCRIPTION 
                FROM HISTORIQUE 
                ORDER BY DATE_ACTION DESC 
                LIMIT 10
                """
                cursor.execute(query)
                activities = cursor.fetchall()
                
                # Ajouter les activités au tableau
                for i, activity in enumerate(activities):
                    date_str = activity['DATE_ACTION'].strftime('%Y-%m-%d %H:%M:%S')
                    tree.insert('', 'end', values=(date_str, activity['TYPE_ACTION'], activity['DESCRIPTION']))
                    
                    # Appliquer des couleurs alternées aux lignes
                    if i % 2 == 0:
                        tree.item(tree.get_children()[-1], tags=('evenrow',))
                    else:
                        tree.item(tree.get_children()[-1], tags=('oddrow',))
                
                # Configurer les tags pour les couleurs alternées
                tree.tag_configure('evenrow', background=TABLE_ROW_EVEN)
                tree.tag_configure('oddrow', background=TABLE_ROW_ODD)
                
                cursor.close()
                conn.close()
            except Error as e:
                print(f"Erreur lors de la récupération des activités: {e}")
    
    def show_stock(self):
        """Affiche la page de stock."""
        self.set_active_menu("Stock")
        self.clear_content()
        
        # Créer l'en-tête
        self.create_header("Stock d'échantillons")
        
        # Cadre principal
        main_frame = ttk.Frame(self.content_frame, style="Content.TFrame")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Titre de la section
        ttk.Label(main_frame, text="Liste des échantillons", 
                 font=("Arial", 14, "bold"), background=CONTENT_BG).pack(anchor="w", pady=(0, 10))
        
        # Cadre pour le tableau
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill="both", expand=True)
        
        # Créer le tableau
        columns = ('reference', 'article', 'taille', 'quantite', 'statut')
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', style="Treeview")
        
        # Définir les en-têtes
        tree.heading('reference', text='Référence')
        tree.heading('article', text='Article')
        tree.heading('taille', text='Taille')
        tree.heading('quantite', text='Quantité')
        tree.heading('statut', text='Statut')
        
        # Définir les largeurs de colonnes
        tree.column('reference', width=120)
        tree.column('article', width=250)
        tree.column('taille', width=80)
        tree.column('quantite', width=80)
        tree.column('statut', width=120)
        
        # Ajouter une scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)
        
        # Remplir le tableau avec les données
        self.populate_stock_table(tree)
    
    def populate_stock_table(self, tree):
        """Remplit le tableau de stock avec les données de la base."""
        # Vider le tableau
        for i in tree.get_children():
            tree.delete(i)
        
        conn = create_db_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                
                # Récupérer les échantillons
                cursor.execute("SELECT * FROM ECHANTILLON ORDER BY ARTICLE")
                samples = cursor.fetchall()
                
                # Ajouter les échantillons au tableau
                for i, sample in enumerate(samples):
                    tree.insert('', 'end', values=(
                        sample['REFERENCE'],
                        sample['ARTICLE'],
                        sample['TAILLE'],
                        sample['QUANTITE'],
                        sample['STATUT']
                    ))
                    
                    # Appliquer des couleurs alternées aux lignes
                    if i % 2 == 0:
                        tree.item(tree.get_children()[-1], tags=('evenrow',))
                    else:
                        tree.item(tree.get_children()[-1], tags=('oddrow',))
                
                # Configurer les tags pour les couleurs alternées
                tree.tag_configure('evenrow', background=TABLE_ROW_EVEN)
                tree.tag_configure('oddrow', background=TABLE_ROW_ODD)
                
                cursor.close()
                conn.close()
            except Error as e:
                messagebox.showerror("Erreur", f"Erreur lors de la récupération des échantillons: {e}")
    
    def show_history(self):
        """Affiche l'historique de l'utilisateur."""
        self.set_active_menu("Historique")
        self.clear_content()
        
        # Créer l'en-tête
        self.create_header("Historique")
        
        # Cadre principal
        main_frame = ttk.Frame(self.content_frame, style="Content.TFrame")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Titre de la section
        ttk.Label(main_frame, text="Votre historique d'actions", 
                 font=("Arial", 14, "bold"), background=CONTENT_BG).pack(anchor="w", pady=(0, 10))
        
        # Cadre pour le tableau
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill="both", expand=True)
        
        # Créer le tableau
        columns = ('date', 'type', 'description')
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', style="Treeview")
        
        # Définir les en-têtes
        tree.heading('date', text='Date')
        tree.heading('type', text='Type')
        tree.heading('description', text='Description')
        
        # Définir les largeurs de colonnes
        tree.column('date', width=150)
        tree.column('type', width=100)
        tree.column('description', width=500)
        
        # Ajouter une scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)
        
        # Remplir le tableau avec les données
        self.populate_history_table(tree)
    
    def populate_history_table(self, tree):
        """Remplit le tableau d'historique avec les données de la base."""
        # Vider le tableau
        for i in tree.get_children():
            tree.delete(i)
        
        conn = create_db_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                
                # Récupérer l'historique de l'utilisateur
                cursor.execute("""
                    SELECT DATE_ACTION, TYPE_ACTION, DESCRIPTION 
                    FROM HISTORIQUE 
                    WHERE MATRICULE = %s 
                    ORDER BY DATE_ACTION DESC
                """, (self.current_user,))
                
                history = cursor.fetchall()
                
                # Ajouter les entrées au tableau
                for i, entry in enumerate(history):
                    date_str = entry['DATE_ACTION'].strftime('%Y-%m-%d %H:%M:%S')
                    tree.insert('', 'end', values=(date_str, entry['TYPE_ACTION'], entry['DESCRIPTION']))
                    
                    # Appliquer des couleurs alternées aux lignes
                    if i % 2 == 0:
                        tree.item(tree.get_children()[-1], tags=('evenrow',))
                    else:
                        tree.item(tree.get_children()[-1], tags=('oddrow',))
                
                # Configurer les tags pour les couleurs alternées
                tree.tag_configure('evenrow', background=TABLE_ROW_EVEN)
                tree.tag_configure('oddrow', background=TABLE_ROW_ODD)
                
                cursor.close()
                conn.close()
            except Error as e:
                messagebox.showerror("Erreur", f"Erreur lors de la récupération de l'historique: {e}")
    
    def show_sample_request(self):
        """Affiche la page de demande d'échantillon."""
        self.set_active_menu("Demander échantillon")
        self.clear_content()
        
        # Créer l'en-tête
        self.create_header("Demander un échantillon")
        
        # Cadre principal
        main_frame = ttk.Frame(self.content_frame, style="Content.TFrame")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Titre de la section
        ttk.Label(main_frame, text="Rechercher un échantillon", 
                 font=("Arial", 14, "bold"), background=CONTENT_BG).pack(anchor="w", pady=(0, 10))
        
        # Barre de recherche
        search_frame = ttk.Frame(main_frame, style="Content.TFrame")
        search_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(search_frame, text="Rechercher par référence ou article:", 
                 background=CONTENT_BG).pack(side="left", padx=(0, 10))
        
        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind('<KeyRelease>', self.search_samples)
        
        # Panneau divisé: liste à gauche, détails à droite
        split_frame = ttk.Frame(main_frame, style="Content.TFrame")
        split_frame.pack(fill="both", expand=True)
        
        # Panneau gauche: liste des échantillons
        left_frame = ttk.Frame(split_frame, style="Card.TFrame", padding=10)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        ttk.Label(left_frame, text="Échantillons disponibles", 
                 font=("Arial", 12, "bold"), background=CARD_BG).pack(anchor="w", pady=(0, 10))
        
        # Liste des échantillons
        list_frame = ttk.Frame(left_frame, style="Card.TFrame")
        list_frame.pack(fill="both", expand=True)
        
        self.samples_listbox = tk.Listbox(list_frame, font=("Arial", 10), 
                                         bg=CARD_BG, fg=TEXT_DARK,
                                         selectbackground=STAT_BLUE, selectforeground=TEXT_LIGHT)
        self.samples_listbox.pack(side="left", fill="both", expand=True)
        
        list_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.samples_listbox.yview)
        self.samples_listbox.configure(yscrollcommand=list_scrollbar.set)
        list_scrollbar.pack(side="right", fill="y")
        
        # Panneau droit: détails de l'échantillon
        right_frame = ttk.Frame(split_frame, style="Card.TFrame", padding=10)
        right_frame.pack(side="right", fill="both", expand=True)
        
        ttk.Label(right_frame, text="Détails de l'échantillon", 
                 font=("Arial", 12, "bold"), background=CARD_BG).pack(anchor="w", pady=(0, 10))
        
        # Cadre pour les détails
        self.details_frame = ttk.Frame(right_frame, style="Card.TFrame")
        self.details_frame.pack(fill="both", expand=True)
        
        # Bouton de demande (initialement désactivé)
        self.request_btn = ttk.Button(right_frame, text="Faire une demande", 
                                     command=self.make_request, state="disabled", style="Success.TButton")
        self.request_btn.pack(pady=10, padx=5, anchor="e")
        
        # Remplir la liste des échantillons
        self.populate_samples_list()
        
        # Lier la sélection dans la liste
        self.samples_listbox.bind('<<ListboxSelect>>', self.show_sample_details)
    
    def populate_samples_list(self, search_term=None):
        """Remplit la liste des échantillons disponibles."""
        # Vider la liste
        self.samples_listbox.delete(0, tk.END)
        
        conn = create_db_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                
                # Requête de base
                query = "SELECT * FROM ECHANTILLON WHERE QUANTITE > 0"
                params = []
                
                # Ajouter le filtre de recherche si nécessaire
                if search_term:
                    query += " AND (REFERENCE LIKE %s OR ARTICLE LIKE %s)"
                    params.extend([f"%{search_term}%", f"%{search_term}%"])
                
                query += " ORDER BY ARTICLE"
                
                cursor.execute(query, params)
                samples = cursor.fetchall()
                
                # Ajouter les échantillons à la liste
                for sample in samples:
                    self.samples_listbox.insert(tk.END, f"{sample['REFERENCE']} - {sample['ARTICLE']} ({sample['TAILLE']})")
                
                cursor.close()
                conn.close()
            except Error as e:
                messagebox.showerror("Erreur", f"Erreur lors de la récupération des échantillons: {e}")
    
    def search_samples(self, event):
        """Recherche des échantillons en fonction du texte saisi."""
        search_term = self.search_entry.get().strip()
        self.populate_samples_list(search_term)
    
    def show_sample_details(self, event):
        """Affiche les détails de l'échantillon sélectionné."""
        # Vider le cadre des détails
        for widget in self.details_frame.winfo_children():
            widget.destroy()
        
        # Désactiver le bouton de demande
        self.request_btn.config(state="disabled")
        
        # Récupérer la sélection
        selection = self.samples_listbox.curselection()
        if not selection:
            return
        
        # Récupérer la référence de l'échantillon
        selected_text = self.samples_listbox.get(selection[0])
        ref = selected_text.split(' - ')[0]
        
        conn = create_db_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                
                # Récupérer les détails de l'échantillon
                cursor.execute("SELECT * FROM ECHANTILLON WHERE REFERENCE = %s", (ref,))
                sample = cursor.fetchone()
                
                if sample:
                    # Afficher les détails
                    details_grid = ttk.Frame(self.details_frame, style="Card.TFrame")
                    details_grid.pack(fill="both", expand=True, padx=5, pady=5)
                    
                    # Configurer les colonnes
                    details_grid.columnconfigure(0, weight=1)
                    details_grid.columnconfigure(1, weight=2)
                    
                    # Ligne 1: Référence
                    ttk.Label(details_grid, text="Référence:", 
                             font=("Arial", 10, "bold"), background=CARD_BG).grid(row=0, column=0, sticky="w", pady=5)
                    ttk.Label(details_grid, text=sample['REFERENCE'], 
                             background=CARD_BG).grid(row=0, column=1, sticky="w", pady=5)
                    
                    # Ligne 2: Article
                    ttk.Label(details_grid, text="Article:", 
                             font=("Arial", 10, "bold"), background=CARD_BG).grid(row=1, column=0, sticky="w", pady=5)
                    ttk.Label(details_grid, text=sample['ARTICLE'], 
                             background=CARD_BG).grid(row=1, column=1, sticky="w", pady=5)
                    
                    # Ligne 3: Taille
                    ttk.Label(details_grid, text="Taille:", 
                             font=("Arial", 10, "bold"), background=CARD_BG).grid(row=2, column=0, sticky="w", pady=5)
                    ttk.Label(details_grid, text=sample['TAILLE'], 
                             background=CARD_BG).grid(row=2, column=1, sticky="w", pady=5)
                    
                    # Ligne 4: Quantité
                    ttk.Label(details_grid, text="Quantité disponible:", 
                             font=("Arial", 10, "bold"), background=CARD_BG).grid(row=3, column=0, sticky="w", pady=5)
                    ttk.Label(details_grid, text=str(sample['QUANTITE']), 
                             background=CARD_BG).grid(row=3, column=1, sticky="w", pady=5)
                    
                    # Ligne 5: Statut
                    ttk.Label(details_grid, text="Statut:", 
                             font=("Arial", 10, "bold"), background=CARD_BG).grid(row=4, column=0, sticky="w", pady=5)
                    ttk.Label(details_grid, text=sample['STATUT'], 
                             background=CARD_BG).grid(row=4, column=1, sticky="w", pady=5)
                    
                    # Séparateur
                    ttk.Separator(details_grid, orient="horizontal").grid(row=5, column=0, columnspan=2, sticky="ew", pady=10)
                    
                    # Ligne 6: Quantité demandée
                    ttk.Label(details_grid, text="Quantité demandée:", 
                             font=("Arial", 10, "bold"), background=CARD_BG).grid(row=6, column=0, sticky="w", pady=5)
                    
                    # Spinbox pour la quantité
                    qty_frame = ttk.Frame(details_grid, style="Card.TFrame")
                    qty_frame.grid(row=6, column=1, sticky="w", pady=5)
                    
                    self.qty_var = tk.IntVar(value=1)
                    self.qty_spinbox = tk.Spinbox(qty_frame, from_=1, to=sample['QUANTITE'], 
                                                textvariable=self.qty_var, width=5, 
                                                font=("Arial", 10))
                    self.qty_spinbox.pack()
                    
                    # Stocker la référence et activer le bouton
                    self.selected_reference = sample['REFERENCE']
                    self.request_btn.config(state="normal")
                
                cursor.close()
                conn.close()
            except Error as e:
                messagebox.showerror("Erreur", f"Erreur lors de la récupération des détails: {e}")
    
    def make_request(self):
        """Crée une demande pour l'échantillon sélectionné."""
        if not hasattr(self, 'selected_reference'):
            messagebox.showwarning("Avertissement", "Veuillez sélectionner un échantillon")
            return
        
        try:
            qty = self.qty_var.get()
            if qty <= 0:
                messagebox.showwarning("Avertissement", "La quantité doit être supérieure à 0")
                return
        except:
            messagebox.showwarning("Avertissement", "Quantité invalide")
            return
        
        conn = create_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Créer la demande
                cursor.execute("INSERT INTO DEMANDE (MATRICULE, STATUT) VALUES (%s, %s)", 
                             (self.current_user, 'en_attente'))
                demande_id = cursor.lastrowid
                
                # Ajouter le détail de la demande
                cursor.execute("INSERT INTO DETAIL_DEMANDE (ID_DEMANDE, REFERENCE, QUANTITE) VALUES (%s, %s, %s)",
                             (demande_id, self.selected_reference, qty))
                
                # Enregistrer dans l'historique
                self.log_action(self.current_user, 'demande', 
                              f"Demande #{demande_id} pour {qty} x {self.selected_reference}")
                
                conn.commit()
                cursor.close()
                conn.close()
                
                messagebox.showinfo("Succès", "Votre demande a été enregistrée et est en attente de validation")
                
                # Retourner au tableau de bord
                self.show_dashboard()
            except Error as e:
                messagebox.showerror("Erreur", f"Erreur lors de la création de la demande: {e}")
    
    def show_return(self):
        """Affiche la page de retour d'échantillon."""
        self.set_active_menu("Retour échantillon")
        self.clear_content()
        
        # Créer l'en-tête
        self.create_header("Retour d'échantillon")
        
        # Cadre principal
        main_frame = ttk.Frame(self.content_frame, style="Content.TFrame")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Titre de la section
        ttk.Label(main_frame, text="Retourner un échantillon", 
                 font=("Arial", 14, "bold"), background=CONTENT_BG).pack(anchor="w", pady=(0, 10))
        
        # Barre de recherche
        search_frame = ttk.Frame(main_frame, style="Content.TFrame")
        search_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(search_frame, text="Rechercher par référence ou article:", 
                 background=CONTENT_BG).pack(side="left", padx=(0, 10))
        
        self.return_search_entry = ttk.Entry(search_frame, width=40)
        self.return_search_entry.pack(side="left", padx=5)
        self.return_search_entry.bind('<KeyRelease>', self.search_user_samples)
        
        # Panneau divisé: liste à gauche, détails à droite
        split_frame = ttk.Frame(main_frame, style="Content.TFrame")
        split_frame.pack(fill="both", expand=True)
        
        # Panneau gauche: liste des échantillons
        left_frame = ttk.Frame(split_frame, style="Card.TFrame", padding=10)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        ttk.Label(left_frame, text="Vos échantillons", 
                 font=("Arial", 12, "bold"), background=CARD_BG).pack(anchor="w", pady=(0, 10))
        
        # Liste des échantillons
        list_frame = ttk.Frame(left_frame, style="Card.TFrame")
        list_frame.pack(fill="both", expand=True)
        
        self.user_samples_listbox = tk.Listbox(list_frame, font=("Arial", 10), 
                                              bg=CARD_BG, fg=TEXT_DARK,
                                              selectbackground=STAT_BLUE, selectforeground=TEXT_LIGHT)
        self.user_samples_listbox.pack(side="left", fill="both", expand=True)
        
        list_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.user_samples_listbox.yview)
        self.user_samples_listbox.configure(yscrollcommand=list_scrollbar.set)
        list_scrollbar.pack(side="right", fill="y")
        
        # Panneau droit: détails de l'échantillon
        right_frame = ttk.Frame(split_frame, style="Card.TFrame", padding=10)
        right_frame.pack(side="right", fill="both", expand=True)
        
        ttk.Label(right_frame, text="Détails du retour", 
                 font=("Arial", 12, "bold"), background=CARD_BG).pack(anchor="w", pady=(0, 10))
        
        # Cadre pour les détails
        self.return_details_frame = ttk.Frame(right_frame, style="Card.TFrame")
        self.return_details_frame.pack(fill="both", expand=True)
        
        # Bouton de retour (initialement désactivé)
        self.return_btn = ttk.Button(right_frame, text="Demander un retour", 
                                    command=self.request_return, state="disabled", style="Warning.TButton")
        self.return_btn.pack(pady=10, padx=5, anchor="e")
        
        # Remplir la liste des échantillons de l'utilisateur
        self.populate_user_samples_list()
        
        # Lier la sélection dans la liste
        self.user_samples_listbox.bind('<<ListboxSelect>>', self.show_return_sample_details)
    
    def populate_user_samples_list(self, search_term=None):
        """Remplit la liste des échantillons en possession de l'utilisateur."""
        # Vider la liste
        self.user_samples_listbox.delete(0, tk.END)
        
        conn = create_db_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                
                # Requête pour récupérer les échantillons de l'utilisateur
                query = """
                SELECT e.REFERENCE, e.ARTICLE, e.TAILLE, dd.QUANTITE
                FROM ECHANTILLON e
                JOIN DETAIL_DEMANDE dd ON e.REFERENCE = dd.REFERENCE
                JOIN DEMANDE d ON dd.ID_DEMANDE = d.ID_DEMANDE
                JOIN LIVRAISON_DEMANDE ld ON d.ID_DEMANDE = ld.ID_DEMANDE
                JOIN livraison l ON ld.ID_LIVRAISON = l.ID_livraison
                JOIN UTILISATEUR u ON d.MATRICULE = u.MATRICULE
                LEFT JOIN UTILISATEUR livreur ON l.MATRICULE_LIVREUR = livreur.MATRICULE
                WHERE d.MATRICULE = %s 
                AND d.STATUT = 'acceptee'
                AND l.STATUT = 'livree'
                AND e.STATUT = 'avec_user'
                AND NOT EXISTS (
                    SELECT 1 FROM RETOUR r
                    JOIN DETAIL_RETOUR dr ON r.ID_RETOUR = dr.ID_RETOUR
                    WHERE dr.REFERENCE = e.REFERENCE
                    AND r.STATUT NOT IN ('refuse', 'traite')
                )
                """
                
                params = [self.current_user]
                
                # Ajouter le filtre de recherche si nécessaire
                if search_term:
                    query += " AND (e.REFERENCE LIKE %s OR e.ARTICLE LIKE %s)"
                    params.extend([f"%{search_term}%", f"%{search_term}%"])
                
                query += " ORDER BY e.ARTICLE"
                
                cursor.execute(query, params)
                samples = cursor.fetchall()
                
                # Ajouter les échantillons à la liste
                for sample in samples:
                    self.user_samples_listbox.insert(tk.END, 
                                                   f"{sample['REFERENCE']} - {sample['ARTICLE']} ({sample['TAILLE']}) - Qté: {sample['QUANTITE']}")
                
                # Afficher un message si la liste est vide
                if self.user_samples_listbox.size() == 0:
                    messagebox.showinfo("Information", "Aucun échantillon disponible pour retour")
                
                cursor.close()
                conn.close()
            except Error as e:
                messagebox.showerror("Erreur", f"Erreur lors de la récupération des échantillons: {e}")
    
    def search_user_samples(self, event):
        """Recherche des échantillons de l'utilisateur en fonction du texte saisi."""
        search_term = self.return_search_entry.get().strip()
        self.populate_user_samples_list(search_term)
    
    def show_return_sample_details(self, event):
        """Affiche les détails de l'échantillon sélectionné pour retour."""
        # Nettoyage du cadre de détails
        for widget in self.return_details_frame.winfo_children():
            widget.destroy()
        self.return_btn.config(state="disabled")
        selection = self.user_samples_listbox.curselection()
        if not selection:
            return
        selected_text = self.user_samples_listbox.get(selection[0])
        ref = selected_text.split(' - ')[0].strip()

        conn = create_db_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                # On récupère la quantité de l'échantillon pour l'utilisateur et la référence
                cursor.execute("""
                    SELECT dd.QUANTITE
                    FROM DETAIL_DEMANDE dd
                    JOIN DEMANDE d ON dd.ID_DEMANDE = d.ID_DEMANDE
                    JOIN LIVRAISON_DEMANDE ld ON d.ID_DEMANDE = ld.ID_DEMANDE
                    JOIN livraison l ON ld.ID_LIVRAISON = l.ID_livraison
                    WHERE d.MATRICULE = %s
                      AND dd.REFERENCE = %s
                      AND d.STATUT = 'acceptee'
                      AND l.STATUT = 'livree'
                    ORDER BY dd.ID_DEMANDE DESC
                    LIMIT 1
                """, (self.current_user, ref))
                sample = cursor.fetchone()
                cursor.close()
                conn.close()
                if sample:
                    details_grid = ttk.Frame(self.return_details_frame)
                    details_grid.pack(fill="both", expand=True, padx=5, pady=5)
                    details_grid.columnconfigure(0, weight=1)
                    details_grid.columnconfigure(1, weight=2)
                    ttk.Label(details_grid, text="Référence:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=5)
                    ttk.Label(details_grid, text=ref).grid(row=0, column=1, sticky="w", pady=5)
                    ttk.Label(details_grid, text="Quantité en possession:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", pady=5)
                    ttk.Label(details_grid, text=str(sample['QUANTITE'])).grid(row=1, column=1, sticky="w", pady=5)
                    ttk.Separator(details_grid, orient="horizontal").grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)
                    ttk.Label(details_grid, text="Quantité à retourner:", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky="w", pady=5)
                    qty_frame = ttk.Frame(details_grid)
                    qty_frame.grid(row=3, column=1, sticky="w", pady=5)
                    self.return_qty_var = tk.IntVar(value=1)
                    self.return_qty_spinbox = tk.Spinbox(qty_frame, from_=1, to=sample['QUANTITE'], textvariable=self.return_qty_var, width=5, font=("Arial", 10))
                    self.return_qty_spinbox.pack()
                    self.selected_return_ref = ref
                    self.return_btn.config(state="normal")
                else:
                    messagebox.showerror("Erreur", "Aucun détail trouvé pour cet échantillon.")
            except Error as e:
                messagebox.showerror("Erreur", f"Erreur lors de la récupération des détails: {e}")
    
    def request_return(self):
        """Crée une demande de retour pour l'échantillon sélectionné."""
        if not hasattr(self, 'selected_return_ref'):
            messagebox.showwarning("Avertissement", "Veuillez sélectionner un échantillon")
            return
        
        try:
            qty = self.return_qty_var.get()
            if qty <= 0:
                messagebox.showwarning("Avertissement", "La quantité doit être supérieure à 0")
                return
        except:
            messagebox.showwarning("Avertissement", "Quantité invalide")
            return
        
        conn = create_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Créer le retour
                cursor.execute("INSERT INTO RETOUR (MATRICULE, STATUT) VALUES (%s, %s)", 
                             (self.current_user, 'en_attente'))
                retour_id = cursor.lastrowid
                
                # Ajouter le détail du retour
                cursor.execute("INSERT INTO DETAIL_RETOUR (ID_RETOUR, REFERENCE, QUANTITE) VALUES (%s, %s, %s)",
                             (retour_id, self.selected_return_ref, qty))
                
                # Créer une livraison pour le retour
                cursor.execute("""
                    INSERT INTO livraison (TYPE, STATUT, MATRICULE_LIVREUR) 
                    VALUES ('retour', 'en_attente', NULL)
                """)
                livraison_id = cursor.lastrowid
                
                # Lier la livraison au retour
                cursor.execute("""
                    UPDATE RETOUR SET ID_livraison = %s WHERE ID_RETOUR = %s
                """, (livraison_id, retour_id))
                
                # Enregistrer dans l'historique
                self.log_action(self.current_user, 'retour', 
                              f"Retour #{retour_id} pour {qty} x {self.selected_return_ref}")
                self.log_action(self.current_user, 'notification', 
                              f"Livraison de retour #{livraison_id} créée pour retour #{retour_id}")
                
                conn.commit()
                cursor.close()
                conn.close()
                
                messagebox.showinfo("Succès", "Votre demande de retour a été enregistrée et sera traitée")
                
                # Retourner au tableau de bord
                self.show_dashboard()
            except Error as e:
                messagebox.showerror("Erreur", f"Erreur lors de la création de la demande de retour: {e}")
    
    def show_requests_management(self):
        """Affiche la page de gestion des demandes (admin)."""
        self.set_active_menu("Gérer demandes")
        self.clear_content()
        
        # Créer l'en-tête
        self.create_header("Gestion des demandes")
        
        # Cadre principal
        main_frame = ttk.Frame(self.content_frame, style="Content.TFrame")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Titre de la section
        ttk.Label(main_frame, text="Liste des demandes", 
                 font=("Arial", 14, "bold"), background=CONTENT_BG).pack(anchor="w", pady=(0, 10))
        
        # Cadre pour le tableau
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill="both", expand=True)
        
        # Créer le tableau
        columns = ('id', 'user', 'date', 'statut', 'details')
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', style="Treeview")
        
        # Définir les en-têtes
        tree.heading('id', text='ID')
        tree.heading('user', text='Utilisateur')
        tree.heading('date', text='Date')
        tree.heading('statut', text='Statut')
        tree.heading('details', text='Détails')
        
        # Définir les largeurs de colonnes
        tree.column('id', width=50)
        tree.column('user', width=150)
        tree.column('date', width=150)
        tree.column('statut', width=100)
        tree.column('details', width=400)
        
        # Ajouter une scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)
        
        # Remplir le tableau avec les données
        self.populate_requests_table(tree)
        
        # Cadre pour les boutons d'action
        btn_frame = ttk.Frame(main_frame, style="Content.TFrame")
        btn_frame.pack(fill="x", pady=10)
        
        # Boutons d'action
        ttk.Button(btn_frame, text="Accepter", command=lambda: self.process_request(tree, 'acceptee'), 
                  style="Success.TButton").pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Refuser", command=lambda: self.process_request(tree, 'refusee'), 
                  style="Danger.TButton").pack(side="left", padx=5)
    
    def populate_requests_table(self, tree):
        """Remplit le tableau des demandes avec les données de la base."""
        # Vider le tableau
        for i in tree.get_children():
            tree.delete(i)
        
        conn = create_db_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                
                # Récupérer les demandes
                cursor.execute("""
                    SELECT 
                        d.ID_DEMANDE,
                        u.MATRICULE,
                        u.NOM,
                        u.PRENOM,
                        d.DATE_DEMANDE,
                        d.STATUT,
                        GROUP_CONCAT(
                            CONCAT(e.ARTICLE, ' (Ref:', dd.REFERENCE, ')')
                            SEPARATOR ', '
                        ) as DETAILS
                    FROM DEMANDE d
                    JOIN UTILISATEUR u ON d.MATRICULE = u.MATRICULE
                    JOIN DETAIL_DEMANDE dd ON d.ID_DEMANDE = dd.ID_DEMANDE
                    JOIN ECHANTILLON e ON dd.REFERENCE = e.REFERENCE
                    GROUP BY d.ID_DEMANDE
                    ORDER BY d.DATE_DEMANDE DESC
                """)
                
                requests = cursor.fetchall()
                
                # Ajouter les demandes au tableau
                for i, req in enumerate(requests):
                    tree.insert('', 'end', values=(
                        req['ID_DEMANDE'],
                        f"{req['MATRICULE']} - {req['NOM']} {req['PRENOM']}",
                        req['DATE_DEMANDE'].strftime('%Y-%m-%d %H:%M'),
                        req['STATUT'],
                        req['DETAILS']
                    ))
                    
                    # Appliquer des couleurs alternées aux lignes
                    if i % 2 == 0:
                        tree.item(tree.get_children()[-1], tags=('evenrow',))
                    else:
                        tree.item(tree.get_children()[-1], tags=('oddrow',))
                
                # Configurer les tags pour les couleurs alternées
                tree.tag_configure('evenrow', background=TABLE_ROW_EVEN)
                tree.tag_configure('oddrow', background=TABLE_ROW_ODD)
                
                cursor.close()
                conn.close()
            except Error as e:
                messagebox.showerror("Erreur", f"Erreur lors de la récupération des demandes: {e}")
    
    def process_request(self, tree, action):
        """Traite une demande (accepter ou refuser)."""
        # Récupérer la sélection
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner une demande")
            return
        
        # Récupérer l'ID de la demande
        item = tree.item(selection[0])
        request_id = item['values'][0]
        request_status = item['values'][3]
        
        # Vérifier si la demande est déjà traitée
        if request_status != 'en_attente':
            messagebox.showwarning("Avertissement", "Cette demande a déjà été traitée")
            return
        
        conn = create_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                if action == 'acceptee':
                    # 1. Création de la livraison
                    cursor.execute("""
                        INSERT INTO livraison (TYPE, STATUT, DATE_LIVRAISON, MATRICULE_LIVREUR)
                        VALUES ('demande', 'en_attente', NOW(), NULL)
                    """)
                    livraison_id = cursor.lastrowid
                    
                    # 2. Lien avec la demande dans LIVRAISON_DEMANDE
                    cursor.execute("""
                        INSERT INTO LIVRAISON_DEMANDE (ID_LIVRAISON, ID_DEMANDE)
                        VALUES (%s, %s)
                    """, (livraison_id, request_id))
                    
                    # 3. Mettre à jour le statut de la demande
                    cursor.execute("""
                        UPDATE DEMANDE 
                        SET STATUT = 'acceptee'
                        WHERE ID_DEMANDE = %s
                    """, (request_id,))
                    
                    # 4. Mise à jour des échantillons
                    cursor.execute("""
                        UPDATE ECHANTILLON e
                        JOIN DETAIL_DEMANDE dd ON e.REFERENCE = dd.REFERENCE
                        SET e.STATUT = 'en_stock'
                        WHERE dd.ID_DEMANDE = %s
                    """, (request_id,))
                    
                    # 5. Décrémenter la quantité si demandé = 1
                    cursor.execute("""
                        SELECT REFERENCE, QUANTITE
                        FROM DETAIL_DEMANDE
                        WHERE ID_DEMANDE = %s
                    """, (request_id,))
                    details = cursor.fetchall()
                    for ref, qty in details:
                        if qty == 1:
                            cursor.execute("""
                                UPDATE ECHANTILLON
                                SET QUANTITE = QUANTITE - 1
                                WHERE REFERENCE = %s AND QUANTITE >= 1
                            """, (ref,))
                    
                    # 6. Enregistrer dans l'historique
                    self.log_action(self.current_user, 'demande', 
                                  f"Demande #{request_id} acceptée")
                
                elif action == 'refusee':
                    # Mettre à jour le statut de la demande
                    cursor.execute("""
                        UPDATE DEMANDE 
                        SET STATUT = 'refusee' 
                        WHERE ID_DEMANDE = %s
                    """, (request_id,))
                    
                    # Enregistrer dans l'historique
                    self.log_action(self.current_user, 'demande', 
                                  f"Demande #{request_id} refusée")
                
                conn.commit()
                cursor.close()
                conn.close()
                
                messagebox.showinfo("Succès", f"Demande #{request_id} {action}e")
                
                # Rafraîchir l'affichage
                self.show_requests_management()
            except Error as e:
                messagebox.showerror("Erreur", f"Erreur lors du traitement de la demande: {e}")
    
    def show_sample_tracking(self):
        """Affiche la page de suivi des échantillons (admin)."""
        self.set_active_menu("Suivi échantillons")
        self.clear_content()
        
        # Créer l'en-tête
        self.create_header("Suivi des échantillons")
        
        # Cadre principal
        main_frame = ttk.Frame(self.content_frame, style="Content.TFrame")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Titre de la section
        ttk.Label(main_frame, text="Localisation des échantillons", 
                 font=("Arial", 14, "bold"), background=CONTENT_BG).pack(anchor="w", pady=(0, 10))
        
        # Cadre pour le tableau
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill="both", expand=True)
        
        # Créer le tableau
        columns = ('reference', 'article', 'statut', 'location')
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', style="Treeview")
        
        # Définir les en-têtes
        tree.heading('reference', text='Référence')
        tree.heading('article', text='Article')
        tree.heading('statut', text='Statut')
        tree.heading('location', text='Localisation')
        
        # Définir les largeurs de colonnes
        tree.column('reference', width=120)
        tree.column('article', width=200)
        tree.column('statut', width=120)
        tree.column('location', width=400)
        
        # Ajouter une scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)
        
        # Remplir le tableau avec les données
        self.populate_tracking_table(tree)
    
    def populate_tracking_table(self, tree):
        """Remplit le tableau de suivi des échantillons avec les données de la base."""
        # Vider le tableau
        for i in tree.get_children():
            tree.delete(i)
        
        conn = create_db_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                all_samples = []
                
                # Échantillons en stock
                cursor.execute("""
                    SELECT REFERENCE, ARTICLE, STATUT, 'En stock' AS location
                    FROM ECHANTILLON
                    WHERE STATUT = 'en_stock'
                """)
                all_samples.extend(cursor.fetchall())
                
                # Échantillons en livraison (demande) - avec info du livreur
                cursor.execute("""
                    SELECT e.REFERENCE, e.ARTICLE, e.STATUT, 
                           CASE
                               WHEN l.MATRICULE_LIVREUR IS NOT NULL THEN
                                   CONCAT('En livraison par ', livreur.NOM, ' ', livreur.PRENOM, 
                                         ' (Demande #', d.ID_DEMANDE, ' pour ', u.NOM, ' ', u.PRENOM, ')')
                               ELSE
                                   CONCAT('En attente de livraison (Demande #', d.ID_DEMANDE, ' pour ', u.NOM, ' ', u.PRENOM, ')')
                           END AS location
                    FROM ECHANTILLON e
                    JOIN DETAIL_DEMANDE dd ON e.REFERENCE = dd.REFERENCE
                    JOIN DEMANDE d ON dd.ID_DEMANDE = d.ID_DEMANDE
                    JOIN LIVRAISON_DEMANDE ld ON d.ID_DEMANDE = ld.ID_DEMANDE
                    JOIN livraison l ON ld.ID_LIVRAISON = l.ID_livraison
                    JOIN UTILISATEUR u ON d.MATRICULE = u.MATRICULE
                    LEFT JOIN UTILISATEUR livreur ON l.MATRICULE_LIVREUR = livreur.MATRICULE
                    WHERE e.STATUT = 'en_livraison'
                    AND l.TYPE = 'demande'
                """)
                all_samples.extend(cursor.fetchall())
                
                # Échantillons avec utilisateur
                cursor.execute("""
                    SELECT e.REFERENCE, e.ARTICLE, e.STATUT, 
                           CONCAT('Avec ', u.NOM, ' ', u.PRENOM, ' (Demande #', d.ID_DEMANDE, ')') AS location
                    FROM ECHANTILLON e
                    JOIN DETAIL_DEMANDE dd ON e.REFERENCE = dd.REFERENCE
                    JOIN DEMANDE d ON dd.ID_DEMANDE = d.ID_DEMANDE
                    JOIN UTILISATEUR u ON d.MATRICULE = u.MATRICULE
                    WHERE e.STATUT = 'avec_user'
                """)
                all_samples.extend(cursor.fetchall())
                
                # Échantillons en retour - avec info du livreur
                cursor.execute("""
                    SELECT e.REFERENCE, e.ARTICLE, e.STATUT, 
                           CASE
                               WHEN l.MATRICULE_LIVREUR IS NOT NULL THEN
                                   CONCAT('En retour par ', livreur.NOM, ' ', livreur.PRENOM, 
                                         ' (Retour #', r.ID_RETOUR, ' de ', u.NOM, ' ', u.PRENOM, ')')
                               ELSE
                                   CONCAT('En attente de retour (Retour #', r.ID_RETOUR, ' de ', u.NOM, ' ', u.PRENOM, ')')
                           END AS location
                    FROM ECHANTILLON e
                    JOIN DETAIL_RETOUR dr ON e.REFERENCE = dr.REFERENCE
                    JOIN RETOUR r ON dr.ID_RETOUR = r.ID_RETOUR
                    JOIN livraison l ON r.ID_livraison = l.ID_livraison
                    JOIN UTILISATEUR u ON r.MATRICULE = u.MATRICULE
                    LEFT JOIN UTILISATEUR livreur ON l.MATRICULE_LIVREUR = livreur.MATRICULE
                    WHERE e.STATUT = 'en_livraison'
                    AND l.TYPE = 'retour'
                """)
                all_samples.extend(cursor.fetchall())
                
                # Ajouter les échantillons au tableau
                for i, sample in enumerate(all_samples):
                    tree.insert('', 'end', values=(
                        sample['REFERENCE'],
                        sample['ARTICLE'],
                        sample['STATUT'],
                        sample['location']
                    ))
                    
                    # Appliquer des couleurs alternées aux lignes
                    if i % 2 == 0:
                        tree.item(tree.get_children()[-1], tags=('evenrow',))
                    else:
                        tree.item(tree.get_children()[-1], tags=('oddrow',))
                
                # Configurer les tags pour les couleurs alternées
                tree.tag_configure('evenrow', background=TABLE_ROW_EVEN)
                tree.tag_configure('oddrow', background=TABLE_ROW_ODD)
                
                cursor.close()
                conn.close()
            except Error as e:
                messagebox.showerror("Erreur", f"Erreur lors de la récupération des échantillons: {e}")
    
    def show_full_history(self):
        """Affiche l'historique complet (admin)."""
        self.set_active_menu("Historique complet")
        self.clear_content()
        
        # Créer l'en-tête
        self.create_header("Historique complet")
        
        # Cadre principal
        main_frame = ttk.Frame(self.content_frame, style="Content.TFrame")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Titre de la section
        ttk.Label(main_frame, text="Historique complet du système", 
                 font=("Arial", 14, "bold"), background=CONTENT_BG).pack(anchor="w", pady=(0, 10))
        
        # Cadre pour le tableau
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill="both", expand=True)
        
        # Créer le tableau
        columns = ('date', 'matricule', 'type', 'description')
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', style="Treeview")
        
        # Définir les en-têtes
        tree.heading('date', text='Date')
        tree.heading('matricule', text='Matricule')
        tree.heading('type', text='Type')
        tree.heading('description', text='Description')
        
        # Définir les largeurs de colonnes
        tree.column('date', width=150)
        tree.column('matricule', width=100)
        tree.column('type', width=100)
        tree.column('description', width=500)
        
        # Ajouter une scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)
        
        # Remplir le tableau avec les données
        self.populate_full_history_table(tree)
    
    def populate_full_history_table(self, tree):
        """Remplit le tableau d'historique complet avec les données de la base."""
        # Vider le tableau
        for i in tree.get_children():
            tree.delete(i)
        
        conn = create_db_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                
                # Récupérer l'historique complet
                cursor.execute("""
                    SELECT h.DATE_ACTION, h.MATRICULE, u.NOM, u.PRENOM, h.TYPE_ACTION, h.DESCRIPTION
                    FROM HISTORIQUE h
                    JOIN UTILISATEUR u ON h.MATRICULE = u.MATRICULE
                    ORDER BY h.DATE_ACTION DESC
                """)
                
                history = cursor.fetchall()
                
                # Ajouter les entrées au tableau
                for i, entry in enumerate(history):
                    tree.insert('', 'end', values=(
                        entry['DATE_ACTION'].strftime('%Y-%m-%d %H:%M:%S'),
                        f"{entry['MATRICULE']} ({entry['NOM']} {entry['PRENOM']})",
                        entry['TYPE_ACTION'],
                        entry['DESCRIPTION']
                    ))
                    
                    # Appliquer des couleurs alternées aux lignes
                    if i % 2 == 0:
                        tree.item(tree.get_children()[-1], tags=('evenrow',))
                    else:
                        tree.item(tree.get_children()[-1], tags=('oddrow',))
                
                # Configurer les tags pour les couleurs alternées
                tree.tag_configure('evenrow', background=TABLE_ROW_EVEN)
                tree.tag_configure('oddrow', background=TABLE_ROW_ODD)
                
                cursor.close()
                conn.close()
            except Error as e:
                messagebox.showerror("Erreur", f"Erreur lors de la récupération de l'historique: {e}")
    
    def show_deliveries(self):
        """Affiche la page des livraisons (livreur)."""
        self.set_active_menu("Livraisons")
        self.clear_content()
        
        # Créer l'en-tête
        self.create_header("Gestion des livraisons")
        
        # Cadre principal
        main_frame = ttk.Frame(self.content_frame, style="Content.TFrame")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Titre de la section
        ttk.Label(main_frame, text="Livraisons à effectuer", 
                 font=("Arial", 14, "bold"), background=CONTENT_BG).pack(anchor="w", pady=(0, 10))
        
        # Cadre pour le tableau
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill="both", expand=True)
        
        # Créer le tableau
        columns = ('id', 'type', 'statut', 'date', 'details')
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', style="Treeview")
        
        # Définir les en-têtes
        tree.heading('id', text='ID')
        tree.heading('type', text='Type')
        tree.heading('statut', text='Statut')
        tree.heading('date', text='Date')
        tree.heading('details', text='Détails')
        
        # Définir les largeurs de colonnes
        tree.column('id', width=50)
        tree.column('type', width=80)
        tree.column('statut', width=100)
        tree.column('date', width=150)
        tree.column('details', width=400)
        
        # Ajouter une scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)
        
        # Remplir le tableau avec les données
        self.populate_deliveries_table(tree)
        
        # Cadre pour les boutons d'action
        btn_frame = ttk.Frame(main_frame, style="Content.TFrame")
        btn_frame.pack(fill="x", pady=10)
        
        # Boutons d'action
        ttk.Button(btn_frame, text="Prendre en charge", 
                  command=lambda: self.update_delivery_status(tree, 'en_cours'),
                  style="Info.TButton").pack(side="left", padx=5)
        
        ttk.Button(btn_frame, text="Marquer comme livrée", 
                  command=lambda: self.update_delivery_status(tree, 'livree'),
                  style="Success.TButton").pack(side="left", padx=5)
    
    def populate_deliveries_table(self, tree):
        """Remplit le tableau des livraisons avec les données de la base."""
        # Vider le tableau
        for i in tree.get_children():
            tree.delete(i)
        
        conn = create_db_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                
                # Récupérer les livraisons
                cursor.execute("""
                    SELECT 
                        l.ID_livraison as id,
                        l.TYPE as type,
                        l.STATUT as statut,
                        l.DATE_LIVRAISON as date,
                        CASE
                            WHEN l.TYPE = 'demande' THEN 
                                CONCAT('Demande #', d.ID_DEMANDE, ' pour ', u.NOM, ' ', u.PRENOM)
                            WHEN l.TYPE = 'retour' THEN 
                                CONCAT('Retour #', r.ID_RETOUR, ' de ', u.NOM, ' ', u.PRENOM)
                        END as details
                    FROM livraison l
                    LEFT JOIN LIVRAISON_DEMANDE ld ON l.ID_livraison = ld.ID_livraison
                    LEFT JOIN DEMANDE d ON ld.ID_DEMANDE = d.ID_DEMANDE
                    LEFT JOIN RETOUR r ON l.ID_livraison = r.ID_livraison
                    LEFT JOIN UTILISATEUR u ON (d.MATRICULE = u.MATRICULE OR r.MATRICULE = u.MATRICULE)
                    WHERE l.STATUT IN ('en_attente', 'en_cours')
                    AND (l.MATRICULE_LIVREUR IS NULL OR l.MATRICULE_LIVREUR = %s)
                    ORDER BY l.DATE_LIVRAISON ASC
                """, (self.current_user,))
                
                deliveries = cursor.fetchall()
                
                # Ajouter les livraisons au tableau
                for i, delivery in enumerate(deliveries):
                    date_str = delivery['date'].strftime('%Y-%m-%d %H:%M:%S') if delivery['date'] else ""
                    tree.insert('', 'end', values=(
                        delivery['id'],
                        delivery['type'],
                        delivery['statut'],
                        date_str,
                        delivery['details']
                    ))
                    
                    # Appliquer des couleurs alternées aux lignes
                    if i % 2 == 0:
                        tree.item(tree.get_children()[-1], tags=('evenrow',))
                    else:
                        tree.item(tree.get_children()[-1], tags=('oddrow',))
                
                # Configurer les tags pour les couleurs alternées
                tree.tag_configure('evenrow', background=TABLE_ROW_EVEN)
                tree.tag_configure('oddrow', background=TABLE_ROW_ODD)
                
                cursor.close()
                conn.close()
            except Error as e:
                messagebox.showerror("Erreur", f"Erreur lors de la récupération des livraisons: {e}")
    
    def update_delivery_status(self, tree, status):
        """Met à jour le statut d'une livraison."""
        # Récupérer la sélection
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner une livraison")
            return
        
        # Récupérer l'ID de la livraison
        item = tree.item(selection[0])
        delivery_id = item['values'][0]
        delivery_type = item['values'][1]
        current_status = item['values'][2]
        
        # Vérifier si le statut est cohérent
        if status == 'en_cours' and current_status != 'en_attente':
            messagebox.showwarning("Avertissement", "Cette livraison est déjà en cours ou terminée")
            return
        
        if status == 'livree' and current_status != 'en_cours':
            messagebox.showwarning("Avertissement", "Vous devez d'abord prendre en charge cette livraison")
            return
        
        conn = create_db_connection()
        cursor = None
        if conn:
            try:
                cursor = conn.cursor()
                
                if status == 'en_cours':
                    # Prendre en charge la livraison
                    cursor.execute("""
                        UPDATE livraison 
                        SET STATUT = 'en_cours', MATRICULE_LIVREUR = %s 
                        WHERE ID_livraison = %s
                    """, (self.current_user, delivery_id))
                 # Mettre à jour le statut des échantillons à 'en_livraison'
                    if delivery_type == 'demande':
                        cursor.execute("""
                            UPDATE ECHANTILLON e
                            JOIN DETAIL_DEMANDE dd ON e.REFERENCE = dd.REFERENCE
                            JOIN DEMANDE d ON dd.ID_DEMANDE = d.ID_DEMANDE
                            JOIN LIVRAISON_DEMANDE ld ON d.ID_DEMANDE = ld.ID_DEMANDE
                            SET e.STATUT = 'en_livraison'
                            WHERE ld.ID_LIVRAISON = %s
                        """, (delivery_id,))
                    elif delivery_type == 'retour':
                        cursor.execute("""
                            UPDATE ECHANTILLON e
                            JOIN DETAIL_RETOUR dr ON e.REFERENCE = dr.REFERENCE
                            JOIN RETOUR r ON dr.ID_RETOUR = r.ID_RETOUR
                            SET e.STATUT = 'en_livraison'
                            WHERE r.ID_livraison = %s
                        """, (delivery_id,))   
                    # Si c'est un retour, mettre à jour le statut des échantillons à 'en_livraison'
                    if delivery_type == 'retour':
                        cursor.execute("""
                            UPDATE ECHANTILLON e
                            JOIN DETAIL_RETOUR dr ON e.REFERENCE = dr.REFERENCE
                            JOIN RETOUR r ON dr.ID_RETOUR = r.ID_RETOUR
                            SET e.STATUT = 'en_livraison'
                            WHERE r.ID_livraison = %s
                        """, (delivery_id,))
                    
                    # Enregistrer dans l'historique
                    self.log_action(self.current_user, 'livraison', 
                                  f"Livraison #{delivery_id} prise en charge")
                
                elif status == 'livree':
                    # Marquer la livraison comme livrée
                    cursor.execute("""
                        UPDATE livraison 
                        SET STATUT = 'livree' 
                        WHERE ID_livraison = %s
                    """, (delivery_id,))
                    
                    # Si c'est une livraison de demande
                    if delivery_type == 'demande':
                        cursor.execute("""
                            UPDATE ECHANTILLON e
                            JOIN DETAIL_DEMANDE dd ON e.REFERENCE = dd.REFERENCE
                            JOIN DEMANDE d ON dd.ID_DEMANDE = d.ID_DEMANDE
                            JOIN LIVRAISON_DEMANDE ld ON d.ID_DEMANDE = ld.ID_DEMANDE
                            SET e.STATUT = 'avec_user'
                            WHERE ld.ID_LIVRAISON = %s
                        """, (delivery_id,))
                    
                    # Si c'est une livraison de retour
                    elif delivery_type == 'retour':
                        # Mettre à jour le statut ET la quantité
                        cursor.execute("""
                            UPDATE ECHANTILLON e
                            JOIN DETAIL_RETOUR dr ON e.REFERENCE = dr.REFERENCE
                            JOIN RETOUR r ON dr.ID_RETOUR = r.ID_RETOUR
                            SET e.STATUT = 'en_stock',
                                e.QUANTITE = e.QUANTITE + dr.QUANTITE
                            WHERE r.ID_livraison = %s
                        """, (delivery_id,))
                        
                        # Mettre à jour le statut du retour
                        cursor.execute("""
                            UPDATE RETOUR 
                            SET STATUT = 'traite' 
                            WHERE ID_livraison = %s
                        """, (delivery_id,))
                
                conn.commit()
                messagebox.showinfo("Succès", f"Statut de la livraison #{delivery_id} mis à jour")
                self.show_deliveries()
                
            except Error as e:
                messagebox.showerror("Erreur", f"Erreur lors de la mise à jour du statut: {e}")
            finally:
                if cursor:
                    cursor.close()
                if conn.is_connected():
                    conn.close()
    
    def logout(self):
        """Déconnecte l'utilisateur et retourne à l'écran de connexion."""
        if self.current_user:
            self.log_action(self.current_user, 'deconnexion', "Déconnexion de l'utilisateur")
        
        self.current_user = None
        self.user_role = None
        self.user_fullname = ""
        self.active_menu = None
        
        self.show_login_frame()

# Point d'entrée de l'application
if __name__ == "__main__":
    root = tk.Tk()
    app = SampleManagementSystem(root)
    root.mainloop()
