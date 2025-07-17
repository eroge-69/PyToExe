import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import tkinter.font as tkfont
import os
from datetime import datetime
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from collections import defaultdict
import colorsys

class RosterProcessor:
    def __init__(self):
        self.df_original = None
        self.df_processed = None
        self.OFF_KEYWORDS = ['WOFF', 'W/OFF', 'RD', 'OFF', 'REST', 'RDO', 'LEAVE']
        self.PATTERN_CODES = [
            "CX-1E2N2E2RD", "CX-2E2N1E2RD", "PAX-GEN-2RD", "PAX-A-2RD", "EBT-3A2N2RD", "EY-1N4E2RD",
            "EY-31700N2RD", "EY-1E117001E1N1E2RD", "EY-217003E2RD", "EY-317002E2RD", "EY-2E217001E2RD",
            "UL/VN-2G2M1RD1G1RD", "PAX-3M2N2RD", "Regular Afternoon", "Regular Morning", "PAX-EM", "PAX-M",
            "PAX-A", "PAX-E", "PAX-N", "SEC-MORN", "SEC-2MAN", "SEC-GEN", "SEC-GEN2", "CRP-GEN", "APR-M",
            "APR-N", "APR-1600-0000", "APR-1A3E1N2RD", "APR-AFT", "APR-1M3E1RD", "APR-2E1N2E2RD",
            "APR-2E1RD3E1RD", "APR-2M2A1E1N2RD", "APR-2M2A1N1E2RD", "APR-2M2A2E2RD", "APR-2M2A2N2RD",
            "APR-2M2E2N2RD", "APR-2M3E2RD", "APR-3G1M2G1RD", "APR-3M2E2RD", "APR-E", "Pax-Gen",
            "PAX-1M4E2RD", "PAX-2M1A2N2RD", "PAX-2M2E1N2RD", "PAX-2M3N2RD", "PAX-2A3E2RD", "EK-2M1A2E2RD",
            "PAX-2M3E2RD", "PAX-E-EY", "PAX-2E3N2RD", "ALL MORNINGS", "3 MORNING 3 AFTERNOON", "pcc-gen",
            "EK-2M3E2RD", "2M2E1N2RD", "EK-3M1E1N2RD", "EK-3M1N1E2RD", "EK-3M2E2RD", "IX-EM", "IX1300-2100",
            "IX1300-2200", "ALL NIGHTS", "2A3N2RD", "EY-1700-0230", "EBT-1m5a1rd", "DD-2E1N1E1RD1E1RD",
            "UL-1G2M1G2M1RD", "UL-2M1G1M2G1RD", "UL-1G1M2G2M1RD", "XY-1EM1M2EM1M1EM1RD", "1EM1M1EM1M2EM1RD",
            "SEC-3G2A1RD", "3A1E1N2RD", "3A2E2RD", "EY-1200-2000-", "MHB-1A1E1A2N2RD", "MHB-1M1A1E2N2RD",
            "MHB-2M2A2M1RD", "MHB-3M3G1RD", "MHB-2G3E2RD", "MHB-3M1G2M1RD", "MHB-1A2M1E1N2RD",
            "MHB-1A4N2RD", "MHB-2A2E1N2RD", "EK-5M1A1RD", "EY-1E117001E2N2RD", "SQ-4M2E1RD", "SQ-5M1E1RD",
            "SV-2G2M1G1M1RD", "SV-1G4M1G1RD", "SV-5M1G1RD"
        ]
        
    def format_date_headers(self, df):
        new_columns = []
        date_formats = [
            "%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d", "%d-%b-%y", "%d %B %Y",
            "%d-%m-%y", "%m-%d-%y", "%y-%m-%d", "%d/%m/%y", "%m/%d/%y"
        ]
        
        for col in df.columns:
            if isinstance(col, str):
                col = col.strip()
                converted = False
                for fmt in date_formats:
                    try:
                        dt = datetime.strptime(col, fmt)
                        new_columns.append(dt.strftime("%d-%m-%Y"))
                        converted = True
                        break
                    except ValueError:
                        continue
                if not converted:
                    if isinstance(col, datetime):
                        new_columns.append(col.strftime("%d-%m-%Y"))
                    else:
                        new_columns.append(col)
            elif isinstance(col, datetime):
                new_columns.append(col.strftime("%d-%m-%Y"))
            else:
                new_columns.append(col)
        df.columns = new_columns
        return df

    def detect_roster_begin(self, row, date_cols):
        for i, val in enumerate(row[date_cols]):
            if pd.isna(val):
                continue
                
            val_str = str(val).upper().strip()
            if any(off in val_str for off in self.OFF_KEYWORDS):
                for j in range(i + 1, len(date_cols)):
                    next_shift = str(row[date_cols[j]]).upper().strip()
                    if not any(off in next_shift for off in self.OFF_KEYWORDS):
                        return date_cols[j]
                return date_cols[0]
        return date_cols[0]

    def generate_roster_begin(self):
        if self.df_original is None:
            raise ValueError("No file loaded")

        date_cols = [col for col in self.df_original.columns if any(char in str(col) for char in ["/", "-"])]
        if not date_cols:
            date_cols = self.df_original.columns[2:9]
            
        self.df_processed = self.df_original.copy()
        self.df_processed = self.format_date_headers(self.df_processed)
        date_cols = [col for col in self.df_processed.columns if any(char in str(col) for char in ["/", "-"])]
        
        self.df_processed['Roster Begin Date'] = self.df_processed.apply(
            lambda row: self.detect_roster_begin(row, date_cols), axis=1)
        self.df_processed['Pattern Code'] = ""
        
        new_order = [col for col in self.df_processed.columns 
                     if col not in ['Roster Begin Date', 'Pattern Code']] + \
                   ['Roster Begin Date', 'Pattern Code']
        self.df_processed = self.df_processed[new_order]
        return self.df_processed

    def validate_data(self):
        """Validate roster data and return issues"""
        issues = []
        if self.df_processed is not None:
            # Check for missing employee IDs
            missing_ids = self.df_processed['EMP ID'].isna().sum()
            if missing_ids > 0:
                issues.append(f"Missing Employee IDs: {missing_ids}")
            
            # Check for empty pattern codes
            empty_patterns = self.df_processed['Pattern Code'].isna().sum()
            if empty_patterns > 0:
                issues.append(f"Empty Pattern Codes: {empty_patterns}")
                
        return issues

