import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import numpy as np
import os
import re
from datetime import datetime

class LaserLabSearchGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🔬 Laser Lab Data Search Tool - Complete Edition")
        self.root.geometry("1200x900")
        self.root.configure(bg='#f0f2f5')
        
        # Variables
        self.file_path = tk.StringVar()
        self.search_mode = tk.StringVar(value="PCI")
        
        # PCI sheet variables
        self.sheet_vars = {
            'PCI 1064nm': tk.BooleanVar(value=True),
            'PCI 355nm': tk.BooleanVar(value=True),
            'PCI 266': tk.BooleanVar(value=True)
        }
        
        # PCI search variables
        self.pci_vars = {
            'sample_type': tk.StringVar(),
            'absorption_before': tk.StringVar(),
            'absorption_after': tk.StringVar(),
            'coating_type': tk.StringVar(),
            'design': tk.StringVar(),
            'aoi': tk.StringVar()
        }
        
        # CRD search variables
        self.crd_vars = {
            'angle': tk.StringVar(),
            'loss_ba_s': tk.StringVar(),
            'loss_ba_p': tk.StringVar(),
            'loss_aa_s': tk.StringVar(),
            'loss_aa_p': tk.StringVar(),
            'refl_ba_s': tk.StringVar(),
            'refl_ba_p': tk.StringVar(),
            'refl_aa_s': tk.StringVar(),
            'refl_aa_p': tk.StringVar()
        }
        
        # CRD tolerance variables (still used for exact value + tolerance mode)
        self.crd_tol_vars = {
            'loss_ba_s': tk.StringVar(),
            'loss_ba_p': tk.StringVar(),
            'loss_aa_s': tk.StringVar(),
            'loss_aa_p': tk.StringVar(),
            'refl_ba_s': tk.StringVar(),
            'refl_ba_p': tk.StringVar(),
            'refl_aa_s': tk.StringVar(),
            'refl_aa_p': tk.StringVar()
        }
        
        # Reflectometer search variables
        self.refl_vars = {
            'aoi': tk.StringVar(),
            'reflectivity': tk.StringVar(),
            'refl_tolerance': tk.StringVar(),
            'transmission': tk.StringVar(),
            'trans_tolerance': tk.StringVar(),
            'polarization': tk.StringVar()
        }
        
        # Thesaurus search variables
        self.thesaurus_vars = {
            'search_term': tk.StringVar(),
            'category': tk.StringVar(value="all")
        }
        
        # CRD column mapping
        self.crd_column_map = {
            'angle': 'Angle of meaurment',
            'loss_ba_s': 'Loss (ppm) | Before Anneal | S-Pol',
            'loss_ba_p': 'Loss (ppm) | Before Anneal | P-Pol',
            'loss_aa_s': 'Loss (ppm) | After Anneal | S-Pol',
            'loss_aa_p': 'Loss (ppm) | After Anneal | P-Pol',
            'refl_ba_s': 'Reflection (%) | Before Anneal | S-Pol',
            'refl_ba_p': 'Reflection (%) | Before Anneal | P-Pol',
            'refl_aa_s': 'Reflection (%) | After Anneal | S-Pol',
            'refl_aa_p': 'Reflection (%) | After Anneal | P-Pol'
        }
        
        self.crd_display_labels = {
            'angle': 'Angle',
            'loss_ba_s': 'Loss BA S-Pol',
            'loss_ba_p': 'Loss BA P-Pol',
            'loss_aa_s': 'Loss AA S-Pol',
            'loss_aa_p': 'Loss AA P-Pol',
            'refl_ba_s': 'Refl BA S-Pol',
            'refl_ba_p': 'Refl BA P-Pol',
            'refl_aa_s': 'Refl AA S-Pol',
            'refl_aa_p': 'Refl AA P-Pol'
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure custom styles
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), background='#f0f2f5')
        style.configure('Heading.TLabel', font=('Arial', 12, 'bold'), background='#f0f2f5')
        style.configure('Custom.TFrame', background='#ffffff', relief='raised', borderwidth=1)
        style.configure('Search.TButton', font=('Arial', 11, 'bold'))
        
        # Main container
        main_container = ttk.Frame(self.root, padding="20")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_container.columnconfigure(1, weight=1)
        main_container.rowconfigure(3, weight=1)
        
        # Title
        title_label = ttk.Label(main_container, text="🔬 Laser Lab Data Search Tool - Complete Edition", 
                               style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Left panel - Search parameters
        left_panel = ttk.Frame(main_container, style='Custom.TFrame', padding="15")
        left_panel.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Right panel - Results
        right_panel = ttk.Frame(main_container, style='Custom.TFrame', padding="15")
        right_panel.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.setup_left_panel(left_panel)
        self.setup_right_panel(right_panel)
        
    def setup_left_panel(self, parent):
        parent.columnconfigure(0, weight=1)
        
        # File selection section
        file_frame = ttk.LabelFrame(parent, text="📁 File Selection", padding="10")
        file_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        file_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(file_frame, textvariable=self.file_path, state='readonly').grid(
            row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        ttk.Button(file_frame, text="Browse", command=self.browse_file).grid(row=0, column=1)
        
        # Search mode selection
        mode_frame = ttk.LabelFrame(parent, text="🔍 Search Mode", padding="10")
        mode_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        modes = [("PCI Sheets", "PCI"), ("CRD Sheets", "CRD"), ("Reflectometer", "REFL"), ("Thesaurus", "THESAURUS")]
        for i, (text, value) in enumerate(modes):
            row = i // 2
            col = i % 2
            ttk.Radiobutton(mode_frame, text=text, variable=self.search_mode, 
                           value=value, command=self.update_search_ui).grid(
                row=row, column=col, sticky=tk.W, padx=10, pady=2)
        
        # Create frames for different search modes
        self.pci_frame = ttk.LabelFrame(parent, text="📊 PCI Search Parameters", padding="10")
        self.crd_frame = ttk.LabelFrame(parent, text="📈 CRD Search Parameters", padding="10")
        self.refl_frame = ttk.LabelFrame(parent, text="🔄 Reflectometer Search Parameters", padding="10")
        self.thesaurus_frame = ttk.LabelFrame(parent, text="📚 Thesaurus Search", padding="10")
        
        self.setup_pci_frame()
        self.setup_crd_frame()
        self.setup_refl_frame()
        self.setup_thesaurus_frame()
        
        # Search button
        search_btn = ttk.Button(parent, text="🔍 Search", command=self.perform_search,
                               style='Search.TButton')
        search_btn.grid(row=4, column=0, pady=10)
        
        # Initially show PCI frame
        self.update_search_ui()
        
    def setup_pci_frame(self):
        self.pci_frame.columnconfigure(1, weight=1)
        
        # Sheet selection
        sheet_subframe = ttk.Frame(self.pci_frame)
        sheet_subframe.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(sheet_subframe, text="Select Sheets:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W)
        for i, (sheet_name, var) in enumerate(self.sheet_vars.items()):
            ttk.Checkbutton(sheet_subframe, text=sheet_name.replace('PCI ', ''), variable=var).grid(
                row=0, column=i+1, sticky=tk.W, padx=10)
        
        # PCI search fields
        fields = [
            ("Sample Type:", 'sample_type', "e.g., T, JGS1, DTO"),
            ("Before Anneal (ppm):", 'absorption_before', "e.g., 100, 100-500, >100"),
            ("After Anneal (ppm):", 'absorption_after', "e.g., 50, 10-100, <50"),
            ("Coating Type:", 'coating_type', "e.g., AR (1064nm only)"),
            ("Design:", 'design', "e.g., ODA (355nm & 266)"),
            ("AOI:", 'aoi', "e.g., 0, 45, 0-45, >30")
        ]
        
        for i, (label, var_name, hint) in enumerate(fields):
            row = i + 1
            ttk.Label(self.pci_frame, text=label).grid(row=row, column=0, sticky=tk.W, pady=5)
            ttk.Entry(self.pci_frame, textvariable=self.pci_vars[var_name]).grid(
                row=row, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
            ttk.Label(self.pci_frame, text=hint, font=('Arial', 8), 
                     foreground='gray').grid(row=row, column=2, sticky=tk.W, padx=(10, 0), pady=5)
    
    def setup_crd_frame(self):
        self.crd_frame.columnconfigure(1, weight=1)
        
        # Add instruction label
        instruction_label = ttk.Label(self.crd_frame, 
                                    text="Use ranges (e.g., 100-200, >50, <100) OR exact value + tolerance", 
                                    font=('Arial', 9, 'italic'), foreground='blue')
        instruction_label.grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        # Header
        ttk.Label(self.crd_frame, text="Parameter", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W)
        ttk.Label(self.crd_frame, text="Value/Range", font=('Arial', 10, 'bold')).grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
        ttk.Label(self.crd_frame, text="Tolerance (±)", font=('Arial', 10, 'bold')).grid(row=1, column=2, sticky=tk.W, padx=(10, 0))
        
        # CRD fields
        for i, (key, label) in enumerate(self.crd_display_labels.items()):
            row = i + 2
            ttk.Label(self.crd_frame, text=f"{label}:").grid(row=row, column=0, sticky=tk.W, pady=2)
            ttk.Entry(self.crd_frame, textvariable=self.crd_vars[key], width=15).grid(
                row=row, column=1, sticky=tk.W, padx=(10, 0), pady=2)
            
            if key != 'angle':  # Angle doesn't have tolerance
                ttk.Entry(self.crd_frame, textvariable=self.crd_tol_vars[key], width=8).grid(
                    row=row, column=2, sticky=tk.W, padx=(10, 0), pady=2)
    
    def setup_refl_frame(self):
        self.refl_frame.columnconfigure(1, weight=1)
        
        # Reflectometer fields
        fields = [
            ("AOI:", 'aoi', "Angle of incidence"),
            ("Reflectivity (%):", 'reflectivity', "e.g., 99.5"),
            ("Refl. Tolerance (±):", 'refl_tolerance', "e.g., 0.1"),
            ("Transmission (%):", 'transmission', "e.g., 0.5"),
            ("Trans. Tolerance (±):", 'trans_tolerance', "e.g., 0.1"),
            ("Polarization:", 'polarization', "S-pol or P-pol")
        ]
        
        for i, (label, var_name, hint) in enumerate(fields):
            ttk.Label(self.refl_frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=5)
            ttk.Entry(self.refl_frame, textvariable=self.refl_vars[var_name]).grid(
                row=i, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
            ttk.Label(self.refl_frame, text=hint, font=('Arial', 8), 
                     foreground='gray').grid(row=i, column=2, sticky=tk.W, padx=(10, 0), pady=5)
    
    def setup_thesaurus_frame(self):
        self.thesaurus_frame.columnconfigure(1, weight=1)
        
        # Description
        desc_label = ttk.Label(self.thesaurus_frame, 
                              text="Search for Sample Types and Designs across all sheets", 
                              font=('Arial', 10, 'italic'), foreground='blue')
        desc_label.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))
        
        # Category selection
        ttk.Label(self.thesaurus_frame, text="Category:").grid(row=1, column=0, sticky=tk.W, pady=5)
        category_combo = ttk.Combobox(self.thesaurus_frame, textvariable=self.thesaurus_vars['category'],
                                     values=["all", "sample_types", "designs", "coating_types"], state="readonly")
        category_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # Search term
        ttk.Label(self.thesaurus_frame, text="Search Term:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(self.thesaurus_frame, textvariable=self.thesaurus_vars['search_term']).grid(
            row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # Hint
        hint_label = ttk.Label(self.thesaurus_frame, 
                              text="Leave search term blank to see all unique values", 
                              font=('Arial', 8), foreground='gray')
        hint_label.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
    
    def update_search_ui(self):
        """Show/hide appropriate search frames based on selected mode"""
        # Hide all frames
        self.pci_frame.grid_remove()
        self.crd_frame.grid_remove()
        self.refl_frame.grid_remove()
        self.thesaurus_frame.grid_remove()
        
        # Show appropriate frame
        if self.search_mode.get() == "PCI":
            self.pci_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        elif self.search_mode.get() == "CRD":
            self.crd_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        elif self.search_mode.get() == "REFL":
            self.refl_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        elif self.search_mode.get() == "THESAURUS":
            self.thesaurus_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
    
    def setup_right_panel(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        
        # Results header
        results_header = ttk.Label(parent, text="📋 Search Results", style='Heading.TLabel')
        results_header.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # Results display
        self.results_text = scrolledtext.ScrolledText(parent, wrap=tk.WORD, 
                                                     font=('Consolas', 10),
                                                     state='disabled')
        self.results_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Results summary
        self.summary_label = ttk.Label(parent, text="No search performed yet.", 
                                      font=('Arial', 9), foreground='gray')
        self.summary_label.grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select Laser Lab Excel File",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        if filename:
            self.file_path.set(filename)
            
    def log_message(self, message, level="INFO"):
        """Add message to results display"""
        self.results_text.config(state='normal')
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if level == "ERROR":
            tag = "error"
            prefix = "❌"
        elif level == "SUCCESS":
            tag = "success"
            prefix = "✅"
        elif level == "WARNING":
            tag = "warning"
            prefix = "⚠️"
        else:
            tag = "info"
            prefix = "ℹ️"
            
        self.results_text.insert(tk.END, f"[{timestamp}] {prefix} {message}\n")
        
        # Configure tags for colored output
        self.results_text.tag_configure("error", foreground="red")
        self.results_text.tag_configure("success", foreground="green")
        self.results_text.tag_configure("warning", foreground="orange")
        self.results_text.tag_configure("info", foreground="blue")
        
        # Apply tag to the last line
        line_start = self.results_text.index("end-2l linestart")
        line_end = self.results_text.index("end-1l lineend")
        self.results_text.tag_add(tag, line_start, line_end)
        
        self.results_text.config(state='disabled')
        self.results_text.see(tk.END)
        self.root.update()
        
    def clear_results(self):
        """Clear the results display"""
        self.results_text.config(state='normal')
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state='disabled')
        
    def perform_search(self):
        # Validate file selection
        if not self.file_path.get():
            messagebox.showerror("Error", "Please select an Excel file first.")
            return
            
        if not os.path.exists(self.file_path.get()):
            messagebox.showerror("Error", "Selected file does not exist.")
            return
        
        # Clear previous results
        self.clear_results()
        self.log_message("Starting search...", "INFO")
        
        try:
            mode = self.search_mode.get()
            
            if mode == "PCI":
                self.perform_pci_search()
            elif mode == "CRD":
                self.perform_crd_search()
            elif mode == "REFL":
                self.perform_refl_search()
            elif mode == "THESAURUS":
                self.perform_thesaurus_search()
                
        except Exception as e:
            self.log_message(f"Search failed: {str(e)}", "ERROR")
            self.summary_label.config(text="Search failed.")
    
    def perform_pci_search(self):
        # Check if at least one sheet is selected
        selected_sheets = [sheet for sheet, var in self.sheet_vars.items() if var.get()]
        if not selected_sheets:
            messagebox.showerror("Error", "Please select at least one PCI sheet to search.")
            return
        
        # Get search parameters
        search_params = {key: var.get().strip() for key, var in self.pci_vars.items()}
        
        # Log search parameters
        self.log_message(f"Searching {len(selected_sheets)} PCI sheet(s): {', '.join(selected_sheets)}", "INFO")
        if any(search_params.values()):
            self.log_message("Search parameters:", "INFO")
            for key, value in search_params.items():
                if value:
                    self.log_message(f"  {key.replace('_', ' ').title()}: {value}", "INFO")
        
        # Perform PCI search
        result = self.search_laser_lab_data(self.file_path.get(), selected_sheets, **search_params)
        
        if isinstance(result, str):
            if result == "none found":
                self.log_message("No matching entries found.", "WARNING")
                self.summary_label.config(text="No results found.")
            else:
                self.log_message(result, "ERROR")
                self.summary_label.config(text="Search failed.")
        else:
            self.display_pci_results(result)
            self.summary_label.config(text=f"Found {len(result)} matching entries.")
    
    def parse_crd_range_input(self, value_str, tolerance_str):
        """Parse CRD input that can be either a range or exact value + tolerance"""
        value_str = value_str.strip()
        tolerance_str = tolerance_str.strip()
        
        if not value_str:
            return None
        
        # If tolerance is provided, use traditional exact value + tolerance mode
        if tolerance_str:
            try:
                val = float(value_str)
                tol = float(tolerance_str)
                return (val, tol)
            except ValueError:
                self.log_message(f"Warning: Could not parse exact value '{value_str}' with tolerance '{tolerance_str}'", "WARNING")
                return None
        
        # Otherwise, try to parse as range
        range_func = self.parse_range_input(value_str)
        if range_func is None:
            # If range parsing failed, try as exact value with 0 tolerance
            try:
                val = float(value_str)
                return (val, 0)
            except ValueError:
                self.log_message(f"Warning: Could not parse CRD input '{value_str}'", "WARNING")
                return None
        
        # Convert range function to (center_value, tolerance) format for existing search
        # This is a simplified approach - for more complex ranges, you might need different logic
        try:
            # For simple exact values, return as is
            test_val = float(value_str)
            return (test_val, 0)
        except ValueError:
            # For ranges like "100-200", ">100", etc., we'll use a different approach
            # We'll return a special marker and handle it in the search logic
            return ("RANGE", range_func)
    
    def perform_crd_search(self):
        # Get CRD search parameters with enhanced range support
        user_input = {}
        for key in self.crd_column_map:
            val = self.crd_vars[key].get().strip()
            if key == 'angle':
                user_input[key] = val if val else None
            else:
                tol = self.crd_tol_vars[key].get().strip()
                parsed_input = self.parse_crd_range_input(val, tol)
                user_input[key] = parsed_input
        
        self.log_message("Searching CRD sheets...", "INFO")
        
        # Log parameters
        active_params = []
        for key, value in user_input.items():
            if value is not None:
                if key == 'angle':
                    active_params.append(f"{self.crd_display_labels[key]}: {value}")
                elif isinstance(value, tuple) and len(value) == 2:
                    if value[0] == "RANGE":
                        active_params.append(f"{self.crd_display_labels[key]}: {self.crd_vars[key].get()}")
                    else:
                        active_params.append(f"{self.crd_display_labels[key]}: {value[0]} ±{value[1]}")
        
        if active_params:
            self.log_message("Search parameters:", "INFO")
            for param in active_params:
                self.log_message(f"  {param}", "INFO")
        
        results = self.process_crd_enhanced(self.file_path.get(), user_input)
        
        if not results:
            self.log_message("No matching entries found.", "WARNING")
            self.summary_label.config(text="No results found.")
        else:
            self.display_crd_results(results)
            total_matches = sum(len(df) for df in results)
            self.summary_label.config(text=f"Found {total_matches} matching entries.")
    
    def perform_refl_search(self):
        # Get reflectometer parameters
        aoi = float(self.refl_vars['aoi'].get()) if self.refl_vars['aoi'].get() else None
        refl = float(self.refl_vars['reflectivity'].get()) if self.refl_vars['reflectivity'].get() else None
        refl_err = float(self.refl_vars['refl_tolerance'].get()) if self.refl_vars['refl_tolerance'].get() else 0
        trans = float(self.refl_vars['transmission'].get()) if self.refl_vars['transmission'].get() else None
        trans_err = float(self.refl_vars['trans_tolerance'].get()) if self.refl_vars['trans_tolerance'].get() else 0
        pol = self.refl_vars['polarization'].get().strip() if self.refl_vars['polarization'].get() else None
        
        self.log_message("Searching Reflectometer sheet...", "INFO")
        
        # Log parameters
        active_params = []
        if aoi is not None:
            active_params.append(f"AOI: {aoi}")
        if refl is not None:
            active_params.append(f"Reflectivity: {refl}% ±{refl_err}")
        if trans is not None:
            active_params.append(f"Transmission: {trans}% ±{trans_err}")
        if pol:
            active_params.append(f"Polarization: {pol}")
        
        if active_params:
            self.log_message("Search parameters:", "INFO")
            for param in active_params:
                self.log_message(f"  {param}", "INFO")
        
        df = self.load_reflectometer(self.file_path.get())
        result = self.search_reflectometer(df, aoi, refl, refl_err, trans, trans_err, pol)
        
        if result.empty:
            self.log_message("No matching entries found.", "WARNING")
            self.summary_label.config(text="No results found.")
        else:
            self.display_refl_results(result)
            self.summary_label.config(text=f"Found {len(result)} matching entries.")
    
    def perform_thesaurus_search(self):
        """Perform thesaurus search to find unique sample types and designs"""
        category = self.thesaurus_vars['category'].get()
        search_term = self.thesaurus_vars['search_term'].get().strip().lower()
        
        self.log_message("Building thesaurus from all sheets...", "INFO")
        
        # Extract unique values from all sheets
        unique_values = self.extract_unique_values(self.file_path.get())
        
        # Filter by category
        filtered_results = {}
        if category == "all" or category == "sample_types":
            filtered_results["Sample Types"] = unique_values.get("sample_types", set())
        if category == "all" or category == "designs":
            filtered_results["Designs"] = unique_values.get("designs", set())
        if category == "all" or category == "coating_types":
            filtered_results["Coating Types"] = unique_values.get("coating_types", set())
        
        # Apply search term filter if provided
        if search_term:
            for category_name, values in filtered_results.items():
                filtered_results[category_name] = {v for v in values if search_term in v.lower()}
        
        # Display results
        self.display_thesaurus_results(filtered_results, search_term)
        
        total_count = sum(len(values) for values in filtered_results.values())
        self.summary_label.config(text=f"Found {total_count} unique entries.")
    
    def extract_unique_values(self, file_path):
        """Extract unique sample types, designs, and coating types from all sheets"""
        unique_values = {
            "sample_types": set(),
            "designs": set(),
            "coating_types": set()
        }
        
        try:
            # Extract from PCI sheets
            pci_sheets = ['PCI 1064nm', 'PCI 355nm', 'PCI 266']
            for sheet_name in pci_sheets:
                try:
                    df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=2)
                    column_mapping = self.get_sheet_column_mapping(sheet_name)
                    
                    # Rename columns
                    for col_idx, new_name in column_mapping.items():
                        if col_idx < len(df.columns):
                            old_name = df.columns[col_idx]
                            df = df.rename(columns={old_name: new_name})
                    
                    # Extract sample types
                    if 'Sample Type' in df.columns:
                        sample_types = df['Sample Type'].dropna().astype(str)
                        unique_values["sample_types"].update([s.strip() for s in sample_types if s.strip() and s.strip().lower() != 'nan'])
                    
                    # Extract designs
                    if 'Design' in df.columns:
                        designs = df['Design'].dropna().astype(str)
                        unique_values["designs"].update([d.strip() for d in designs if d.strip() and d.strip().lower() != 'nan'])
                    
                    # Extract coating types
                    if 'Coating Type' in df.columns:
                        coatings = df['Coating Type'].dropna().astype(str)
                        unique_values["coating_types"].update([c.strip() for c in coatings if c.strip() and c.strip().lower() != 'nan'])
                    
                    self.log_message(f"✓ Processed {sheet_name}", "INFO")
                except Exception as e:
                    self.log_message(f"⚠️ Could not process {sheet_name}: {str(e)}", "WARNING")
            
            # Extract from CRD sheets
            xl = pd.ExcelFile(file_path)
            crd_sheets = [s for s in xl.sheet_names if s.startswith("CRD")]
            for sheet_name in crd_sheets:
                try:
                    df_raw = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
                    flat_columns = self.make_unique(df_raw.iloc[1:4].T.ffill(axis=0).apply(
                        lambda x: ' | '.join([str(i).strip() for i in x if pd.notna(i)]), axis=1))
                    df = df_raw.iloc[4:].copy()
                    df.columns = flat_columns
                    
                    # Look for sample type columns
                    for col in df.columns:
                        if 'sample' in col.lower() and 'type' in col.lower():
                            sample_types = df[col].dropna().astype(str)
                            unique_values["sample_types"].update([s.strip() for s in sample_types if s.strip() and s.strip().lower() != 'nan'])
                    
                    self.log_message(f"✓ Processed {sheet_name}", "INFO")
                except Exception as e:
                    self.log_message(f"⚠️ Could not process {sheet_name}: {str(e)}", "WARNING")
            
            # Extract from Reflectometer sheet
            try:
                df = pd.read_excel(file_path, sheet_name="Reflectometer ")
                df.columns = df.iloc[1]
                df = df[2:].reset_index(drop=True)
                
                # Look for relevant columns (if any sample type info exists)
                for col in df.columns:
                    if pd.notna(col) and ('sample' in str(col).lower() or 'type' in str(col).lower()):
                        values = df[col].dropna().astype(str)
                        unique_values["sample_types"].update([v.strip() for v in values if v.strip() and v.strip().lower() != 'nan'])
                
                self.log_message("✓ Processed Reflectometer sheet", "INFO")
            except Exception as e:
                self.log_message(f"⚠️ Could not process Reflectometer sheet: {str(e)}", "WARNING")
            
        except Exception as e:
            self.log_message(f"Error extracting unique values: {str(e)}", "ERROR")
        
        return unique_values
    
    def display_thesaurus_results(self, results, search_term):
        """Display thesaurus search results"""
        if search_term:
            self.log_message(f"🔍 Thesaurus results for '{search_term}':", "SUCCESS")
        else:
            self.log_message("📚 Complete Thesaurus:", "SUCCESS")
        
        self.log_message("─" * 60, "INFO")
        
        for category, values in results.items():
            if values:
                sorted_values = sorted(list(values))
                self.log_message(f"\n📂 {category} ({len(sorted_values)} unique entries):", "SUCCESS")
                
                # Display in columns for better readability
                for i, value in enumerate(sorted_values, 1):
                    self.log_message(f"  {i:2d}. {value}", "INFO")
            else:
                self.log_message(f"\n📂 {category}: No entries found", "WARNING")
        
        self.log_message("\n" + "═" * 60, "SUCCESS")
        self.log_message("Thesaurus search completed!", "SUCCESS")
    
    def display_pci_results(self, result_df):
        """Display PCI search results"""
        self.log_message(f"Found {len(result_df)} total matching entries!", "SUCCESS")
        
        # Group by sheet for organized display
        for sheet_name in result_df['Sheet'].unique():
            sheet_results = result_df[result_df['Sheet'] == sheet_name]
            self.log_message(f"\n📊 {sheet_name} ({len(sheet_results)} matches):", "SUCCESS")
            self.log_message("─" * 60, "INFO")
            
            for idx, (_, row) in enumerate(sheet_results.iterrows(), 1):
                self.log_message(f"\n[{idx}] Run: {row['Run Number']}", "SUCCESS")
                
                # Collect details
                details = []
                if pd.notna(row['Sample Type']) and str(row['Sample Type']).strip():
                    details.append(f"Type: {row['Sample Type']}")
                if pd.notna(row['Before Anneal']):
                    details.append(f"Before: {row['Before Anneal']} ppm")
                if pd.notna(row['After Anneal']):
                    details.append(f"After: {row['After Anneal']} ppm")
                if 'Coating Type' in row and pd.notna(row['Coating Type']) and str(row['Coating Type']).strip():
                    details.append(f"Coating: {row['Coating Type']}")
                if 'Design' in row and pd.notna(row['Design']) and str(row['Design']).strip():
                    details.append(f"Design: {row['Design']}")
                if pd.notna(row['AOI']) and str(row['AOI']).strip():
                    details.append(f"AOI: {row['AOI']}")
                if pd.notna(row['Measured Date']):
                    details.append(f"Date: {row['Measured Date']}")
                
                self.log_message(f"    {' | '.join(details)}", "INFO")
                
                # Show note if present
                if pd.notna(row['Note']) and str(row['Note']).strip():
                    self.log_message(f"    Note: {row['Note']}", "INFO")
        
        self.log_message("\n" + "═" * 60, "SUCCESS")
        self.log_message("PCI search completed successfully!", "SUCCESS")
    
    def display_crd_results(self, results):
        """Display CRD search results"""
        total_matches = sum(len(df) for df in results)
        self.log_message(f"Found {total_matches} total matching entries!", "SUCCESS")
        
        for df in results:
            sheet = df["Sheet"].iloc[0]
            self.log_message(f"\n📈 {sheet} ({len(df)} matches):", "SUCCESS")
            self.log_message("─" * 60, "INFO")
            
            for idx, (_, row) in enumerate(df.iterrows(), 1):
                line = self.format_crd_output(row, sheet)
                self.log_message(f"[{idx}] {line}", "INFO")
        
        self.log_message("\n" + "═" * 60, "SUCCESS")
        self.log_message("CRD search completed successfully!", "SUCCESS")
    
    def display_refl_results(self, result_df):
        """Display Reflectometer search results"""
        self.log_message(f"Found {len(result_df)} matching entries!", "SUCCESS")
        self.log_message("🔄 Reflectometer Results:", "SUCCESS")
        self.log_message("─" * 60, "INFO")
        
        for idx, (_, row) in enumerate(result_df.iterrows(), 1):
            txt = f"Run {row['Run Number']} | AOI: {row['AOI']} | "
            txt += f"Refl: [{row['Reflect_1550']}, {row['Reflect_1064']}, {row['Reflect_1047']}] | "
            txt += f"Trans: [{row['Trans_1550']}, {row['Trans_1064']}, {row['Trans_1047']}] | "
            txt += f"Note: {row['Note']}"
            self.log_message(f"[{idx}] {txt}", "INFO")
        
        self.log_message("\n" + "═" * 60, "SUCCESS")
        self.log_message("Reflectometer search completed successfully!", "SUCCESS")
    
    # ============= PCI SEARCH FUNCTIONS =============
    def get_sheet_column_mapping(self, sheet_name):
        """Return the column mapping for each PCI sheet based on their different structures"""
        if sheet_name == 'PCI 1064nm':
            return {
                0: 'Run Number', 1: 'Customer Name', 2: 'Sample Type',
                3: 'Before Anneal', 4: 'After Anneal', 5: 'Coating Type',
                6: 'Measured Date', 7: 'AOI', 8: 'Note'
            }
        elif sheet_name == 'PCI 355nm':
            return {
                0: 'Run Number', 1: 'Customer Name', 2: 'Sample Type',
                3: 'Before Anneal', 4: 'After Anneal', 5: 'Measured Date',
                6: 'AOI', 7: 'Design', 8: 'Note'
            }
        elif sheet_name == 'PCI 266':
            return {
                0: 'Run Number', 1: 'Sample Type', 2: 'Before Anneal',
                3: 'After Anneal', 4: 'Measured Date', 5: 'AOI',
                6: 'Design', 7: 'Note'
            }
        else:
            return {}

    def parse_range_input(self, range_str):
        """Parse range input and return a function to test values"""
        range_str = range_str.strip()
        if not range_str:
            return None
        
        try:
            # Check for range with dash (e.g., "100-200")
            if '-' in range_str and not range_str.startswith('-'):
                parts = range_str.split('-')
                if len(parts) == 2:
                    min_val = float(parts[0].strip())
                    max_val = float(parts[1].strip())
                    return lambda x: min_val <= x <= max_val
            
            # Check for comparison operators
            if range_str.startswith('>='):
                val = float(range_str[2:].strip())
                return lambda x: x >= val
            elif range_str.startswith('<='):
                val = float(range_str[2:].strip())
                return lambda x: x <= val
            elif range_str.startswith('>'):
                val = float(range_str[1:].strip())
                return lambda x: x > val
            elif range_str.startswith('<'):
                val = float(range_str[1:].strip())
                return lambda x: x < val
            else:
                # Exact match
                val = float(range_str)
                return lambda x: x == val
        
        except ValueError:
            self.log_message(f"Warning: Could not parse range '{range_str}'. Using text search instead.", "WARNING")
            return None

    def apply_numeric_filter(self, df, column_name, range_input):
        """Apply numeric filter with range support"""
        if not range_input.strip():
            return df
        
        range_func = self.parse_range_input(range_input)
        if range_func is None:
            # Fall back to text search if parsing failed
            return df[df[column_name].astype(str).str.contains(range_input, case=False, na=False)]
        
        # Apply numeric range filter
        numeric_values = pd.to_numeric(df[column_name], errors='coerce')
        valid_mask = ~numeric_values.isna()
        range_mask = numeric_values[valid_mask].apply(range_func)
        
        # Create full mask for the dataframe
        full_mask = pd.Series(False, index=df.index)
        full_mask.loc[valid_mask] = range_mask
        
        return df[full_mask]

    def search_single_sheet(self, file_path, sheet_name, sample_type="", absorption_before="", absorption_after="", coating_type="", design="", aoi=""):
        """Search a single PCI sheet for matching entries"""
        try:
            # Read the sheet starting from row 3 (where actual headers are)
            df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=2)
            
            # Get column mapping for this sheet
            column_mapping = self.get_sheet_column_mapping(sheet_name)
            
            # Rename columns based on the mapping
            for col_idx, new_name in column_mapping.items():
                if col_idx < len(df.columns):
                    old_name = df.columns[col_idx]
                    df = df.rename(columns={old_name: new_name})
            
            # Remove rows where Run Number is NaN (empty rows)
            df = df.dropna(subset=['Run Number'])
            
            if len(df) == 0:
                return pd.DataFrame(), 0
            
            # Create a copy for filtering
            filtered_df = df.copy()
            original_count = len(filtered_df)
            
            # Apply filters based on non-blank inputs
            if sample_type.strip():
                filtered_df = filtered_df[filtered_df['Sample Type'].astype(str).str.contains(sample_type, case=False, na=False)]
            
            # Apply numeric range filters
            if absorption_before.strip():
                filtered_df = self.apply_numeric_filter(filtered_df, 'Before Anneal', absorption_before)
            
            if absorption_after.strip():
                filtered_df = self.apply_numeric_filter(filtered_df, 'After Anneal', absorption_after)
            
            if aoi.strip():
                filtered_df = self.apply_numeric_filter(filtered_df, 'AOI', aoi)
            
            # Apply text filters
            if coating_type.strip() and 'Coating Type' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['Coating Type'].astype(str).str.contains(coating_type, case=False, na=False)]
            
            if design.strip() and 'Design' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['Design'].astype(str).str.contains(design, case=False, na=False)]
            
            # Add sheet name to results for identification
            if len(filtered_df) > 0:
                filtered_df['Sheet'] = sheet_name
            
            return filtered_df, original_count
            
        except Exception as e:
            self.log_message(f"Warning: Error reading {sheet_name}: {str(e)}", "WARNING")
            return pd.DataFrame(), 0

    def search_laser_lab_data(self, file_path, sheets, sample_type="", absorption_before="", absorption_after="", coating_type="", design="", aoi=""):
        """Search multiple PCI sheets for runs matching the specified parameters"""
        
        # If single sheet provided as string, convert to list
        if isinstance(sheets, str):
            sheets = [sheets]
        
        all_results = []
        
        self.log_message(f"Searching {len(sheets)} sheet(s): {', '.join(sheets)}", "INFO")
        
        for sheet_name in sheets:
            self.log_message(f"Searching {sheet_name}...", "INFO")
            result_df, original_count = self.search_single_sheet(file_path, sheet_name, sample_type, absorption_before, 
                                                           absorption_after, coating_type, design, aoi)
            
            if len(result_df) > 0:
                all_results.append(result_df)
                self.log_message(f"✓ {sheet_name}: {len(result_df)} matches (from {original_count} total)", "SUCCESS")
            else:
                self.log_message(f"❌ {sheet_name}: 0 matches (from {original_count} total)", "INFO")
        
        # Combine all results
        if not all_results:
            return "none found"
        
        # Concatenate all results
        combined_results = pd.concat(all_results, ignore_index=True, sort=False)
        return combined_results
    
    # ============= CRD SEARCH FUNCTIONS =============
    def make_unique(self, columns):
        """Make column names unique"""
        seen = {}
        result = []
        for col in columns:
            if col not in seen:
                seen[col] = 1
                result.append(col)
            else:
                seen[col] += 1
                result.append(f"{col} ({seen[col]})")
        return result

    def row_matches_enhanced(self, row, user_input):
        """Enhanced row matching with range support for CRD"""
        for key, cond in user_input.items():
            col = self.crd_column_map[key]
            if cond is None:
                continue
            if key == 'angle':
                val = row.get(col)
                if isinstance(val, str):
                    match = re.search(r'\(([\d.]+)', val)
                    if match and match.group(1) != cond:
                        return False
                else:
                    return False
            else:
                # Handle enhanced range inputs
                if isinstance(cond, tuple) and len(cond) == 2:
                    if cond[0] == "RANGE":
                        # Apply range function
                        range_func = cond[1]
                        try:
                            val = float(row.get(col))
                            if not range_func(val):
                                return False
                        except:
                            return False
                    else:
                        # Traditional target ± tolerance
                        target, tol = cond
                        try:
                            val = float(row.get(col))
                            if not (target - tol <= val <= target + tol):
                                return False
                        except:
                            return False
        return True

    def process_crd_enhanced(self, filepath, user_input):
        """Enhanced CRD processing with range support"""
        xl = pd.ExcelFile(filepath)
        results = []
        for sheet in [s for s in xl.sheet_names if s.startswith("CRD")]:
            df_raw = pd.read_excel(filepath, sheet_name=sheet, header=None)
            flat_columns = self.make_unique(df_raw.iloc[1:4].T.ffill(axis=0).apply(
                lambda x: ' | '.join([str(i).strip() for i in x if pd.notna(i)]), axis=1))
            df = df_raw.iloc[4:].copy()
            df.columns = flat_columns
            df.reset_index(drop=True, inplace=True)
            if "Customer Name" in df.columns:
                df.drop(columns=["Customer Name"], inplace=True)
            matches = df[df.apply(lambda r: self.row_matches_enhanced(r, user_input), axis=1)]
            if not matches.empty:
                matches.insert(0, "Sheet", sheet)
                results.append(matches)
        return results

    def process_crd(self, filepath, user_input):
        """Process CRD sheets and return matching results"""
        xl = pd.ExcelFile(filepath)
        results = []
        for sheet in [s for s in xl.sheet_names if s.startswith("CRD")]:
            df_raw = pd.read_excel(filepath, sheet_name=sheet, header=None)
            flat_columns = self.make_unique(df_raw.iloc[1:4].T.ffill(axis=0).apply(
                lambda x: ' | '.join([str(i).strip() for i in x if pd.notna(i)]), axis=1))
            df = df_raw.iloc[4:].copy()
            df.columns = flat_columns
            df.reset_index(drop=True, inplace=True)
            if "Customer Name" in df.columns:
                df.drop(columns=["Customer Name"], inplace=True)
            matches = df[df.apply(lambda r: self.row_matches(r, user_input), axis=1)]
            if not matches.empty:
                matches.insert(0, "Sheet", sheet)
                results.append(matches)
        return results

    def row_matches(self, row, user_input):
        """Check if a row matches the user input criteria"""
        for key, cond in user_input.items():
            col = self.crd_column_map[key]
            if cond is None:
                continue
            if key == 'angle':
                val = row.get(col)
                if isinstance(val, str):
                    match = re.search(r'\(([\d.]+)', val)
                    if match and match.group(1) != cond:
                        return False
                else:
                    return False
            else:
                target, tol = cond
                try:
                    val = float(row.get(col))
                    if not (target - tol <= val <= target + tol):
                        return False
                except:
                    return False
        return True

    def format_crd_output(self, row, sheet):
        """Format CRD output for display"""
        parts = [f"Run {row.get('Run Number', '').strip()} | {row.get('Angle of meaurment', '').strip()}"]
        for key in self.crd_column_map:
            if key == 'angle': 
                continue
            val = row.get(self.crd_column_map[key])
            if pd.notna(val):
                parts.append(f"{self.crd_display_labels[key]}: {val}")
        return " | ".join(parts)
    
    # ============= REFLECTOMETER SEARCH FUNCTIONS =============
    def load_reflectometer(self, filepath):
        """Load and process reflectometer data"""
        df = pd.read_excel(filepath, sheet_name="Reflectometer ")
        df.columns = df.iloc[1]
        df = df[2:].reset_index(drop=True)
        df.columns.name = None
        df.columns = [
            "Run Number", "Customer Name", "AOI",
            "Reflect_1550", "Reflect_1064", "Reflect_1047",
            "Trans_1550", "Trans_1064", "Trans_1047",
            "Measured Date", "Note", "Col12", "Col13"
        ]
        for c in df.columns[2:9]:
            df[c] = pd.to_numeric(df[c], errors='coerce')
        return df

    def search_reflectometer(self, df, aoi, refl, refl_err, trans, trans_err, pol):
        """Search reflectometer data with given parameters"""
        if aoi is not None:
            df = df[df["AOI"].round(3) == round(float(aoi), 3)]
        if refl is not None:
            refl_cols = ["Reflect_1550", "Reflect_1064", "Reflect_1047"]
            df = df[df[refl_cols].apply(lambda r: any(abs(r[c] - refl) <= refl_err for c in refl_cols if pd.notna(r[c])), axis=1)]
        if trans is not None:
            trans_cols = ["Trans_1550", "Trans_1064", "Trans_1047"]
            df = df[df[trans_cols].apply(lambda r: any(abs(r[c] - trans) <= trans_err for c in trans_cols if pd.notna(r[c])), axis=1)]
        if pol:
            df = df[df["Note"].astype(str).str.lower().str.startswith(pol.lower())]
        return df.reset_index(drop=True)

def main():
    root = tk.Tk()
    app = LaserLabSearchGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
