import os
import psutil
import subprocess
import ctypes
import sys
import time
import webbrowser
from tkinter import Tk, Label, Button, Frame, messagebox, Checkbutton, IntVar, Canvas, Toplevel
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
        try:
            root.state('zoomed')  # Start in maximized window
        except:
            root.attributes('-zoomed', True)
        
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
                self.background_label.image = self.bg_photo  # Keep a reference
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
        free_games_window = Toplevel(self.root)  # Use Toplevel instead of Tk for child windows
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
    
    def get_current_power_plan(self):
        try:
            result = subprocess.run(["powercfg", "/getactivescheme"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            lines = result.stdout.split('\n')
            for line in lines:
                if "GUID" in line:
                    return line.split(':')[1].strip().split(' ')[0]
            return None
        except Exception as e:
            print(f"Error getting power plan: {e}")
            return None
    
    def set_power_plan(self, plan_guid):
        try:
            subprocess.run(["powercfg", "/setactive", plan_guid], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error setting power plan: {e}")
            return False
    
    def find_high_performance_plan(self):
        try:
            result = subprocess.run(["powercfg", "/list"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            lines = result.stdout.split('\n')
            for line in lines:
                if "High performance" in line:
                    parts = line.split()
                    for part in parts:
                        if len(part) == 36 and part.count('-') == 4:  # GUID format
                            return part
            return None
        except Exception as e:
            print(f"Error finding high performance plan: {e}")
            return None
    
    def close_background_apps(self):
        try:
            processes_to_close = [
                "chrome.exe", "msedge.exe", "firefox.exe", 
                "discord.exe", "spotify.exe", "steam.exe",
                "origin.exe", "epicgameslauncher.exe",
                "notepad.exe", "word.exe", "excel.exe",
                "outlook.exe", "teams.exe", "skype.exe"
            ]
            
            closed_count = 0
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'].lower() in processes_to_close:
                    try:
                        p = psutil.Process(proc.info['pid'])
                        p.terminate()
                        closed_count += 1
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        continue
            
            self.update_status(f"Closed {closed_count} background processes")
            time.sleep(1)
            return closed_count
        except Exception as e:
            print(f"Error closing background apps: {e}")
            self.update_status("Error closing background apps", "red")
            return 0
    
    def clean_ram(self):
        try:
            if os.name == 'nt':
                # More effective method for Windows
                ctypes.windll.kernel32.SetProcessWorkingSetSize(-1, ctypes.c_size_t(-1), ctypes.c_size_t(-1))
                self.update_status("RAM cleaned")
                return True
            return False
        except Exception as e:
            print(f"Error cleaning RAM: {e}")
            self.update_status("Error cleaning RAM", "red")
            return False
    
    def disable_notifications(self):
        try:
            subprocess.run(["powershell", "-command", "Set-ItemProperty -Path HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Notifications\\Settings -Name NOC_GLOBAL_SETTING_TOASTS_ENABLED -Value 0"], 
                          check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            subprocess.run(["powershell", "-command", "Set-ItemProperty -Path HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\FocusAssist -Name PriorityOnly -Value 1"], 
                          check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            self.update_status("Notifications disabled")
            return True
        except Exception as e:
            print(f"Error disabling notifications: {e}")
            self.update_status("Error disabling notifications", "red")
            return False
    
    def enable_notifications(self):
        try:
            subprocess.run(["powershell", "-command", "Set-ItemProperty -Path HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Notifications\\Settings -Name NOC_GLOBAL_SETTING_TOASTS_ENABLED -Value 1"], 
                          check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            subprocess.run(["powershell", "-command", "Set-ItemProperty -Path HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\FocusAssist -Name PriorityOnly -Value 0"], 
                          check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            return True
        except Exception as e:
            print(f"Error enabling notifications: {e}")
            return False
    
    def boost_performance(self):
        try:
            self.update_status("Optimizing system...", "blue")
            
            if self.close_bg_apps.get():
                self.close_background_apps()
            
            if self.set_high_performance.get():
                high_perf_plan = self.find_high_performance_plan()
                if high_perf_plan:
                    if self.set_power_plan(high_perf_plan):
                        self.update_status("Set to High Performance power plan")
                    else:
                        self.update_status("Failed to set power plan", "orange")
                else:
                    self.update_status("High Performance plan not found", "orange")
            
            if self.clean_ram.get():
                self.clean_ram()
            
            if self.disable_notifications.get():
                self.disable_notifications()
            
            if self.prioritize_game.get():
                self.update_status("Run this after starting your game", "orange")
            
            self.update_status("Optimization complete!", "green")
            messagebox.showinfo("Success", "System optimized for gaming!")
            
        except Exception as e:
            print(f"Error during optimization: {e}")
            self.update_status("Optimization failed", "red")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def restore_settings(self):
        try:
            self.update_status("Restoring settings...", "blue")
            
            if self.set_high_performance.get() and self.original_power_plan:
                if self.set_power_plan(self.original_power_plan):
                    self.update_status("Restored original power plan")
                else:
                    self.update_status("Failed to restore power plan", "orange")
            
            if self.disable_notifications.get():
                self.enable_notifications()
                self.update_status("Notifications restored")
            
            self.update_status("Settings restored", "green")
            messagebox.showinfo("Success", "Original settings restored!")
            
        except Exception as e:
            print(f"Error restoring settings: {e}")
            self.update_status("Restore failed", "red")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def update_status(self, message, color="green"):
        self.status_label.config(text=message, fg=color)
        self.root.update()

if __name__ == "__main__":
    run_as_admin()
    root = Tk()
    app = GameBoosterApp(root)
    root.mainloop()