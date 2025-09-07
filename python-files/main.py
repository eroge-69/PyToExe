import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import os
from PIL import Image, ImageDraw, ImageFont
import random
import threading
import time

# --- MODERN THEME CONFIGURATION ---
class ModernTheme:
    # Color Palette - Dark Modern Theme
    BG_PRIMARY = "#0a0a0a"
    BG_SECONDARY = "#141414"
    BG_TERTIARY = "#1a1a1a"
    BG_CARD = "#1f1f1f"
    
    ACCENT_PRIMARY = "#00d4ff"  # Cyan
    ACCENT_SECONDARY = "#ff6b35"  # Orange
    ACCENT_SUCCESS = "#00ff88"  # Green
    ACCENT_WARNING = "#ffd700"  # Gold
    ACCENT_ERROR = "#ff3366"  # Red
    
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#a0a0a0"
    TEXT_MUTED = "#606060"
    
    GRADIENT_START = "#00d4ff"
    GRADIENT_END = "#0099cc"
    
    # Modern rounded corners
    CORNER_RADIUS = 12
    BUTTON_RADIUS = 8
    
    # Shadows and effects
    SHADOW_COLOR = "#000000"
    GLOW_COLOR = "#00d4ff"

# --- DATA ---
POTENTIAL_MAPS = {
    "Serpent Beach": ["TMM_P_Beach_v02", "TMM_Beach_P_v04", "SG_Serpentbeach_P", "SG_SerpentBeach_RW_P"],
    "Jaguar Falls": ["TMM_P_Temple_v02", "TMM_Falls_P_v04", "SG_Jaguarfalls_P", "SG_JaguarFalls_Rework_P"],
    "Fish Market": ["FMM_P_Dock_v02", "SG_Fishmarket_P"],
    "Frog Isle": ["TMM_P_Isle_v02", "SG_FrogIsle_P", "SG_FrogIsle_V2_P"],
    "Ice Mines": ["IMM_P_Mine_v02", "IMM_Mines_P_v04", "SG_Icemines_P"],
    "Frozen Guard": ["IMM_P_Igloo_v02", "SG_FrozenGuard_P", "SGA_SG_FrozenGuard_P"],
    "Stone Keep": ["KMM_P_v01", "SG_Stonekeep_P", "SG_StoneKeep_V2_P", "SG_StoneKeep_V2_DAY_P"],
    "Brightmarsh": ["BMM_P_v01", "SG_Brightmarsh_P"],
    "Ascension Peak": ["QMM_P_v01", "SG_Ascensionpeak_P"],
    "Battle Grounds": ["BG_P"]
}

GAMEMODES = {
    "Siege (Standard)": "TgGame.TgGame_Paladins_Siege",
    "Siege (Chaos)": "TgGame.TgGame_ChaosSiege_CaptureAndPayload",
    "Battlegrounds": "TgGame.TgGame_Royale"
}

CHAMPIONS_OB57 = sorted(["Androxus","Ash","Barik","Bomb King","Buck","Cassie","Drogoz","Evie",
                         "Fernando","Grohk","Grover","Inara","Jenos","Kinessa","Lex","Lian",
                         "Maeve","Makoa","Mal'Damba","Pip","Ruckus","Seris","Sha Lin","Skye",
                         "Strix","Talus","Torvald","Tyra","Viktor","Willo","Ying","Zhin"])

# --- CUSTOM MODERN WIDGETS ---
class ModernButton(ctk.CTkButton):
    def __init__(self, parent, text="", command=None, variant="primary", **kwargs):
        colors = {
            "primary": (ModernTheme.ACCENT_PRIMARY, "#0099cc"),
            "secondary": (ModernTheme.BG_CARD, ModernTheme.BG_SECONDARY),
            "success": (ModernTheme.ACCENT_SUCCESS, "#00cc66"),
            "error": (ModernTheme.ACCENT_ERROR, "#cc0033")
        }
        
        fg_color, hover_color = colors.get(variant, colors["primary"])
        
        super().__init__(
            parent,
            text=text,
            command=command,
            fg_color=fg_color,
            hover_color=hover_color,
            corner_radius=ModernTheme.BUTTON_RADIUS,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            **kwargs
        )
        
        # Add hover animation
        self.bind("<Enter>", self._on_hover_enter)
        self.bind("<Leave>", self._on_hover_leave)
    
    def _on_hover_enter(self, event):
        self.configure(height=42)
    
    def _on_hover_leave(self, event):
        self.configure(height=40)

