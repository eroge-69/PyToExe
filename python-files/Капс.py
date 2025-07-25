import tkinter as tk
from tkinter import ttk, messagebox
import keyboard
import ctypes
import sys
import os
from typing import Optional

class CapsLockManager:
    """
    Professional Caps Lock Management Tool
    Version: 2.3
    Author: absurD
    """
    
    def __init__(self, master: tk.Tk):
        self.master = master
        self.caps_pressed = False
        self.vk_capital = 0x14
        self.user32 = ctypes.WinDLL("User32.dll")
        
        self.setup_appearance()
        self.create_widgets()
        self.setup_hotkeys()
        self.verify_admin()
        
        # Ensure clean exit
        self.master.protocol("WM_DELETE_WINDOW", self.safe_exit)

    def setup_appearance(self):
        """Configure application visual style"""
        self.master.title("Caps Lock Manager")
        self.master.geometry("450x300")
        self.master.resizable(False, False)
        self.master.iconbitmap(self.resource_path("icon.ico")) if os.path.exists("icon.ico") else None
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#f5f5f5')
        style.configure('TLabel', background='#f5f5f5', font=('Segoe UI', 9))
        style.configure('TButton', font=('Segoe UI', 9))
        style.configure('Header.TLabel', font=('Segoe UI', 12, 'bold'))
        style.configure('Status.TFrame', background='#e9e9e9')

    def create_widgets(self):
        """Build the application interface"""
        # Header
        header_frame = ttk.Frame(self.master)
        header_frame.pack(pady=(10, 5), padx=10, fill=tk.X)
        
        ttk.Label(
            header_frame,
            text="CAPS LOCK MANAGER",
            style='Header.TLabel'
        ).pack(side=tk.LEFT)
        
        ttk.Label(
            header_frame,
            text="v2.3 by absurD",
            style='TLabel'
        ).pack(side=tk.RIGHT)
        
        # Status panel
        status_frame = ttk.Frame(self.master, style='Status.TFrame')
        status_frame.pack(pady=10, padx=10, fill=tk.X)
        
        self.status_text = tk.StringVar(value="Status: Ready")
        ttk.Label(
            status_frame,
            textvariable=self.status_text,
            style='TLabel'
        ).pack(pady=5)
        
        # Control buttons
        btn_frame = ttk.Frame(self.master)
        btn_frame.pack(pady=15)
        
        self.press_btn = ttk.Button(
            btn_frame,
            text="Hold Caps Lock (Ctrl+F1)",
            command=self.hold_caps,
            width=20
        )
        self.press_btn.pack(side=tk.LEFT, padx=5)
        
        self.release_btn = ttk.Button(
            btn_frame,
            text="Release Caps Lock (Ctrl+F2)",
            command=self.release_caps,
            width=20,
            state=tk.DISABLED
        )
        self.release_btn.pack(side=tk.LEFT, padx=5)
        
        # Activity log
        log_frame = ttk.Frame(self.master)
        log_frame.pack(pady=(5, 10), padx=10, fill=tk.BOTH, expand=True)
        
        ttk.Label(log_frame, text="Activity Log:").pack(anchor=tk.W)
        
        self.log = tk.Text(
            log_frame,
            height=6,
            font=('Consolas', 8),
            state=tk.DISABLED,
            wrap=tk.WORD,
            padx=5,
            pady=5
        )
        scrollbar = ttk.Scrollbar(log_frame, command=self.log.yview)
        self.log.configure(yscrollcommand=scrollbar.set)
        
        self.log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def setup_hotkeys(self):
        """Register global hotkeys"""
        try:
            keyboard.add_hotkey('ctrl+f1', self.hold_caps)
            keyboard.add_hotkey('ctrl+f2', self.release_caps)
            self.log_message("Hotkeys registered: Ctrl+F1, Ctrl+F2")
        except Exception as e:
            self.log_message(f"Hotkey registration failed: {str(e)}", True)

    def verify_admin(self):
        """Check for administrator privileges"""
        try:
            if not ctypes.windll.shell32.IsUserAnAdmin():
                self.log_message("Warning: Admin privileges recommended", True)
        except:
            pass

    def hold_caps(self):
        """Simulate continuous Caps Lock press"""
        if not self.caps_pressed:
            try:
                self.user32.keybd_event(self.vk_capital, 0, 0x0001, 0)
                self.caps_pressed = True
                self.status_text.set("Status: Caps Lock HELD")
                self.press_btn.config(state=tk.DISABLED)
                self.release_btn.config(state=tk.NORMAL)
                self.log_message("Caps Lock held (simulated press)")
            except Exception as e:
                self.log_message(f"Error holding Caps Lock: {str(e)}", True)

    def release_caps(self):
        """Release simulated Caps Lock press"""
        if self.caps_pressed:
            try:
                self.user32.keybd_event(self.vk_capital, 0, 0x0002, 0)
                self.caps_pressed = False
                self.status_text.set("Status: Ready")
                self.press_btn.config(state=tk.NORMAL)
                self.release_btn.config(state=tk.DISABLED)
                self.log_message("Caps Lock released")
            except Exception as e:
                self.log_message(f"Error releasing Caps Lock: {str(e)}", True)

    def log_message(self, message: str, is_error: bool = False):
        """Add message to activity log"""
        self.log.config(state=tk.NORMAL)
        self.log.insert(tk.END, f"[{self.current_time()}] {message}\n", 
                       'error' if is_error else 'info')
        self.log.see(tk.END)
        self.log.config(state=tk.DISABLED)
        
    def current_time(self) -> str:
        """Get current time for logging"""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")

    def resource_path(self, relative_path: str) -> str:
        """Get absolute path to resource"""
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def safe_exit(self):
        """Clean up resources before exit"""
        if self.caps_pressed:
            self.release_caps()
        try:
            keyboard.unhook_all()
        except:
            pass
        self.master.destroy()
        sys.exit(0)

def main():
    root = tk.Tk()
    
    # Center window
    window_width = 450
    window_height = 300
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    # Configure text tags
    root.option_add('*Text*background', 'white')
    
    app = CapsLockManager(root)
    
    # Configure text colors
    app.log.tag_config('info', foreground='black')
    app.log.tag_config('error', foreground='red')
    
    root.mainloop()

if __name__ == "__main__":
    main()
