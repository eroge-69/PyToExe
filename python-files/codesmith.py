import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import os
import subprocess
import threading
import re
import time

# Language definitions
LANGUAGES = {
    "python": {
        "extensions": [".py", ".pyw"],
        "keywords": [
            'def', 'return', 'if', 'else', 'elif', 'for', 'while', 'import', 'from', 'class',
            'try', 'except', 'with', 'as', 'pass', 'break', 'continue', 'in', 'and', 'or', 'not',
            'is', 'lambda', 'print', 'True', 'False', 'None', 'async', 'await', 'yield', 'global',
            'nonlocal', 'assert', 'del', 'raise', 'finally'
        ],
        "run_command": ["python"],
        "comment": "#"
    },
    "javascript": {
        "extensions": [".js", ".jsx", ".mjs"],
        "keywords": [
            'var', 'let', 'const', 'function', 'return', 'if', 'else', 'for', 'while', 'do',
            'switch', 'case', 'default', 'break', 'continue', 'try', 'catch', 'finally', 'throw',
            'class', 'extends', 'import', 'export', 'from', 'async', 'await', 'true', 'false',
            'null', 'undefined', 'new', 'this', 'super', 'typeof', 'instanceof', 'delete'
        ],
        "run_command": ["node"],
        "comment": "//"
    },
    "java": {
        "extensions": [".java"],
        "keywords": [
            'public', 'private', 'protected', 'static', 'final', 'class', 'interface', 'extends',
            'implements', 'import', 'package', 'void', 'int', 'double', 'float', 'long', 'short',
            'byte', 'char', 'boolean', 'String', 'if', 'else', 'for', 'while', 'do', 'switch',
            'case', 'default', 'break', 'continue', 'return', 'try', 'catch', 'finally', 'throw',
            'throws', 'new', 'this', 'super', 'abstract', 'synchronized', 'volatile', 'transient'
        ],
        "run_command": ["java"],
        "comment": "//"
    },
    "cpp": {
        "extensions": [".cpp", ".cc", ".cxx", ".c", ".h", ".hpp"],
        "keywords": [
            'int', 'float', 'double', 'char', 'bool', 'void', 'auto', 'const', 'static', 'extern',
            'register', 'volatile', 'inline', 'virtual', 'public', 'private', 'protected', 'class',
            'struct', 'union', 'enum', 'typedef', 'namespace', 'using', 'template', 'typename',
            'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'default', 'break', 'continue',
            'return', 'try', 'catch', 'throw', 'new', 'delete', 'this', 'nullptr', 'true', 'false'
        ],
        "run_command": ["g++", "-o", "temp_exe"],
        "comment": "//"
    },
    "html": {
        "extensions": [".html", ".htm", ".xhtml"],
        "keywords": [
            'html', 'head', 'title', 'body', 'div', 'span', 'p', 'a', 'img', 'ul', 'ol', 'li',
            'table', 'tr', 'td', 'th', 'form', 'input', 'button', 'select', 'option', 'textarea',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'br', 'hr', 'meta', 'link', 'script', 'style'
        ],
        "run_command": None,  # HTML doesn't run directly
        "comment": "<!--"
    },
    "css": {
        "extensions": [".css"],
        "keywords": [
            'color', 'background', 'font', 'margin', 'padding', 'border', 'width', 'height',
            'display', 'position', 'float', 'clear', 'text-align', 'font-size', 'font-weight',
            'font-family', 'line-height', 'text-decoration', 'list-style', 'overflow', 'z-index',
            'opacity', 'visibility', 'cursor', 'transform', 'transition', 'animation'
        ],
        "run_command": None,
        "comment": "/*"
    },
    "json": {
        "extensions": [".json"],
        "keywords": ['true', 'false', 'null'],
        "run_command": None,
        "comment": None
    },
    "xml": {
        "extensions": [".xml"],
        "keywords": [],
        "run_command": None,
        "comment": "<!--"
    },
    "markdown": {
        "extensions": [".md", ".markdown"],
        "keywords": [],
        "run_command": None,
        "comment": None
    }
}

# Get all supported extensions
ALL_EXTENSIONS = []
for lang_data in LANGUAGES.values():
    ALL_EXTENSIONS.extend(lang_data["extensions"])

# Discord Application ID for Codesmith IDE
DISCORD_CLIENT_ID = "1234567890123456789"  # You'd need to register your own app

class DiscordManager:
    """Handles Discord Rich Presence integration."""
    
    def __init__(self):
        self.enabled = False
        self.rpc = None
        self.start_time = time.time()
        self.current_file = None
        self.current_language = None
        self.connected = False

    def disconnect(self):
        """Disconnect from Discord Rich Presence."""
        if self.rpc and self.connected:
            try:
                self.rpc.close()
            except:
                pass
        self.connected = False
        self.enabled = False
        self.rpc = None
    
    def update_presence(self, details, state=None, large_image=None, small_image=None):
        """Update Discord presence."""
        if not self.enabled or not self.rpc or not self.connected:
            return
            
        try:
            self.rpc.update(
                details=details,
                state=state,
                start=self.start_time,
                large_image=large_image or "codesmith_logo",
                large_text="Codesmith IDE",
                small_image=small_image,
                small_text=state
            )
        except Exception as e:
            print(f"Failed to update Discord presence: {e}")
    
    def update_file_status(self, filename, language, line_count=None):
        """Update presence when working on a file."""
        if not self.enabled:
            return
            
        self.current_file = filename
        self.current_language = language
        
        if filename:
            details = f"Editing {filename}"
            if line_count:
                state = f"{language.upper()} • {line_count} lines"
            else:
                state = f"Working on {language.upper()} code"
            
            # Map languages to icons
            language_icons = {
                "python": "python_icon",
                "javascript": "js_icon", 
                "java": "java_icon",
                "cpp": "cpp_icon",
                "html": "html_icon",
                "css": "css_icon"
            }
            
            small_image = language_icons.get(language, "code_icon")
            self.update_presence(details, state, small_image=small_image)
        else:
            self.update_presence("In Codesmith IDE", "Idle")
    
    def update_coding_session(self, files_open=0, language=None):
        """Update presence with coding session info."""
        if not self.enabled:
            return
            
        if files_open > 1:
            details = f"Working on {files_open} files"
        elif files_open == 1:
            details = "Deep in the code"
        else:
            details = "In Codesmith IDE"
            
        if language:
            state = f"Coding in {language.upper()}"
        else:
            state = "Multi-language development"
            
        self.update_presence(details, state)
    
    def update_terminal_status(self):
        """Update presence when using terminal."""
        if not self.enabled:
            return
        self.update_presence("Using integrated terminal", "Running commands")

