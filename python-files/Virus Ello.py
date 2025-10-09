import tkinter as tk
from tkinter import ttk
import random
import time
import threading

class PrankSoftware:
    def __init__(self):
        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='black')
        self.setup_ui()
        
    def setup_ui(self):
        # Phase 1: Fake System Scan
        self.show_scan_screen()
        
    def show_scan_screen(self):
        # Clear screen
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Scan screen UI
        title = tk.Label(self.root, text="🔍 Windows Security Scan", 
                        fg='white', bg='black', font=("Arial", 24, "bold"))
        title.pack(pady=50)
        
        self.scan_label = tk.Label(self.root, text="Scanning system files...", 
                                  fg='yellow', bg='black', font=("Arial", 14))
        self.scan_label.pack(pady=20)
        
        # Progress bar
        self.progress = ttk.Progressbar(self.root, length=600, mode='determinate')
        self.progress.pack(pady=20)
        
        # Start scanning animation
        self.start_scan()
        
    def start_scan(self):
        scan_messages = [
            "Scanning C:\\Windows\\System32...",
            "Checking registry integrity...",
            "Analyzing network security...",
            "Verifying user accounts...",
            "Detecting potential threats...",
            "CRITICAL THREAT DETECTED!",
            "Multiple viruses found!",
            "SYSTEM COMPROMISED!"
        ]
        
        def update_scan():
            for i, msg in enumerate(scan_messages):
                self.scan_label.config(text=msg)
                self.progress['value'] = (i + 1) * (100 / len(scan_messages))
                self.root.update()
                time.sleep(1.5)
                
                if i == 4:  # After "Detecting potential threats"
                    time.sleep(2)
                    self.show_fake_errors()
                    
            time.sleep(2)
            self.show_glitch_effect()
            
        threading.Thread(target=update_scan, daemon=True).start()
    
    def show_fake_errors(self):
        error_messages = [
            ("Critical Error", "Memory access violation at 0x7FFE0304"),
            ("Virus Alert", "Trojan:Win32/Malware.A detected!"),
            ("System Warning", "Kernel security check failure"),
            ("BSOD Preview", "SYSTEM_THREAD_EXCEPTION_NOT_HANDLED")
        ]
        
        for title, msg in error_messages:
            error_win = tk.Toplevel(self.root)
            error_win.title(title)
            error_win.geometry("400x200")
            error_win.attributes('-topmost', True)
            
            # Random position
            x = random.randint(100, 800)
            y = random.randint(100, 600)
            error_win.geometry(f"+{x}+{y}")
            
            tk.Label(error_win, text=msg, fg='red', font=("Arial", 11)).pack(expand=True)
            error_win.after(2000, error_win.destroy)
    
    def show_glitch_effect(self):
        for widget in self.root.winfo_children():
            widget.destroy()
            
        colors = ['red', 'blue', 'green', 'purple', 'yellow']
        
        def glitch():
            for _ in range(15):
                color = random.choice(colors)
                self.root.configure(bg=color)
                self.root.update()
                time.sleep(0.1)
            
            # Show final message
            self.show_truth()
            
        threading.Thread(target=glitch, daemon=True).start()
    
    def show_truth(self):
        for widget in self.root.winfo_children():
            widget.destroy()
            
        self.root.configure(bg='black')
        
        # Main message
        main_text = tk.Label(self.root, 
                            text="😊 JUST A PRANK! 😊\n\n" +
                                 "Your computer is COMPLETELY SAFE!\n" +
                                 "No changes were made to your system.\n\n" +
                                 "This was a harmless demonstration.\n\n" +
                                 "Press ESC to exit or click Exit below",
                            fg='green', bg='black', 
                            font=("Arial", 18), justify='center')
        main_text.pack(expand=True)
        
        # Exit button
        exit_btn = tk.Button(self.root, text="EXIT", 
                           command=self.safe_exit,
                           bg='red', fg='white', 
                           font=("Arial", 16, "bold"),
                           padx=20, pady=10)
        exit_btn.pack(pady=30)
        
        # Bind ESC key
        self.root.bind('<Escape>', lambda e: self.safe_exit())
        
        # Make sure window is on top
        self.root.attributes('-topmost', True)
    
    def safe_exit(self):
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        # Safety disclaimer first
        disclaimer = tk.Toplevel(self.root)
        disclaimer.attributes('-topmost', True)
        disclaimer.title("⚠️ READ THIS FIRST!")
        disclaimer.geometry("500x300")
        
        tk.Label(disclaimer, 
                text="⚠️ PRANK SOFTWARE - READ CAREFULLY!\n\n" +
                     "This is a SIMULATION only for entertainment.\n" +
                     "Your computer is SAFE - no real changes will be made.\n\n" +
                     "Features:\n" +
                     "• Fake system scan\n" +
                     "• Fake error messages  \n" +
                     "• Visual effects\n" +
                     "• Easy exit (ESC key)\n\n" +
                     "Click OK to continue (10 seconds auto-start)",
                font=("Arial", 12), justify='left', wraplength=450).pack(expand=True)
        
        def start_countdown(seconds=10):
            if seconds > 0:
                disclaimer.title(f"Starting in {seconds}...")
                disclaimer.after(1000, lambda: start_countdown(seconds-1))
            else:
                disclaimer.destroy()
                self.root.deiconify()
        
        disclaimer.after(100, lambda: start_countdown())
        self.root.withdraw()
        
        self.root.mainloop()

# PENTING: BACA INI SEBELUM MENJALANKAN
"""
PERINGATAN ETIS:
1. HANYA gunakan dengan orang yang TAHU itu bercanda
2. JANGAN gunakan pada orang yang mudah panik/bermasalah jantung
3. SELALU beri tahu ini hanya prank setelahnya
4. Pastikan user tahu cara exit (ESC atau tombol)
5. Tidak untuk digunakan sembarangan!
"""

if __name__ == "__main__":
    app = PrankSoftware()
    app.run()