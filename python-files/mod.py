import os
import sys
import json
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class MinecraftModManager:
    """
    A GUI application to easily manage Minecraft mods and profiles.
    """
    CONFIG_FILE = "mod_manager_config.json"
    MOD_LIBRARY_DIR = "mod_library"

    def __init__(self, root):
        self.root = root
        self.root.title("Minecraft Mod Manager")
        self.root.geometry("850x600")
        self.root.minsize(700, 500)

        # --- Data ---
        self.config = self.load_config()
        self.minecraft_path = tk.StringVar(value=self.config.get("minecraft_path", ""))
        self.mods_path = ""
        self.update_mods_path()

        # Ensure the mod library directory exists
        if not os.path.exists(self.MOD_LIBRARY_DIR):
            os.makedirs(self.MOD_LIBRARY_DIR)

        # --- UI Setup ---
        self.create_styles()
        self.create_widgets()
        self.populate_lists()
        self.populate_profiles_dropdown()

    def create_styles(self):
        """Creates custom styles for the ttk widgets."""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TLabel", padding=5, font=('Segoe UI', 10))
        style.configure("TButton", padding=5, font=('Segoe UI', 10, 'bold'))
        style.configure("TFrame", padding=10)
        style.configure("Header.TLabel", font=('Segoe UI', 14, 'bold'))
        style.configure("TMenubutton", font=('Segoe UI', 10))

    def create_widgets(self):
        """Creates and arranges all the UI elements in the window."""
        # --- Top Frame for Minecraft Path ---
        path_frame = ttk.Frame(self.root, padding=10)
        path_frame.pack(fill='x', side='top')

        ttk.Label(path_frame, text="Minecraft Path:").pack(side='left', padx=(0, 5))
        path_entry = ttk.Entry(path_frame, textvariable=self.minecraft_path)
        path_entry.pack(side='left', fill='x', expand=True, padx=5)
        browse_button = ttk.Button(path_frame, text="Browse...", command=self.select_minecraft_path)
        browse_button.pack(side='left', padx=5)

        # --- Main Frame for Mod Lists ---
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, pady=5)
        main_frame.column_configure(0, weight=1)
        main_frame.column_configure(1, weight=0) # For buttons
        main_frame.column_configure(2, weight=1)
        main_frame.row_configure(1, weight=1)

        # Mod Library (Left Side)
        ttk.Label(main_frame, text="Mod Library", style="Header.TLabel").grid(row=0, column=0, pady=(0, 5), sticky='w')
        lib_frame = ttk.Frame(main_frame, relief="sunken", borderwidth=1)
        lib_frame.grid(row=1, column=0, sticky='nsew', padx=(0, 5))
        self.lib_listbox = tk.Listbox(lib_frame, selectmode='extended', bg="#f0f0f0", bd=0, highlightthickness=0)
        self.lib_listbox.pack(fill='both', expand=True, padx=5, pady=5)

        # Control Buttons (Middle)
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=1, sticky='ns', padx=10)
        ttk.Button(button_frame, text=">>", command=self.install_all).pack(pady=5, fill='x')
        ttk.Button(button_frame, text=" > ", command=self.install_selected).pack(pady=5, fill='x')
        ttk.Button(button_frame, text=" < ", command=self.uninstall_selected).pack(pady=5, fill='x')
        ttk.Button(button_frame, text="<<", command=self.uninstall_all).pack(pady=5, fill='x')

        # Active Mods (Right Side)
        ttk.Label(main_frame, text="Active Mods", style="Header.TLabel").grid(row=0, column=2, pady=(0, 5), sticky='w')
        active_frame = ttk.Frame(main_frame, relief="sunken", borderwidth=1)
        active_frame.grid(row=1, column=2, sticky='nsew', padx=(5, 0))
        self.active_listbox = tk.Listbox(active_frame, selectmode='extended', bg="#f0f0f0", bd=0, highlightthickness=0)
        self.active_listbox.pack(fill='both', expand=True, padx=5, pady=5)

        # --- Bottom Frame for Profiles ---
        profile_frame = ttk.Frame(self.root)
        profile_frame.pack(fill='x', side='bottom', pady=(5, 10))
        ttk.Label(profile_frame, text="Mod Profiles:", font=('Segoe UI', 11, 'bold')).pack(side='left')
        
        self.profile_name_entry = ttk.Entry(profile_frame)
        self.profile_name_entry.pack(side='left', padx=10)
        ttk.Button(profile_frame, text="Save Current", command=self.save_profile).pack(side='left')

        self.profile_var = tk.StringVar()
        self.profile_dropdown = ttk.Combobox(profile_frame, textvariable=self.profile_var, state='readonly')
        self.profile_dropdown.pack(side='left', padx=10)

        ttk.Button(profile_frame, text="Load Profile", command=self.load_profile).pack(side='left')
        ttk.Button(profile_frame, text="Delete Profile", command=self.delete_profile).pack(side='left', padx=10)

    # --- Core Logic Functions ---

    def get_default_minecraft_path(self):
        """Returns the default .minecraft path based on the OS."""
        if sys.platform == "win32":
            return os.path.join(os.getenv('APPDATA'), '.minecraft')
        elif sys.platform == "darwin": # macOS
            return os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'minecraft')
        else: # Linux
            return os.path.join(os.path.expanduser('~'), '.minecraft')

    def select_minecraft_path(self):
        """Opens a dialog to select the .minecraft directory."""
        initial_dir = self.minecraft_path.get() or self.get_default_minecraft_path()
        path = filedialog.askdirectory(title="Select .minecraft Folder", initialdir=initial_dir)
        if path:
            self.minecraft_path.set(path)
            self.update_mods_path()
            self.save_config()
            self.populate_lists()

    def update_mods_path(self):
        """Updates the mods_path variable based on the minecraft_path."""
        mc_path = self.minecraft_path.get()
        if mc_path and os.path.isdir(mc_path):
            self.mods_path = os.path.join(mc_path, "mods")
        else:
            self.mods_path = ""

    def populate_lists(self):
        """Scans the library and active mods folders and updates the listboxes."""
        self.lib_listbox.delete(0, 'end')
        self.active_listbox.delete(0, 'end')

        # Populate library list
        for item in sorted(os.listdir(self.MOD_LIBRARY_DIR)):
            if item.endswith(('.jar', '.disabled')):
                self.lib_listbox.insert('end', item)

        # Populate active mods list
        self.update_mods_path()
        if self.mods_path and os.path.exists(self.mods_path):
            for item in sorted(os.listdir(self.mods_path)):
                if item.endswith(('.jar', '.disabled')):
                    self.active_listbox.insert('end', item)

    def move_mods(self, mods_to_move, source_folder, dest_folder):
        """Helper function to move a list of mods between folders."""
        if not self.minecraft_path.get():
            messagebox.showerror("Error", "Minecraft path is not set.")
            return
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)
            
        for mod_name in mods_to_move:
            source_path = os.path.join(source_folder, mod_name)
            dest_path = os.path.join(dest_folder, mod_name)
            try:
                shutil.move(source_path, dest_path)
            except Exception as e:
                messagebox.showerror("Move Error", f"Could not move {mod_name}.\nError: {e}")
        self.populate_lists()

    def install_selected(self):
        selected_indices = self.lib_listbox.curselection()
        mods_to_install = [self.lib_listbox.get(i) for i in selected_indices]
        self.move_mods(mods_to_install, self.MOD_LIBRARY_DIR, self.mods_path)

    def uninstall_selected(self):
        selected_indices = self.active_listbox.curselection()
        mods_to_uninstall = [self.active_listbox.get(i) for i in selected_indices]
        self.move_mods(mods_to_uninstall, self.mods_path, self.MOD_LIBRARY_DIR)
        
    def install_all(self):
        all_mods = list(self.lib_listbox.get(0, 'end'))
        self.move_mods(all_mods, self.MOD_LIBRARY_DIR, self.mods_path)

    def uninstall_all(self):
        all_mods = list(self.active_listbox.get(0, 'end'))
        self.move_mods(all_mods, self.mods_path, self.MOD_LIBRARY_DIR)

    # --- Profile Management ---
    
    def populate_profiles_dropdown(self):
        """Updates the profiles dropdown with saved profiles."""
        profiles = list(self.config.get("profiles", {}).keys())
        self.profile_dropdown['values'] = sorted(profiles)
        if profiles:
            self.profile_var.set(sorted(profiles)[0])
        else:
            self.profile_var.set("")

    def save_profile(self):
        profile_name = self.profile_name_entry.get().strip()
        if not profile_name:
            messagebox.showwarning("Warning", "Please enter a name for the profile.")
            return

        active_mods = list(self.active_listbox.get(0, 'end'))
        if not active_mods:
            messagebox.showinfo("Info", "No active mods to save in profile.")
            return

        if "profiles" not in self.config:
            self.config["profiles"] = {}
        
        self.config["profiles"][profile_name] = active_mods
        self.save_config()
        self.populate_profiles_dropdown()
        self.profile_name_entry.delete(0, 'end')
        messagebox.showinfo("Success", f"Profile '{profile_name}' saved successfully.")

    def load_profile(self):
        profile_name = self.profile_var.get()
        if not profile_name:
            messagebox.showwarning("Warning", "Please select a profile to load.")
            return
            
        if not messagebox.askyesno("Confirm Load", f"This will replace all active mods with the '{profile_name}' profile.\nAre you sure?"):
            return

        # First, uninstall all current mods
        self.uninstall_all()
        
        # Then, install mods from the selected profile
        profile_mods = self.config.get("profiles", {}).get(profile_name, [])
        self.move_mods(profile_mods, self.MOD_LIBRARY_DIR, self.mods_path)
        messagebox.showinfo("Success", f"Profile '{profile_name}' loaded.")

    def delete_profile(self):
        profile_name = self.profile_var.get()
        if not profile_name:
            messagebox.showwarning("Warning", "Please select a profile to delete.")
            return
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the profile '{profile_name}'?"):
            if "profiles" in self.config and profile_name in self.config["profiles"]:
                del self.config["profiles"][profile_name]
                self.save_config()
                self.populate_profiles_dropdown()
                messagebox.showinfo("Success", f"Profile '{profile_name}' deleted.")

    # --- Config Management ---

    def load_config(self):
        """Loads the configuration from a JSON file."""
        if os.path.exists(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, 'r') as f:
                return json.load(f)
        # Set a default path if no config exists
        return {"minecraft_path": self.get_default_minecraft_path()}

    def save_config(self):
        """Saves the current configuration to a JSON file."""
        self.config["minecraft_path"] = self.minecraft_path.get()
        with open(self.CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=4)


if __name__ == "__main__":
    root = tk.Tk()
    app = MinecraftModManager(root)
    root.mainloop()
