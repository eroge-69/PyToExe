import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from pathlib import Path
import json
from datetime import datetime

# Get the directory where the script is located
SCRIPT_DIR = Path(__file__).resolve().parent
CSV_FILENAME = "master_interlock.csv"
CSV_PATH = SCRIPT_DIR / CSV_FILENAME

# Create empty CSV in script directory if missing
def create_csv_if_missing(path=CSV_PATH):
    if not path.exists():
        df = pd.DataFrame(columns=["key", "cause", "effect", "remark"])
        df.to_csv(path, index=False)
        print(f"Created empty CSV: {path}")
    return path.exists()

# Load and parse CSV into data dict
def build_is_data_from_csv(csv_path):
    try:
        df = pd.read_csv(csv_path)
        df.dropna(how='all', inplace=True)
        
        data_dict = {}
        
        for _, row in df.iterrows():
            key = str(row['key']).strip()
            if not key or key == 'nan':
                continue
            
            if key not in data_dict:
                data_dict[key] = {"cause": [], "effect": [], "remark": []}
            
            for col in ["cause", "effect", "remark"]:
                value = row.get(col)
                if pd.notna(value) and str(value).strip() and str(value).strip() != 'nan':
                    clean_value = str(value).strip()
                    if clean_value not in data_dict[key][col]:  # Avoid duplicates
                        data_dict[key][col].append(clean_value)
        
        return data_dict
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load CSV: {str(e)}")
        return {}

