import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import random
import sys
import os

class CSModClient:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CS:Source MOD Client")
        self.root.geometry("900x700")
        self.root.resizable(False, False)
        
        # Center window on screen
        self.center_window()
        
        self.setup_ui()
        
    def center_window(self):
        self.root.update_idletasks()
        width = 900
        height = 700
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_ui(self):
        # Main frame
        main_frame = tk.Frame(self.root, bg='#2c2c2c')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="Client MOD Hack CS:Source BY TungMinh",
            font=('Arial', 20, 'bold'),
            fg='#00ff00',
            bg='#2c2c2c'
        )
        title_label.pack(pady=20)
        
        # Separator
        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.pack(fill=tk.X, padx=20, pady=10)
        
        # Features frame
        features_frame = tk.Frame(main_frame, bg='#2c2c2c')
        features_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Features label
        features_label = tk.Label(
            features_frame,
            text="Available Features:",
            font=('Arial', 14, 'bold'),
            fg='#ffffff',
            bg='#2c2c2c',
            anchor='w'
        )
        features_label.pack(anchor='w', pady=(0, 10))
        
        # Features list
        features = [
            "AimBot - Tự động ngắm bắn",
            "WallHack - Nhìn xuyên tường",
            "Bhop Script - Nhảy tự động",
            "No Recoil - Không giật súng",
            "Speed Hack - Tăng tốc độ di chuyển",
            "ESP - Hiển thị thông tin người chơi",
            "Radar Hack - Radar toàn màn hình",
            "Trigger Bot - Tự động bắn",
            "Anti-Flash - Chống mù flashbang",
            "Skin Changer - Đổi skin vũ khí"
        ]
        
        self.feature_vars = {}
        
        for feature in features:
            var = tk.BooleanVar()
            self.feature_vars[feature] = var
            
            checkbox = tk.Checkbutton(
                features_frame,
                text=feature,
                font=('Arial', 11),
                fg='#ffffff',
                bg='#2c2c2c',
                selectcolor='#1a1a1a',
                activebackground='#2c2c2c',
                activeforeground='#ffffff',
                variable=var
            )
            checkbox.pack(anchor='w', pady=2)
        
        # Console output frame
        console_frame = tk.Frame(main_frame, bg='#000000')
        console_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        console_label = tk.Label(
            console_frame,
            text="Console Output:",
            font=('Arial', 12, 'bold'),
            fg='#ffffff',
            bg='#2c2c2c',
            anchor='w'
        )
        console_label.pack(anchor='w', pady=(0, 5))
        
        self.console_text = tk.Text(
            console_frame,
            bg='#000000',
            fg='#00ff00',
            font=('Consolas', 10),
            width=80,
            height=12,
            state=tk.DISABLED
        )
        
        scrollbar = tk.Scrollbar(console_frame, orient=tk.VERTICAL, command=self.console_text.yview)
        self.console_text.configure(yscrollcommand=scrollbar.set)
        
        self.console_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Apply button
        apply_button = tk.Button(
            main_frame,
            text="APPLY MODS",
            font=('Arial', 14, 'bold'),
            bg='#ff4444',
            fg='#ffffff',
            activebackground='#cc0000',
            activeforeground='#ffffff',
            command=self.apply_mods,
            width=20,
            height=2
        )
        apply_button.pack(pady=20)
    
    def log_message(self, message):
        self.console_text.config(state=tk.NORMAL)
        self.console_text.insert(tk.END, message + "\n")
        self.console_text.see(tk.END)
        self.console_text.config(state=tk.DISABLED)
        self.root.update()
    
    def generate_random_code(self):
        chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyz!@#$%^&*()"
        return ''.join(random.choice(chars) for _ in range(random.randint(20, 50)))
    
    def apply_mods(self):
        # Get selected features
        selected_features = [feature for feature, var in self.feature_vars.items() if var.get()]
        
        if not selected_features:
            messagebox.showwarning("Warning", "Please select at least one feature!")
            return
        
        # Show running message
        self.log_message("Running Script Client...")
        self.log_message("=" * 50)
        
        # Disable apply button during execution
        self.root.update()
        
        # Run in separate thread to prevent GUI freezing
        thread = threading.Thread(target=self.run_script, args=(selected_features,))
        thread.daemon = True
        thread.start()
    
    def run_script(self, features):
        # Simulate script execution with random codes
        start_time = time.time()
        
        # Initialization messages
        init_messages = [
            "Initializing CS:Source memory hooks...",
            "Bypassing VAC detection...",
            "Loading external libraries...",
            "Setting up overlay renderer...",
            "Injecting DLL modules...",
            "Hooking DirectX functions...",
            "Reading game memory...",
            "Setting up cheat signatures..."
        ]
        
        for msg in init_messages:
            self.log_message(f"[INFO] {msg}")
            time.sleep(0.3)
        
        self.log_message("=" * 50)
        
        # Apply selected features
        for feature in features:
            self.log_message(f"[APPLYING] {feature}")
            
            # Generate random code lines for each feature
            for _ in range(random.randint(3, 8)):
                code_line = self.generate_random_code()
                self.log_message(f"  -> {code_line}")
                time.sleep(0.1)
            
            self.log_message(f"[SUCCESS] {feature} - Activated")
            time.sleep(0.2)
        
        # Final messages
        final_messages = [
            "All features applied successfully!",
            "VAC bypass completed!",
            "Memory protection enabled!",
            "Starting CS:Source with mods...",
            "Client MOD ready for use!"
        ]
        
        self.log_message("=" * 50)
        
        for msg in final_messages:
            self.log_message(f"[SYSTEM] {msg}")
            time.sleep(0.4)
        
        elapsed_time = time.time() - start_time
        self.log_message(f"\n[COMPLETED] Script finished in {elapsed_time:.2f} seconds")
        
        # Show completion message
        self.root.after(0, lambda: messagebox.showinfo("Completed", "All mods have been applied successfully!\n\nNow start CS:Source and enjoy!"))
    
    def run(self):
        self.root.mainloop()

def main():
    # Check if running on Windows
    if os.name != 'nt':
        messagebox.showerror("Error", "This application is designed for Windows only!")
        return
    
    app = CSModClient()
    app.run()

if __name__ == "__main__":
    main()