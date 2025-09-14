import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import subprocess
import sys
from pathlib import Path
import shutil
from tkinter import font

class AppLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 Mijn App Launcher")
        self.root.geometry("800x600")
        self.root.configure(bg='#2c3e50')
        
        # Data opslag
        self.data_file = "launcher_apps.json"
        self.apps = self.load_apps()
        
        # Setup UI
        self.setup_styles()
        self.create_widgets()
        self.refresh_apps_display()
        
        # Drag and drop setup
        self.setup_drag_drop()
        
    def setup_styles(self):
        """Setup custom styles voor de interface"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure styles
        self.style.configure('Title.TLabel', 
                           background='#2c3e50', 
                           foreground='white', 
                           font=('Segoe UI', 20, 'bold'))
        
        self.style.configure('Subtitle.TLabel',
                           background='#2c3e50',
                           foreground='#ecf0f1',
                           font=('Segoe UI', 10))
        
        self.style.configure('App.TFrame',
                           background='#34495e',
                           relief='raised',
                           borderwidth=2)
        
        self.style.configure('AppName.TLabel',
                           background='#34495e',
                           foreground='white',
                           font=('Segoe UI', 12, 'bold'))
        
        self.style.configure('AppPath.TLabel',
                           background='#34495e',
                           foreground='#bdc3c7',
                           font=('Segoe UI', 8))
    
    def create_widgets(self):
        """Maak alle UI widgets"""
        # Header
        header_frame = tk.Frame(self.root, bg='#2c3e50', pady=20)
        header_frame.pack(fill='x')
        
        title_label = ttk.Label(header_frame, text="🚀 Mijn App Launcher", style='Title.TLabel')
        title_label.pack()
        
        subtitle_label = ttk.Label(header_frame, text="Sleep apps hiernaartoe of klik 'App Toevoegen'", style='Subtitle.TLabel')
        subtitle_label.pack(pady=(5, 0))
        
        # Drop zone
        self.drop_frame = tk.Frame(self.root, bg='#3498db', height=100, relief='dashed', bd=3)
        self.drop_frame.pack(fill='x', padx=20, pady=10)
        self.drop_frame.pack_propagate(False)
        
        drop_label = tk.Label(self.drop_frame, text="📁 SLEEP BESTANDEN HIER NAARTOE 📁", 
                             bg='#3498db', fg='white', font=('Segoe UI', 14, 'bold'))
        drop_label.pack(expand=True)
        
        # Control buttons
        controls_frame = tk.Frame(self.root, bg='#2c3e50')
        controls_frame.pack(fill='x', padx=20, pady=10)
        
        btn_add = tk.Button(controls_frame, text="📂 App Toevoegen", 
                           command=self.add_app_dialog,
                           bg='#27ae60', fg='white', font=('Segoe UI', 10, 'bold'),
                           padx=20, pady=5, relief='flat')
        btn_add.pack(side='left', padx=(0, 10))
        
        btn_export = tk.Button(controls_frame, text="💾 Exporteer", 
                              command=self.export_apps,
                              bg='#f39c12', fg='white', font=('Segoe UI', 10, 'bold'),
                              padx=20, pady=5, relief='flat')
        btn_export.pack(side='left', padx=(0, 10))
        
        btn_import = tk.Button(controls_frame, text="📥 Importeer", 
                              command=self.import_apps,
                              bg='#9b59b6', fg='white', font=('Segoe UI', 10, 'bold'),
                              padx=20, pady=5, relief='flat')
        btn_import.pack(side='left', padx=(0, 10))
        
        btn_clear = tk.Button(controls_frame, text="🗑️ Alles Wissen", 
                             command=self.clear_all,
                             bg='#e74c3c', fg='white', font=('Segoe UI', 10, 'bold'),
                             padx=20, pady=5, relief='flat')
        btn_clear.pack(side='right')
        
        # Apps display area
        self.setup_apps_area()
    
    def setup_apps_area(self):
        """Setup het gebied waar apps worden weergegeven"""
        # Frame voor scrollable area
        self.canvas_frame = tk.Frame(self.root, bg='#2c3e50')
        self.canvas_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Canvas en scrollbar
        self.canvas = tk.Canvas(self.canvas_frame, bg='#2c3e50', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='#2c3e50')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to canvas
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def setup_drag_drop(self):
        """Setup drag and drop functionality"""
        # Enable drop on the drop frame
        self.drop_frame.drop_target_register('DND_Files')
        self.drop_frame.dnd_bind('<<Drop>>', self.handle_drop)
        
        # Bind drop events
        self.root.bind('<Button-1>', self.on_click)
        self.setup_file_drop()
    
    def setup_file_drop(self):
        """Setup file drop handling (simplified approach)"""
        # Note: Voor echte drag-and-drop zou je tkinterdnd2 package nodig hebben
        # Dit is een vereenvoudigde versie
        pass
    
    def on_click(self, event):
        """Handle click events"""
        pass
    
    def handle_drop(self, event):
        """Handle dropped files"""
        # Dit zou met tkinterdnd2 package werken
        pass
    
    def add_app_dialog(self):
        """Open file dialog om app toe te voegen"""
        file_types = [
            ("Alle bestanden", "*.*"),
            ("Executables", "*.exe"),
            ("Batch files", "*.bat"),
            ("HTML files", "*.html"),
            ("Python files", "*.py")
        ]
        
        files = filedialog.askopenfilenames(
            title="Selecteer apps om toe te voegen",
            filetypes=file_types
        )
        
        for file_path in files:
            self.add_app(file_path)
    
    def add_app(self, file_path):
        """Voeg een app toe aan de collectie"""
        if not os.path.exists(file_path):
            messagebox.showerror("Fout", f"Bestand bestaat niet: {file_path}")
            return
        
        # Check if app already exists
        if any(app['path'] == file_path for app in self.apps):
            messagebox.showinfo("Info", "Deze app bestaat al in je collectie!")
            return
        
        # Get app info
        app_name = os.path.splitext(os.path.basename(file_path))[0]
        
        app_info = {
            'name': app_name,
            'path': file_path,
            'added_date': str(Path(file_path).stat().st_mtime)
        }
        
        self.apps.append(app_info)
        self.save_apps()
        self.refresh_apps_display()
        
        messagebox.showinfo("Succes", f"'{app_name}' toegevoegd!")
    
    def launch_app(self, app_path):
        """Start een app"""
        try:
            if not os.path.exists(app_path):
                messagebox.showerror("Fout", f"Bestand niet gevonden: {app_path}")
                return
            
            # Different launch methods based on file type
            if app_path.lower().endswith('.html'):
                # Open HTML files in default browser
                os.startfile(app_path)
            elif app_path.lower().endswith(('.exe', '.bat', '.cmd')):
                # Run executables and batch files
                subprocess.Popen([app_path], shell=True)
            elif app_path.lower().endswith('.py'):
                # Run Python files
                subprocess.Popen([sys.executable, app_path])
            else:
                # Try to open with default application
                os.startfile(app_path)
                
        except Exception as e:
            messagebox.showerror("Fout", f"Kon app niet starten: {str(e)}")
    
    def remove_app(self, app_index):
        """Verwijder een app uit de collectie"""
        if 0 <= app_index < len(self.apps):
            app_name = self.apps[app_index]['name']
            result = messagebox.askyesno("Bevestigen", 
                                       f"Weet je zeker dat je '{app_name}' wilt verwijderen?")
            if result:
                self.apps.pop(app_index)
                self.save_apps()
                self.refresh_apps_display()
                messagebox.showinfo("Succes", f"'{app_name}' verwijderd!")
    
    def refresh_apps_display(self):
        """Ververs de weergave van apps"""
        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        if not self.apps:
            # Show empty state
            empty_label = tk.Label(self.scrollable_frame, 
                                 text="🎯 Geen apps toegevoegd\n\nKlik 'App Toevoegen' om te beginnen!",
                                 bg='#2c3e50', fg='#95a5a6', 
                                 font=('Segoe UI', 14), pady=50)
            empty_label.pack(expand=True, fill='both')
            return
        
        # Create app tiles in a grid
        apps_per_row = 3
        current_row_frame = None
        
        for i, app in enumerate(self.apps):
            if i % apps_per_row == 0:
                current_row_frame = tk.Frame(self.scrollable_frame, bg='#2c3e50')
                current_row_frame.pack(fill='x', pady=5)
            
            app_frame = tk.Frame(current_row_frame, bg='#34495e', relief='raised', bd=2)
            app_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)
            
            # App icon (emoji based on file type)
            icon = self.get_app_icon(app['path'])
            icon_label = tk.Label(app_frame, text=icon, bg='#34495e', 
                                font=('Segoe UI', 24), pady=10)
            icon_label.pack()
            
            # App name
            name_label = tk.Label(app_frame, text=app['name'], bg='#34495e', 
                                fg='white', font=('Segoe UI', 11, 'bold'),
                                wraplength=150)
            name_label.pack(pady=(0, 5))
            
            # App path (shortened)
            short_path = "..." + app['path'][-30:] if len(app['path']) > 33 else app['path']
            path_label = tk.Label(app_frame, text=short_path, bg='#34495e', 
                                fg='#bdc3c7', font=('Segoe UI', 8),
                                wraplength=150)
            path_label.pack(pady=(0, 10))
            
            # Buttons frame
            btn_frame = tk.Frame(app_frame, bg='#34495e')
            btn_frame.pack(pady=(0, 10))
            
            # Launch button
            launch_btn = tk.Button(btn_frame, text="🚀 Start", 
                                 command=lambda path=app['path']: self.launch_app(path),
                                 bg='#27ae60', fg='white', font=('Segoe UI', 9, 'bold'),
                                 padx=10, relief='flat')
            launch_btn.pack(side='left', padx=(0, 5))
            
            # Remove button
            remove_btn = tk.Button(btn_frame, text="🗑️", 
                                 command=lambda idx=i: self.remove_app(idx),
                                 bg='#e74c3c', fg='white', font=('Segoe UI', 9, 'bold'),
                                 width=3, relief='flat')
            remove_btn.pack(side='left')
    
    def get_app_icon(self, file_path):
        """Bepaal icoon gebaseerd op bestandstype"""
        ext = os.path.splitext(file_path)[1].lower()
        icons = {
            '.exe': '⚙️',
            '.bat': '📝',
            '.cmd': '📝',
            '.html': '🌐',
            '.py': '🐍',
            '.js': '📜',
            '.txt': '📄',
            '.pdf': '📕',
            '.jpg': '🖼️',
            '.jpeg': '🖼️',
            '.png': '🖼️',
            '.gif': '🖼️',
            '.mp3': '🎵',
            '.mp4': '🎬',
            '.zip': '📦',
            '.rar': '📦'
        }
        return icons.get(ext, '📄')
    
    def load_apps(self):
        """Laad apps uit JSON bestand"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                messagebox.showerror("Fout", f"Kon apps niet laden: {str(e)}")
                return []
        return []
    
    def save_apps(self):
        """Sla apps op naar JSON bestand"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.apps, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Fout", f"Kon apps niet opslaan: {str(e)}")
    
    def export_apps(self):
        """Exporteer apps naar JSON bestand"""
        if not self.apps:
            messagebox.showinfo("Info", "Geen apps om te exporteren!")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Apps exporteren naar...",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("Alle bestanden", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.apps, f, indent=2, ensure_ascii=False)
                messagebox.showinfo("Succes", f"Apps geëxporteerd naar: {file_path}")
            except Exception as e:
                messagebox.showerror("Fout", f"Export mislukt: {str(e)}")
    
    def import_apps(self):
        """Importeer apps van JSON bestand"""
        file_path = filedialog.askopenfilename(
            title="Apps importeren van...",
            filetypes=[("JSON files", "*.json"), ("Alle bestanden", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    imported_apps = json.load(f)
                
                # Filter out duplicates
                new_apps = []
                for imported_app in imported_apps:
                    if not any(app['path'] == imported_app['path'] for app in self.apps):
                        new_apps.append(imported_app)
                
                self.apps.extend(new_apps)
                self.save_apps()
                self.refresh_apps_display()
                
                messagebox.showinfo("Succes", 
                                  f"{len(new_apps)} nieuwe apps geïmporteerd!\n"
                                  f"({len(imported_apps) - len(new_apps)} duplicaten genegeerd)")
            except Exception as e:
                messagebox.showerror("Fout", f"Import mislukt: {str(e)}")
    
    def clear_all(self):
        """Verwijder alle apps"""
        if not self.apps:
            messagebox.showinfo("Info", "Geen apps om te wissen!")
            return
        
        result = messagebox.askyesno("Bevestigen", 
                                   f"Weet je zeker dat je alle {len(self.apps)} apps wilt verwijderen?")
        if result:
            self.apps = []
            self.save_apps()
            self.refresh_apps_display()
            messagebox.showinfo("Succes", "Alle apps verwijderd!")

def main():
    """Main functie om de applicatie te starten"""
    root = tk.Tk()
    app = AppLauncher(root)
    
    # Set window icon (if available)
    try:
        root.iconbitmap('icon.ico')
    except:
        pass
    
    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":
    main()