import subprocess
import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import importlib.util
import tkinter.font as tkfont
import shutil
import zipfile
import json

def ensure_package(package_name):
    try:
        __import__(package_name)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

ensure_package("requests")
import requests

PLUGIN_DIR = "plugins"
FEATURED_DIR = "featured plugins"
FONT_DIR = "fonts"
SETTINGS_FILE = "settings.json"

os.makedirs(PLUGIN_DIR, exist_ok=True)
os.makedirs(FEATURED_DIR, exist_ok=True)
os.makedirs(FONT_DIR, exist_ok=True)

loaded_plugins = []

def load_custom_font():
    FONT_PATH = os.path.join(FONT_DIR, "Rubik-Bold.ttf")
    if os.path.exists(FONT_PATH):
        try:
            tkfont.Font(root, name="RubikBold", file=FONT_PATH, size=10)
        except tk.TclError:
            pass

class ThemeManager:
    @staticmethod
    def get_themes():
        return {
            "Midnight": {
                "bg_color": "#0a0a0a",
                "container_bg": "#1a1a1a",
                "button_bg": "#2a2a2a",
                "button_selected_bg": "#404040",
                "red_x_bg": "#4a1a1a",
                "label_fg": "#e0e0e0",
                "text_fg": "#f0f0f0"
            },
            "Dark": {
                "bg_color": "#222222",
                "container_bg": "#3b3b3b",
                "button_bg": "#636363",
                "button_selected_bg": "#3271EC",
                "red_x_bg": "#cc4c4c",
                "label_fg": "white",
                "text_fg": "white"
            },
            "Light": {
                "bg_color": "#d8e3ec",
                "container_bg": "#cad4dc",
                "button_bg": "#ebf0f4",
                "button_selected_bg": "#3271EC",
                "red_x_bg": "#cc4c4c",
                "label_fg": "black",
                "text_fg": "black"
            },
            "Amethyst": {
                "bg_color": "#331e5c",
                "container_bg": "#6649a0",
                "button_bg": "#5b23ca",
                "button_selected_bg": "#ac94db",
                "red_x_bg": "#3f374e",
                "label_fg": "white",
                "text_fg": "white"
            },
            "Navy": {
                "bg_color": "#152f57",
                "container_bg": "#173c76",
                "button_bg": "#1a57b4",
                "button_selected_bg": "#0065ff",
                "red_x_bg": "#2d405e",
                "label_fg": "white",
                "text_fg": "white"
            },
            "Banana": {
                "bg_color": "#ebecc3",
                "container_bg": "#d8d9ad",
                "button_bg": "#c0c192",
                "button_selected_bg": "#b9bb6b",
                "red_x_bg": "#bebf8f",
                "label_fg": "#4c4c4c",
                "text_fg": "#4c4c4c"
            },
            "Autumn": {
                "bg_color": "#2d1a0f",
                "container_bg": "#4a2f1a",
                "button_bg": "#cc6600",
                "button_selected_bg": "#ff8533",
                "red_x_bg": "#8b3a00",
                "label_fg": "#fff2e6",
                "text_fg": "#fff2e6"
            },
            "Forest": {
                "bg_color": "#1a2e1a",
                "container_bg": "#3d2f1a",
                "button_bg": "#5d4037",
                "button_selected_bg": "#66bb6a",
                "red_x_bg": "#6d4c41",
                "label_fg": "#e8f5e8",
                "text_fg": "#e8f5e8"
            },
            "Crimson": {
                "bg_color": "#2d1b1b",
                "container_bg": "#4a2c2c",
                "button_bg": "#c62828",
                "button_selected_bg": "#e53935",
                "red_x_bg": "#b71c1c",
                "label_fg": "#ffebee",
                "text_fg": "#ffebee"
            },
            "Lily": {
                "bg_color": "#f8e8f0",
                "container_bg": "#f0d4e0",
                "button_bg": "#e8b4d0",
                "button_selected_bg": "#d48bb8",
                "red_x_bg": "#c76ba0",
                "label_fg": "#6b2c47",
                "text_fg": "#6b2c47"
            }
        }
    
    @staticmethod
    def load_settings():
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {"theme": "Dark"}
    
    @staticmethod
    def save_settings(settings):
        try:
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(settings, f)
        except:
            pass

