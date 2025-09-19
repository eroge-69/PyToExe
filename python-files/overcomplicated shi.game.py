import tkinter as tk
from tkinter import ttk, messagebox
import json
import time
from math import floor

class AdvancedClickerGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Clicker Game")
        self.root.geometry("800x600")
        
        # Theme settings
        self.dark_mode = False
        self.themes = {
            "light": {
                "bg": "#F0F0F0",
                "fg": "#000000",
                "button_bg": "#E0E0E0",
                "button_fg": "#000000",
                "frame_bg": "#E8E8E8",
                "text_bg": "#FFFFFF",
                "text_fg": "#000000",
                "accent1": "#4CAF50",
                "accent2": "#2196F3",
                "accent3": "#FF9800",
                "accent4": "#9C27B0",
                "accent5": "#607D8B",
                "accent6": "#F44336"
            },
            "dark": {
                "bg": "#121212",
                "fg": "#FFFFFF",
                "button_bg": "#2D2D2D",
                "button_fg": "#FFFFFF",
                "frame_bg": "#1E1E1E",
                "text_bg": "#2D2D2D",
                "text_fg": "#FFFFFF",
                "accent1": "#388E3C",
                "accent2": "#1976D2",
                "accent3": "#F57C00",
                "accent4": "#7B1FA2",
                "accent5": "#455A64",
                "accent6": "#D32F2F"
            }
        }
        
        # Fullscreen state
        self.fullscreen = False
        
        # Game state
        self.clicks = 0
        self.click_power = 1
        self.autoclickers = 0
        self.autoclick_power = 0.1
        self.passive_income = 0
        self.last_update_time = time.time()
        self.upgrades = {
            "click_power": {"level": 1, "cost": 10, "cost_multiplier": 1.5},
            "autoclicker": {"level": 0, "cost": 15, "cost_multiplier": 1.8},
            "passive_income": {"level": 0, "cost": 50, "cost_multiplier": 2.0}
        }
        self.achievements = {
            "first_click": {"achieved": False, "name": "First Click!", "description": "Make your first click"},
            "hundred_clicks": {"achieved": False, "name": "100 Clicks!", "description": "Reach 100 clicks"},
            "thousand_clicks": {"achieved": False, "name": "1,000 Clicks!", "description": "Reach 1,000 clicks"},
            "first_upgrade": {"achieved": False, "name": "First Upgrade", "description": "Purchase your first upgrade"},
            "millionaire": {"achieved": False, "name": "Millionaire", "description": "Reach 1,000,000 clicks"}
        }
        
        # Load saved game if available
        self.load_game()
        
        # Setup UI
        self.setup_ui()
        
        # Bind keyboard shortcuts
        self.root.bind('<F11>', self.toggle_fullscreen)
        self.root.bind('<Escape>', self.exit_fullscreen)
        self.root.bind('<t>', self.toggle_theme)
        
        # Start the game loop
        self.update_game()
    
    def setup_ui(self):
        # Configure style
        self.style = ttk.Style()
        self.style.configure("TFrame", background=self.get_theme_color("bg"))
        self.style.configure("TLabelframe", background=self.get_theme_color("frame_bg"))
        self.style.configure("TLabelframe.Label", background=self.get_theme_color("frame_bg"), 
                            foreground=self.get_theme_color("fg"))
        
        # Configure root background
        self.root.configure(bg=self.get_theme_color("bg"))
        
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Top button frame
        top_button_frame = ttk.Frame(self.main_frame)
        top_button_frame.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky=(tk.E, tk.W))
        
        # Theme toggle button
        self.theme_button = tk.Button(top_button_frame, text="🌙 Dark Mode", command=self.toggle_theme, 
                                     bg=self.get_theme_color("button_bg"), fg=self.get_theme_color("button_fg"),
                                     relief="flat", font=("Arial", 10))
        self.theme_button.pack(side=tk.LEFT)
        
        # Fullscreen toggle button
        self.fullscreen_button = tk.Button(top_button_frame, text="⛶ Fullscreen", command=self.toggle_fullscreen, 
                                         bg=self.get_theme_color("button_bg"), fg=self.get_theme_color("button_fg"),
                                         relief="flat", font=("Arial", 10))
        self.fullscreen_button.pack(side=tk.RIGHT)
        
        # Click button
        self.click_button = tk.Button(self.main_frame, text="CLICK ME!", font=("Arial", 24, "bold"), 
                                     command=self.click, bg=self.get_theme_color("accent1"), fg="white", 
                                     height=3, width=15)
        self.click_button.grid(row=1, column=0, columnspan=2, pady=20, padx=10)
        
        # Stats frame
        self.stats_frame = ttk.LabelFrame(self.main_frame, text="Stats", padding="10")
        self.stats_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        self.clicks_label = tk.Label(self.stats_frame, text="Clicks: 0", font=("Arial", 14), 
                                    bg=self.get_theme_color("text_bg"), fg=self.get_theme_color("text_fg"))
        self.clicks_label.grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        
        self.click_power_label = tk.Label(self.stats_frame, text="Click Power: 1", font=("Arial", 12), 
                                         bg=self.get_theme_color("text_bg"), fg=self.get_theme_color("text_fg"))
        self.click_power_label.grid(row=1, column=0, sticky=tk.W, pady=2, padx=5)
        
        self.autoclickers_label = tk.Label(self.stats_frame, text="Auto-Clickers: 0", font=("Arial", 12), 
                                          bg=self.get_theme_color("text_bg"), fg=self.get_theme_color("text_fg"))
        self.autoclickers_label.grid(row=2, column=0, sticky=tk.W, pady=2, padx=5)
        
        self.passive_income_label = tk.Label(self.stats_frame, text="Passive Income: 0/sec", font=("Arial", 12), 
                                            bg=self.get_theme_color("text_bg"), fg=self.get_theme_color("text_fg"))
        self.passive_income_label.grid(row=3, column=0, sticky=tk.W, pady=2, padx=5)
        
        # Upgrades frame
        self.upgrades_frame = ttk.LabelFrame(self.main_frame, text="Upgrades", padding="10")
        self.upgrades_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # Click power upgrade
        self.click_power_btn = tk.Button(self.upgrades_frame, text="Upgrade Click Power (10)", 
                                        command=lambda: self.buy_upgrade("click_power"), 
                                        bg=self.get_theme_color("accent2"), fg="white", width=25)
        self.click_power_btn.grid(row=0, column=0, pady=5)
        
        # Auto-clicker upgrade
        self.autoclicker_btn = tk.Button(self.upgrades_frame, text="Buy Auto-Clicker (15)", 
                                        command=lambda: self.buy_upgrade("autoclicker"), 
                                        bg=self.get_theme_color("accent3"), fg="white", width=25)
        self.autoclicker_btn.grid(row=1, column=0, pady=5)
        
        # Passive income upgrade
        self.passive_income_btn = tk.Button(self.upgrades_frame, text="Buy Passive Income (50)", 
                                           command=lambda: self.buy_upgrade("passive_income"), 
                                           bg=self.get_theme_color("accent4"), fg="white", width=25)
        self.passive_income_btn.grid(row=2, column=0, pady=5)
        
        # Achievements frame
        self.achievements_frame = ttk.LabelFrame(self.main_frame, text="Achievements", padding="10")
        self.achievements_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        self.achievements_text = tk.Text(self.achievements_frame, height=6, width=70, state=tk.DISABLED,
                                        bg=self.get_theme_color("text_bg"), fg=self.get_theme_color("text_fg"),
                                        relief="flat")
        self.achievements_text.grid(row=0, column=0, pady=5)
        
        # Button frame
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        # Save button
        self.save_button = tk.Button(button_frame, text="Save Game", command=self.save_game, 
                               bg=self.get_theme_color("accent5"), fg="white", width=15)
        self.save_button.pack(side=tk.LEFT, padx=10)
        
        # Reset button
        self.reset_button = tk.Button(button_frame, text="Reset Game", command=self.reset_game, 
                                bg=self.get_theme_color("accent6"), fg="white", width=15)
        self.reset_button.pack(side=tk.RIGHT, padx=10)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(2, weight=1)
        self.main_frame.rowconfigure(3, weight=1)
        
        # Initialize achievements display
        self.update_achievements_display()
    
    def get_theme_color(self, color_key):
        theme = "dark" if self.dark_mode else "light"
        return self.themes[theme][color_key]
    
    def apply_theme(self):
        # Update root background
        self.root.configure(bg=self.get_theme_color("bg"))
        
        # Update style configurations
        self.style.configure("TFrame", background=self.get_theme_color("bg"))
        self.style.configure("TLabelframe", background=self.get_theme_color("frame_bg"))
        self.style.configure("TLabelframe.Label", background=self.get_theme_color("frame_bg"), 
                            foreground=self.get_theme_color("fg"))
        
        # Update all widgets
        self.update_widget_colors(self.root)
        
        # Update button texts
        self.theme_button.config(text="☀️ Light Mode" if self.dark_mode else "🌙 Dark Mode",
                                bg=self.get_theme_color("button_bg"), fg=self.get_theme_color("button_fg"))
        
        self.fullscreen_button.config(text="❐ Exit Fullscreen" if self.fullscreen else "⛶ Fullscreen",
                                    bg=self.get_theme_color("button_bg"), fg=self.get_theme_color("button_fg"))
        
        # Update click button
        self.click_button.config(bg=self.get_theme_color("accent1"))
        
        # Update upgrade buttons
        self.click_power_btn.config(bg=self.get_theme_color("accent2"))
        self.autoclicker_btn.config(bg=self.get_theme_color("accent3"))
        self.passive_income_btn.config(bg=self.get_theme_color("accent4"))
        
        # Update action buttons
        self.save_button.config(bg=self.get_theme_color("accent5"))
        self.reset_button.config(bg=self.get_theme_color("accent6"))
        
        # Update labels
        self.clicks_label.config(bg=self.get_theme_color("text_bg"), fg=self.get_theme_color("text_fg"))
        self.click_power_label.config(bg=self.get_theme_color("text_bg"), fg=self.get_theme_color("text_fg"))
        self.autoclickers_label.config(bg=self.get_theme_color("text_bg"), fg=self.get_theme_color("text_fg"))
        self.passive_income_label.config(bg=self.get_theme_color("text_bg"), fg=self.get_theme_color("text_fg"))
        
        # Update achievements text
        self.achievements_text.config(bg=self.get_theme_color("text_bg"), fg=self.get_theme_color("text_fg"))
        self.update_achievements_display()
    
    def update_widget_colors(self, widget):
        # Recursively update widget colors based on current theme
        try:
            if isinstance(widget, (tk.Label, tk.Button)):
                if isinstance(widget, tk.Label):
                    widget.configure(bg=self.get_theme_color("text_bg"), fg=self.get_theme_color("text_fg"))
                elif isinstance(widget, tk.Button):
                    # Skip buttons with custom colors (handled separately)
                    if widget not in [self.theme_button, self.fullscreen_button, self.click_button, 
                                     self.click_power_btn, self.autoclicker_btn, self.passive_income_btn,
                                     self.save_button, self.reset_button]:
                        widget.configure(bg=self.get_theme_color("button_bg"), fg=self.get_theme_color("button_fg"))
            elif isinstance(widget, (tk.Frame, ttk.Frame, ttk.LabelFrame)):
                if isinstance(widget, tk.Frame):
                    widget.configure(bg=self.get_theme_color("bg"))
                # ttk widgets are handled by style configurations
        except:
            pass
        
        for child in widget.winfo_children():
            self.update_widget_colors(child)
    
    def toggle_theme(self, event=None):
        self.dark_mode = not self.dark_mode
        self.apply_theme()
    
    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)
        self.fullscreen_button.config(text="❐ Exit Fullscreen" if self.fullscreen else "⛶ Fullscreen")
    
    def exit_fullscreen(self, event=None):
        self.fullscreen = False
        self.root.attributes("-fullscreen", False)
        self.fullscreen_button.config(text="⛶ Fullscreen")
    
    def click(self):
        self.clicks += self.click_power
        self.update_stats()
        
        # Check for achievements
        if not self.achievements["first_click"]["achieved"]:
            self.achievements["first_click"]["achieved"] = True
            self.show_achievement("first_click")
        
        if self.clicks >= 100 and not self.achievements["hundred_clicks"]["achieved"]:
            self.achievements["hundred_clicks"]["achieved"] = True
            self.show_achievement("hundred_clicks")
        
        if self.clicks >= 1000 and not self.achievements["thousand_clicks"]["achieved"]:
            self.achievements["thousand_clicks"]["achieved"] = True
            self.show_achievement("thousand_clicks")
            
        if self.clicks >= 1000000 and not self.achievements["millionaire"]["achieved"]:
            self.achievements["millionaire"]["achieved"] = True
            self.show_achievement("millionaire")
    
    def buy_upgrade(self, upgrade_type):
        upgrade = self.upgrades[upgrade_type]
        cost = upgrade["cost"]
        
        if self.clicks >= cost:
            self.clicks -= cost
            upgrade["level"] += 1
            upgrade["cost"] = floor(upgrade["cost"] * upgrade["cost_multiplier"])
            
            if upgrade_type == "click_power":
                self.click_power = upgrade["level"]
            elif upgrade_type == "autoclicker":
                self.autoclickers = upgrade["level"]
            elif upgrade_type == "passive_income":
                self.passive_income = upgrade["level"] * 0.5
            
            self.update_stats()
            self.update_upgrade_buttons()
            
            if not self.achievements["first_upgrade"]["achieved"]:
                self.achievements["first_upgrade"]["achieved"] = True
                self.show_achievement("first_upgrade")
        else:
            messagebox.showinfo("Not Enough Clicks", f"You need {cost} clicks to buy this upgrade!")
    
    def update_game(self):
        current_time = time.time()
        delta_time = current_time - self.last_update_time
        self.last_update_time = current_time
        
        # Add auto-clicker income
        if self.autoclickers > 0:
            self.clicks += self.autoclickers * self.autoclick_power * delta_time
        
        # Add passive income
        if self.passive_income > 0:
            self.clicks += self.passive_income * delta_time
        
        self.update_stats()
        self.root.after(50, self.update_game)  # Update 20 times per second
    
    def update_stats(self):
        self.clicks_label.config(text=f"Clicks: {floor(self.clicks)}")
        self.click_power_label.config(text=f"Click Power: {self.click_power}")
        self.autoclickers_label.config(text=f"Auto-Clickers: {self.autoclickers} ({self.autoclickers * self.autoclick_power:.1f}/sec)")
        self.passive_income_label.config(text=f"Passive Income: {self.passive_income:.1f}/sec")
    
    def update_upgrade_buttons(self):
        self.click_power_btn.config(text=f"Upgrade Click Power ({self.upgrades['click_power']['cost']})")
        self.autoclicker_btn.config(text=f"Buy Auto-Clicker ({self.upgrades['autoclicker']['cost']})")
        self.passive_income_btn.config(text=f"Buy Passive Income ({self.upgrades['passive_income']['cost']})")
    
    def show_achievement(self, achievement_key):
        achievement = self.achievements[achievement_key]
        messagebox.showinfo("Achievement Unlocked!", 
                           f"{achievement['name']}\n{achievement['description']}")
        self.update_achievements_display()
    
    def update_achievements_display(self):
        self.achievements_text.config(state=tk.NORMAL)
        self.achievements_text.delete(1.0, tk.END)
        
        achieved = [a for a in self.achievements.values() if a["achieved"]]
        not_achieved = [a for a in self.achievements.values() if not a["achieved"]]
        
        if achieved:
            self.achievements_text.insert(tk.END, "Unlocked Achievements:\n", "achieved")
            for achievement in achieved:
                self.achievements_text.insert(tk.END, f"• {achievement['name']}: {achievement['description']}\n", "achieved")
        
        if not_achieved:
            if achieved:
                self.achievements_text.insert(tk.END, "\n")
            self.achievements_text.insert(tk.END, "Locked Achievements:\n", "locked")
            for achievement in not_achieved:
                self.achievements_text.insert(tk.END, f"• {achievement['name']}: {achievement['description']}\n", "locked")
        
        self.achievements_text.tag_config("achieved", foreground="green")
        self.achievements_text.tag_config("locked", foreground="gray")
        self.achievements_text.config(state=tk.DISABLED)
    
    def save_game(self):
        game_data = {
            "clicks": self.clicks,
            "click_power": self.click_power,
            "autoclickers": self.autoclickers,
            "passive_income": self.passive_income,
            "upgrades": self.upgrades,
            "achievements": self.achievements,
            "dark_mode": self.dark_mode
        }
        
        with open("clicker_save.json", "w") as f:
            json.dump(game_data, f)
        
        messagebox.showinfo("Game Saved", "Your progress has been saved successfully!")
    
    def load_game(self):
        try:
            with open("clicker_save.json", "r") as f:
                game_data = json.load(f)
            
            self.clicks = game_data["clicks"]
            self.click_power = game_data["click_power"]
            self.autoclickers = game_data["autoclickers"]
            self.passive_income = game_data["passive_income"]
            self.upgrades = game_data["upgrades"]
            self.achievements = game_data["achievements"]
            self.dark_mode = game_data.get("dark_mode", False)
            
        except FileNotFoundError:
            pass  # No saved game, start fresh
    
    def reset_game(self):
        result = messagebox.askyesno("Reset Game", "Are you sure you want to reset your game? All progress will be lost!")
        if result:
            self.clicks = 0
            self.click_power = 1
            self.autoclickers = 0
            self.passive_income = 0
            
            self.upgrades = {
                "click_power": {"level": 1, "cost": 10, "cost_multiplier": 1.5},
                "autoclicker": {"level": 0, "cost": 15, "cost_multiplier": 1.8},
                "passive_income": {"level": 0, "cost": 50, "cost_multiplier": 2.0}
            }
            
            self.achievements = {
                "first_click": {"achieved": False, "name": "First Click!", "description": "Make your first click"},
                "hundred_clicks": {"achieved": False, "name": "100 Clicks!", "description": "Reach 100 clicks"},
                "thousand_clicks": {"achieved": False, "name": "1,000 Clicks!", "description": "Reach 1,000 clicks"},
                "first_upgrade": {"achieved": False, "name": "First Upgrade", "description": "Purchase your first upgrade"},
                "millionaire": {"achieved": False, "name": "Millionaire", "description": "Reach 1,000,000 clicks"}
            }
            
            self.update_stats()
            self.update_upgrade_buttons()
            self.update_achievements_display()

if __name__ == "__main__":
    root = tk.Tk()
    game = AdvancedClickerGame(root)
    root.mainloop()
