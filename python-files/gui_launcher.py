import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import subprocess
import sys
import json
from pathlib import Path

class SimpleLauncher:
    def __init__(self, root):
        """Initialize the launcher application"""
        self.root = root
        self.root.title("Simple Launcher")
        self.root.geometry("600x500")
        self.root.configure(bg='#f0f0f0')
        
        # Configuration file path - in same directory as script
        self.config_file = Path(__file__).parent / "launcher_config.json"
        
        # Default shortcuts if config file doesn't exist
        self.default_shortcuts = [
            {"name": "Notepad", "path": "notepad.exe", "type": "executable"},
            {"name": "Calculator", "path": "calc.exe", "type": "executable"},
            {"name": "Documents", "path": str(Path.home() / "Documents"), "type": "folder"},
            {"name": "Downloads", "path": str(Path.home() / "Downloads"), "type": "folder"}
        ]
        
        self.shortcuts = []
        self.setup_ui()
        self.load_shortcuts()
        self.refresh_shortcuts_display()
        
        # Center the window on screen
        self.center_window()
    
    def center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_ui(self):
        """Create the user interface"""
        # Main title
        title_label = tk.Label(
            self.root, 
            text="Simple Launcher", 
            font=("Arial", 16, "bold"),
            bg='#f0f0f0',
            fg='#333333'
        )
        title_label.pack(pady=10)
        
        # Create a frame for the main content
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create a scrollable frame for shortcuts
        self.create_scrollable_frame(main_frame)
        
        # Button frame at the bottom
        button_frame = tk.Frame(self.root, bg='#f0f0f0')
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Buttons for managing shortcuts
        self.create_buttons(button_frame)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = tk.Label(
            self.root, 
            textvariable=self.status_var, 
            relief=tk.SUNKEN, 
            anchor=tk.W,
            bg='#e0e0e0',
            fg='#666666'
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_scrollable_frame(self, parent):
        """Create a scrollable frame for the shortcuts"""
        # Create canvas and scrollbar
        canvas = tk.Canvas(parent, bg='#ffffff', highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg='#ffffff')
        
        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel to canvas
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
    
    def create_buttons(self, parent):
        """Create management buttons"""
        # Add shortcut button
        add_btn = tk.Button(
            parent,
            text="Add Shortcut",
            command=self.add_shortcut,
            bg='#4CAF50',
            fg='white',
            font=("Arial", 10, "bold"),
            relief=tk.RAISED,
            bd=2
        )
        add_btn.pack(side=tk.LEFT, padx=5)
        
        # Edit config button
        edit_btn = tk.Button(
            parent,
            text="Edit Config File",
            command=self.edit_config,
            bg='#2196F3',
            fg='white',
            font=("Arial", 10, "bold"),
            relief=tk.RAISED,
            bd=2
        )
        edit_btn.pack(side=tk.LEFT, padx=5)
        
        # Refresh button
        refresh_btn = tk.Button(
            parent,
            text="Refresh",
            command=self.refresh_shortcuts,
            bg='#FF9800',
            fg='white',
            font=("Arial", 10, "bold"),
            relief=tk.RAISED,
            bd=2
        )
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Help button
        help_btn = tk.Button(
            parent,
            text="Help",
            command=self.show_help,
            bg='#9C27B0',
            fg='white',
            font=("Arial", 10, "bold"),
            relief=tk.RAISED,
            bd=2
        )
        help_btn.pack(side=tk.RIGHT, padx=5)
    
    def load_shortcuts(self):
        """Load shortcuts from the configuration file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.shortcuts = json.load(f)
                self.status_var.set(f"Loaded {len(self.shortcuts)} shortcuts")
            else:
                # Create default config file
                self.shortcuts = self.default_shortcuts
                self.save_shortcuts()
                self.status_var.set("Created default configuration")
        except Exception as e:
            self.show_error(
                "Configuration Loading Error",
                f"Could not load shortcuts configuration: {str(e)}\n\n"
                "The program will use default shortcuts. You can recreate the "
                "configuration by adding shortcuts manually."
            )
            self.shortcuts = self.default_shortcuts
    
    def save_shortcuts(self):
        """Save shortcuts to the configuration file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.shortcuts, f, indent=2)
            self.status_var.set("Configuration saved successfully")
        except Exception as e:
            self.show_error(
                "Configuration Save Error",
                f"Could not save shortcuts configuration: {str(e)}\n\n"
                "Make sure you have write permissions to the program directory."
            )
    
    def refresh_shortcuts_display(self):
        """Refresh the display of shortcuts"""
        # Clear existing shortcuts
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        if not self.shortcuts:
            # Show message if no shortcuts
            no_shortcuts_label = tk.Label(
                self.scrollable_frame,
                text="No shortcuts configured.\nClick 'Add Shortcut' to get started!",
                font=("Arial", 12),
                bg='#ffffff',
                fg='#666666'
            )
            no_shortcuts_label.pack(pady=50)
            return
        
        # Create shortcut buttons
        for i, shortcut in enumerate(self.shortcuts):
            self.create_shortcut_button(shortcut, i)
    
    def create_shortcut_button(self, shortcut, index):
        """Create a button for a shortcut"""
        # Frame for each shortcut
        shortcut_frame = tk.Frame(self.scrollable_frame, bg='#ffffff', relief=tk.RAISED, bd=1)
        shortcut_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Determine icon based on type
        if shortcut['type'] == 'folder':
            icon = "📁"
        elif shortcut['type'] == 'executable':
            icon = "⚙️"
        else:
            icon = "📄"
        
        # Main button
        btn = tk.Button(
            shortcut_frame,
            text=f"{icon} {shortcut['name']}",
            command=lambda s=shortcut: self.open_shortcut(s),
            font=("Arial", 12, "bold"),
            bg='#e3f2fd',
            fg='#1976d2',
            relief=tk.RAISED,
            bd=2,
            cursor='hand2'
        )
        btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        
        # Delete button
        delete_btn = tk.Button(
            shortcut_frame,
            text="✕",
            command=lambda idx=index: self.delete_shortcut(idx),
            font=("Arial", 10, "bold"),
            bg='#f44336',
            fg='white',
            width=3,
            relief=tk.RAISED,
            bd=2,
            cursor='hand2'
        )
        delete_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Path label
        path_label = tk.Label(
            shortcut_frame,
            text=shortcut['path'],
            font=("Arial", 8),
            bg='#ffffff',
            fg='#666666'
        )
        path_label.pack(side=tk.BOTTOM, anchor=tk.W, padx=5, pady=2)
    
    def open_shortcut(self, shortcut):
        """Open a shortcut (file, folder, or executable)"""
        try:
            path = shortcut['path']
            
            # Check if path exists
            if not os.path.exists(path):
                # For executables, try to find them in PATH
                if shortcut['type'] == 'executable':
                    try:
                        subprocess.run([path], check=True)
                        self.status_var.set(f"Opened {shortcut['name']}")
                        return
                    except:
                        pass
                
                self.show_error(
                    "Path Not Found",
                    f"The path '{path}' does not exist.\n\n"
                    f"Please check if:\n"
                    f"• The file or folder hasn't been moved or deleted\n"
                    f"• The path is spelled correctly\n"
                    f"• You have permission to access this location\n\n"
                    f"You can edit the configuration to fix this path."
                )
                return
            
            # Open based on type
            if shortcut['type'] == 'folder':
                # Open folder in explorer
                os.startfile(path)
            elif shortcut['type'] == 'executable':
                # Run executable
                subprocess.Popen([path])
            else:
                # Open file with default application
                os.startfile(path)
            
            self.status_var.set(f"Opened {shortcut['name']}")
            
        except Exception as e:
            self.show_error(
                "Open Error",
                f"Could not open '{shortcut['name']}': {str(e)}\n\n"
                f"This might happen if:\n"
                f"• The file type isn't associated with any program\n"
                f"• You don't have permission to access the file\n"
                f"• The file is corrupted or in use by another program\n\n"
                f"Try opening the file manually to verify it works."
            )
    
    def add_shortcut(self):
        """Add a new shortcut"""
        dialog = AddShortcutDialog(self.root, self.add_shortcut_callback)
    
    def add_shortcut_callback(self, name, path, shortcut_type):
        """Callback for adding a new shortcut"""
        new_shortcut = {
            "name": name,
            "path": path,
            "type": shortcut_type
        }
        self.shortcuts.append(new_shortcut)
        self.save_shortcuts()
        self.refresh_shortcuts_display()
        self.status_var.set(f"Added shortcut: {name}")
    
    def delete_shortcut(self, index):
        """Delete a shortcut"""
        if 0 <= index < len(self.shortcuts):
            shortcut = self.shortcuts[index]
            result = messagebox.askyesno(
                "Delete Shortcut",
                f"Are you sure you want to delete '{shortcut['name']}'?"
            )
            if result:
                self.shortcuts.pop(index)
                self.save_shortcuts()
                self.refresh_shortcuts_display()
                self.status_var.set(f"Deleted shortcut: {shortcut['name']}")
    
    def edit_config(self):
        """Open the configuration file for editing"""
        try:
            os.startfile(self.config_file)
            self.status_var.set("Opened configuration file for editing")
            messagebox.showinfo(
                "Edit Configuration",
                "The configuration file has been opened in your default text editor.\n\n"
                "After making changes, save the file and click 'Refresh' to reload the shortcuts.\n\n"
                "Format: Each shortcut needs 'name', 'path', and 'type' fields.\n"
                "Types can be: 'file', 'folder', or 'executable'"
            )
        except Exception as e:
            self.show_error(
                "Edit Configuration Error",
                f"Could not open configuration file: {str(e)}\n\n"
                f"The file location is: {self.config_file}\n\n"
                f"You can manually open this file with any text editor."
            )
    
    def refresh_shortcuts(self):
        """Refresh shortcuts from the configuration file"""
        self.load_shortcuts()
        self.refresh_shortcuts_display()
    
    def show_help(self):
        """Show help information"""
        help_text = """Simple Launcher Help

How to use:
• Click any shortcut button to open that file, folder, or program
• Use 'Add Shortcut' to add new shortcuts
• Click the red '✕' button to delete a shortcut
• Use 'Edit Config File' to manually edit the configuration
• Click 'Refresh' to reload shortcuts after editing the config file

Configuration File:
The shortcuts are stored in 'launcher_config.json' in the same folder as this program.

Shortcut Types:
• file: Any document or file
• folder: Any directory/folder
• executable: Any .exe program

Tips:
• For system programs (like Calculator), just use the program name (calc.exe)
• For files/folders, use the full path
• The configuration file is automatically created with examples"""
        
        messagebox.showinfo("Help", help_text)
    
    def show_error(self, title, message):
        """Show an error message to the user"""
        messagebox.showerror(title, message)
        self.status_var.set("Error occurred - see message")