class ModernCard(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            fg_color=ModernTheme.BG_CARD,
            corner_radius=ModernTheme.CORNER_RADIUS,
            **kwargs
        )

class AnimatedLabel(ctk.CTkLabel):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.original_color = kwargs.get("text_color", ModernTheme.TEXT_PRIMARY)
        
    def pulse(self, color=ModernTheme.ACCENT_PRIMARY, duration=1000):
        """Pulse animation for the label"""
        self.configure(text_color=color)
        self.after(duration, lambda: self.configure(text_color=self.original_color))

class ModernDropdown(ctk.CTkOptionMenu):
    def __init__(self, parent, values=[], command=None, **kwargs):
        super().__init__(
            parent,
            values=values if values else ["No options"],
            command=command,
            fg_color=ModernTheme.BG_TERTIARY,
            button_color=ModernTheme.BG_SECONDARY,
            button_hover_color=ModernTheme.ACCENT_PRIMARY,
            dropdown_fg_color=ModernTheme.BG_SECONDARY,
            dropdown_hover_color=ModernTheme.BG_CARD,
            dropdown_text_color=ModernTheme.TEXT_PRIMARY,
            text_color=ModernTheme.TEXT_PRIMARY,
            font=ctk.CTkFont(size=13),
            dropdown_font=ctk.CTkFont(size=12),
            corner_radius=ModernTheme.BUTTON_RADIUS,
            **kwargs
        )
        
        # Enable mouse wheel scrolling
        self._dropdown_menu.bind_all("<MouseWheel>", self._on_mousewheel)
    
    def _on_mousewheel(self, event):
        if hasattr(self, '_dropdown_menu') and self._dropdown_menu.winfo_ismapped():
            current_values = self._values
            if not current_values:
                return
            
            current_index = current_values.index(self.get()) if self.get() in current_values else 0
            
            if event.delta > 0:  # Scroll up
                new_index = max(0, current_index - 1)
            else:  # Scroll down
                new_index = min(len(current_values) - 1, current_index + 1)
            
            self.set(current_values[new_index])
            if self._command:
                self._command(current_values[new_index])

class GlowingEntry(ctk.CTkEntry):
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            fg_color=ModernTheme.BG_TERTIARY,
            border_color=ModernTheme.BG_SECONDARY,
            text_color=ModernTheme.TEXT_PRIMARY,
            font=ctk.CTkFont(family="Fira Code", size=12),
            corner_radius=ModernTheme.BUTTON_RADIUS,
            **kwargs
        )
        
        self.bind("<FocusIn>", lambda e: self.configure(border_color=ModernTheme.ACCENT_PRIMARY))
        self.bind("<FocusOut>", lambda e: self.configure(border_color=ModernTheme.BG_SECONDARY))

