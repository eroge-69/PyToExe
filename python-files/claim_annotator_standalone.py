#!/usr/bin/env python3
"""
Claim Annotator - Standalone Version
A complete medical claims processing application in a single file.
"""

import sys
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import yaml
import logging
import threading
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from difflib import get_close_matches


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class Rule:
    """Represents a business rule for claim annotation."""
    name: str
    priority: int
    stop: bool
    comment: str
    conditions: Dict[str, Any]


class Record:
    """Represents a normalized claim record."""
    def __init__(self, id: str, payer: str, dos: str, claim_date: str, 
                 cpt_list: List[str], denial_reason: str):
        self.id = id
        self.payer = payer
        self.dos = dos
        self.claim_date = claim_date
        self.cpt_list = cpt_list
        self.denial_reason = denial_reason


# ============================================================================
# RULE ENGINE
# ============================================================================

class RuleEngine:
    """Engine for evaluating business rules against claim records."""
    
    def __init__(self, rules: List[Rule], config: Dict[str, Any]):
        self.rules = sorted(rules, key=lambda r: r.priority)
        self.config = config
    
    def evaluate(self, record: Record) -> tuple[List[str], List[str]]:
        """Evaluate all rules against a record and return comments and matched rules."""
        comments = []
        matched_rules = []
        
        for rule in self.rules:
            if self._evaluate_rule(rule, record):
                comments.append(rule.comment)
                matched_rules.append(rule.name)
                
                if rule.stop:
                    break
        
        return comments, matched_rules
    
    def _evaluate_rule(self, rule: Rule, record: Record) -> bool:
        """Evaluate a single rule against a record."""
        if not rule.conditions:
            return True
        
        for condition_name, condition_value in rule.conditions.items():
            if not self._evaluate_condition(condition_name, condition_value, record):
                return False
        
        return True
    
    def _evaluate_condition(self, condition_name: str, condition_value: Any, record: Record) -> bool:
        """Evaluate a single condition against a record."""
        try:
            if condition_name == "contains_any_cpt":
                return self._contains_any_cpt(condition_value, record)
            elif condition_name == "contains_all_cpt":
                return self._contains_all_cpt(condition_value, record)
            elif condition_name == "payer_includes":
                return self._payer_includes(condition_value, record)
            elif condition_name == "payer_excludes":
                return self._payer_excludes(condition_value, record)
            elif condition_name == "denial_includes":
                return self._denial_includes(condition_value, record)
            elif condition_name == "has_em_with_tcm":
                return self._has_em_with_tcm(record)
            elif condition_name == "has_vaccine":
                return self._has_vaccine(record)
            elif condition_name == "special_pair_any":
                return self._special_pair_any(condition_value, record)
            else:
                return False
        except Exception:
            return False
    
    def _contains_any_cpt(self, cpt_codes: List[str], record: Record) -> bool:
        """Check if record contains any of the specified CPT codes."""
        record_cpts = set(code.upper() for code in record.cpt_list)
        target_cpts = set(code.upper() for code in cpt_codes)
        return bool(record_cpts.intersection(target_cpts))
    
    def _contains_all_cpt(self, cpt_codes: List[str], record: Record) -> bool:
        """Check if record contains all of the specified CPT codes."""
        record_cpts = set(code.upper() for code in record.cpt_list)
        target_cpts = set(code.upper() for code in cpt_codes)
        return target_cpts.issubset(record_cpts)
    
    def _payer_includes(self, keywords: List[str], record: Record) -> bool:
        """Check if payer contains any of the specified keywords (case-insensitive)."""
        payer_lower = record.payer.lower()
        return any(keyword.lower() in payer_lower for keyword in keywords)
    
    def _payer_excludes(self, keywords: List[str], record: Record) -> bool:
        """Check if payer does not contain any of the specified keywords (case-insensitive)."""
        payer_lower = record.payer.lower()
        return not any(keyword.lower() in payer_lower for keyword in keywords)
    
    def _denial_includes(self, keywords: List[str], record: Record) -> bool:
        """Check if denial reason contains any of the specified keywords (case-insensitive)."""
        denial_lower = record.denial_reason.lower()
        return any(keyword.lower() in denial_lower for keyword in keywords)
    
    def _has_em_with_tcm(self, record: Record) -> bool:
        """Check if record has both TCM codes (99495, 99496) and E/M codes (992XX)."""
        cpt_codes = record.cpt_list
        
        # Check for TCM codes
        tcm_codes = {'99495', '99496'}
        has_tcm = any(code.upper() in tcm_codes for code in cpt_codes)
        
        # Check for E/M codes (starting with 992)
        has_em = any(code.upper().startswith('992') for code in cpt_codes)
        
        return has_tcm and has_em
    
    def _has_vaccine(self, record: Record) -> bool:
        """Check if record contains any vaccine codes."""
        record_cpts = set(code.upper() for code in record.cpt_list)
        vaccine_codes = set(code.upper() for code in self.config.get('vaccine_codes', []))
        return bool(record_cpts.intersection(vaccine_codes))
    
    def _special_pair_any(self, pair_config: Dict[str, List[str]], record: Record) -> bool:
        """Check if record contains any of the specified code pairs."""
        if 'pair' not in pair_config:
            return False
        
        pair_codes = set(code.upper() for code in pair_config['pair'])
        record_cpts = set(code.upper() for code in record.cpt_list)
        
        return pair_codes.issubset(record_cpts)


