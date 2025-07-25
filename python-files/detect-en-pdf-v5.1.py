import os
import re
import csv
import time
import threading
import queue
import shutil
import platform
import subprocess
import webbrowser
from urllib.parse import quote
from urllib.request import pathname2url
from collections import defaultdict
from tkinter import *
from tkinter import ttk, filedialog, messagebox, font
import PyPDF2
import nltk
from langdetect import detect, LangDetectException, detect_langs
from tqdm import tqdm
import pyautogui

'''
Dans le conda prompt :
pyinstaller --onefile --windowed --exclude-module tkinter --add-data "skips.csv;." detect-en-pdf-v5.1.py

'''
# Télécharger les ressources nécessaires pour nltk
nltk.download('punkt', quiet=True)

# Ajouter un mapping des langues
LANGUAGE_NAMES = {
    'de': 'German', 'ar': 'Arabic', 'bg': 'Bulgarian', 'hr': 'Croatian', 'en': 'English',
    'fr': 'French', 'es': 'Spanish', 'it': 'Italian', 'pt': 'Portuguese', 'nl': 'Dutch',
    'la': 'Latin', 'zh': 'Chinese', 'ko': 'Korean', 'ru': 'Russian', 'ja': 'Japanese',
    'sv': 'Swedish', 'fi': 'Finnish', 'no': 'Norwegian', 'da': 'Danish', 'pl': 'Polish',
    'cs': 'Czech', 'sk': 'Slovak', 'ro': 'Romanian', 'el': 'Greek', 'tr': 'Turkish',
    'he': 'Hebrew', 'fa': 'Persian', 'hi': 'Hindi', 'bn': 'Bengali', 'ur': 'Urdu',
    'ta': 'Tamil', 'te': 'Telugu', 'th': 'Thai', 'vi': 'Vietnamese', 'id': 'Indonesian',
    'ms': 'Malay', 'sw': 'Swahili', 'am': 'Amharic', 'zu': 'Zulu', 'xh': 'Xhosa', 'ha': 'Hausa',
    'yo': 'Yoruba', 'ig': 'Igbo', 'uk': 'Ukrainian'}

# Charger les passages à ignorer
def load_skips():
    skips = defaultdict(set)
    if os.path.exists('skips.csv'):
        with open('skips.csv', 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)  # Skip header
            for row in reader:
                if len(row) >= 2:
                    skips[row[0]].add(row[1])
    return skips

def detect_main_language(text, max_chars=10000):
    if not text.strip():
        return "Unknown"
    
    try:
        truncated_text = text[:max_chars]
        lang_probs = detect_langs(truncated_text)
        main_lang = lang_probs[0].lang
        return LANGUAGE_NAMES.get(main_lang, main_lang)
    except LangDetectException:
        return "Unknown"
    except Exception as e:
        print(f"Language detection error: {str(e)}")
        return "Unknown"
    
def extract_text_from_pdf(pdf_path):
    text_per_page = []
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text = page.extract_text() or ""
                text_per_page.append(text)
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {str(e)}")
    return text_per_page

def detect_english_passages(pdf_path, skip_set, min_words=4):  # Changé de 3 à 4
    english_sections = []
    
    # Liste de mots français courants à exclure
    french_words = {"le", "la", "les", "de", "des", "du", "à", "au", "aux", 
                    "et", "ou", "où", "qui", "que", "quoi", "dans", "en", 
                    "sur", "sous", "avec", "pour", "par", "chez", "mais", 
                    "donc", "or", "ni", "car", "si", "rincer", "bouche", "oreille", "oeil", "yeux"}
    
    try:
        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            filename = os.path.basename(pdf_path)
            
            for page_num in tqdm(range(len(pdf_reader.pages)), 
                                desc=f"Analyzing {filename}", 
                                leave=False):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                
                if not text:
                    continue
                    
                clean_text = re.sub(r'\s+', ' ', text).strip()
                sentences = nltk.sent_tokenize(clean_text)
                
                for sentence in sentences:
                    words = sentence.split()
                    if len(words) < min_words:
                        continue
                    
                    if sentence in skip_set:
                        continue
                    
                    # Vérifier si la phrase contient des mots français courants
                    if any(word.lower() in french_words for word in words):
                        continue
                    
                    try:
                        lang = detect(sentence)
                        if lang == 'en':
                            start_index = clean_text.find(sentence)
                            end_index = start_index + len(sentence)
                            english_sections.append((
                                page_num + 1,
                                sentence,
                                start_index,
                                end_index
                            ))
                    except LangDetectException:
                        continue
    except Exception as e:
        print(f"Error analyzing {pdf_path}: {str(e)}")
                    
    return english_sections

