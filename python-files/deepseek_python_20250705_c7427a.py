import os
import psutil
import subprocess
import ctypes
import sys
import time
import webbrowser
from tkinter import Tk, Label, Button, Frame, messagebox, Checkbutton, IntVar, Canvas, PhotoImage
from PIL import Image, ImageTk

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

class GameBoosterApp:
    def __init__(self, root):
        self.root = root
        root.title("Game Booster")
        root.geometry("800x600")
        root.state('zoomed')  # Start in maximized window
        
        # Variables for checkboxes
        self.close_bg_apps = IntVar(value=1)
        self.set_high_performance = IntVar(value=1)
        self.clean_ram = IntVar(value=1)
        self.disable_notifications = IntVar(value=1)
        self.prioritize_game = IntVar(value=1)
        self.fullscreen_mode = IntVar(value=0)
        
        # Load background image
        self.setup_background()
        
        # Create main container
        self.main_frame = Frame(root, bg='')
        self.main_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # UI Elements
        Label(self.main_frame, text="Game Booster", font=("Arial", 24, "bold"), bg='black', fg='white').pack(pady=20)
        
        # Options frame with semi-transparent background
        options_frame = Frame(self.main_frame, bg='#222222', bd=2, relief='ridge')
        options_frame.pack(pady=10, padx=20, fill="x")
        
        Checkbutton(options_frame, text="Close Background Applications", variable=self.close_bg_apps, 
                   bg='#222222', fg='white', selectcolor='black', activebackground='#222222', 
                   activeforeground='white').pack(anchor="w", pady=5, padx=10)
        Checkbutton(options_frame, text="Set High Performance Power Plan", variable=self.set_high_performance,
                   bg='#222222', fg='white', selectcolor='black', activebackground='#222222',
                   activeforeground='white').pack(anchor="w", pady=5, padx=10)
        Checkbutton(options_frame, text="Clean RAM", variable=self.clean_ram,
                   bg='#222222', fg='white', selectcolor='black', activebackground='#222222',
                   activeforeground='white').pack(anchor="w", pady=5, padx=10)
        Checkbutton(options_frame, text="Disable Notifications", variable=self.disable_notifications,
                   bg='#222222', fg='white', selectcolor='black', activebackground='#222222',
                   activeforeground='white').pack(anchor="w", pady=5, padx=10)
        Checkbutton(options_frame, text="Prioritize Game Process", variable=self.prioritize_game,
                   bg='#222222', fg='white', selectcolor='black', activebackground='#222222',
                   activeforeground='white').pack(anchor="w", pady=5, padx=10)
        Checkbutton(options_frame, text="Fullscreen Mode", variable=self.fullscreen_mode,
                   bg='#222222', fg='white', selectcolor='black', activebackground='#222222',
                   activeforeground='white', command=self.toggle_fullscreen).pack(anchor="w", pady=5, padx=10)
        
        # Buttons frame
        buttons_frame = Frame(self.main_frame, bg='')
        buttons_frame.pack(pady=20)
        
        Button(buttons_frame, text="Boost Performance", command=self.boost_performance, 
              height=2, width=20, bg='#4CAF50', fg='white').pack(side='left', padx=10)
        Button(buttons_frame, text="Restore Settings", command=self.restore_settings, 
              height=2, width=20, bg='#f44336', fg='white').pack(side='left', padx=10)
        Button(buttons_frame, text="Free Games", command=self.show_free_games, 
              height=2, width=20, bg='#2196F3', fg='white').pack(side='left', padx=10)
        
        self.status_label = Label(self.main_frame, text="Ready", fg="green", bg='black', font=('Arial', 12))
        self.status_label.pack(pady=10)
        
        # Store original settings for restoration
        self.original_power_plan = self.get_current_power_plan()
        
        # Free games data
        self.free_games = [
            {"name": "Epic Games Free", "url": "https://store.epicgames.com/en-US/free-games"},
            {"name": "Steam Free to Play", "url": "https://store.steampowered.com/genre/Free%20to%20Play/"},
            {"name": "GOG Free Games", "url": "https://www.gog.com/games?priceRange=0,0"},
            {"name": "Itch.io Free Games", "url": "https://itch.io/games/free"},
            {"name": "Ubisoft Free Games", "url": "https://free.ubisoft.com/"}
        ]
    
    def setup_background(self):
        # Try to load a local gaming background image
        bg_path = "gaming_bg.jpg"
        
        if os.path.exists(bg_path):
            try:
                self.bg_image = Image.open(bg_path)
                self.bg_photo = ImageTk.PhotoImage(self.bg_image.resize((self.root.winfo_screenwidth(), self.root.winfo_screenheight())))
                self.background_label = Label(self.root, image=self.bg_photo)
                self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
                return
            except Exception as e:
                print(f"Error loading background image: {e}")
        
        # If no local image, use a solid color as fallback
        self.canvas = Canvas(self.root, bg='#121212', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        
        # Add some simple gaming-themed elements if no image
        self.canvas.create_text(self.root.winfo_screenwidth()//2, 100, 
                              text="GAME BOOSTER", 
                              font=("Arial", 36, "bold"), 
                              fill="#4CAF50")
    
    def toggle_fullscreen(self):
        if self.fullscreen_mode.get():
            self.root.attributes('-fullscreen', True)
        else:
            self.root.attributes('-fullscreen', False)
    
    def show_free_games(self):
        free_games_window = Tk()
        free_games_window.title("Free Games")
        free_games_window.geometry("600x400")
        
        Label(free_games_window, text="Popular Free Game Platforms", font=("Arial", 16, "bold")).pack(pady=10)
        
        for game in self.free_games:
            btn = Button(free_games_window, text=game["name"], 
                        command=lambda url=game["url"]: webbrowser.open_new(url),
                        width=30, height=2)
            btn.pack(pady=5)
        
        Label(free_games_window, text="For AI-generated gaming wallpapers, visit:", 
             font=("Arial", 10)).pack(pady=10)
        Button(free_games_window, text="AI Gaming Wallpapers", 
              command=lambda: webbrowser.open_new("https://www.artstation.com/search?q=gaming+wallpaper"),
              width=25).pack()
        
        free_games_window.mainloop()
    
    # ... [Keep all the existing methods unchanged from your original code] ...

if __name__ == "__main__":
    run_as_admin()
    root = Tk()
    app = GameBoosterApp(root)
    root.mainloop()