class PluginContainer(tk.Frame):
    """Container for a single plugin with border and title"""
    def __init__(self, parent, plugin_name, theme_colors):
        super().__init__(parent, bg=theme_colors["bg_color"])
        self.plugin_name = plugin_name
        self.theme_colors = theme_colors
        self.original_title_method = None
        
        # Create a labeled frame for the plugin
        self.plugin_frame = tk.LabelFrame(
            self, 
            text=plugin_name,
            bg=theme_colors["container_bg"],
            fg=theme_colors["label_fg"],
            font=("TkDefaultFont", 10, "bold"),
            bd=2,
            relief="raised"
        )
        self.plugin_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Override the title method to prevent plugins from changing window title
        self.title = self._blocked_title
        self.configure = self._safe_configure
        self.geometry = self._blocked_geometry
        self.minsize = self._blocked_minsize
        self.resizable = self._blocked_resizable
    
    def _blocked_title(self, *args):
        """Block plugins from changing the window title"""
        pass
    
    def _safe_configure(self, *args, **kwargs):
        """Only allow safe configuration changes"""
        # Remove window-level configurations that shouldn't be changed
        safe_kwargs = {k: v for k, v in kwargs.items() 
                      if k not in ['title']}
        if safe_kwargs:
            super().configure(**safe_kwargs)
    
    def _blocked_geometry(self, *args):
        """Block plugins from changing window geometry"""
        pass
    
    def _blocked_minsize(self, *args):
        """Block plugins from changing window minimum size"""
        pass
    
    def _blocked_resizable(self, *args):
        """Block plugins from changing window resizable state"""
        pass
    
    def get_plugin_frame(self):
        """Return the frame where plugin content should be placed"""
        return self.plugin_frame

class PluginManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("VokoToolkitHub")
        self.root.geometry("480x420")
        self.root.minsize(400, 600)
        
        self.selected_plugins = set()
        self.settings = ThemeManager.load_settings()
        self.current_theme = self.settings.get("theme", "Dark")
        self.theme_colors = ThemeManager.get_themes()[self.current_theme]
        
        self.apply_theme()
        self.create_widgets()

    def apply_theme(self):
        self.root.configure(bg=self.theme_colors["bg_color"])
        
        # Update theme colors as instance variables for easy access
        self.BG_COLOR = self.theme_colors["bg_color"]
        self.CONTAINER_BG = self.theme_colors["container_bg"]
        self.BUTTON_BG = self.theme_colors["button_bg"]
        self.BUTTON_SELECTED_BG = self.theme_colors["button_selected_bg"]
        self.RED_X_BG = self.theme_colors["red_x_bg"]
        self.LABEL_FG = self.theme_colors["label_fg"]
        self.TEXT_FG = self.theme_colors["text_fg"]

    def create_widgets(self):
        rubik_bold = "RubikBold" if "RubikBold" in tkfont.names() else "TkDefaultFont"
        rubik_regular = rubik_bold

        style = ttk.Style()
        style.theme_use("default")
        style.configure("TButton",
                        background=self.BUTTON_BG,
                        foreground=self.TEXT_FG,
                        font=(rubik_regular, 10),
                        padding=6,
                        relief="flat")
        style.map("TButton",
                  background=[("active", "#505050"), ("pressed", "#404040")],
                  foreground=[("disabled", "#aaaaaa")])

        title_frame = tk.Frame(self.root, bg=self.BG_COLOR)
        title_frame.pack(fill="x", pady=(10, 5))

        title_label = tk.Label(title_frame, text="VokoToolkit", bg=self.BG_COLOR, fg=self.TEXT_FG,
                               font=(rubik_bold, 20, "bold"))
        title_label.pack(side="left", padx=(20, 5))

        testing_label = tk.Label(title_frame, text=" ", bg=self.BG_COLOR, fg=self.TEXT_FG,
                                 font=(rubik_regular, 12))
        testing_label.pack(side="left", pady=(8, 0))

        gear_button = tk.Button(title_frame, text="\u2699\ufe0f", bg=self.BG_COLOR, fg=self.TEXT_FG, font=(rubik_bold, 20),
                                relief="flat", bd=0, command=self.open_settings_window)
        gear_button.pack(side="right", padx=15)

        outer_frame = tk.Frame(self.root, bg=self.CONTAINER_BG, bd=0, relief="flat")
        outer_frame.pack(padx=15, pady=(0, 0), fill="both", expand=True)

        self.plugins_label = tk.Label(outer_frame, text="Plugins", bg=self.CONTAINER_BG,
                                      fg=self.LABEL_FG,
                                      font=(rubik_bold, 14, "bold"))
        self.plugins_label.pack(anchor="nw", padx=15, pady=(10, 0))

        self.canvas = tk.Canvas(outer_frame, bg=self.CONTAINER_BG, highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.scrollbar = ttk.Scrollbar(outer_frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.scrollbar.pack_forget()

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.plugin_button_frame = tk.Frame(self.canvas, bg=self.CONTAINER_BG)
        self.plugin_button_frame_id = self.canvas.create_window((0, 0), window=self.plugin_button_frame, anchor="nw")

        self.canvas.bind('<Configure>', self.resize_plugin_frame)
        self.plugin_button_frame.bind("<Configure>", self.update_scrollbar_visibility)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.plugin_files = []
        self.refresh_plugin_buttons(rubik_regular)

        buttons_frame = tk.Frame(self.root, bg=self.BG_COLOR)
        buttons_frame.pack(pady=15)

        launch_button = ttk.Button(buttons_frame, text="Launch New Window", command=self.launch_blank_window)
        launch_button.pack(side="left", padx=(0, 10))

        featured_button = ttk.Button(buttons_frame, text="Add Featured Plugin", command=self.open_featured_plugin_dialog)
        featured_button.pack(side="left")

    def refresh_plugin_buttons(self, font):
        for widget in self.plugin_button_frame.winfo_children():
            widget.destroy()

        self.plugin_files = []
        for filename in os.listdir(PLUGIN_DIR):
            if filename.endswith(".py"):
                plugin_name = os.path.splitext(filename)[0]
                self.plugin_files.append(plugin_name)

        self.plugin_files.sort()

        for plugin_name in self.plugin_files:
            frame = tk.Frame(self.plugin_button_frame, bg=self.CONTAINER_BG)
            frame.pack(fill="x", pady=3, padx=10, anchor="nw")

            btn_container = tk.Frame(frame, bg=self.CONTAINER_BG)
            btn_container.pack(side="left", fill="x", expand=True)

            btn = tk.Button(
                btn_container,
                text=plugin_name,
                bg=self.BUTTON_SELECTED_BG if plugin_name in self.selected_plugins else self.BUTTON_BG,
                fg=self.TEXT_FG,
                relief="raised",
                font=(font, 12),
                padx=10,
                pady=6,
                anchor="w",
                highlightthickness=0,
                command=lambda name=plugin_name: self.toggle_plugin_selection(name)
            )
            btn.pack(fill="x", expand=True)

            red_x_btn = tk.Button(
                frame,
                text="\u2716",
                bg=self.RED_X_BG,
                fg="white",
                font=(font, 12, "bold"),
                relief="flat",
                width=3,
                highlightthickness=0,
                command=lambda name=plugin_name: self.confirm_and_delete(name)
            )
            red_x_btn.pack(side="right", padx=(5, 0), pady=6)

    def toggle_plugin_selection(self, plugin_name):
        if plugin_name in self.selected_plugins:
            self.selected_plugins.remove(plugin_name)
        else:
            self.selected_plugins.add(plugin_name)

        for frame in self.plugin_button_frame.winfo_children():
            widgets = frame.winfo_children()
            if widgets:
                btn_container = widgets[0]
                btns = btn_container.winfo_children()
                if btns:
                    btn = btns[0]
                    if isinstance(btn, tk.Button):
                        name = btn.cget("text")
                        if name in self.selected_plugins:
                            btn.config(bg=self.BUTTON_SELECTED_BG)
                        else:
                            btn.config(bg=self.BUTTON_BG)

    def change_theme(self, theme_name):
        self.current_theme = theme_name
        self.theme_colors = ThemeManager.get_themes()[theme_name]
        self.settings["theme"] = theme_name
        ThemeManager.save_settings(self.settings)
        
        # Update colors
        self.apply_theme()
        
        # Recreate all widgets with new theme
        for widget in self.root.winfo_children():
            widget.destroy()
        self.create_widgets()

    def resize_plugin_frame(self, event):
        canvas_width = event.width
        self.canvas.itemconfig(self.plugin_button_frame_id, width=canvas_width)

    def update_scrollbar_visibility(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        canvas_height = self.canvas.winfo_height()
        frame_height = self.plugin_button_frame.winfo_height()

        if frame_height > canvas_height:
            self.scrollbar.pack(side="right", fill="y")
            self.canvas.configure(yscrollcommand=self.scrollbar.set)
        else:
            self.scrollbar.pack_forget()
            self.canvas.yview_moveto(0)
            self.canvas.configure(yscrollcommand=None)

    def _on_mousewheel(self, event):
        if self.scrollbar.winfo_ismapped():
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def confirm_and_delete(self, plugin_name):
        answer = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{plugin_name}'?")
        if answer:
            plugin_path = os.path.join(PLUGIN_DIR, f"{plugin_name}.py")
            try:
                os.remove(plugin_path)
                if plugin_name in self.selected_plugins:
                    self.selected_plugins.remove(plugin_name)
                self.refresh_plugin_buttons("TkDefaultFont")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete plugin '{plugin_name}':\n{e}")

    def open_featured_plugin_dialog(self):
        filepath = filedialog.askopenfilename(
            title="Select Featured Plugin to Add",
            initialdir=os.path.abspath(FEATURED_DIR),
            filetypes=[("Python Files", "*.py")]
        )
        if filepath:
            filename = os.path.basename(filepath)
            dest_path = os.path.join(PLUGIN_DIR, filename)
            try:
                shutil.copy(filepath, dest_path)
                self.refresh_plugin_buttons("TkDefaultFont")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to copy featured plugin:\n{e}")

    def launch_blank_window(self):
        if not self.selected_plugins:
            messagebox.showinfo("No Plugins Selected", "Please select one or more plugins to launch.")
            return

        win = tk.Toplevel(self.root)
        win.title("VokoToolkit - Plugins")
        win.geometry("800x600")
        win.configure(bg=self.BG_COLOR)
        win.minsize(600, 400)
        win.resizable(True, True)

        # Create main container for plugins using grid
        main_container = tk.Frame(win, bg=self.BG_COLOR)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Calculate layout based on number of plugins
        num_plugins = len(self.selected_plugins)
        if num_plugins == 1:
            rows, cols = 1, 1
        elif num_plugins == 2:
            rows, cols = 1, 2
        elif num_plugins <= 4:
            rows, cols = 2, 2
        elif num_plugins <= 6:
            rows, cols = 2, 3
        elif num_plugins <= 9:
            rows, cols = 3, 3
        else:
            rows, cols = 4, 4

        # Create a grid of frames that will enforce equal sizes
        grid_frames = []
        for row in range(rows):
            for col in range(cols):
                grid_frame = tk.Frame(main_container, bg=self.BG_COLOR)
                grid_frame.grid(row=row, column=col, sticky="nsew", padx=2, pady=2)
                grid_frames.append(grid_frame)

        # Configure grid weights for equal distribution
        for row in range(rows):
            main_container.grid_rowconfigure(row, weight=1, uniform="row")
        for col in range(cols):
            main_container.grid_columnconfigure(col, weight=1, uniform="col")

        # Create plugin containers inside each grid frame
        plugin_containers = []
        sorted_plugins = sorted(self.selected_plugins)
        for i, plugin_name in enumerate(sorted_plugins):
            if i >= len(grid_frames):
                break  # Shouldn't happen as we created enough grid frames
            
            # Create plugin container inside the grid frame
            container = PluginContainer(grid_frames[i], plugin_name, self.theme_colors)
            container.pack(fill="both", expand=True)
            plugin_containers.append((container, plugin_name))

        # Load plugins into their containers
        rubik_bold = "RubikBold" if "RubikBold" in tkfont.names() else "TkDefaultFont"
        font_used = (rubik_bold, 16, "bold")

        loaded_any = False
        for container, plugin_name in plugin_containers:
            plugin_path = os.path.join(PLUGIN_DIR, f"{plugin_name}.py")
            if os.path.exists(plugin_path):
                try:
                    module = self.load_plugin_module(plugin_name, plugin_path)
                    if hasattr(module, "register"):
                        # Pass the plugin container instead of the main window
                        plugin_frame = container.get_plugin_frame()
                        
                        # Set theme colors on the plugin frame
                        if hasattr(plugin_frame, 'theme_colors'):
                            plugin_frame.theme_colors = self.theme_colors
                        else:
                            setattr(plugin_frame, 'theme_colors', self.theme_colors)
                        
                        module.register(plugin_frame)
                        if module not in loaded_plugins:
                            loaded_plugins.append(module)
                        loaded_any = True
                except Exception as e:
                    messagebox.showerror("Plugin Load Error", f"Failed to load plugin '{plugin_name}':\n{e}")
                    # Add error message to the container
                    error_label = tk.Label(
                        container.get_plugin_frame(), 
                        text=f"Error loading plugin:\n{str(e)}", 
                        bg=self.theme_colors["container_bg"], 
                        fg=self.theme_colors["red_x_bg"], 
                        font=("TkDefaultFont", 10),
                        wraplength=200,
                        justify="center"
                    )
                    error_label.pack(expand=True, fill="both")
            else:
                messagebox.showwarning("Plugin Missing", f"Plugin file '{plugin_name}.py' not found.")
                # Add missing message to the container
                missing_label = tk.Label(
                    container.get_plugin_frame(), 
                    text="Plugin file not found", 
                    bg=self.theme_colors["container_bg"], 
                    fg=self.theme_colors["red_x_bg"], 
                    font=font_used
                )
                missing_label.pack(expand=True)

        if not loaded_any and not self.selected_plugins:
            label = tk.Label(main_container, text="Get A Plugin to Start", bg=self.BG_COLOR, fg=self.TEXT_FG, font=font_used)
            label.pack(expand=True)

    def load_plugin_module(self, name, path):
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module

    def open_settings_window(self):
        settings_win = tk.Toplevel(self.root)
        settings_win.title("Settings")
        settings_win.geometry("400x250")
        settings_win.configure(bg=self.BG_COLOR)
        settings_win.resizable(False, False)

        rubik_bold = "RubikBold" if "RubikBold" in tkfont.names() else "TkDefaultFont"
        label_font = (rubik_bold, 14, "bold")
        button_font = (rubik_bold, 12)

        label = tk.Label(settings_win, text="Settings", bg=self.BG_COLOR, fg=self.TEXT_FG, font=label_font)
        label.pack(pady=(15, 10))

        # Theme selection
        theme_frame = tk.Frame(settings_win, bg=self.BG_COLOR)
        theme_frame.pack(pady=10)

        theme_label = tk.Label(theme_frame, text="Theme:", bg=self.BG_COLOR, fg=self.TEXT_FG, font=button_font)
        theme_label.pack(side="left", padx=(0, 10))

        theme_var = tk.StringVar(value=self.current_theme)
        theme_dropdown = ttk.Combobox(theme_frame, textvariable=theme_var, values=["Midnight", "Dark", "Light", "Amethyst", "Navy", "Banana", "Autumn", "Forest", "Crimson", "Lily"], 
                                     state="readonly", width=12)
        theme_dropdown.pack(side="left")
        theme_dropdown.bind("<<ComboboxSelected>>", lambda e: self.change_theme(theme_var.get()))

        import_btn = ttk.Button(settings_win, text="Import Plugins", command=self.import_plugins)
        import_btn.pack(pady=10, ipadx=5, ipady=5)

        export_btn = ttk.Button(settings_win, text="Export Plugins", command=self.export_plugins)
        export_btn.pack(pady=10, ipadx=5, ipady=5)

    def copy_plugin_file(self, src_path):
        try:
            filename = os.path.basename(src_path)
            dest_path = os.path.join(PLUGIN_DIR, filename)
            shutil.copy2(src_path, dest_path)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy plugin file '{filename}':\n{e}")
            return False

    def extract_zip_plugins(self, zip_path):
        try:
            imported_any = False
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for file in zip_ref.namelist():
                    if file.endswith(".py") and not file.endswith("/"):
                        extracted_path = zip_ref.extract(file, PLUGIN_DIR)
                        imported_any = True
            return imported_any
        except Exception as e:
            messagebox.showerror("Error", f"Failed to extract zip file '{os.path.basename(zip_path)}':\n{e}")
            return False

    def import_plugins(self):
        paths = filedialog.askopenfilenames(
            title="Select Python or Zip files to import",
            filetypes=[
                ("Python and Zip files", "*.py *.zip"),
                ("Python files", "*.py"),
                ("Zip files", "*.zip"),
                ("All files", "*.*"),
            ],
        )
        if not paths:
            return

        imported_files_count = 0
        skipped_files = []

        for path in paths:
            ext = os.path.splitext(path)[1].lower()
            if ext == ".py":
                if self.copy_plugin_file(path):
                    imported_files_count += 1
            elif ext == ".zip":
                if self.extract_zip_plugins(path):
                    imported_files_count += 1
            else:
                skipped_files.append(os.path.basename(path))

        self.refresh_plugin_buttons("TkDefaultFont")

        msg = f"Imported {imported_files_count} file(s)." if imported_files_count > 0 else "No Python files were imported."
        if skipped_files:
            msg += "\nSkipped unsupported files:\n" + ", ".join(skipped_files)

        messagebox.showinfo("Import Result", msg)

    def export_plugins(self):
        try:
            import tempfile
            import datetime

            temp_dir = tempfile.mkdtemp()
            for filename in os.listdir(PLUGIN_DIR):
                if filename.endswith(".py"):
                    shutil.copy2(os.path.join(PLUGIN_DIR, filename), temp_dir)

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            zip_filename = f"voko_plugins_export_{timestamp}.zip"

            downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
            zip_path = os.path.join(downloads_path, zip_filename)

            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file in os.listdir(temp_dir):
                    full_path = os.path.join(temp_dir, file)
                    zipf.write(full_path, arcname=file)

            shutil.rmtree(temp_dir)

            messagebox.showinfo("Export Complete", f"Exported plugins to:\n{zip_path}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Failed to export plugins:\n{e}")

def main():
    global root
    root = tk.Tk()
    load_custom_font()
    app = PluginManagerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()