# ============================================================================
# I/O UTILITIES
# ============================================================================

def load_dataframe(file_path: str, sheet: Optional[str] = None) -> pd.DataFrame:
    """Load a DataFrame from CSV or Excel file."""
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    file_ext = file_path.suffix.lower()
    
    try:
        if file_ext == '.csv':
            return pd.read_csv(file_path)
        elif file_ext in ['.xlsx', '.xls']:
            if sheet:
                return pd.read_excel(file_path, sheet_name=sheet)
            else:
                excel_file = pd.ExcelFile(file_path)
                first_sheet = excel_file.sheet_names[0]
                return pd.read_excel(file_path, sheet_name=first_sheet)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
    except Exception as e:
        raise Exception(f"Error loading file {file_path}: {e}")


def save_dataframe(df: pd.DataFrame, file_path: str) -> None:
    """Save a DataFrame to CSV or Excel file."""
    file_path = Path(file_path)
    file_ext = file_path.suffix.lower()
    
    try:
        if file_ext == '.csv':
            df.to_csv(file_path, index=False)
        elif file_ext in ['.xlsx', '.xls']:
            df.to_excel(file_path, index=False)
        else:
            raise ValueError(f"Unsupported output format: {file_ext}")
    except Exception as e:
        raise Exception(f"Error saving file {file_path}: {e}")


def resolve_columns(df: pd.DataFrame) -> Dict[str, str]:
    """Resolve column names using fuzzy matching for common variations."""
    actual_columns = list(df.columns)
    
    # Define column mappings with synonyms
    column_mappings = {
        'id': ['id', 'line', 'index', 'claim_id', 'claimid', 'line_id', 'lineid', 's.no', 'account #'],
        'payer': ['payer', 'insurance', 'insurance_company', 'carrier', 'payor'],
        'dos': ['dos', 'date_of_service', 'service_date', 'dateofservice'],
        'claim_date': ['claim_date', 'claimdate', 'submission_date', 'submissiondate', 'date_submitted', 'bt date'],
        'cpt': ['cpt', 'cpt_codes', 'cptcodes', 'procedure_codes', 'procedurecodes', 'codes', 'procedures'],
        'denial_reason': ['denial_reason', 'denialreason', 'denial', 'reason', 'denial_text', 'denialtext']
    }
    
    resolved = {}
    
    for standard_name, synonyms in column_mappings.items():
        found_column = None
        
        # First try exact match (case-insensitive)
        for col in actual_columns:
            if col.lower() == standard_name.lower():
                found_column = col
                break
        
        # If not found, try fuzzy matching
        if not found_column:
            for synonym in synonyms:
                matches = get_close_matches(synonym.lower(), 
                                         [col.lower() for col in actual_columns], 
                                         n=1, cutoff=0.8)
                if matches:
                    # Find the original case column name
                    for col in actual_columns:
                        if col.lower() == matches[0]:
                            found_column = col
                            break
                    break
        
        if found_column:
            resolved[standard_name] = found_column
        else:
            if standard_name == 'cpt':
                raise ValueError(f"Required column 'CPT' not found. Available columns: {actual_columns}")
            else:
                resolved[standard_name] = None
    
    return resolved


