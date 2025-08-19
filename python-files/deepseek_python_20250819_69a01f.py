import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
import threading

class HotspotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hotspot Controller")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title = ttk.Label(main_frame, text="Hotspot Controller", 
                         font=("Segoe UI", 16, "bold"))
        title.grid(row=0, column=0, pady=(0, 20))
        
        # SSID Entry
        ttk.Label(main_frame, text="Network Name:").grid(row=1, column=0, sticky=tk.W)
        self.ssid_entry = ttk.Entry(main_frame, font=("Segoe UI", 10))
        self.ssid_entry.grid(row=2, column=0, pady=(0, 10), sticky=(tk.W, tk.E))
        self.ssid_entry.insert(0, "MyHotspot")
        
        # Password Entry
        ttk.Label(main_frame, text="Password:").grid(row=3, column=0, sticky=tk.W)
        self.password_entry = ttk.Entry(main_frame, show="•", font=("Segoe UI", 10))
        self.password_entry.grid(row=4, column=0, pady=(0, 20), sticky=(tk.W, tk.E))
        self.password_entry.insert(0, "Password123")
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=5, column=0, pady=10)
        
        self.start_btn = ttk.Button(btn_frame, text="Start Hotspot", 
                                   command=self.start_hotspot)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(btn_frame, text="Stop Hotspot", 
                                  command=self.stop_hotspot, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Status
        self.status_label = ttk.Label(main_frame, text="Status: Inactive", 
                                     foreground="red", font=("Segoe UI", 10))
        self.status_label.grid(row=6, column=0, pady=(20, 0))
        
    def run_cmd(self, commands):
        try:
            result = subprocess.run(commands, capture_output=True, text=True, shell=True)
            return result.returncode == 0
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return False
            
    def start_hotspot(self):
        ssid = self.ssid_entry.get()
        password = self.password_entry.get()
        
        if len(password) < 8:
            messagebox.showerror("Error", "Password must be at least 8 characters")
            return
            
        def thread_target():
            self.start_btn.config(state=tk.DISABLED)
            if self.run_cmd(f'netsh wlan set hostednetwork mode=allow ssid="{ssid}" key="{password}"'):
                if self.run_cmd('netsh wlan start hostednetwork'):
                    self.status_label.config(text="Status: Active", foreground="green")
                    self.stop_btn.config(state=tk.NORMAL)
                    messagebox.showinfo("Success", "Hotspot started successfully!")
                else:
                    messagebox.showerror("Error", "Failed to start hotspot")
            self.start_btn.config(state=tk.NORMAL)
            
        threading.Thread(target=thread_target, daemon=True).start()
        
    def stop_hotspot(self):
        def thread_target():
            self.stop_btn.config(state=tk.DISABLED)
            if self.run_cmd('netsh wlan stop hostednetwork'):
                self.status_label.config(text="Status: Inactive", foreground="red")
                messagebox.showinfo("Success", "Hotspot stopped successfully!")
            else:
                messagebox.showerror("Error", "Failed to stop hotspot")
            self.stop_btn.config(state=tk.NORMAL)
            
        threading.Thread(target=thread_target, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = HotspotApp(root)
    root.mainloop()