import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox, Listbox
import os
import csv
import json
import xml.etree.ElementTree as ET
import re
from datetime import datetime
import sqlite3

# New libraries to solve RTL issue
try:
    from arabic_reshaper import reshape
    from bidi.algorithm import get_display
    HAS_BIDI_SUPPORT = True
except ImportError:
    HAS_BIDI_SUPPORT = False
    print("Warning: arabic_reshaper or python-bidi libraries are not installed. Install them with the following command:")
    print("pip install arabic-reshaper python-bidi")

class IranianPlateSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Iranian Vehicle Plate Search")
        self.root.geometry("1000x800")
        self.root.configure(bg="#f0f8ff")
        
        # Advanced RTL settings
        self.root.tk_setPalette(background="#f0f8ff")
        try:
            self.root.tk.call('tk', 'scaling', 1.0)
        except:
            pass
        
        # Appearance settings
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#f0f8ff')
        self.style.configure('TLabel', background='#f0f8ff', font=('Vazirmatn', 11))
        self.style.configure('TButton', font=('Vazirmatn', 11, 'bold'))
        
        # Program variables
        self.selected_files = []
        self.search_history = []
        self.history_file = "plate_search_history.json"
        
        # Allowed letters in Iranian plates
        self.persian_letters = [
            'ا', 'ب', 'پ', 'ت', 'ث', 'ج', 'چ', 'ح', 'خ', 'د', 'ذ', 'ر', 'ز', 'ژ', 'س', 'ش', 
            'ص', 'ض', 'ط', 'ظ', 'ع', 'غ', 'ف', 'ق', 'ک', 'گ', 'ل', 'م', 'ن', 'و', 'ه', 'ی'
        ]
        
        # Create user interface
        self.create_widgets()
        
        # Load search history
        self.load_search_history()
    
    def get_persian_text(self, text):
        """Convert Persian text to correct format for display"""
        if HAS_BIDI_SUPPORT:
            try:
                reshaped_text = reshape(text)
                return get_display(reshaped_text)
            except:
                return text
        else:
            return text
    
    def create_widgets(self):
        # Top section: Bismillah
        header_frame = tk.Frame(self.root, bg="#1e3a8a", height=80)
        header_frame.pack(fill=tk.X, padx=5, pady=5)
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame, 
            text=self.get_persian_text("In the name of God, the Most Gracious, the Most Merciful"), 
            font=("Vazirmatn", 24, "bold"),
            bg="#1e3a8a", 
            fg="white"
        ).pack(expand=True)
        
        # Main section with notebook
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Plate search tab
        self.plate_search_tab = tk.Frame(notebook, bg="#f0f8ff")
        notebook.add(self.plate_search_tab, text=self.get_persian_text("Plate Search"))
        self.create_plate_search_tab()
        
        # General search tab
        self.general_search_tab = tk.Frame(notebook, bg="#f0f8ff")
        notebook.add(self.general_search_tab, text=self.get_persian_text("General Search"))
        self.create_general_search_tab()
        
        # Bottom section: File list and search history
        bottom_frame = tk.Frame(self.root, bg="#f0f8ff")
        bottom_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # File list section
        files_frame = tk.LabelFrame(
            bottom_frame, 
            text=self.get_persian_text("Selected Files"), 
            font=("Vazirmatn", 12, "bold"),
            bg="#f0f8ff",
            fg="#1e3a8a"
        )
        files_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.files_listbox = Listbox(
            files_frame, 
            font=("Vazirmatn", 10),
            bg="white",
            selectbackground="#3b82f6",
            height=10
        )
        self.files_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Search history section
        history_frame = tk.LabelFrame(
            bottom_frame, 
            text=self.get_persian_text("Search History"), 
            font=("Vazirmatn", 12, "bold"),
            bg="#f0f8ff",
            fg="#1e3a8a"
        )
        history_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.history_text = tk.Text(
            history_frame, 
            font=("Vazirmatn", 10),
            bg="white",
            height=10,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.history_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.history_text.tag_configure("rtl", justify='right', font=("Vazirmatn", 10))
        self.history_text.bind('<Double-Button-1>', self.on_history_select)
        
        # Creator information section
        footer_frame = tk.Frame(self.root, bg="#1e3a8a", height=60)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=5)
        footer_frame.pack_propagate(False)
        
        tk.Label(
            footer_frame, 
            text=self.get_persian_text(""), 
            font=("Vazirmatn", 11, "italic"),
            bg="#1e3a8a", 
            fg="white"
        ).pack(side=tk.LEFT, padx=20, pady=15)
        
        tk.Label(
            footer_frame, 
            text="your welcome", 
            font=("Vazirmatn", 11),
            bg="#1e3a8a", 
            fg="white"
        ).pack(side=tk.RIGHT, padx=20, pady=15)
    
    def create_plate_search_tab(self):
        # Instructions section
        info_frame = tk.Frame(self.plate_search_tab, bg="#f0f8ff")
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            info_frame, 
            text=self.get_persian_text("Iranian Plate Search with Format: [Two Digits] [Persian Letter] [Three Digits] [Two Digits]"), 
            font=("Vazirmatn", 14, "bold"),
            bg="#f0f8ff",
            fg="#dc2626"
        ).pack()
        
        # Plate input section with correct format
        plate_frame = tk.Frame(self.plate_search_tab, bg="#f0f8ff")
        plate_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Part 1: Two-digit number
        part1_frame = tk.Frame(plate_frame, bg="#f0f8ff")
        part1_frame.pack(side=tk.RIGHT, padx=10, pady=10)
        
        tk.Label(
            part1_frame, 
            text=self.get_persian_text("Part 1\n(Two Digits)"), 
            font=("Vazirmatn", 11, "bold"),
            bg="#f0f8ff"
        ).pack()
        
        self.part1_entry = tk.Entry(
            part1_frame, 
            font=("Vazirmatn", 14, "bold"),
            width=5,
            justify='center'
        )
        self.part1_entry.pack(pady=5)
        
        # Part 2: Persian letter
        part2_frame = tk.Frame(plate_frame, bg="#f0f8ff")
        part2_frame.pack(side=tk.RIGHT, padx=10, pady=10)
        
        tk.Label(
            part2_frame, 
            text=self.get_persian_text("Part 2\n(Persian Letter)"), 
            font=("Vazirmatn", 11, "bold"),
            bg="#f0f8ff"
        ).pack()
        
        self.part2_var = tk.StringVar()
        self.part2_combobox = ttk.Combobox(
            part2_frame, 
            textvariable=self.part2_var,
            values=[""] + self.persian_letters,
            font=("Vazirmatn", 14, "bold"),
            width=3,
            state="readonly"
        )
        self.part2_combobox.pack(pady=5)
        
        # Part 3: Three-digit number
        part3_frame = tk.Frame(plate_frame, bg="#f0f8ff")
        part3_frame.pack(side=tk.RIGHT, padx=10, pady=10)
        
        tk.Label(
            part3_frame, 
            text=self.get_persian_text("Part 3\n(Three Digits)"), 
            font=("Vazirmatn", 11, "bold"),
            bg="#f0f8ff"
        ).pack()
        
        self.part3_entry = tk.Entry(
            part3_frame, 
            font=("Vazirmatn", 14, "bold"),
            width=5,
            justify='center'
        )
        self.part3_entry.pack(pady=5)
        
        # Part 4: Two-digit number
        part4_frame = tk.Frame(plate_frame, bg="#f0f8ff")
        part4_frame.pack(side=tk.RIGHT, padx=10, pady=10)
        
        tk.Label(
            part4_frame, 
            text=self.get_persian_text("Part 4\n(Two Digits)"), 
            font=("Vazirmatn", 11, "bold"),
            bg="#f0f8ff"
        ).pack()
        
        self.part4_entry = tk.Entry(
            part4_frame, 
            font=("Vazirmatn", 14, "bold"),
            width=5,
            justify='center'
        )
        self.part4_entry.pack(pady=5)
        
        # Buttons
        buttons_frame = tk.Frame(plate_frame, bg="#f0f8ff")
        buttons_frame.pack(side=tk.LEFT, padx=20, pady=10)
        
        tk.Button(
            buttons_frame, 
            text=self.get_persian_text("Search Plate"), 
            command=self.search_plate_pattern,
            bg="#dc2626", 
            fg="white",
            font=("Vazirmatn", 12, "bold"),
            padx=15,
            pady=10,
            width=12
        ).pack(pady=5)
        
        tk.Button(
            buttons_frame, 
            text=self.get_persian_text("Clear"), 
            command=self.clear_plate_fields,
            bg="#6b7280", 
            fg="white",
            font=("Vazirmatn", 12, "bold"),
            padx=15,
            pady=10,
            width=12
        ).pack(pady=5)
        
        # Results section
        results_frame = tk.Frame(self.plate_search_tab, bg="#f0f8ff")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(
            results_frame, 
            text=self.get_persian_text("Plate Search Results:"), 
            font=("Vazirmatn", 14, "bold"),
            bg="#f0f8ff"
        ).pack(anchor=tk.W, padx=5)
        
        self.plate_results_text = scrolledtext.ScrolledText(
            results_frame, 
            width=80, 
            height=15, 
            font=("Vazirmatn", 11),
            wrap=tk.WORD,
            padx=10,
            pady=10,
            bg="white"
        )
        self.plate_results_text.pack(fill=tk.BOTH, expand=True)
        
        # Set right-align for result text
        self.plate_results_text.tag_configure("rtl", justify='right', font=("Vazirmatn", 11))
    
    def create_general_search_tab(self):
        # File selection section
        file_frame = tk.Frame(self.general_search_tab, bg="#f0f8ff")
        file_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            file_frame, 
            text=self.get_persian_text("Select Files:"), 
            font=("Vazirmatn", 14, "bold"),
            bg="#f0f8ff"
        ).pack(side=tk.LEFT, padx=5)
        
        self.file_count_label = tk.Label(
            file_frame, 
            text=self.get_persian_text("Number of Files: 0"), 
            font=("Vazirmatn", 11),
            bg="#f0f8ff",
            fg="#6b7280"
        )
        self.file_count_label.pack(side=tk.RIGHT, padx=5)
        
        tk.Button(
            file_frame, 
            text=self.get_persian_text("Select Files"), 
            command=self.select_files,
            bg="#059669", 
            fg="white",
            font=("Vazirmatn", 12, "bold"),
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=10)
        
        # Keyword section
        keyword_frame = tk.Frame(self.general_search_tab, bg="#f0f8ff")
        keyword_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            keyword_frame, 
            text=self.get_persian_text("Keyword:"), 
            font=("Vazirmatn", 14, "bold"),
            bg="#f0f8ff"
        ).pack(side=tk.LEFT, padx=5)
        
        self.keyword_entry = tk.Entry(
            keyword_frame, 
            font=("Vazirmatn", 12),
            width=40,
            justify='right'
        )
        self.keyword_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        tk.Button(
            keyword_frame, 
            text=self.get_persian_text("Search"), 
            command=self.search_keyword,
            bg="#2563eb", 
            fg="white",
            font=("Vazirmatn", 12, "bold"),
            padx=15,
            pady=5
        ).pack(side=tk.RIGHT, padx=5)
        
        # Results section
        results_frame = tk.Frame(self.general_search_tab, bg="#f0f8ff")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(
            results_frame, 
            text=self.get_persian_text("Search Results:"), 
            font=("Vazirmatn", 14, "bold"),
            bg="#f0f8ff"
        ).pack(anchor=tk.W, padx=5)
        
        self.general_results_text = scrolledtext.ScrolledText(
            results_frame, 
            width=80, 
            height=15, 
            font=("Vazirmatn", 11),
            wrap=tk.WORD,
            padx=10,
            pady=10,
            bg="white"
        )
        self.general_results_text.pack(fill=tk.BOTH, expand=True)
        
        # Set right-align for result text
        self.general_results_text.tag_configure("rtl", justify='right', font=("Vazirmatn", 11))
    
    def clear_plate_fields(self):
        self.part1_entry.delete(0, tk.END)
        self.part2_var.set("")
        self.part3_entry.delete(0, tk.END)
        self.part4_entry.delete(0, tk.END)
    
    def select_files(self):
        files = filedialog.askopenfilenames(
            title=self.get_persian_text("Select Files"),
            filetypes=[
                (self.get_persian_text("Text Files"), "*.txt"),
                (self.get_persian_text("CSV Files"), "*.csv"),
                (self.get_persian_text("JSON Files"), "*.json"),
                (self.get_persian_text("XML Files"), "*.xml"),
                (self.get_persian_text("LOG Files"), "*.log"),
                (self.get_persian_text("INI Files"), "*.ini"),
                (self.get_persian_text("SQL Files"), "*.sql"),
                (self.get_persian_text("DB Files"), "*.db"),
                (self.get_persian_text("All Files"), "*.*")
            ]
        )
        if files:
            self.selected_files = files
            self.file_count_label.config(text=self.get_persian_text(f"Number of Files: {len(files)}"))
            
            # Update file list
            self.files_listbox.delete(0, tk.END)
            for file_path in files:
                self.files_listbox.insert(tk.END, os.path.basename(file_path))
    
    def search_keyword(self):
        keyword = self.keyword_entry.get().strip()
        if not keyword:
            messagebox.showwarning(self.get_persian_text("Warning"), self.get_persian_text("Please enter a keyword!"))
            return
        
        if not self.selected_files:
            messagebox.showwarning(self.get_persian_text("Warning"), self.get_persian_text("First, select the files!"))
            return
        
        self.general_results_text.delete(1.0, tk.END)
        results = []
        start_time = datetime.now()
        
        for file_path in self.selected_files:
            try:
                file_name = os.path.basename(file_path)
                ext = os.path.splitext(file_name)[1].lower()
                
                # Read file content based on type
                content = ""
                if ext == '.txt':
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                elif ext == '.csv':
                    with open(file_path, 'r', encoding='utf-8') as file:
                        reader = csv.reader(file)
                        lines = []
                        for row in reader:
                            lines.append(','.join(row))
                        content = '\n'.join(lines)
                elif ext == '.json':
                    with open(file_path, 'r', encoding='utf-8') as file:
                        data = json.load(file)
                        content = json.dumps(data, indent=4, ensure_ascii=False)
                elif ext == '.xml':
                    tree = ET.parse(file_path)
                    root = tree.getroot()
                    content = ET.tostring(root, encoding='unicode')
                elif ext == '.db':
                    # Search in SQLite database
                    conn = sqlite3.connect(file_path)
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables = cursor.fetchall()
                    
                    for table in tables:
                        table_name = table[0]
                        cursor.execute(f"SELECT * FROM {table_name}")
                        rows = cursor.fetchall()
                        for row in rows:
                            row_str = ' '.join(str(item) for item in row)
                            if keyword.lower() in row_str.lower():
                                results.append(f"File: {file_name} (Table: {table_name})\n{row_str}")
                    conn.close()
                    continue
                else:
                    # For other formats, read as plain text
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                
                # Split content into lines
                lines = content.splitlines()
                matches = []
                
                for line_num, line in enumerate(lines, 1):
                    if keyword.lower() in line.lower():  # Case-insensitive search
                        matches.append(f"Line {line_num}: {line.strip()}")
                
                if matches:
                    results.append(f"\n--- File: {file_name} ---\n" + "\n".join(matches))
            except Exception as e:
                results.append(f"\nError reading file {file_name}: {str(e)}")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        if results:
            # Add results with right-align tag
            processed_results = []
            for result in results:
                processed_lines = []
                for line in result.split('\n'):
                    processed_lines.append(self.get_persian_text(line))
                processed_results.append('\n'.join(processed_lines))
            
            self.general_results_text.insert(tk.END, '\n'.join(processed_results), "rtl")
            # Add to search history
            self.add_to_search_history(f"Keyword: {keyword}", len(results), duration)
        else:
            self.general_results_text.insert(tk.END, self.get_persian_text("No results found!"), "rtl")
            self.add_to_search_history(f"Keyword: {keyword}", 0, duration)
    
    def search_plate_pattern(self):
        part1 = self.part1_entry.get().strip()
        part2 = self.part2_var.get().strip()
        part3 = self.part3_entry.get().strip()
        part4 = self.part4_entry.get().strip()
        
        # Validate inputs
        if not any([part1, part2, part3, part4]):
            messagebox.showwarning(self.get_persian_text("Warning"), self.get_persian_text("Please enter at least one part of the plate!"))
            return
        
        if part1 and (not part1.isdigit() or len(part1) != 2):
            messagebox.showwarning(self.get_persian_text("Warning"), self.get_persian_text("Part 1 must be two digits!"))
            return
        
        if part3 and (not part3.isdigit() or len(part3) != 3):
            messagebox.showwarning(self.get_persian_text("Warning"), self.get_persian_text("Part 3 must be three digits!"))
            return
        
        if part4 and (not part4.isdigit() or len(part4) != 2):
            messagebox.showwarning(self.get_persian_text("Warning"), self.get_persian_text("Part 4 must be two digits!"))
            return
        
        if not self.selected_files:
            messagebox.showwarning(self.get_persian_text("Warning"), self.get_persian_text("First, select the files!"))
            return
        
        self.plate_results_text.delete(1.0, tk.END)
        results = []
        start_time = datetime.now()
        
        # Build regex pattern with correct Iranian plate format
        pattern_parts = []
        pattern_parts.append(r"\d{2}" if not part1 else part1)
        pattern_parts.append(r"[\u0600-\u06FF]" if not part2 else part2)  # Persian letters range
        pattern_parts.append(r"\d{3}" if not part3 else part3)
        pattern_parts.append(r"\d{2}" if not part4 else part4)
        
        pattern = r"\s+".join(pattern_parts)
        regex = re.compile(pattern)
        
        for file_path in self.selected_files:
            try:
                file_name = os.path.basename(file_path)
                ext = os.path.splitext(file_name)[1].lower()
                
                # Read file content based on type
                content = ""
                if ext == '.txt':
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                elif ext == '.csv':
                    with open(file_path, 'r', encoding='utf-8') as file:
                        reader = csv.reader(file)
                        lines = []
                        for row in reader:
                            lines.append(','.join(row))
                        content = '\n'.join(lines)
                elif ext == '.json':
                    with open(file_path, 'r', encoding='utf-8') as file:
                        data = json.load(file)
                        content = json.dumps(data, indent=4, ensure_ascii=False)
                elif ext == '.xml':
                    tree = ET.parse(file_path)
                    root = tree.getroot()
                    content = ET.tostring(root, encoding='unicode')
                elif ext == '.db':
                    # Search in SQLite database
                    conn = sqlite3.connect(file_path)
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables = cursor.fetchall()
                    
                    for table in tables:
                        table_name = table[0]
                        cursor.execute(f"SELECT * FROM {table_name}")
                        rows = cursor.fetchall()
                        for row in rows:
                            row_str = ' '.join(str(item) for item in row)
                            if regex.search(row_str):
                                results.append(f"File: {file_name} (Table: {table_name})\n{row_str}")
                    conn.close()
                    continue
                else:
                    # For other formats, read as plain text
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                
                # Search with pattern
                lines = content.splitlines()
                matches = []
                
                for line_num, line in enumerate(lines, 1):
                    if regex.search(line):
                        matches.append(f"Line {line_num}: {line.strip()}")
                
                if matches:
                    results.append(f"\n--- File: {file_name} ---\n" + "\n".join(matches))
            except Exception as e:
                results.append(f"\nError reading file {file_name}: {str(e)}")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Build plate string for display with correct format
        plate_str = f"{part1 or '--'} {part2 or '-'} {part3 or '---'} {part4 or '--'}"
        
        if results:
            # Add results with right-align tag
            processed_results = []
            for result in results:
                processed_lines = []
                for line in result.split('\n'):
                    processed_lines.append(self.get_persian_text(line))
                processed_results.append('\n'.join(processed_lines))
            
            self.plate_results_text.insert(tk.END, '\n'.join(processed_results), "rtl")
            # Add to search history
            self.add_to_search_history(f"Vehicle Plate: {plate_str}", len(results), duration)
        else:
            self.plate_results_text.insert(tk.END, self.get_persian_text("No plate found!"), "rtl")
            self.add_to_search_history(f"Vehicle Plate: {plate_str}", 0, duration)
    
    def add_to_search_history(self, query, result_count, duration):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        history_item = {
            "query": query,
            "result_count": result_count,
            "duration": duration,
            "timestamp": timestamp
        }
        
        self.search_history.append(history_item)
        self.save_search_history()
        self.update_history_listbox()
    
    def update_history_listbox(self):
        self.history_text.config(state=tk.NORMAL)
        self.history_text.delete(1.0, tk.END)
        for item in reversed(self.search_history[-20:]):  # Show last 20 items
            display_text = f"{item['timestamp']} | {item['query']} | {self.get_persian_text('Results')}: {item['result_count']} | {self.get_persian_text('Time')}: {item['duration']:.2f}{self.get_persian_text('seconds')}"
            self.history_text.insert(tk.END, display_text + "\n", "rtl")
        self.history_text.config(state=tk.DISABLED)
    
    def on_history_select(self, event):
        # Get the index of the line under the cursor
        index = self.history_text.index(f"@{event.x},{event.y}")
        line_num = int(index.split('.')[0])
        
        total_displayed = min(20, len(self.search_history))
        if 1 <= line_num <= total_displayed:
            actual_index = len(self.search_history) - line_num
            if 0 <= actual_index < len(self.search_history):
                history_item = self.search_history[actual_index]
                messagebox.showinfo(
                    self.get_persian_text("Search Details"), 
                    f"{self.get_persian_text('Search Query')}: {history_item['query']}\n"
                    f"{self.get_persian_text('Number of Results')}: {history_item['result_count']}\n"
                    f"{self.get_persian_text('Search Time')}: {history_item['duration']:.2f} {self.get_persian_text('seconds')}\n"
                    f"{self.get_persian_text('Date and Time')}: {history_item['timestamp']}"
                )
    
    def save_search_history(self):
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.search_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving search history: {e}")
    
    def load_search_history(self):
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.search_history = json.load(f)
                self.update_history_listbox()
        except Exception as e:
            print(f"Error loading search history: {e}")
            self.search_history = []

if __name__ == "__main__":
    root = tk.Tk()
    app = IranianPlateSearchApp(root)
    root.mainloop()