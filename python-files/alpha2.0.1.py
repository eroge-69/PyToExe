import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, filedialog
import threading
import subprocess
import minecraft_launcher_lib as mc
import minecraft_launcher_lib.microsoft_account as mc_microsoft_account
import os
import json
import requests
from datetime import datetime
import shutil
import re
import sys
import time

# --- GLOBAL CONFIGURATIONS & PATHS ---
# Using os.path.expanduser('~') for cross-platform home directory detection
MC_DIR = os.path.join(os.path.expanduser('~'), ".minecraft")
os.makedirs(MC_DIR, exist_ok=True) # Ensure the default .minecraft directory exists

LAUNCHER_DATA_DIR = os.path.join(os.path.expanduser('~'), ".dark_aero_launcher")
os.makedirs(LAUNCHER_DATA_DIR, exist_ok=True) # Directory for launcher-specific data

AUTH_FILE = os.path.join(LAUNCHER_DATA_DIR, "auth_data.json") # Stores Microsoft auth tokens
CONFIG_FILE = os.path.join(LAUNCHER_DATA_DIR, "launcher_config.json") # Stores launcher settings

DEFAULT_GAME_DIR = MC_DIR # Default to .minecraft if not overridden

# --- CustomTKinter Global Appearance Settings (Initial setup) ---
# These will be overridden by loaded config in __init__
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# --- DPI Scaling (Optional but Recommended for High-DPI Screens) ---
# try:
#     ctk.set_widget_scaling(1.0)
#     ctk.set_window_scaling(1.0)
#     ctk.set_appearance_mode("System") # Modes: "System" (standard), "Dark", "Light"
#     ctk.set_default_color_theme("blue") # Themes: "blue" (standard), "dark-blue", "green"
# except Exception as e:
#     print(f"CustomTkinter scaling/theme error (may not support older versions): {e}")


class LauncherUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("DarkAero Launcher Alpha 2.0.0")
        self.geometry("900x600")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Configure grid layout
        self.grid_columnconfigure(0, weight=0) # Sidebar
        self.grid_columnconfigure(1, weight=1) # Main content area
        self.grid_rowconfigure(0, weight=1) # All rows within the main window

        # --- Sidebar (Frame) ---
        self.sidebar_frame = ctk.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1) # For status log to push down

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="DarkAero Launcher", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=20)

        self.login_button = ctk.CTkButton(self.sidebar_frame, text="Login to Microsoft", command=self.login_microsoft_account)
        self.login_button.grid(row=1, column=0, padx=20, pady=10)

        self.logout_button = ctk.CTkButton(self.sidebar_frame, text="Logout", command=self.logout_account, fg_color="red", hover_color="#8B0000")
        self.logout_button.grid(row=2, column=0, padx=20, pady=10)

        self.settings_button = ctk.CTkButton(self.sidebar_frame, text="Settings", command=self.open_settings)
        self.settings_button.grid(row=3, column=0, padx=20, pady=10)

        # Status Log at the bottom of the sidebar
        self.status_log_label = ctk.CTkLabel(self.sidebar_frame, text="Status Log:", font=ctk.CTkFont(weight="bold"))
        self.status_log_label.grid(row=4, column=0, padx=20, pady=(10, 5), sticky="sw")
        self.status_log_text = ctk.CTkTextbox(self.sidebar_frame, height=150, wrap="word", state="disabled")
        self.status_log_text.grid(row=5, column=0, padx=10, pady=(0, 10), sticky="nsew")

        # --- Main Content Area (Tabview) ---
        self.tabview = ctk.CTkTabview(self, segmented_button_fg_color=("white", "#1b1b1b"))
        self.tabview.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # --- Play Tab ---
        self.play_tab = self.tabview.add("Play")
        self.play_tab.grid_columnconfigure(0, weight=1)
        self.play_tab.grid_rowconfigure((0,1,2,3,4,5,6), weight=0) # Content rows
        self.play_tab.grid_rowconfigure(7, weight=1) # For padding at bottom

        self.version_label = ctk.CTkLabel(self.play_tab, text="Select Version:")
        self.version_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")
        self.version_optionmenu = ctk.CTkOptionMenu(self.play_tab, values=["Loading..."])
        self.version_optionmenu.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        self.instance_label = ctk.CTkLabel(self.play_tab, text="Select Instance:")
        self.instance_label.grid(row=2, column=0, padx=10, pady=(10, 0), sticky="w")
        self.instance_dropdown = ctk.CTkOptionMenu(self.play_tab, values=["default"])
        self.instance_dropdown.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        self.add_instance_entry = ctk.CTkEntry(self.play_tab, placeholder_text="New Instance Name")
        self.add_instance_entry.grid(row=4, column=0, padx=10, pady=(10, 5), sticky="ew")
        self.add_instance_button = ctk.CTkButton(self.play_tab, text="Add Instance", command=self.add_new_instance)
        self.add_instance_button.grid(row=5, column=0, padx=10, pady=5, sticky="w")

        self.launch_button = ctk.CTkButton(self.play_tab, text="Launch Minecraft", command=self.launch_minecraft, fg_color="green", hover_color="#006400")
        self.launch_button.grid(row=6, column=0, padx=10, pady=20, sticky="ew")

        # --- Console Tab ---
        self.console_tab = self.tabview.add("Console")
        self.console_tab.grid_columnconfigure(0, weight=1)
        self.console_tab.grid_rowconfigure(0, weight=1)
        self.console_output = ctk.CTkTextbox(self.console_tab, wrap="word", state="disabled")
        self.console_output.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # --- Initial Setup ---
        self.minecraft_versions = []
        self.instance_list = ["default"] # Default instance
        self.selected_account = None # Stores logged-in account data

        # --- Configuration Variables (Existing and New) ---
        self.ram_allocation = 2048 # Default Max RAM in MB (2GB)
        self.offline_mode_enabled = False
        self.offline_username = "Player" # Default offline username
        self.auto_restart_on_crash = False

        # --- NEW: Additional Configuration Variables ---
        self.min_ram_allocation = 512 # Minimum RAM in MB
        self.custom_jvm_arguments = ""
        self.use_native_libraries = True
        self.custom_java_path = "" # Empty means auto-detect

        self.resolution_width = 854 # Default Minecraft window width
        self.resolution_height = 480 # Default Minecraft window height
        self.fullscreen_mode = False
        self.server_ip_on_launch = ""
        self.game_directory_override = "" # Empty means use instance_directory
        self.enable_custom_game_arguments = False
        self.custom_game_arguments = ""

        self.close_launcher_on_game_start = False
        self.auto_update_launcher = True # Placeholder, actual update logic not covered here
        self.show_console_on_launch = True # Currently always shows, setting for future
        self.theme_mode = "System" # System, Dark, Light
        self.color_theme = "blue" # blue, dark-blue, green
        self.download_server_jars = False # For server hosting feature
        self.show_snapshots_betas = False # Whether to show snapshot/beta versions in the dropdown
        self.custom_assets_root = "" # For custom assets directory
        self.keep_launcher_open_on_game_start = True # Mutually exclusive with close_launcher_on_game_start
        # --- END NEW ---

        self.load_config() # This will load all settings including new ones
        self.load_auth_data()

        # Apply initial theme settings from config
        ctk.set_appearance_mode(self.theme_mode)
        ctk.set_default_color_theme(self.color_theme)

        self.populate_instance_dropdown()
        self.check_login_status()
        self.update_version_list() # This will now consider show_snapshots_betas

    def on_closing(self):
        """Handle window close event."""
        self.log_status("Closing DarkAero Launcher...", level="info")
        self.save_auth_data() # Save auth data on close
        self.save_config() # Save configuration on close
        self.destroy() # Close the main window

    def log_status(self, message, level="info"):
        """Log status messages to the UI textbox and console."""
        timestamp = datetime.now().strftime("[%H:%M:%S]")
        colored_message = f"{timestamp} [{level.upper()}] {message}\n"

        self.status_log_text.configure(state="normal")
        self.status_log_text.insert(tk.END, colored_message)
        self.status_log_text.see(tk.END) # Auto-scroll to the end
        self.status_log_text.configure(state="disabled")

        # Also print to standard output for debugging
        print(colored_message.strip())

    def log_console_output(self, message):
        """Log Minecraft console output to the Console tab."""
        self.console_output.configure(state="normal")
        self.console_output.insert(tk.END, message)
        self.console_output.see(tk.END) # Auto-scroll to the end
        self.console_output.configure(state="disabled")

    def custom_input_dialog(self, title, prompt):
        """Creates a custom input dialog for user input."""
        dialog = ctk.CTkInputDialog(text=prompt, title=title)
        return dialog.get_input()

    def load_config(self):
        """Loads launcher configuration from file."""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    self.instance_list = config.get("instance_list", ["default"])
                    self.ram_allocation = config.get("ram_allocation", 2048)
                    self.offline_mode_enabled = config.get("offline_mode_enabled", False)
                    self.offline_username = config.get("offline_username", "Player")
                    self.auto_restart_on_crash = config.get("auto_restart_on_crash", False)

                    # --- NEW: Load all additional settings ---
                    self.min_ram_allocation = config.get("min_ram_allocation", 512)
                    self.custom_jvm_arguments = config.get("custom_jvm_arguments", "")
                    self.use_native_libraries = config.get("use_native_libraries", True)
                    self.custom_java_path = config.get("custom_java_path", "")

                    self.resolution_width = config.get("resolution_width", 854)
                    self.resolution_height = config.get("resolution_height", 480)
                    self.fullscreen_mode = config.get("fullscreen_mode", False)
                    self.server_ip_on_launch = config.get("server_ip_on_launch", "")
                    self.game_directory_override = config.get("game_directory_override", "")
                    self.enable_custom_game_arguments = config.get("enable_custom_game_arguments", False)
                    self.custom_game_arguments = config.get("custom_game_arguments", "")

                    self.close_launcher_on_game_start = config.get("close_launcher_on_game_start", False)
                    self.auto_update_launcher = config.get("auto_update_launcher", True)
                    self.show_console_on_launch = config.get("show_console_on_launch", True)
                    self.theme_mode = config.get("theme_mode", "System")
                    self.color_theme = config.get("color_theme", "blue")
                    self.download_server_jars = config.get("download_server_jars", False)
                    self.show_snapshots_betas = config.get("show_snapshots_betas", False)
                    self.custom_assets_root = config.get("custom_assets_root", "")
                    self.keep_launcher_open_on_game_start = config.get("keep_launcher_open_on_game_start", True)
                    # --- END NEW ---

                    self.log_status("Launcher configuration loaded.", level="success")
            except json.JSONDecodeError as e:
                self.log_status(f"Error loading launcher configuration file. Resetting to default: {e}", level="error")
                self._reset_config_to_defaults()
        else:
            self.log_status("No launcher configuration found. Using default settings.", level="info")
            self._reset_config_to_defaults() # Ensure all default values are set

        self.populate_instance_dropdown()

    def _reset_config_to_defaults(self):
        """Helper to set all config variables to their default initial values."""
        self.instance_list = ["default"]
        self.ram_allocation = 2048
        self.offline_mode_enabled = False
        self.offline_username = "Player"
        self.auto_restart_on_crash = False

        self.min_ram_allocation = 512
        self.custom_jvm_arguments = ""
        self.use_native_libraries = True
        self.custom_java_path = ""

        self.resolution_width = 854
        self.resolution_height = 480
        self.fullscreen_mode = False
        self.server_ip_on_launch = ""
        self.game_directory_override = ""
        self.enable_custom_game_arguments = False
        self.custom_game_arguments = ""

        self.close_launcher_on_game_start = False
        self.auto_update_launcher = True
        self.show_console_on_launch = True
        self.theme_mode = "System"
        self.color_theme = "blue"
        self.download_server_jars = False
        self.show_snapshots_betas = False
        self.custom_assets_root = ""
        self.keep_launcher_open_on_game_start = True

    def save_config(self):
        """Saves launcher configuration to file."""
        config = {
            "instance_list": self.instance_list,
            "ram_allocation": self.ram_allocation,
            "offline_mode_enabled": self.offline_mode_enabled,
            "offline_username": self.offline_username,
            "auto_restart_on_crash": self.auto_restart_on_crash,

            # --- NEW: Save all new settings ---
            "min_ram_allocation": self.min_ram_allocation,
            "custom_jvm_arguments": self.custom_jvm_arguments,
            "use_native_libraries": self.use_native_libraries,
            "custom_java_path": self.custom_java_path,

            "resolution_width": self.resolution_width,
            "resolution_height": self.resolution_height,
            "fullscreen_mode": self.fullscreen_mode,
            "server_ip_on_launch": self.server_ip_on_launch,
            "game_directory_override": self.game_directory_override,
            "enable_custom_game_arguments": self.enable_custom_game_arguments,
            "custom_game_arguments": self.custom_game_arguments,

            "close_launcher_on_game_start": self.close_launcher_on_game_start,
            "auto_update_launcher": self.auto_update_launcher,
            "show_console_on_launch": self.show_console_on_launch,
            "theme_mode": self.theme_mode,
            "color_theme": self.color_theme,
            "download_server_jars": self.download_server_jars,
            "show_snapshots_betas": self.show_snapshots_betas,
            "custom_assets_root": self.custom_assets_root,
            "keep_launcher_open_on_game_start": self.keep_launcher_open_on_game_start
            # --- END NEW ---
        }
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=4)
            self.log_status("Launcher configuration saved.", level="success")
        except Exception as e:
            self.log_status(f"Error saving launcher configuration: {e}", level="error")

    def load_auth_data(self):
        """Loads authentication data from file."""
        if os.path.exists(AUTH_FILE):
            try:
                with open(AUTH_FILE, 'r') as f:
                    self.selected_account = json.load(f)
                self.log_status("Authentication data loaded.", level="success")
            except json.JSONDecodeError:
                self.log_status("Error loading authentication data file. Please log in again.", level="error")
                self.selected_account = None
        else:
            self.log_status("No authentication data found. Please log in.", level="info")
            self.selected_account = None
        self.check_login_status() # Update UI based on loaded data

    def save_auth_data(self):
        """Saves authentication data to file."""
        try:
            with open(AUTH_FILE, 'w') as f:
                json.dump(self.selected_account, f, indent=4)
            self.log_status("Authentication data saved.", level="success")
        except Exception as e:
            self.log_status(f"Error saving authentication data: {e}", level="error")

    def check_login_status(self):
        """Updates UI based on login status."""
        if self.selected_account:
            username = self.selected_account.get("name", "Unknown")
            self.login_button.configure(text=f"Logged in as: {username}", state="disabled")
            self.logout_button.configure(state="normal")
            self.log_status(f"Currently logged in as: {username}", level="info")
        else:
            self.login_button.configure(text="Login to Microsoft", state="normal")
            self.logout_button.configure(state="disabled")
            self.log_status("Not logged in.", level="info")

    def logout_account(self):
        """Logs out the current account."""
        self.selected_account = None
        if os.path.exists(AUTH_FILE):
            os.remove(AUTH_FILE)
            self.log_status("Authentication data cleared.", level="success")
        self.check_login_status()
        messagebox.showinfo("Logout", "You have been logged out.")

    def login_microsoft_account(self):
        """Initiates the Microsoft account login flow in a new thread."""
        self.log_status("Initiating Microsoft login...", level="info")
        self.login_button.configure(state="disabled", text="Logging in...")
        threading.Thread(target=self._run_microsoft_login_flow).start()

    def _run_microsoft_login_flow(self):
        """Handles the actual Microsoft login process."""
        try:
            self.log_status("Initiating Microsoft login using minecraft-launcher-lib's default client...", level="info")

            # Pass None for CLIENT_ID and REDIRECT_URL to use the library's default.
            # This means you DO NOT need to register an Azure AD application yourself.
            login_url, state, code_verifier = mc_microsoft_account.get_secure_login_data(None, None)

            self.log_status(f"Please open the following URL in your browser and log in:\n{login_url}", level="info")
            messagebox.showinfo("Login Required",
                                f"Please open the following URL in your browser and log in, then paste the full URL you are redirected to back here:\n\n{login_url}")

            code_url = self.custom_input_dialog("Paste Redirect URL", "After logging in, paste the full URL you were redirected to:")

            if not code_url:
                self.log_status("Login cancelled or no URL provided.", level="warning")
                return

            self.log_status("Parsing authentication code...", level="info")
            auth_code = mc_microsoft_account.parse_auth_code_url(code_url, state)

            self.log_status("Completing login...", level="info")
            login_data = mc_microsoft_account.complete_login(None, None, None, auth_code, code_verifier)

            self.selected_account = login_data
            self.save_auth_data()
            self.check_login_status()
            self.log_status(f"Successfully logged in as {self.selected_account.get('name', 'Unknown')}", level="success")

        except Exception as e:
            self.log_status(f"Microsoft login failed: {e}", level="error")
            messagebox.showerror("Login Error", f"Failed to log in to Microsoft account: {e}")
            self.selected_account = None
            self.check_login_status() # Update UI to not logged in
        finally:
            # Ensure button state is reset even on failure
            self.after(0, lambda: self.login_button.configure(state="normal", text="Login to Microsoft"))

    def populate_instance_dropdown(self):
        """Populates the instance dropdown with saved instances."""
        if not self.instance_list:
            self.instance_list = ["default"] # Ensure at least a default
        self.instance_dropdown.configure(values=self.instance_list)
        if self.instance_list and self.instance_dropdown.get() not in self.instance_list:
            self.instance_dropdown.set(self.instance_list[0])

    def add_new_instance(self):
        """Adds a new instance to the launcher."""
        new_instance_name = self.add_instance_entry.get().strip()
        if new_instance_name:
            if new_instance_name not in self.instance_list:
                self.instance_list.append(new_instance_name)
                self.populate_instance_dropdown()
                self.add_instance_entry.delete(0, tk.END)
                self.save_config()
                self.log_status(f"Instance '{new_instance_name}' added.", level="success")
            else:
                self.log_status(f"Instance '{new_instance_name}' already exists.", level="warning")
                messagebox.showwarning("Add Instance", f"Instance '{new_instance_name}' already exists.")
        else:
            self.log_status("Please enter a name for the new instance.", level="warning")
            messagebox.showwarning("Add Instance", "Please enter a name for the new instance.")

    def update_version_list(self):
        """Fetches and updates the list of available Minecraft versions."""
        self.log_status("Updating Minecraft version list...", level="info")
        try:
            # We pass include_snapshots=self.show_snapshots_betas
            versions = mc.utils.get_version_list(self.game_directory_override or DEFAULT_GAME_DIR, include_snapshots=self.show_snapshots_betas)

            # Filter out alpha/beta/pre-release/snapshot versions if not enabled
            if not self.show_snapshots_betas:
                stable_versions = []
                for v in versions:
                    # Filter for 'release' type and ensure no common snapshot/pre-release patterns
                    if v["type"] == "release" and not re.search(r'-(pre|rc|b\d+|snapshot|alpha|beta|dev)', v["id"], re.IGNORECASE):
                        stable_versions.append(v["id"])
                self.minecraft_versions = stable_versions
            else:
                self.minecraft_versions = [v["id"] for v in versions]

            if not self.minecraft_versions:
                self.version_optionmenu.set("No versions found")
                self.log_status("No Minecraft versions found.", level="warning")
            else:
                # Sort versions (a more robust sort could be implemented for semantic versioning)
                # Simple attempt to sort by major.minor.patch
                def version_sort_key(version_str):
                    parts = version_str.split('-')[0].split('.')
                    return [int(p) if p.isdigit() else p for p in parts]

                # Sort by version number (descending for latest first), then by full string if numbers are equal
                self.minecraft_versions.sort(key=lambda s: (version_sort_key(s), s), reverse=True)

                self.version_optionmenu.configure(values=self.minecraft_versions)
                if self.minecraft_versions:
                    self.version_optionmenu.set(self.minecraft_versions[0]) # Select the latest
                self.log_status(f"Loaded {len(self.minecraft_versions)} Minecraft versions.", level="success")
        except Exception as e:
            self.log_status(f"Error loading Minecraft versions: {e}", level="error")
            self.version_optionmenu.set("Error loading versions")

    def launch_minecraft(self):
        """Prepares and launches Minecraft."""
        selected_version = self.version_optionmenu.get()
        selected_instance = self.instance_dropdown.get()

        if selected_version == "Loading..." or selected_version == "No versions found" or selected_version == "Error loading versions":
            self.log_status("Please select a valid Minecraft version.", level="warning")
            messagebox.showwarning("Launch Error", "Please select a valid Minecraft version before launching.")
            return

        # Handle offline mode login if no Microsoft account is selected
        if not self.selected_account:
            if self.offline_mode_enabled:
                if not self.offline_username or self.offline_username.strip() == "" or self.offline_username == "Player":
                    username_input = self.custom_input_dialog("Offline Username", "Enter your desired username for offline mode:")
                    if username_input and username_input.strip() != "":
                        self.offline_username = username_input.strip()
                        self.save_config()
                    else:
                        self.log_status("Offline username not provided. Cannot launch in offline mode.", level="warning")
                        messagebox.showwarning("Launch Error", "Offline username is required for offline mode.")
                        return
                self.log_status(f"Launching in offline mode as: {self.offline_username}", level="info")
            else:
                self.log_status("Please log in to your Microsoft account first or enable offline mode in settings.", level="warning")
                messagebox.showwarning("Launch Error", "You must be logged in to a Microsoft account to launch Minecraft, or enable offline mode in settings.")
                return

        self.log_status(f"Preparing to launch Minecraft {selected_version} for instance '{selected_instance}'...", level="info")
        self.launch_button.configure(state="disabled", text="Launching...")

        # Run launch process in a separate thread to keep UI responsive
        threading.Thread(target=self._run_minecraft_launch_threaded, args=(selected_version, selected_instance)).start()

    def _run_minecraft_launch_threaded(self, version_id, instance_name):
        """Threaded function to handle Minecraft installation and launch."""
        attempts = 0
        max_attempts = 1 if not self.auto_restart_on_crash else 5 # Limit auto-restart attempts

        # Determine the actual game directory to use based on settings
        # If game_directory_override is set, use it; otherwise, use the instance-specific directory
        if self.game_directory_override:
            game_directory = self.game_directory_override
            self.log_status(f"Using custom game directory: {game_directory}", level="info")
        else:
            game_directory = os.path.join(LAUNCHER_DATA_DIR, "instances", instance_name)
            self.log_status(f"Using instance directory: {game_directory}", level="info")

        os.makedirs(game_directory, exist_ok=True) # Ensure the chosen game directory exists

        while attempts < max_attempts:
            attempts += 1
            if attempts > 1:
                self.log_status(f"Attempting to re-launch Minecraft (Attempt {attempts}/{max_attempts})...", level="warning")
                time.sleep(4) # Wait 4 seconds before retrying

            try:
                # Check if version is installed, if not, install it
                self.log_status(f"Checking installation for version {version_id}...", level="info")
                if not mc.utils.is_installed(version_id, game_directory):
                    self.log_status(f"Installing Minecraft {version_id}...", level="info")
                    callback = {
                        "setStatus": lambda text: self.log_status(f"Installation: {text}", level="info"),
                        "setProgress": lambda value: None,
                        "setMax": lambda value: None
                    }
                    mc.install.install_minecraft_version(version_id, game_directory, callback=callback)
                    self.log_status(f"Minecraft {version_id} installed successfully.", level="success")
                else:
                    self.log_status(f"Minecraft {version_id} is already installed.", level="info")

                # Get latest Java executable or use custom path
                java_path = self.custom_java_path if self.custom_java_path and os.path.exists(self.custom_java_path) else mc.utils.get_java_executable()
                if not java_path or not os.path.exists(java_path):
                    self.log_status("Java executable not found or invalid. Please ensure Java is installed and in your PATH, or specify a valid custom path in settings.", level="error")
                    self.after(0, lambda: messagebox.showerror("Launch Error", "Java executable not found or invalid. Please install Java (JRE/JDK 17 or higher) and ensure it's in your system's PATH, or specify a valid custom path in settings."))
                    return

                # Construct JVM arguments
                jvm_args = [
                    f"-Xmx{self.ram_allocation}M",
                    f"-Xms{self.min_ram_allocation}M"
                ]
                if self.custom_jvm_arguments:
                    jvm_args.extend(self.custom_jvm_arguments.split()) # Add custom JVM args

                # Construct Game arguments
                game_args = []
                if self.enable_custom_game_arguments and self.custom_game_arguments:
                    game_args.extend(self.custom_game_arguments.split()) # Add custom game args

                # Prepare launch options
                options = {
                    "launcherName": "DarkAeroLauncher",
                    "launcherVersion": "2.0.0 Alpha",
                    "java_path": java_path,
                    "jvmArguments": jvm_args,
                    "nativePath": os.path.join(game_directory, "natives") if self.use_native_libraries else None,
                    "gameDirectory": game_directory,

                    "resolutionWidth": self.resolution_width if self.resolution_width > 0 else None,
                    "resolutionHeight": self.resolution_height if self.resolution_height > 0 else None,
                    "fullscreen": self.fullscreen_mode,

                    "server": self.server_ip_on_launch if self.server_ip_on_launch else None,
                    "assetsDir": self.custom_assets_root if self.custom_assets_root else None,
                    "gameArguments": game_args,
                }

                # Add account specific data or offline data
                if self.offline_mode_enabled:
                    options["username"] = self.offline_username
                    options["uuid"] = "offline_user_uuid" # Placeholder UUID for offline
                    options["token"] = "offline_user_token" # Placeholder token for offline
                    self.log_status("Launching in OFFLINE mode.", level="info")
                else:
                    if self.selected_account:
                        options["username"] = self.selected_account["name"]
                        options["uuid"] = self.selected_account["id"]
                        options["token"] = self.selected_account["access_token"]
                        self.log_status("Launching in ONLINE mode.", level="info")
                    else:
                        self.log_status("No account selected and offline mode is disabled. This should not happen.", level="error")
                        self.after(0, lambda: messagebox.showerror("Launch Error", "No valid account found to launch Minecraft."))
                        return

                self.log_status("Generating launch command...", level="info")
                minecraft_command = mc.command.get_minecraft_command(version_id, game_directory, options)

                self.log_status("Launching Minecraft...", level="info")

                # Handle launcher closing behavior
                if self.close_launcher_on_game_start:
                    self.log_status("Closing launcher as per settings.", level="info")
                    self.save_auth_data() # Save before closing
                    self.save_config() # Save before closing
                    subprocess.Popen(minecraft_command) # Start process without waiting
                    self.destroy() # Close the main window
                    return # Exit the function as launcher is closed

                # Start subprocess for Minecraft and redirect output
                process = subprocess.Popen(minecraft_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True)

                self.log_status("Minecraft process started. Output in Console tab.", level="info")
                if self.show_console_on_launch:
                    self.after(100, lambda: self.tabview.set("Console"))

                for line in process.stdout:
                    self.after(0, self.log_console_output, line)
                process.wait()

                # Crash detection and handling
                if process.returncode != 0:
                    self.log_status(f"Minecraft exited with error code: {process.returncode}", level="error")
                    self.after(0, lambda: messagebox.showerror("Minecraft Crashed",
                                                                f"Minecraft crashed with error code: {process.returncode}.\n"
                                                                f"Check the 'Console' tab for details."))
                    if self.auto_restart_on_crash and attempts < max_attempts:
                        self.log_status(f"Auto-restart enabled. Retrying in 4 seconds...", level="warning")
                    else:
                        self.log_status(f"Auto-restart disabled or max attempts reached. Launch process ended.", level="info")
                        break
                else:
                    self.log_status("Minecraft exited normally.", level="success")
                    break # Exit loop on successful exit

            except Exception as e:
                self.log_status(f"Error during Minecraft launch: {e}", level="error")
                self.after(0, lambda: messagebox.showerror("Launch Error", f"An error occurred during launch: {e}"))
                if self.auto_restart_on_crash and attempts < max_attempts:
                    self.log_status(f"Auto-restart enabled. Retrying in 4 seconds...", level="warning")
                else:
                    self.log_status(f"Auto-restart disabled or max attempts reached. Launch process ended.", level="info")
                    break
            finally:
                # Clear console output for next launch only when process fully ends (success or max attempts)
                if attempts >= max_attempts or process.returncode == 0:
                    self.after(0, lambda: self.console_output.delete("1.0", tk.END))

        self.after(0, lambda: self.launch_button.configure(state="normal", text="Launch Minecraft"))


    def open_settings(self):
        """Opens the settings window."""
        if hasattr(self, 'settings_window') and self.settings_window.winfo_exists():
            self.settings_window.focus()
            return

        self.log_status("Opening settings...", level="info")
        self.settings_window = ctk.CTkToplevel(self)
        self.settings_window.title("Launcher Settings")
        self.settings_window.geometry("700x600") # Adjust size for more settings
        self.settings_window.transient(self) # Make it appear on top of main window
        self.settings_window.grab_set() # Make it modal

        self.settings_window.grid_columnconfigure(0, weight=1)
        self.settings_window.grid_rowconfigure(0, weight=1)

        # Create a Tabview inside the settings window for organization
        self.settings_tabview = ctk.CTkTabview(self.settings_window)
        self.settings_tabview.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # --- Tab 1: General Settings ---
        self.general_settings_tab = self.settings_tabview.add("General")
        self.general_settings_tab.grid_columnconfigure((0,1), weight=1)
        self.general_settings_tab.grid_rowconfigure((0,1,2,3,4,5,6,7), weight=0)

        row_idx = 0
        self.appearance_label = ctk.CTkLabel(self.general_settings_tab, text="Appearance:", font=ctk.CTkFont(weight="bold"))
        self.appearance_label.grid(row=row_idx, column=0, columnspan=2, padx=10, pady=(10,5), sticky="w")
        row_idx += 1

        self.theme_mode_label = ctk.CTkLabel(self.general_settings_tab, text="Theme Mode:")
        self.theme_mode_label.grid(row=row_idx, column=0, padx=10, pady=5, sticky="w")
        self.theme_mode_optionmenu = ctk.CTkOptionMenu(self.general_settings_tab, values=["System", "Dark", "Light"],
                                                        command=self.set_theme_mode)
        self.theme_mode_optionmenu.set(self.theme_mode)
        self.theme_mode_optionmenu.grid(row=row_idx, column=1, padx=10, pady=5, sticky="ew")
        row_idx += 1

        self.color_theme_label = ctk.CTkLabel(self.general_settings_tab, text="Color Theme:")
        self.color_theme_label.grid(row=row_idx, column=0, padx=10, pady=5, sticky="w")
        self.color_theme_optionmenu = ctk.CTkOptionMenu(self.general_settings_tab, values=["blue", "dark-blue", "green"],
                                                         command=self.set_color_theme)
        self.color_theme_optionmenu.set(self.color_theme)
        self.color_theme_optionmenu.grid(row=row_idx, column=1, padx=10, pady=5, sticky="ew")
        row_idx += 1

        self.behavior_label = ctk.CTkLabel(self.general_settings_tab, text="Launcher Behavior:", font=ctk.CTkFont(weight="bold"))
        self.behavior_label.grid(row=row_idx, column=0, columnspan=2, padx=10, pady=(10,5), sticky="w")
        row_idx += 1

        self.close_launcher_checkbox = ctk.CTkCheckBox(self.general_settings_tab, text="Close launcher when game starts",
                                                       command=self.toggle_launcher_close_behavior)
        self.close_launcher_checkbox.grid(row=row_idx, column=0, columnspan=2, padx=10, pady=5, sticky="w")
        self.close_launcher_checkbox.select() if self.close_launcher_on_game_start else self.close_launcher_checkbox.deselect()
        row_idx += 1

        self.keep_launcher_open_checkbox = ctk.CTkCheckBox(self.general_settings_tab, text="Keep launcher open when game starts",
                                                           command=self.toggle_launcher_keep_open_behavior)
        self.keep_launcher_open_checkbox.grid(row=row_idx, column=0, columnspan=2, padx=10, pady=5, sticky="w")
        self.keep_launcher_open_checkbox.select() if self.keep_launcher_open_on_game_start else self.keep_launcher_open_checkbox.deselect()
        row_idx += 1

        self.auto_update_checkbox = ctk.CTkCheckBox(self.general_settings_tab, text="Enable Auto-update (Future)",
                                                    command=lambda: self._update_setting("auto_update_launcher", self.auto_update_checkbox.get() == 1))
        self.auto_update_checkbox.grid(row=row_idx, column=0, columnspan=2, padx=10, pady=5, sticky="w")
        self.auto_update_checkbox.select() if self.auto_update_launcher else self.auto_update_checkbox.deselect()
        row_idx += 1

        self.show_console_checkbox = ctk.CTkCheckBox(self.general_settings_tab, text="Show Console Tab on Launch",
                                                    command=lambda: self._update_setting("show_console_on_launch", self.show_console_checkbox.get() == 1))
        self.show_console_checkbox.grid(row=row_idx, column=0, columnspan=2, padx=10, pady=5, sticky="w")
        self.show_console_checkbox.select() if self.show_console_on_launch else self.show_console_checkbox.deselect()
        row_idx += 1

        # --- Tab 2: Game & Performance Settings ---
        self.game_perf_tab = self.settings_tabview.add("Game & Performance")
        self.game_perf_tab.grid_columnconfigure((0,1), weight=1)
        self.game_perf_tab.grid_rowconfigure((0,1,2,3,4,5,6,7,8,9,10,11,12,13,14), weight=0)

        row_idx = 0
        self.ram_label = ctk.CTkLabel(self.game_perf_tab, text="Allocate Max RAM (MB):")
        self.ram_label.grid(row=row_idx, column=0, padx=10, pady=(20,5), sticky="w")
        self.current_ram_display = ctk.CTkLabel(self.game_perf_tab, text=f"{self.ram_allocation} MB")
        self.current_ram_display.grid(row=row_idx, column=1, padx=10, pady=(20,5), sticky="e")
        row_idx += 1
        self.ram_slider = ctk.CTkSlider(self.game_perf_tab, from_=1024, to=8192,
                                        number_of_steps=7, # 1GB, 2GB, ..., 8GB
                                        command=self.update_ram_display)
        self.ram_slider.set(self.ram_allocation)
        self.ram_slider.grid(row=row_idx, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        row_idx += 1

        self.min_ram_label = ctk.CTkLabel(self.game_perf_tab, text="Allocate Min RAM (MB):")
        self.min_ram_label.grid(row=row_idx, column=0, padx=10, pady=5, sticky="w")
        self.current_min_ram_display = ctk.CTkLabel(self.game_perf_tab, text=f"{self.min_ram_allocation} MB")
        self.current_min_ram_display.grid(row=row_idx, column=1, padx=10, pady=5, sticky="e")
        row_idx += 1
        self.min_ram_slider = ctk.CTkSlider(self.game_perf_tab, from_=512, to=8192, # Can go up to max RAM
                                            number_of_steps=max(1, int((8192 - 512) / 256)), # Steps of 256MB
                                            command=self.update_min_ram_display)
        self.min_ram_slider.set(self.min_ram_allocation)
        self.min_ram_slider.grid(row=row_idx, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        row_idx += 1

        self.jvm_args_label = ctk.CTkLabel(self.game_perf_tab, text="Custom JVM Arguments (space separated):")
        self.jvm_args_label.grid(row=row_idx, column=0, columnspan=2, padx=10, pady=(10,5), sticky="w")
        row_idx += 1
        self.jvm_args_entry = ctk.CTkEntry(self.game_perf_tab, placeholder_text="-XX:+UseG1GC")
        self.jvm_args_entry.grid(row=row_idx, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        self.jvm_args_entry.insert(0, self.custom_jvm_arguments)
        self.jvm_args_entry.bind("<FocusOut>", lambda e: self._update_setting("custom_jvm_arguments", self.jvm_args_entry.get()))
        self.jvm_args_entry.bind("<Return>", lambda e: self._update_setting("custom_jvm_arguments", self.jvm_args_entry.get()))
        row_idx += 1

        self.java_path_label = ctk.CTkLabel(self.game_perf_tab, text="Custom Java Executable Path:")
        self.java_path_label.grid(row=row_idx, column=0, padx=10, pady=(10,5), sticky="w")
        self.java_path_entry = ctk.CTkEntry(self.game_perf_tab, placeholder_text="e.g., C:\\Program Files\\Java\\jdk-17\\bin\\java.exe")
        self.java_path_entry.grid(row=row_idx, column=0, padx=10, pady=5, sticky="ew")
        self.java_path_entry.insert(0, self.custom_java_path)
        self.java_path_entry.bind("<FocusOut>", lambda e: self._update_setting("custom_java_path", self.java_path_entry.get()))
        self.java_path_entry.bind("<Return>", lambda e: self._update_setting("custom_java_path", self.java_path_entry.get()))
        self.browse_java_path_button = ctk.CTkButton(self.game_perf_tab, text="Browse", width=70, command=self.browse_java_path)
        self.browse_java_path_button.grid(row=row_idx, column=1, padx=10, pady=5, sticky="e")
        row_idx += 1

        self.use_native_checkbox = ctk.CTkCheckBox(self.game_perf_tab, text="Use Native Libraries (Recommended)",
                                                  command=lambda: self._update_setting("use_native_libraries", self.use_native_checkbox.get() == 1))
        self.use_native_checkbox.grid(row=row_idx, column=0, columnspan=2, padx=10, pady=5, sticky="w")
        self.use_native_checkbox.select() if self.use_native_libraries else self.use_native_checkbox.deselect()
        row_idx += 1

        self.game_dir_override_label = ctk.CTkLabel(self.game_perf_tab, text="Custom Game Directory:")
        self.game_dir_override_label.grid(row=row_idx, column=0, padx=10, pady=(10,5), sticky="w")
        self.game_dir_override_entry = ctk.CTkEntry(self.game_perf_tab, placeholder_text="Leave empty for instance default")
        self.game_dir_override_entry.grid(row=row_idx, column=0, padx=10, pady=5, sticky="ew")
        self.game_dir_override_entry.insert(0, self.game_directory_override)
        self.game_dir_override_entry.bind("<FocusOut>", lambda e: self._update_setting("game_directory_override", self.game_dir_override_entry.get()))
        self.game_dir_override_entry.bind("<Return>", lambda e: self._update_setting("game_directory_override", self.game_dir_override_entry.get()))
        self.browse_game_dir_button = ctk.CTkButton(self.game_perf_tab, text="Browse", width=70, command=self.browse_game_directory)
        self.browse_game_dir_button.grid(row=row_idx, column=1, padx=10, pady=5, sticky="e")
        row_idx += 1

        self.custom_assets_root_label = ctk.CTkLabel(self.game_perf_tab, text="Custom Assets Directory:")
        self.custom_assets_root_label.grid(row=row_idx, column=0, padx=10, pady=(10,5), sticky="w")
        self.custom_assets_root_entry = ctk.CTkEntry(self.game_perf_tab, placeholder_text="Leave empty for default")
        self.custom_assets_root_entry.grid(row=row_idx, column=0, padx=10, pady=5, sticky="ew")
        self.custom_assets_root_entry.insert(0, self.custom_assets_root)
        self.custom_assets_root_entry.bind("<FocusOut>", lambda e: self._update_setting("custom_assets_root", self.custom_assets_root_entry.get()))
        self.custom_assets_root_entry.bind("<Return>", lambda e: self._update_setting("custom_assets_root", self.custom_assets_root_entry.get()))
        self.browse_assets_dir_button = ctk.CTkButton(self.game_perf_tab, text="Browse", width=70, command=self.browse_assets_directory)
        self.browse_assets_dir_button.grid(row=row_idx, column=1, padx=10, pady=5, sticky="e")
        row_idx += 1

        self.enable_game_args_checkbox = ctk.CTkCheckBox(self.game_perf_tab, text="Enable Custom Game Arguments",
                                                         command=self.toggle_custom_game_args_entry)
        self.enable_game_args_checkbox.grid(row=row_idx, column=0, columnspan=2, padx=10, pady=10, sticky="w")
        self.enable_game_args_checkbox.select() if self.enable_custom_game_arguments else self.enable_game_args_checkbox.deselect()
        row_idx += 1

        self.custom_game_args_entry = ctk.CTkEntry(self.game_perf_tab, placeholder_text="--server YOUR_IP --port 25565")
        self.custom_game_args_entry.grid(row=row_idx, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        self.custom_game_args_entry.insert(0, self.custom_game_arguments)
        self.custom_game_args_entry.bind("<FocusOut>", lambda e: self._update_setting("custom_game_arguments", self.custom_game_args_entry.get()))
        self.custom_game_args_entry.bind("<Return>", lambda e: self._update_setting("custom_game_arguments", self.custom_game_args_entry.get()))
        self.toggle_custom_game_args_entry() # Set initial state
        row_idx += 1

        self.resolution_label = ctk.CTkLabel(self.game_perf_tab, text="Game Resolution:", font=ctk.CTkFont(weight="bold"))
        self.resolution_label.grid(row=row_idx, column=0, columnspan=2, padx=10, pady=(10,5), sticky="w")
        row_idx += 1

        self.res_width_label = ctk.CTkLabel(self.game_perf_tab, text="Width:")
        self.res_width_label.grid(row=row_idx, column=0, padx=10, pady=5, sticky="w")
        self.res_width_entry = ctk.CTkEntry(self.game_perf_tab, width=100)
        self.res_width_entry.grid(row=row_idx, column=1, padx=10, pady=5, sticky="w")
        self.res_width_entry.insert(0, str(self.resolution_width))
        self.res_width_entry.bind("<FocusOut>", lambda e: self._update_int_setting("resolution_width", self.res_width_entry.get()))
        self.res_width_entry.bind("<Return>", lambda e: self._update_int_setting("resolution_width", self.res_width_entry.get()))
        row_idx += 1

        self.res_height_label = ctk.CTkLabel(self.game_perf_tab, text="Height:")
        self.res_height_label.grid(row=row_idx, column=0, padx=10, pady=5, sticky="w")
        self.res_height_entry = ctk.CTkEntry(self.game_perf_tab, width=100)
        self.res_height_entry.grid(row=row_idx, column=1, padx=10, pady=5, sticky="w")
        self.res_height_entry.insert(0, str(self.resolution_height))
        self.res_height_entry.bind("<FocusOut>", lambda e: self._update_int_setting("resolution_height", self.res_height_entry.get()))
        self.res_height_entry.bind("<Return>", lambda e: self._update_int_setting("resolution_height", self.res_height_entry.get()))
        row_idx += 1

        self.fullscreen_checkbox = ctk.CTkCheckBox(self.game_perf_tab, text="Launch in Fullscreen Mode",
                                                  command=lambda: self._update_setting("fullscreen_mode", self.fullscreen_checkbox.get() == 1))
        self.fullscreen_checkbox.grid(row=row_idx, column=0, columnspan=2, padx=10, pady=10, sticky="w")
        self.fullscreen_checkbox.select() if self.fullscreen_mode else self.fullscreen_checkbox.deselect()
        row_idx += 1

        self.server_ip_label = ctk.CTkLabel(self.game_perf_tab, text="Auto-Join Server IP:")
        self.server_ip_label.grid(row=row_idx, column=0, columnspan=2, padx=10, pady=(10,5), sticky="w")
        row_idx += 1
        self.server_ip_entry = ctk.CTkEntry(self.game_perf_tab, placeholder_text="play.hypixel.net")
        self.server_ip_entry.grid(row=row_idx, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        self.server_ip_entry.insert(0, self.server_ip_on_launch)
        self.server_ip_entry.bind("<FocusOut>", lambda e: self._update_setting("server_ip_on_launch", self.server_ip_entry.get()))
        self.server_ip_entry.bind("<Return>", lambda e: self._update_setting("server_ip_on_launch", self.server_ip_entry.get()))
        row_idx += 1

        # --- Tab 3: Advanced/Experimental Settings ---
        self.advanced_settings_tab = self.settings_tabview.add("Advanced")
        self.advanced_settings_tab.grid_columnconfigure((0,1), weight=1)
        self.advanced_settings_tab.grid_rowconfigure((0,1,2,3,4,5,6), weight=0)

        row_idx = 0

        self.offline_mode_checkbox = ctk.CTkCheckBox(self.advanced_settings_tab, text="Enable Offline Mode",
                                                     command=self.toggle_offline_mode)
        self.offline_mode_checkbox.grid(row=row_idx, column=0, columnspan=2, padx=10, pady=(20,10), sticky="w")
        self.offline_mode_checkbox.select() if self.offline_mode_enabled else self.offline_mode_checkbox.deselect()
        row_idx += 1

        self.offline_username_label = ctk.CTkLabel(self.advanced_settings_tab, text="Offline Username:")
        self.offline_username_label.grid(row=row_idx, column=0, padx=10, pady=(0,5), sticky="w")
        self.offline_username_entry = ctk.CTkEntry(self.advanced_settings_tab, placeholder_text="Your Offline Name")
        self.offline_username_entry.grid(row=row_idx, column=1, padx=10, pady=(0,5), sticky="ew")
        self.offline_username_entry.insert(0, self.offline_username)
        self.offline_username_entry.bind("<FocusOut>", self.save_offline_username)
        self.offline_username_entry.bind("<Return>", self.save_offline_username)
        self.update_offline_username_state() # Initial state
        row_idx += 1

        self.auto_restart_checkbox = ctk.CTkCheckBox(self.advanced_settings_tab, text="Auto-restart Minecraft on crash",
                                                     command=self.toggle_auto_restart)
        self.auto_restart_checkbox.grid(row=row_idx, column=0, columnspan=2, padx=10, pady=10, sticky="w")
        self.auto_restart_checkbox.select() if self.auto_restart_on_crash else self.auto_restart_checkbox.deselect()
        row_idx += 1

        self.show_snapshots_betas_checkbox = ctk.CTkCheckBox(self.advanced_settings_tab, text="Show Snapshots/Betas in Version List",
                                                            command=self.toggle_show_snapshots_betas)
        self.show_snapshots_betas_checkbox.grid(row=row_idx, column=0, columnspan=2, padx=10, pady=10, sticky="w")
        self.show_snapshots_betas_checkbox.select() if self.show_snapshots_betas else self.show_snapshots_betas_checkbox.deselect()
        row_idx += 1

        self.download_server_jars_checkbox = ctk.CTkCheckBox(self.advanced_settings_tab, text="Download Server Jars (Future Feature)",
                                                            command=lambda: self._update_setting("download_server_jars", self.download_server_jars_checkbox.get() == 1))
        self.download_server_jars_checkbox.grid(row=row_idx, column=0, columnspan=2, padx=10, pady=10, sticky="w")
        self.download_server_jars_checkbox.select() if self.download_server_jars else self.download_server_jars_checkbox.deselect()
        row_idx += 1

        # --- Save Button (Common for all tabs) ---
        self.save_settings_button = ctk.CTkButton(self.settings_window, text="Apply & Save", command=self.save_settings_from_ui)
        self.save_settings_button.grid(row=1, column=0, padx=20, pady=(0,20), sticky="ew") # Placed below tabview

        # Handle window close protocol
        self.settings_window.protocol("WM_DELETE_WINDOW", self.on_settings_closing)

    # --- SETTINGS HELPER METHODS ---

    def _update_setting(self, setting_name, value):
        """Generic helper to update an instance variable and log it."""
        setattr(self, setting_name, value)
        self.log_status(f"Setting '{setting_name}' updated to: {value}", level="info")

    def _update_int_setting(self, setting_name, value_str):
        """Helper to update an integer setting, with validation."""
        try:
            int_value = int(value_str)
            if int_value >= 0: # Ensure non-negative
                setattr(self, setting_name, int_value)
                self.log_status(f"Setting '{setting_name}' updated to: {int_value}", level="info")
            else:
                self.log_status(f"Invalid input for '{setting_name}': {value_str}. Must be non-negative integer.", level="warning")
                # Revert entry to last valid value
                entry_widget = getattr(self, f"{setting_name.replace('resolution', 'res')}_entry") # Handle resolution_width/height naming
                entry_widget.delete(0, tk.END)
                entry_widget.insert(0, str(getattr(self, setting_name)))
        except ValueError:
            self.log_status(f"Invalid input for '{setting_name}': {value_str}. Not an integer.", level="warning")
            # Revert entry to last valid value
            entry_widget = getattr(self, f"{setting_name.replace('resolution', 'res')}_entry")
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, str(getattr(self, setting_name)))

    def update_ram_display(self, value):
        """Updates the display for max RAM slider."""
        int_value = int(value)
        self.current_ram_display.configure(text=f"{int_value} MB")
        self.ram_allocation = int_value
        self.log_status(f"Max RAM set to: {self.ram_allocation} MB", level="info")
        # Adjust min RAM slider's max limit if max RAM decreases
        if hasattr(self, 'min_ram_slider'):
            self.min_ram_slider.configure(to=self.ram_allocation)
            if self.min_ram_allocation > self.ram_allocation:
                self.min_ram_allocation = self.ram_allocation
                self.min_ram_slider.set(self.min_ram_allocation)
                self.current_min_ram_display.configure(text=f"{self.min_ram_allocation} MB")

    def update_min_ram_display(self, value):
        """Updates the display for min RAM slider."""
        int_value = int(value)
        # Ensure min RAM is not greater than max RAM
        if int_value > self.ram_allocation:
            int_value = self.ram_allocation
            self.min_ram_slider.set(self.ram_allocation)
        
        self.current_min_ram_display.configure(text=f"{int_value} MB")
        self.min_ram_allocation = int_value
        self.log_status(f"Min RAM set to: {self.min_ram_allocation} MB", level="info")

    def set_theme_mode(self, new_mode):
        """Sets the CustomTkinter appearance mode."""
        self.theme_mode = new_mode
        ctk.set_appearance_mode(new_mode)
        self.log_status(f"Theme mode set to: {new_mode}", level="info")

    def set_color_theme(self, new_theme):
        """Sets the CustomTkinter color theme."""
        self.color_theme = new_theme
        ctk.set_default_color_theme(new_theme)
        self.log_status(f"Color theme set to: {new_theme}", level="info")

    def toggle_launcher_close_behavior(self):
        """Handles mutual exclusivity of close/keep open checkboxes."""
        self.close_launcher_on_game_start = self.close_launcher_checkbox.get() == 1
        if self.close_launcher_on_game_start:
            self.keep_launcher_open_on_game_start = False
            self.keep_launcher_open_checkbox.deselect()
            self.log_status("Launcher will close on game start.", level="info")
        else:
            # If "close" is deselected, and "keep open" is also deselected, default to "keep open"
            if not self.keep_launcher_open_on_game_start:
                self.keep_launcher_open_on_game_start = True
                self.keep_launcher_open_checkbox.select()
            self.log_status("Launcher will not close automatically.", level="info")

    def toggle_launcher_keep_open_behavior(self):
        """Handles mutual exclusivity of close/keep open checkboxes."""
        self.keep_launcher_open_on_game_start = self.keep_launcher_open_checkbox.get() == 1
        if self.keep_launcher_open_on_game_start:
            self.close_launcher_on_game_start = False
            self.close_launcher_checkbox.deselect()
            self.log_status("Launcher will stay open on game start.", level="info")
        else:
            # If "keep open" is deselected, and "close" is also deselected, default to "close"
            if not self.close_launcher_on_game_start:
                self.close_launcher_on_game_start = True
                self.close_launcher_checkbox.select()
            self.log_status("Launcher will not be forced to stay open.", level="info")

    def toggle_offline_mode(self):
        """Toggles offline mode and updates username entry state."""
        self.offline_mode_enabled = self.offline_mode_checkbox.get() == 1
        self.update_offline_username_state()
        self.log_status(f"Offline mode: {'Enabled' if self.offline_mode_enabled else 'Disabled'}", level="info")

    def update_offline_username_state(self):
        """Enables/disables and shows/hides the offline username entry."""
        if self.offline_mode_enabled:
            self.offline_username_label.grid()
            self.offline_username_entry.grid()
            self.offline_username_entry.configure(state="normal")
        else:
            self.offline_username_label.grid_remove()
            self.offline_username_entry.grid_remove()
            self.offline_username_entry.configure(state="disabled")

    def save_offline_username(self, event=None):
        """Saves the offline username from the entry field."""
        new_username = self.offline_username_entry.get().strip()
        if new_username:
            self.offline_username = new_username
            self.log_status(f"Offline username set to: {self.offline_username}", level="info")
        else:
            self.offline_username = "Player" # Default if empty
            self.offline_username_entry.delete(0, tk.END)
            self.offline_username_entry.insert(0, "Player")
            self.log_status("Offline username cleared, set to 'Player'.", level="warning")

    def toggle_auto_restart(self):
        """Toggles auto-restart on crash setting."""
        self.auto_restart_on_crash = self.auto_restart_checkbox.get() == 1
        self.log_status(f"Auto-restart on crash: {'Enabled' if self.auto_restart_on_crash else 'Disabled'}", level="info")

    def browse_java_path(self):
        """Opens a file dialog to select Java executable."""
        file_path = filedialog.askopenfilename(
            title="Select Java Executable",
            filetypes=[("Java Executable", "*.exe"), ("All Files", "*.*")] # .exe for Windows, others for Linux/macOS
        )
        if file_path:
            self.custom_java_path = file_path
            self.java_path_entry.delete(0, tk.END)
            self.java_path_entry.insert(0, file_path)
            self.log_status(f"Custom Java path set to: {file_path}", level="info")

    def browse_game_directory(self):
        """Opens a directory dialog to select custom game directory."""
        dir_path = filedialog.askdirectory(title="Select Custom Game Directory")
        if dir_path:
            self.game_directory_override = dir_path
            self.game_dir_override_entry.delete(0, tk.END)
            self.game_dir_override_entry.insert(0, dir_path)
            self.log_status(f"Custom game directory set to: {dir_path}", level="info")

    def browse_assets_directory(self):
        """Opens a directory dialog to select custom assets directory."""
        dir_path = filedialog.askdirectory(title="Select Custom Assets Directory")
        if dir_path:
            self.custom_assets_root = dir_path
            self.custom_assets_root_entry.delete(0, tk.END)
            self.custom_assets_root_entry.insert(0, dir_path)
            self.log_status(f"Custom assets directory set to: {dir_path}", level="info")

    def toggle_custom_game_args_entry(self):
        """Enables/disables the custom game arguments entry."""
        self.enable_custom_game_arguments = self.enable_game_args_checkbox.get() == 1
        state = "normal" if self.enable_custom_game_arguments else "disabled"
        self.custom_game_args_entry.configure(state=state)
        self.log_status(f"Custom Game Arguments field: {state}", level="info")

    def toggle_show_snapshots_betas(self):
        """Toggles display of snapshots/betas and refreshes version list."""
        self.show_snapshots_betas = self.show_snapshots_betas_checkbox.get() == 1
        self.log_status(f"Show Snapshots/Betas: {'Enabled' if self.show_snapshots_betas else 'Disabled'}", level="info")
        self.update_version_list() # Immediately refresh version list when this setting changes

    def save_settings_from_ui(self):
        """Gathers all current UI settings and saves them to the config file."""
        # Ensure entries that might not have lost focus are updated
        self._update_setting("custom_jvm_arguments", self.jvm_args_entry.get())
        self._update_setting("custom_java_path", self.java_path_entry.get())
        self._update_int_setting("resolution_width", self.res_width_entry.get())
        self._update_int_setting("resolution_height", self.res_height_entry.get())
        self._update_setting("server_ip_on_launch", self.server_ip_entry.get())
        self._update_setting("game_directory_override", self.game_dir_override_entry.get())
        self._update_setting("custom_game_arguments", self.custom_game_args_entry.get())
        self._update_setting("custom_assets_root", self.custom_assets_root_entry.get())

        self.save_offline_username() # Ensure the latest username is saved
        self.save_config()
        self.log_status("Settings applied and saved.", level="success")
        self.settings_window.destroy()

    def on_settings_closing(self):
        """Ensures settings are saved when the settings window is closed directly."""
        self.save_settings_from_ui()


# --- Main execution ---
if __name__ == "__main__":
    app = LauncherUI()
    app.mainloop()
