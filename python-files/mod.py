import os
import sys
import json
import shutil
import base64
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class MinecraftModManager:
    """
    A GUI application to easily manage Minecraft mods and profiles,
    ready to be packaged as a standalone executable.
    """
    APP_NAME = "MinecraftModManager"

    def __init__(self, root):
        self.root = root
        self.root.title("Minecraft Mod Manager")
        self.root.geometry("850x650")
        self.root.minsize(750, 550)

        # --- Set App Icon ---
        self.set_app_icon()

        # --- Setup Robust Paths ---
        self.setup_paths()

        # --- Data ---
        self.config = self.load_config()
        self.minecraft_path = tk.StringVar(value=self.config.get("minecraft_path", ""))
        self.mods_path = ""
        self.update_mods_path()

        # Ensure the mod library directory exists
        if not os.path.exists(self.mod_library_dir):
            os.makedirs(self.mod_library_dir)

        # --- UI Setup ---
        self.create_styles()
        self.create_widgets()
        self.populate_lists()
        self.populate_profiles_dropdown()

    def set_app_icon(self):
        """Sets the application icon from base64 data."""
        try:
            # A simple grass block icon encoded in base64
            icon_data = base64.b64decode(
                'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6QAAAARnQU1BAACx'
                'jwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAARJSURBVFhHzZdrTBxVFMd/59x7p5SS9AotkEAt'
                'tYCiFeSDRFEgYARBEFFECKjxwIMQU4wXjA8aE4mJxp/Ggw/GPxjjgScgGo1GoxFpEW0pIlQptdAe'
                '6G13Znef40hL2y1sO0kf/MnNzJ2595z/Of9/5zA0TfO/D0CgdM6wQ/Ps3QzFksmYj7/9+7Pz4PzE'
                '3M2P9w9J501E8P71r34E7M1PzD35+r6l/dVV1c2HhE9a3S6b328MhD8nE/j+5/s/Xr349v0H01mH'
                's370JQDw7Yf7D03fP9++f3/15t3/vj/g1+bNt11Wp10+XgKAFx9+/3Hq5ccf/zL28MMPp1/+eB3R'
                '9Qx1hYI69O0JAEwGgu/e/+Xlhz9dvvj23Y9/vvzu9t3/Xm+dO+Nn0+n0FpY+hAsA4D9+/PDs7Udn'
                'b3+4eu3a1etfb978s/bqdZ0gIJCfzy8sLMzk5GSrI2w6nQ8fPvzo4UeHDx8+dM9/wP/+3PzD1avX'
                'v/v55/2vP+9/3bx56/Wrl7/95S+Xz549++DBg4mJiWPGjGFpaSkzMzM4HA5BEAhBEAQ+nw9BEOD3'
                '+/P5fMVisWQyOTg4aM3y8vJFixYlJydv3Ljx0qVLzc3NFRUVrVZrp9M5bNiwVatWqampI0eOzM7O'
                'Dhw4UFFRkZSUFBQUdPfu3ZSUlCVLlixbtmz58uXT0tKSn5+/YsWK1atXz5kzp6SkhMvlGj9+/P79'
                '+y0tLeXl5fX19bNnzx47duza1auXLFmSnZ39559/joyM3L9/v6Gh4ciRI7t37y4qKmJpaTls2LBl'
                'y5bt3r17xYoVM2fOnDlzRkdH4/P5ubm54eHhgwYNcnNz+/r6RkdHOxwO3W7Xtu3AgQMaGhrS09N/'
                '/fXXJUuWLF++fM6cOXPmzJkyZUrFihU9PT3z8/O5XC4IgsOHDx8+fNjR0dHX1zdsbW3t7e0dHR0d'
                'HR0dHR3RNC0Igv3790+bNm3MmDEqlcodO3bs3r1bURSxWEwQBMVicWhoKBqNhqZpaZrmer1erVYN'
                'DAzMzMycnJx0Oh2eJ+bzeW1tbWNjY1dX19zc3NbW1tbW1t7eHh4e7u3tRTAYnDhx4vTp0wMGDGho'
                'aAgODh4xYsSuXbukpKT4fL4sy/l8vqurq6Ghoaen59ChQ5qmIUmSNE3TNHV3d7/44osLFy5cvXp1'
                'WlpaRkZGVlaWLMvFYlFcXNzEiROXLFmyZMmSoqIiy7KGYfD5fF6v12q1dnd35+bmNjQ0DA8Pf/75'
                '56dOnQqC4Pjx4w8fPuxwOHw+HyFXRkZGZmZmTqeTpunl5eXq6mpnZ2chZ3d3NwRB8vv9kGU5nU5P'
                'T09/f/9FixZNnDgRBARB8DwPhmEIIYQQAwMDhw8f7ujoGB0djaIoDodDXV3da6+95nK5tm37+uuv'
                'b9++ff369fPmzdu/f/8PP/xw8+bNo0ePnjx58uzZsxMnTpw1a9a4ceNMnTp1zpw5CxcuPHny5MiR'
                'I9PT0y9evNi3b9/NmzcPHjy4ffv2rVu3Ll68eOHChUuXLp02bVplZWXx8fGpqanr169PTU0dOXLk'
                'woUL169fX11dvW3btoGBgZqaGo7jBEG6u7tDQ0N9fX2jY1qmL+q6Pmv7M/M3j0Mh0LgAAAAASUVO'
                'RK5CYII='
            )
            photo = tk.PhotoImage(data=icon_data)
            self.root.iconphoto(False, photo)
        except Exception as e:
            print(f"Could not set icon: {e}")

    def setup_paths(self):
        """Creates and sets paths for config and mod library in the user's app data directory."""
        if sys.platform == "win32":
            app_data_path = os.getenv('APPDATA')
        elif sys.platform == "darwin":
            app_data_path = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support')
        else: # Linux
            app_data_path = os.path.join(os.path.expanduser('~'), '.config')

        self.config_dir = os.path.join(app_data_path, self.APP_NAME)
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)

        self.config_file = os.path.join(self.config_dir, "config.json")
        self.mod_library_dir = os.path.join(self.config_dir, "mod_library")

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
        path_frame.pack(fill='x', side='top', pady=(5,0))
        ttk.Label(path_frame, text="Minecraft Path:").pack(side='left', padx=(0, 5))
        path_entry = ttk.Entry(path_frame, textvariable=self.minecraft_path)
        path_entry.pack(side='left', fill='x', expand=True, padx=5)
        browse_button = ttk.Button(path_frame, text="Browse...", command=self.select_minecraft_path)
        browse_button.pack(side='left', padx=5)

        # --- Main Frame for Mod Lists ---
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, pady=5)
        main_frame.column_configure(0, weight=1)
        main_frame.column_configure(1, weight=0)
        main_frame.column_configure(2, weight=1)
        main_frame.row_configure(1, weight=1)

        # Mod Library (Left Side)
        ttk.Label(main_frame, text="Mod Library", style="Header.TLabel").grid(row=0, column=0, pady=(0, 5), sticky='w')
        lib_frame = ttk.Frame(main_frame, relief="sunken", borderwidth=1)
        lib_frame.grid(row=1, column=0, sticky='nsew', padx=(0, 5))
        self.lib_listbox = tk.Listbox(lib_frame, selectmode='extended', bg="#f0f0f0", bd=0, highlightthickness=0, font=('Segoe UI', 10))
        self.lib_listbox.pack(fill='both', expand=True, padx=5, pady=5)
        self.lib_listbox.bind("<Button-3>", self.show_context_menu)

        # Control Buttons (Middle)
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=1, sticky='ns', padx=10)
        ttk.Button(button_frame, text=">>", command=self.install_all, width=4).pack(pady=5, fill='x')
        ttk.Button(button_frame, text=" > ", command=self.install_selected, width=4).pack(pady=5, fill='x')
        ttk.Button(button_frame, text=" < ", command=self.uninstall_selected, width=4).pack(pady=5, fill='x')
        ttk.Button(button_frame, text="<<", command=self.uninstall_all, width=4).pack(pady=5, fill='x')

        # Active Mods (Right Side)
        ttk.Label(main_frame, text="Active Mods", style="Header.TLabel").grid(row=0, column=2, pady=(0, 5), sticky='w')
        active_frame = ttk.Frame(main_frame, relief="sunken", borderwidth=1)
        active_frame.grid(row=1, column=2, sticky='nsew', padx=(5, 0))
        self.active_listbox = tk.Listbox(active_frame, selectmode='extended', bg="#f0f0f0", bd=0, highlightthickness=0, font=('Segoe UI', 10))
        self.active_listbox.pack(fill='both', expand=True, padx=5, pady=5)
        self.active_listbox.bind("<Button-3>", self.show_context_menu)

        # --- Utility Frame for Refresh/Open ---
        util_frame = ttk.Frame(self.root)
        util_frame.pack(fill='x', side='bottom', pady=5)
        ttk.Button(util_frame, text="Refresh Lists", command=self.populate_lists).pack(side='left', padx=(0, 10))
        ttk.Button(util_frame, text="Open Library Folder", command=self.open_library_folder).pack(side='left')
        ttk.Button(util_frame, text="Open Mods Folder", command=self.open_mods_folder).pack(side='right')

        # --- Bottom Frame for Profiles ---
        profile_frame = ttk.Frame(self.root)
        profile_frame.pack(fill='x', side='bottom', pady=(5, 10))
        ttk.Label(profile_frame, text="Mod Profiles:", font=('Segoe UI', 11, 'bold')).pack(side='left')
        self.profile_name_entry = ttk.Entry(profile_frame)
        self.profile_name_entry.pack(side='left', padx=10, fill='x', expand=True)
        ttk.Button(profile_frame, text="Save Current", command=self.save_profile).pack(side='left')
        self.profile_var = tk.StringVar()
        self.profile_dropdown = ttk.Combobox(profile_frame, textvariable=self.profile_var, state='readonly', width=20)
        self.profile_dropdown.pack(side='left', padx=10)
        ttk.Button(profile_frame, text="Load Profile", command=self.load_profile).pack(side='left')
        ttk.Button(profile_frame, text="Delete Profile", command=self.delete_profile).pack(side='left', padx=10)

    # --- Core Logic Functions ---

    def get_default_minecraft_path(self):
        """Returns the default .minecraft path based on the OS."""
        if sys.platform == "win32":
            return os.path.join(os.getenv('APPDATA'), '.minecraft')
        elif sys.platform == "darwin":
            return os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'minecraft')
        else:
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
        for listbox in [self.lib_listbox, self.active_listbox]:
            listbox.delete(0, 'end')

        # Populate library list
        for item in sorted(os.listdir(self.mod_library_dir)):
            if item.endswith(('.jar', '.jar.disabled')):
                self.lib_listbox.insert('end', item)
                if item.endswith('.disabled'):
                    self.lib_listbox.itemconfig('end', {'fg': 'grey'})

        # Populate active mods list
        self.update_mods_path()
        if self.mods_path and os.path.exists(self.mods_path):
            for item in sorted(os.listdir(self.mods_path)):
                if item.endswith(('.jar', '.jar.disabled')):
                    self.active_listbox.insert('end', item)
                    if item.endswith('.disabled'):
                        self.active_listbox.itemconfig('end', {'fg': 'grey'})

    def move_mods(self, mods_to_move, source_folder, dest_folder):
        """Helper function to move a list of mods between folders."""
        if not self.minecraft_path.get() or not self.mods_path:
            messagebox.showerror("Error", "Minecraft path is not set correctly.")
            return
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)
        for mod_name in mods_to_move:
            try:
                shutil.move(os.path.join(source_folder, mod_name), os.path.join(dest_folder, mod_name))
            except Exception as e:
                messagebox.showerror("Move Error", f"Could not move {mod_name}.\nError: {e}")
        self.populate_lists()

    def install_selected(self):
        selected_indices = self.lib_listbox.curselection()
        mods_to_install = [self.lib_listbox.get(i) for i in selected_indices]
        self.move_mods(mods_to_install, self.mod_library_dir, self.mods_path)

    def uninstall_selected(self):
        selected_indices = self.active_listbox.curselection()
        mods_to_uninstall = [self.active_listbox.get(i) for i in selected_indices]
        self.move_mods(mods_to_uninstall, self.mods_path, self.mod_library_dir)
        
    def install_all(self):
        self.move_mods(list(self.lib_listbox.get(0, 'end')), self.mod_library_dir, self.mods_path)

    def uninstall_all(self):
        self.move_mods(list(self.active_listbox.get(0, 'end')), self.mods_path, self.mod_library_dir)

    # --- Right-Click Context Menu & Actions ---

    def show_context_menu(self, event):
        """Displays a context menu on right-click."""
        listbox = event.widget
        if not listbox.curselection():
            return
            
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="Enable Selected", command=lambda: self.toggle_mods_state(listbox, enable=True))
        context_menu.add_command(label="Disable Selected", command=lambda: self.toggle_mods_state(listbox, enable=False))
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    def toggle_mods_state(self, listbox, enable):
        """Enables or disables selected mods by renaming them."""
        base_path = self.mod_library_dir if listbox is self.lib_listbox else self.mods_path
        if not base_path: return

        selected_indices = listbox.curselection()
        for i in selected_indices:
            mod_name = listbox.get(i)
            new_name = ""
            if enable and mod_name.endswith(".jar.disabled"):
                new_name = mod_name.replace(".jar.disabled", ".jar")
            elif not enable and mod_name.endswith(".jar"):
                new_name = mod_name + ".disabled"
            
            if new_name:
                try:
                    os.rename(os.path.join(base_path, mod_name), os.path.join(base_path, new_name))
                except Exception as e:
                    messagebox.showerror("Rename Error", f"Could not rename {mod_name}.\nError: {e}")
        self.populate_lists()

    # --- Utility Button Actions ---
    
    def open_folder(self, path):
        """Opens a given path in the default file explorer."""
        if not path or not os.path.exists(path):
            messagebox.showwarning("Warning", f"Path does not exist:\n{path}")
            return
        try:
            if sys.platform == 'win32':
                os.startfile(path)
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', path])
            else:
                subprocess.Popen(['xdg-open', path])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder.\nError: {e}")

    def open_library_folder(self):
        self.open_folder(self.mod_library_dir)

    def open_mods_folder(self):
        self.open_folder(self.mods_path)

    # --- Profile Management ---
    
    def populate_profiles_dropdown(self):
        profiles = list(self.config.get("profiles", {}).keys())
        self.profile_dropdown['values'] = sorted(profiles)
        self.profile_var.set("")

    def save_profile(self):
        profile_name = self.profile_name_entry.get().strip()
        if not profile_name:
            messagebox.showwarning("Warning", "Please enter a name for the profile.")
            return
        active_mods = [mod for mod in self.active_listbox.get(0, 'end') if mod.endswith('.jar')]
        if not active_mods:
            if not messagebox.askyesno("Info", "No enabled mods are active. Save an empty profile?"):
                return
        if "profiles" not in self.config: self.config["profiles"] = {}
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
        self.uninstall_all()
        profile_mods = self.config.get("profiles", {}).get(profile_name, [])
        self.move_mods(profile_mods, self.mod_library_dir, self.mods_path)
        messagebox.showinfo("Success", f"Profile '{profile_name}' loaded.")

    def delete_profile(self):
        profile_name = self.profile_var.get()
        if not profile_name:
            messagebox.showwarning("Warning", "Please select a profile to delete.")
            return
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete profile '{profile_name}'?"):
            if "profiles" in self.config and profile_name in self.config["profiles"]:
                del self.config["profiles"][profile_name]
                self.save_config()
                self.populate_profiles_dropdown()
                messagebox.showinfo("Success", f"Profile '{profile_name}' deleted.")

    # --- Config Management ---

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {"minecraft_path": self.get_default_minecraft_path()}
        return {"minecraft_path": self.get_default_minecraft_path()}

    def save_config(self):
        self.config["minecraft_path"] = self.minecraft_path.get()
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)


if __name__ == "__main__":
    root = tk.Tk()
    app = MinecraftModManager(root)
    root.mainloop()