def parse_cpts(raw_cpt: str) -> List[str]:
    """Parse CPT codes from a raw string."""
    if pd.isna(raw_cpt) or raw_cpt == '':
        return []
    
    # Split on common separators and clean up
    separators = r'[,;\s]+'
    codes = re.split(separators, str(raw_cpt))
    
    # Clean and filter codes
    cleaned_codes = []
    for code in codes:
        code = code.strip().upper()
        if code:  # Skip empty strings
            cleaned_codes.append(code)
    
    return cleaned_codes


def normalize_record(row: pd.Series, column_mapping: Dict[str, str]) -> Record:
    """Normalize a DataFrame row into a standard record format."""
    def get_value(standard_name: str) -> str:
        actual_col = column_mapping.get(standard_name)
        if actual_col and actual_col in row.index:
            value = row[actual_col]
            return str(value) if pd.notna(value) else ""
        return ""
    
    return Record(
        id=get_value('id'),
        payer=get_value('payer'),
        dos=get_value('dos'),
        claim_date=get_value('claim_date'),
        cpt_list=parse_cpts(get_value('cpt')),
        denial_reason=get_value('denial_reason')
    )


def get_output_filename(input_path: str, output_path: Optional[str] = None) -> str:
    """Generate output filename based on input path."""
    if output_path:
        return output_path
    
    input_path = Path(input_path)
    input_ext = input_path.suffix.lower()
    
    if input_ext == '.csv':
        output_ext = '.csv'
    else:
        output_ext = '.xlsx'
    
    output_name = f"{input_path.stem}_annotated{output_ext}"
    return str(input_path.parent / output_name)


# ============================================================================
# RULES LOADING
# ============================================================================

