import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime
import os

# Import optionnel de reportlab pour les PDFs
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

class AtelierManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Gestion d'Atelier de Meubles")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        # Initialiser la base de données
        self.init_database()
        
        # Créer l'interface
        self.create_interface()
        
        # Rafraîchir l'affichage
        self.refresh_all()
    
    def init_database(self):
        """Initialise la base de données SQLite"""
        self.conn = sqlite3.connect('atelier_meubles.db')
        self.cursor = self.conn.cursor()
        
        # Table des produits (renommage colonne prix_fabrication -> prix_revient)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS produits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                designation TEXT NOT NULL,
                description TEXT,
                stock_initial INTEGER DEFAULT 0,
                stock_actuel INTEGER DEFAULT 0,
                prix_revient REAL DEFAULT 0
            )
        ''')
        
        # Vérifier si la colonne existe déjà sous l'ancien nom et la renommer
        self.cursor.execute("PRAGMA table_info(produits)")
        columns = [column[1] for column in self.cursor.fetchall()]
        if 'prix_fabrication' in columns and 'prix_revient' not in columns:
            self.cursor.execute('ALTER TABLE produits RENAME COLUMN prix_fabrication TO prix_revient')
            self.conn.commit()
        
        # Table des ventes (renommage colonne prix_fabrication -> prix_revient + ajout acheteur)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ventes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produit_id INTEGER,
                quantite INTEGER,
                prix_revient REAL,
                prix_vente REAL,
                benefice REAL,
                acheteur TEXT,
                date_vente TEXT,
                FOREIGN KEY (produit_id) REFERENCES produits (id)
            )
        ''')
        
        # Vérifier et renommer la colonne dans la table ventes aussi
        self.cursor.execute("PRAGMA table_info(ventes)")
        columns = [column[1] for column in self.cursor.fetchall()]
        if 'prix_fabrication' in columns and 'prix_revient' not in columns:
            self.cursor.execute('ALTER TABLE ventes RENAME COLUMN prix_fabrication TO prix_revient')
            self.conn.commit()
        
        # Ajouter la colonne acheteur si elle n'existe pas
        if 'acheteur' not in columns:
            self.cursor.execute('ALTER TABLE ventes ADD COLUMN acheteur TEXT')
            self.conn.commit()
        
        self.conn.commit()
    
    def create_interface(self):
        """Crée l'interface graphique principale"""
        # Notebook pour les onglets
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Onglet 1: Gestion des produits
        self.create_products_tab()
        
        # Onglet 2: Gestion des ventes
        self.create_sales_tab()
        
        # Onglet 3: Tableau de bord
        self.create_dashboard_tab()
        
        # Onglet 4: Historique des ventes
        self.create_history_tab()
        
        # Onglet 5: Export et Utilitaires
        self.create_utilities_tab()
    
    def create_products_tab(self):
        """Crée l'onglet de gestion des produits"""
        products_frame = ttk.Frame(self.notebook)
        self.notebook.add(products_frame, text="Gestion des Produits")
        
        # Frame pour ajouter un produit
        add_frame = ttk.LabelFrame(products_frame, text="Ajouter un Produit", padding=10)
        add_frame.pack(fill='x', padx=10, pady=5)
        
        # Champs de saisie
        ttk.Label(add_frame, text="Désignation:").grid(row=0, column=0, sticky='w', pady=2)
        self.designation_entry = ttk.Entry(add_frame, width=30)
        self.designation_entry.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(add_frame, text="Description:").grid(row=1, column=0, sticky='w', pady=2)
        self.description_entry = ttk.Entry(add_frame, width=50)
        self.description_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=2)
        
        ttk.Label(add_frame, text="Stock Initial:").grid(row=2, column=0, sticky='w', pady=2)
        self.stock_entry = ttk.Entry(add_frame, width=15)
        self.stock_entry.grid(row=2, column=1, padx=5, pady=2)
        
        ttk.Label(add_frame, text="Prix de Revient:").grid(row=3, column=0, sticky='w', pady=2)
        self.prix_revient_entry = ttk.Entry(add_frame, width=15)
        self.prix_revient_entry.grid(row=3, column=1, padx=5, pady=2)
        
        # Boutons d'action
        buttons_frame = ttk.Frame(add_frame)
        buttons_frame.grid(row=4, column=1, pady=10)
        
        ttk.Button(buttons_frame, text="Ajouter Produit", command=self.add_product).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Modifier Sélectionné", command=self.modify_product).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Supprimer Sélectionné", command=self.delete_product).pack(side='left', padx=5)
        
        # Liste des produits
        list_frame = ttk.LabelFrame(products_frame, text="Liste des Produits", padding=10)
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Treeview pour afficher les produits
        columns = ('ID', 'Désignation', 'Description', 'Stock Actuel', 'Prix de Revient')
        self.products_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.products_tree.heading(col, text=col)
            self.products_tree.column(col, width=150)
        
        scrollbar_products = ttk.Scrollbar(list_frame, orient='vertical', command=self.products_tree.yview)
        self.products_tree.configure(yscrollcommand=scrollbar_products.set)
        
        self.products_tree.pack(side='left', fill='both', expand=True)
        scrollbar_products.pack(side='right', fill='y')
    
    def create_sales_tab(self):
        """Crée l'onglet de gestion des ventes"""
        sales_frame = ttk.Frame(self.notebook)
        self.notebook.add(sales_frame, text="Gestion des Ventes")
        
        # Frame pour enregistrer une vente
        sale_frame = ttk.LabelFrame(sales_frame, text="Enregistrer une Vente", padding=10)
        sale_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(sale_frame, text="Produit:").grid(row=0, column=0, sticky='w', pady=2)
        self.product_combo = ttk.Combobox(sale_frame, width=40, state='readonly')
        self.product_combo.grid(row=0, column=1, padx=5, pady=2)
        self.product_combo.bind('<<ComboboxSelected>>', self.on_product_selected)
        
        ttk.Label(sale_frame, text="Quantité à vendre:").grid(row=1, column=0, sticky='w', pady=2)
        self.quantity_sale_entry = ttk.Entry(sale_frame, width=15)
        self.quantity_sale_entry.grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(sale_frame, text="Prix de vente unitaire:").grid(row=2, column=0, sticky='w', pady=2)
        self.prix_vente_entry = ttk.Entry(sale_frame, width=15)
        self.prix_vente_entry.grid(row=2, column=1, padx=5, pady=2)
        
        # NOUVEAU CHAMP ACHETEUR
        ttk.Label(sale_frame, text="Acheteur:").grid(row=3, column=0, sticky='w', pady=2)
        self.acheteur_entry = ttk.Entry(sale_frame, width=40)
        self.acheteur_entry.grid(row=3, column=1, padx=5, pady=2)
        
        # Informations sur le produit sélectionné
        info_frame = ttk.LabelFrame(sales_frame, text="Informations Produit", padding=10)
        info_frame.pack(fill='x', padx=10, pady=5)
        
        self.stock_info_label = ttk.Label(info_frame, text="Stock disponible: -")
        self.stock_info_label.pack(anchor='w')
        
        self.prix_revient_info_label = ttk.Label(info_frame, text="Prix de revient: -")
        self.prix_revient_info_label.pack(anchor='w')
        
        self.benefice_preview_label = ttk.Label(info_frame, text="Bénéfice prévu: -", foreground='green')
        self.benefice_preview_label.pack(anchor='w')
        
        ttk.Button(sale_frame, text="Enregistrer Vente", command=self.record_sale).grid(row=4, column=1, pady=10)
        
        # Bind pour calculer le bénéfice en temps réel
        self.prix_vente_entry.bind('<KeyRelease>', self.calculate_preview_benefit)
        self.quantity_sale_entry.bind('<KeyRelease>', self.calculate_preview_benefit)
    
    def create_dashboard_tab(self):
        """Crée l'onglet tableau de bord"""
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="Tableau de Bord")
        
        # Statistiques générales
        stats_frame = ttk.LabelFrame(dashboard_frame, text="Statistiques Générales", padding=10)
        stats_frame.pack(fill='x', padx=10, pady=5)
        
        self.total_products_label = ttk.Label(stats_frame, text="Nombre total de produits: -", font=('Arial', 12))
        self.total_products_label.pack(anchor='w', pady=2)
        
        self.total_stock_label = ttk.Label(stats_frame, text="Stock total: -", font=('Arial', 12))
        self.total_stock_label.pack(anchor='w', pady=2)
        
        self.total_benefit_label = ttk.Label(stats_frame, text="Bénéfice total: -", font=('Arial', 12, 'bold'), foreground='green')
        self.total_benefit_label.pack(anchor='w', pady=2)
        
        # Détail par produit
        detail_frame = ttk.LabelFrame(dashboard_frame, text="Bénéfices par Produit", padding=10)
        detail_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        columns_dash = ('Produit', 'Stock Restant', 'Quantité Vendue', 'Bénéfice Total')
        self.dashboard_tree = ttk.Treeview(detail_frame, columns=columns_dash, show='headings', height=15)
        
        for col in columns_dash:
            self.dashboard_tree.heading(col, text=col)
            self.dashboard_tree.column(col, width=200)
        
        scrollbar_dash = ttk.Scrollbar(detail_frame, orient='vertical', command=self.dashboard_tree.yview)
        self.dashboard_tree.configure(yscrollcommand=scrollbar_dash.set)
        
        self.dashboard_tree.pack(side='left', fill='both', expand=True)
        scrollbar_dash.pack(side='right', fill='y')
        
        # Bouton de rafraîchissement
        ttk.Button(dashboard_frame, text="Rafraîchir", command=self.refresh_dashboard).pack(pady=10)
    
    def create_history_tab(self):
        """Crée l'onglet historique des ventes"""
        history_frame = ttk.Frame(self.notebook)
        self.notebook.add(history_frame, text="Historique des Ventes")
        
        # Frame pour les boutons d'action
        actions_frame = ttk.Frame(history_frame)
        actions_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(actions_frame, text="Modifier Vente Sélectionnée", 
                  command=self.modify_sale).pack(side='left', padx=5)
        ttk.Button(actions_frame, text="Supprimer Vente Sélectionnée", 
                  command=self.delete_sale).pack(side='left', padx=5)
        ttk.Button(actions_frame, text="Exporter Historique PDF", 
                  command=self.export_sales_pdf).pack(side='right', padx=5)
        
        # Treeview pour l'historique (AVEC ACHETEUR)
        columns_hist = ('ID', 'Date', 'Produit', 'Acheteur', 'Quantité', 'Prix de Revient', 'Prix Vente', 'Bénéfice')
        self.history_tree = ttk.Treeview(history_frame, columns=columns_hist, show='headings', height=18)
        
        for col in columns_hist:
            self.history_tree.heading(col, text=col)
            if col == 'ID':
                self.history_tree.column(col, width=50)
            elif col == 'Acheteur':
                self.history_tree.column(col, width=150)
            else:
                self.history_tree.column(col, width=120)
        
        scrollbar_hist = ttk.Scrollbar(history_frame, orient='vertical', command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar_hist.set)
        
        self.history_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar_hist.pack(side='right', fill='y', pady=10)
    
    def add_product(self):
        """Ajoute un nouveau produit"""
        try:
            designation = self.designation_entry.get().strip()
            description = self.description_entry.get().strip()
            stock = int(self.stock_entry.get())
            prix_revient = float(self.prix_revient_entry.get())
            
            if not designation:
                messagebox.showerror("Erreur", "La désignation est obligatoire")
                return
            
            self.cursor.execute('''
                INSERT INTO produits (designation, description, stock_initial, stock_actuel, prix_revient)
                VALUES (?, ?, ?, ?, ?)
            ''', (designation, description, stock, stock, prix_revient))
            
            self.conn.commit()
            messagebox.showinfo("Succès", "Produit ajouté avec succès")
            
            # Vider les champs
            self.designation_entry.delete(0, tk.END)
            self.description_entry.delete(0, tk.END)
            self.stock_entry.delete(0, tk.END)
            self.prix_revient_entry.delete(0, tk.END)
            
            self.refresh_all()
            
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer des valeurs numériques valides")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'ajout: {str(e)}")
    
    def modify_product(self):
        """Modifie le produit sélectionné"""
        selection = self.products_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un produit à modifier")
            return
        
        # Récupérer les informations du produit sélectionné
        item = self.products_tree.item(selection[0])
        product_id, designation, description, stock_actuel, prix_revient = item['values']
        
        # Créer une fenêtre de modification
        self.create_modify_window(product_id, designation, description, stock_actuel, prix_revient)
    
    def create_modify_window(self, product_id, designation, description, stock_actuel, prix_revient):
        """Crée la fenêtre de modification du produit"""
        modify_window = tk.Toplevel(self.root)
        modify_window.title(f"Modifier le produit: {designation}")
        modify_window.geometry("400x300")
        modify_window.configure(bg='#f0f0f0')
        modify_window.transient(self.root)
        modify_window.grab_set()
        
        # Frame principal
        main_frame = ttk.LabelFrame(modify_window, text="Modification du Produit", padding=20)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Champs de modification
        ttk.Label(main_frame, text="Désignation:").grid(row=0, column=0, sticky='w', pady=5)
        designation_var = tk.StringVar(value=designation)
        designation_entry = ttk.Entry(main_frame, textvariable=designation_var, width=30)
        designation_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(main_frame, text="Description:").grid(row=1, column=0, sticky='w', pady=5)
        description_var = tk.StringVar(value=description)
        description_entry = ttk.Entry(main_frame, textvariable=description_var, width=30)
        description_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(main_frame, text="Stock Actuel:").grid(row=2, column=0, sticky='w', pady=5)
        stock_var = tk.StringVar(value=str(stock_actuel))
        stock_entry = ttk.Entry(main_frame, textvariable=stock_var, width=30)
        stock_entry.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(main_frame, text="Prix de Revient:").grid(row=3, column=0, sticky='w', pady=5)
        prix_var = tk.StringVar(value=str(prix_revient))
        prix_entry = ttk.Entry(main_frame, textvariable=prix_var, width=30)
        prix_entry.grid(row=3, column=1, padx=5, pady=5)
        
        # Avertissement sur les ventes
        self.cursor.execute('SELECT COUNT(*) FROM ventes WHERE produit_id = ?', (product_id,))
        sales_count = self.cursor.fetchone()[0]
        
        if sales_count > 0:
            warning_frame = ttk.Frame(main_frame)
            warning_frame.grid(row=4, column=0, columnspan=2, pady=10)
            
            warning_label = ttk.Label(warning_frame, 
                                    text=f"⚠️ Attention: Ce produit a {sales_count} vente(s) enregistrée(s)",
                                    foreground='orange', font=('Arial', 9, 'bold'))
            warning_label.pack()
            
            info_label = ttk.Label(warning_frame,
                                 text="Modifier le prix affectera les calculs de bénéfices futurs",
                                 foreground='gray', font=('Arial', 8))
            info_label.pack()
        
        # Boutons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        def save_changes():
            try:
                new_designation = designation_var.get().strip()
                new_description = description_var.get().strip()
                new_stock = int(stock_var.get())
                new_prix = float(prix_var.get())
                
                if not new_designation:
                    messagebox.showerror("Erreur", "La désignation est obligatoire")
                    return
                
                if new_stock < 0:
                    messagebox.showerror("Erreur", "Le stock ne peut pas être négatif")
                    return
                
                # Mettre à jour en base
                self.cursor.execute('''
                    UPDATE produits 
                    SET designation = ?, description = ?, stock_actuel = ?, prix_revient = ?
                    WHERE id = ?
                ''', (new_designation, new_description, new_stock, new_prix, product_id))
                
                self.conn.commit()
                messagebox.showinfo("Succès", "Produit modifié avec succès")
                modify_window.destroy()
                self.refresh_all()
                
            except ValueError:
                messagebox.showerror("Erreur", "Veuillez entrer des valeurs numériques valides")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la modification: {str(e)}")
        
        ttk.Button(buttons_frame, text="Sauvegarder", command=save_changes).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Annuler", command=modify_window.destroy).pack(side='left', padx=5)
        
        # Focus sur le premier champ
        designation_entry.focus()
    
    def create_utilities_tab(self):
        """Crée l'onglet des utilitaires et exports"""
        utilities_frame = ttk.Frame(self.notebook)
        self.notebook.add(utilities_frame, text="Export & Utilitaires")
        
        # Section Export
        export_frame = ttk.LabelFrame(utilities_frame, text="Exports PDF", padding=20)
        export_frame.pack(fill='x', padx=10, pady=10)
        
        if REPORTLAB_AVAILABLE:
            ttk.Label(export_frame, text="Générer des rapports PDF de vos données:", 
                     font=('Arial', 11)).pack(anchor='w', pady=(0, 10))
            
            buttons_export = ttk.Frame(export_frame)
            buttons_export.pack(fill='x')
            
            ttk.Button(buttons_export, text="📄 Exporter Liste des Produits", 
                      command=self.export_products_pdf).pack(side='left', padx=5)
            ttk.Button(buttons_export, text="📊 Exporter Historique des Ventes", 
                      command=self.export_sales_pdf).pack(side='left', padx=5)
        else:
            ttk.Label(export_frame, text="❌ Export PDF non disponible", 
                     font=('Arial', 11, 'bold'), foreground='red').pack(anchor='w')
            ttk.Label(export_frame, text="Pour activer l'export PDF, installez reportlab:", 
                     font=('Arial', 10)).pack(anchor='w', pady=(5, 0))
            ttk.Label(export_frame, text="pip install reportlab", 
                     font=('Courier', 10), foreground='blue').pack(anchor='w', pady=(2, 10))
            
            # Alternatives d'export
            ttk.Label(export_frame, text="Alternatives disponibles:", 
                     font=('Arial', 10, 'bold')).pack(anchor='w', pady=(10, 5))
            
            buttons_alt = ttk.Frame(export_frame)
            buttons_alt.pack(fill='x')
            
            ttk.Button(buttons_alt, text="📝 Exporter Produits (CSV)", 
                      command=self.export_products_csv).pack(side='left', padx=5)
            ttk.Button(buttons_alt, text="📈 Exporter Ventes (CSV)", 
                      command=self.export_sales_csv).pack(side='left', padx=5)
    
    def modify_sale(self):
        """Modifie la vente sélectionnée"""
        selection = self.history_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner une vente à modifier")
            return
        
        # Récupérer les informations de la vente (AVEC ACHETEUR)
        item = self.history_tree.item(selection[0])
        sale_id, date, produit, acheteur, quantite, prix_revient, prix_vente, benefice = item['values']
        
        # Créer fenêtre de modification
        self.create_modify_sale_window(sale_id, date, produit, acheteur, quantite, prix_revient, prix_vente)
    
    def create_modify_sale_window(self, sale_id, date, produit, acheteur, quantite, prix_revient, prix_vente):
        """Crée la fenêtre de modification de vente"""
        modify_window = tk.Toplevel(self.root)
        modify_window.title(f"Modifier la vente: {produit}")
        modify_window.geometry("450x400")
        modify_window.configure(bg='#f0f0f0')
        modify_window.transient(self.root)
        modify_window.grab_set()
        
        main_frame = ttk.LabelFrame(modify_window, text="Modification de la Vente", padding=20)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Informations non modifiables
        ttk.Label(main_frame, text=f"Date: {date}", font=('Arial', 10, 'bold')).pack(anchor='w', pady=2)
        ttk.Label(main_frame, text=f"Produit: {produit}", font=('Arial', 10, 'bold')).pack(anchor='w', pady=2)
        
        # Prix de revient (NON MODIFIABLE - affiché pour information)
        prix_revient_clean = float(prix_revient.replace(' DA', ''))
        ttk.Label(main_frame, text=f"Prix de revient: {prix_revient_clean:.2f} DA", 
                 font=('Arial', 10), foreground='blue').pack(anchor='w', pady=(10, 2))
        ttk.Label(main_frame, text="(Prix de revient fixé par le produit)", 
                 font=('Arial', 8), foreground='gray').pack(anchor='w', pady=(0, 10))
        
        # Champs modifiables
        ttk.Label(main_frame, text="Acheteur:").pack(anchor='w', pady=(10, 2))
        acheteur_var = tk.StringVar(value=acheteur if acheteur else "")
        acheteur_entry = ttk.Entry(main_frame, textvariable=acheteur_var, width=40)
        acheteur_entry.pack(anchor='w', pady=2)
        
        ttk.Label(main_frame, text="Quantité vendue:").pack(anchor='w', pady=(10, 2))
        quantite_var = tk.StringVar(value=str(quantite))
        quantite_entry = ttk.Entry(main_frame, textvariable=quantite_var, width=20)
        quantite_entry.pack(anchor='w', pady=2)
        
        ttk.Label(main_frame, text="Prix de vente unitaire:").pack(anchor='w', pady=(10, 2))
        # Nettoyer le prix de vente (enlever " DA")
        prix_vente_clean = float(prix_vente.replace(' DA', ''))
        prix_vente_var = tk.StringVar(value=str(prix_vente_clean))
        prix_vente_entry = ttk.Entry(main_frame, textvariable=prix_vente_var, width=20)
        prix_vente_entry.pack(anchor='w', pady=2)
        
        # Informations calculées
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill='x', pady=15)
        
        benefice_label = ttk.Label(info_frame, text="", foreground='green', font=('Arial', 10, 'bold'))
        benefice_label.pack(anchor='w')
        
        def update_benefice(*args):
            try:
                new_qty = int(quantite_var.get())
                new_prix = float(prix_vente_var.get())
                new_benefice = (new_prix - prix_revient_clean) * new_qty
                color = 'green' if new_benefice > 0 else 'red'
                benefice_label.config(text=f"Nouveau bénéfice: {new_benefice:.2f} DA", foreground=color)
            except ValueError:
                benefice_label.config(text="Bénéfice: -", foreground='black')
        
        quantite_var.trace('w', update_benefice)
        prix_vente_var.trace('w', update_benefice)
        update_benefice()
        
        # Boutons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(pady=20)
        
        def save_sale_changes():
            try:
                new_acheteur = acheteur_var.get().strip()
                new_quantite = int(quantite_var.get())
                new_prix_vente = float(prix_vente_var.get())
                
                if new_quantite <= 0:
                    messagebox.showerror("Erreur", "La quantité doit être positive")
                    return
                
                # Calculer nouveau bénéfice
                new_benefice = (new_prix_vente - prix_revient_clean) * new_quantite
                
                # Récupérer l'ancienne quantité pour ajuster le stock
                self.cursor.execute('SELECT quantite, produit_id FROM ventes WHERE id = ?', (sale_id,))
                old_qty, product_id = self.cursor.fetchone()
                
                stock_diff = old_qty - new_quantite  # Différence à ajouter au stock
                
                # Vérifier que le stock est suffisant si on augmente la quantité
                if stock_diff < 0:  # On vend plus qu'avant
                    self.cursor.execute('SELECT stock_actuel FROM produits WHERE id = ?', (product_id,))
                    stock_actuel = self.cursor.fetchone()[0]
                    if stock_actuel < abs(stock_diff):
                        messagebox.showerror("Erreur", f"Stock insuffisant. Stock disponible: {stock_actuel}")
                        return
                
                # Mettre à jour la vente (AVEC ACHETEUR)
                self.cursor.execute('''
                    UPDATE ventes 
                    SET quantite = ?, prix_vente = ?, benefice = ?, acheteur = ?
                    WHERE id = ?
                ''', (new_quantite, new_prix_vente, new_benefice, new_acheteur, sale_id))
                
                # Ajuster le stock du produit
                self.cursor.execute('''
                    UPDATE produits 
                    SET stock_actuel = stock_actuel + ?
                    WHERE id = ?
                ''', (stock_diff, product_id))
                
                self.conn.commit()
                messagebox.showinfo("Succès", "Vente modifiée avec succès")
                modify_window.destroy()
                self.refresh_all()
                
            except ValueError:
                messagebox.showerror("Erreur", "Veuillez entrer des valeurs numériques valides")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la modification: {str(e)}")
        
        ttk.Button(buttons_frame, text="Sauvegarder", command=save_sale_changes).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Annuler", command=modify_window.destroy).pack(side='left', padx=5)
        
        # Focus sur le premier champ
        acheteur_entry.focus()
    
    def delete_sale(self):
        """Supprime la vente sélectionnée"""
        selection = self.history_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner une vente à supprimer")
            return
        
        item = self.history_tree.item(selection[0])
        sale_id, date, produit, acheteur, quantite = item['values'][:5]
        
        result = messagebox.askyesno("Confirmation", 
                                   f"Supprimer la vente de {quantite} {produit} du {date}?\n"
                                   f"Acheteur: {acheteur if acheteur else 'Non spécifié'}\n\n"
                                   f"Le stock sera remis à jour (+{quantite})")
        if not result:
            return
        
        try:
            # Récupérer l'ID du produit et la quantité
            self.cursor.execute('SELECT produit_id, quantite FROM ventes WHERE id = ?', (sale_id,))
            product_id, qty = self.cursor.fetchone()
            
            # Supprimer la vente
            self.cursor.execute('DELETE FROM ventes WHERE id = ?', (sale_id,))
            
            # Remettre le stock
            self.cursor.execute('UPDATE produits SET stock_actuel = stock_actuel + ? WHERE id = ?', 
                              (qty, product_id))
            
            self.conn.commit()
            messagebox.showinfo("Succès", f"Vente supprimée et stock remis à jour (+{qty})")
            self.refresh_all()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la suppression: {str(e)}")
            self.conn.rollback()
    
    def export_products_pdf(self):
        """Exporte la liste des produits en PDF"""
        if not REPORTLAB_AVAILABLE:
            messagebox.showerror("Erreur", "ReportLab n'est pas installé. Utilisez l'export CSV.")
            return
            
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                title="Sauvegarder le rapport des produits"
            )
            if not filename:
                return
            
            doc = SimpleDocTemplate(filename, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Titre
            title = Paragraph("RAPPORT DES PRODUITS", styles['Title'])
            story.append(title)
            story.append(Spacer(1, 12))
            
            # Date du rapport
            date_str = datetime.now().strftime("%d/%m/%Y à %H:%M")
            date_para = Paragraph(f"Généré le {date_str}", styles['Normal'])
            story.append(date_para)
            story.append(Spacer(1, 20))
            
            # Récupérer les données
            self.cursor.execute('SELECT designation, description, stock_actuel, prix_revient FROM produits')
            products = self.cursor.fetchall()
            
            if products:
                # Créer le tableau
                data = [['Désignation', 'Description', 'Stock Actuel', 'Prix de Revient']]
                for product in products:
                    designation, description, stock, prix = product
                    data.append([designation, description or '-', str(stock), f"{prix:.2f} DA"])
                
                table = Table(data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 14),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(table)
            else:
                story.append(Paragraph("Aucun produit trouvé.", styles['Normal']))
            
            doc.build(story)
            messagebox.showinfo("Succès", f"Rapport exporté: {filename}")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'export: {str(e)}")
    
    def export_sales_pdf(self):
        """Exporte l'historique des ventes en PDF (AVEC ACHETEUR)"""
        if not REPORTLAB_AVAILABLE:
            messagebox.showerror("Erreur", "ReportLab n'est pas installé. Utilisez l'export CSV.")
            return
            
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                title="Sauvegarder l'historique des ventes"
            )
            if not filename:
                return
            
            doc = SimpleDocTemplate(filename, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Titre
            title = Paragraph("HISTORIQUE DES VENTES", styles['Title'])
            story.append(title)
            story.append(Spacer(1, 12))
            
            # Date du rapport
            date_str = datetime.now().strftime("%d/%m/%Y à %H:%M")
            date_para = Paragraph(f"Généré le {date_str}", styles['Normal'])
            story.append(date_para)
            story.append(Spacer(1, 20))
            
            # Récupérer les données (AVEC ACHETEUR)
            query = '''
                SELECT v.date_vente, p.designation, v.acheteur, v.quantite, v.prix_revient, v.prix_vente, v.benefice
                FROM ventes v
                JOIN produits p ON v.produit_id = p.id
                ORDER BY v.date_vente DESC
            '''
            self.cursor.execute(query)
            sales = self.cursor.fetchall()
            
            if sales:
                # Statistiques globales
                total_benefice = sum(sale[6] for sale in sales)
                stats_para = Paragraph(f"<b>Bénéfice total: {total_benefice:.2f} DA | Nombre de ventes: {len(sales)}</b>", styles['Normal'])
                story.append(stats_para)
                story.append(Spacer(1, 15))
                
                # Créer le tableau (AVEC ACHETEUR)
                data = [['Date', 'Produit', 'Acheteur', 'Qté', 'Prix Rev.', 'Prix Vente', 'Bénéfice']]
                for sale in sales:
                    date, produit, acheteur, qty, prix_revient, prix_vente, benefice = sale
                    # Formater la date
                    date_obj = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                    date_formatted = date_obj.strftime("%d/%m/%Y")
                    
                    data.append([
                        date_formatted, 
                        produit, 
                        acheteur if acheteur else '-',
                        str(qty), 
                        f"{prix_revient:.2f} DA", 
                        f"{prix_vente:.2f} DA", 
                        f"{benefice:.2f} DA"
                    ])
                
                table = Table(data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 8)
                ]))
                story.append(table)
            else:
                story.append(Paragraph("Aucune vente trouvée.", styles['Normal']))
            
            doc.build(story)
            messagebox.showinfo("Succès", f"Historique exporté: {filename}")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'export: {str(e)}")
    
    def export_products_csv(self):
        """Exporte la liste des produits en CSV"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                title="Sauvegarder la liste des produits"
            )
            if not filename:
                return
            
            self.cursor.execute('SELECT designation, description, stock_actuel, prix_revient FROM produits')
            products = self.cursor.fetchall()
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("Désignation,Description,Stock Actuel,Prix de Revient\n")
                for product in products:
                    designation, description, stock, prix = product
                    description = description or ''
                    f.write(f'"{designation}","{description}",{stock},{prix:.2f}\n')
            
            messagebox.showinfo("Succès", f"Liste des produits exportée: {filename}")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'export: {str(e)}")
    
    def export_sales_csv(self):
        """Exporte l'historique des ventes en CSV (AVEC ACHETEUR)"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                title="Sauvegarder l'historique des ventes"
            )
            if not filename:
                return
            
            query = '''
                SELECT v.date_vente, p.designation, v.acheteur, v.quantite, v.prix_revient, v.prix_vente, v.benefice
                FROM ventes v
                JOIN produits p ON v.produit_id = p.id
                ORDER BY v.date_vente DESC
            '''
            self.cursor.execute(query)
            sales = self.cursor.fetchall()
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("Date,Produit,Acheteur,Quantité,Prix de Revient,Prix Vente,Bénéfice\n")
                for sale in sales:
                    date, produit, acheteur, qty, prix_revient, prix_vente, benefice = sale
                    acheteur = acheteur if acheteur else ''
                    f.write(f'"{date}","{produit}","{acheteur}",{qty},{prix_revient:.2f},{prix_vente:.2f},{benefice:.2f}\n')
            
            messagebox.showinfo("Succès", f"Historique des ventes exporté: {filename}")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'export: {str(e)}")
    
    def delete_product(self):
        """Supprime le produit sélectionné"""
        selection = self.products_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un produit à supprimer")
            return
        
        # Récupérer les informations du produit sélectionné
        item = self.products_tree.item(selection[0])
        product_id = item['values'][0]
        product_name = item['values'][1]
        
        # Vérifier s'il y a des ventes pour ce produit
        self.cursor.execute('SELECT COUNT(*) FROM ventes WHERE produit_id = ?', (product_id,))
        sales_count = self.cursor.fetchone()[0]
        
        if sales_count > 0:
            # Produit avec historique de ventes - demander confirmation
            message = (f"Le produit '{product_name}' a {sales_count} vente(s) enregistrée(s).\n\n"
                      f"⚠️ ATTENTION: Supprimer ce produit effacera également:\n"
                      f"• Toutes les ventes associées ({sales_count} vente(s))\n"
                      f"• L'historique des bénéfices\n\n"
                      f"Cette action est irréversible. Voulez-vous continuer?")
            
            result = messagebox.askyesno("Confirmation de suppression", message, icon='warning')
            if not result:
                return
            
            # Supprimer d'abord les ventes
            self.cursor.execute('DELETE FROM ventes WHERE produit_id = ?', (product_id,))
        else:
            # Produit sans ventes - confirmation simple
            result = messagebox.askyesno("Confirmation", 
                                       f"Êtes-vous sûr de vouloir supprimer le produit '{product_name}'?")
            if not result:
                return
        
        try:
            # Supprimer le produit
            self.cursor.execute('DELETE FROM produits WHERE id = ?', (product_id,))
            self.conn.commit()
            
            messagebox.showinfo("Succès", f"Produit '{product_name}' supprimé avec succès")
            self.refresh_all()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la suppression: {str(e)}")
            self.conn.rollback()
    
    def on_product_selected(self, event):
        """Met à jour les informations quand un produit est sélectionné"""
        selection = self.product_combo.get()
        if selection:
            product_id = selection.split(' - ')[0]
            self.cursor.execute('SELECT stock_actuel, prix_revient FROM produits WHERE id = ?', (product_id,))
            result = self.cursor.fetchone()
            if result:
                stock, prix_revient = result
                self.stock_info_label.config(text=f"Stock disponible: {stock}")
                self.prix_revient_info_label.config(text=f"Prix de revient: {prix_revient:.2f} DA")
    
    def calculate_preview_benefit(self, event=None):
        """Calcule et affiche le bénéfice prévu"""
        try:
            selection = self.product_combo.get()
            if not selection:
                return
            
            quantity = self.quantity_sale_entry.get()
            prix_vente = self.prix_vente_entry.get()
            
            if quantity and prix_vente:
                quantity = int(quantity)
                prix_vente = float(prix_vente)
                
                product_id = selection.split(' - ')[0]
                self.cursor.execute('SELECT prix_revient FROM produits WHERE id = ?', (product_id,))
                result = self.cursor.fetchone()
                if result:
                    prix_revient = result[0]
                    benefice_unitaire = prix_vente - prix_revient
                    benefice_total = benefice_unitaire * quantity
                    
                    color = 'green' if benefice_total > 0 else 'red'
                    self.benefice_preview_label.config(
                        text=f"Bénéfice prévu: {benefice_total:.2f} DA ({benefice_unitaire:.2f} DA/unité)",
                        foreground=color
                    )
        except ValueError:
            self.benefice_preview_label.config(text="Bénéfice prévu: -", foreground='black')
    
    def record_sale(self):
        """Enregistre une vente (AVEC ACHETEUR)"""
        try:
            selection = self.product_combo.get()
            if not selection:
                messagebox.showerror("Erreur", "Veuillez sélectionner un produit")
                return
            
            # Vérifier qu'il y a des produits disponibles
            if not self.product_combo['values']:
                messagebox.showwarning("Attention", "Aucun produit disponible pour la vente")
                return
            
            product_id = int(selection.split(' - ')[0])
            quantity = int(self.quantity_sale_entry.get())
            prix_vente = float(self.prix_vente_entry.get())
            acheteur = self.acheteur_entry.get().strip()  # NOUVEAU CHAMP
            
            # Vérifier le stock
            self.cursor.execute('SELECT stock_actuel, prix_revient FROM produits WHERE id = ?', (product_id,))
            result = self.cursor.fetchone()
            if not result:
                messagebox.showerror("Erreur", "Produit non trouvé")
                return
            
            stock_actuel, prix_revient = result
            if stock_actuel < quantity:
                messagebox.showerror("Erreur", f"Stock insuffisant. Stock disponible: {stock_actuel}")
                return
            
            # Calculer le bénéfice
            benefice_unitaire = prix_vente - prix_revient
            benefice_total = benefice_unitaire * quantity
            
            # Enregistrer la vente (AVEC ACHETEUR)
            date_vente = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute('''
                INSERT INTO ventes (produit_id, quantite, prix_revient, prix_vente, benefice, acheteur, date_vente)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (product_id, quantity, prix_revient, prix_vente, benefice_total, acheteur, date_vente))
            
            # Mettre à jour le stock
            nouveau_stock = stock_actuel - quantity
            self.cursor.execute('UPDATE produits SET stock_actuel = ? WHERE id = ?', (nouveau_stock, product_id))
            
            self.conn.commit()
            messagebox.showinfo("Succès", f"Vente enregistrée!\nBénéfice: {benefice_total:.2f} DA")
            
            # Vider les champs
            self.quantity_sale_entry.delete(0, tk.END)
            self.prix_vente_entry.delete(0, tk.END)
            self.acheteur_entry.delete(0, tk.END)  # NOUVEAU CHAMP À VIDER
            
            self.refresh_all()
            
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer des valeurs numériques valides")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement: {str(e)}")
    
    def refresh_all(self):
        """Rafraîchit tous les affichages"""
        self.refresh_products()
        self.refresh_product_combo()
        self.refresh_dashboard()
        self.refresh_history()
    
    def refresh_products(self):
        """Rafraîchit la liste des produits"""
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        self.cursor.execute('SELECT id, designation, description, stock_actuel, prix_revient FROM produits')
        for row in self.cursor.fetchall():
            self.products_tree.insert('', 'end', values=row)
    
    def refresh_product_combo(self):
        """Rafraîchit la combobox des produits"""
        self.cursor.execute('SELECT id, designation FROM produits WHERE stock_actuel > 0')
        products = [f"{row[0]} - {row[1]}" for row in self.cursor.fetchall()]
        self.product_combo['values'] = products
        
        # Vider la sélection actuelle
        self.product_combo.set('')
        
        # Désactiver/activer la combobox selon la disponibilité des produits
        if not products:
            self.product_combo.config(state='disabled')
            # Réinitialiser les informations
            self.stock_info_label.config(text="Aucun produit disponible")
            self.prix_revient_info_label.config(text="Ajoutez des produits pour commencer")
            self.benefice_preview_label.config(text="", foreground='black')
        else:
            self.product_combo.config(state='readonly')
    
    def refresh_dashboard(self):
        """Rafraîchit le tableau de bord"""
        # Statistiques générales
        self.cursor.execute('SELECT COUNT(*) FROM produits')
        total_products = self.cursor.fetchone()[0]
        
        self.cursor.execute('SELECT SUM(stock_actuel) FROM produits')
        total_stock = self.cursor.fetchone()[0] or 0
        
        self.cursor.execute('SELECT SUM(benefice) FROM ventes')
        total_benefit = self.cursor.fetchone()[0] or 0
        
        self.total_products_label.config(text=f"Nombre total de produits: {total_products}")
        self.total_stock_label.config(text=f"Stock total: {total_stock}")
        self.total_benefit_label.config(text=f"Bénéfice total: {total_benefit:.2f} DA")
        
        # Détail par produit
        for item in self.dashboard_tree.get_children():
            self.dashboard_tree.delete(item)
        
        query = '''
            SELECT p.designation, p.stock_actuel, 
                   COALESCE(SUM(v.quantite), 0) as quantite_vendue,
                   COALESCE(SUM(v.benefice), 0) as benefice_total
            FROM produits p
            LEFT JOIN ventes v ON p.id = v.produit_id
            GROUP BY p.id, p.designation, p.stock_actuel
        '''
        
        self.cursor.execute(query)
        for row in self.cursor.fetchall():
            designation, stock, qty_vendue, benefice = row
            self.dashboard_tree.insert('', 'end', values=(
                designation, stock, int(qty_vendue), f"{benefice:.2f} DA"
            ))
    
    def refresh_history(self):
        """Rafraîchit l'historique des ventes (AVEC ACHETEUR)"""
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        query = '''
            SELECT v.id, v.date_vente, p.designation, v.acheteur, v.quantite, v.prix_revient, v.prix_vente, v.benefice
            FROM ventes v
            JOIN produits p ON v.produit_id = p.id
            ORDER BY v.date_vente DESC
        '''
        
        self.cursor.execute(query)
        for row in self.cursor.fetchall():
            sale_id, date, designation, acheteur, qty, prix_revient, prix_vente, benefice = row
            self.history_tree.insert('', 'end', values=(
                sale_id, date, designation, acheteur if acheteur else '-', qty, 
                f"{prix_revient:.2f} DA", f"{prix_vente:.2f} DA", f"{benefice:.2f} DA"
            ))
    
    def run(self):
        """Lance l'application"""
        self.root.mainloop()
        self.conn.close()

if __name__ == "__main__":
    app = AtelierManager()
    app.run()