class NSKRosterApp:
    def __init__(self, root):
        self.root = root
        self.current_theme = "darkly"
        self.available_themes = ["darkly", "superhero", "vapor", "cyborg", "solar", "morph", "quartz", "pulse", "flatly", "litera"]
        self.style = ttk.Style(theme=self.current_theme)
        
        # Initialize theme colors
        self.update_theme_colors()
        
        self.processor = RosterProcessor()
        self.setup_ui()
        self.setup_autocomplete()
        self.shift_colors = {}
        
    def update_theme_colors(self):
        """Update theme colors based on current theme"""
        self.bg_color = self.style.colors.dark
        self.fg_color = self.style.colors.light
        self.select_color = self.style.colors.primary
        
    def change_theme(self, theme_name):
        """Change the application theme"""
        try:
            self.current_theme = theme_name
            self.style.theme_use(theme_name)
            self.update_theme_colors()
            self.update_treeview_style()
            self.status_var.set(f"Theme changed to: {theme_name}")
        except Exception as e:
            messagebox.showerror("Theme Error", f"Failed to change theme: {str(e)}")
        
    def update_treeview_style(self):
        """Update treeview styling after theme change"""
        self.style.configure("Treeview", 
                             background=self.bg_color, 
                             foreground=self.fg_color,
                             fieldbackground=self.bg_color,
                             rowheight=28)
        self.style.configure("Treeview.Heading", 
                             background=self.style.colors.primary, 
                             foreground=self.fg_color,
                             font=("Segoe UI", 10, "bold"))
        self.style.map("Treeview", 
                      background=[("selected", self.select_color)])
        
    def setup_ui(self):
        self.root.title("NSK's Roster Analyzer Pro")
        self.root.geometry("1400x800")
        
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header frame with NSK branding
        header_frame = ttk.Frame(main_container, padding=15)
        header_frame.pack(fill="x", pady=(0, 10))
        
        # NSK's Title with enhanced styling
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side="left", fill="x", expand=True)
        
        main_title = ttk.Label(
            title_frame, 
            text="NSK's ROSTER ANALYZER", 
            font=("Segoe UI", 18, "bold"),
            bootstyle="primary"
        )
        main_title.pack(anchor="w")
        
        subtitle = ttk.Label(
            title_frame,
            text="Professional Shift Management Suite",
            font=("Segoe UI", 10, "italic"),
            bootstyle="secondary"
        )
        subtitle.pack(anchor="w", pady=(0, 5))
        
        # Theme selector
        theme_frame = ttk.Frame(header_frame)
        theme_frame.pack(side="right", padx=(20, 0))
        
        ttk.Label(theme_frame, text="Theme:", font=("Segoe UI", 10)).pack(side="left", padx=(0, 5))
        
        self.theme_var = tk.StringVar(value=self.current_theme)
        theme_combo = ttk.Combobox(
            theme_frame,
            textvariable=self.theme_var,
            values=self.available_themes,
            state="readonly",
            width=12,
            bootstyle="primary"
        )
        theme_combo.pack(side="left")
        theme_combo.bind("<<ComboboxSelected>>", lambda e: self.change_theme(self.theme_var.get()))
        
        # Button frame with enhanced layout
        btn_frame = ttk.Frame(main_container)
        btn_frame.pack(fill="x", pady=(0, 15))
        
        # Primary actions
        primary_frame = ttk.Frame(btn_frame)
        primary_frame.pack(side="left", fill="x", expand=True)
        
        primary_actions = [
            ("📂 Import File", self.browse_file, "primary", "Import roster data from Excel/CSV"),
            ("⚙️ Generate Roster", self.generate_roster, "success", "Generate roster begin dates"),
            ("💾 Export Data", self.export_to_excel, "warning", "Export processed data to Excel"),
            ("🔍 Validate Data", self.validate_data, "info", "Check data integrity")
        ]
        
        for text, command, style, tooltip in primary_actions:
            btn = ttk.Button(
                primary_frame, 
                text=text, 
                command=command, 
                bootstyle=style,
                width=15
            )
            btn.pack(side="left", padx=5)
            self.create_tooltip(btn, tooltip)
        
        # Secondary actions
        secondary_frame = ttk.Frame(btn_frame)
        secondary_frame.pack(side="right")
        
        secondary_actions = [
            ("➕ Add Pattern", self.add_pattern_code, "secondary", "Add new pattern code"),
            ("📊 Statistics", self.show_statistics, "info", "View data statistics"),
            ("🔧 Settings", self.show_settings, "dark", "Application settings")
        ]
        
        for text, command, style, tooltip in secondary_actions:
            btn = ttk.Button(
                secondary_frame, 
                text=text, 
                command=command, 
                bootstyle=style,
                width=12
            )
            btn.pack(side="left", padx=2)
            self.create_tooltip(btn, tooltip)
        
        # Search frame
        search_frame = ttk.Frame(main_container)
        search_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(search_frame, text="Search:", font=("Segoe UI", 10)).pack(side="left", padx=(0, 5))
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            width=30,
            bootstyle="primary"
        )
        search_entry.pack(side="left", padx=(0, 10))
        search_entry.bind("<KeyRelease>", self.search_data)
        
        ttk.Button(
            search_frame,
            text="Clear",
            command=self.clear_search,
            bootstyle="secondary",
            width=8
        ).pack(side="left")
        
        # Table frame with enhanced styling
        table_frame = ttk.LabelFrame(
            main_container, 
            text="📋 Roster Data", 
            bootstyle="primary",
            padding=15
        )
        table_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Treeview with enhanced scrollbars
        self.tree = ttk.Treeview(
            table_frame,
            show="headings",
            bootstyle="primary",
            selectmode="extended"
        )
        
        # Enhanced scrollbars
        vsb = ttk.Scrollbar(
            table_frame, 
            orient="vertical", 
            command=self.tree.yview,
            bootstyle="primary-round"
        )
        hsb = ttk.Scrollbar(
            table_frame, 
            orient="horizontal", 
            command=self.tree.xview,
            bootstyle="primary-round"
        )
        
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        # Configure grid weights
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Configure initial treeview style
        self.update_treeview_style()
        
        # Enhanced status bar
        status_frame = ttk.Frame(main_container)
        status_frame.pack(fill="x", pady=(5, 0))
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - NSK's Roster Analyzer Pro")
        
        status_label = ttk.Label(
            status_frame, 
            textvariable=self.status_var,
            bootstyle="secondary",
            anchor="w",
            font=("Segoe UI", 9)
        )
        status_label.pack(side="left", fill="x", expand=True, padx=10)
        
        # Progress bar (initially hidden)
        self.progress = ttk.Progressbar(
            status_frame,
            mode="indeterminate",
            bootstyle="primary-striped"
        )
        
        # Record count label
        self.record_count_var = tk.StringVar()
        self.record_count_var.set("Records: 0")
        
        record_label = ttk.Label(
            status_frame,
            textvariable=self.record_count_var,
            bootstyle="info",
            font=("Segoe UI", 9)
        )
        record_label.pack(side="right", padx=10)
        
        # Bind events
        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Control-d>", self.copy_from_above)  # Ctrl+D binding
        self.tree.bind("<Button-1>", self.on_treeview_click)  # Track last clicked position
        self.tree.bind("<Return>", self.on_enter_key)  # Enter key binding
        
        # Track last clicked position
        self.last_clicked_column = None
        self.last_clicked_row = None
        
    def on_treeview_click(self, event):
        """Track last clicked cell position"""
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            self.last_clicked_column = self.tree.identify_column(event.x)
            self.last_clicked_row = self.tree.identify_row(event.y)
            
    def on_enter_key(self, event):
        """Handle Enter key press in treeview"""
        if self.last_clicked_row and self.last_clicked_column:
            # Only move to next row if we're in the Pattern Code column
            if self.last_clicked_column == f"#{len(self.tree['columns'])}":
                next_item = self.tree.next(self.last_clicked_row)
                if next_item:
                    self.tree.selection_set(next_item)
                    self.tree.focus(next_item)
                    self.tree.see(next_item)
                    self.last_clicked_row = next_item
                    # Edit the cell in Pattern Code column
                    self.edit_cell(next_item, f"#{len(self.tree['columns'])}")
                    
    def copy_from_above(self, event):
        """Copy value from cell above to selected cells"""
        if self.last_clicked_row and self.last_clicked_column:
            prev_item = self.tree.prev(self.last_clicked_row)
            if prev_item:
                value_above = self.tree.set(prev_item, self.last_clicked_column)
                
                # Update all selected cells
                selected_items = self.tree.selection()
                for item in selected_items:
                    self.tree.set(item, self.last_clicked_column, value_above)
                    
                    # Update DataFrame if available
                    if self.processor.df_processed is not None:
                        index = int(self.tree.index(item))
                        col_name = self.tree["columns"][int(self.last_clicked_column[1:])-1]
                        self.processor.df_processed.at[index, col_name] = value_above
                        
                self.status_var.set("Copied from above")
                self.update_table(self.processor.df_processed)  # Refresh table to update highlighting
                
    def generate_color(self, shift_value, column_name):
        """Generate consistent color for a shift value in a specific column"""
        # Create a unique key for this shift value in this column
        key = f"{column_name}_{shift_value}"
        
        # Return existing color if we have one
        if key in self.shift_colors:
            return self.shift_colors[key]
            
        # Generate new color using HSV color space for better distribution
        hue = (len(self.shift_colors) * 0.618) % 1.0  # Golden ratio for distribution
        saturation = 0.7
        value = 0.85 if self.current_theme in ["darkly", "cyborg", "solar"] else 0.7
        
        # Convert HSV to RGB
        r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
        r, g, b = int(r * 255), int(g * 255), int(b * 255)
        
        # Format as hex color
        color = f"#{r:02x}{g:02x}{b:02x}"
        self.shift_colors[key] = color
        return color
        
    def highlight_shifts(self, df):
        """Highlight same shift timings in each column"""
        if df is None:
            return
            
        # Clear existing shift tags by resetting all items to just row color tags
        for idx, item in enumerate(self.tree.get_children()):
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.tree.item(item, tags=(tag,))
        
        # Create tags for each unique shift value in each column
        shift_columns = [col for col in df.columns if any(char in str(col) for char in ["/", "-"])]
        
        for col in shift_columns:
            col_idx = df.columns.get_loc(col) + 1  # +1 because tree columns are 1-indexed
            
            # Group rows by shift value
            groups = defaultdict(list)
            for idx, value in enumerate(df[col]):
                if pd.isna(value):
                    value = ""
                groups[str(value)].append(idx)
                
            # Create tags for each group
            for value, indices in groups.items():
                if not value:  # Skip empty values
                    continue
                    
                color = self.generate_color(value, col)
                tag_name = f"shift_{col}_{value}"
                
                # Configure tag
                self.tree.tag_configure(tag_name, background=color)
                
                # Apply tag to all items in this group
                for idx in indices:
                    if idx < len(self.tree.get_children()):
                        item = self.tree.get_children()[idx]
                        current_tags = list(self.tree.item(item, "tags"))
                        current_tags.append(tag_name)
                        self.tree.item(item, tags=current_tags)
    
    def create_tooltip(self, widget, text):
        """Create tooltip for widget"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = ttk.Label(
                tooltip,
                text=text,
                background=self.bg_color,
                foreground=self.fg_color,
                relief="solid",
                borderwidth=1,
                font=("Segoe UI", 9)
            )
            label.pack()
            
            def hide_tooltip():
                tooltip.destroy()
                
            tooltip.after(3000, hide_tooltip)
            widget.tooltip = tooltip
            
        def hide_tooltip(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                
        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)
        
    def setup_autocomplete(self):
        self.autocomplete_window = None
        self.autocomplete_listbox = None
        self.current_edit = None
        self.selected_index = 0
        
    def search_data(self, event=None):
        """Search functionality for the data table"""
        search_term = self.search_var.get().lower()
        
        if not search_term:
            self.update_table(self.processor.df_processed if self.processor.df_processed is not None else self.processor.df_original)
            return
            
        if self.processor.df_processed is not None:
            df = self.processor.df_processed
        elif self.processor.df_original is not None:
            df = self.processor.df_original
        else:
            return
            
        # Filter dataframe based on search term
        filtered_df = df[df.astype(str).apply(lambda x: x.str.lower().str.contains(search_term, na=False)).any(axis=1)]
        self.update_table(filtered_df)
        
    def clear_search(self):
        """Clear search and show all data"""
        self.search_var.set("")
        self.update_table(self.processor.df_processed if self.processor.df_processed is not None else self.processor.df_original)
        
    def show_context_menu(self, event):
        """Show context menu on right-click"""
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="Copy Cell", command=self.copy_cell)
        context_menu.add_command(label="Copy Row", command=self.copy_row)
        context_menu.add_separator()
        context_menu.add_command(label="Edit Cell", command=lambda: self.on_double_click(event))
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
            
    def copy_cell(self):
        """Copy selected cell to clipboard"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            # Get the column that was clicked
            # This is a simplified version - you might want to track the actual clicked column
            values = self.tree.item(item)['values']
            if values:
                self.root.clipboard_clear()
                self.root.clipboard_append(str(values[0]))
                self.status_var.set("Cell copied to clipboard")
                
    def copy_row(self):
        """Copy selected row to clipboard"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item)['values']
            row_text = '\t'.join(str(val) for val in values)
            self.root.clipboard_clear()
            self.root.clipboard_append(row_text)
            self.status_var.set("Row copied to clipboard")
            
    def show_statistics(self):
        """Show data statistics"""
        if self.processor.df_processed is None and self.processor.df_original is None:
            messagebox.showwarning("No Data", "Please load data first")
            return
            
        df = self.processor.df_processed if self.processor.df_processed is not None else self.processor.df_original
        
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Data Statistics")
        stats_window.geometry("400x300")
        
        stats_text = tk.Text(stats_window, wrap=tk.WORD, padx=10, pady=10)
        stats_text.pack(fill="both", expand=True)
        
        # Generate statistics
        stats = f"""Data Statistics - NSK's Roster Analyzer