# Enhanced GUI App Class
class ISExplorerApp:
    def __init__(self, root, data):
        self.root = root
        self.root.title("🔗 IS Cause & Effect Explorer v2.0")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Configure modern color scheme
        self.colors = {
            'bg_primary': '#f8f9fa',
            'bg_secondary': '#ffffff',
            'accent': '#007bff',
            'accent_light': '#e3f2fd',
            'text_primary': '#212529',
            'text_secondary': '#6c757d',
            'success': '#28a745',
            'warning': '#ffc107',
            'danger': '#dc3545',
            'border': '#dee2e6'
        }
        
        self.root.configure(bg=self.colors['bg_primary'])
        self.data = data
        self.history = []  # Navigation history
        self.bookmarks = set()  # Bookmarked items
        self.search_results = []
        
        self.setup_styles()
        self.create_gui()
        self.load_settings()
        
    def setup_styles(self):
        """Configure modern ttk styles"""
        style = ttk.Style()
        
        # Configure treeview
        style.configure("Modern.Treeview", 
                       background=self.colors['bg_secondary'],
                       foreground=self.colors['text_primary'],
                       rowheight=28,
                       fieldbackground=self.colors['bg_secondary'],
                       borderwidth=1,
                       relief="solid")
        
        style.configure("Modern.Treeview.Heading",
                       background=self.colors['accent'],
                       foreground='white',
                       relief="flat",
                       font=('Segoe UI', 10, 'bold'))
        
        style.map("Modern.Treeview",
                 background=[('selected', self.colors['accent_light'])],
                 foreground=[('selected', self.colors['text_primary'])])
        
        # Configure buttons
        style.configure("Modern.TButton",
                       font=('Segoe UI', 9),
                       padding=(10, 5))
        
        # Configure notebook
        style.configure("Modern.TNotebook",
                       background=self.colors['bg_primary'])
        style.configure("Modern.TNotebook.Tab",
                       padding=[20, 8],
                       font=('Segoe UI', 9))
    
    def create_gui(self):
        """Create the main GUI layout"""
        # Create main container with padding
        main_container = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header section
        self.create_header(main_container)
        
        # Search and navigation section
        self.create_search_nav(main_container)
        
        # Main content area with notebook
        self.create_main_content(main_container)
        
        # Status bar
        self.create_status_bar(main_container)
    
    def create_header(self, parent):
        """Create header with title and controls"""
        header_frame = tk.Frame(parent, bg=self.colors['bg_primary'], height=60)
        header_frame.pack(fill="x", pady=(0, 10))
        header_frame.pack_propagate(False)
        
        # Title
        title_label = tk.Label(header_frame, 
                              text="🔗 IS Cause & Effect Explorer",
                              font=('Segoe UI', 16, 'bold'),
                              bg=self.colors['bg_primary'],
                              fg=self.colors['accent'])
        title_label.pack(side="left", pady=10)
        
        # Control buttons
        controls_frame = tk.Frame(header_frame, bg=self.colors['bg_primary'])
        controls_frame.pack(side="right", pady=10)
        
        # ttk.Button(controls_frame, text="📁 Load CSV", 
        #           command=self.load_csv, style="Modern.TButton").pack(side="left", padx=2)
        ttk.Button(controls_frame, text="💾 Export", 
                  command=self.export_data, style="Modern.TButton").pack(side="left", padx=2)
        ttk.Button(controls_frame, text="⚙️ Settings", 
                  command=self.show_settings, style="Modern.TButton").pack(side="left", padx=2)
    
    def create_search_nav(self, parent):
        """Create search and navigation section"""
        nav_frame = tk.Frame(parent, bg=self.colors['bg_secondary'], relief="solid", bd=1)
        nav_frame.pack(fill="x", pady=(0, 10))
        
        # Search section
        search_frame = tk.Frame(nav_frame, bg=self.colors['bg_secondary'])
        search_frame.pack(fill="x", padx=10, pady=8)
        
        tk.Label(search_frame, text="🔍 Search:", 
                font=('Segoe UI', 10, 'bold'),
                bg=self.colors['bg_secondary']).pack(side="left")
        
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                                   font=('Segoe UI', 10), width=30)
        self.search_entry.pack(side="left", padx=(5, 10))
        self.search_entry.bind('<KeyRelease>', self.on_search)
        self.search_entry.bind('<Return>', self.perform_search)
        
        ttk.Button(search_frame, text="Search", 
                  command=self.perform_search, style="Modern.TButton").pack(side="left", padx=2)
        ttk.Button(search_frame, text="Clear", 
                  command=self.clear_search, style="Modern.TButton").pack(side="left", padx=2)
        
        # Navigation section
        nav_controls = tk.Frame(search_frame, bg=self.colors['bg_secondary'])
        nav_controls.pack(side="right")
        
        ttk.Button(nav_controls, text="⬅️ Back", 
                  command=self.go_back, style="Modern.TButton").pack(side="left", padx=2)
        ttk.Button(nav_controls, text="🏠 Home", 
                  command=self.go_home, style="Modern.TButton").pack(side="left", padx=2)
        ttk.Button(nav_controls, text="⭐ Bookmarks", 
                  command=self.show_bookmarks, style="Modern.TButton").pack(side="left", padx=2)
    
    def create_main_content(self, parent):
        """Create main content area with tabbed interface"""
        # Dropdown section
        dropdown_frame = tk.Frame(parent, bg=self.colors['bg_secondary'], relief="solid", bd=1)
        dropdown_frame.pack(fill="x", pady=(0, 10))
        
        inner_dropdown = tk.Frame(dropdown_frame, bg=self.colors['bg_secondary'])
        inner_dropdown.pack(fill="x", padx=10, pady=8)
        
        tk.Label(inner_dropdown, text="📋 Select IS Block:", 
                font=('Segoe UI', 12, 'bold'),
                bg=self.colors['bg_secondary']).pack(side="left")
        
        self.selected_is = tk.StringVar()
        self.dropdown = ttk.Combobox(inner_dropdown, textvariable=self.selected_is, 
                                   values=sorted(list(self.data.keys())), 
                                   state="readonly", font=('Segoe UI', 10))
        self.dropdown.pack(side="left", padx=10, fill="x", expand=True)
        self.dropdown.bind("<<ComboboxSelected>>", self.display_info)
        
        # Bookmark button
        self.bookmark_btn = ttk.Button(inner_dropdown, text="⭐", 
                                     command=self.toggle_bookmark, style="Modern.TButton")
        self.bookmark_btn.pack(side="left", padx=5)
        
        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(parent, style="Modern.TNotebook")
        self.notebook.pack(fill="both", expand=True)
        
        # Main view tab
        self.create_main_tab()
        
        # Analysis tab
        self.create_analysis_tab()
        
        # Tree view tab
        self.create_tree_tab()
    
    def create_main_tab(self):
        """Create main cause-effect view tab"""
        main_tab = tk.Frame(self.notebook, bg=self.colors['bg_primary'])
        self.notebook.add(main_tab, text="📊 Cause & Effect")
        
        # Content frame
        content_frame = tk.Frame(main_tab, bg=self.colors['bg_primary'])
        content_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Cause and Effect frames
        tables_frame = tk.Frame(content_frame, bg=self.colors['bg_primary'])
        tables_frame.pack(fill="both", expand=True)
        
        # Causes section
        self.cause_frame = tk.Frame(tables_frame, bg=self.colors['bg_secondary'], 
                                   relief="solid", bd=1)
        self.cause_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        cause_header = tk.Frame(self.cause_frame, bg=self.colors['accent'], height=40)
        cause_header.pack(fill="x")
        cause_header.pack_propagate(False)
        
        tk.Label(cause_header, text="⬅️ CAUSES", 
                font=('Segoe UI', 14, 'bold'),
                bg=self.colors['accent'], fg='white').pack(expand=True)
        
        self.cause_tree = ttk.Treeview(self.cause_frame, columns=("Item",), 
                                     show="headings", selectmode="browse", 
                                     style="Modern.Treeview")
        self.cause_tree.heading("Item", text="Cause Items")
        self.cause_tree.pack(fill="both", expand=True, padx=5, pady=5)
        self.cause_tree.bind("<Double-1>", self.on_tree_double_click)
        
        # Effects section
        self.effect_frame = tk.Frame(tables_frame, bg=self.colors['bg_secondary'], 
                                   relief="solid", bd=1)
        self.effect_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        effect_header = tk.Frame(self.effect_frame, bg=self.colors['accent'], height=40)
        effect_header.pack(fill="x")
        effect_header.pack_propagate(False)
        
        tk.Label(effect_header, text="➡️ EFFECTS", 
                font=('Segoe UI', 14, 'bold'),
                bg=self.colors['accent'], fg='white').pack(expand=True)
        
        self.effect_tree = ttk.Treeview(self.effect_frame, columns=("Item",), 
                                      show="headings", selectmode="browse", 
                                      style="Modern.Treeview")
        self.effect_tree.heading("Item", text="Effect Items")
        self.effect_tree.pack(fill="both", expand=True, padx=5, pady=5)
        self.effect_tree.bind("<Double-1>", self.on_tree_double_click)

    def create_analysis_tab(self):
        """Create analysis tab"""
        analysis_tab = tk.Frame(self.notebook, bg=self.colors['bg_primary'])
        self.notebook.add(analysis_tab, text="📈 Analysis")
        
        # Statistics frame
        stats_frame = tk.LabelFrame(analysis_tab, text="📊 Statistics", 
                                  font=('Segoe UI', 12, 'bold'),
                                  bg=self.colors['bg_primary'])
        stats_frame.pack(fill="x", padx=10, pady=10)
        
        self.stats_text = tk.Text(stats_frame, height=8, font=('Segoe UI', 10),
                                bg=self.colors['bg_secondary'], state="disabled")
        self.stats_text.pack(fill="x", padx=5, pady=5)
        
        remarks_frame = tk.LabelFrame(analysis_tab, text="💬 Remarks", 
                                 font=('Segoe UI', 12, 'bold'),
                                 bg=self.colors['bg_primary'])
        remarks_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create remarks table similar to cause/effect tables
        self.remarks_tree = ttk.Treeview(remarks_frame, columns=("Item",), 
                                    show="headings",selectmode="browse", 
                                    style="Modern.Treeview")
        self.remarks_tree.heading("Item", text="Remarks")
        self.remarks_tree.pack(fill="both", expand=True, padx=5, pady=5)
    
    def create_tree_tab(self):
        """Create tree view tab for hierarchical visualization"""
        tree_tab = tk.Frame(self.notebook, bg=self.colors['bg_primary'])
        self.notebook.add(tree_tab, text="🌳 Hierarchy")
        
        tree_controls = tk.Frame(tree_tab, bg=self.colors['bg_primary'])
        tree_controls.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(tree_controls, text="🔄 Refresh Tree", 
                  command=self.refresh_tree, style="Modern.TButton").pack(side="left")
        ttk.Button(tree_controls, text="📤 Expand All", 
                  command=self.expand_all, style="Modern.TButton").pack(side="left", padx=5)
        ttk.Button(tree_controls, text="📥 Collapse All", 
                  command=self.collapse_all, style="Modern.TButton").pack(side="left")
        
        # Tree view
        tree_frame = tk.Frame(tree_tab, bg=self.colors['bg_secondary'], relief="solid", bd=1)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.hierarchy_tree = ttk.Treeview(tree_frame, style="Modern.Treeview")
        self.hierarchy_tree.pack(fill="both", expand=True, padx=5, pady=5)
        self.hierarchy_tree.bind("<Double-1>", self.on_hierarchy_double_click)
    
    def create_status_bar(self, parent):
        """Create status bar"""
        self.status_frame = tk.Frame(parent, bg=self.colors['border'], height=25)
        self.status_frame.pack(fill="x", side="bottom")
        self.status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(self.status_frame, 
                                   text=f"Ready | Total IS Blocks: {len(self.data)}", 
                                   font=('Segoe UI', 9),
                                   bg=self.colors['border'], 
                                   fg=self.colors['text_secondary'])
        self.status_label.pack(side="left", padx=5, pady=2)
        
        # Time label
        self.time_label = tk.Label(self.status_frame, 
                                 text=datetime.now().strftime("%H:%M:%S"),
                                 font=('Segoe UI', 9),
                                 bg=self.colors['border'], 
                                 fg=self.colors['text_secondary'])
        self.time_label.pack(side="right", padx=5, pady=2)
        
        # Update time every second
        self.update_time()
    
    def update_time(self):
        """Update time in status bar"""
        self.time_label.config(text=datetime.now().strftime("%H:%M:%S"))
        self.root.after(1000, self.update_time)
    
    # Enhanced functionality methods
    def display_info(self, event=None):
        """Display information for selected IS block"""
        is_block = self.selected_is.get()
        if is_block not in self.data:
            return
        
        # Add to history
        if not self.history or self.history[-1] != is_block:
            self.history.append(is_block)
            if len(self.history) > 20:  # Limit history
                self.history.pop(0)
        
        self.clear_tables()
        
        causes = self.data[is_block].get("cause", [])
        effects = self.data[is_block].get("effect", [])
        remarks = self.data[is_block].get("remark", [])
        
        self.populate_table(self.cause_tree, causes)
        self.populate_table(self.effect_tree, effects)
        
        # Update bookmark button
        if is_block in self.bookmarks:
            self.bookmark_btn.config(text="⭐")
        else:
            self.bookmark_btn.config(text="☆")
        
        # Update analysis
        self.update_analysis(is_block)
        
        # Update status
        self.status_label.config(text=f"Viewing: {is_block} | Causes: {len(causes)} | Effects: {len(effects)}")
    
    def populate_table(self, tree, items):
        """Populate tree with items, highlighting clickable ones"""
        for index, item in enumerate(items):
            is_clickable = item in self.data
            is_bookmarked = item in self.bookmarks
            
            display_text = f"⭐ {item}" if is_bookmarked else item
            
            if is_clickable:
                tree.insert("", "end", values=(display_text,), 
                          tags=("clickable", f"row{index % 2}"))
            else:
                tree.insert("", "end", values=(display_text,), 
                          tags=("static", f"row{index % 2}"))
        
        # Configure tags
        tree.tag_configure("clickable", 
                         foreground=self.colors['accent'], 
                         font=('Segoe UI', 10, 'underline'))
        tree.tag_configure("static", 
                         foreground=self.colors['text_primary'], 
                         font=('Segoe UI', 10))
        tree.tag_configure("row0", background="white")
        tree.tag_configure("row1", background="#f8f9fa")
    
    def clear_tables(self):
        """Clear all tables"""
        for tree in [self.cause_tree, self.effect_tree, self.remarks_tree]:
            for item in tree.get_children():
                tree.delete(item)
    
    def on_tree_double_click(self, event):
        """Handle double-click on tree items"""
        tree = event.widget
        item_id = tree.identify_row(event.y)
        if not item_id:
            return
        
        item_text = tree.item(item_id, "values")[0]
        # Remove bookmark star if present
        clean_text = item_text.replace("⭐ ", "")
        
        if clean_text in self.data:
            self.selected_is.set(clean_text)
            self.display_info()
    
    def on_hierarchy_double_click(self, event):
        """Handle double-click on hierarchy tree"""
        item_id = self.hierarchy_tree.identify_row(event.y)
        if not item_id:
            return
        
        item_text = self.hierarchy_tree.item(item_id, "text")
        if item_text in self.data:
            self.selected_is.set(item_text)
            self.display_info()
            # Switch to main tab
            self.notebook.select(0)
    
    def on_search(self, event=None):
        """Handle search input"""
        search_term = self.search_var.get().lower()
        if len(search_term) < 2:
            self.dropdown.config(values=sorted(list(self.data.keys())))
            return
        
        # Filter dropdown values
        filtered = [key for key in self.data.keys() 
                   if search_term in key.lower()]
        self.dropdown.config(values=sorted(filtered))
    
    def perform_search(self):
        """Perform detailed search"""
        search_term = self.search_var.get().lower()
        if not search_term:
            return
        
        results = []
        for key, data in self.data.items():
            # Search in key
            if search_term in key.lower():
                results.append(f"🔑 {key}")
            
            # Search in causes, effects, remarks
            for category in ['cause', 'effect', 'remark']:
                for item in data.get(category, []):
                    if search_term in item.lower():
                        results.append(f"{key} → {category}: {item}")
        
        if results:
            self.show_search_results(results)
        else:
            messagebox.showinfo("Search Results", f"No results found for '{search_term}'")
    
    def show_search_results(self, results):
        """Show search results in a popup"""
        result_window = tk.Toplevel(self.root)
        result_window.title("🔍 Search Results")
        result_window.geometry("600x400")
        result_window.configure(bg=self.colors['bg_primary'])
        
        tk.Label(result_window, text="Search Results", 
                font=('Segoe UI', 14, 'bold'),
                bg=self.colors['bg_primary']).pack(pady=10)
        
        listbox = tk.Listbox(result_window, font=('Segoe UI', 10))
        listbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        for result in results:
            listbox.insert(tk.END, result)
        
        def on_result_select(event):
            selection = listbox.get(listbox.curselection())
            if selection.startswith("🔑"):
                key = selection.replace("🔑 ", "")
                self.selected_is.set(key)
                self.display_info()
                result_window.destroy()
        
        listbox.bind("<Double-1>", on_result_select)
    
    def clear_search(self):
        """Clear search and reset dropdown"""
        self.search_var.set("")
        self.dropdown.config(values=sorted(list(self.data.keys())))
    
    def toggle_bookmark(self):
        """Toggle bookmark for current selection"""
        current = self.selected_is.get()
        if not current:
            return
        
        if current in self.bookmarks:
            self.bookmarks.remove(current)
            self.bookmark_btn.config(text="☆")
        else:
            self.bookmarks.add(current)
            self.bookmark_btn.config(text="⭐")
        
        # Refresh display to update bookmark indicators
        self.display_info()
    
    def show_bookmarks(self):
        """Show bookmarks dialog"""
        if not self.bookmarks:
            messagebox.showinfo("Bookmarks", "No bookmarks saved.")
            return
        
        bookmark_window = tk.Toplevel(self.root)
        bookmark_window.title("⭐ Bookmarks")
        bookmark_window.geometry("400x300")
        bookmark_window.configure(bg=self.colors['bg_primary'])
        
        tk.Label(bookmark_window, text="Your Bookmarks", 
                font=('Segoe UI', 14, 'bold'),
                bg=self.colors['bg_primary']).pack(pady=10)
        
        listbox = tk.Listbox(bookmark_window, font=('Segoe UI', 10))
        listbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        for bookmark in sorted(self.bookmarks):
            listbox.insert(tk.END, bookmark)
        
        def on_bookmark_select(event):
            if listbox.curselection():
                selection = listbox.get(listbox.curselection())
                self.selected_is.set(selection)
                self.display_info()
                bookmark_window.destroy()
        
        listbox.bind("<Double-1>", on_bookmark_select)
    
    def go_back(self):
        """Navigate back in history"""
        if len(self.history) > 1:
            self.history.pop()  # Remove current
            previous = self.history[-1]
            self.selected_is.set(previous)
            self.display_info()
    
    def go_home(self):
        """Go to first item or clear selection"""
        if self.data:
            first_key = sorted(list(self.data.keys()))[0]
            self.selected_is.set(first_key)
            self.display_info()
    
    def update_analysis(self, is_block):
        """Update analysis tab with statistics"""
        if is_block not in self.data:
            return
        
        data = self.data[is_block]
        causes = data.get("cause", [])
        effects = data.get("effect", [])
        remarks = data.get("remark", [])
        
        # Update statistics
        self.stats_text.config(state="normal")
        self.stats_text.delete("1.0", tk.END)
        
        stats = f"""Current IS Block: {is_block}
        
📊 STATISTICS:
• Number of Causes: {len(causes)}
• Number of Effects: {len(effects)}
• Number of Remarks: {len(remarks)}
• Clickable Causes: {sum(1 for c in causes if c in self.data)}
• Clickable Effects: {sum(1 for e in effects if e in self.data)}

🔗 CONNECTIVITY:
• Total Related Blocks: {len(set(causes + effects) & set(self.data.keys()))}
• Upstream Dependencies: {len([c for c in causes if c in self.data])}
• Downstream Dependencies: {len([e for e in effects if e in self.data])}
"""
        
        self.stats_text.insert("1.0", stats)
        self.stats_text.config(state="disabled")
        
        for item in self.remarks_tree.get_children():
            self.remarks_tree.delete(item)
        
        # Populate remarks table
        if remarks:
            for index, remark in enumerate(remarks):
                self.remarks_tree.insert("", "end", values=(remark,), 
                                    tags=(f"row{index % 2}",))
        else:
            self.remarks_tree.insert("", "end", values=("No remarks available for this IS block.",), 
                                tags=("no_remarks",))
        
        # Configure tags for styling
        self.remarks_tree.tag_configure("row0", background="white")
        self.remarks_tree.tag_configure("row1", background="#f8f9fa")
        self.remarks_tree.tag_configure("no_remarks", 
                                    foreground=self.colors['text_secondary'],
                                    font=('Segoe UI', 10, 'italic'))
    
    def refresh_tree(self):
        """Refresh hierarchy tree view"""
        # Clear existing tree
        for item in self.hierarchy_tree.get_children():
            self.hierarchy_tree.delete(item)
        
        # Build hierarchy
        processed = set()
        root_nodes = []
        
        # Find root nodes (items that are not effects of others)
        all_effects = set()
        for data in self.data.values():
            all_effects.update(data.get("effect", []))
        
        for key in self.data.keys():
            if key not in all_effects:
                root_nodes.append(key)
        
        # Add root nodes to tree
        for root in sorted(root_nodes):
            if root not in processed:
                self.add_tree_node("", root, processed, level=0)
    
    def add_tree_node(self, parent, node, processed, level=0):
        """Recursively add nodes to hierarchy tree"""
        if node in processed or level > 10:  # Prevent infinite recursion
            return
        
        processed.add(node)
        
        # Add current node
        node_id = self.hierarchy_tree.insert(parent, "end", text=node, 
                                           values=(f"Level {level}",))
        
        # Add children (effects that are also IS blocks)
        if node in self.data:
            effects = self.data[node].get("effect", [])
            for effect in sorted(effects):
                if effect in self.data and effect not in processed:
                    self.add_tree_node(node_id, effect, processed, level + 1)
    
    def expand_all(self):
        """Expand all tree nodes"""
        def expand_recursive(item):
            self.hierarchy_tree.item(item, open=True)
            for child in self.hierarchy_tree.get_children(item):
                expand_recursive(child)
        
        for item in self.hierarchy_tree.get_children():
            expand_recursive(item)
    
    def collapse_all(self):
        """Collapse all tree nodes"""
        def collapse_recursive(item):
            self.hierarchy_tree.item(item, open=False)
            for child in self.hierarchy_tree.get_children(item):
                collapse_recursive(child)
        
        for item in self.hierarchy_tree.get_children():
            collapse_recursive(item)
    
    def export_data(self):
        """Export current data"""
        if not self.data:
            messagebox.showwarning("Warning", "No data to export.")
            return
        
        export_window = tk.Toplevel(self.root)
        export_window.title("📤 Export Data")
        export_window.geometry("400x300")
        export_window.configure(bg=self.colors['bg_primary'])
        
        tk.Label(export_window, text="Export Options", 
                font=('Segoe UI', 14, 'bold'),
                bg=self.colors['bg_primary']).pack(pady=10)
        
        export_frame = tk.Frame(export_window, bg=self.colors['bg_primary'])
        export_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        def export_json():
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if file_path:
                try:
                    export_data = {
                        "metadata": {
                            "exported_at": datetime.now().isoformat(),
                            "total_blocks": len(self.data),
                            "bookmarks": list(self.bookmarks)
                        },
                        "data": self.data
                    }
                    with open(file_path, 'w') as f:
                        json.dump(export_data, f, indent=2)
                    messagebox.showinfo("Success", f"Data exported to {file_path}")
                    export_window.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Export failed: {str(e)}")
        
        def export_summary():
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if file_path:
                try:
                    with open(file_path, 'w') as f:
                        f.write("IS CAUSE & EFFECT EXPLORER - SUMMARY REPORT\n")
                        f.write("=" * 50 + "\n\n")
                        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"Total IS Blocks: {len(self.data)}\n")
                        f.write(f"Bookmarked Items: {len(self.bookmarks)}\n\n")
                        
                        for key, data in sorted(self.data.items()):
                            f.write(f"IS BLOCK: {key}\n")
                            f.write("-" * (len(key) + 10) + "\n")
                            
                            causes = data.get("cause", [])
                            effects = data.get("effect", [])
                            remarks = data.get("remark", [])
                            
                            f.write(f"Causes ({len(causes)}):\n")
                            for cause in causes:
                                f.write(f"  • {cause}\n")
                            
                            f.write(f"\nEffects ({len(effects)}):\n")
                            for effect in effects:
                                f.write(f"  • {effect}\n")
                            
                            if remarks:
                                f.write(f"\nRemarks:\n")
                                for remark in remarks:
                                    f.write(f"  • {remark}\n")
                            
                            f.write("\n" + "=" * 50 + "\n\n")
                    
                    messagebox.showinfo("Success", f"Summary exported to {file_path}")
                    export_window.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Export failed: {str(e)}")
        
        ttk.Button(export_frame, text="📄 Export as JSON", 
                  command=export_json, style="Modern.TButton").pack(pady=5, fill="x")
        ttk.Button(export_frame, text="📝 Export Summary Report", 
                  command=export_summary, style="Modern.TButton").pack(pady=5, fill="x")
        ttk.Button(export_frame, text="❌ Cancel", 
                  command=export_window.destroy, style="Modern.TButton").pack(pady=10)
    
    def show_settings(self):
        """Show settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("⚙️ Settings")
        settings_window.geometry("500x400")
        settings_window.configure(bg=self.colors['bg_primary'])
        
        tk.Label(settings_window, text="Application Settings", 
                font=('Segoe UI', 14, 'bold'),
                bg=self.colors['bg_primary']).pack(pady=10)
        
        notebook = ttk.Notebook(settings_window, style="Modern.TNotebook")
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # General settings
        general_frame = tk.Frame(notebook, bg=self.colors['bg_primary'])
        notebook.add(general_frame, text="General")
        
        tk.Label(general_frame, text="Theme:", 
                bg=self.colors['bg_primary']).pack(anchor="w", padx=10, pady=5)
        
        theme_var = tk.StringVar(value="Light")
        theme_combo = ttk.Combobox(general_frame, textvariable=theme_var,
                                 values=["Light", "Dark"], state="readonly")
        theme_combo.pack(anchor="w", padx=10, pady=5)
        
        # Display settings
        display_frame = tk.Frame(notebook, bg=self.colors['bg_primary'])
        notebook.add(display_frame, text="Display")
        
        show_bookmarks_var = tk.BooleanVar(value=True)
        tk.Checkbutton(display_frame, text="Show bookmark indicators in lists",
                      variable=show_bookmarks_var,
                      bg=self.colors['bg_primary']).pack(anchor="w", padx=10, pady=5)
        
        auto_expand_var = tk.BooleanVar(value=False)
        tk.Checkbutton(display_frame, text="Auto-expand tree hierarchy",
                      variable=auto_expand_var,
                      bg=self.colors['bg_primary']).pack(anchor="w", padx=10, pady=5)
        
        # About tab
        about_frame = tk.Frame(notebook, bg=self.colors['bg_primary'])
        notebook.add(about_frame, text="About")
        
        about_text = """
