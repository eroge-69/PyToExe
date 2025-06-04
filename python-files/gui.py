import customtkinter as ctk
from gamepad_control import GamepadController
import webbrowser
import os
import subprocess
import time
import configparser
import threading

class AutomatorGUI:
    def __init__(self):
        self.controller = None
        self.chrome_path = 'C:/Program Files/Google/Chrome/Application/chrome.exe'  # Adjust if Chrome is elsewhere
        self.num_accounts = 20
        self.shortcuts_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Shortcuts")
        self.bo6_url = "https://www.xbox.com/en-US/play/launch/call-of-duty-black-ops-6---cross-gen-bundle/9PF528M6CRHQ"
        
        # Load config
        self.config = configparser.ConfigParser()
        self.config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini")
        self.config.read(self.config_path)
        
        # Setup the main window
        self.window = ctk.CTk()
        self.window.title("Bot Ops Lobby Tool")
        self.window.geometry("900x900")
        ctk.set_appearance_mode("dark")
        
        # Create tabview
        self.tabview = ctk.CTkTabview(self.window)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create tabs
        self.main_tab = self.tabview.add("Main")
        self.settings_tab = self.tabview.add("Settings")
        
        # Setup main tab
        self.setup_main_tab()
        
        # Setup settings tab
        self.setup_settings_tab()
        
        # Set default tab
        self.tabview.set("Main")
        
        # Initial log message
        self.log("Ready to start. Select number of accounts and click 'Open Xbox Sessions'")
        
        # Initialize state
        self.is_running = False
        
        # Scan for available profiles
        self.available_profiles = self.scan_profiles()
        self.profile_label.configure(text=f"Available Profiles: {len(self.available_profiles)}/20")
        
        # Update dropdown values based on available profiles
        if self.available_profiles:
            values = [str(i+1) for i in range(len(self.available_profiles))]
            self.account_counter.configure(values=values)
            self.account_counter.set("1")  # Set default value
    
    def setup_main_tab(self):
        """Setup the main tab with existing controls"""
        self.profile_frame = ctk.CTkFrame(self.main_tab)
        self.profile_frame.pack(fill="x", padx=10, pady=5)
        
        title = ctk.CTkLabel(self.profile_frame, text="Bot Ops Lobby Tool - (BETA)", font=("Arial", 20, "bold"))
        title.pack(pady=(0, 10))
        
        description = ctk.CTkLabel(self.profile_frame, text="Let's get that schmoney\n", font=("Arial", 12), justify="center")
        description.pack(pady=(0, 20))
        
        profile_frame = ctk.CTkFrame(self.main_tab)
        profile_frame.pack(padx=10, pady=10, fill="x")
        
        self.profile_label = ctk.CTkLabel(profile_frame, text=f"Available Profiles: 0/20", font=("Arial", 12, "bold"))
        self.profile_label.pack(pady=5)
        
        counter_frame = ctk.CTkFrame(self.main_tab)
        counter_frame.pack(padx=10, pady=10, fill="x")
        
        ctk.CTkLabel(counter_frame, text="Number of Accounts:", font=("Arial", 12)).pack(side="left", padx=5)
        
        self.account_counter = ctk.CTkComboBox(counter_frame, width=70, values=["1"], state="readonly")
        self.account_counter.pack(side="left", padx=5)
        
        self.status_label = ctk.CTkLabel(self.main_tab, text="Status: Ready", font=("Arial", 12, "bold"), fg_color=("gray85", "gray25"), corner_radius=6)
        self.status_label.pack(padx=10, pady=20, fill="x")
        
        button_frame = ctk.CTkFrame(self.main_tab)
        button_frame.pack(padx=10, pady=10, fill="x")
        
        self.browser_button = ctk.CTkButton(button_frame, text="Open Xbox Sessions", command=self.open_browser_windows, font=("Arial", 14, "bold"), height=40)
        self.browser_button.pack(padx=5, pady=5, fill="x")
        
        gamepad_frame = ctk.CTkFrame(self.main_tab)
        gamepad_frame.pack(padx=10, pady=10, fill="x")
        
        self.connect_button = ctk.CTkButton(gamepad_frame, text="Connect Controller", command=self.toggle_controller_connection, font=("Arial", 14, "bold"), height=40)
        self.connect_button.pack(padx=5, pady=5, fill="x")
        
        self.movement_button = ctk.CTkButton(gamepad_frame, text="Enable Movement Bot", command=self.toggle_movement, font=("Arial", 14, "bold"), height=40, state="disabled")
        self.movement_button.pack(padx=5, pady=5, fill="x")
        
        self.select_class_button = ctk.CTkButton(gamepad_frame, text="Select Class", command=self.select_class, font=("Arial", 14, "bold"), height=40, state="disabled")
        self.select_class_button.pack(padx=5, pady=5, fill="x")
        
        self.anti_afk_button = ctk.CTkButton(gamepad_frame, text="Enable Anti-AFK", command=self.toggle_anti_afk, font=("Arial", 14, "bold"), height=40, state="disabled")
        self.anti_afk_button.pack(padx=5, pady=5, fill="x")
        
        log_frame = ctk.CTkFrame(self.main_tab)
        log_frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        ctk.CTkLabel(log_frame, text="Activity Log:", font=("Arial", 12, "bold")).pack(padx=5, pady=5, anchor="w")
        
        self.log_text = ctk.CTkTextbox(log_frame, height=150)
        self.log_text.pack(padx=5, pady=5, fill="both", expand=True)
    
    def create_labeled_slider(self, parent, row, label_text, from_, to_, section, key, fallback):
        """Helper function to create a labeled slider with value display"""
        label = ctk.CTkLabel(parent, text=label_text)
        label.grid(row=row, column=0, padx=10, pady=(5,0))
        value_label = ctk.CTkLabel(parent, text="0.00", width=50)
        value_label.grid(row=row, column=1, padx=5, pady=(5,0))
        slider = ctk.CTkSlider(parent, from_=from_, to=to_)
        slider.grid(row=row+1, column=0, columnspan=2, padx=10, pady=(0,5), sticky="ew")
        initial_value = self.config.getfloat(section, key, fallback=fallback)
        slider.set(initial_value)
        value_label.configure(text=f"{initial_value:.2f}")
        def on_slider_change(value):
            value_label.configure(text=f"{value:.2f}")
            self.update_setting(section, key, value)
        slider.configure(command=on_slider_change)
        return slider
 
    def setup_settings_tab(self):
        """Setup the settings tab with config controls"""
        self.movement_settings_frame = ctk.CTkFrame(self.settings_tab)
        self.movement_settings_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.movement_settings_label = ctk.CTkLabel(self.movement_settings_frame, text="Movement Settings", font=("Arial", 16, "bold"))
        self.movement_settings_label.grid(row=0, column=0, columnspan=2, padx=10, pady=5)
        self.movement_settings_frame.grid_columnconfigure(0, weight=3)
        self.movement_settings_frame.grid_columnconfigure(1, weight=1)
        current_row = 1
        self.look_intensity_slider = self.create_labeled_slider(self.movement_settings_frame, current_row, "Look Intensity", 0, 3, 'Movement', 'look_intensity', 1.5)
        current_row += 2
        self.move_intensity_slider = self.create_labeled_slider(self.movement_settings_frame, current_row, "Move Intensity", 0, 2, 'Movement', 'move_intensity', 0.3)
        current_row += 2
        self.forward_intensity_slider = self.create_labeled_slider(self.movement_settings_frame, current_row, "Forward Intensity", 0, 2, 'Movement', 'forward_intensity', 1.0)
        current_row += 2
        self.jump_chance_slider = self.create_labeled_slider(self.movement_settings_frame, current_row, "Jump Chance", 0, 1, 'Movement', 'jump_chance', 0.15)
        current_row += 2
        self.jump_interval_slider = self.create_labeled_slider(self.movement_settings_frame, current_row, "Jump Interval (s)", 1, 10, 'Movement', 'jump_interval', 3.0)
        current_row += 2
        self.weapon_switch_chance_slider = self.create_labeled_slider(self.movement_settings_frame, current_row, "Weapon Switch Chance", 0, 1, 'Movement', 'weapon_switch_chance', 0.1)
        current_row += 2
        self.weapon_switch_interval_slider = self.create_labeled_slider(self.movement_settings_frame, current_row, "Weapon Switch Interval (s)", 1, 15, 'Movement', 'weapon_switch_interval', 5.0)
        current_row += 2
        self.min_movement_duration_slider = self.create_labeled_slider(self.movement_settings_frame, current_row, "Min Movement Duration (s)", 1, 10, 'Movement', 'min_movement_duration', 2.0)
        current_row += 2
        self.max_movement_duration_slider = self.create_labeled_slider(self.movement_settings_frame, current_row, "Max Movement Duration (s)", 2, 15, 'Movement', 'max_movement_duration', 8.0)
        current_row += 2
        self.min_break_duration_slider = self.create_labeled_slider(self.movement_settings_frame, current_row, "Min Break Duration (s)", 1, 10, 'Movement', 'min_break_duration', 3.0)
        current_row += 2
        self.max_break_duration_slider = self.create_labeled_slider(self.movement_settings_frame, current_row, "Max Break Duration (s)", 2, 20, 'Movement', 'max_break_duration', 12.0)
        current_row += 2
        self.afk_frame = ctk.CTkFrame(self.settings_tab)
        self.afk_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.afk_frame.grid_columnconfigure(0, weight=3)
        self.afk_frame.grid_columnconfigure(1, weight=1)
        self.afk_label = ctk.CTkLabel(self.afk_frame, text="Anti-AFK Settings", font=("Arial", 16, "bold"))
        self.afk_label.grid(row=0, column=0, columnspan=2, padx=10, pady=5)
        current_row = 1
        self.interval_slider = self.create_labeled_slider(self.afk_frame, current_row, "Interval (seconds)", 10, 120, 'AntiAFK', 'interval', 60.0)
        current_row += 2
        self.right_bumper_slider = self.create_labeled_slider(self.afk_frame, current_row, "Right Bumper Duration", 0.1, 1, 'AntiAFK', 'right_bumper_duration', 0.1)
        current_row += 2
        self.left_bumper_slider = self.create_labeled_slider(self.afk_frame, current_row, "Left Bumper Duration", 0.1, 1, 'AntiAFK', 'left_bumper_duration', 0.2)
        current_row += 2
        self.delay_slider = self.create_labeled_slider(self.afk_frame, current_row, "Delay Between Buttons", 0.1, 2, 'AntiAFK', 'delay_between_buttons', 1.0)
        current_row += 2
        self.settings_tab.grid_columnconfigure(0, weight=1)
        self.settings_tab.grid_columnconfigure(1, weight=1)
        self.save_button = ctk.CTkButton(self.settings_tab, text="Save Settings", command=self.save_settings)
        self.save_button.grid(row=1, column=0, columnspan=2, pady=10)
    
    def update_setting(self, section, key, value):
        """Update a setting in the controller"""
        if self.controller:
            self.controller.update_config(section, key, value)
    
    def save_settings(self):
        """Save all settings to config file"""
        if self.controller:
            self.controller.save_config()
            self.log("Settings saved to config.ini")
        else:
            with open(self.config_path, 'w') as configfile:
                self.config.write(configfile)
            self.log("Settings saved to config.ini")
    
    def scan_profiles(self):
        """Scan for available Chrome profiles in shortcuts directory"""
        profiles = []
        if os.path.exists(self.shortcuts_path):
            for i in range(1, 21):  # b1 through b20
                profile_name = f"b{i}"
                if os.path.exists(os.path.join(self.shortcuts_path, f"{profile_name}.lnk")):
                    profiles.append(profile_name)
        self.log(f"Found {len(profiles)} profiles in Shortcuts folder")
        return profiles
    
    def open_browser_windows(self):
        """Open multiple Chrome windows using profile directories"""
        def worker():
            if not os.path.exists(self.chrome_path):
                self.log("Chrome not found at " + self.chrome_path + " - check install path")
                return
            num_accounts = min(int(self.account_counter.get()), len(self.available_profiles))
            if num_accounts < 1:
                self.log("Please enter a valid number of accounts")
                return
            self.log(f"Opening {num_accounts} Xbox Cloud Gaming sessions...")
            for i in range(num_accounts):
                profile = self.available_profiles[i]
                try:
                    subprocess.run([
                        self.chrome_path,
                        "--profile-directory=" + profile,
                        "https://www.xbox.com/play"
                    ], shell=True, check=True)
                    self.log(f"Opened session {i+1}/{num_accounts} with profile {profile}")
                    time.sleep(1)  # Stagger to avoid crash
                except Exception as e:
                    self.log(f"Error opening {profile}: {str(e)}")
            self.log("All sessions opened successfully")
            self.browser_button.configure(text="Launch Black Ops 6", command=self.launch_black_ops, fg_color="orange")
        threading.Thread(target=worker, daemon=True).start()
    
    def launch_black_ops(self):
        """Launch Black Ops 6 in all open sessions"""
        def worker():
            if not os.path.exists(self.chrome_path):
                self.log("Chrome not found at " + self.chrome_path + " - check install path")
                return
            num_accounts = min(int(self.account_counter.get()), len(self.available_profiles))
            for i in range(num_accounts):
                profile = self.available_profiles[i]
                try:
                    subprocess.run([
                        self.chrome_path,
                        "--profile-directory=" + profile,
                        self.bo6_url
                    ], shell=True, check=True)
                    self.log(f"Launching Black Ops 6 for profile {profile}")
                    time.sleep(1)
                except Exception as e:
                    self.log(f"Error launching Black Ops 6: {str(e)}")
            self.log("Black Ops 6 launched in all sessions")
        threading.Thread(target=worker, daemon=True).start()
    
    def toggle_controller_connection(self):
        """Connect or disconnect the controller"""
        if not self.controller:
            self.controller = GamepadController()
        if self.controller.gamepad is None:
            if self.controller.connect():
                self.controller.start()
                self.connect_button.configure(text="Disconnect Controller", fg_color="red")
                self.movement_button.configure(state="normal")
                self.anti_afk_button.configure(state="normal")
                self.select_class_button.configure(state="normal")
                self.log("Controller connected and started")
            else:
                self.log("Failed to connect controller")
        else:
            self.controller.disconnect()
            self.connect_button.configure(text="Connect Controller", fg_color=["#3B8ED0", "#1F6AA5"])
            self.movement_button.configure(state="disabled")
            self.anti_afk_button.configure(state="disabled")
            self.select_class_button.configure(state="disabled")
            self.movement_button.configure(text="Enable Movement Bot", fg_color=["#3B8ED0", "#1F6AA5"])
            self.anti_afk_button.configure(text="Enable Anti-AFK", fg_color=["#3B8ED0", "#1F6AA5"])
            self.log("Controller disconnected")
    
    def toggle_movement(self):
        """Toggle movement bot"""
        if not self.controller:
            self.log("Controller not connected")
            return
        is_enabled = self.controller.toggle_movement()
        if is_enabled:
            self.movement_button.configure(text="Stop Movement", fg_color="red")
            self.log("Movement bot started")
        else:
            self.movement_button.configure(text="Start Movement", fg_color="green")
            self.log("Movement bot stopped")
    
    def toggle_anti_afk(self):
        """Toggle anti-AFK"""
        if not self.controller:
            self.log("Controller not connected")
            return
        is_enabled = self.controller.toggle_anti_afk()
        if is_enabled:
            self.anti_afk_button.configure(text="Stop Anti-AFK", fg_color="red")
            self.log("Anti-AFK started")
        else:
            self.anti_afk_button.configure(text="Start Anti-AFK", fg_color="green")
            self.log("Anti-AFK stopped")
    
    def select_class(self):
        """Handle class selection button press"""
        if not self.controller:
            self.log("Controller not connected")
            return
        self.log("Starting class selection...")
        if self.controller.select_class():
            self.log("Class selection complete")
        else:
            self.log("Class selection failed")
    
    def log(self, message):
        """Add message to log display"""
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")
    
    def cleanup(self):
        """Clean up resources"""
        if self.controller:
            self.controller.stop()
    
    def run(self):
        """Start the GUI"""
        try:
            self.window.mainloop()
        finally:
            self.cleanup()

if __name__ == "__main__":
    gui = AutomatorGUI()
    gui.run()