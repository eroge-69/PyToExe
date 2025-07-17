import os
import pandas as pd
from tkinter import *
from tkinter import filedialog, messagebox, ttk
from tkinter.font import Font
from tkinter.simpledialog import Dialog

class ColumnSelectDialog(Toplevel):
    def __init__(self, parent, title, columns, selected_columns):
        super().__init__(parent)
        self.title(title)
        self.transient(parent)
        self.grab_set()
        
        self.columns = list(dict.fromkeys(columns))
        self.selected_columns = selected_columns
        self.result = None
        self.checkboxes = {}
        
        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        
    def create_widgets(self):
        mainframe = Frame(self)
        mainframe.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        Label(mainframe, text="Select columns to display:", 
              font=('Segoe UI', 12)).pack(pady=(0,10))
        
        btn_frame = Frame(mainframe)
        btn_frame.pack(fill=X)
        
        Button(btn_frame, text="Select All", command=self.select_all,
              font=('Segoe UI', 10)).pack(side=LEFT, padx=5)
        Button(btn_frame, text="Deselect All", command=self.deselect_all,
              font=('Segoe UI', 10)).pack(side=LEFT, padx=5)
        
        self.canvas = Canvas(mainframe, borderwidth=0)
        scrollbar = ttk.Scrollbar(mainframe, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = Frame(self.canvas)
        
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.bind("<MouseWheel>", self._on_mousewheel)
        self.scrollable_frame.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        
        cols_per_row = 3
        for i, col in enumerate(self.columns):
            var = BooleanVar(value=col in self.selected_columns)
            cb = Checkbutton(self.scrollable_frame, text=col, variable=var, 
                           font=('Segoe UI', 12), anchor='w')
            cb.grid(row=i//cols_per_row, column=i%cols_per_row, 
                   sticky='w', padx=5, pady=2)
            self.checkboxes[col] = var
        
        for i in range(cols_per_row):
            self.scrollable_frame.grid_columnconfigure(i, weight=1)
        
        btn_frame = Frame(mainframe)
        btn_frame.pack(pady=10)
        
        Button(btn_frame, text="OK", command=self.on_ok, 
              font=('Segoe UI', 10)).pack(side=LEFT, padx=5)
        Button(btn_frame, text="Cancel", command=self.on_cancel,
              font=('Segoe UI', 10)).pack(side=LEFT, padx=5)
        
        self.minsize(600, 500)
        self.resizable(False, True)
    
    def _on_mousewheel(self, event):
        if event.delta:
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        return "break"
    
    def select_all(self):
        for var in self.checkboxes.values():
            var.set(True)
    
    def deselect_all(self):
        for var in self.checkboxes.values():
            var.set(False)
    
    def on_ok(self):
        self.result = [col for col, var in self.checkboxes.items() if var.get()]
        self.destroy()
    
    def on_cancel(self):
        self.result = None
        self.destroy()

class CSVComparator:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Change Viewer - Folder Comparison")
        self.root.state('zoomed')
        
        self.configure_styles()
        
        self.folder1_path = StringVar()
        self.folder2_path = StringVar()
        self.status = StringVar(value="Ready")
        self.search_text = StringVar()  # For other columns
        self.key_search_text = StringVar()  # For key column
        self.search_column = StringVar(value="All Columns")
        self.selected_file = StringVar()
        self.visible_columns = []
        self.all_columns = []
        self.changed_files = []
        self.all_comparison_results = {}
        self.column_search_terms = StringVar()  # For multi-column search
        
        self.create_widgets()
    
    def configure_styles(self):
        self.bold_font = Font(family="Segoe UI", size=12, weight="bold")
        self.large_font = Font(family="Segoe UI", size=12)
        self.pop_font = Font(family="Segoe UI", size=14)

        style = ttk.Style()
        
        style.configure("Treeview",
                      font=self.large_font,
                      rowheight=35,
                      background="white",
                      fieldbackground="white",
                      bordercolor="#333333",
                      borderwidth=2,
                      relief="solid")
        
        style.map("Treeview",
                background=[('selected', '#0078d7')],
                foreground=[('selected', 'white')])
        
        style.configure("Treeview.Heading",
                      background="#f0f0f0",
                      bordercolor="#333333",
                      borderwidth=2,
                      relief="solid")
    
    def create_widgets(self):
        main_frame = Frame(self.root)
        main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Folder comparison widgets
        folder_comp_frame = LabelFrame(main_frame, text="Folder Comparison", padx=10, pady=5)
        folder_comp_frame.pack(fill=X)
        
        Label(folder_comp_frame, text="Original Folder:", font=self.large_font).grid(row=0, column=0, sticky=W)
        Entry(folder_comp_frame, textvariable=self.folder1_path, width=40, font=self.large_font).grid(row=0, column=1, padx=5)
        Button(folder_comp_frame, text="Browse", command=lambda: self.browse_folder(1), 
              font=self.large_font).grid(row=0, column=2, padx=5)
        
        Label(folder_comp_frame, text="Modified Folder:", font=self.large_font).grid(row=1, column=0, sticky=W)
        Entry(folder_comp_frame, textvariable=self.folder2_path, width=40, font=self.large_font).grid(row=1, column=1, padx=5)
        Button(folder_comp_frame, text="Browse", command=lambda: self.browse_folder(2), 
              font=self.large_font).grid(row=1, column=2, padx=5)
        
        # File selection for folder mode
        self.file_select_frame = Frame(folder_comp_frame)
        self.file_select_frame.grid(row=2, column=0, columnspan=3, pady=5, sticky=W)
        
        Label(self.file_select_frame, text="Select File:", font=self.large_font).pack(side=LEFT)
        self.file_combobox = ttk.Combobox(self.file_select_frame, textvariable=self.selected_file, 
                                        state="readonly", font=self.large_font, width=30)
        self.file_combobox.pack(side=LEFT, padx=5)
        self.file_combobox.bind("<<ComboboxSelected>>", lambda e: self.show_selected_file())
        
        # Common controls
        key_frame = Frame(main_frame)
        key_frame.pack(fill=X, pady=5)
        
        Button(key_frame, text="COMPARE", command=self.compare_folders, 
              font=self.bold_font, bg="#4CAF50", fg="white", padx=10).pack(side=LEFT, padx=10)
        Button(key_frame, text="Select Columns", command=self.select_columns, 
              font=self.large_font, padx=10).pack(side=LEFT, padx=10)
        Button(key_frame, text="Export", command=self.export_to_csv, 
              font=self.large_font, padx=10).pack(side=LEFT, padx=10)
        
        # Search frames
        search_frame = Frame(main_frame)
        search_frame.pack(fill=X, pady=(5,0))

        # Key column search frame
        key_search_frame = LabelFrame(search_frame, text="Key Column Search (OR)", padx=10, pady=5)
        key_search_frame.pack(side=LEFT, fill=X, expand=True)

        Label(key_search_frame, text="Search Key:", font=self.large_font).grid(row=0, column=0, sticky=W)
        Entry(key_search_frame, textvariable=self.key_search_text, width=30, font=self.large_font).grid(row=0, column=1, padx=5)

        Button(key_search_frame, text="Search", command=self.perform_key_search, 
            font=self.large_font, bg="#28a745", fg="white").grid(row=0, column=2, padx=5)
        Button(key_search_frame, text="Clear", command=self.clear_key_search, 
            font=self.large_font).grid(row=0, column=3, padx=5)

        # Multi-column search frame
        multi_search_frame = LabelFrame(search_frame, text="Multi-Column Search (AND)", padx=10, pady=5)
        multi_search_frame.pack(side=LEFT, fill=X, expand=True)

        Label(multi_search_frame, text="Search Terms:", font=self.large_font).grid(row=0, column=0, sticky=W)
        Entry(multi_search_frame, textvariable=self.column_search_terms, width=30, font=self.large_font).grid(row=0, column=1, padx=5)

        Button(multi_search_frame, text="Select Columns", command=self.show_column_search_popup, 
            font=self.large_font, bg="#0078d7", fg="white").grid(row=0, column=2, padx=5)
        Button(multi_search_frame, text="Search", command=self.perform_multi_column_search,
            font=self.large_font, bg="#28a745", fg="white").grid(row=0, column=3, padx=5)
        Button(multi_search_frame, text="Clear", command=self.clear_search, 
            font=self.large_font).grid(row=0, column=4, padx=5)
        
        # Results frame
        results_frame = Frame(main_frame)
        results_frame.pack(fill=BOTH, expand=True, pady=(5,0))
        
        tree_container = Frame(results_frame)
        tree_container.pack(fill=BOTH, expand=True)
        
        hsb = ttk.Scrollbar(tree_container, orient="horizontal")
        hsb.pack(side=BOTTOM, fill=X)
        
        vsb = ttk.Scrollbar(tree_container, orient="vertical")
        vsb.pack(side=RIGHT, fill=Y)
        
        self.tree = ttk.Treeview(tree_container,
                                xscrollcommand=hsb.set,
                                yscrollcommand=vsb.set,
                                style="Treeview")
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        
        hsb.config(command=self.tree.xview)
        vsb.config(command=self.tree.yview)
        
        self.tree.bind("<MouseWheel>", self._on_tree_mousewheel)
        
        self.status_bar = Label(main_frame, textvariable=self.status, bd=2, relief=SUNKEN, 
                              anchor=W, font=self.large_font, bg="#f0f0f0")
        self.status_bar.pack(fill=X, pady=(5,0))
    
    def _on_tree_mousewheel(self, event):
        if event.delta:
            self.tree.yview_scroll(int(-1*(event.delta/120)), "units")
        return "break"
    
    def browse_folder(self, folder_num):
        folder_path = filedialog.askdirectory()
        if folder_path:
            if folder_num == 1:
                self.folder1_path.set(folder_path)
            else:
                self.folder2_path.set(folder_path)
    
    def compare_folders(self):
        folder1 = self.folder1_path.get()
        folder2 = self.folder2_path.get()
        
        if not folder1 or not folder2:
            messagebox.showerror("Error", "Please select both folders")
            return
        
        try:
            self.status.set("Scanning folders...")
            self.root.update()
            
            # Get list of CSV files in each folder
            csv_files1 = [f for f in os.listdir(folder1) if f.endswith('.csv')]
            csv_files2 = [f for f in os.listdir(folder2) if f.endswith('.csv')]
            
            # Find common CSV files
            common_files = sorted(set(csv_files1) & set(csv_files2))
            
            if not common_files:
                messagebox.showinfo("Info", "No common CSV files found in both folders.")
                return
            
            self.changed_files = []
            self.all_comparison_results = {}
            
            # Compare all files and find which ones have differences
            for file in common_files:
                try:
                    file1_path = os.path.join(folder1, file)
                    file2_path = os.path.join(folder2, file)
                    
                    # Add this parameter to drop unnamed columns when reading CSVs
                    df1 = pd.read_csv(file1_path, index_col=False).loc[:, ~pd.read_csv(file1_path).columns.str.contains('^Unnamed')]
                    df2 = pd.read_csv(file2_path, index_col=False).loc[:, ~pd.read_csv(file2_path).columns.str.contains('^Unnamed')]
                    
                    df1.columns = df1.columns.str.strip()
                    df2.columns = df2.columns.str.strip()
                    
                    # Find differences and let the method determine the best key column
                    results = self.find_differences(df1, df2, df1.columns[0] if len(df1.columns) > 0 else None)
                    current_key_col = results.get('key_col')
                    
                    # Only store files with differences
                    if results['changed'] or results['added'] or results['removed']:
                        self.changed_files.append(file)
                        self.all_comparison_results[file] = {
                            'results': results,
                            'key_col': current_key_col,
                            'file1_path': file1_path,
                            'file2_path': file2_path,
                            'all_columns': list(df1.columns)  # Store all columns for this file
                        }
                
                except Exception as e:
                    print(f"Error comparing file {file}: {str(e)}")
                    continue
            
            if not self.changed_files:
                messagebox.showinfo("No Differences", "No differences found in any of the files.")
                return
            
            # Update the combobox with only changed files
            self.file_combobox['values'] = self.changed_files
            if self.changed_files:
                self.selected_file.set(self.changed_files[0])
                # Clear any previous display
                self.tree.delete(*self.tree.get_children())
                self.all_items = []
                self.search_text.set("")
                self.search_column.set("All Columns")
                self.show_selected_file()
            
            self.status.set(f"Found {len(self.changed_files)} files with differences out of {len(common_files)} common files")
        
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.status.set("Error occurred")
    
    def show_selected_file(self):
        # Clear the current display
        self.tree.delete(*self.tree.get_children())
        self.all_items = []
        self.search_text.set("")
        self.search_column.set("All Columns")
        
        filename = self.selected_file.get()
        if not filename or filename not in self.all_comparison_results:
            return
        
        file_data = self.all_comparison_results[filename]
        results = file_data['results']
        key_col = file_data.get('key_col')  # Get the key column from file_data
        
        # Reset visible columns for the new file
        self.visible_columns = ['Changes'] + ([key_col] if key_col else []) + ['Status']
        
        self.display_results(results, key_col)
        
        self.status.set(f"Showing {filename} - Changed: {len(results['changed'])}, Added: {len(results['added'])}, Removed: {len(results['removed'])}, Unchanged: {len(results.get('unchanged', []))}")
    
    def find_differences(self, df1, df2, key_col):
        results = {
            'changed': [],
            'added': [],
            'removed': [],
            'unchanged': [],  # Track unchanged rows
            'columns': list(df1.columns),
            'key_col': None
        }
        
        # If key_col is specified and exists in both files, use it
        if key_col and key_col in df1.columns and key_col in df2.columns:
            try:
                df1 = df1.set_index(key_col)
                df2 = df2.set_index(key_col)
                
                added_keys = df2.index.difference(df1.index)
                removed_keys = df1.index.difference(df2.index)
                
                results['added'] = df2.loc[added_keys].reset_index().to_dict('records')
                results['removed'] = df1.loc[removed_keys].reset_index().to_dict('records')
                
                common_keys = df1.index.intersection(df2.index)
                for key in common_keys:
                    row1 = df1.loc[key]
                    row2 = df2.loc[key]
                    
                    other_cols = [col for col in df1.columns if col != key_col]
                    diff_cols = [col for col in other_cols if str(row1[col]) != str(row2[col])]
                    
                    if diff_cols:
                        changes = {
                            'key': key,
                            'changes': {col: {'old': row1[col], 'new': row2[col]} for col in diff_cols},
                            'full_row': row2.to_dict()
                        }
                        results['changed'].append(changes)
                    else:
                        # Track unchanged rows
                        unchanged = {
                            'key': key,
                            'full_row': row2.to_dict()
                        }
                        results['unchanged'].append(unchanged)
                
                results['key_col'] = key_col
                return results
            except:
                # If setting index fails, fall through to alternative methods
                pass
        
        # If key column doesn't exist in both files, fall back to tuple comparison
        # First try to find a common column that could serve as key
        common_columns = set(df1.columns) & set(df2.columns)
        possible_key_col = None
        
        # Look for a column named 'id' or similar that might be a key
        for col in common_columns:
            if col.lower() in ['id', 'key', 'identifier']:
                possible_key_col = col
                break
        
        if possible_key_col:
            # Try using the possible key column
            try:
                df1 = df1.set_index(possible_key_col)
                df2 = df2.set_index(possible_key_col)
                
                added_keys = df2.index.difference(df1.index)
                removed_keys = df1.index.difference(df2.index)
                
                results['added'] = df2.loc[added_keys].reset_index().to_dict('records')
                results['removed'] = df1.loc[removed_keys].reset_index().to_dict('records')
                
                common_keys = df1.index.intersection(df2.index)
                for key in common_keys:
                    row1 = df1.loc[key]
                    row2 = df2.loc[key]
                    
                    other_cols = [col for col in df1.columns if col != possible_key_col]
                    diff_cols = [col for col in other_cols if str(row1[col]) != str(row2[col])]
                    
                    if diff_cols:
                        changes = {
                            'key': key,
                            'changes': {col: {'old': row1[col], 'new': row2[col]} for col in diff_cols},
                            'full_row': row2.to_dict()
                        }
                        results['changed'].append(changes)
                    else:
                        # Track unchanged rows
                        unchanged = {
                            'key': key,
                            'full_row': row2.to_dict()
                        }
                        results['unchanged'].append(unchanged)
                
                results['key_col'] = possible_key_col
                return results
            except:
                # If setting index fails, fall through to tuple comparison
                pass
        
        # Fall back to comparing entire rows
        df1['__temp_key__'] = df1.apply(tuple, axis=1)
        df2['__temp_key__'] = df2.apply(tuple, axis=1)
        
        added = df2[~df2['__temp_key__'].isin(df1['__temp_key__'])].drop('__temp_key__', axis=1)
        removed = df1[~df1['__temp_key__'].isin(df2['__temp_key__'])].drop('__temp_key__', axis=1)
        
        results['added'] = added.to_dict('records')
        results['removed'] = removed.to_dict('records')
        
        return results
    
    def select_columns(self):
        filename = self.selected_file.get()
        if not filename or filename not in self.all_comparison_results:
            messagebox.showwarning("Warning", "Please select a file first")
            return
        
        # Store current search state
        current_search_type = None
        current_search_terms = ""
        current_search_columns = []
        
        if hasattr(self, 'column_search_vars'):
            # Multi-column search is active
            current_search_type = "multi"
            current_search_terms = self.column_search_terms.get()
            current_search_columns = [col for col, var in self.column_search_vars.items() if var.get()]
        elif self.key_search_text.get():
            # Key search is active
            current_search_type = "key"
            current_search_terms = self.key_search_text.get()
        
        file_data = self.all_comparison_results[filename]
        key_col = file_data.get('key_col')
        
        # Get all available columns (including special columns)
        all_cols = ['Changes'] + ([key_col] if key_col else []) + file_data['all_columns'] + ['Status']
        all_cols = list(dict.fromkeys(all_cols))  # Remove duplicates while preserving order
        
        # Get current visible columns or use default if not set
        current_visible = self.visible_columns if self.visible_columns else ['Changes'] + ([key_col] if key_col else []) + ['Status']
        
        dialog = ColumnSelectDialog(self.root, "Select Columns", all_cols, current_visible)
        self.root.wait_window(dialog)

        if dialog.result is not None:
            new_visible = dialog.result
            # Ensure Changes and Status columns are always included
            if 'Changes' not in new_visible:
                new_visible.insert(0, 'Changes')
            if 'Status' not in new_visible:
                new_visible.append('Status')
            # Ensure key column is included if it exists
            if key_col and key_col not in new_visible:
                new_visible.insert(1, key_col)
                
            self.visible_columns = new_visible
            
            # Redisplay the current file with new column selection
            self.display_results(file_data['results'], key_col)
            
            # Reapply search if one was active
            if current_search_type == "multi" and current_search_terms and current_search_columns:
                # Filter to only include columns that still exist in the new visible set
                valid_search_columns = [col for col in current_search_columns if col in new_visible]
                if valid_search_columns:
                    self.column_search_terms.set(current_search_terms)
                    # Recreate the search vars (simplified version)
                    self.column_search_vars = {col: BooleanVar(value=col in valid_search_columns) for col in valid_search_columns}
                    self.perform_multi_column_search()
            elif current_search_type == "key" and current_search_terms:
                self.key_search_text.set(current_search_terms)
                self.perform_key_search()
    
    def display_results(self, results, key_col):
        self.tree.delete(*self.tree.get_children())
        
        # Use the visible columns that were set
        visible_cols = self.visible_columns.copy()
        
        # Configure tree columns
        self.tree["columns"] = visible_cols
        self.tree.column("#0", width=0, stretch=NO)
        
        for col in visible_cols:
            width = 600 if col == 'Changes' else 150 if col == 'Status' else 200
            self.tree.column(col, width=width, minwidth=50, stretch=NO)
            self.tree.heading(col, text=col)
        
        self.all_items = []
        
        # Display added rows
        for row in results['added']:
            key_value = row.get(key_col, '') if key_col else ''
            changes = f"NEW ROW (Key: {key_value})" if key_col else "ENTIRE ROW ADDED"
            
            values = []
            for col in visible_cols:
                if col == 'Changes':
                    values.append(changes)
                elif col == 'Status':
                    values.append("ADDED")
                elif col == key_col:
                    values.append(key_value)
                else:
                    values.append(row.get(col, ""))
            
            item_id = self.tree.insert("", END, values=values, tags=('added',))
            self.all_items.append((item_id, values))
        
        # Display removed rows
        for row in results['removed']:
            key_value = row.get(key_col, '') if key_col else ''
            changes = f"DELETED ROW (Key: {key_value})" if key_col else "ENTIRE ROW REMOVED"
            
            values = []
            for col in visible_cols:
                if col == 'Changes':
                    values.append(changes)
                elif col == 'Status':
                    values.append("REMOVED")
                elif col == key_col:
                    values.append(key_value)
                else:
                    values.append(row.get(col, ""))
            
            item_id = self.tree.insert("", END, values=values, tags=('removed',))
            self.all_items.append((item_id, values))
        
        # Display changed rows
        for change in results['changed']:
            row_data = change['full_row']
            key_value = change['key']
            change_list = []
            
            for col, vals in change['changes'].items():
                if col != key_col:
                    change_list.append(f"{col}: {vals['old']} → {vals['new']}")
            
            changes = " | ".join(change_list)
            
            values = []
            for col in visible_cols:
                if col == 'Changes':
                    values.append(changes)
                elif col == 'Status':
                    values.append("CHANGED")
                elif col == key_col:
                    values.append(key_value)
                else:
                    values.append(row_data.get(col, ""))
            
            item_id = self.tree.insert("", END, values=values, tags=('changed',))
            self.all_items.append((item_id, values))
        
        # Display unchanged rows
        for unchanged in results.get('unchanged', []):
            row_data = unchanged['full_row']
            key_value = unchanged['key']
            
            values = []
            for col in visible_cols:
                if col == 'Changes':
                    values.append("No changes")
                elif col == 'Status':
                    values.append("UNCHANGED")
                elif col == key_col:
                    values.append(key_value)
                else:
                    values.append(row_data.get(col, ""))
            
            item_id = self.tree.insert("", END, values=values, tags=('unchanged',))
            self.all_items.append((item_id, values))

        # Configure row colors
        self.tree.tag_configure('added', background='#d4edda')  # Light green
        self.tree.tag_configure('removed', background='#f8d7da')  # Light red
        self.tree.tag_configure('changed', background='#fff3cd')  # Light yellow
        self.tree.tag_configure('unchanged', background='#d1ecf1')  # Light blue
    
    def show_column_search_popup(self):
        filename = self.selected_file.get()
        if not filename or filename not in self.all_comparison_results:
            messagebox.showwarning("Warning", "Please select a file first")
            return
        
        # Get all available columns (excluding special columns)
        file_data = self.all_comparison_results[filename]
        columns = [col for col in file_data['all_columns'] if col != file_data.get('key_col', '')]
        
        if not columns:
            messagebox.showinfo("Info", "No columns available for search")
            return
        
        # Create popup window
        self.column_search_popup = Toplevel(self.root)
        self.column_search_popup.title("Select Columns to Search")
        self.column_search_popup.transient(self.root)
        self.column_search_popup.grab_set()
        
        mainframe = Frame(self.column_search_popup)
        mainframe.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Column selection
        Label(mainframe, text="Select columns to search (AND operation):", font=self.large_font).pack(anchor=W)
        
        # Add Select All/Deselect All buttons
        btn_frame = Frame(mainframe)
        btn_frame.pack(fill=X, pady=(0, 5))
        
        Button(btn_frame, text="Select All", command=lambda: self.set_all_column_search_vars(True),
            font=self.large_font).pack(side=LEFT, padx=5)
        Button(btn_frame, text="Deselect All", command=lambda: self.set_all_column_search_vars(False),
            font=self.large_font).pack(side=LEFT, padx=5)
        
        canvas = Canvas(mainframe, borderwidth=0)
        scrollbar = ttk.Scrollbar(mainframe, orient="vertical", command=canvas.yview)
        scrollable_frame = Frame(canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Initialize search vars if they don't exist
        if not hasattr(self, 'column_search_vars'):
            self.column_search_vars = {}
        
        # Create checkboxes with current selection state
        self.column_checkboxes = {}  # Store references to checkboxes
        for col in columns:
            # Use existing var if it exists, otherwise create new one
            if col in self.column_search_vars:
                var = self.column_search_vars[col]
            else:
                var = BooleanVar(value=False)
                self.column_search_vars[col] = var
                
            cb = Checkbutton(scrollable_frame, text=col, variable=var, 
                            font=self.large_font, anchor='w')
            cb.pack(anchor='w', padx=5, pady=2)
            self.column_checkboxes[col] = cb
        
        # Buttons
        btn_frame = Frame(mainframe)
        btn_frame.pack(pady=(10,0))
        
        def on_ok():
            # Store the selected columns before closing
            self.selected_search_columns = [col for col, var in self.column_search_vars.items() if var.get()]
            self.column_search_popup.destroy()
        
        Button(btn_frame, text="OK", command=on_ok,
            font=self.large_font).pack(side=LEFT, padx=5)
        
        self.column_search_popup.minsize(400, 400)
        self.column_search_popup.resizable(True, True)

    def set_all_column_search_vars(self, value):
        """Set all column search checkboxes to the specified value (True/False)"""
        if hasattr(self, 'column_search_vars'):
            for var in self.column_search_vars.values():
                var.set(value)

    def perform_multi_column_search(self):
        filename = self.selected_file.get()
        if not filename or filename not in self.all_comparison_results:
            messagebox.showwarning("Warning", "Please select a file first")
            return
        
        if not hasattr(self, 'column_search_vars'):
            messagebox.showwarning("Warning", "Please select columns to search first")
            return
        
        search_terms = self.column_search_terms.get()
        if not search_terms:
            messagebox.showwarning("Warning", "Please enter search terms")
            return
        
        terms = [term.strip().lower() for term in search_terms.split(",") if term.strip()]
        if not terms:
            messagebox.showwarning("Warning", "Please enter valid search terms")
            return
        
        selected_columns = [col for col, var in self.column_search_vars.items() if var.get()]
        if not selected_columns:
            messagebox.showwarning("Warning", "Please select at least one column")
            return
        
        # Get column indices
        columns = self.tree["columns"]
        column_indices = []
        for col in selected_columns:
            try:
                column_indices.append(columns.index(col))
            except ValueError:
                continue
        
        if not column_indices:
            messagebox.showerror("Error", "Selected columns not found in display")
            return
        
        # First hide all items
        for item_id in self.tree.get_children():
            self.tree.detach(item_id)
        
        matched_items = []
        for item_id, values in self.all_items:
            # Track which terms have been matched
            matched_terms = set()
            
            # Check each selected column for matches
            for col_idx in column_indices:
                if col_idx < len(values):
                    cell_value = str(values[col_idx]).lower()
                    
                    # Check each term against this column
                    for term in terms:
                        if term in cell_value:
                            matched_terms.add(term)
            
            # If all terms were matched (could be in different columns)
            if len(matched_terms) == len(terms):
                matched_items.append(item_id)
                self.tree.reattach(item_id, "", "end")
        
        if matched_items:
            self.tree.see(matched_items[0])
            self.tree.selection_set(matched_items[0])
            self.status.set(f"Found {len(matched_items)} items where each search term matches in at least one column")
        else:
            messagebox.showinfo("Search", "No matching items found")
            self.clear_search()

    def perform_key_search(self):
        filename = self.selected_file.get()
        if not filename or filename not in self.all_comparison_results:
            messagebox.showwarning("Warning", "Please select a file first")
            return
        
        file_data = self.all_comparison_results[filename]
        key_col = file_data.get('key_col')
        
        if not key_col:
            messagebox.showinfo("Info", "No key column identified for this file")
            return
        
        search_terms = self.key_search_text.get()
        if not search_terms:
            self.clear_key_search()
            return
        
        terms = [term.strip().lower() for term in search_terms.split(",") if term.strip()]
        if not terms:
            self.clear_key_search()
            return
        
        # First hide all items
        for item_id in self.tree.get_children():
            self.tree.detach(item_id)
        
        # Find key column index
        columns = self.tree["columns"]
        try:
            key_idx = columns.index(key_col)
        except ValueError:
            messagebox.showerror("Error", f"Key column '{key_col}' not found in display")
            return
        
        matched_items = []
        for item_id, values in self.all_items:
            if key_idx < len(values):
                cell_value = str(values[key_idx]).lower()
                # Modified to use partial matching (OR operation)
                if any(term in cell_value for term in terms):
                    matched_items.append(item_id)
                    self.tree.reattach(item_id, "", "end")
        
        if matched_items:
            self.tree.see(matched_items[0])
            self.tree.selection_set(matched_items[0])
            self.status.set(f"Showing {len(matched_items)} matching items (Key column OR search)")
        else:
            messagebox.showinfo("Search", "No matching items found")
            self.clear_key_search()

    def clear_key_search(self):
        self.key_search_text.set("")
        # Reattach all items
        for item_id, _ in self.all_items:
            self.tree.reattach(item_id, "", "end")
        # Reset selection and status
        self.tree.selection_set()
        self.status.set("Key search cleared - showing all items")

    def clear_search(self):
        self.column_search_terms.set("")
        # Reattach all items
        for item_id, _ in self.all_items:
            self.tree.reattach(item_id, "", "end")
        # Reset selection and status
        self.tree.selection_set()
        self.status.set("Search cleared - showing all items")
    
    def export_to_csv(self):
        filename = self.selected_file.get()
        if not filename or filename not in self.all_comparison_results:
            messagebox.showwarning("Warning", "Please select a file first")
            return
        
        # Get the visible columns
        visible_cols = self.visible_columns
        
        # Get all items from the treeview
        items = []
        for item_id in self.tree.get_children():
            item = self.tree.item(item_id)
            items.append(item['values'])
        
        if not items:
            messagebox.showwarning("Warning", "No data to export")
            return
        
        # Ask for save location
        default_filename = f"export_{filename.replace('.csv', '')}.csv"
        save_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=default_filename
        )
        
        if not save_path:
            return  # User cancelled
        
        try:
            # Create DataFrame from the treeview data
            df = pd.DataFrame(items, columns=visible_cols)
            
            # Export to CSV
            df.to_csv(save_path, index=False)
            messagebox.showinfo("Success", f"Data exported successfully to:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data:\n{str(e)}")

if __name__ == "__main__":
    root = Tk()
    app = CSVComparator(root)
    root.mainloop()