class PDFAnalyzerApp:
    def __init__(self, root):
        self.full_passages = {}
        self.root = root
        self.root.title("PDF Translation Analyzer")
        self.root.geometry("1280x780")
        self.root.configure(bg="#f5f7fa")
        
        # Définir les répertoires de travail
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.original_dir = os.path.join(base_dir, "ORIGINAL PDF FILES")
        self.ok_dir = os.path.join(base_dir, "PDF FILES OK")
        self.review_dir = os.path.join(base_dir, "PDF FILES TO REVIEW")
        
        # Créer les répertoires s'ils n'existent pas
        os.makedirs(self.original_dir, exist_ok=True)
        os.makedirs(self.ok_dir, exist_ok=True)
        os.makedirs(self.review_dir, exist_ok=True)
        
        # Charger les skips
        self.skips = load_skips()
        self.skipped_passages = []
        
        # Configurer les polices
        self.title_font = font.Font(family="Segoe UI", size=14, weight="bold")
        self.header_font = font.Font(family="Segoe UI", size=10, weight="bold")
        self.base_font = font.Font(family="Segoe UI", size=10)
        
        # Créer le style
        self.setup_styles()
        
        # Barre d'outils supérieure
        self.create_toolbar()
        
        # Variables pour l'alternance de couleurs
        self.file_color_index = {}
        self.next_color_index = 0
        
        # Variables pour le regroupement par fichier
        self.current_filename = None
        self.first_passage = True
        
        # Créer le notebook pour les onglets
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=BOTH, expand=True, padx=0, pady=0)
        
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # Créer les onglets
        self.analysis_tab = ttk.Frame(self.notebook)
        self.directories_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.analysis_tab, text='ANALYSIS')
        self.notebook.add(self.directories_tab, text='DIRECTORIES')
        
        # Construire l'onglet ANALYSIS
        self.create_analysis_tab()
        
        # Construire l'onglet DIRECTORIES
        self.create_directories_tab()
        
        # Variables pour la gestion des threads
        self.analysis_thread = None
        self.stop_event = threading.Event()
        
        # Barre de progression
        progress_frame = ttk.Frame(root)
        progress_frame.pack(fill=X, padx=20, pady=(0, 10))
        
        self.progress = ttk.Progressbar(
            progress_frame, 
            orient=HORIZONTAL, 
            mode='determinate',
            length=300,
            style='Custom.Horizontal.TProgressbar'
        )
        self.progress.pack(fill=X, expand=True)
        
        # Barre d'état
        self.status_var = StringVar()
        self.status_bar = ttk.Label(
            root, 
            textvariable=self.status_var,
            relief=SUNKEN,
            anchor=W,
            padding=8,
            style='Status.TLabel'
        )
        self.status_bar.pack(side=BOTTOM, fill=X)
        self.status_var.set("Ready")
        
        # Initialiser la file pour la communication entre threads
        self.queue = queue.Queue()
    
    def on_tab_changed(self, event):
        """Rafraîchit les treeviews quand on change d'onglet"""
        current_tab = self.notebook.index(self.notebook.select())
        if current_tab == 1:  # Index de l'onglet DIRECTORIES
            self.refresh_all_directory_trees()
    
    def refresh_all_directory_trees(self):
        """Rafraîchit tous les treeviews de l'onglet DIRECTORIES"""
        if hasattr(self, 'original_tree'):
            self.refresh_directory_tree(self.original_tree, self.original_dir)
        if hasattr(self, 'ok_tree'):
            self.refresh_directory_tree(self.ok_tree, self.ok_dir)
        if hasattr(self, 'review_tree'):
            self.refresh_directory_tree(self.review_tree, self.review_dir)
        
    def create_toolbar(self):
        toolbar = ttk.Frame(self.root, height=40, style='Toolbar.TFrame')
        toolbar.pack(fill=X, padx=0, pady=0)
        
        # Logo et titre
        logo_frame = ttk.Frame(toolbar, style='Toolbar.TFrame')
        logo_frame.pack(side=LEFT, padx=(20, 15), pady=5)
        
        title = ttk.Label(
            logo_frame, 
            text="PDF Translation Analyzer", 
            font=self.title_font,
            style='Toolbar.TLabel'
        )
        title.pack(side=LEFT)
        
        # Version
        version = ttk.Label(
            logo_frame, 
            text="v5.1", 
            font=self.base_font,
            style='Toolbar.TLabel'
        )
        version.pack(side=LEFT, padx=(10, 0), pady=5)
        
        # Boutons de droite
        button_frame = ttk.Frame(toolbar, style='Toolbar.TFrame')
        button_frame.pack(side=RIGHT, padx=20)
        
        # Bouton d'aide
        help_btn = ttk.Button(
            button_frame, 
            text="Help", 
            command=self.show_help,
            style='Toolbar.TButton'
        )
        help_btn.pack(side=RIGHT, padx=(10, 0))
    
    def setup_styles(self):
        style = ttk.Style()
        
        # Style global
        style.theme_use('clam')
        style.configure('.', font=self.base_font)
        
        # Toolbar
        style.configure('Toolbar.TFrame', background='#2c3e50')
        style.configure('Toolbar.TLabel', background='#2c3e50', foreground='white')
        style.configure('Toolbar.TButton', 
                       background='#3498db', 
                       foreground='white',
                       borderwidth=0,
                       focuscolor='#3498db')
        
        # Cartes
        style.configure('Card.TFrame', background='#ffffff', borderwidth=0)
        style.configure('Card.TLabelframe', 
                       background='#ffffff', 
                       borderwidth=1,
                       relief='solid',
                       bordercolor='#e0e0e0')
        style.configure('Card.TLabelframe.Label', 
                       background='#ffffff',
                       foreground='#2c3e50',
                       font=self.header_font)
        
        # Boutons
        style.configure('TButton', 
                       padding=8, 
                       relief='flat', 
                       background='#f5f5f5', 
                       foreground='#333333',
                       borderwidth=0,
                       focuscolor='#f5f5f5')
        style.map('TButton', 
                 background=[('active', '#e0e0e0')],
                 foreground=[('active', '#333333')])
        
        style.configure('Accent.TButton', 
                       background='#3498db', 
                       foreground='white')
        style.map('Accent.TButton', 
                 background=[('active', '#2980b9')],
                 foreground=[('active', 'white')])
        
        style.configure('Red.TButton', 
                       background='#f5f5f5',
                       foreground='#e74c3c')
        style.map('Red.TButton', 
                 background=[('active', '#e0e0e0')],
                 foreground=[('active', '#c0392b')])
        
        style.configure('Green.TButton', 
                       background='#f5f5f5',
                       foreground='#2ecc71')
        style.map('Green.TButton', 
                 background=[('active', '#e0e0e0')],
                 foreground=[('active', '#27ae60')])
        
        # Treeview - CORRECTION: nom de style corrigé
        style.configure('Custom.Treeview', 
                       background='white', 
                       fieldbackground='white', 
                       foreground='#333333',
                       rowheight=28,
                       borderwidth=0)
        style.configure('Custom.Treeview.Heading', 
                       background='#3498db', 
                       foreground='white',
                       padding=8,
                       font=self.header_font)
        style.map('Custom.Treeview', 
                 background=[('selected', '#d6eaf8')],
                 foreground=[('selected', '#333333')])
        
        # Barre de progression
        style.configure('Custom.Horizontal.TProgressbar', 
                       background='#3498db', 
                       troughcolor='#e0e0e0',
                       thickness=12)
        
        # Barre d'état
        style.configure('Status.TLabel', 
                       background='#2c3e50', 
                       foreground='white',
                       font=('Segoe UI', 9))
        
        # Styles pour l'onglet DIRECTORIES
        style.configure('Dir.TLabelframe', background='#ffffff', borderwidth=1)
        style.configure('Dir.TLabeframe.Label', background='#ffffff', foreground='#2c3e50')

    def create_analysis_tab(self):
        # Cadre principal
        main_frame = ttk.Frame(self.analysis_tab, style='Card.TFrame')
        main_frame.pack(fill=BOTH, expand=True, padx=20, pady=(10, 15))
        
        # Cadre gauche (fichiers)
        left_frame = ttk.LabelFrame(
            main_frame, 
            text="📁 PDF Files", 
            padding=(15, 10, 15, 10),
            style='Card.TLabelframe'
        )
        left_frame.pack(side=LEFT, fill=Y, padx=(0, 15), pady=5)
        
        # Boutons de contrôle
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=X, pady=(0, 12))
        
        self.add_btn = ttk.Button(
            btn_frame, 
            text="Add files", 
            command=self.add_files,
            style='Accent.TButton'
        )
        self.add_btn.pack(side=LEFT, fill=X, expand=True, padx=(0, 8))
        
        self.clear_btn = ttk.Button(
            btn_frame, 
            text="Clear List", 
            command=self.clear_files
        )
        self.clear_btn.pack(side=LEFT, fill=X, expand=True)
        
        # Liste des fichiers
        file_list_frame = ttk.Frame(left_frame)
        file_list_frame.pack(fill=BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(file_list_frame)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        self.file_list = Listbox(
            file_list_frame, 
            yscrollcommand=scrollbar.set,
            selectmode=MULTIPLE,
            bg="white",
            relief=SOLID,
            borderwidth=1,
            font=self.base_font
        )
        self.file_list.pack(fill=BOTH, expand=True)
        scrollbar.config(command=self.file_list.yview)
        
        # Bouton d'analyse
        self.analyze_btn = ttk.Button(
            left_frame, 
            text="Start Analysis", 
            command=self.start_analysis,
            style='Accent.TButton'
        )
        self.analyze_btn.pack(fill=X, pady=(15, 0))
        
        # Cadre droit (résultats)
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=RIGHT, fill=BOTH, expand=True)
        
        # Treeview pour les résultats
        results_frame = ttk.LabelFrame(
            right_frame, 
            text="🔍 Detected English Passages", 
            padding=(15, 10, 15, 10),
            style='Card.TLabelframe'
        )
        results_frame.pack(fill=BOTH, expand=True, pady=5)
        
        # Créer le Treeview avec barre de défilement
        tree_container = ttk.Frame(results_frame)
        tree_container.pack(fill=BOTH, expand=True)
        
        tree_scroll_y = ttk.Scrollbar(tree_container)
        tree_scroll_y.pack(side=RIGHT, fill=Y)
        
        tree_scroll_x = ttk.Scrollbar(tree_container, orient=HORIZONTAL)
        tree_scroll_x.pack(side=BOTTOM, fill=X)
        
        columns = ('File', 'Page', 'Line', 'Language', 'English', 'Ignore')
        
        # CORRECTION: Utilisation du nom de style correct
        self.results_tree = ttk.Treeview(
            tree_container, 
            columns=columns, 
            show='headings',
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set,
            selectmode='extended',
            style='Custom.Treeview'  # Nom de style corrigé
        )
        
        # Configurer les tags pour l'alternance de couleurs
        self.results_tree.tag_configure('even', background='#ffffff')
        self.results_tree.tag_configure('odd', background='#f5f7fa')
        
        tree_scroll_y.config(command=self.results_tree.yview)
        tree_scroll_x.config(command=self.results_tree.xview)
        
        # Configurer les colonnes
        col_widths = [180, 60, 60, 110, 550, 70]
        for col, width in zip(columns, col_widths):
            self.results_tree.heading(col, text=col, anchor=W)
            self.results_tree.column(col, width=width, anchor=W, stretch=NO)
        
        self.results_tree.pack(fill=BOTH, expand=True)
        
        # Ajouter des checkboxes pour ignorer
        self.results_tree.tag_configure('skip', background='#ffecec')
        self.skip_vars = {}
        
        # Boutons d'action
        action_frame = ttk.Frame(right_frame)
        action_frame.pack(fill=X, pady=(15, 0))
        
        self.save_btn = ttk.Button(
            action_frame, 
            text="Record Ignored", 
            command=self.save_skips,
            state=DISABLED
        )
        self.save_btn.pack(side=LEFT, padx=(0, 8))
        
        self.open_btn = ttk.Button(
            action_frame, 
            text="Open PDF", 
            command=self.open_pdf,
            state=DISABLED
        )
        self.open_btn.pack(side=LEFT, padx=(0, 8))
        
        # Bouton "Move in Files To Review" (texte rouge)
        self.move_to_review_btn = ttk.Button(
            action_frame, 
            text="Move to Review",
            command=self.move_to_review,
            style='Red.TButton'
        )
        self.move_to_review_btn.pack(side=LEFT, padx=(0, 8))
        
        # Bouton "Move to OK" (texte vert)
        self.move_to_ok_btn = ttk.Button(
            action_frame, 
            text="Move to OK",
            command=self.move_to_ok,
            style='Green.TButton'
        )
        self.move_to_ok_btn.pack(side=LEFT)
        
        # Configurer le Treeview
        self.results_tree.bind('<<TreeviewSelect>>', self.on_tree_select)

    def create_directories_tab(self):
        # Style pour les cadres
        style = ttk.Style()
        style.configure('Dir.TLabelframe', background='#ffffff', borderwidth=1)
        style.configure('Dir.TLabelframe.Label', background='#ffffff', foreground='#2c3e50')
        
        # Cadre principal
        main_frame = ttk.Frame(self.directories_tab)
        main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Configuration des colonnes
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Original PDF Files
        original_frame = ttk.LabelFrame(
            main_frame, 
            text="ORIGINAL PDF FILES",
            padding=10,
            style='Dir.TLabelframe'
        )
        original_frame.grid(row=0, column=0, padx=10, pady=10, sticky=NSEW)
        original_frame.columnconfigure(0, weight=1)  # AJOUTER
        original_frame.rowconfigure(0, weight=1)     # AJOUTER
        self.original_tree = self.create_directory_tree(original_frame, self.original_dir)
        
        # PDF Files OK
        ok_frame = ttk.LabelFrame(
            main_frame, 
            text="PDF FILES OK",
            padding=10,
            style='Dir.TLabelframe'
        )
        ok_frame.grid(row=0, column=1, padx=10, pady=10, sticky=NSEW)
        ok_frame.columnconfigure(0, weight=1)  # AJOUTER
        ok_frame.rowconfigure(0, weight=1)     # AJOUTER
        self.ok_tree = self.create_directory_tree(ok_frame, self.ok_dir)
        
        # PDF Files TO REVIEW
        review_frame = ttk.LabelFrame(
            main_frame, 
            text="PDF FILES TO REVIEW",
            padding=10,
            style='Dir.TLabelframe'
        )
        review_frame.grid(row=0, column=2, padx=10, pady=10, sticky=NSEW)
        review_frame.columnconfigure(0, weight=1)  # AJOUTER
        review_frame.rowconfigure(0, weight=1)     # AJOUTER
        self.review_tree = self.create_directory_tree(review_frame, self.review_dir)
    
    def create_directory_tree(self, parent, directory_path):
        # Frame pour le treeview
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=BOTH, expand=True)
        
        # Barre de défilement
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Treeview
        tree = ttk.Treeview(  # Stocker dans une variable locale
            tree_frame, 
            columns=("Size", "Date"), 
            show="tree headings",
            yscrollcommand=scrollbar.set
        )
        tree.pack(fill=BOTH, expand=True)
        scrollbar.config(command=tree.yview)
        
        # Configurer les colonnes
        tree.column("#0", width=300, anchor=W)
        tree.column("Size", width=100, anchor=W)
        tree.column("Date", width=150, anchor=W)
        
        tree.heading("#0", text="Name", anchor=W)
        tree.heading("Size", text="Size", anchor=W)
        tree.heading("Date", text="Modified", anchor=W)
        
        # Bouton de rafraîchissement
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=X, pady=(10, 0))
        
        refresh_btn = ttk.Button(
            btn_frame, 
            text="Refresh", 
            command=lambda: self.refresh_directory_tree(tree, directory_path)
        )
        refresh_btn.pack(side=LEFT)
        
        # AJOUT: Bouton de suppression
        delete_btn = ttk.Button(
            btn_frame,
            text="Delete files",
            command=lambda: self.delete_selected_files(tree, directory_path),
            style='Red.TButton'  # Style rouge pour indiquer une action dangereuse
        )
        delete_btn.pack(side=LEFT, padx=(8, 8))
        
        # Bouton d'ouverture
        open_btn = ttk.Button(
            btn_frame, 
            text="Open Directory", 
            command=lambda: self.open_directory(directory_path)
        )
        open_btn.pack(side=RIGHT)
    
    
        # Charger les fichiers
        self.refresh_directory_tree(tree, directory_path)
        
        # Lier le double-clic
        tree.bind("<Double-1>", lambda e: self.open_pdf_from_tree(tree))
        
        return tree
    
    def refresh_directory_tree(self, tree, directory_path):
        # Vider le treeview
        for item in tree.get_children():
            tree.delete(item)
        
        # Ajouter les fichiers PDF
        if os.path.exists(directory_path):
            for filename in os.listdir(directory_path):
                if filename.lower().endswith('.pdf'):
                    filepath = os.path.join(directory_path, filename)
                    stat = os.stat(filepath)
                    size = self.format_size(stat.st_size)
                    date = time.strftime('%Y-%m-%d %H:%M', time.localtime(stat.st_mtime))
                    
                    tree.insert("", "end", text=filename, values=(size, date), tags=(filepath,))
    
    def format_size(self, size):
        # Convertir la taille en unités lisible
        if size < 1024:
            return f"{size} bytes"
        elif size < 1024 * 1024:
            return f"{size/1024:.1f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size/(1024*1024):.1f} MB"
        else:
            return f"{size/(1024*1024*1024):.1f} GB"
    
    def open_directory(self, path):
        # Ouvrir l'explorateur de fichiers
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    
    def open_pdf_from_tree(self, tree):
        # Ouvrir le fichier PDF sélectionné
        selection = tree.selection()
        if selection:
            filepath = tree.item(selection[0], "tags")[0]
            self.open_pdf_file(filepath)
    
    def open_pdf_file(self, pdf_path):
        try:
            abs_path = os.path.abspath(pdf_path)
            
            # Ouvrir avec le lecteur PDF par défaut
            if platform.system() == 'Windows':
                # Ouvrir avec SumatraPDF si disponible
                sumatra_path = "C:\\Program Files\\SumatraPDF\\SumatraPDF.exe"
                if os.path.exists(sumatra_path):
                    subprocess.Popen([sumatra_path, abs_path])
                else:
                    # Fallback pour Adobe Reader
                    adobe_path = "C:\\Program Files\\Adobe\\Acrobat DC\\Acrobat\\Acrobat.exe"
                    if os.path.exists(adobe_path):
                        subprocess.Popen([adobe_path, abs_path])
                    else:
                        # Ouvrir avec le lecteur par défaut
                        os.startfile(abs_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.Popen(['open', '-a', 'Preview', abs_path])
            else:  # Linux
                # Linux: utiliser evince ou okular
                try:
                    subprocess.Popen(['evince', abs_path])
                except:
                    try:
                        subprocess.Popen(['okular', abs_path])
                    except:
                        subprocess.Popen(['xdg-open', abs_path])
                        
        except Exception as e:
            messagebox.showerror("Error", f"Could not open PDF:\n{str(e)}")
    
    def delete_selected_files(self, tree, directory_path):
        """Supprime les fichiers sélectionnés après confirmation"""
        selection = tree.selection()
        if not selection:
            messagebox.showinfo("Information", "No file selected")
            return
        
        # Récupérer les chemins complets des fichiers
        file_paths = []
        for item in selection:
            tags = tree.item(item, "tags")
            if tags:
                file_paths.append(tags[0])
        
        # Vérifier que tous les fichiers existent
        existing_files = [fp for fp in file_paths if os.path.exists(fp)]
        if not existing_files:
            messagebox.showinfo("Information", "Selected files not found")
            return
        
        # Demander confirmation
        file_list = "\n".join([os.path.basename(fp) for fp in existing_files])
        if not messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to permanently delete these {len(existing_files)} files?\n\n"
            f"{file_list}\n\n"
            "This action cannot be undone!",
            icon='warning'
        ):
            return
        
        # Supprimer les fichiers
        errors = []
        for file_path in existing_files:
            try:
                os.remove(file_path)
            except Exception as e:
                errors.append(f"{os.path.basename(file_path)}: {str(e)}")
        
        # Rafraîchir l'arborescence
        self.refresh_directory_tree(tree, directory_path)
        
        # Afficher les résultats
        if errors:
            messagebox.showerror(
                "Deletion Errors",
                f"{len(errors)} error(s) occurred:\n\n" + "\n".join(errors)
            )
        else:
            messagebox.showinfo(
                "Success",
                f"{len(existing_files)} file(s) deleted successfully"
            )
    
    def add_files(self):
        files = filedialog.askopenfilenames(
            title="Select PDF Files",
            filetypes=[("PDF Files", "*.pdf")]
        )
        for file in files:
            if file and file not in self.file_list.get(0, END):
                self.file_list.insert(END, file)
    
    def clear_files(self):
        self.file_list.delete(0, END)
    
    def start_analysis(self):
        if not self.file_list.size():
            messagebox.showwarning("Warning", "Please select at least one PDF file")
            return
        
        # Réinitialiser l'interface
        self.results_tree.delete(*self.results_tree.get_children())
        self.save_btn.config(state=DISABLED)
        self.open_btn.config(state=DISABLED)
        self.move_to_review_btn.config(state=DISABLED)
        self.move_to_ok_btn.config(state=DISABLED)
        self.progress['value'] = 0
        self.status_var.set("Analyzing...")
        
        # Réinitialiser les index de couleur
        self.file_color_index = {}
        self.next_color_index = 0
        
        # Réinitialiser les variables de regroupement
        self.current_filename = None
        self.first_passage = True
        
        # Récupérer les fichiers
        files = self.file_list.get(0, END)
        
        # Démarrer le thread d'analyse
        self.stop_event.clear()
        self.analysis_thread = threading.Thread(
            target=self.analyze_pdfs, 
            args=(files,),
            daemon=True
        )
        self.analysis_thread.start()
        
        # Vérifier périodiquement la progression
        self.check_progress()
    
    def analyze_pdfs(self, files):
        try:
            total_files = len(files)
            for idx, pdf_path in enumerate(files):
                if self.stop_event.is_set():
                    break
                
                filename = os.path.basename(pdf_path)
                self.queue.put(('file_start', filename))  # Nouveau message pour le début d'un fichier
                self.queue.put(('status', f"Processing: {filename}"))
                
                # Détecter la langue principale
                full_text = " ".join(extract_text_from_pdf(pdf_path))
                main_language = detect_main_language(full_text)
                
                # Détecter les passages anglais
                skip_set = self.skips.get(filename, set())
                english_sections = detect_english_passages(pdf_path, skip_set)
                
                # Ajouter les résultats à la file
                for (page_num, sentence, start_index, end_index) in english_sections:
                    page_text = extract_text_from_pdf(pdf_path)[page_num - 1]
                    line_num = page_text.count('\n', 0, start_index) + 1 if page_text else "N/A"
                    
                    self.queue.put(('result', {
                        'file': filename,
                        'path': pdf_path,
                        'page': page_num,
                        'line': line_num,
                        'language': main_language,
                        'passage': sentence,
                        'full': sentence
                    }))
                
                # Ajouter une entrée si aucun passage détecté
                if not english_sections:
                    self.queue.put(('no_result', {
                        'file': filename,
                        'path': pdf_path,
                        'language': main_language
                    }))
                
                # Mettre à jour la progression
                self.queue.put(('progress', (idx + 1) / total_files * 100))
            
            self.queue.put(('status', "Analysis completed"))
            self.queue.put(('progress', 100))
        except Exception as e:
            self.queue.put(('error', str(e)))
    
    def check_progress(self):
        try:
            while not self.queue.empty():
                msg_type, data = self.queue.get_nowait()
                
                if msg_type == 'status':
                    self.status_var.set(data)
                elif msg_type == 'progress':
                    self.progress['value'] = data
                elif msg_type == 'file_start':
                    # Début d'un nouveau fichier
                    self.current_filename = data
                    self.first_passage = True
                elif msg_type == 'file_end':
                    # Fin du fichier courant
                    self.current_filename = None
                    self.first_passage = True
                elif msg_type == 'result':
                    # Déterminer la couleur pour ce fichier
                    filename = data['file']
                    if filename not in self.file_color_index:
                        self.file_color_index[filename] = self.next_color_index % 2
                        self.next_color_index += 1
                    
                    color_tag = 'even' if self.file_color_index[filename] == 0 else 'odd'
                    
                    # Afficher le nom du fichier seulement pour la première ligne
                    display_filename = self.current_filename if self.first_passage else ""
                    if self.first_passage:
                        self.first_passage = False
                    
                    # Créer l'item dans le treeview
                    item_id = self.results_tree.insert('', 'end', values=(
                        display_filename,  # Afficher le nom seulement sur la première ligne
                        data['page'],
                        data['line'],
                        data['language'],
                        data['passage'][:150] + '...' if len(data['passage']) > 150 else data['passage'],
                        "❌"
                    ), tags=(color_tag, data['path']))
                    
                    # Stocker le passage complet
                    self.full_passages[item_id] = data['full']
                    self.results_tree.item(item_id, tags=(data['path'],))
                    self.skip_vars[item_id] = False
                
                elif msg_type == 'no_result':
                    # Déterminer la couleur pour ce fichier
                    filename = data['file']
                    if filename not in self.file_color_index:
                        self.file_color_index[filename] = self.next_color_index % 2
                        self.next_color_index += 1
                    
                    color_tag = 'even' if self.file_color_index[filename] == 0 else 'odd'
                    
                    # Pour les fichiers sans passages, afficher toujours le nom
                    item_id = self.results_tree.insert('', 'end', values=(
                        data['file'],  # Toujours afficher le nom
                        "-",
                        "-",
                        data['language'],
                        "No English passages detected",
                        "-"
                    ), tags=(color_tag, 'no_english', data['path']))
                    self.results_tree.tag_configure('no_english', foreground='#2ecc71')
                
                elif msg_type == 'error':
                    messagebox.showerror("Error", f"An error occurred:\n{data}")
        
        except queue.Empty:
            pass
        
        # Vérifier si le thread est toujours actif
        if self.analysis_thread and self.analysis_thread.is_alive():
            self.root.after(100, self.check_progress)
        else:
            if self.results_tree.get_children():
                self.save_btn.config(state=NORMAL)
            self.analysis_thread = None
    
    def on_tree_select(self, event):
        selection = self.results_tree.selection()
        if selection:
            # Activer les boutons
            self.open_btn.config(state=NORMAL)
            self.move_to_review_btn.config(state=NORMAL)
            self.move_to_ok_btn.config(state=NORMAL)
            
            # Basculer l'état "Ignorer" UNIQUEMENT pour les éléments non-verts
            for item in selection:
                # Passer les éléments verts
                if 'no_english' in self.results_tree.item(item, 'tags'):
                    continue
                    
                current_state = self.skip_vars[item]
                new_state = not current_state
                self.skip_vars[item] = new_state
                
                # Mettre à jour l'affichage
                self.results_tree.item(item, values=(
                    *self.results_tree.item(item)['values'][:-1],
                    "✅" if new_state else "❌"
                ))
                
                # Ajouter/retirer de la liste des passages à ignorer
                # Récupérer le nom du fichier à partir des données complètes
                # au lieu de la colonne "File" qui peut être vide
                filename = os.path.basename(self.results_tree.item(item, 'tags')[0])
                passage = self.get_full_passage(item)
                
                if new_state:
                    if (filename, passage) not in self.skipped_passages:
                        self.skipped_passages.append((filename, passage))
                else:
                    if (filename, passage) in self.skipped_passages:
                        self.skipped_passages.remove((filename, passage))
        else:
            self.open_btn.config(state=DISABLED)
            self.move_to_review_btn.config(state=DISABLED)
            self.move_to_ok_btn.config(state=DISABLED)
    
    def get_full_passage(self, item):
        # Récupérer le passage complet à partir du dictionnaire
        return self.full_passages.get(item, "")
    
    def save_skips(self):
        if not self.skipped_passages:
            messagebox.showinfo("Information", "No passages selected to ignore")
            return
        
        try:
            # Créer ou mettre à jour le fichier skips.csv avec encodage UTF-8 et BOM
            with open('skips.csv', 'a', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                for filename, passage in self.skipped_passages:
                    writer.writerow([filename, passage])
            
            # Mettre à jour les skips en mémoire
            for filename, passage in self.skipped_passages:
                self.skips[filename].add(passage)
            
            # Supprimer les éléments cochés du Treeview
            files_to_update = set()  # Fichiers dont la première ligne doit être mise à jour
            items_to_remove = []
            for item in list(self.results_tree.get_children()):
                if self.skip_vars.get(item, False):
                    # Vérifier si c'est la première ligne d'un groupe
                    values = self.results_tree.item(item)['values']
                    if values[0]:  # Si cette ligne a un nom de fichier
                        files_to_update.add(self.results_tree.item(item, 'tags')[0])
                    
                    items_to_remove.append(item)
            
            # Supprimer les items
            for item in items_to_remove:
                self.results_tree.delete(item)
                del self.skip_vars[item]
                if item in self.full_passages:
                    del self.full_passages[item]
            
            # Mettre à jour la première ligne des fichiers affectés
            for file_path in files_to_update:
                # Trouver tous les items restants pour ce fichier
                file_items = []
                for item in self.results_tree.get_children():
                    tags = self.results_tree.item(item, 'tags')
                    if tags and tags[0] == file_path:
                        file_items.append(item)
                
                # Mettre à jour la première ligne si elle existe
                if file_items:
                    first_item = file_items[0]
                    values = list(self.results_tree.item(first_item, 'values'))
                    filename = os.path.basename(file_path)
                    values[0] = filename  # Réinsérer le nom du fichier
                    self.results_tree.item(first_item, values=values)
            
            self.skipped_passages = []
            messagebox.showinfo("Success", "Passages have been saved and will be ignored in future analyses")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error while saving:\n{str(e)}")
    
    def open_pdf(self):
        selection = self.results_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        pdf_path = self.results_tree.item(item, 'tags')[0]
        values = self.results_tree.item(item)['values']
        
        # Récupérer le numéro de page
        page = values[1]
        
        try:
            abs_path = os.path.abspath(pdf_path)
            
            # Ouvrir avec le lecteur PDF par défaut en spécifiant la page
            if platform.system() == 'Windows':
                # Ouvrir avec SumatraPDF si disponible (recommandé pour cette fonctionnalité)
                sumatra_path = "C:\\Program Files\\SumatraPDF\\SumatraPDF.exe"
                if os.path.exists(sumatra_path):
                    subprocess.Popen([sumatra_path, "-page", str(page), abs_path])
                else:
                    # Fallback pour Adobe Reader
                    adobe_path = "C:\\Program Files\\Adobe\\Acrobat DC\\Acrobat\\Acrobat.exe"
                    if os.path.exists(adobe_path):
                        subprocess.Popen([adobe_path, "/A", f"page={page}", abs_path])
                    else:
                        # Ouvrir avec le lecteur par défaut
                        os.startfile(abs_path)
            elif platform.system() == 'Darwin':  # macOS
                # macOS: utiliser open avec Preview et spécifier la page
                subprocess.Popen(['open', '-a', 'Preview', abs_path])
                time.sleep(1)  # Donner le temps à Preview de s'ouvrir
                if page != "-":
                    subprocess.Popen(['osascript', '-e', 
                                     f'tell application "Preview" to set page of document 1 to {page}'])
            else:  # Linux
                # Linux: utiliser evince ou okular
                try:
                    subprocess.Popen(['evince', '-p', str(page), abs_path])
                except:
                    try:
                        subprocess.Popen(['okular', '-p', str(page), abs_path])
                    except:
                        subprocess.Popen(['xdg-open', abs_path])
                        
        except Exception as e:
            messagebox.showerror("Error", f"Could not open PDF:\n{str(e)}")
    
    def get_selected_files(self):
        """Récupère la liste des fichiers distincts sélectionnés dans le Treeview"""
        selected_files = set()
        for item in self.results_tree.selection():
            tags = self.results_tree.item(item, 'tags')
            if tags:
                # Le chemin du fichier est toujours le dernier tag
                file_path = tags[-1]
                filename = os.path.basename(file_path)
                selected_files.add(filename)
        return list(selected_files)
    
    def move_to_review(self):
        """Déplace les fichiers sélectionnés vers 'PDF FILES TO REVIEW'"""
        self.move_files("PDF FILES TO REVIEW")
    
    def move_to_ok(self):
        """Déplace les fichiers sélectionnés vers 'PDF FILES OK'"""
        self.move_files("PDF FILES OK")
    
    def move_files(self, target_dir_name):
        """Déplace les fichiers sélectionnés vers le répertoire cible"""
        # Récupérer les fichiers sélectionnés
        selected_files = self.get_selected_files()
        if not selected_files:
            messagebox.showinfo("Information", "No file selected")
            return
        
        # Déterminer le répertoire cible
        if target_dir_name == "PDF FILES OK":
            target_dir = self.ok_dir
        else:
            target_dir = self.review_dir
        
        moved_files = []
        errors = []
        
        # Déplacer chaque fichier
        for filename in selected_files:
            src_path = os.path.join(self.original_dir, filename)
            dest_path = os.path.join(target_dir, filename)
            
            if not os.path.exists(src_path):
                errors.append(f"File not found: {filename}")
                continue
            
            try:
                shutil.move(src_path, dest_path)
                moved_files.append(filename)
            except Exception as e:
                errors.append(f"Error with {filename}: {str(e)}")
        
        # Supprimer TOUS les éléments du fichier, pas seulement les sélectionnés
        items_to_remove = []
        for item in self.results_tree.get_children():
            tags = self.results_tree.item(item, 'tags')
            if tags:
                # Le chemin du fichier est toujours le dernier tag
                file_path = tags[-1]  # MODIFICATION ICI: utiliser le dernier tag
                filename = os.path.basename(file_path)
                
                if filename in moved_files:
                    items_to_remove.append(item)
        
        for item in items_to_remove:
            self.results_tree.delete(item)
            if item in self.skip_vars:
                del self.skip_vars[item]
            if item in self.full_passages:
                del self.full_passages[item]
        
        # Afficher les résultats
        if moved_files:
            messagebox.showinfo("Success", f"{len(moved_files)} files moved to {target_dir_name}")
        if errors:
            messagebox.showerror("Errors", "\n".join(errors))
    
    def show_help(self):
        help_text = """
        PDF Translation Analyzer - Help
        
        1. Add PDF files using the 'Add files' button
        2. Click 'Start Analysis' to scan for English passages
        3. Review the detected passages in the results table
        4. Select passages to ignore (they will be marked with ✅)
        5. Save ignored passages with 'Record Ignored'
        6. Open PDFs at the detected location with 'Open PDF'
        7. Move files to review or OK folders using the action buttons
        
        Tips:
        - Click on a passage to toggle ignore status
        - Files with no English passages are shown in green
        - Ignored passages are saved in skips.csv
        
        DIRECTORIES Tab:
        - View PDF files in different folders
        - Double-click to open a PDF
        - Use 'Refresh' to update the file list
        - Use 'Open Directory' to open the folder in explorer
        """
        messagebox.showinfo("Help", help_text.strip())

if __name__ == "__main__":
    root = Tk()
    app = PDFAnalyzerApp(root)
    root.mainloop()