def load_rules(rules_path: str) -> tuple[List[Rule], Dict[str, Any]]:
    """Load rules from YAML file."""
    try:
        with open(rules_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if not isinstance(data, dict):
            raise ValueError("Rules file must contain a dictionary")
        
        # Extract config
        config = data.get('config', {})
        if 'vaccine_codes' not in config:
            config['vaccine_codes'] = []
        
        # Extract and validate rules
        rules_data = data.get('rules', [])
        if not isinstance(rules_data, list):
            raise ValueError("Rules must be a list")
        
        rules = []
        for i, rule_data in enumerate(rules_data):
            try:
                rule = Rule(
                    name=rule_data.get('name', f'Rule_{i}'),
                    priority=rule_data.get('priority', 9999),
                    stop=rule_data.get('stop', False),
                    comment=rule_data.get('comment', ''),
                    conditions=rule_data.get('conditions', {})
                )
                rules.append(rule)
            except Exception:
                continue
        
        return rules, config
        
    except FileNotFoundError:
        raise FileNotFoundError(f"Rules file not found: {rules_path}")
    except yaml.YAMLError as e:
        raise Exception(f"Error parsing YAML file {rules_path}: {e}")


def get_rules_path(rules_arg: str = None) -> str:
    """Get the path to the rules file, handling frozen executable case."""
    if rules_arg:
        return rules_arg
    
    # Check if running as frozen executable
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller executable
        base_path = sys._MEIPASS
        rules_path = os.path.join(base_path, 'rules.yaml')
        if os.path.exists(rules_path):
            return rules_path
    
    # Default to rules.yaml in current directory
    return 'rules.yaml'


# ============================================================================
# PROCESSING FUNCTIONS
# ============================================================================

def process_claims(input_path: str, rules_path: str, output_path: str = None, 
                  sheet: str = None) -> None:
    """Process claims file with rules and generate annotated output."""
    try:
        # Load rules
        rules, config = load_rules(rules_path)
        if not rules:
            raise Exception("No valid rules found")
        
        # Initialize rule engine
        engine = RuleEngine(rules, config)
        
        # Load input data
        df = load_dataframe(input_path, sheet)
        
        if df.empty:
            raise Exception("Input file is empty")
        
        # Resolve column mappings
        column_mapping = resolve_columns(df)
        
        # Process each record
        comments_list = []
        matched_rules_list = []
        
        for index, row in df.iterrows():
            try:
                # Normalize record
                record = normalize_record(row, column_mapping)
                
                # Evaluate rules
                comments, matched_rules = engine.evaluate(record)
                
                # Join comments with " | "
                comment_str = " | ".join(comments) if comments else ""
                matched_rules_str = "; ".join(matched_rules) if matched_rules else ""
                
                comments_list.append(comment_str)
                matched_rules_list.append(matched_rules_str)
                    
            except Exception as e:
                comments_list.append("")
                matched_rules_list.append("")
        
        # Add results to DataFrame
        df['Comment'] = comments_list
        df['MatchedRules'] = matched_rules_list
        
        # Generate output filename
        output_file = get_output_filename(input_path, output_path)
        
        # Save results
        save_dataframe(df, output_file)
        
    except Exception as e:
        raise Exception(f"Error processing claims: {e}")


# ============================================================================
# GUI APPLICATION
# ============================================================================

class ClaimAnnotatorGUI:
    """GUI application for claim annotation."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Claim Annotator v1.0.0")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Variables
        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar()
        self.rules_file = tk.StringVar(value=get_rules_path())
        self.status = tk.StringVar(value="Ready to process claims")
        
        self.setup_ui()
        self.setup_logging()
    
    def setup_ui(self):
        """Set up the user interface."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Claim Annotator", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Input file selection
        ttk.Label(main_frame, text="Input File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.input_file, width=50).grid(
            row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Browse...", 
                  command=self.browse_input_file).grid(row=1, column=2, pady=5)
        
        # Rules file selection
        ttk.Label(main_frame, text="Rules File:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.rules_file, width=50).grid(
            row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Browse...", 
                  command=self.browse_rules_file).grid(row=2, column=2, pady=5)
        
        # Output file selection
        ttk.Label(main_frame, text="Output File:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.output_file, width=50).grid(
            row=3, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Browse...", 
                  command=self.browse_output_file).grid(row=3, column=2, pady=5)
        
        # Process button
        self.process_button = ttk.Button(main_frame, text="Process Claims", 
                                        command=self.process_claims_threaded)
        self.process_button.grid(row=4, column=0, columnspan=3, pady=20)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Status label
        status_label = ttk.Label(main_frame, textvariable=self.status)
        status_label.grid(row=6, column=0, columnspan=3, pady=5)
        
        # Log text area
        ttk.Label(main_frame, text="Log Output:").grid(row=7, column=0, sticky=tk.W, pady=(20, 5))
        
        # Create frame for log area
        log_frame = ttk.Frame(main_frame)
        log_frame.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Log text widget with scrollbar
        self.log_text = tk.Text(log_frame, height=10, width=70)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure main frame row weights
        main_frame.rowconfigure(8, weight=1)
    
    def setup_logging(self):
        """Set up logging to display in the GUI."""
        # Create a custom log handler
        class GUILogHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
            
            def emit(self, record):
                msg = self.format(record)
                # Use after() to ensure thread safety
                self.text_widget.after(0, lambda: self.append_log(msg))
            
            def append_log(self, msg):
                self.text_widget.insert(tk.END, msg + '\n')
                self.text_widget.see(tk.END)
        
        # Set up logging
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        
        # Remove existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Add GUI handler
        gui_handler = GUILogHandler(self.log_text)
        gui_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(gui_handler)
    
    def browse_input_file(self):
        """Browse for input file."""
        filetypes = [
            ("Excel files", "*.xlsx *.xls"),
            ("CSV files", "*.csv"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select Input Claims File",
            filetypes=filetypes
        )
        
        if filename:
            self.input_file.set(filename)
            # Auto-suggest output filename
            if not self.output_file.get():
                input_path = Path(filename)
                output_name = f"{input_path.stem}_annotated{input_path.suffix}"
                self.output_file.set(str(input_path.parent / output_name))
    
    def browse_rules_file(self):
        """Browse for rules file."""
        filetypes = [
            ("YAML files", "*.yaml *.yml"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select Rules File",
            filetypes=filetypes
        )
        
        if filename:
            self.rules_file.set(filename)
    
    def browse_output_file(self):
        """Browse for output file location."""
        # Determine file extension based on input file
        input_path = Path(self.input_file.get())
        if input_path.suffix.lower() == '.csv':
            filetypes = [("CSV files", "*.csv")]
            defaultextension = ".csv"
        else:
            filetypes = [("Excel files", "*.xlsx")]
            defaultextension = ".xlsx"
        
        filename = filedialog.asksaveasfilename(
            title="Save Annotated Claims As",
            filetypes=filetypes,
            defaultextension=defaultextension,
            initialvalue=self.output_file.get()
        )
        
        if filename:
            self.output_file.set(filename)
    
    def process_claims_threaded(self):
        """Process claims in a separate thread to avoid blocking the GUI."""
        if not self.input_file.get():
            messagebox.showerror("Error", "Please select an input file.")
            return
        
        if not self.output_file.get():
            messagebox.showerror("Error", "Please select an output file location.")
            return
        
        if not os.path.exists(self.rules_file.get()):
            messagebox.showerror("Error", f"Rules file not found: {self.rules_file.get()}")
            return
        
        # Disable the process button and start progress bar
        self.process_button.config(state='disabled')
        self.progress.start()
        self.status.set("Processing claims...")
        
        # Clear log
        self.log_text.delete(1.0, tk.END)
        
        # Start processing in a separate thread
        thread = threading.Thread(target=self.process_claims_worker)
        thread.daemon = True
        thread.start()
    
    def process_claims_worker(self):
        """Worker function to process claims."""
        try:
            logging.info("Starting claim processing...")
            logging.info(f"Input file: {self.input_file.get()}")
            logging.info(f"Rules file: {self.rules_file.get()}")
            logging.info(f"Output file: {self.output_file.get()}")
            
            # Process the claims
            process_claims(
                input_path=self.input_file.get(),
                rules_path=self.rules_file.get(),
                output_path=self.output_file.get()
            )
            
            # Success - update UI in main thread
            self.root.after(0, self.processing_complete)
            
        except Exception as e:
            # Error - update UI in main thread
            self.root.after(0, lambda: self.processing_error(str(e)))
    
    def processing_complete(self):
        """Called when processing is complete."""
        self.progress.stop()
        self.process_button.config(state='normal')
        self.status.set("Processing complete!")
        
        # Show success message
        result = messagebox.askyesno(
            "Success", 
            f"Claims processed successfully!\n\nOutput saved to:\n{self.output_file.get()}\n\nWould you like to open the output file?"
        )
        
        if result:
            try:
                os.startfile(self.output_file.get())
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {e}")
    
    def processing_error(self, error_msg):
        """Called when processing encounters an error."""
        self.progress.stop()
        self.process_button.config(state='normal')
        self.status.set("Processing failed!")
        
        messagebox.showerror("Error", f"Processing failed:\n{error_msg}")
        logging.error(f"Processing error: {error_msg}")
    
    def run(self):
        """Run the GUI application."""
        self.root.mainloop()


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point."""
    # Check if running as PyInstaller executable
    if getattr(sys, 'frozen', False):
        # Running as executable - show GUI
        try:
            app = ClaimAnnotatorGUI()
            app.run()
        except Exception as e:
            print(f"Error starting GUI: {e}")
            input("Press Enter to exit...")
    else:
        # Running as script - show GUI
        app = ClaimAnnotatorGUI()
        app.run()


if __name__ == '__main__':
    main()
