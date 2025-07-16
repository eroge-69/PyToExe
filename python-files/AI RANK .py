import os
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
import threading
import json
from datetime import datetime

# --- Configuration ---
SAVE_FOLDER_NAME = "save"
AUTOLEVEL_FILENAME = "autolevel.save"
AI_RANK_FILENAME = "AI_Rank.save"
CHECK_INTERVAL = 1  # Time in seconds to check for file updates
CONFIG_FILE = "ranker_config.json"

# --- Ranking Tiers ---
TIERS = {
    "God": (150, float('inf')),
    "S": (100, 149),
    "A": (70, 99),
    "B": (40, 69),
    "C": (20, 39),
    "D": (0, 19),
    "E": (-20, -1),
    "F": (float('-inf'), -21),
}

# --- Dark Theme Colors ---
DARK_THEME = {
    'bg': '#2b2b2b',
    'fg': '#ffffff',
    'select_bg': '#404040',
    'select_fg': '#ffffff',
    'entry_bg': '#3c3c3c',
    'entry_fg': '#ffffff',
    'button_bg': '#404040',
    'button_fg': '#ffffff',
    'frame_bg': '#2b2b2b',
    'treeview_bg': '#3c3c3c',
    'treeview_fg': '#ffffff',
    'treeview_select': '#505050',
    'scrollbar_bg': '#404040',
    'scrollbar_fg': '#606060'
}

# --- Tier Colors ---
TIER_COLORS = {
    'God': '#FFD700',  # Gold
    'S': '#FF6B6B',    # Red
    'A': '#4ECDC4',    # Teal
    'B': '#45B7D1',    # Blue
    'C': '#96CEB4',    # Green
    'D': '#FECA57',    # Yellow
    'E': '#FF9FF3',    # Pink
    'F': '#A0A0A0'     # Gray
}

class CharacterRankerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Salty Bet Style Character Ranker")
        self.root.geometry("1000x700")
        self.root.configure(bg=DARK_THEME['bg'])
        
        # Data variables
        self.characters = {}
        self.ai_ranks = []
        self.ranked_characters = []
        self.monitoring = False
        self.monitor_thread = None
        self.last_mod_autolevel = 0
        self.last_mod_ai_rank = 0
        
        # Paths
        self.autolevel_path = None
        self.ai_rank_path = None
        
        # Load configuration
        self.load_config()
        
        # Setup GUI
        self.setup_styles()
        self.create_widgets()
        
        # Try to locate save files
        self.locate_save_files()
        
        # Start monitoring if files found
        if self.autolevel_path and self.ai_rank_path:
            self.start_monitoring()
    
    def load_config(self):
        """Load configuration from file."""
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                self.save_folder_path = config.get('save_folder_path', '')
        except FileNotFoundError:
            self.save_folder_path = ''
    
    def save_config(self):
        """Save configuration to file."""
        config = {'save_folder_path': self.save_folder_path}
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)
    
    def setup_styles(self):
        """Configure ttk styles for dark theme."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure Treeview
        style.configure('Treeview', 
                       background=DARK_THEME['treeview_bg'],
                       foreground=DARK_THEME['treeview_fg'],
                       fieldbackground=DARK_THEME['treeview_bg'],
                       borderwidth=0)
        style.configure('Treeview.Heading',
                       background=DARK_THEME['button_bg'],
                       foreground=DARK_THEME['button_fg'],
                       relief='flat')
        style.map('Treeview',
                 background=[('selected', DARK_THEME['treeview_select'])])
        
        # Configure other widgets
        style.configure('TButton',
                       background=DARK_THEME['button_bg'],
                       foreground=DARK_THEME['button_fg'],
                       borderwidth=1,
                       relief='flat')
        style.map('TButton',
                 background=[('active', DARK_THEME['select_bg'])])
        
        style.configure('TLabel',
                       background=DARK_THEME['bg'],
                       foreground=DARK_THEME['fg'])
        
        style.configure('TFrame',
                       background=DARK_THEME['frame_bg'])
    
    def create_widgets(self):
        """Create the GUI widgets."""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Control panel
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill='x', pady=(0, 10))
        
        # File selection
        file_frame = ttk.Frame(control_frame)
        file_frame.pack(side='left', fill='x', expand=True)
        
        ttk.Button(file_frame, text="Select Save Folder", 
                  command=self.select_save_folder).pack(side='left', padx=(0, 5))
        
        self.folder_label = ttk.Label(file_frame, text="No folder selected")
        self.folder_label.pack(side='left', padx=(5, 0))
        
        # Control buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(side='right')
        
        self.monitor_button = ttk.Button(button_frame, text="Start Monitoring",
                                        command=self.toggle_monitoring)
        self.monitor_button.pack(side='left', padx=(0, 5))
        
        ttk.Button(button_frame, text="Refresh Now",
                  command=self.manual_refresh).pack(side='left', padx=(0, 5))
        
        ttk.Button(button_frame, text="Export Results",
                  command=self.export_results).pack(side='left')
        
        # Status bar
        self.status_label = ttk.Label(main_frame, text="Ready")
        self.status_label.pack(fill='x', pady=(0, 5))
        
        # Search frame
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(search_frame, text="Search:").pack(side='left')
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_characters)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side='left', padx=(5, 10))
        
        # Filter by tier
        ttk.Label(search_frame, text="Filter by Tier:").pack(side='left')
        self.tier_filter_var = tk.StringVar(value="All")
        tier_combo = ttk.Combobox(search_frame, textvariable=self.tier_filter_var,
                                 values=["All"] + list(TIERS.keys()), width=10)
        tier_combo.pack(side='left', padx=(5, 0))
        tier_combo.bind('<<ComboboxSelected>>', self.filter_characters)
        
        # Statistics frame
        stats_frame = ttk.Frame(main_frame)
        stats_frame.pack(fill='x', pady=(0, 10))
        
        self.stats_label = ttk.Label(stats_frame, text="Characters: 0")
        self.stats_label.pack(side='left')
        
        # Treeview for character rankings
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill='both', expand=True)
        
        # Treeview with scrollbars
        self.tree = ttk.Treeview(tree_frame, columns=('Tier', 'Score', 'AI Rank'), show='tree headings')
        
        # Configure columns
        self.tree.heading('#0', text='Character')
        self.tree.heading('Tier', text='Tier')
        self.tree.heading('Score', text='Score')
        self.tree.heading('AI Rank', text='AI Rank')
        
        self.tree.column('#0', width=300)
        self.tree.column('Tier', width=80)
        self.tree.column('Score', width=100)
        self.tree.column('AI Rank', width=100)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal', command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.tree.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        
        # Bind double-click event
        self.tree.bind('<Double-1>', self.on_character_double_click)
    
    def select_save_folder(self):
        """Open file dialog to select save folder."""
        folder = filedialog.askdirectory(title="Select Save Folder")
        if folder:
            self.save_folder_path = folder
            self.save_config()
            self.locate_save_files()
    
    def locate_save_files(self):
        """Locate save files in the selected folder."""
        if self.save_folder_path:
            save_folder = Path(self.save_folder_path)
        else:
            # Try to locate relative to script
            script_path = Path(__file__).resolve()
            game_folder = script_path.parent
            save_folder = game_folder / SAVE_FOLDER_NAME
        
        autolevel_path = save_folder / AUTOLEVEL_FILENAME
        ai_rank_path = save_folder / AI_RANK_FILENAME
        
        if save_folder.exists() and autolevel_path.exists() and ai_rank_path.exists():
            self.autolevel_path = autolevel_path
            self.ai_rank_path = ai_rank_path
            self.folder_label.config(text=f"Folder: {save_folder}")
            self.status_label.config(text="Save files located successfully")
            return True
        else:
            self.autolevel_path = None
            self.ai_rank_path = None
            self.folder_label.config(text="Save files not found")
            self.status_label.config(text="Please select the save folder")
            return False
    
    def toggle_monitoring(self):
        """Toggle file monitoring on/off."""
        if not self.monitoring:
            self.start_monitoring()
        else:
            self.stop_monitoring()
    
    def start_monitoring(self):
        """Start monitoring files for changes."""
        if not self.autolevel_path or not self.ai_rank_path:
            messagebox.showerror("Error", "Please locate save files first")
            return
        
        self.monitoring = True
        self.monitor_button.config(text="Stop Monitoring")
        self.status_label.config(text="Monitoring for file changes...")
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self.monitor_files, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop monitoring files."""
        self.monitoring = False
        self.monitor_button.config(text="Start Monitoring")
        self.status_label.config(text="Monitoring stopped")
    
    def monitor_files(self):
        """Monitor files for changes in a separate thread."""
        while self.monitoring:
            try:
                mod_autolevel = os.path.getmtime(self.autolevel_path)
                mod_ai_rank = os.path.getmtime(self.ai_rank_path)
                
                if (mod_autolevel != self.last_mod_autolevel or 
                    mod_ai_rank != self.last_mod_ai_rank):
                    
                    self.last_mod_autolevel = mod_autolevel
                    self.last_mod_ai_rank = mod_ai_rank
                    
                    # Update data in main thread
                    self.root.after(0, self.update_data)
                
                time.sleep(CHECK_INTERVAL)
                
            except Exception as e:
                self.root.after(0, lambda: self.status_label.config(
                    text=f"Error monitoring files: {str(e)}"))
                break
    
    def manual_refresh(self):
        """Manually refresh the data."""
        if not self.autolevel_path or not self.ai_rank_path:
            messagebox.showerror("Error", "Please locate save files first")
            return
        
        self.update_data()
    
    def update_data(self):
        """Update character data and refresh display."""
        try:
            characters = self.parse_autolevel(self.autolevel_path)
            ai_ranks = self.parse_ai_rank(self.ai_rank_path)
            
            if characters is not None and ai_ranks is not None:
                self.characters = characters
                self.ai_ranks = ai_ranks
                self.ranked_characters = self.calculate_ranks(characters, ai_ranks)
                self.update_display()
                self.status_label.config(text=f"Updated: {datetime.now().strftime('%H:%M:%S')}")
            else:
                self.status_label.config(text="Error reading save files")
                
        except Exception as e:
            self.status_label.config(text=f"Error updating data: {str(e)}")
    
    def parse_autolevel(self, file_path):
        """Parse the autolevel.save file."""
        characters = {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) == 2:
                        char_path = parts[0].strip()
                        try:
                            score = sum(map(int, parts[1].strip().split()))
                            characters[char_path] = {
                                'score': score,
                                'name': os.path.splitext(os.path.basename(char_path))[0]
                            }
                        except (ValueError, IndexError):
                            continue
        except FileNotFoundError:
            return None
        return characters
    
    def parse_ai_rank(self, file_path):
        """Parse the AI_Rank.save file."""
        ai_ranks = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines[1:]:  # Skip header
                    char_path = line.strip()
                    if char_path:
                        ai_ranks.append(char_path)
        except FileNotFoundError:
            return None
        return ai_ranks
    
    def calculate_ranks(self, characters, ai_ranks):
        """Calculate final scores and assign tiers."""
        if not characters:
            return []
        
        ranked_characters = []
        num_ranked = len(ai_ranks)
        
        for char_path, data in characters.items():
            final_score = data['score']
            ai_rank_pos = None
            
            if ai_ranks and char_path in ai_ranks:
                ai_rank_pos = ai_ranks.index(char_path) + 1
                rank_bonus = (num_ranked - ai_rank_pos + 1) * 0.5
                final_score += rank_bonus
            
            # Assign tier
            tier = "F"
            for t, (min_s, max_s) in TIERS.items():
                if min_s <= final_score <= max_s:
                    tier = t
                    break
            
            ranked_characters.append({
                'name': data['name'],
                'score': final_score,
                'tier': tier,
                'ai_rank': ai_rank_pos
            })
        
        ranked_characters.sort(key=lambda x: x['score'], reverse=True)
        return ranked_characters
    
    def update_display(self):
        """Update the treeview display."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add characters grouped by tier
        for tier in TIERS:
            tier_characters = [char for char in self.ranked_characters if char['tier'] == tier]
            
            if tier_characters:
                # Add tier header
                tier_item = self.tree.insert('', 'end', text=f"{tier} Tier ({len(tier_characters)})",
                                           values=('', '', ''), tags=(f'tier_{tier}',))
                
                # Configure tier color
                self.tree.tag_configure(f'tier_{tier}', background=TIER_COLORS[tier],
                                       foreground='#000000')
                
                # Add characters under tier
                for char in tier_characters:
                    ai_rank_text = str(char['ai_rank']) if char['ai_rank'] else "N/A"
                    self.tree.insert(tier_item, 'end', text=char['name'],
                                   values=(char['tier'], f"{char['score']:.2f}", ai_rank_text),
                                   tags=(f'char_{tier}',))
                
                # Configure character color (lighter version of tier color)
                char_color = self.lighten_color(TIER_COLORS[tier], 0.3)
                self.tree.tag_configure(f'char_{tier}', background=char_color,
                                       foreground='#000000')
                
                # Expand tier by default
                self.tree.item(tier_item, open=True)
        
        # Update statistics
        self.update_statistics()
        
        # Apply current filter
        self.filter_characters()
    
    def lighten_color(self, color, factor):
        """Lighten a hex color by a factor."""
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        rgb = tuple(min(255, int(c + (255 - c) * factor)) for c in rgb)
        return '#{:02x}{:02x}{:02x}'.format(*rgb)
    
    def update_statistics(self):
        """Update the statistics display."""
        total_chars = len(self.ranked_characters)
        tier_counts = {}
        
        for char in self.ranked_characters:
            tier = char['tier']
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
        
        stats_text = f"Total Characters: {total_chars}"
        if tier_counts:
            tier_text = " | ".join([f"{tier}: {count}" for tier, count in tier_counts.items()])
            stats_text += f" | {tier_text}"
        
        self.stats_label.config(text=stats_text)
    
    def filter_characters(self, *args):
        """Filter characters based on search and tier filter."""
        search_term = self.search_var.get().lower()
        tier_filter = self.tier_filter_var.get()
        
        # Show/hide items based on filters
        for item in self.tree.get_children():
            self.filter_item(item, search_term, tier_filter)
    
    def filter_item(self, item, search_term, tier_filter):
        """Filter a single item and its children."""
        item_text = self.tree.item(item, 'text').lower()
        item_values = self.tree.item(item, 'values')
        
        # Check if item matches filters
        matches_search = not search_term or search_term in item_text
        matches_tier = tier_filter == "All" or (item_values and item_values[0] == tier_filter)
        
        # For tier headers, check if any children match
        children = self.tree.get_children(item)
        if children:
            visible_children = 0
            for child in children:
                if self.filter_item(child, search_term, tier_filter):
                    visible_children += 1
            
            # Show tier header if it has visible children
            if visible_children > 0:
                self.tree.item(item, open=True)
                return True
            else:
                self.tree.detach(item)
                return False
        else:
            # For character items
            if matches_search and matches_tier:
                return True
            else:
                self.tree.detach(item)
                return False
    
    def on_character_double_click(self, event):
        """Handle double-click on character."""
        item = self.tree.selection()[0]
        if item:
            char_name = self.tree.item(item, 'text')
            values = self.tree.item(item, 'values')
            if values and values[0]:  # Has tier info (is a character, not tier header)
                messagebox.showinfo("Character Details", 
                                  f"Character: {char_name}\n"
                                  f"Tier: {values[0]}\n"
                                  f"Score: {values[1]}\n"
                                  f"AI Rank: {values[2]}")
    
    def export_results(self):
        """Export results to a file."""
        if not self.ranked_characters:
            messagebox.showwarning("Warning", "No data to export")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("Character Rankings Export\n")
                    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    
                    for tier in TIERS:
                        tier_chars = [char for char in self.ranked_characters if char['tier'] == tier]
                        if tier_chars:
                            f.write(f"--- {tier} Tier ---\n")
                            for char in tier_chars:
                                ai_rank = char['ai_rank'] if char['ai_rank'] else "N/A"
                                f.write(f"{char['name']} (Score: {char['score']:.2f}, AI Rank: {ai_rank})\n")
                            f.write("\n")
                
                messagebox.showinfo("Success", f"Results exported to {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {str(e)}")

def main():
    """Main function to run the GUI application."""
    root = tk.Tk()
    app = CharacterRankerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()