THEMES = {
    "Black": {
        "bg": "#121212", "fg": "#eeeeee", "keyword": "#ff79c6",
        "terminal_bg": "#1e1e1e", "terminal_fg": "#ffffff",
        "sidebar_bg": "#222222", "sidebar_fg": "#eeeeee",
        "autocomplete_bg": "#333333", "autocomplete_fg": "#eeeeee"
    },
    "White": {
        "bg": "#ffffff", "fg": "#000000", "keyword": "#0000ff",
        "terminal_bg": "#f0f0f0", "terminal_fg": "#000000",
        "sidebar_bg": "#e0e0e0", "sidebar_fg": "#000000",
        "autocomplete_bg": "#dddddd", "autocomplete_fg": "#000000"
    },
    "Ironman": {
        "bg": "#3e0000", "fg": "#ffcc00", "keyword": "#ff4444",
        "terminal_bg": "#4a0000", "terminal_fg": "#ffcc00",
        "sidebar_bg": "#4a0000", "sidebar_fg": "#ffcc00",
        "autocomplete_bg": "#660000", "autocomplete_fg": "#ffcc00"
    }
}

THEMES.update({
    # 1. Safe Shallows (Subnautica)
    "Safe Shallows": {
        "bg": "#3a7ca5",
        "fg": "#d9f0f7",
        "keyword": "#f2c14e",
        "terminal_bg": "#27496d",
        "terminal_fg": "#d9f0f7",
        "sidebar_bg": "#2a628f",
        "sidebar_fg": "#d9f0f7",
        "autocomplete_bg": "#367db9",
        "autocomplete_fg": "#d9f0f7"
    },
    # 2. Doctor Doom (green & dark metal)
    "Doctor Doom": {
        "bg": "#1e2d1e",
        "fg": "#a4c639",
        "keyword": "#7bb661",
        "terminal_bg": "#121a12",
        "terminal_fg": "#a4c639",
        "sidebar_bg": "#2a3a2a",
        "sidebar_fg": "#a4c639",
        "autocomplete_bg": "#3b503b",
        "autocomplete_fg": "#a4c639"
    },
    # 3. Jellyshroom Caves (Subnautica)
    "Jellyshroom Caves": {
        "bg": "#6a5181",
        "fg": "#e0d5f5",
        "keyword": "#f78fb3",
        "terminal_bg": "#4b3a63",
        "terminal_fg": "#e0d5f5",
        "sidebar_bg": "#5a4574",
        "sidebar_fg": "#e0d5f5",
        "autocomplete_bg": "#694d7d",
        "autocomplete_fg": "#e0d5f5"
    },
    # 4. Kelp Forest (Subnautica)
    "Kelp Forest": {
        "bg": "#2f5d50",
        "fg": "#b0e3c7",
        "keyword": "#f9d56e",
        "terminal_bg": "#1f433a",
        "terminal_fg": "#b0e3c7",
        "sidebar_bg": "#234b42",
        "sidebar_fg": "#b0e3c7",
        "autocomplete_bg": "#316252",
        "autocomplete_fg": "#b0e3c7"
    },
    # 5. Alterra (Subnautica)
    "Alterra": {
        "bg": "#0b3c5d",
        "fg": "#f7b32b",
        "keyword": "#ffffff",
        "terminal_bg": "#10375c",
        "terminal_fg": "#f7b32b",
        "sidebar_bg": "#12466b",
        "sidebar_fg": "#f7b32b",
        "autocomplete_bg": "#145a8d",
        "autocomplete_fg": "#f7b32b"
    },

    # 6. Cyberpunk Neon
    "Cyberpunk Neon": {
        "bg": "#0d001f",
        "fg": "#39ff14",
        "keyword": "#ff2079",
        "terminal_bg": "#15002b",
        "terminal_fg": "#39ff14",
        "sidebar_bg": "#1a003f",
        "sidebar_fg": "#39ff14",
        "autocomplete_bg": "#29003f",
        "autocomplete_fg": "#39ff14"
    },
    # 7. Solarized Dark
    "Solarized Dark": {
        "bg": "#002b36",
        "fg": "#839496",
        "keyword": "#b58900",
        "terminal_bg": "#073642",
        "terminal_fg": "#839496",
        "sidebar_bg": "#073642",
        "sidebar_fg": "#839496",
        "autocomplete_bg": "#586e75",
        "autocomplete_fg": "#839496"
    },
    # 8. Sunset Glow
    "Sunset Glow": {
        "bg": "#ff5e62",
        "fg": "#fff5f0",
        "keyword": "#ffc371",
        "terminal_bg": "#d94e4f",
        "terminal_fg": "#fff5f0",
        "sidebar_bg": "#e04f4f",
        "sidebar_fg": "#fff5f0",
        "autocomplete_bg": "#f4684d",
        "autocomplete_fg": "#fff5f0"
    },
    # 9. Midnight Blue
    "Midnight Blue": {
        "bg": "#191970",
        "fg": "#e0e0ff",
        "keyword": "#ff7f50",
        "terminal_bg": "#121152",
        "terminal_fg": "#e0e0ff",
        "sidebar_bg": "#1c1c7a",
        "sidebar_fg": "#e0e0ff",
        "autocomplete_bg": "#202062",
        "autocomplete_fg": "#e0e0ff"
    },
    # 10. Retro Arcade
    "Retro Arcade": {
        "bg": "#000000",
        "fg": "#00ffea",
        "keyword": "#ff0055",
        "terminal_bg": "#111111",
        "terminal_fg": "#00ffea",
        "sidebar_bg": "#111111",
        "sidebar_fg": "#00ffea",
        "autocomplete_bg": "#003344",
        "autocomplete_fg": "#00ffea"
    }
})




