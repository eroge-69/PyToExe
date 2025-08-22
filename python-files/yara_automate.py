import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import yara
import threading
import json
import csv
import datetime
from pathlib import Path
import hashlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
import webbrowser

class ProfessionalYaraScanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Enterprise YARA Scanner v2.0")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        
        # Variables
        self.target_path = tk.StringVar()
        self.rules_path = tk.StringVar()
        self.scanning = False
        self.compiled_rules = None
        self.scan_results = []
        self.rule_stats = {}
        self.recent_rules_folders = []
        self.recent_targets = []
        
        # Load settings
        self.load_settings()
        
        # Setup UI
        self.setup_ui()
        
        # Initialize with saved paths if available
        if self.recent_rules_folders:
            self.rules_path.set(self.recent_rules_folders[0])
        if self.recent_targets:
            self.target_path.set(self.recent_targets[0])
        
    def configure_styles(self):
        # Configure styles for a professional look
        self.style.configure('Title.TLabel', 
                            font=('Helvetica', 16, 'bold'),
                            foreground='#2c3e50')
        self.style.configure('Subtitle.TLabel',
                            font=('Helvetica', 10),
                            foreground='#7f8c8d')
        self.style.configure('Action.TButton',
                            font=('Helvetica', 10, 'bold'),
                            foreground='white',
                            background='#3498db',
                            borderwidth=1)
        self.style.map('Action.TButton',
                      background=[('active', '#2980b9')])
        self.style.configure('Success.TButton',
                            font=('Helvetica', 10, 'bold'),
                            foreground='white',
                            background='#27ae60',
                            borderwidth=1)
        self.style.map('Success.TButton',
                      background=[('active', '#229954')])
        self.style.configure('Danger.TButton',
                            font=('Helvetica', 10, 'bold'),
                            foreground='white',
                            background='#e74c3c',
                            borderwidth=1)
        self.style.map('Danger.TButton',
                      background=[('active', '#c0392b')])
        self.style.configure('Panel.TFrame',
                            background='#ecf0f1',
                            borderwidth=1,
                            relief='sunken')
        self.style.configure('PanelHeader.TLabel',
                            font=('Helvetica', 11, 'bold'),
                            foreground='#2c3e50',
                            background='#dfe6e9')
        
    def setup_ui(self):
        # Create main paned window for resizable panels
        main_pane = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel for controls
        left_frame = ttk.Frame(main_pane, width=400, style='Panel.TFrame')
        main_pane.add(left_frame, weight=1)
        
        # Right panel for results
        right_frame = ttk.Frame(main_pane)
        main_pane.add(right_frame, weight=2)
        
        # Configure grid weights
        left_frame.columnconfigure(1, weight=1)
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)
        
        # Application title
        title_frame = ttk.Frame(left_frame)
        title_frame.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky=tk.EW)
        
        # Load and display logo
        try:
            logo_image = Image.new('RGB', (32, 32), color='#3498db')
            logo_photo = ImageTk.PhotoImage(logo_image)
            logo_label = ttk.Label(title_frame, image=logo_photo)
            logo_label.image = logo_photo
            logo_label.grid(row=0, column=0, padx=(0, 10))
        except:
            pass  # If image loading fails, continue without logo
        
        ttk.Label(title_frame, text="Enterprise YARA Scanner", style='Title.TLabel').grid(row=0, column=1, sticky=tk.W)
        ttk.Label(title_frame, text="Advanced malware detection and analysis", style='Subtitle.TLabel').grid(row=1, column=1, sticky=tk.W)
        
        # Settings panel
        settings_frame = ttk.LabelFrame(left_frame, text=" Scan Settings ", style='Panel.TFrame')
        settings_frame.grid(row=1, column=0, columnspan=2, sticky=tk.EW, padx=5, pady=5)
        
        # Target selection
        ttk.Label(settings_frame, text="Target to Scan:").grid(row=0, column=0, sticky=tk.W, pady=5)
        target_combo = ttk.Combobox(settings_frame, textvariable=self.target_path, values=self.recent_targets)
        target_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Button(settings_frame, text="Browse File", command=self.browse_file, width=12).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(settings_frame, text="Browse Folder", command=self.browse_folder, width=12).grid(row=0, column=3, padx=5, pady=5)
        
        # Rules selection
        ttk.Label(settings_frame, text="YARA Rules Folder:").grid(row=1, column=0, sticky=tk.W, pady=5)
        rules_combo = ttk.Combobox(settings_frame, textvariable=self.rules_path, values=self.recent_rules_folders)
        rules_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Button(settings_frame, text="Select Folder", command=self.browse_rules_folder, width=12).grid(row=1, column=2, columnspan=2, padx=5, pady=5)
        
        # Scan options
        options_frame = ttk.Frame(settings_frame)
        options_frame.grid(row=2, column=0, columnspan=4, pady=10, sticky=tk.EW)
        
        self.fast_scan = tk.BooleanVar(value=True)
        self.recursive_scan = tk.BooleanVar(value=True)
        self.gen_hashes = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(options_frame, text="Fast Scan", variable=self.fast_scan).grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(options_frame, text="Recursive Scan", variable=self.recursive_scan).grid(row=0, column=1, sticky=tk.W)
        ttk.Checkbutton(options_frame, text="Generate Hashes", variable=self.gen_hashes).grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
        # Action buttons
        button_frame = ttk.Frame(left_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky=tk.EW)
        
        ttk.Button(button_frame, text="Compile Rules", command=self.compile_rules, style='Action.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Start Scan", command=self.start_scan, style='Success.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Stop Scan", command=self.stop_scan, style='Danger.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Results", command=self.clear_results).pack(side=tk.LEFT, padx=5)
        
        # Progress frame
        progress_frame = ttk.Frame(left_frame)
        progress_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky=tk.EW)
        
        self.progress = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=5)
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(progress_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X)
        
        # Rules statistics panel
        stats_frame = ttk.LabelFrame(left_frame, text=" Rules Statistics ", style='Panel.TFrame')
        stats_frame.grid(row=4, column=0, columnspan=2, sticky=tk.EW, padx=5, pady=5)
        
        self.rules_count_var = tk.StringVar(value="Total Rules: 0")
        ttk.Label(stats_frame, textvariable=self.rules_count_var).pack(anchor=tk.W, pady=2)
        
        self.rules_loaded_var = tk.StringVar(value="Rules Loaded: No")
        ttk.Label(stats_frame, textvariable=self.rules_loaded_var).pack(anchor=tk.W, pady=2)
        
        # Quick actions panel
        actions_frame = ttk.LabelFrame(left_frame, text=" Quick Actions ", style='Panel.TFrame')
        actions_frame.grid(row=5, column=0, columnspan=2, sticky=tk.EW, padx=5, pady=5)
        
        ttk.Button(actions_frame, text="Export Results", command=self.export_results).pack(fill=tk.X, pady=2)
        ttk.Button(actions_frame, text="View Rule Details", command=self.view_rule_details).pack(fill=tk.X, pady=2)
        ttk.Button(actions_frame, text="Create Rule Pack", command=self.create_rule_pack).pack(fill=tk.X, pady=2)
        ttk.Button(actions_frame, text="Settings", command=self.show_settings).pack(fill=tk.X, pady=2)
        
        # Right panel - Results area
        results_header = ttk.Label(right_frame, text="Scan Results", style='PanelHeader.TLabel')
        results_header.grid(row=0, column=0, sticky=tk.EW, pady=(0, 5))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.grid(row=1, column=0, sticky=tk.NSEW, pady=5)
        
        # Results tab
        results_tab = ttk.Frame(self.notebook)
        self.notebook.add(results_tab, text="Scan Results")
        
        # Create text area with scrollbar
        results_frame = ttk.Frame(results_tab)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, height=20, font=('Consolas', 10))
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Statistics tab
        stats_tab = ttk.Frame(self.notebook)
        self.notebook.add(stats_tab, text="Statistics")
        
        # Add a frame for statistics
        stats_display_frame = ttk.Frame(stats_tab)
        stats_display_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.stats_text = scrolledtext.ScrolledText(stats_display_frame, wrap=tk.WORD, height=10)
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        
        # Rule details tab
        rules_tab = ttk.Frame(self.notebook)
        self.notebook.add(rules_tab, text="Rule Details")
        
        rules_frame = ttk.Frame(rules_tab)
        rules_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.rules_text = scrolledtext.ScrolledText(rules_frame, wrap=tk.WORD, height=10, font=('Consolas', 10))
        self.rules_text.pack(fill=tk.BOTH, expand=True)
        
        # Dashboard tab
        dashboard_tab = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_tab, text="Dashboard")
        
        # Add dashboard content
        dashboard_frame = ttk.Frame(dashboard_tab)
        dashboard_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add some dashboard widgets
        ttk.Label(dashboard_frame, text="Scan Activity Overview", style='PanelHeader.TLabel').pack(fill=tk.X, pady=5)
        
        # Placeholder for charts
        chart_frame = ttk.Frame(dashboard_frame)
        chart_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Footer
        footer_frame = ttk.Frame(right_frame)
        footer_frame.grid(row=2, column=0, sticky=tk.EW, pady=5)
        
        ttk.Label(footer_frame, text="© 2023 Enterprise YARA Scanner v2.0").pack(side=tk.LEFT)
        ttk.Button(footer_frame, text="Help", command=self.show_help).pack(side=tk.RIGHT, padx=5)
        ttk.Button(footer_frame, text="About", command=self.show_about).pack(side=tk.RIGHT)
        
    def browse_file(self):
        filename = filedialog.askopenfilename(title="Select file to scan")
        if filename:
            self.target_path.set(filename)
            if filename not in self.recent_targets:
                self.recent_targets.insert(0, filename)
                if len(self.recent_targets) > 5:
                    self.recent_targets.pop()
                self.save_settings()
            
    def browse_folder(self):
        folder = filedialog.askdirectory(title="Select folder to scan")
        if folder:
            self.target_path.set(folder)
            if folder not in self.recent_targets:
                self.recent_targets.insert(0, folder)
                if len(self.recent_targets) > 5:
                    self.recent_targets.pop()
                self.save_settings()
            
    def browse_rules_folder(self):
        folder = filedialog.askdirectory(title="Select folder containing YARA rules")
        if folder:
            self.rules_path.set(folder)
            if folder not in self.recent_rules_folders:
                self.recent_rules_folders.insert(0, folder)
                if len(self.recent_rules_folders) > 5:
                    self.recent_rules_folders.pop()
                self.save_settings()
            
    def compile_rules(self):
        rules_dir = self.rules_path.get()
        if not rules_dir:
            messagebox.showerror("Error", "Please select a folder containing YARA rules first.")
            return
            
        try:
            # Find all .yar and .yara files in the directory
            rule_files = {}
            rule_count = 0
            for ext in ['*.yar', '*.yara']:
                for file_path in Path(rules_dir).rglob(ext):
                    rule_name = file_path.stem
                    rule_files[rule_name] = str(file_path)
                    rule_count += 1
            
            if not rule_files:
                messagebox.showerror("Error", "No YARA rules files (.yar or .yara) found in the selected directory.")
                return
                
            # Compile rules
            self.compiled_rules = yara.compile(filepaths=rule_files)
            self.rules_count_var.set(f"Total Rules: {rule_count}")
            self.rules_loaded_var.set("Rules Loaded: Yes")
            
            # Update rule details tab
            self.update_rule_details(rule_files)
            
            self.status_var.set(f"Rules compiled successfully: {rule_count} rules loaded")
            messagebox.showinfo("Success", f"Rules compiled successfully: {len(rule_files)} rules loaded")
            
        except yara.SyntaxError as e:
            messagebox.showerror("Compilation Error", f"Syntax error in YARA rules: {str(e)}")
        except yara.Error as e:
            messagebox.showerror("Compilation Error", f"Error compiling YARA rules: {str(e)}")
        except Exception as e:
            messagebox.showerror("Compilation Error", f"Unexpected error: {str(e)}")
            
    def update_rule_details(self, rule_files):
        """Update the rule details tab with information about loaded rules"""
        self.rules_text.delete(1.0, tk.END)
        
        for rule_name, rule_path in rule_files.items():
            try:
                with open(rule_path, 'r') as f:
                    rule_content = f.read()
                
                self.rules_text.insert(tk.END, f"Rule: {rule_name}\n")
                self.rules_text.insert(tk.END, f"Path: {rule_path}\n")
                self.rules_text.insert(tk.END, "-" * 50 + "\n")
                self.rules_text.insert(tk.END, rule_content)
                self.rules_text.insert(tk.END, "\n" + "="*80 + "\n\n")
            except:
                self.rules_text.insert(tk.END, f"Could not read rule: {rule_name}\n\n")
            
    def start_scan(self):
        if self.scanning:
            return
            
        if not self.compiled_rules:
            messagebox.showerror("Error", "Please compile rules first.")
            return
            
        target = self.target_path.get()
        if not target:
            messagebox.showerror("Error", "Please select a file or folder to scan.")
            return
            
        # Start scan in a separate thread
        self.scanning = True
        self.progress.start()
        self.status_var.set("Scanning...")
        
        # Clear previous results
        self.scan_results = []
        self.rule_stats = {}
        self.results_text.delete(1.0, tk.END)
        self.stats_text.delete(1.0, tk.END)
        
        scan_thread = threading.Thread(target=self.perform_scan, args=(target,))
        scan_thread.daemon = True
        scan_thread.start()
        
    def stop_scan(self):
        if self.scanning:
            self.scanning = False
            self.status_var.set("Scan stopped")
            self.progress.stop()
            
    def perform_scan(self, target_path):
        try:
            start_time = datetime.datetime.now()
            
            if os.path.isfile(target_path):
                self.scan_file(target_path)
            else:
                self.scan_folder(target_path)
                
            end_time = datetime.datetime.now()
            scan_duration = end_time - start_time
            
            # Update statistics
            self.update_statistics(scan_duration)
            
            self.status_var.set("Scan completed")
            
        except Exception as e:
            self.results_text.insert(tk.END, f"Error during scan: {str(e)}\n")
            self.status_var.set("Scan error")
            
        finally:
            self.scanning = False
            self.progress.stop()
            
    def scan_file(self, file_path):
        try:
            file_info = {
                'path': file_path,
                'size': os.path.getsize(file_path),
                'matches': [],
                'hash': None
            }
            
            if self.gen_hashes.get():
                file_info['hash'] = self.calculate_hash(file_path)
            
            matches = self.compiled_rules.match(file_path)
            
            if matches:
                for match in matches:
                    file_info['matches'].append({
                        'rule': match.rule,
                        'tags': match.tags,
                        'meta': match.meta
                    })
                    
                    # Update rule statistics
                    if match.rule in self.rule_stats:
                        self.rule_stats[match.rule]['count'] += 1
                    else:
                        self.rule_stats[match.rule] = {
                            'count': 1,
                            'meta': match.meta
                        }
            
            self.scan_results.append(file_info)
            
            # Update UI with results
            self.update_results_ui(file_info)
                
        except Exception as e:
            error_info = {
                'path': file_path,
                'error': str(e),
                'matches': []
            }
            self.scan_results.append(error_info)
            self.results_text.insert(tk.END, f"Error scanning {file_path}: {str(e)}\n\n")
            
    def scan_folder(self, folder_path):
        file_count = 0
        match_count = 0
        
        for root, _, files in os.walk(folder_path):
            for file in files:
                if not self.scanning:
                    self.results_text.insert(tk.END, "Scan stopped by user\n")
                    return
                    
                file_path = os.path.join(root, file)
                
                # Skip files that are too large for fast scanning
                if self.fast_scan.get() and os.path.getsize(file_path) > 10 * 1024 * 1024:  # 10MB
                    continue
                    
                try:
                    self.scan_file(file_path)
                    file_count += 1
                    
                    # Update status every 10 files
                    if file_count % 10 == 0:
                        match_count = sum(1 for result in self.scan_results if result['matches'])
                        self.status_var.set(f"Scanning... {file_count} files processed, {match_count} with matches")
                        
                except Exception as e:
                    # Skip files that can't be read or scanned
                    continue
                    
        match_count = sum(1 for result in self.scan_results if result.get('matches'))
        error_count = sum(1 for result in self.scan_results if result.get('error'))
        
        self.results_text.insert(tk.END, f"\nScan completed. Processed {file_count} files, "
                                        f"found matches in {match_count} files, "
                                        f"{error_count} errors.\n")
        
    def calculate_hash(self, file_path):
        """Calculate MD5 hash of a file"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except:
            return "Error calculating hash"
        
    def update_results_ui(self, file_info):
        """Update the results UI with information about a scanned file"""
        if file_info.get('error'):
            self.results_text.insert(tk.END, f"File: {file_info['path']} - ERROR: {file_info['error']}\n\n")
            return
            
        if file_info['matches']:
            result = f"File: {file_info['path']}\n"
            result += f"Size: {file_info['size']} bytes\n"
            
            if file_info['hash']:
                result += f"MD5: {file_info['hash']}\n"
                
            result += "Matches:\n"
            
            for match in file_info['matches']:
                result += f"  Rule: {match['rule']}\n"
                if match['tags']:
                    result += f"    Tags: {', '.join(match['tags'])}\n"
                if match['meta']:
                    result += f"    Meta: {match['meta']}\n"
                    
            result += "\n"
            self.results_text.insert(tk.END, result)
        else:
            self.results_text.insert(tk.END, f"File: {file_info['path']} - No matches found\n\n")
            
    def update_statistics(self, scan_duration):
        """Update the statistics tab with scan results"""
        total_files = len(self.scan_results)
        files_with_matches = sum(1 for result in self.scan_results if result.get('matches'))
        error_count = sum(1 for result in self.scan_results if result.get('error'))
        
        self.stats_text.insert(tk.END, "SCAN STATISTICS\n")
        self.stats_text.insert(tk.END, "=" * 50 + "\n\n")
        self.stats_text.insert(tk.END, f"Scan started: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.stats_text.insert(tk.END, f"Duration: {scan_duration.total_seconds():.2f} seconds\n")
        self.stats_text.insert(tk.END, f"Total files scanned: {total_files}\n")
        self.stats_text.insert(tk.END, f"Files with matches: {files_with_matches}\n")
        self.stats_text.insert(tk.END, f"Errors: {error_count}\n\n")
        
        self.stats_text.insert(tk.END, "RULE STATISTICS\n")
        self.stats_text.insert(tk.END, "=" * 50 + "\n\n")
        
        for rule, stats in self.rule_stats.items():
            self.stats_text.insert(tk.END, f"Rule: {rule}\n")
            self.stats_text.insert(tk.END, f"  Matches: {stats['count']}\n")
            if stats.get('meta'):
                self.stats_text.insert(tk.END, f"  Meta: {stats['meta']}\n")
            self.stats_text.insert(tk.END, "\n")
            
    def clear_results(self):
        self.results_text.delete(1.0, tk.END)
        self.stats_text.delete(1.0, tk.END)
        self.scan_results = []
        self.rule_stats = {}
        
    def export_results(self):
        """Export scan results to a file"""
        if not self.scan_results:
            messagebox.showwarning("Export", "No results to export.")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv"), ("Text files", "*.txt")]
        )
        
        if not file_path:
            return
            
        try:
            if file_path.endswith('.json'):
                with open(file_path, 'w') as f:
                    json.dump(self.scan_results, f, indent=2)
            elif file_path.endswith('.csv'):
                with open(file_path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['File', 'Size', 'Matches', 'Hash'])
                    for result in self.scan_results:
                        matches = "; ".join([m['rule'] for m in result.get('matches', [])])
                        writer.writerow([
                            result['path'],
                            result.get('size', ''),
                            matches,
                            result.get('hash', '')
                        ])
            else:
                with open(file_path, 'w') as f:
                    for result in self.scan_results:
                        f.write(f"File: {result['path']}\n")
                        if 'size' in result:
                            f.write(f"Size: {result['size']} bytes\n")
                        if 'hash' in result:
                            f.write(f"Hash: {result['hash']}\n")
                        if 'matches' in result and result['matches']:
                            f.write("Matches:\n")
                            for match in result['matches']:
                                f.write(f"  Rule: {match['rule']}\n")
                                if match['tags']:
                                    f.write(f"    Tags: {', '.join(match['tags'])}\n")
                        f.write("\n")
                        
            messagebox.showinfo("Export", "Results exported successfully.")
        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting results: {str(e)}")
            
    def view_rule_details(self):
        """Show rule details dialog"""
        if not self.compiled_rules:
            messagebox.showwarning("Rule Details", "No rules loaded. Please compile rules first.")
            return
            
        # Select the rules tab
        self.notebook.select(2)
        
    def create_rule_pack(self):
        """Create a rule pack from selected rules"""
        messagebox.showinfo("Info", "This feature would allow you to create a custom rule pack from selected rules.")
        
    def show_settings(self):
        """Show settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x300")
        
        ttk.Label(settings_window, text="Application Settings", style='Title.TLabel').pack(pady=10)
        
        # Add some settings controls
        ttk.Checkbutton(settings_window, text="Enable automatic updates", variable=tk.BooleanVar(value=True)).pack(anchor=tk.W, padx=20, pady=5)
        ttk.Checkbutton(settings_window, text="Send anonymous usage statistics", variable=tk.BooleanVar(value=False)).pack(anchor=tk.W, padx=20, pady=5)
        
        ttk.Label(settings_window, text="Max recent items:").pack(anchor=tk.W, padx=20, pady=(20, 5))
        ttk.Spinbox(settings_window, from_=1, to=10, width=5).pack(anchor=tk.W, padx=20)
        
        ttk.Button(settings_window, text="Save", command=settings_window.destroy).pack(pady=20)
        
    def show_help(self):
        """Show help information"""
        webbrowser.open("https://yara.readthedocs.io/")
        
    def show_about(self):
        """Show about dialog"""
        about_text = """
        Enterprise YARA Scanner v2.0
        
        A professional malware detection tool using YARA rules.
        
        Features:
        - Advanced file scanning with YARA rules
        - Comprehensive results reporting
        - Statistical analysis of scan results
        - Export functionality for results
        - Professional user interface
        
        Built with Python and Tkinter.
        """
        
        messagebox.showinfo("About", about_text)
        
    def load_settings(self):
        """Load application settings"""
        try:
            config_path = os.path.expanduser("~/.yara_scanner_config.json")
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    self.recent_rules_folders = config.get('recent_rules_folders', [])
                    self.recent_targets = config.get('recent_targets', [])
        except:
            # If loading fails, use defaults
            self.recent_rules_folders = []
            self.recent_targets = []
            
    def save_settings(self):
        """Save application settings"""
        try:
            config = {
                'recent_rules_folders': self.recent_rules_folders,
                'recent_targets': self.recent_targets
            }
            
            config_path = os.path.expanduser("~/.yara_scanner_config.json")
            with open(config_path, 'w') as f:
                json.dump(config, f)
        except:
            pass  # Silently fail if saving settings doesn't work

def main():
    root = tk.Tk()
    app = ProfessionalYaraScanner(root)
    root.mainloop()

if __name__ == "__main__":
    main()