class StatusBar(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=ModernTheme.BG_SECONDARY, height=50)
        
        self.icon_label = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=20),
            text_color=ModernTheme.TEXT_PRIMARY
        )
        self.icon_label.pack(side="left", padx=15)
        
        self.text_label = AnimatedLabel(
            self, text="", font=ctk.CTkFont(size=14),
            text_color=ModernTheme.TEXT_SECONDARY
        )
        self.text_label.pack(side="left", padx=5, expand=True, fill="x")
        
        self.progress = ctk.CTkProgressBar(
            self, width=200, height=4,
            fg_color=ModernTheme.BG_TERTIARY,
            progress_color=ModernTheme.ACCENT_PRIMARY
        )
        
    def show_message(self, message, status_type="info", duration=5000):
        icons = {
            "success": "✅",
            "error": "❌",
            "warning": "⚠️",
            "info": "ℹ️",
            "loading": "⏳"
        }
        
        colors = {
            "success": ModernTheme.ACCENT_SUCCESS,
            "error": ModernTheme.ACCENT_ERROR,
            "warning": ModernTheme.ACCENT_WARNING,
            "info": ModernTheme.ACCENT_PRIMARY,
            "loading": ModernTheme.TEXT_SECONDARY
        }
        
        self.icon_label.configure(text=icons.get(status_type, ""))
        self.text_label.configure(text=message, text_color=colors.get(status_type, ModernTheme.TEXT_SECONDARY))
        self.text_label.pulse(colors.get(status_type), 500)
        
        if status_type == "loading":
            self.progress.pack(side="right", padx=15)
            self.progress.start()
        else:
            self.progress.stop()
            self.progress.pack_forget()
        
        if duration > 0:
            self.after(duration, self.clear)
    
    def clear(self):
        self.icon_label.configure(text="")
        self.text_label.configure(text="")
        self.progress.stop()
        self.progress.pack_forget()