class ClosableNotebook(ttk.Notebook):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bind("<Button-1>", self.on_click)

    def on_click(self, event):
        x, y = event.x, event.y
        elem = self.identify(event.x, event.y)
        if "close" in elem:
            index = self.index(f"@{x},{y}")
            self.forget(index)
            self.event_generate("<<NotebookTabClosed>>")

    def add(self, child, **kw):
        text = kw.get("text", "")
        kw["text"] = text + "  \u2716"
        super().add(child, **kw)

class CodeSmith(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Codesmith - Multi-Language IDE with Terminal")
        self.geometry("1200x700")
        self.theme = "Black"
        self.configure(bg=THEMES[self.theme]["bg"])
        self.open_files = {}
        self.autocomplete_popup = None

        self.create_widgets()
        self.apply_theme()
    
    def detect_language(self, filepath):
        """Detect the programming language based on file extension."""
        if not filepath:
            return "python"  # Default
        
        _, ext = os.path.splitext(filepath)
        ext = ext.lower()
        
        for lang_name, lang_data in LANGUAGES.items():
            if ext in lang_data["extensions"]:
                return lang_name
        return "text"  # Fallback for unknown extensions

    def suggest_projects(self):
        suggestions = [
            "To-Do List App (Python/JavaScript)",
            "Weather Dashboard (HTML/CSS/JS)",
            "Expense Tracker (Java/Python)",
            "Portfolio Website (HTML/CSS/JS)",
            "Simple Calculator (C++/Java)",
            "File Organizer (Python)",
            "REST API (Python/JavaScript)",
            "Pomodoro Timer (Any Language)",
            "Simple Game (C++/Python)",
            "Note-Taking App (JavaScript/Python)",
            "Data Structures Practice (C++/Java)",
            "Web Scraper (Python)"
        ]

        suggestion_window = tk.Toplevel(self)
        suggestion_window.title("Project Ideas")
        suggestion_window.geometry("300x250")

        label = tk.Label(suggestion_window, text="Here are some project ideas:", font=("Arial", 12))
        label.pack(pady=10)

        listbox = tk.Listbox(suggestion_window)
        for item in suggestions:
            listbox.insert(tk.END, item)
        listbox.pack(padx=10, pady=10, fill="both", expand=True)

        close_btn = tk.Button(suggestion_window, text="Close", command=suggestion_window.destroy)
        close_btn.pack(pady=5)

    def create_widgets(self):
        menubar = tk.Menu(self)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="New Tab", command=self.new_tab)
        filemenu.add_command(label="Open", command=self.open_file_dialog)
        filemenu.add_command(label="Save", command=self.save_file)
        filemenu.add_command(label="Save As", command=self.save_file_as)
        menubar.add_cascade(label="File", menu=filemenu)



        thememenu = tk.Menu(menubar, tearoff=0)
        for theme in THEMES.keys():
            thememenu.add_command(label=theme, command=lambda t=theme: self.change_theme(t))
        menubar.add_cascade(label="Themes", menu=thememenu)

        # Terminal Menu
        terminal_menu = tk.Menu(menubar, tearoff=0)
        terminal_menu.add_command(label="New Terminal", command=self.create_terminal_tab)
        terminal_menu.add_command(label="Clear Terminal", command=self.clear_current_terminal)
        terminal_menu.add_separator()
        terminal_menu.add_command(label="Show/Hide Terminal", command=self.toggle_terminal)
        menubar.add_cascade(label="Terminal", menu=terminal_menu)

        menubar.add_command(label="Run", command=self.run_code)
        menubar.add_command(label="Projects", command=self.suggest_projects)
        self.config(menu=menubar)
        
        # Add keyboard shortcuts
        self.bind_all("<Control-n>", lambda e: self.new_tab())
        self.bind_all("<Control-o>", lambda e: self.open_file_dialog())
        self.bind_all("<Control-s>", lambda e: self.save_file())
        self.bind_all("<Control-Shift-S>", lambda e: self.save_file_as())
        self.bind_all("<F5>", lambda e: self.run_code())
        self.bind_all("<Control-grave>", lambda e: self.toggle_terminal())  # Ctrl+` to toggle terminal
        self.bind_all("<Control-Shift-grave>", lambda e: self.create_terminal_tab())  # Ctrl+Shift+` for new terminal

        self.sidebar_frame = tk.Frame(self, width=250)
        self.sidebar_frame.pack(side="left", fill="y")

        self.main_frame = tk.Frame(self)
        self.main_frame.pack(side="right", fill="both", expand=True)

        self.tree = ttk.Treeview(self.sidebar_frame)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewOpen>>", self.on_tree_expand)
        self.tree.bind("<Double-1>", self.on_tree_select)

        self.root_path = os.path.expanduser("~")
        self.insert_node("", self.root_path)

        self.notebook = ClosableNotebook(self.main_frame)
        self.notebook.pack(fill="both", expand=True)
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        self.notebook.bind("<<NotebookTabClosed>>", self.on_tab_closed)

        # Create terminal notebook for multiple terminals
        self.terminal_notebook = ttk.Notebook(self.main_frame, height=250)
        self.terminal_notebook.pack(fill="x", side="bottom")
        
        # Create first terminal tab
        self.create_terminal_tab()

        self.new_tab()

    # Terminal Management
    def create_terminal_tab(self):
        """Create a new interactive terminal tab."""
        terminal_frame = tk.Frame(self.terminal_notebook)
        
        # Create terminal display
        terminal_display = scrolledtext.ScrolledText(
            terminal_frame,
            bg=THEMES[self.theme]["terminal_bg"],
            fg=THEMES[self.theme]["terminal_fg"],
            font=("Consolas", 10),
            state="disabled",
            wrap="word"
        )
        terminal_display.pack(fill="both", expand=True)
        
        # Create command input frame
        input_frame = tk.Frame(terminal_frame)
        input_frame.pack(fill="x", side="bottom")
        
        # Prompt label
        prompt_label = tk.Label(
            input_frame, 
            text="$ ", 
            bg=THEMES[self.theme]["terminal_bg"],
            fg=THEMES[self.theme]["terminal_fg"],
            font=("Consolas", 10)
        )
        prompt_label.pack(side="left")
        
        # Command input entry
        command_entry = tk.Entry(
            input_frame,
            bg=THEMES[self.theme]["terminal_bg"],
            fg=THEMES[self.theme]["terminal_fg"],
            font=("Consolas", 10),
            insertbackground=THEMES[self.theme]["terminal_fg"],
            bd=0,
            highlightthickness=0
        )
        command_entry.pack(fill="x", expand=True, side="left")
        
        # Terminal data storage
        terminal_data = {
            "display": terminal_display,
            "entry": command_entry,
            "history": [],
            "history_index": -1,
            "current_process": None,
            "cwd": os.getcwd()
        }
        
        # Bind events
        command_entry.bind("<Return>", lambda e: self.execute_terminal_command(terminal_data))
        command_entry.bind("<Up>", lambda e: self.terminal_history_up(terminal_data))
        command_entry.bind("<Down>", lambda e: self.terminal_history_down(terminal_data))
        command_entry.bind("<Control-c>", lambda e: self.interrupt_terminal_process(terminal_data))
        command_entry.bind("<Control-l>", lambda e: self.clear_terminal_shortcut(terminal_data))
        
        # Add tab to notebook
        tab_name = f"Terminal {len(self.terminal_notebook.tabs()) + 1}"
        self.terminal_notebook.add(terminal_frame, text=tab_name)
        self.terminal_notebook.select(terminal_frame)
        
        # Store terminal data
        setattr(terminal_frame, "terminal_data", terminal_data)
        
        # Welcome message
        self.append_to_terminal(terminal_data, f"Codesmith Terminal - {tab_name}\n")
        self.append_to_terminal(terminal_data, f"Current directory: {terminal_data['cwd']}\n")
        self.append_to_terminal(terminal_data, "Type 'help' for available commands.\n\n")
        
        # Focus on command entry
        command_entry.focus_set()
        
        return terminal_frame
    
    def get_current_terminal_data(self):
        """Get the currently selected terminal's data."""
        current_tab = self.terminal_notebook.select()
        if not current_tab:
            return None
        
        terminal_frame = self.nametowidget(current_tab)
        return getattr(terminal_frame, "terminal_data", None)
    
    def append_to_terminal(self, terminal_data, text):
        """Append text to terminal display."""
        display = terminal_data["display"]
        display.config(state="normal")
        display.insert(tk.END, text)
        display.see(tk.END)
        display.config(state="disabled")
    
    def execute_terminal_command(self, terminal_data):
        """Execute command entered in terminal."""
        command = terminal_data["entry"].get().strip()
        terminal_data["entry"].delete(0, tk.END)
        
        if not command:
            return
        
        # Add to history
        if command not in terminal_data["history"]:
            terminal_data["history"].append(command)
        terminal_data["history_index"] = len(terminal_data["history"])
        
        # Display command
        self.append_to_terminal(terminal_data, f"$ {command}\n")
        
        # Handle built-in commands
        if command == "help":
            help_text = """
Available commands:
  help         - Show this help message
  clear        - Clear terminal screen  
  pwd          - Show current directory
  cd <path>    - Change directory
  ls / dir     - List directory contents
  exit         - Close terminal tab
  
You can also run any system command (python, node, javac, etc.)
"""
            self.append_to_terminal(terminal_data, help_text)
        elif command == "clear":
            terminal_data["display"].config(state="normal")
            terminal_data["display"].delete(1.0, tk.END)
            terminal_data["display"].config(state="disabled")
        elif command == "pwd":
            self.append_to_terminal(terminal_data, f"{terminal_data['cwd']}\n")
        elif command.startswith("cd "):
            path = command[3:].strip()
            self.change_directory(terminal_data, path)
        elif command in ["ls", "dir"]:
            self.list_directory(terminal_data)
        elif command == "exit":
            self.close_current_terminal()
        else:
            # Execute system command
            self.execute_system_command(terminal_data, command)
    
    def change_directory(self, terminal_data, path):
        """Change terminal working directory."""
        try:
            if path == "..":
                new_path = os.path.dirname(terminal_data["cwd"])
            elif os.path.isabs(path):
                new_path = path
            else:
                new_path = os.path.join(terminal_data["cwd"], path)
            
            new_path = os.path.abspath(new_path)
            if os.path.exists(new_path) and os.path.isdir(new_path):
                terminal_data["cwd"] = new_path
                self.append_to_terminal(terminal_data, f"Changed directory to: {new_path}\n")
            else:
                self.append_to_terminal(terminal_data, f"Directory not found: {path}\n")
        except Exception as e:
            self.append_to_terminal(terminal_data, f"Error: {str(e)}\n")
    
    def list_directory(self, terminal_data):
        """List directory contents."""
        try:
            items = os.listdir(terminal_data["cwd"])
            if not items:
                self.append_to_terminal(terminal_data, "Directory is empty.\n")
                return
            
            # Separate directories and files
            dirs = [item for item in items if os.path.isdir(os.path.join(terminal_data["cwd"], item))]
            files = [item for item in items if os.path.isfile(os.path.join(terminal_data["cwd"], item))]
            
            # Display directories first
            for item in sorted(dirs):
                self.append_to_terminal(terminal_data, f"[DIR]  {item}\n")
            
            # Display files
            for item in sorted(files):
                self.append_to_terminal(terminal_data, f"       {item}\n")
                
        except Exception as e:
            self.append_to_terminal(terminal_data, f"Error listing directory: {str(e)}\n")
    
    def execute_system_command(self, terminal_data, command):
        """Execute system command in separate thread."""
        def run_command():
            try:
                # Start process
                process = subprocess.Popen(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=terminal_data["cwd"],
                    bufsize=1,
                    universal_newlines=True
                )
                
                terminal_data["current_process"] = process
                
                # Read output in real-time
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        self.append_to_terminal(terminal_data, output)
                
                # Read any remaining output
                stdout, stderr = process.communicate()
                if stdout:
                    self.append_to_terminal(terminal_data, stdout)
                if stderr:
                    self.append_to_terminal(terminal_data, f"Error: {stderr}")
                
                # Show completion
                if process.returncode == 0:
                    self.append_to_terminal(terminal_data, f"\nProcess completed successfully.\n")
                else:
                    self.append_to_terminal(terminal_data, f"\nProcess exited with code {process.returncode}.\n")
                
                terminal_data["current_process"] = None
                
            except Exception as e:
                self.append_to_terminal(terminal_data, f"Error executing command: {str(e)}\n")
                terminal_data["current_process"] = None
        
        # Run command in separate thread
        thread = threading.Thread(target=run_command)
        thread.daemon = True
        thread.start()
    
    def terminal_history_up(self, terminal_data):
        """Navigate up in command history."""
        if terminal_data["history"] and terminal_data["history_index"] > 0:
            terminal_data["history_index"] -= 1
            command = terminal_data["history"][terminal_data["history_index"]]
            terminal_data["entry"].delete(0, tk.END)
            terminal_data["entry"].insert(0, command)
    
    def terminal_history_down(self, terminal_data):
        """Navigate down in command history."""
        if terminal_data["history"] and terminal_data["history_index"] < len(terminal_data["history"]) - 1:
            terminal_data["history_index"] += 1
            command = terminal_data["history"][terminal_data["history_index"]]
            terminal_data["entry"].delete(0, tk.END)
            terminal_data["entry"].insert(0, command)
        elif terminal_data["history_index"] >= len(terminal_data["history"]) - 1:
            terminal_data["entry"].delete(0, tk.END)
            terminal_data["history_index"] = len(terminal_data["history"])
    
    def clear_current_terminal(self):
        """Clear the currently selected terminal."""
        terminal_data = self.get_current_terminal_data()
        if terminal_data:
            terminal_data["display"].config(state="normal")
            terminal_data["display"].delete(1.0, tk.END)
            terminal_data["display"].config(state="disabled")
    
    def close_current_terminal(self):
        """Close the currently selected terminal tab."""
        current_tab = self.terminal_notebook.select()
        if current_tab and len(self.terminal_notebook.tabs()) > 1:
            self.terminal_notebook.forget(current_tab)
    
    def toggle_terminal(self):
        """Show/hide the terminal panel."""
        if self.terminal_notebook.winfo_viewable():
            self.terminal_notebook.pack_forget()
        else:
            self.terminal_notebook.pack(fill="x", side="bottom")
    
    def interrupt_terminal_process(self, terminal_data):
        """Interrupt current running process (Ctrl+C)."""
        if terminal_data["current_process"]:
            try:
                terminal_data["current_process"].terminate()
                self.append_to_terminal(terminal_data, "\n^C Process interrupted.\n")
            except Exception as e:
                self.append_to_terminal(terminal_data, f"\nError interrupting process: {e}\n")
        return "break"
    
    def clear_terminal_shortcut(self, terminal_data):
        """Clear terminal using Ctrl+L shortcut."""
        terminal_data["display"].config(state="normal")
        terminal_data["display"].delete(1.0, tk.END)
        terminal_data["display"].config(state="disabled")
        return "break"

    # File tree handling
    def insert_node(self, parent, path):
        try:
            basename = os.path.basename(path)
            if not basename:
                basename = path
            node = self.tree.insert(parent, "end", text=basename, open=False, values=[path])
            if os.path.isdir(path):
                self.tree.insert(node, "end")
        except Exception as e:
            print(f"Error inserting node: {e}")

    def on_tree_expand(self, event):
        node = self.tree.focus()
        if not node:
            return
        children = self.tree.get_children(node)
        if children:
            first_child = children[0]
            if self.tree.item(first_child, "text") == "":
                self.tree.delete(first_child)
                path = self.tree.item(node, "values")[0]
                try:
                    for entry in os.listdir(path):
                        full_path = os.path.join(path, entry)
                        self.insert_node(node, full_path)
                except Exception as e:
                    print(f"Error expanding node: {e}")

    def on_tree_select(self, event):
        node = self.tree.focus()
        if not node:
            return
        path = self.tree.item(node, "values")[0]
        if os.path.isfile(path):
            # Check if file extension is supported
            _, ext = os.path.splitext(path)
            if ext.lower() in ALL_EXTENSIONS or ext == "":  # Also allow extensionless files
                self.open_file_in_tab(path)

    # Tab and editor management
    def open_file_in_tab(self, filepath):
        for tab_id in self.notebook.tabs():
            if self.open_files.get(tab_id) == filepath:
                self.notebook.select(tab_id)
                return
        frame = tk.Frame(self.notebook)
        text_widget = tk.Text(frame, wrap="none", undo=True)
        text_widget.pack(fill="both", expand=True)
        
        # Try different encodings to handle various file types
        content = ""
        encodings = ['utf-8', 'utf-8-sig', 'cp1252', 'iso-8859-1', 'latin-1']
        
        for encoding in encodings:
            try:
                with open(filepath, "r", encoding=encoding) as f:
                    content = f.read()
                break
            except UnicodeDecodeError:
                continue
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file {filepath}: {e}")
                return
        else:
            # If all encodings fail, try binary mode and decode with errors='replace'
            try:
                with open(filepath, "rb") as f:
                    raw_content = f.read()
                    content = raw_content.decode('utf-8', errors='replace')
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file {filepath}: {e}")
                return
        
        text_widget.insert(tk.END, content)
        # Add language indicator to tab title
        language = self.detect_language(filepath)
        basename = os.path.basename(filepath)
        if language != "text":
            tab_title = f"{basename} [{language.upper()}]  \u2716"
        else:
            tab_title = basename + "  \u2716"
            
        self.notebook.add(frame, text=tab_title)
        self.notebook.select(frame)
        self.open_files[str(frame)] = filepath
        self.apply_theme_to_widget(text_widget)
        text_widget.bind("<KeyRelease>", self.on_key_release)
        text_widget.bind("<Tab>", self.on_tab_press)
        text_widget.bind("<Down>", self.on_autocomplete_down)
        text_widget.bind("<Up>", self.on_autocomplete_up)
        text_widget.bind("<Return>", self.on_autocomplete_return)
        self.highlight_syntax(text_widget)

    def new_tab(self):
        frame = tk.Frame(self.notebook)
        text_widget = tk.Text(frame, wrap="none", undo=True)
        text_widget.pack(fill="both", expand=True)
        self.notebook.add(frame, text="Untitled  \u2716")
        self.notebook.select(frame)
        self.open_files[str(frame)] = None
        self.apply_theme_to_widget(text_widget)
        text_widget.bind("<KeyRelease>", self.on_key_release)
        text_widget.bind("<Tab>", self.on_tab_press)
        text_widget.bind("<Down>", self.on_autocomplete_down)
        text_widget.bind("<Up>", self.on_autocomplete_up)
        text_widget.bind("<Return>", self.on_autocomplete_return)

    def get_current_text_widget(self):
        tab = self.notebook.select()
        if not tab:
            return None
        frame = self.nametowidget(tab)
        children = frame.winfo_children()
        if children:
            return children[0]
        return None

    # File save/load
    def save_file(self):
        tab = self.notebook.select()
        if not tab:
            return
        filepath = self.open_files.get(tab)
        text_widget = self.get_current_text_widget()
        if filepath:
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(text_widget.get("1.0", tk.END))
                messagebox.showinfo("Saved", f"Saved {filepath}")
                self.update_tab_title(tab, os.path.basename(filepath))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")
        else:
            self.save_file_as()

    def save_file_as(self):
        # Create filetypes for save dialog
        filetypes = [
            ("Python Files", "*.py"),
            ("JavaScript Files", "*.js"),
            ("Java Files", "*.java"),
            ("C++ Files", "*.cpp"),
            ("C Files", "*.c"),
            ("HTML Files", "*.html"),
            ("CSS Files", "*.css"),
            ("JSON Files", "*.json"),
            ("XML Files", "*.xml"),
            ("Markdown Files", "*.md"),
            ("All Files", "*.*")
        ]
        
        filepath = filedialog.asksaveasfilename(defaultextension=".py", filetypes=filetypes)
        if filepath:
            tab = self.notebook.select()
            if not tab:
                return
            text_widget = self.get_current_text_widget()
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(text_widget.get("1.0", tk.END))
                self.open_files[tab] = filepath
                self.update_tab_title(tab, os.path.basename(filepath))
                messagebox.showinfo("Saved", f"Saved {filepath}")
                # Refresh syntax highlighting after save
                self.highlight_syntax(text_widget)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")

    def update_tab_title(self, tab_id, filename):
        # Add language indicator to tab title
        filepath = self.open_files.get(tab_id)
        language = self.detect_language(filepath)
        if language != "text":
            display_name = f"{filename} [{language.upper()}]"
        else:
            display_name = filename
        
        self.notebook.tab(tab_id, text=display_name + "  \u2716")
        self.title(f"Codesmith - {display_name}")

    def change_theme(self, theme_name):
        self.theme = theme_name
        self.apply_theme()

    def apply_theme(self):
        theme = THEMES[self.theme]
        self.configure(bg=theme["bg"])
        self.sidebar_frame.config(bg=theme["sidebar_bg"])

        style = ttk.Style()
        style.configure("Custom.Treeview",
                        background=theme["sidebar_bg"],
                        foreground=theme["sidebar_fg"],
                        fieldbackground=theme["sidebar_bg"])
        style.configure("Custom.Treeview.Heading",
                        background=theme["sidebar_bg"],
                        foreground=theme["sidebar_fg"])
        self.tree.configure(style="Custom.Treeview")
        self.tree.tag_configure("folder", background=theme["sidebar_bg"], foreground=theme["sidebar_fg"])

        for tab in self.notebook.tabs():
            frame = self.nametowidget(tab)
            for widget in frame.winfo_children():
                if isinstance(widget, tk.Text):
                    self.apply_theme_to_widget(widget)

        # Update terminal themes
        for terminal_tab in self.terminal_notebook.tabs():
            terminal_frame = self.nametowidget(terminal_tab)
            terminal_data = getattr(terminal_frame, "terminal_data", None)
            if terminal_data:
                terminal_data["display"].config(bg=theme["terminal_bg"], fg=theme["terminal_fg"])
                terminal_data["entry"].config(bg=theme["terminal_bg"], fg=theme["terminal_fg"], insertbackground=theme["terminal_fg"])
                # Update prompt label
                for widget in terminal_frame.winfo_children():
                    if isinstance(widget, tk.Frame):
                        for child in widget.winfo_children():
                            if isinstance(child, tk.Label):
                                child.config(bg=theme["terminal_bg"], fg=theme["terminal_fg"])

        # Also hide autocomplete popup if theme changes
        self.hide_autocomplete_popup()

    def apply_theme_to_widget(self, widget):
        theme = THEMES[self.theme]
        widget.config(bg=theme["bg"], fg=theme["fg"], insertbackground=theme["fg"])
        self.highlight_syntax(widget)

    # Syntax highlighting
    def highlight_syntax(self, widget):
        widget.tag_remove("keyword", "1.0", tk.END)
        theme = THEMES[self.theme]
        
        # Get current file path to determine language
        current_tab = self.notebook.select()
        if not current_tab:
            return
            
        filepath = self.open_files.get(current_tab)
        language = self.detect_language(filepath)
        
        # Get keywords for the detected language
        if language in LANGUAGES:
            keywords = LANGUAGES[language]["keywords"]
            for keyword in keywords:
                idx = "1.0"
                while True:
                    idx = widget.search(rf"\b{keyword}\b", idx, nocase=0, stopindex=tk.END, regexp=True)
                    if not idx:
                        break
                    end_idx = f"{idx}+{len(keyword)}c"
                    widget.tag_add("keyword", idx, end_idx)
                    idx = end_idx
        
        widget.tag_config("keyword", foreground=theme["keyword"])

    def on_key_release(self, event):
        widget = event.widget
        self.highlight_syntax(widget)
        self.handle_autocomplete(event)

    def on_tab_press(self, event):
        widget = event.widget
        # Accept autocomplete suggestion if popup visible
        if self.autocomplete_popup and self.autocomplete_popup.winfo_viewable():
            self.insert_autocomplete()
            return "break"
        widget.insert(tk.INSERT, " " * 4)
        return "break"

    # Autocomplete popup handling
    def handle_autocomplete(self, event):
        widget = event.widget
        cursor_index = widget.index(tk.INSERT)
        line_start = widget.index(f"{cursor_index} linestart")
        current_line = widget.get(line_start, cursor_index)
        word_match = re.findall(r"\w+$", current_line)
        if word_match:
            prefix = word_match[0]
            
            # Get current language
            current_tab = self.notebook.select()
            if current_tab:
                filepath = self.open_files.get(current_tab)
                language = self.detect_language(filepath)
                
                if language in LANGUAGES:
                    keywords = LANGUAGES[language]["keywords"]
                    matches = [kw for kw in keywords if kw.startswith(prefix)]
                    if matches:
                        self.show_autocomplete_popup(widget, matches, prefix)
                        return
        self.hide_autocomplete_popup()

    def show_autocomplete_popup(self, widget, suggestions, prefix):
        if self.autocomplete_popup is None:
            self.autocomplete_popup = tk.Toplevel(self)
            self.autocomplete_popup.wm_overrideredirect(True)
            self.listbox = tk.Listbox(self.autocomplete_popup, height=6)
            self.listbox.pack()
            self.listbox.bind("<Double-Button-1>", lambda e: self.insert_autocomplete())
            self.listbox.bind("<Return>", lambda e: self.insert_autocomplete())

        else:
            self.listbox.delete(0, tk.END)

        for s in suggestions:
            self.listbox.insert(tk.END, s)

        self.autocomplete_prefix = prefix
        self.listbox.select_set(0)

        # Position popup near cursor
        bbox = widget.bbox(tk.INSERT)
        if bbox:
            x, y, width, height = bbox
            x_root = widget.winfo_rootx() + x
            y_root = widget.winfo_rooty() + y + height
            self.autocomplete_popup.wm_geometry(f"+{x_root}+{y_root}")

        self.autocomplete_popup.deiconify()
        self.autocomplete_popup.lift()
        self.autocomplete_popup.update_idletasks()

    def hide_autocomplete_popup(self):
        if self.autocomplete_popup:
            self.autocomplete_popup.withdraw()

    def insert_autocomplete(self):
        if not self.autocomplete_popup:
            return
        widget = self.get_current_text_widget()
        if not widget:
            return
        selection = self.listbox.curselection()
        if not selection:
            return
        selected_text = self.listbox.get(selection[0])
        # Replace current prefix with selected text
        cursor_index = widget.index(tk.INSERT)
        line_start = widget.index(f"{cursor_index} linestart")
        current_line = widget.get(line_start, cursor_index)
        prefix_len = len(self.autocomplete_prefix)
        start_index = f"{cursor_index} - {prefix_len}c"
        widget.delete(start_index, cursor_index)
        widget.insert(start_index, selected_text)
        self.hide_autocomplete_popup()
        widget.mark_set(tk.INSERT, f"{start_index} + {len(selected_text)}c")

    def on_autocomplete_down(self, event):
        if self.autocomplete_popup and self.autocomplete_popup.winfo_viewable():
            idx = self.listbox.curselection()
            if idx:
                next_idx = (idx[0] + 1) % self.listbox.size()
            else:
                next_idx = 0
            self.listbox.select_clear(0, tk.END)
            self.listbox.select_set(next_idx)
            self.listbox.activate(next_idx)
            return "break"

    def on_autocomplete_up(self, event):
        if self.autocomplete_popup and self.autocomplete_popup.winfo_viewable():
            idx = self.listbox.curselection()
            if idx:
                prev_idx = (idx[0] - 1) % self.listbox.size()
            else:
                prev_idx = self.listbox.size() - 1
            self.listbox.select_clear(0, tk.END)
            self.listbox.select_set(prev_idx)
            self.listbox.activate(prev_idx)
            return "break"

    def on_autocomplete_return(self, event):
        if self.autocomplete_popup and self.autocomplete_popup.winfo_viewable():
            self.insert_autocomplete()
            return "break"

    # Run code in current tab
    def run_code(self):
        tab = self.notebook.select()
        if not tab:
            return
        filepath = self.open_files.get(tab)
        widget = self.get_current_text_widget()
        code = widget.get("1.0", tk.END)

        # Detect language and get run command
        language = self.detect_language(filepath)
        if language not in LANGUAGES or not LANGUAGES[language]["run_command"]:
            messagebox.showwarning("Cannot Run", f"Cannot execute {language} files directly.\nSupported executable languages: Python, JavaScript, Java, C++")
            return

        # Save file first
        if filepath:
            filename = filepath
            with open(filename, "w", encoding="utf-8") as f:
                f.write(code)
        else:
            import tempfile
            # Use appropriate extension for the language
            if language in LANGUAGES:
                ext = LANGUAGES[language]["extensions"][0]
            else:
                ext = ".txt"
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext, mode='w', encoding="utf-8") as tmp:
                filename = tmp.name
                tmp.write(code)

        def run():
            # Get current terminal or create one
            terminal_data = self.get_current_terminal_data()
            if not terminal_data:
                self.create_terminal_tab()
                terminal_data = self.get_current_terminal_data()
            
            # Clear terminal and show run info
            self.append_to_terminal(terminal_data, f"\n=== Running {language} file: {os.path.basename(filename)} ===\n")
            
            run_command = LANGUAGES[language]["run_command"].copy()
            
            try:
                if language == "cpp":
                    # Special handling for C++: compile first, then run
                    exe_name = filename.replace(".cpp", ".exe").replace(".c", ".exe")
                    compile_cmd = ["g++", filename, "-o", exe_name]
                    compile_process = subprocess.Popen(compile_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=terminal_data["cwd"])
                    compile_out, compile_err = compile_process.communicate()
                    
                    if compile_process.returncode != 0:
                        self.append_to_terminal(terminal_data, f"Compilation failed:\n{compile_err}")
                        return
                    else:
                        self.append_to_terminal(terminal_data, f"Compilation successful.\n")
                        process = subprocess.Popen([exe_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=terminal_data["cwd"])
                elif language == "java":
                    # Special handling for Java: compile first, then run
                    class_name = os.path.splitext(os.path.basename(filename))[0]
                    compile_cmd = ["javac", filename]
                    compile_process = subprocess.Popen(compile_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=terminal_data["cwd"])
                    compile_out, compile_err = compile_process.communicate()
                    
                    if compile_process.returncode != 0:
                        self.append_to_terminal(terminal_data, f"Compilation failed:\n{compile_err}")
                        return
                    else:
                        self.append_to_terminal(terminal_data, f"Compilation successful.\n")
                        # Run the class file
                        directory = os.path.dirname(filename)
                        process = subprocess.Popen(["java", "-cp", directory, class_name], 
                                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=terminal_data["cwd"])
                else:
                    # For Python, JavaScript, etc.
                    run_command.append(filename)
                    process = subprocess.Popen(run_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=terminal_data["cwd"])

                # Read output in real-time
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        self.append_to_terminal(terminal_data, output)
                    
                # Read any remaining output
                stdout, stderr = process.communicate()
                if stdout:
                    self.append_to_terminal(terminal_data, stdout)
                if stderr:
                    self.append_to_terminal(terminal_data, f"Error: {stderr}")

                self.append_to_terminal(terminal_data, f"\n=== Process finished with exit code {process.returncode} ===\n\n")
                
            except FileNotFoundError:
                self.append_to_terminal(terminal_data, f"Error: {run_command[0]} not found. Please install {language} runtime/compiler.\n")
            except Exception as e:
                self.append_to_terminal(terminal_data, f"Error running code: {e}\n")

        threading.Thread(target=run).start()

    # Tab events
    def on_tab_changed(self, event):
        tab = event.widget.select()
        filepath = self.open_files.get(tab)
        if filepath:
            language = self.detect_language(filepath)
            basename = os.path.basename(filepath)
            if language != "text":
                display_name = f"{basename} [{language.upper()}]"
            else:
                display_name = basename
            self.title(f"Codesmith - {display_name}")
        else:
            self.title("Codesmith - Untitled")

    def on_tab_closed(self, event):
        closed_tabs = set(self.open_files.keys()) - set(self.notebook.tabs())
        for tab in closed_tabs:
            self.open_files.pop(tab, None)

    # Open file dialog
    def open_file_dialog(self):
        # Create filetypes list for all supported languages
        filetypes = []
        
        # Add specific language filters
        filetypes.append(("Python Files", "*.py;*.pyw"))
        filetypes.append(("JavaScript Files", "*.js;*.jsx;*.mjs"))
        filetypes.append(("Java Files", "*.java"))
        filetypes.append(("C/C++ Files", "*.c;*.cpp;*.cc;*.cxx;*.h;*.hpp"))
        filetypes.append(("HTML Files", "*.html;*.htm;*.xhtml"))
        filetypes.append(("CSS Files", "*.css"))
        filetypes.append(("JSON Files", "*.json"))
        filetypes.append(("XML Files", "*.xml"))
        filetypes.append(("Markdown Files", "*.md;*.markdown"))
        
        # Add generic options
        all_extensions = ";".join([f"*{ext}" for ext in ALL_EXTENSIONS])
        filetypes.insert(0, ("All Code Files", all_extensions))
        filetypes.append(("All Files", "*.*"))
        
        filepath = filedialog.askopenfilename(filetypes=filetypes)
        if filepath:
            self.open_file_in_tab(filepath)

if __name__ == "__main__":
    app = CodeSmith()
    app.mainloop()