IS Cause & Effect Explorer v2.0

Enhanced features:
• Modern, responsive UI design
• Advanced search and filtering
• Navigation history and bookmarks
• Multi-tab interface with analysis
• Hierarchical tree visualization
• Data export capabilities
• Comprehensive statistics

Built with Python & Tkinter
        """
        
        tk.Label(about_frame, text=about_text, 
                bg=self.colors['bg_primary'],
                justify="left", font=('Segoe UI', 10)).pack(padx=20, pady=20)
        
        # Buttons
        button_frame = tk.Frame(settings_window, bg=self.colors['bg_primary'])
        button_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(button_frame, text="💾 Save Settings", 
                  command=lambda: self.save_settings(settings_window),
                  style="Modern.TButton").pack(side="right", padx=5)
        ttk.Button(button_frame, text="❌ Cancel", 
                  command=settings_window.destroy,
                  style="Modern.TButton").pack(side="right")
    
    def save_settings(self, window):
        """Save application settings"""
        # This would save settings to a config file in a real application
        messagebox.showinfo("Settings", "Settings saved successfully!")
        window.destroy()
    
    def load_settings(self):
        """Load application settings"""
        # This would load settings from a config file in a real application
        pass

# Enhanced main function
def main():
    """Main application entry point"""
    try:
        # Create CSV if missing
        csv_exists = create_csv_if_missing(CSV_PATH)
        
        # Load data
        is_data = build_is_data_from_csv(CSV_PATH)
        
        if not is_data and csv_exists:
            print("Warning: Kindly ensure Master Interlock CSV is available")
        
        # Create and run application
        root = tk.Tk()
        
        # Set application icon (if available)
        try:
            # You can add an icon file here
            # root.iconbitmap('icon.ico')
            pass
        except:
            pass
        
        # Configure root window
        root.minsize(800, 600)
        
        # Create application
        app = ISExplorerApp(root, is_data)
        
        # Handle window closing
        def on_closing():
            if messagebox.askokcancel("Quit", "Do you want to quit the application?"):
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Run application
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("Application Error", f"Failed to start application: {str(e)}")
        print(f"Error: {e}")

if __name__ == "__main__":
    main()