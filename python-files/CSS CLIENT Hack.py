import tkinter as tk
from tkinter import ttk, messagebox
import random
import time
import threading
import sys

class CSClientMOD:
    def __init__(self, root):
        self.root = root
        self.root.title("Client MOD Hack CS:Source")
        self.root.geometry("900x700")
        self.root.resizable(False, False)
        self.root.configure(bg='#1a1a1a')
        
        # Biến lưu trạng thái các tính năng
        self.features = {
            "AimBot": tk.BooleanVar(),
            "WallHack": tk.BooleanVar(),
            "Bhop Script": tk.BooleanVar(),
            "No Recoil": tk.BooleanVar(),
            "Speed Hack": tk.BooleanVar(),
            "ESP": tk.BooleanVar(),
            "Radar Hack": tk.BooleanVar(),
            "Trigger Bot": tk.BooleanVar()
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        # Header
        header_frame = tk.Frame(self.root, bg='#2d2d2d', height=100)
        header_frame.pack(fill='x', padx=10, pady=10)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="Client MOD Hack CS:Source BY TungMinh",
            font=('Arial', 20, 'bold'),
            fg='#00ff00',
            bg='#2d2d2d'
        )
        title_label.pack(expand=True)
        
        # Hiệu ứng chữ nhấp nháy
        self.blink_title(title_label)
        
        # Main content frame
        main_frame = tk.Frame(self.root, bg='#1a1a1a')
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Features frame
        features_frame = tk.LabelFrame(
            main_frame,
            text="MOD Features",
            font=('Arial', 14, 'bold'),
            fg='#ffffff',
            bg='#2d2d2d',
            bd=2,
            relief='ridge'
        )
        features_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        # Tạo các checkbox cho tính năng
        self.create_feature_checkboxes(features_frame)
        
        # Console output frame
        console_frame = tk.LabelFrame(
            main_frame,
            text="Console Output",
            font=('Arial', 12, 'bold'),
            fg='#ffffff',
            bg='#2d2d2d',
            bd=2,
            relief='ridge'
        )
        console_frame.pack(fill='both', expand=True)
        
        # Text widget cho console output
        self.console_text = tk.Text(
            console_frame,
            height=10,
            bg='#000000',
            fg='#00ff00',
            font=('Consolas', 10),
            insertbackground='#00ff00'
        )
        
        scrollbar = tk.Scrollbar(console_frame, command=self.console_text.yview)
        self.console_text.configure(yscrollcommand=scrollbar.set)
        
        self.console_text.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        scrollbar.pack(side='right', fill='y')
        
        # Apply button
        apply_button = tk.Button(
            main_frame,
            text="APPLY MODS",
            command=self.apply_mods,
            font=('Arial', 16, 'bold'),
            bg='#ff4444',
            fg='white',
            activebackground='#ff6666',
            activeforeground='white',
            relief='raised',
            bd=4,
            width=20,
            height=2
        )
        apply_button.pack(pady=20)
        
        # Hiệu ứng hover cho nút Apply
        apply_button.bind("<Enter>", lambda e: apply_button.config(bg='#ff6666'))
        apply_button.bind("<Leave>", lambda e: apply_button.config(bg='#ff4444'))
        
    def create_feature_checkboxes(self, parent):
        # Tạo 2 cột cho các tính năng
        left_frame = tk.Frame(parent, bg='#2d2d2d')
        left_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        
        right_frame = tk.Frame(parent, bg='#2d2d2d')
        right_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        features_list = list(self.features.keys())
        mid_point = len(features_list) // 2
        
        for i, feature in enumerate(features_list):
            if i < mid_point:
                frame = left_frame
            else:
                frame = right_frame
                
            cb = tk.Checkbutton(
                frame,
                text=feature,
                variable=self.features[feature],
                font=('Arial', 12, 'bold'),
                fg='#ffffff',
                bg='#2d2d2d',
                activebackground='#2d2d2d',
                activeforeground='#00ff00',
                selectcolor='#1a1a1a',
                padx=10,
                pady=8
            )
            cb.pack(anchor='w', pady=5)
            
            # Hiệu ứng khi check
            def on_check(feature_name=feature):
                if self.features[feature_name].get():
                    self.console_print(f"✓ {feature_name} activated")
                else:
                    self.console_print(f"✗ {feature_name} deactivated")
            
            cb.config(command=on_check)
    
    def blink_title(self, label):
        def blink():
            colors = ['#00ff00', '#00cc00', '#009900', '#00ff00']
            for color in colors:
                label.config(fg=color)
                self.root.update()
                time.sleep(0.3)
            self.root.after(1000, blink)
        blink()
    
    def console_print(self, message):
        self.console_text.insert('end', f"{message}\n")
        self.console_text.see('end')
        self.root.update()
    
    def generate_fake_code(self):
        """Tạo các dòng code giả cho hiệu ứng"""
        prefixes = [
            "[DEBUG]", "[INFO]", "[MOD]", "[MEMORY]", 
            "[INJECT]", "[HOOK]", "[PATCH]", "[BYTE]"
        ]
        
        actions = [
            "Injecting DLL into process...",
            "Patching memory addresses...",
            "Hooking game functions...",
            "Reading game memory...",
            "Writing cheat bytes...",
            "Setting up ESP overlay...",
            "Configuring aimbot algorithm...",
            "Initializing wallhack render...",
            "Setting up bunnyhop trigger...",
            "Modifying player coordinates...",
            "Bypassing anti-cheat...",
            "Encrypting cheat signatures...",
            "Loading configuration...",
            "Starting cheat thread...",
            "Hooking DirectX functions..."
        ]
        
        statuses = ["SUCCESS", "FAILED", "COMPLETED", "RUNNING", "INITIALIZED"]
        
        code_lines = []
        for _ in range(25):  # Tạo 25 dòng code
            prefix = random.choice(prefixes)
            action = random.choice(actions)
            status = random.choice(statuses)
            
            # Thêm số hex ngẫu nhiên
            hex_addr = f"0x{random.randint(0x1000, 0xFFFF):04X}"
            
            line = f"{prefix} {action} [{status}] at {hex_addr}"
            code_lines.append(line)
        
        return code_lines
    
    def apply_mods(self):
        """Xử lý khi nhấn nút Apply"""
        # Kiểm tra xem có tính năng nào được chọn không
        selected_features = [name for name, var in self.features.items() if var.get()]
        
        if not selected_features:
            messagebox.showwarning("Warning", "Please select at least one feature!")
            return
        
        # Hiển thị thông báo bắt đầu
        self.console_print("=" * 60)
        self.console_print("STARTING CLIENT MOD INJECTION...")
        self.console_print("=" * 60)
        self.console_print(f"Selected features: {', '.join(selected_features)}")
        self.console_print("Initializing hack sequence...")
        
        # Chạy hiệu ứng trong thread riêng để không block GUI
        threading.Thread(target=self.run_script_animation, daemon=True).start()
    
    def run_script_animation(self):
        """Chạy hiệu ứng script trong 5 giây"""
        start_time = time.time()
        code_lines = self.generate_fake_code()
        
        while time.time() - start_time < 5:
            # Hiển thị dòng code ngẫu nhiên
            line = random.choice(code_lines)
            
            # Thêm hiệu ứng màu sắc ngẫu nhiên
            colors = ['#00ff00', '#00cc00', '#009900', '#66ff66']
            color = random.choice(colors)
            
            self.console_text.insert('end', f"{line}\n", color)
            self.console_text.see('end')
            self.root.update()
            
            # Tốc độ hiển thị ngẫu nhiên
            time.sleep(random.uniform(0.05, 0.2))
        
        # Hiển thị thông báo hoàn thành
        self.console_print("=" * 60)
        self.console_print("✓ CLIENT MOD INJECTION COMPLETED SUCCESSFULLY!")
        self.console_print("✓ All selected features have been activated")
        self.console_print("✓ Launch CS:Source to enjoy your advantages!")
        self.console_print("=" * 60)
        
        # Hiệu ứng hoàn thành
        messagebox.showinfo("Success", "Client MOD has been applied successfully!\nLaunch CS:Source to use the features.")

def main():
    # Tạo cửa sổ chính
    root = tk.Tk()
    
    # Đặt icon (có thể thay thế bằng file icon riêng)
    try:
        root.iconbitmap(default='icon.ico')  # Nếu có file icon
    except:
        pass
    
    app = CSClientMOD(root)
    
    # Chạy ứng dụng
    root.mainloop()

if __name__ == "__main__":
    main()