# --- MAIN APPLICATION ---
class ModernPaladinsConsole(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Window Configuration
        self.title("Paladins Console Buddy • Modern Edition")
        self.geometry("1000x700")
        self.minsize(900, 600)
        
        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        # Configure window background
        self.configure(fg_color=ModernTheme.BG_PRIMARY)
        
        # Dynamic data
        self.verified_maps = {}
        self.animation_running = False
        
        # Setup UI
        self.setup_ui()
        
        # Start with animation
        self.animate_startup()
    
    def setup_ui(self):
        # Main container with padding
        self.main_container = ctk.CTkFrame(self, fg_color=ModernTheme.BG_PRIMARY)
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        self.create_header()
        
        # Tab view with modern styling
        self.tab_view = ctk.CTkTabview(
            self.main_container,
            fg_color=ModernTheme.BG_SECONDARY,
            segmented_button_fg_color=ModernTheme.BG_TERTIARY,
            segmented_button_selected_color=ModernTheme.ACCENT_PRIMARY,
            segmented_button_selected_hover_color=ModernTheme.ACCENT_PRIMARY,
            segmented_button_unselected_color=ModernTheme.BG_CARD,
            segmented_button_unselected_hover_color=ModernTheme.BG_CARD,
            text_color=ModernTheme.TEXT_SECONDARY,
            corner_radius=ModernTheme.CORNER_RADIUS
        )
        self.tab_view.pack(fill="both", expand=True, pady=(20, 0))
        
        # Add tabs
        self.tab_view.add("🗺️ Map Loader")
        self.tab_view.add("⚡ Quick Commands")
        self.tab_view.add("🎮 Champion Tools")
        
        # Setup tabs
        self.setup_map_loader_tab()
        self.setup_quick_commands_tab()
        self.setup_champion_tools_tab()
        
        # Status bar
        self.status_bar = StatusBar(self)
        self.status_bar.pack(fill="x", side="bottom", pady=(10, 0))
    
    def create_header(self):
        header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))
        
        # Title with gradient effect (simulated)
        title = ctk.CTkLabel(
            header_frame,
            text="PALADINS CONSOLE BUDDY",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=ModernTheme.ACCENT_PRIMARY
        )
        title.pack(side="left")
        
        # Version badge
        version_badge = ctk.CTkFrame(
            header_frame,
            fg_color=ModernTheme.BG_CARD,
            corner_radius=20,
            width=100,
            height=30
        )
        version_badge.pack(side="left", padx=20)
        
        version_label = ctk.CTkLabel(
            version_badge,
            text="v11.0 MODERN",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=ModernTheme.ACCENT_SUCCESS
        )
        version_label.pack(pady=5, padx=10)
        
        # Settings button (decorative)
        settings_btn = ModernButton(
            header_frame,
            text="⚙️",
            width=40,
            variant="secondary",
            command=self.show_about
        )
        settings_btn.pack(side="right")
    
    def setup_map_loader_tab(self):
        tab = self.tab_view.tab("🗺️ Map Loader")
        
        # Create scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(
            tab,
            fg_color="transparent",
            scrollbar_button_color=ModernTheme.BG_CARD,
            scrollbar_button_hover_color=ModernTheme.ACCENT_PRIMARY
        )
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Verification card
        self.verification_card = ModernCard(scroll_frame)
        self.verification_card.pack(fill="x", pady=(0, 20))
        
        self.setup_verification_ui()
    
    def setup_verification_ui(self):
        # Clear existing widgets
        for widget in self.verification_card.winfo_children():
            widget.destroy()
        
        container = ctk.CTkFrame(self.verification_card, fg_color="transparent")
        container.pack(padx=20, pady=20)
        
        # Icon and title
        title_frame = ctk.CTkFrame(container, fg_color="transparent")
        title_frame.pack(fill="x")
        
        icon = ctk.CTkLabel(
            title_frame,
            text="📁",
            font=ctk.CTkFont(size=40)
        )
        icon.pack(side="left", padx=(0, 15))
        
        title = ctk.CTkLabel(
            title_frame,
            text="Map Verification Required",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=ModernTheme.TEXT_PRIMARY
        )
        title.pack(side="left")
        
        info = ctk.CTkLabel(
            container,
            text="Select your Paladins 'CookedPCConsole' folder to scan for available maps",
            font=ctk.CTkFont(size=13),
            text_color=ModernTheme.TEXT_SECONDARY
        )
        info.pack(pady=(10, 20))
        
        select_btn = ModernButton(
            container,
            text="Select Game Folder",
            command=self.verify_maps,
            width=200
        )
        select_btn.pack()
    
    def setup_map_controls(self):
        # Clear and rebuild with controls
        for widget in self.verification_card.winfo_children():
            widget.destroy()
        
        container = ctk.CTkFrame(self.verification_card, fg_color="transparent")
        container.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Success header
        success_frame = ctk.CTkFrame(container, fg_color="transparent")
        success_frame.pack(fill="x", pady=(0, 20))
        
        success_icon = ctk.CTkLabel(
            success_frame,
            text="✅",
            font=ctk.CTkFont(size=24)
        )
        success_icon.pack(side="left", padx=(0, 10))
        
        success_text = ctk.CTkLabel(
            success_frame,
            text=f"Found {len(self.verified_maps)} verified maps",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=ModernTheme.ACCENT_SUCCESS
        )
        success_text.pack(side="left")
        
        # Control grid
        controls_frame = ctk.CTkFrame(container, fg_color="transparent")
        controls_frame.pack(fill="both", expand=True)
        
        # Map selection
        map_label = ctk.CTkLabel(
            controls_frame,
            text="SELECT MAP",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=ModernTheme.TEXT_MUTED
        )
        map_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.map_dropdown = ModernDropdown(
            controls_frame,
            values=list(self.verified_maps.keys()),
            command=self.on_map_select,
            width=250
        )
        self.map_dropdown.grid(row=1, column=0, padx=(0, 10), sticky="ew")
        
        # Version selection
        version_label = ctk.CTkLabel(
            controls_frame,
            text="MAP VERSION",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=ModernTheme.TEXT_MUTED
        )
        version_label.grid(row=0, column=1, sticky="w", pady=(0, 5))
        
        self.version_dropdown = ModernDropdown(
            controls_frame,
            values=[],
            command=self.update_command,
            width=250
        )
        self.version_dropdown.grid(row=1, column=1, padx=(0, 10), sticky="ew")
        
        # Gamemode selection
        mode_label = ctk.CTkLabel(
            controls_frame,
            text="GAME MODE",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=ModernTheme.TEXT_MUTED
        )
        mode_label.grid(row=2, column=0, sticky="w", pady=(20, 5))
        
        self.mode_dropdown = ModernDropdown(
            controls_frame,
            values=list(GAMEMODES.keys()),
            command=self.update_command,
            width=250
        )
        self.mode_dropdown.grid(row=3, column=0, padx=(0, 10), sticky="ew")
        
        # Command output
        output_card = ModernCard(container)
        output_card.pack(fill="x", pady=(30, 0))
        
        output_container = ctk.CTkFrame(output_card, fg_color="transparent")
        output_container.pack(padx=15, pady=15, fill="x")
        
        output_label = ctk.CTkLabel(
            output_container,
            text="GENERATED COMMAND",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=ModernTheme.TEXT_MUTED
        )
        output_label.pack(anchor="w", pady=(0, 10))
        
        self.command_var = tk.StringVar()
        self.command_entry = GlowingEntry(
            output_container,
            textvariable=self.command_var,
            state="readonly",
            height=40
        )
        self.command_entry.pack(fill="x", pady=(0, 10))
        
        copy_btn = ModernButton(
            output_container,
            text="📋 Copy Command",
            command=self.copy_command,
            variant="primary",
            width=150
        )
        copy_btn.pack()
        
        # Initialize
        if self.verified_maps:
            first_map = list(self.verified_maps.keys())[0]
            self.map_dropdown.set(first_map)
            self.on_map_select(first_map)
    
    def setup_quick_commands_tab(self):
        tab = self.tab_view.tab("⚡ Quick Commands")
        
        scroll_frame = ctk.CTkScrollableFrame(
            tab,
            fg_color="transparent",
            scrollbar_button_color=ModernTheme.BG_CARD,
            scrollbar_button_hover_color=ModernTheme.ACCENT_PRIMARY
        )
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        commands = [
            ("🛡️ God Mode", "god", "Become invincible"),
            ("❄️ No Cooldowns", "cooldown", "Remove all ability cooldowns"),
            ("⚡ Fill Ultimate", "fillenergy", "Instantly charge ultimate"),
            ("👻 Ghost Mode", "ghost", "Walk through walls"),
            ("🚶 Normal Mode", "walk", "Return to normal state"),
            ("👁️ Third Person", "Set3p", "Switch to third person view"),
            ("🎯 First Person", "Set1p", "Switch to first person view"),
            ("🤖 Freeze Bots", "freezeai", "Stop all bot movement"),
            ("🐎 Enable Mounts", "allowmount 1", "Enable alpha mount animations"),
            ("🚪 Disconnect", "disconnect", "Return to login screen")
        ]
        
        for i, (name, command, desc) in enumerate(commands):
            card = ModernCard(scroll_frame)
            card.pack(fill="x", pady=5)
            
            content = ctk.CTkFrame(card, fg_color="transparent")
            content.pack(padx=15, pady=12, fill="x")
            
            # Left side - info
            info_frame = ctk.CTkFrame(content, fg_color="transparent")
            info_frame.pack(side="left", fill="x", expand=True)
            
            name_label = ctk.CTkLabel(
                info_frame,
                text=name,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=ModernTheme.TEXT_PRIMARY,
                anchor="w"
            )
            name_label.pack(anchor="w")
            
            desc_label = ctk.CTkLabel(
                info_frame,
                text=desc,
                font=ctk.CTkFont(size=11),
                text_color=ModernTheme.TEXT_MUTED,
                anchor="w"
            )
            desc_label.pack(anchor="w")
            
            # Right side - button
            copy_btn = ModernButton(
                content,
                text="Copy",
                command=lambda c=command: self.copy_to_clipboard(c),
                variant="secondary",
                width=80
            )
            copy_btn.pack(side="right")
    
    def setup_champion_tools_tab(self):
        tab = self.tab_view.tab("🎮 Champion Tools")
        
        container = ctk.CTkFrame(tab, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Switch champion card
        switch_card = ModernCard(container)
        switch_card.pack(fill="x", pady=(0, 20))
        
        switch_container = ctk.CTkFrame(switch_card, fg_color="transparent")
        switch_container.pack(padx=20, pady=20, fill="x")
        
        switch_title = ctk.CTkLabel(
            switch_container,
            text="🔄 SWITCH CHAMPION",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=ModernTheme.ACCENT_PRIMARY
        )
        switch_title.pack(anchor="w", pady=(0, 10))
        
        switch_frame = ctk.CTkFrame(switch_container, fg_color="transparent")
        switch_frame.pack(fill="x")
        
        self.switch_dropdown = ModernDropdown(
            switch_frame,
            values=CHAMPIONS_OB57,
            width=200
        )
        self.switch_dropdown.pack(side="left", padx=(0, 10))
        
        switch_btn = ModernButton(
            switch_frame,
            text="Copy Switch Command",
            command=lambda: self.copy_to_clipboard(f"switchclass {self.switch_dropdown.get()}"),
            variant="primary"
        )
        switch_btn.pack(side="left")
        
        # Spawn bot card
        spawn_card = ModernCard(container)
        spawn_card.pack(fill="x")
        
        spawn_container = ctk.CTkFrame(spawn_card, fg_color="transparent")
        spawn_container.pack(padx=20, pady=20, fill="x")
        
        spawn_title = ctk.CTkLabel(
            spawn_container,
            text="🤖 SPAWN BOTS",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=ModernTheme.ACCENT_PRIMARY
        )
        spawn_title.pack(anchor="w", pady=(0, 10))
        
        spawn_frame = ctk.CTkFrame(spawn_container, fg_color="transparent")
        spawn_frame.pack(fill="x")
        
        # Champion selection
        champ_frame = ctk.CTkFrame(spawn_frame, fg_color="transparent")
        champ_frame.pack(side="left", padx=(0, 15))
        
        ctk.CTkLabel(
            champ_frame,
            text="Champion",
            font=ctk.CTkFont(size=11),
            text_color=ModernTheme.TEXT_MUTED
        ).pack(anchor="w")
        
        self.spawn_champ = ModernDropdown(
            champ_frame,
            values=CHAMPIONS_OB57,
            width=150
        )
        self.spawn_champ.pack()
        
        # Team selection
        team_frame = ctk.CTkFrame(spawn_frame, fg_color="transparent")
        team_frame.pack(side="left", padx=(0, 15))
        
        ctk.CTkLabel(
            team_frame,
            text="Team",
            font=ctk.CTkFont(size=11),
            text_color=ModernTheme.TEXT_MUTED
        ).pack(anchor="w")
        
        self.spawn_team = ModernDropdown(
            team_frame,
            values=["Team 1 (Ally)", "Team 2 (Enemy)"],
            width=150,
            command=self.on_team_change
        )
        self.spawn_team.pack()
        
        # Amount selection
        amount_frame = ctk.CTkFrame(spawn_frame, fg_color="transparent")
        amount_frame.pack(side="left", padx=(0, 15))
        
        ctk.CTkLabel(
            amount_frame,
            text="Amount",
            font=ctk.CTkFont(size=11),
            text_color=ModernTheme.TEXT_MUTED
        ).pack(anchor="w")
        
        self.spawn_amount = ModernDropdown(
            amount_frame,
            values=["1", "2", "3"],
            width=80
        )
        self.spawn_amount.pack()
        
        # Spawn button
        spawn_btn = ModernButton(
            spawn_frame,
            text="Copy Spawn Command",
            command=self.copy_spawn_command,
            variant="primary"
        )
        spawn_btn.pack(side="left", padx=(20, 0))
    
    # --- FUNCTIONALITY ---
    def verify_maps(self):
        self.status_bar.show_message("Scanning for game files...", "loading", 0)
        
        game_path = filedialog.askdirectory(
            title="Select 'CookedPCConsole' Folder",
            initialdir=os.getcwd()
        )
        
        if not game_path:
            self.status_bar.show_message("Map verification cancelled", "warning")
            return
        
        try:
            # Scan for files
            all_files = {f.replace('.upk', '') for f in os.listdir(game_path) if f.endswith('.upk')}
            
            # Filter maps
            for map_name, map_codes in POTENTIAL_MAPS.items():
                existing = [code for code in map_codes if code in all_files]
                if existing:
                    self.verified_maps[map_name] = existing
            
            if self.verified_maps:
                self.status_bar.show_message(f"Successfully verified {len(self.verified_maps)} maps!", "success")
                self.setup_map_controls()
            else:
                self.status_bar.show_message("No maps found in selected folder", "error")
        
        except Exception as e:
            self.status_bar.show_message(f"Error: {str(e)}", "error")
    
    def on_map_select(self, map_name):
        versions = self.verified_maps.get(map_name, [])
        self.version_dropdown.configure(values=versions)
        if versions:
            self.version_dropdown.set(versions[0])
        self.update_command()
    
    def on_team_change(self, team):
        if "Team 1" in team:
            self.spawn_amount.configure(values=["1", "2", "3"])
        else:
            self.spawn_amount.configure(values=["1", "2", "3", "4", "5"])
        self.spawn_amount.set("1")
    
    def update_command(self, _=None):
        if not hasattr(self, 'version_dropdown'):
            return
        
        map_version = self.version_dropdown.get()
        gamemode = self.mode_dropdown.get()
        
        if map_version and gamemode and gamemode in GAMEMODES:
            command = f"switchlevel {map_version}?game={GAMEMODES[gamemode]}"
            self.command_var.set(command)
    
    def copy_command(self):
        command = self.command_var.get()
        if command:
            self.copy_to_clipboard(command)
    
    def copy_spawn_command(self):
        champ = self.spawn_champ.get()
        team = "1" if "Team 1" in self.spawn_team.get() else "2"
        amount = self.spawn_amount.get()
        command = f"spawnbot {champ} {team} {amount}"
        self.copy_to_clipboard(command)
    
    def copy_to_clipboard(self, text):
        if not text:
            self.status_bar.show_message("Nothing to copy", "error")
            return
        
        try:
            self.clipboard_clear()
            self.clipboard_append(text)
            self.status_bar.show_message(f"Copied: {text}", "success", 3000)
        except Exception as e:
            self.status_bar.show_message(f"Copy failed: {str(e)}", "error")
    
    def show_about(self):
        """Show about dialog with animation"""
        about_window = ctk.CTkToplevel(self)
        about_window.title("About")
        about_window.geometry("400x300")
        about_window.resizable(False, False)
        about_window.configure(fg_color=ModernTheme.BG_SECONDARY)
        
        # Center the window
        about_window.transient(self)
        about_window.grab_set()
        
        # Content
        content = ctk.CTkFrame(about_window, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Logo/Icon
        logo = ctk.CTkLabel(
            content,
            text="🎮",
            font=ctk.CTkFont(size=60)
        )
        logo.pack(pady=(0, 20))
        
        # Title
        title = ctk.CTkLabel(
            content,
            text="Paladins Console Buddy",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=ModernTheme.ACCENT_PRIMARY
        )
        title.pack()
        
        # Version
        version = ctk.CTkLabel(
            content,
            text="Version 11.0 - Modern Edition",
            font=ctk.CTkFont(size=12),
            text_color=ModernTheme.TEXT_SECONDARY
        )
        version.pack(pady=(5, 20))
        
        # Description
        desc = ctk.CTkLabel(
            content,
            text="A modern tool for Paladins OB57 console commands\nwith sleek UI and enhanced user experience.",
            font=ctk.CTkFont(size=11),
            text_color=ModernTheme.TEXT_MUTED,
            justify="center"
        )
        desc.pack(pady=(0, 30))
        
        # Close button
        close_btn = ModernButton(
            content,
            text="Close",
            command=about_window.destroy,
            variant="primary",
            width=100
        )
        close_btn.pack()
    
    def animate_startup(self):
        """Smooth startup animation"""
        self.withdraw()  # Hide window initially
        self.after(100, self._fade_in)
    
    def _fade_in(self):
        self.deiconify()  # Show window
        self.attributes('-alpha', 0.0)
        
        def fade(alpha=0.0):
            if alpha < 1.0:
                alpha += 0.05
                self.attributes('-alpha', alpha)
                self.after(20, lambda: fade(alpha))
            else:
                self.attributes('-alpha', 1.0)
        
        fade()

# --- ENHANCED SCROLLABLE DROPDOWN ---
class ScrollableDropdown(ctk.CTkOptionMenu):
    """Enhanced dropdown with better scroll wheel support"""
    def __init__(self, parent, values=[], command=None, **kwargs):
        super().__init__(parent, values=values, command=command, **kwargs)
        
        # Bind mouse wheel globally when dropdown is focused
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self._scroll_active = False
    
    def _on_enter(self, event):
        self._scroll_active = True
        self.bind_all("<MouseWheel>", self._on_scroll)
        self.bind_all("<Button-4>", self._on_scroll)  # Linux
        self.bind_all("<Button-5>", self._on_scroll)  # Linux
    
    def _on_leave(self, event):
        self._scroll_active = False
        self.unbind_all("<MouseWheel>")
        self.unbind_all("<Button-4>")
        self.unbind_all("<Button-5>")
    
    def _on_scroll(self, event):
        if not self._scroll_active or not self._values:
            return
        
        current_index = self._values.index(self.get()) if self.get() in self._values else 0
        
        # Determine scroll direction
        if event.num == 4 or event.delta > 0:  # Scroll up
            new_index = max(0, current_index - 1)
        elif event.num == 5 or event.delta < 0:  # Scroll down
            new_index = min(len(self._values) - 1, current_index + 1)
        else:
            return
        
        self.set(self._values[new_index])
        if self._command:
            self._command(self._values[new_index])

# --- ANIMATED PROGRESS INDICATOR ---
class AnimatedProgress(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        self.dots = []
        for i in range(3):
            dot = ctk.CTkLabel(
                self,
                text="●",
                font=ctk.CTkFont(size=20),
                text_color=ModernTheme.ACCENT_PRIMARY
            )
            dot.grid(row=0, column=i, padx=5)
            self.dots.append(dot)
        
        self.current = 0
        self.animating = False
    
    def start(self):
        self.animating = True
        self._animate()
    
    def stop(self):
        self.animating = False
        for dot in self.dots:
            dot.configure(text_color=ModernTheme.ACCENT_PRIMARY)
    
    def _animate(self):
        if not self.animating:
            return
        
        for i, dot in enumerate(self.dots):
            if i == self.current:
                dot.configure(text_color=ModernTheme.ACCENT_SUCCESS)
            else:
                dot.configure(text_color=ModernTheme.TEXT_MUTED)
        
        self.current = (self.current + 1) % len(self.dots)
        self.after(300, self._animate)

# --- TOOLTIP SUPPORT ---
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show)
        self.widget.bind("<Leave>", self.hide)
    
    def show(self, event=None):
        if self.tooltip:
            return
        
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        self.tooltip = ctk.CTkToplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        label = ctk.CTkLabel(
            self.tooltip,
            text=self.text,
            fg_color=ModernTheme.BG_CARD,
            corner_radius=6,
            text_color=ModernTheme.TEXT_PRIMARY,
            font=ctk.CTkFont(size=11)
        )
        label.pack(padx=10, pady=5)
    
    def hide(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

# --- MAIN ENTRY POINT ---
if __name__ == "__main__":
    app = ModernPaladinsConsole()
    
    # Add some tooltips
    app.after(1000, lambda: [
        ToolTip(app.tab_view._segmented_button._buttons_dict["🗺️ Map Loader"], 
                "Load custom maps with verified game files"),
        ToolTip(app.tab_view._segmented_button._buttons_dict["⚡ Quick Commands"], 
                "Quick access to common console commands"),
        ToolTip(app.tab_view._segmented_button._buttons_dict["🎮 Champion Tools"], 
                "Champion switching and bot spawning tools")
    ])
    
    app.mainloop()