class AddShortcutDialog:
    def __init__(self, parent, callback):
        """Initialize the add shortcut dialog"""
        self.callback = callback
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add Shortcut")
        self.dialog.geometry("500x300")
        self.dialog.configure(bg='#f0f0f0')
        self.dialog.resizable(False, False)
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog on parent
        self.center_dialog(parent)
        
        self.setup_dialog()
    
    def center_dialog(self, parent):
        """Center the dialog on the parent window"""
        parent.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 250
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 150
        self.dialog.geometry(f"500x300+{x}+{y}")
    
    def setup_dialog(self):
        """Setup the dialog interface"""
        # Title
        title_label = tk.Label(
            self.dialog,
            text="Add New Shortcut",
            font=("Arial", 14, "bold"),
            bg='#f0f0f0'
        )
        title_label.pack(pady=10)
        
        # Name entry
        name_frame = tk.Frame(self.dialog, bg='#f0f0f0')
        name_frame.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(name_frame, text="Name:", font=("Arial", 10, "bold"), bg='#f0f0f0').pack(anchor=tk.W)
        self.name_entry = tk.Entry(name_frame, font=("Arial", 10), width=50)
        self.name_entry.pack(fill=tk.X, pady=2)
        
        # Path entry
        path_frame = tk.Frame(self.dialog, bg='#f0f0f0')
        path_frame.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(path_frame, text="Path:", font=("Arial", 10, "bold"), bg='#f0f0f0').pack(anchor=tk.W)
        
        path_entry_frame = tk.Frame(path_frame, bg='#f0f0f0')
        path_entry_frame.pack(fill=tk.X, pady=2)
        
        self.path_entry = tk.Entry(path_entry_frame, font=("Arial", 10))
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_btn = tk.Button(
            path_entry_frame,
            text="Browse",
            command=self.browse_path,
            bg='#2196F3',
            fg='white',
            font=("Arial", 9)
        )
        browse_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Type selection
        type_frame = tk.Frame(self.dialog, bg='#f0f0f0')
        type_frame.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(type_frame, text="Type:", font=("Arial", 10, "bold"), bg='#f0f0f0').pack(anchor=tk.W)
        
        self.type_var = tk.StringVar(value="file")
        
        type_radio_frame = tk.Frame(type_frame, bg='#f0f0f0')
        type_radio_frame.pack(anchor=tk.W, pady=2)
        
        tk.Radiobutton(type_radio_frame, text="File", variable=self.type_var, value="file", bg='#f0f0f0').pack(side=tk.LEFT)
        tk.Radiobutton(type_radio_frame, text="Folder", variable=self.type_var, value="folder", bg='#f0f0f0').pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(type_radio_frame, text="Executable", variable=self.type_var, value="executable", bg='#f0f0f0').pack(side=tk.LEFT)
        
        # Buttons
        button_frame = tk.Frame(self.dialog, bg='#f0f0f0')
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=self.dialog.destroy,
            bg='#f44336',
            fg='white',
            font=("Arial", 10, "bold")
        )
        cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        add_btn = tk.Button(
            button_frame,
            text="Add Shortcut",
            command=self.add_shortcut,
            bg='#4CAF50',
            fg='white',
            font=("Arial", 10, "bold")
        )
        add_btn.pack(side=tk.RIGHT, padx=5)
        
        # Focus on name entry
        self.name_entry.focus()
    
    def browse_path(self):
        """Browse for a file or folder"""
        if self.type_var.get() == "folder":
            path = filedialog.askdirectory()
        else:
            path = filedialog.askopenfilename()
        
        if path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, path)
    
    def add_shortcut(self):
        """Add the shortcut"""
        name = self.name_entry.get().strip()
        path = self.path_entry.get().strip()
        shortcut_type = self.type_var.get()
        
        if not name:
            messagebox.showerror("Error", "Please enter a name for the shortcut.")
            return
        
        if not path:
            messagebox.showerror("Error", "Please enter a path for the shortcut.")
            return
        
        # Validate path exists (except for executables which might be in PATH)
        if shortcut_type != "executable" and not os.path.exists(path):
            result = messagebox.askyesno(
                "Path Not Found",
                f"The path '{path}' does not exist.\n\nDo you want to add it anyway?"
            )
            if not result:
                return
        
        self.callback(name, path, shortcut_type)
        self.dialog.destroy()


def main():
    """Main function to run the application"""
    try:
        root = tk.Tk()
        app = SimpleLauncher(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror(
            "Application Error",
            f"An unexpected error occurred: {str(e)}\n\n"
            f"The application will now close."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
