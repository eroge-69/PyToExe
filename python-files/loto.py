import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from itertools import combinations
from collections import defaultdict
import random
import os
import webbrowser
import time
from collections import Counter

class LoterijaScraper:
    BASE_URL = "https://www.loterija.si/loto/rezultati"
    PROGRAM_URL = "https://www.loterija.si"
    UPDATE_URL = "https://api.example.com/version-check"
    VERSION = "1.3.8"
    MIN_YEAR = 2000  # Earliest year with available data
    MAX_YEAR = datetime.now().year

    @staticmethod
    def get_results(year):
        all_results = []
        session = requests.Session()
        
        if year < LoterijaScraper.MIN_YEAR or year > LoterijaScraper.MAX_YEAR:
            messagebox.showwarning("Opozorilo", 
                                f"Podatki za leto {year} niso na voljo.\n"
                                f"Na voljo so podatki od {LoterijaScraper.MIN_YEAR} do {LoterijaScraper.MAX_YEAR}.")
            return None
        
        page = 1
        max_pages = 3
        retries = 3
        timeout = 20
        consecutive_empty_pages = 0  # Track consecutive empty pages
        
        while page <= max_pages:
            for attempt in range(retries):
                try:
                    # Try both URL formats
                    urls_to_try = [
                        f"https://www.loterija.si/loto/rezultati/{year}?page={page}",
                        f"https://www.loterija.si/loto/rezultati?year={year}&selectedGame=loto&page={page}&ajax=.archive-dynamic"
                    ]
                    
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Referer': 'https://www.loterija.si/loto/rezultati'
                    }
                    
                    response = None
                    for url in urls_to_try:
                        try:
                            response = session.get(url, headers=headers, timeout=timeout)
                            if response.status_code == 200:
                                break
                        except:
                            continue
                    
                    if not response or response.status_code != 200:
                        raise Exception(f"Could not fetch data from any URL for page {page}")
                    
                    print(f"\n=== Processing page {page} ===")
                    print(f"URL: {response.url}")
                    print(f"Status code: {response.status_code}")
                    
                    page_results = LoterijaScraper.parse_results(response.text, year)
                    
                    if not page_results:
                        print(f"No valid results found on page {page}")
                        consecutive_empty_pages += 1
                        
                        # Stop if we've had 2 consecutive empty pages
                        if consecutive_empty_pages >= 2:
                            print("Stopping after 2 consecutive empty pages")
                            return all_results if all_results else None
                            
                        if page == 1:
                            return None
                        break
                    else:
                        consecutive_empty_pages = 0  # Reset counter if we get results
                        
                    all_results.extend(page_results)
                    print(f"Added {len(page_results)} results from page {page}")
                    
                    # Check if we should continue to next page
                    if len(page_results) < 10:
                        print("Fewer than 10 results, assuming last page")
                        return all_results
                        
                    time.sleep(random.uniform(1, 2))
                    page += 1
                    break
                        
                except Exception as e:
                    print(f"Attempt {attempt + 1} failed for page {page}: {e}")
                    if attempt == retries - 1:
                        if page == 1:
                            messagebox.showwarning("Opozorilo", 
                                                f"Podatki za leto {year} niso na voljo ali je spletna stran spremenila strukturo.\n"
                                                f"Poskusite z leti med {LoterijaScraper.MIN_YEAR} in {LoterijaScraper.MAX_YEAR}.")
                            return None
                        break
                    time.sleep(3)
        
        print(f"\nTotal results collected: {len(all_results)}")
        return all_results if all_results else None
    
    @staticmethod
    def parse_results(html_content, year):
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Try different selectors for archive elements
        draws = soup.find_all('article', class_='archive-element')
        if not draws:
            draws = soup.find_all('div', class_='archive-element')
        if not draws:
            draws = soup.find_all('div', class_='archive-item')
        
        results = []
        
        for draw in draws:
            try:
                # Extract date - try multiple selectors
                date_element = None
                date_selectors = [
                    {'tag': 'h3', 'class': 'date'},
                    {'tag': 'div', 'class': 'archive-element-date'},
                    {'tag': 'div', 'class': 'archive-item-date'},
                    {'tag': 'div', 'class': 'date'},
                    {'tag': 'span', 'class': 'date'}
                ]
                
                for selector in date_selectors:
                    date_element = draw.find(selector['tag'], class_=selector.get('class'))
                    if date_element:
                        break
                
                if not date_element:
                    # Fallback to searching for date pattern in text
                    date_text = None
                    for elem in draw.find_all(string=re.compile(r'\d{1,2}\.\s?\d{1,2}\.\s?\d{4}')):
                        date_text = elem.strip()
                        break
                    
                    if not date_text:
                        print("No date element found")
                        continue
                else:
                    date_text = date_element.get_text(strip=True)
                
                date_match = re.search(r'(\d{1,2}\.\s?\d{1,2}\.\s?\d{4})', date_text)
                if not date_match:
                    print(f"Date format not matched in: {date_text}")
                    continue
                    
                current_date = date_match.group(1).replace(' ', '')

                # Check if winning combination
                draw_text = draw.get_text().lower()
                is_winning = ("šestica je bila izžrebana" in draw_text or 
                            "je bil izžreban" in draw_text or
                            bool(draw.find('div', class_='winnings')) or
                            'archive-item-prize' in draw.get('class', []) or
                            'dobitna' in draw.get('class', []))

                # Extract numbers - try multiple selectors
                numbers_div = None
                number_selectors = [
                    {'class': 'numbers'},
                    {'class': 'archive-element-numbers'},
                    {'class': 'archive-item-numbers'},
                    {'class': 'stevilke'},
                    {'class': 'loto-numbers'}
                ]
                
                for selector in number_selectors:
                    numbers_div = draw.find('div', class_=selector['class'])
                    if numbers_div:
                        break
                
                if not numbers_div:
                    print("No numbers div found")
                    continue
                    
                main_numbers = []
                additional_number = None
                
                # Find all number elements
                number_elements = numbers_div.find_all(['div', 'span'], class_=lambda x: x and (
                    'number' in x or 
                    'stevilka' in x or 
                    'krog' in x or
                    'ball' in x
                ))
                
                for num in number_elements:
                    try:
                        num_text = ''.join([t for t in num.contents if isinstance(t, str)]).strip()
                        if not num_text.isdigit():
                            continue
                            
                        num_int = int(num_text)
                        
                        # Check if additional number
                        if ('additional' in num.get('class', []) or 
                            num.find_parent('div', class_='additional')):
                            if 1 <= num_int <= 44:
                                additional_number = num_int
                        else:
                            if 1 <= num_int <= 39:
                                main_numbers.append(num_int)
                    except (ValueError, AttributeError) as e:
                        print(f"Error parsing number: {e}")
                        continue

                # Fallback for additional number
                if additional_number is None:
                    additional_div = numbers_div.find('div', class_='additional')
                    if additional_div:
                        try:
                            additional_text = additional_div.get_text(strip=True)
                            additional_match = re.search(r'\d+', additional_text)
                            if additional_match and additional_match.group().isdigit():
                                additional_number = int(additional_match.group())
                        except (ValueError, AttributeError):
                            pass

                if len(main_numbers) >= 6:
                    results.append({
                        'datum': current_date,
                        'stevilke': sorted(main_numbers[:7]),
                        'dodatna_stevilka': additional_number,
                        'winning': is_winning
                    })
                    
                    print(f"Parsed: {current_date} - Numbers: {main_numbers} - Additional: {additional_number}")
                else:
                    print(f"Insufficient numbers ({len(main_numbers)}) for date {current_date}")
                    
            except Exception as e:
                print(f"Error parsing draw: {str(e)}")
                continue
        
        print(f"Successfully parsed {len(results)} draws")
        return results

    @staticmethod
    def check_for_updates():
        try:
            response = requests.get(LoterijaScraper.UPDATE_URL, timeout=5)
            response.raise_for_status()
            data = response.json()
            if data['version'] != LoterijaScraper.VERSION:
                return data['version'], data.get('changelog', '')
            return None, None
        except Exception:
            return None, None

class LoterijaApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Loterijski Analizator - Slovenija v{LoterijaScraper.VERSION}")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        self.bg_color = "#2d2d2d"
        self.fg_color = "#ffffff"
        self.accent_color = "#3a7ebf"
        self.secondary_color = "#1e1e1e"
        self.text_color = "#e0e0e0"
        self.highlight_color = "#4a90d9"
        
        self.root.configure(bg=self.bg_color)
        
        self.configure_styles()
        self.create_menu()
        
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.create_fetch_tab()
        self.create_history_tab()
        self.create_analysis_tab()
        self.create_visualization_tab()
        self.create_generator_tab()
        
        self.data = []
        self.all_numbers = set(range(1, 40))
        self.winning_combinations = set()
        self.history_file = "loto_history.json"
        self.load_history()
        
        self.check_updates()
    
    def configure_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure styles
        self.style.configure('.', 
                           background=self.bg_color,
                           foreground=self.fg_color,
                           font=('Segoe UI', 10))
        
        self.style.configure('TNotebook', 
                           background=self.secondary_color)
        self.style.configure('TNotebook.Tab', 
                           background=self.secondary_color,
                           foreground=self.fg_color,
                           padding=[10, 5],
                           font=('Segoe UI', 9, 'bold'))
        self.style.map('TNotebook.Tab',
                     background=[('selected', self.accent_color)],
                     foreground=[('selected', self.fg_color)])
        
        self.style.configure('Treeview',
                           background=self.secondary_color,
                           foreground=self.fg_color,
                           fieldbackground=self.secondary_color,
                           borderwidth=0)
        self.style.configure('Treeview.Heading',
                           background=self.accent_color,
                           foreground=self.fg_color,
                           font=('Segoe UI', 9, 'bold'),
                           borderwidth=0)
        self.style.map('Treeview',
                      background=[('selected', self.highlight_color)])
        
        self.style.configure('TFrame',
                           background=self.secondary_color)
        self.style.configure('TLabelframe',
                           background=self.secondary_color,
                           foreground=self.fg_color)
        self.style.configure('TLabelframe.Label',
                           foreground=self.fg_color)
        
        self.style.configure('TEntry',
                           fieldbackground=self.secondary_color,
                           foreground=self.text_color,
                           insertcolor=self.fg_color)
        
        self.style.configure('TButton',
                           font=('Segoe UI', 10),
                           foreground=self.fg_color,
                           background=self.secondary_color)
        
        self.style.configure('Accent.TButton',
                           font=('Segoe UI', 10, 'bold'),
                           foreground=self.fg_color,
                           background=self.accent_color)
        self.style.map('Accent.TButton',
                      background=[('active', self.highlight_color)])
        
        self.style.configure('Warning.TButton',
                           foreground=self.fg_color,
                           background='#d9534f')
        
        self.style.configure('Vertical.TScrollbar',
                           background=self.secondary_color,
                           troughcolor=self.bg_color)
        self.style.configure('Horizontal.TScrollbar',
                           background=self.secondary_color,
                           troughcolor=self.bg_color)
    
    def create_menu(self):
        menubar = tk.Menu(self.root, tearoff=0, bg=self.secondary_color, fg=self.fg_color)
        
        help_menu = tk.Menu(menubar, tearoff=0, bg=self.secondary_color, fg=self.fg_color)
        help_menu.add_command(label="Preveri posodobitve", command=self.check_updates)
        help_menu.add_command(label="O programu", command=self.show_about)
        help_menu.add_command(label="Odpri spletno stran", command=lambda: webbrowser.open(LoterijaScraper.PROGRAM_URL))
        
        menubar.add_cascade(label="Pomoč", menu=help_menu)
        self.root.config(menu=menubar)

    def create_fetch_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Pridobi podatke")
        
        fetch_frame = ttk.LabelFrame(tab, text="Pridobi zgodovinske podatke", padding=(15, 10))
        fetch_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        input_frame = ttk.Frame(fetch_frame)
        input_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(input_frame, text="Leto:").grid(row=0, column=0, padx=(0, 5), pady=5, sticky='e')
        
        vcmd = (self.root.register(self.validate_year), '%P')
        self.year_var = tk.StringVar()
        self.year_entry = ttk.Entry(input_frame, width=10, textvariable=self.year_var, validate='key', validatecommand=vcmd)
        self.year_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        
        current_year = datetime.now().year
        self.year_var.set(str(current_year))
        self.year_entry.focus_set()
        self.year_entry.icursor(tk.END)
        self.year_entry.bind('<Return>', lambda event: self.fetch_data())
        
        fetch_btn = ttk.Button(input_frame, text="Pridobi podatke", style='Accent.TButton', command=self.fetch_data)
        fetch_btn.grid(row=0, column=2, padx=5, pady=5)
        
        clear_btn = ttk.Button(input_frame, text="Izbriši zgodovino", style='Warning.TButton', command=self.clear_history)
        clear_btn.grid(row=0, column=3, padx=5, pady=5)
        
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(fetch_frame, textvariable=self.status_var)
        self.status_bar.pack(fill='x', pady=(0, 10))
        
        ttk.Label(fetch_frame, text="Neobdelani podatki:").pack(anchor='w')
        
        text_frame = ttk.Frame(fetch_frame)
        text_frame.pack(fill='both', expand=True)
        
        self.raw_text = tk.Text(text_frame, height=15, wrap=tk.NONE, 
                              font=('Consolas', 10),
                              bg=self.secondary_color,
                              fg=self.fg_color,
                              insertbackground=self.fg_color,
                              selectbackground=self.highlight_color,
                              selectforeground=self.fg_color)
        self.raw_text.grid(row=0, column=0, sticky='nsew')
        
        scroll_y = ttk.Scrollbar(text_frame, orient='vertical', command=self.raw_text.yview)
        scroll_y.grid(row=0, column=1, sticky='ns')
        self.raw_text.configure(yscrollcommand=scroll_y.set)
        
        scroll_x = ttk.Scrollbar(text_frame, orient='horizontal', command=self.raw_text.xview)
        scroll_x.grid(row=1, column=0, sticky='ew')
        self.raw_text.configure(xscrollcommand=scroll_x.set)
        
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)

    def validate_year(self, new_text):
        if new_text == "":
            return True
        if len(new_text) > 4:
            return False
        if not new_text.isdigit():
            return False
        if len(new_text) == 4:
            year = int(new_text)
            current_year = datetime.now().year
            return 1990 <= year <= current_year
        return True
    
    def create_history_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Zgodovina")
        
        tree_frame = ttk.Frame(tab)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.tree = ttk.Treeview(tree_frame, 
                               columns=('Datum', 'Številke', 'Dodatna', 'Dobitna'), 
                               show='headings',
                               selectmode='browse')
        
        self.tree.heading('Datum', text='Datum')
        self.tree.heading('Številke', text='Številke (7)')
        self.tree.heading('Dodatna', text='Dodatna številka')
        self.tree.heading('Dobitna', text='Dobitna kombinacija')
        
        self.tree.column('Datum', width=120, anchor='center')
        self.tree.column('Številke', width=250, anchor='center')
        self.tree.column('Dodatna', width=100, anchor='center')
        self.tree.column('Dobitna', width=100, anchor='center')
        
        y_scroll = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        x_scroll = ttk.Scrollbar(tree_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        
        self.tree.grid(row=0, column=0, sticky='nsew')
        y_scroll.grid(row=0, column=1, sticky='ns')
        x_scroll.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        self.tree.tag_configure('winning', background='#3d5c5c')
        self.tree.tag_configure('normal', background=self.secondary_color)
    
    def create_analysis_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Analiza")
        
        analysis_frame = ttk.LabelFrame(tab, text="Pogostost številk", padding=(15, 10))
        analysis_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        analyze_btn = ttk.Button(analysis_frame, text="Analiziraj", style='Accent.TButton', command=self.analyze_data)
        analyze_btn.pack(pady=(0, 10))
        
        text_frame = ttk.Frame(analysis_frame)
        text_frame.pack(fill='both', expand=True)
        
        self.analysis_text = tk.Text(text_frame, height=20, wrap=tk.WORD, 
                                font=('Segoe UI', 10),
                                bg=self.secondary_color,
                                fg=self.fg_color,
                                insertbackground=self.fg_color,
                                selectbackground=self.highlight_color,
                                selectforeground=self.fg_color)
        self.analysis_text.pack(side='left', fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=self.analysis_text.yview)
        scrollbar.pack(side='right', fill='y')
        self.analysis_text.configure(yscrollcommand=scrollbar.set)
        
        self.analysis_text.tag_configure('header', foreground=self.accent_color, font=('Segoe UI', 10, 'bold'))
        self.analysis_text.tag_configure('divider', foreground=self.accent_color)
        
    def create_visualization_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Vizualizacija")
        
        vis_frame = ttk.LabelFrame(tab, text="Grafični prikaz", padding=(15, 10))
        vis_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.plot_btn = ttk.Button(vis_frame, text="Prikaži graf", style='Accent.TButton', command=self.plot_data)
        self.plot_btn.pack(pady=(0, 10))
        
        plt.style.use('dark_background')
        self.figure = plt.figure(figsize=(10, 6), dpi=100, facecolor=self.secondary_color)
        self.canvas = FigureCanvasTkAgg(self.figure, master=vis_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        
        self.vis_status = ttk.Label(vis_frame, text="Najprej pridobite podatke in jih analizirajte")
        self.vis_status.pack()
    
    def create_generator_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Generator")
        
        gen_frame = ttk.LabelFrame(tab, text="Generator kombinacij", padding=(15, 10))
        gen_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        btn_frame = ttk.Frame(gen_frame)
        btn_frame.pack(fill='x', pady=(0, 10))
        
        gen_btn = ttk.Button(btn_frame, text="Generiraj nove kombinacije", style='Accent.TButton', command=self.generate_new_combinations)
        gen_btn.pack(side='left', padx=(0, 10))
        
        save_btn = ttk.Button(btn_frame, text="Shrani kombinacije", style='Accent.TButton', command=self.save_combinations)
        save_btn.pack(side='left')
        
        text_frame = ttk.Frame(gen_frame)
        text_frame.pack(fill='both', expand=True)
        
        self.generated_text = tk.Text(text_frame, height=15, wrap=tk.WORD, 
                                    font=('Segoe UI', 10),
                                    bg=self.secondary_color,
                                    fg=self.fg_color,
                                    insertbackground=self.fg_color,
                                    selectbackground=self.highlight_color,
                                    selectforeground=self.fg_color)
        self.generated_text.pack(side='left', fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=self.generated_text.yview)
        scrollbar.pack(side='right', fill='y')
        self.generated_text.configure(yscrollcommand=scrollbar.set)
        
        self.gen_status = ttk.Label(gen_frame, text="")
        self.gen_status.pack()
    
    def fetch_data(self):
        year = self.year_var.get().strip()
        if not year.isdigit() or len(year) != 4:
            messagebox.showerror("Napaka", "Vnesite veljavno leto (npr. 2006)")
            return
        
        current_year = datetime.now().year
        year_int = int(year)
        if year_int < 1990 or year_int > current_year:
            messagebox.showerror("Napaka", f"Leto mora biti med 1990 in {current_year}")
            return
        
        self.status_var.set(f"Pridobivam podatke za leto {year}...")
        self.root.update()
        
        try:
            new_results = LoterijaScraper.get_results(year_int)
            
            if not new_results:
                messagebox.showinfo("Info", f"Ni podatkov za leto {year}")
                self.status_var.set(f"Ni podatkov za leto {year}")
                return
            
            existing_entries = {entry['datum']: entry for entry in self.data}
            added_count = 0
            
            for entry in new_results:
                if entry['datum'] not in existing_entries:
                    existing_entries[entry['datum']] = entry
                    added_count += 1
            
            if added_count == 0:
                messagebox.showinfo("Info", "Vsi podatki za to leto so že v bazi")
                self.status_var.set(f"Ni novih podatkov za leto {year}")
                return
                
            self.data = list(existing_entries.values())
            self.update_winning_combinations()
            self.save_history()
            
            self.raw_text.delete(1.0, tk.END)
            self.raw_text.insert(tk.END, json.dumps(new_results, indent=2, ensure_ascii=False))
            
            self.refresh_history()
            
            self.status_var.set(f"Dodanih {added_count} novih zapisov za leto {year} (skupaj {len(self.data)})")
            
        except Exception as e:
            messagebox.showerror("Napaka", f"Napaka pri pridobivanju podatkov: {str(e)}")
            self.status_var.set("Napaka pri pridobivanju podatkov")
    
    def refresh_history(self):
        self.tree.delete(*self.tree.get_children())
        displayed_dates = set()
        
        try:
            sorted_data = sorted(
                self.data,
                key=lambda x: datetime.strptime(x['datum'], '%d.%m.%Y'),
                reverse=True
            )
        except Exception as e:
            print(f"Error sorting data: {e}")
            sorted_data = self.data
        
        added_count = 0
        for entry in sorted_data:
            if entry['datum'] not in displayed_dates:
                try:
                    numbers_display = ', '.join(str(n) for n in sorted(entry['stevilke']))
                    additional_display = str(entry['dodatna_stevilka']) if entry['dodatna_stevilka'] is not None else ''
                    
                    self.tree.insert('', 'end', 
                        values=(
                            entry['datum'],
                            numbers_display,
                            additional_display,
                            'DA' if entry.get('winning', False) else 'NE'
                        ),
                        tags=('winning' if entry.get('winning', False) else 'normal',)
                    )
                    displayed_dates.add(entry['datum'])
                    added_count += 1
                except Exception as e:
                    print(f"Error displaying entry {entry.get('datum', 'unknown')}: {e}")
        
        self.status_var.set(f"Prikazanih {added_count} zapisov (brez podvajanj)")
        print(f"Displayed {added_count} unique entries in history tab")
    
    def update_winning_combinations(self):
        self.winning_combinations = set()
        for entry in self.data:
            if entry['dodatna_stevilka'] is not None:
                combo = tuple(sorted(entry['stevilke'])) + (entry['dodatna_stevilka'],)
                self.winning_combinations.add(combo)
    
    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    
                    unique_entries = {}
                    for entry in loaded_data:
                        date_key = entry['datum']
                        if date_key not in unique_entries:
                            unique_entries[date_key] = entry
                    
                    self.data = list(unique_entries.values())
                    self.update_winning_combinations()
                    self.refresh_history()
                    
                    print(f"Loaded {len(self.data)} unique entries from history file")
            except Exception as e:
                messagebox.showerror("Napaka", f"Napaka pri nalaganju zgodovine: {str(e)}")
                
    def save_history(self):
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            print(f"Saved {len(self.data)} entries to history file")
        except Exception as e:
            messagebox.showerror("Napaka", f"Napaka pri shranjevanju zgodovine: {str(e)}")
    
    def clear_history(self):
        self.data = []
        self.winning_combinations = set()
        self.refresh_history()
        try:
            if os.path.exists(self.history_file):
                os.remove(self.history_file)
            messagebox.showinfo("Info", "Zgodovina izbrisana")
        except Exception as e:
            messagebox.showerror("Napaka", f"Napaka pri brisanju zgodovine: {str(e)}")
    
    def analyze_data(self):
        if not self.data:
            messagebox.showwarning("Opozorilo", "Ni podatkov za analizo")
            return
        
        frequency = defaultdict(int)
        additional_freq = defaultdict(int)
        
        for entry in self.data:
            for num in entry['stevilke']:
                frequency[num] += 1
            
            if entry['dodatna_stevilka'] is not None:
                additional_freq[entry['dodatna_stevilka']] += 1
        
        sorted_freq = sorted(frequency.items(), key=lambda x: x[1], reverse=True)
        sorted_add_freq = sorted(additional_freq.items(), key=lambda x: x[1], reverse=True)
        
        self.analysis_text.delete(1.0, tk.END)
        
        self.analysis_text.insert(tk.END, "Pogostost glavnih številk (1-39):\n", 'header')
        self.analysis_text.insert(tk.END, "="*30 + "\n", 'divider')
        for num, count in sorted_freq:
            self.analysis_text.insert(tk.END, f"Številka {num}: {count} pojavitev\n")
        
        self.analysis_text.insert(tk.END, "\nPogostost dodatnih številk (1-44):\n", 'header')
        self.analysis_text.insert(tk.END, "="*30 + "\n", 'divider')
        for num, count in sorted_add_freq:
            self.analysis_text.insert(tk.END, f"Dodatna številka {num}: {count} pojavitev\n")
        
        pair_freq = defaultdict(int)
        triplet_freq = defaultdict(int)
        
        for entry in self.data:
            numbers = entry['stevilke']
            
            for pair in combinations(sorted(numbers), 2):
                pair_freq[pair] += 1
            
            for triplet in combinations(sorted(numbers), 3):
                triplet_freq[triplet] += 1
        
        sorted_pairs = sorted(pair_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        self.analysis_text.insert(tk.END, "\nTOP 10 parov:\n", 'header')
        for pair, count in sorted_pairs:
            self.analysis_text.insert(tk.END, f"{pair[0]} & {pair[1]}: {count} pojavitev\n")
        
        sorted_triplets = sorted(triplet_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        self.analysis_text.insert(tk.END, "\nTOP 10 trojčkov:\n", 'header')
        for triplet, count in sorted_triplets:
            self.analysis_text.insert(tk.END, f"{triplet[0]}, {triplet[1]}, {triplet[2]}: {count} pojavitev\n")
        
        self.vis_status.config(text="Podatki so pripravljeni za vizualizacijo")
    
    def plot_data(self):
        if not self.data:
            messagebox.showwarning("Opozorilo", "Ni podatkov za vizualizacijo")
            return
        
        frequency = defaultdict(int)
        for entry in self.data:
            for num in entry['stevilke']:
                frequency[num] += 1
            
            if entry['dodatna_stevilka'] is not None:
                frequency[entry['dodatna_stevilka']] += 1
        
        numbers = sorted(frequency.keys())
        counts = [frequency[num] for num in numbers]
        
        self.figure.clear()
        
        ax = self.figure.add_subplot(111)
        ax.bar(numbers, counts, color=self.accent_color)
        ax.set_title('Pogostost številk v žrebanjih', fontsize=12, pad=20, color=self.fg_color)
        ax.set_xlabel('Številka', fontsize=10, color=self.fg_color)
        ax.set_ylabel('Število pojavitev', fontsize=10, color=self.fg_color)
        ax.grid(True, linestyle='--', alpha=0.3)
        
        ax.set_facecolor(self.secondary_color)
        self.figure.set_facecolor(self.secondary_color)
        ax.tick_params(colors=self.fg_color)
        for spine in ax.spines.values():
            spine.set_color(self.fg_color)
        
        self.canvas.draw()
    
    def generate_new_combinations(self):
        if not self.data:
            messagebox.showwarning("Opozorilo", "Najprej pridobite podatke")
            return
        
        self.generated_text.delete(1.0, tk.END)
        
        generated = set()
        attempts = 0
        max_attempts = 1000
        
        while len(generated) < 10 and attempts < max_attempts:
            attempts += 1
            
            main_numbers = sorted(random.sample(range(1, 40), 7))
            additional_number = random.randint(1, 44)
            
            combo = tuple(main_numbers) + (additional_number,)
            
            if combo not in self.winning_combinations and combo not in generated:
                generated.add(combo)
                self.generated_text.insert(tk.END, 
                    f"Kombinacija {len(generated)}:\n"
                    f"Glavne številke: {', '.join(map(str, main_numbers))}\n"
                    f"Dodatna številka: {additional_number}\n\n"
                )
        
        if len(generated) < 10:
            self.gen_status.config(text=f"Ustvarjenih le {len(generated)} unikatnih kombinacij")
        else:
            self.gen_status.config(text="Ustvarjenih 10 novih kombinacij")
    
    def save_combinations(self):
        content = self.generated_text.get("1.0", tk.END)
        if not content.strip():
            messagebox.showwarning("Opozorilo", "Ni kombinacij za shranjevanje")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile="loto_kombinacije.txt"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Uspeh", f"Kombinacije shranjene v {file_path}")
            except Exception as e:
                messagebox.showerror("Napaka", f"Napaka pri shranjevanju: {str(e)}")
    
    def show_about(self):
        about_window = tk.Toplevel(self.root)
        about_window.title("O programu")
        about_window.geometry("500x400")
        about_window.resizable(False, False)
        about_window.configure(bg=self.bg_color)
        
        window_width = 500
        window_height = 400
        screen_width = about_window.winfo_screenwidth()
        screen_height = about_window.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        about_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        main_frame = ttk.Frame(about_window)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        title_label = ttk.Label(
            main_frame,
            text="Loterijski Analizator - Slovenija",
            font=('Segoe UI', 14, 'bold')
        )
        title_label.pack(pady=(0, 10))
        
        version_frame = ttk.Frame(main_frame)
        version_frame.pack(fill='x', pady=5)
        
        ttk.Label(
            version_frame,
            text="Različica:",
            font=('Segoe UI', 10, 'bold')
        ).pack(side='left')
        
        ttk.Label(
            version_frame,
            text=LoterijaScraper.VERSION,
            font=('Segoe UI', 10)
        ).pack(side='left', padx=5)
        
        features_frame = ttk.LabelFrame(
            main_frame,
            text="Funkcije programa"
        )
        features_frame.pack(fill='both', expand=True, pady=10)
        
        features = [
            "• Pridobivanje zgodovinskih podatkov LOTO žrebanj",
            "• Analiza pogostosti številk",
            "• Vizualizacija podatkov s grafom",
            "• Generator naključnih kombinacij",
            "• Shranjevanje zgodovine žrebanj",
            "• Preverjanje posodobitev"
        ]
        
        for feature in features:
            ttk.Label(
                features_frame,
                text=feature,
                anchor='w'
            ).pack(fill='x', padx=10, pady=2)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(10, 0))
        
        update_btn = ttk.Button(
            button_frame,
            text="Preveri posodobitve",
            style='Accent.TButton',
            command=self.check_updates
        )
        update_btn.pack(side='left', padx=5)
        
        close_btn = ttk.Button(
            button_frame,
            text="Zapri",
            style='Accent.TButton',
            command=about_window.destroy
        )
        close_btn.pack(side='right', padx=5)
        
        link_frame = ttk.Frame(main_frame)
        link_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Label(
            link_frame,
            text="Spletna stran:"
        ).pack(side='left')
        
        link_label = ttk.Label(
            link_frame,
            text=LoterijaScraper.PROGRAM_URL,
            foreground='#4a90d9',
            cursor='hand2'
        )
        link_label.pack(side='left', padx=5)
        link_label.bind('<Button-1>', lambda e: webbrowser.open(LoterijaScraper.PROGRAM_URL))

    def check_updates(self):
        try:
            new_version, changelog = LoterijaScraper.check_for_updates()
            
            if new_version:
                update_window = tk.Toplevel(self.root)
                update_window.title("Posodobitev")
                update_window.geometry("600x400")
                update_window.resizable(False, False)
                update_window.configure(bg=self.bg_color)
                
                window_width = 600
                window_height = 400
                screen_width = update_window.winfo_screenwidth()
                screen_height = update_window.winfo_screenheight()
                x = (screen_width // 2) - (window_width // 2)
                y = (screen_height // 2) - (window_height // 2)
                update_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
                
                main_frame = ttk.Frame(update_window)
                main_frame.pack(fill='both', expand=True, padx=20, pady=20)
                
                ttk.Label(
                    main_frame,
                    text="Na voljo je nova različica!",
                    font=('Segoe UI', 14, 'bold')
                ).pack(pady=(0, 10))
                
                version_frame = ttk.Frame(main_frame)
                version_frame.pack(fill='x', pady=5)
                
                ttk.Label(
                    version_frame,
                    text="Trenutna različica:"
                ).pack(side='left')
                
                ttk.Label(
                    version_frame,
                    text=LoterijaScraper.VERSION,
                    foreground='#ff5555'
                ).pack(side='left', padx=5)
                
                ttk.Label(
                    version_frame,
                    text="Nova različica:"
                ).pack(side='left', padx=(20, 0))
                
                ttk.Label(
                    version_frame,
                    text=new_version,
                    foreground='#55ff55'
                ).pack(side='left', padx=5)
                
                changelog_frame = ttk.LabelFrame(
                    main_frame,
                    text="Novosti v različici"
                )
                changelog_frame.pack(fill='both', expand=True, pady=10)
                
                changelog_text = tk.Text(
                    changelog_frame,
                    wrap=tk.WORD,
                    bg=self.secondary_color,
                    fg=self.fg_color,
                    font=('Segoe UI', 9),
                    padx=10,
                    pady=10,
                    highlightthickness=0,
                    borderwidth=0
                )
                changelog_text.pack(fill='both', expand=True)
                changelog_text.insert(tk.END, changelog)
                changelog_text.configure(state='disabled')
                
                button_frame = ttk.Frame(main_frame)
                button_frame.pack(fill='x', pady=(10, 0))
                
                download_btn = ttk.Button(
                    button_frame,
                    text="Prenesi posodobitev",
                    style='Accent.TButton',
                    command=lambda: webbrowser.open(LoterijaScraper.PROGRAM_URL)
                )
                download_btn.pack(side='left', padx=5)
                
                close_btn = ttk.Button(
                    button_frame,
                    text="Zapri",
                    style='Accent.TButton',
                    command=update_window.destroy
                )
                close_btn.pack(side='right', padx=5)
                
            else:
                messagebox.showinfo("Posodobitev", "Imate najnovejšo različico programa")
                
        except Exception as e:
            messagebox.showerror("Napaka", f"Napaka pri preverjanju posodobitev: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = LoterijaApp(root)
    root.mainloop()