Total Records: {len(df)}
Total Columns: {len(df.columns)}

Column Information:
"""
        for col in df.columns:
            non_null = df[col].notna().sum()
            stats += f"• {col}: {non_null} non-null values\n"
            
        if 'Pattern Code' in df.columns:
            pattern_counts = df['Pattern Code'].value_counts()
            stats += f"\nTop Pattern Codes:\n"
            for pattern, count in pattern_counts.head(5).items():
                stats += f"• {pattern}: {count}\n"
                
        stats_text.insert(tk.END, stats)
        stats_text.config(state=tk.DISABLED)
        
    def show_settings(self):
        """Show application settings"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("350x250")
        
        ttk.Label(settings_window, text="Application Settings", font=("Segoe UI", 12, "bold")).pack(pady=10)
        
        # Add settings options here
        ttk.Label(settings_window, text="More settings coming soon...").pack(pady=20)
        
        ttk.Button(settings_window, text="Close", command=settings_window.destroy).pack(pady=10)
        
    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Roster File",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            self.progress.pack(side="right", padx=10)
            self.progress.start()
            
            try:
                if file_path.endswith('.csv'):
                    df = pd.read_csv(file_path, dtype={'EMP ID': str})
                else:
                    df = pd.read_excel(file_path, dtype={'EMP ID': str})
                
                df = self.processor.format_date_headers(df)
                self.processor.df_original = df
                self.update_table(df)
                self.status_var.set(f"Loaded: {os.path.basename(file_path)} - {len(df)} records")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file:\n{str(e)}")
                self.status_var.set("Error loading file")
            finally:
                self.progress.stop()
                self.progress.pack_forget()
    
    def generate_roster(self):
        if self.processor.df_original is None:
            messagebox.showwarning("No Data", "Please load a file first")
            return
            
        self.progress.pack(side="right", padx=10)
        self.progress.start()
        
        try:
            df = self.processor.generate_roster_begin()
            self.update_table(df)
            self.status_var.set("Roster dates generated with Pattern Code column")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status_var.set("Error generating roster")
        finally:
            self.progress.stop()
            self.progress.pack_forget()
    
    def validate_data(self):
        """Validate the current data"""
        if self.processor.df_processed is None:
            messagebox.showwarning("No Data", "Please generate roster data first")
            return
            
        issues = self.processor.validate_data()
        
        if issues:
            issue_text = "\n".join(issues)
            messagebox.showwarning("Data Validation", f"Issues found:\n\n{issue_text}")
        else:
            messagebox.showinfo("Data Validation", "✅ All data looks good!")
            
        self.status_var.set(f"Validation complete - {len(issues)} issues found")
    
    def update_table(self, df):
        if df is None:
            return
            
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Update columns
        self.tree["columns"] = list(df.columns)
        
        # Configure columns
        font = tkfont.Font(family="Segoe UI", size=10)
        
        for col in df.columns:
            self.tree.heading(col, text=col, anchor="center")
            col_width = font.measure(col) + 40
            
            # Sample data for width calculation
            sample_data = df[col].astype(str).head(50)
            for val in sample_data:
                col_width = max(col_width, font.measure(str(val)) + 40)
                
            self.tree.column(col, width=min(col_width, 300), anchor='center')
        
        # Insert data with alternating row colors
        for idx, (_, row) in enumerate(df.iterrows()):
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.tree.insert("", "end", values=list(row), tags=(tag,))
            
        # Configure row colors
        self.tree.tag_configure("evenrow", background=self.bg_color)
        self.tree.tag_configure("oddrow", background=self.style.colors.secondary)
        
        # Apply shift highlighting
        self.highlight_shifts(df)
        
        # Update record count
        self.record_count_var.set(f"Records: {len(df)}")
    
    def on_double_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            item = self.tree.identify_row(event.y)
            
            # Only allow editing of Pattern Code column (last column)
            if column == "#" + str(len(self.tree["columns"])):
                self.edit_cell(item, column)
    
    def edit_cell(self, item, column):
        # Get cell coordinates and current value
        x, y, width, height = self.tree.bbox(item, column)
        current_value = self.tree.set(item, column)
        
        # Create entry widget
        entry = ttk.Entry(
            self.tree, 
            font=("Segoe UI", 10),
            bootstyle="primary"
        )
        entry.place(x=x, y=y, width=width, height=height, anchor="nw")
        entry.insert(0, current_value)
        entry.select_range(0, tk.END)
        entry.focus()
        
        # Bind events
        entry.bind("<Return>", lambda e: self.save_cell(item, column, entry))
        entry.bind("<Tab>", lambda e: self.save_cell(item, column, entry))
        entry.bind("<Escape>", lambda e: self.cancel_edit(entry))
        entry.bind("<KeyRelease>", lambda e: self.update_autocomplete(entry))
        entry.bind("<Up>", lambda e: self.handle_entry_up(e))
        entry.bind("<Down>", lambda e: self.handle_entry_down(e))
        
        self.current_edit = (item, column, entry)
        self.selected_index = 0
    
    def handle_entry_up(self, event):
        if self.autocomplete_listbox and self.autocomplete_listbox.winfo_exists():
            if self.selected_index > 0:
                self.selected_index -= 1
                self.autocomplete_listbox.selection_clear(0, tk.END)
                self.autocomplete_listbox.selection_set(self.selected_index)
                self.autocomplete_listbox.see(self.selected_index)
        return "break"
    
    def handle_entry_down(self, event):
        if self.autocomplete_listbox and self.autocomplete_listbox.winfo_exists():
            max_index = self.autocomplete_listbox.size() - 1
            if self.selected_index < max_index:
                self.selected_index += 1
                self.autocomplete_listbox.selection_clear(0, tk.END)
                self.autocomplete_listbox.selection_set(self.selected_index)
                self.autocomplete_listbox.see(self.selected_index)
        return "break"
    
    def cancel_edit(self, entry):
        """Cancel editing and clean up"""
        self.hide_autocomplete()
        if entry.winfo_exists():
            entry.destroy()
        self.current_edit = None
    
    def update_autocomplete(self, entry):
        # Small delay to make typing smoother
        self.root.after(100, self._delayed_autocomplete, entry)
    
    def _delayed_autocomplete(self, entry):
        # Check if entry still exists
        if not entry.winfo_exists():
            return
            
        text = entry.get().upper()
        if not text:
            self.hide_autocomplete()
            return
            
        # Find matches that start with the typed text (primary matches)
        primary_matches = [code for code in self.processor.PATTERN_CODES if code.upper().startswith(text)]
        # Find matches that contain the typed text (secondary matches)
        secondary_matches = [code for code in self.processor.PATTERN_CODES 
                           if text in code.upper() and not code.upper().startswith(text)]
        
        # Combine primary and secondary matches
        matches = primary_matches + secondary_matches
        
        if matches:
            self.show_autocomplete(entry, matches)
        else:
            self.hide_autocomplete()
    
    def show_autocomplete(self, entry, matches):
        # Check if entry still exists
        if not entry.winfo_exists():
            return
            
        if self.autocomplete_window:
            self.autocomplete_window.destroy()
            
        x = entry.winfo_rootx()
        y = entry.winfo_rooty() + entry.winfo_height()
        
        self.autocomplete_window = tk.Toplevel(self.root)
        self.autocomplete_window.wm_overrideredirect(True)
        self.autocomplete_window.wm_geometry(f"+{x}+{y}")
        self.autocomplete_window.configure(bg=self.bg_color)
        
        # Limit number of items
        max_items = 8
        matches = matches[:max_items]
        
        self.autocomplete_listbox = tk.Listbox(
            self.autocomplete_window,
            height=min(len(matches), max_items),
            width=max(len(match) for match in matches) + 2,
            selectbackground=self.select_color,
            selectforeground=self.fg_color,
            bg=self.bg_color,
            fg=self.fg_color,
            font=("Segoe UI", 10),
            bd=1,
            highlightthickness=0,
            relief="solid",
            activestyle="none"
        )
        self.autocomplete_listbox.pack()
        
        for match in matches:
            self.autocomplete_listbox.insert(tk.END, match)
        
        # Select first item by default
        self.selected_index = 0
        self.autocomplete_listbox.selection_set(0)
        
        # Bind events but don't steal focus
        self.autocomplete_listbox.bind("<Button-1>", self.on_autocomplete_click)
        self.autocomplete_listbox.bind("<Double-Button-1>", self.on_autocomplete_double_click)
        
        # Keep focus on entry
        entry.focus()
    
    def on_autocomplete_click(self, event):
        # Update selected index based on click
        self.selected_index = self.autocomplete_listbox.nearest(event.y)
        self.autocomplete_listbox.selection_clear(0, tk.END)
        self.autocomplete_listbox.selection_set(self.selected_index)
        
        # Return focus to entry
        if self.current_edit:
            _, _, entry = self.current_edit
            if entry.winfo_exists():
                entry.focus()
    
    def on_autocomplete_double_click(self, event):
        self.select_autocomplete()
    
    def hide_autocomplete(self):
        if self.autocomplete_window:
            self.autocomplete_window.destroy()
            self.autocomplete_window = None
            self.autocomplete_listbox = None
    
    def select_autocomplete(self, event=None):
        if self.autocomplete_listbox and self.current_edit:
            if self.selected_index < self.autocomplete_listbox.size():
                selection = self.autocomplete_listbox.get(self.selected_index)
                item, column, entry = self.current_edit
                
                # Check if entry still exists
                if not entry.winfo_exists():
                    self.hide_autocomplete()
                    return
                
                # Update the entry widget
                entry.delete(0, tk.END)
                entry.insert(0, selection)
                
                # Update the cell immediately
                self.tree.set(item, column, selection)
                
                # Update DataFrame
                if self.processor.df_processed is not None:
                    index = int(self.tree.index(item))
                    col_name = self.tree["columns"][int(column[1:])-1]
                    self.processor.df_processed.at[index, col_name] = selection
                
                # Close autocomplete window and clean up
                self.hide_autocomplete()
                entry.destroy()
                self.current_edit = None
                self.update_table(self.processor.df_processed)  # Refresh table to update highlighting
    
    def save_cell(self, item, column, entry):
        # Check if entry still exists
        if not entry.winfo_exists():
            return
        
        # If autocomplete is visible and user pressed Enter, select from autocomplete
        if self.autocomplete_listbox and self.autocomplete_listbox.winfo_exists():
            self.select_autocomplete()
            return
            
        new_value = entry.get()
        self.tree.set(item, column, new_value)
        
        # Update DataFrame
        if self.processor.df_processed is not None:
            index = int(self.tree.index(item))
            col_name = self.tree["columns"][int(column[1:])-1]
            self.processor.df_processed.at[index, col_name] = new_value
        
        # Clean up
        self.hide_autocomplete()
        entry.destroy()
        self.current_edit = None
        
        # Auto-move to next row in Pattern Code column
        col_index = int(column[1:])
        if col_index == len(self.tree["columns"]):  # If in Pattern Code column
            next_item = self.tree.next(item)
            if next_item:
                self.root.after(100, lambda: self.edit_cell(next_item, column))
                self.update_table(self.processor.df_processed)  # Refresh table to update highlighting
    
    def export_to_excel(self):
        if self.processor.df_processed is None:
            messagebox.showwarning("No Data", "Please generate roster data first")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Export Roster Data",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv")]
        )
        
        if file_path:
            self.progress.pack(side="right", padx=10)
            self.progress.start()
            
            try:
                # Ensure all date headers are in DD-MM-YYYY format
                self.processor.df_processed = self.processor.format_date_headers(self.processor.df_processed)
                
                if file_path.endswith('.csv'):
                    self.processor.df_processed.to_csv(file_path, index=False)
                else:
                    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                        self.processor.df_processed.to_excel(writer, index=False, sheet_name="Roster Data")
                        effective_df = self.processor.df_processed[['EMP ID', 'Roster Begin Date', 'Pattern Code']].copy()
                        effective_df.to_excel(writer, index=False, sheet_name="Effective Dates")
                
                self.status_var.set(f"Exported to {os.path.basename(file_path)}")
                messagebox.showinfo("Export Success", f"File exported successfully to:\n{file_path}")
                
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export file:\n{str(e)}")
                self.status_var.set("Export failed")
            finally:
                self.progress.stop()
                self.progress.pack_forget()
    
    def add_pattern_code(self):
        new_code = simpledialog.askstring(
            "Add Pattern Code", 
            "Enter new pattern code:",
            parent=self.root
        )
        if new_code and new_code.strip():
            new_code = new_code.strip()
            if new_code not in self.processor.PATTERN_CODES:
                self.processor.PATTERN_CODES.append(new_code)
                self.processor.PATTERN_CODES.sort()  # Keep sorted for better UX
                self.status_var.set(f"Added new pattern code: {new_code}")
                messagebox.showinfo("Success", f"Added new pattern code: {new_code}")
            else:
                messagebox.showwarning("Duplicate", "Pattern code already exists!")

# Enhanced main execution
if __name__ == "__main__":
    try:
        root = ttk.Window(title="NSK's Roster Analyzer Pro", themename="darkly")
        
        # Set window icon and additional properties
        root.resizable(True, True)
        root.minsize(1000, 600)
        
        # Center the window on screen
        root.geometry("1400x800")
        root.eval('tk::PlaceWindow . center')
        
        # Create the application
        app = NSKRosterApp(root)
        
        # Handle window closing
        def on_closing():
            if messagebox.askokcancel("Quit", "Do you want to quit NSK's Roster Analyzer?"):
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Start the application
        root.mainloop()
        
    except Exception as e:
        import traceback
        error_msg = f"Application failed to start:\n{str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        
        # Try to show error in GUI, fallback to console
        try:
            error_root = tk.Tk()
            error_root.withdraw()
            messagebox.showerror("Startup Error", error_msg)
            error_root.destroy()
        except:
            print(error_msg)