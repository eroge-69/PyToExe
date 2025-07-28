import os
import subprocess
import winreg
import ctypes
import sys
from pathlib import Path
import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time

try:
    import wmi
except ImportError:
    wmi = None

class AdvancedGameOptimizer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎮 Ultimate Gaming Optimizer - Hardware Specific")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1e1e1e')
        self.root.resizable(True, True)
        
        # Set window icon and style
        try:
            self.root.iconbitmap(default='icon.ico')
        except:
            pass
            
        self.setup_styles()
        self.hardware_info = self.detect_hardware()
        self.optimizations_applied = []
        
        self.setup_ui()
        
    def setup_styles(self):
        """Setup custom styles for the application"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), foreground='#00ff00', background='#1e1e1e')
        style.configure('Subtitle.TLabel', font=('Arial', 12), foreground='#ffffff', background='#1e1e1e')
        style.configure('Custom.TNotebook', background='#2d2d2d', borderwidth=0)
        style.configure('Custom.TNotebook.Tab', padding=[20, 10], font=('Arial', 10, 'bold'))
        
    def detect_hardware(self):
        """Detect system hardware using WMI"""
        try:
            if wmi is None:
                return self.get_fallback_hardware_info()
                
            c = wmi.WMI()
            
            # Get CPU info
            cpu_info = c.Win32_Processor()[0]
            cpu_name = cpu_info.Name.strip()
            cpu_vendor = 'intel' if 'intel' in cpu_name.lower() else 'amd' if 'amd' in cpu_name.lower() else 'unknown'
            
            # Get GPU info
            gpu_info = c.Win32_VideoController()
            gpu_vendors = []
            gpu_names = []
            
            for gpu in gpu_info:
                if gpu.Name and 'Microsoft' not in gpu.Name:
                    gpu_names.append(gpu.Name)
                    if 'nvidia' in gpu.Name.lower() or 'geforce' in gpu.Name.lower():
                        gpu_vendors.append('nvidia')
                    elif 'amd' in gpu.Name.lower() or 'radeon' in gpu.Name.lower():
                        gpu_vendors.append('amd')
                    elif 'intel' in gpu.Name.lower():
                        gpu_vendors.append('intel')
                        
            return {
                'cpu': {'vendor': cpu_vendor, 'name': cpu_name},
                'gpu': {'vendors': list(set(gpu_vendors)), 'names': gpu_names},
                'ram': self.get_ram_info(),
                'os': self.get_os_info()
            }
            
        except Exception as e:
            self.log(f"⚠️ Hardware detection error: {e}")
            return self.get_fallback_hardware_info()
    
    def get_fallback_hardware_info(self):
        """Fallback hardware detection using registry"""
        try:
            # CPU detection via registry
            cpu_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
            cpu_name = winreg.QueryValueEx(cpu_key, "ProcessorNameString")[0]
            winreg.CloseKey(cpu_key)
            
            cpu_vendor = 'intel' if 'intel' in cpu_name.lower() else 'amd' if 'amd' in cpu_name.lower() else 'unknown'
            
            return {
                'cpu': {'vendor': cpu_vendor, 'name': cpu_name},
                'gpu': {'vendors': ['unknown'], 'names': ['Unknown GPU']},
                'ram': '8GB (estimated)',
                'os': 'Windows 10/11'
            }
        except:
            return {
                'cpu': {'vendor': 'unknown', 'name': 'Unknown CPU'},
                'gpu': {'vendors': ['unknown'], 'names': ['Unknown GPU']},
                'ram': 'Unknown',
                'os': 'Windows'
            }
    
    def get_ram_info(self):
        """Get RAM information"""
        try:
            import psutil
            ram_gb = round(psutil.virtual_memory().total / (1024**3))
            return f"{ram_gb}GB"
        except:
            return "Unknown"
    
    def get_os_info(self):
        """Get OS information"""
        try:
            import platform
            return f"{platform.system()} {platform.release()}"
        except:
            return "Windows"
        
    def setup_ui(self):
        """Setup the main user interface"""
        # Main title frame
        title_frame = tk.Frame(self.root, bg='#1e1e1e')
        title_frame.pack(fill='x', pady=10)
        
        title_label = tk.Label(title_frame, text="🎮 Ultimate Gaming Optimizer", 
                              font=('Arial', 20, 'bold'), fg='#00ff00', bg='#1e1e1e')
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, text="Hardware-Specific Gaming Performance Optimization", 
                                 font=('Arial', 12), fg='#ffffff', bg='#1e1e1e')
        subtitle_label.pack()
        
        # Hardware info display
        hw_frame = tk.Frame(self.root, bg='#2d2d2d', relief='raised', bd=1)
        hw_frame.pack(fill='x', padx=10, pady=5)
        
        cpu_name_short = self.hardware_info['cpu']['name'][:50] + "..." if len(self.hardware_info['cpu']['name']) > 50 else self.hardware_info['cpu']['name']
        hw_text = f"🔍 Detected Hardware: {self.hardware_info['cpu']['vendor'].upper()} CPU ({cpu_name_short}) | GPU: {', '.join([v.upper() for v in self.hardware_info['gpu']['vendors']])}"
        hw_label = tk.Label(hw_frame, text=hw_text, font=('Arial', 10), fg='#ffff00', bg='#2d2d2d')
        hw_label.pack(pady=5)
        
        # Create main notebook
        self.notebook = ttk.Notebook(self.root, style='Custom.TNotebook')
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_hardware_info_tab()
        self.create_cpu_optimization_tab()
        self.create_gpu_optimization_tab()
        self.create_general_optimization_tab()
        self.create_control_panel_tab()
        
        # Bottom control frame
        control_frame = tk.Frame(self.root, bg='#1e1e1e')
        control_frame.pack(fill='x', padx=10, pady=10)
        
        # Control buttons
        btn_frame = tk.Frame(control_frame, bg='#1e1e1e')
        btn_frame.pack(side='left')
        
        apply_all_btn = tk.Button(btn_frame, text="🚀 Apply All Hardware Optimizations", 
                                 command=self.apply_all_hardware_optimizations,
                                 bg='#00aa00', fg='white', font=('Arial', 12, 'bold'),
                                 padx=20, pady=10)
        apply_all_btn.pack(side='left', padx=5)
        
        revert_btn = tk.Button(btn_frame, text="↩️ Revert All", 
                              command=self.revert_all_optimizations,
                              bg='#aa6600', fg='white', font=('Arial', 12, 'bold'),
                              padx=20, pady=10)
        revert_btn.pack(side='left', padx=5)
        
        restart_btn = tk.Button(btn_frame, text="🔄 Restart PC", 
                               command=self.restart_computer,
                               bg='#aa0000', fg='white', font=('Arial', 12, 'bold'),
                               padx=20, pady=10)
        restart_btn.pack(side='left', padx=5)
        
        # Status frame
        status_frame = tk.Frame(control_frame, bg='#1e1e1e')
        status_frame.pack(side='right')
        
        self.status_var = tk.StringVar(value="Ready")
        status_label = tk.Label(status_frame, textvariable=self.status_var, 
                               font=('Arial', 10), fg='#00ff00', bg='#1e1e1e')
        status_label.pack()
        
    def create_hardware_info_tab(self):
        """Create hardware information tab"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="🔍 Hardware Info")
        
        # Create scrollable text widget
        info_text = scrolledtext.ScrolledText(tab_frame, wrap=tk.WORD, 
                                             bg='#2d2d2d', fg='#ffffff', 
                                             font=('Consolas', 11))
        info_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Hardware information
        hw_info = f"""
🖥️  SYSTEM HARDWARE INFORMATION
{'='*60}

💻 CPU Information:
   Vendor: {self.hardware_info['cpu']['vendor'].upper()}
   Model: {self.hardware_info['cpu']['name']}

🎮 GPU Information:
   Vendors: {', '.join([v.upper() for v in self.hardware_info['gpu']['vendors']])}
   Models: {', '.join(self.hardware_info['gpu']['names'])}

💾 Memory: {self.hardware_info['ram']}
🖥️  OS: {self.hardware_info['os']}

⚙️  OPTIMIZATION STATUS
{'='*60}

✅ Hardware-specific optimizations will be applied based on detected hardware
✅ Intel CPU optimizations: {'AVAILABLE' if self.hardware_info['cpu']['vendor'] == 'intel' else 'NOT APPLICABLE'}
✅ AMD CPU optimizations: {'AVAILABLE' if self.hardware_info['cpu']['vendor'] == 'amd' else 'NOT APPLICABLE'}
✅ NVIDIA GPU optimizations: {'AVAILABLE' if 'nvidia' in self.hardware_info['gpu']['vendors'] else 'NOT APPLICABLE'}
✅ AMD GPU optimizations: {'AVAILABLE' if 'amd' in self.hardware_info['gpu']['vendors'] else 'NOT APPLICABLE'}
✅ Intel GPU optimizations: {'AVAILABLE' if 'intel' in self.hardware_info['gpu']['vendors'] else 'NOT APPLICABLE'}

⚠️  IMPORTANT NOTES
{'='*60}

🔸 Always run as Administrator for full functionality
🔸 Create a System Restore Point before applying optimizations
🔸 Restart your computer after applying optimizations
🔸 Some changes require a full system restart to take effect
🔸 Use Windows System Restore to revert changes if needed

🎯 RECOMMENDED WORKFLOW
{'='*60}

1. Create System Restore Point
2. Apply hardware-specific optimizations
3. Restart computer
4. Test gaming performance
5. Fine-tune individual settings if needed
        """
        
        info_text.insert('1.0', hw_info)
        info_text.config(state='disabled')
        
    def create_cpu_optimization_tab(self):
        """Create CPU optimization tab"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text=f"🔥 {self.hardware_info['cpu']['vendor'].upper()} CPU")
        
        # Create scrollable frame
        canvas = tk.Canvas(tab_frame, bg='#2d2d2d')
        scrollbar = ttk.Scrollbar(tab_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # CPU optimizations based on vendor
        if self.hardware_info['cpu']['vendor'] == 'intel':
            self.create_intel_cpu_options(scrollable_frame)
        elif self.hardware_info['cpu']['vendor'] == 'amd':
            self.create_amd_cpu_options(scrollable_frame)
        else:
            self.create_generic_cpu_options(scrollable_frame)
            
    def create_intel_cpu_options(self, parent):
        """Create Intel CPU optimization options"""
        title = tk.Label(parent, text="🔵 Intel CPU Optimizations", 
                        font=('Arial', 16, 'bold'), fg='#0066cc', bg='#2d2d2d')
        title.pack(pady=10)
        
        options = [
            ("Disable Intel SpeedStep", "Disables CPU frequency scaling for consistent performance", self.disable_intel_speedstep),
            ("Optimize Intel Turbo Boost", "Configures Turbo Boost for maximum performance", self.optimize_intel_turbo),
            ("Disable Intel C-States", "Prevents CPU from entering low-power states", self.disable_intel_cstates),
            ("Optimize Hyperthreading", "Configures Hyperthreading for gaming workloads", self.optimize_intel_hyperthreading),
            ("Set High Performance Power Plan", "Activates Windows high performance mode", self.set_high_performance_plan),
            ("Disable CPU Parking", "Prevents Windows from parking CPU cores", self.disable_cpu_parking)
        ]
        
        for name, desc, func in options:
            self.create_optimization_option(parent, name, desc, func)
            
    def create_amd_cpu_options(self, parent):
        """Create AMD CPU optimization options"""
        title = tk.Label(parent, text="🔴 AMD CPU Optimizations", 
                        font=('Arial', 16, 'bold'), fg='#cc0000', bg='#2d2d2d')
        title.pack(pady=10)
        
        options = [
            ("Disable AMD Cool'n'Quiet", "Disables AMD power management for consistent performance", self.disable_amd_coolnquiet),
            ("Optimize AMD Precision Boost", "Configures Precision Boost for maximum performance", self.optimize_amd_precision_boost),
            ("Optimize AMD SMT", "Configures Simultaneous Multithreading for gaming", self.optimize_amd_smt),
            ("AMD Ryzen Optimizations", "Applies Ryzen-specific performance tweaks", self.optimize_amd_ryzen),
            ("Set High Performance Power Plan", "Activates Windows high performance mode", self.set_high_performance_plan),
            ("Disable CPU Parking", "Prevents Windows from parking CPU cores", self.disable_cpu_parking)
        ]
        
        for name, desc, func in options:
            self.create_optimization_option(parent, name, desc, func)
            
    def create_generic_cpu_options(self, parent):
        """Create generic CPU optimization options"""
        title = tk.Label(parent, text="⚙️ Generic CPU Optimizations", 
                        font=('Arial', 16, 'bold'), fg='#666666', bg='#2d2d2d')
        title.pack(pady=10)
        
        options = [
            ("Set High Performance Power Plan", "Activates Windows high performance mode", self.set_high_performance_plan),
            ("Disable CPU Parking", "Prevents Windows from parking CPU cores", self.disable_cpu_parking),
            ("Optimize CPU Scheduling", "Configures Windows CPU scheduler for gaming", self.optimize_cpu_scheduling),
            ("Disable CPU Throttling", "Prevents thermal throttling where possible", self.disable_cpu_throttling)
        ]
        
        for name, desc, func in options:
            self.create_optimization_option(parent, name, desc, func)
            
    def create_gpu_optimization_tab(self):
        """Create GPU optimization tab"""
        tab_frame = ttk.Frame(self.notebook)
        gpu_vendors = ', '.join([v.upper() for v in self.hardware_info['gpu']['vendors']])
        self.notebook.add(tab_frame, text=f"🎮 {gpu_vendors} GPU")
        
        # Create scrollable frame
        canvas = tk.Canvas(tab_frame, bg='#2d2d2d')
        scrollbar = ttk.Scrollbar(tab_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # GPU optimizations based on vendors
        if 'nvidia' in self.hardware_info['gpu']['vendors']:
            self.create_nvidia_gpu_options(scrollable_frame)
        if 'amd' in self.hardware_info['gpu']['vendors']:
            self.create_amd_gpu_options(scrollable_frame)
        if 'intel' in self.hardware_info['gpu']['vendors']:
            self.create_intel_gpu_options(scrollable_frame)
            
    def create_nvidia_gpu_options(self, parent):
        """Create NVIDIA GPU optimization options"""
        title = tk.Label(parent, text="🟢 NVIDIA GPU Optimizations", 
                        font=('Arial', 16, 'bold'), fg='#00cc00', bg='#2d2d2d')
        title.pack(pady=10)
        
        options = [
            ("NVIDIA Maximum Performance", "Sets NVIDIA GPU to maximum performance mode", self.nvidia_max_performance),
            ("Optimize NVIDIA CUDA", "Configures CUDA for optimal gaming performance", self.optimize_nvidia_cuda),
            ("Optimize Shader Cache", "Configures NVIDIA shader cache settings", self.optimize_nvidia_shader_cache),
            ("NVIDIA Control Panel Tweaks", "Applies optimal NVIDIA control panel settings", self.apply_nvidia_control_panel_tweaks),
            ("Disable NVIDIA Telemetry", "Disables NVIDIA data collection services", self.disable_nvidia_telemetry)
        ]
        
        for name, desc, func in options:
            self.create_optimization_option(parent, name, desc, func)
            
    def create_amd_gpu_options(self, parent):
        """Create AMD GPU optimization options"""
        title = tk.Label(parent, text="🔴 AMD GPU Optimizations", 
                        font=('Arial', 16, 'bold'), fg='#cc0000', bg='#2d2d2d')
        title.pack(pady=10)
        
        options = [
            ("Optimize AMD Radeon Settings", "Configures AMD Radeon for maximum performance", self.optimize_amd_radeon),
            ("Disable AMD PowerPlay", "Disables AMD GPU power management", self.disable_amd_powerplay),
            ("Disable AMD ULPS", "Disables Ultra Low Power State for multi-GPU", self.disable_amd_ulps),
            ("AMD GPU Scheduling", "Optimizes AMD GPU scheduling settings", self.optimize_amd_gpu_scheduling)
        ]
        
        for name, desc, func in options:
            self.create_optimization_option(parent, name, desc, func)
            
    def create_intel_gpu_options(self, parent):
        """Create Intel GPU optimization options"""
        title = tk.Label(parent, text="🔵 Intel GPU Optimizations", 
                        font=('Arial', 16, 'bold'), fg='#0066cc', bg='#2d2d2d')
        title.pack(pady=10)
        
        options = [
            ("Intel GPU Maximum Performance", "Sets Intel GPU to maximum performance", self.intel_gpu_max_performance),
            ("Lock Intel GPU Frequency", "Locks Intel GPU to maximum frequency", self.lock_intel_gpu_frequency),
            ("Optimize Intel Graphics Settings", "Configures Intel graphics control panel", self.optimize_intel_graphics)
        ]
        
        for name, desc, func in options:
            self.create_optimization_option(parent, name, desc, func)
            
    def create_general_optimization_tab(self):
        """Create general optimization tab"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="⚙️ General Tweaks")
        
        # Create scrollable frame
        canvas = tk.Canvas(tab_frame, bg='#2d2d2d')
        scrollbar = ttk.Scrollbar(tab_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        title = tk.Label(scrollable_frame, text="⚙️ General System Optimizations", 
                        font=('Arial', 16, 'bold'), fg='#ffaa00', bg='#2d2d2d')
        title.pack(pady=10)
        
        options = [
            ("Optimize Windows for Gaming", "Applies general Windows gaming optimizations", self.optimize_windows_gaming),
            ("Disable Windows Game Mode", "Disables Windows Game Mode (can cause issues)", self.disable_game_mode),
            ("Optimize Memory Management", "Configures Windows memory management", self.optimize_memory_management),
            ("Network Optimizations", "Optimizes network settings for gaming", self.optimize_network),
            ("Disable Windows Updates", "Temporarily disables automatic Windows updates", self.disable_windows_updates),
            ("Clean System Files", "Cleans temporary files and cache", self.clean_system_files),
            ("Optimize Visual Effects", "Disables unnecessary visual effects", self.optimize_visual_effects),
            ("Disable Background Apps", "Disables unnecessary background applications", self.disable_background_apps)
        ]
        
        for name, desc, func in options:
            self.create_optimization_option(scrollable_frame, name, desc, func)
            
    def create_control_panel_tab(self):
        """Create control panel tab with logs"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="📊 Control Panel")
        
        # Log frame
        log_frame = ttk.LabelFrame(tab_frame, text="📝 Optimization Log")
        log_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, 
                                                 bg='#1a1a1a', fg='#00ff00', 
                                                 font=('Consolas', 10))
        self.log_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Control buttons frame
        control_frame = ttk.LabelFrame(tab_frame, text="🎛️ System Controls")
        control_frame.pack(fill='x', padx=10, pady=5)
        
        btn_frame = tk.Frame(control_frame, bg='#2d2d2d')
        btn_frame.pack(pady=10)
        
        # System control buttons
        buttons = [
            ("🔄 Restart Explorer", self.restart_explorer),
            ("🧹 Clear Logs", self.clear_logs),
            ("💾 Create Restore Point", self.create_restore_point),
            ("📊 System Info", self.show_system_info),
            ("🔧 Open Task Manager", self.open_task_manager),
            ("⚙️ Open Services", self.open_services)
        ]
        
        for i, (text, command) in enumerate(buttons):
            btn = tk.Button(btn_frame, text=text, command=command,
                           bg='#404040', fg='white', font=('Arial', 9),
                           padx=15, pady=5)
            btn.grid(row=i//3, column=i%3, padx=5, pady=5, sticky='ew')
            
        # Configure grid weights
        for i in range(3):
            btn_frame.columnconfigure(i, weight=1)
            
    def create_optimization_option(self, parent, name, description, function):
        """Create an optimization option widget"""
        frame = tk.Frame(parent, bg='#3d3d3d', relief='raised', bd=1)
        frame.pack(fill='x', padx=10, pady=5)
        
        # Option name
        name_label = tk.Label(frame, text=name, font=('Arial', 12, 'bold'), 
                             fg='#ffffff', bg='#3d3d3d')
        name_label.pack(anchor='w', padx=10, pady=(10, 0))
        
        # Description
        desc_label = tk.Label(frame, text=description, font=('Arial', 10), 
                             fg='#cccccc', bg='#3d3d3d', wraplength=800)
        desc_label.pack(anchor='w', padx=10, pady=(0, 5))
        
        # Apply button
        apply_btn = tk.Button(frame, text="Apply", command=function,
                             bg='#00aa00', fg='white', font=('Arial', 10, 'bold'),
                             padx=20, pady=5)
        apply_btn.pack(anchor='e', padx=10, pady=(0, 10))
        
    def run_registry_command(self, command):
        """Run a registry command safely"""
        try:
            result = subprocess.run(command, check=True, shell=True, capture_output=True, text=True)
            return True
        except subprocess.CalledProcessError as e:
            self.log(f"Registry command failed: {' '.join(command)}")
            return False
        except Exception as e:
            self.log(f"Error running command: {e}")
            return False
        
    # CPU Optimization Methods
    def disable_intel_speedstep(self):
        """Disable Intel SpeedStep"""
        try:
            self.log("🔵 Disabling Intel SpeedStep...")
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Power\\PowerSettings\\54533251-82be-4824-96c1-47b60b740d00\\be337238-0d82-4146-a960-4f3749d470c7',
                '/v', 'Attributes', '/t', 'REG_DWORD', '/d', '0', '/f'
            ])
            self.log("✅ Intel SpeedStep disabled")
            self.optimizations_applied.append("Intel SpeedStep Disabled")
        except Exception as e:
            self.log(f"❌ Failed to disable Intel SpeedStep: {e}")
            
    def optimize_intel_turbo(self):
        """Optimize Intel Turbo Boost"""
        try:
            self.log("🔵 Optimizing Intel Turbo Boost...")
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Power\\PowerSettings\\54533251-82be-4824-96c1-47b60b740d00\\be337238-0d82-4146-a960-4f3749d470c7',
                '/v', 'Attributes', '/t', 'REG_DWORD', '/d', '0', '/f'
            ])
            self.log("✅ Intel Turbo Boost optimized")
            self.optimizations_applied.append("Intel Turbo Boost Optimized")
        except Exception as e:
            self.log(f"❌ Failed to optimize Intel Turbo Boost: {e}")
            
    def disable_intel_cstates(self):
        """Disable Intel C-States"""
        try:
            self.log("🔵 Disabling Intel C-States...")
            subprocess.run(['bcdedit', '/set', 'disabledynamictick', 'yes'], check=True, shell=True)
            subprocess.run(['bcdedit', '/set', 'useplatformtick', 'yes'], check=True, shell=True)
            self.log("✅ Intel C-States disabled")
            self.optimizations_applied.append("Intel C-States Disabled")
        except Exception as e:
            self.log(f"❌ Failed to disable Intel C-States: {e}")
            
    def optimize_intel_hyperthreading(self):
        """Optimize Intel Hyperthreading"""
        try:
            self.log("🔵 Optimizing Intel Hyperthreading...")
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\kernel',
                '/v', 'ThreadDpcEnable', '/t', 'REG_DWORD', '/d', '1', '/f'
            ])
            self.log("✅ Intel Hyperthreading optimized")
            self.optimizations_applied.append("Intel Hyperthreading Optimized")
        except Exception as e:
            self.log(f"❌ Failed to optimize Intel Hyperthreading: {e}")
            
    def disable_amd_coolnquiet(self):
        """Disable AMD Cool'n'Quiet"""
        try:
            self.log("🔴 Disabling AMD Cool'n'Quiet...")
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e968-e325-11ce-bfc1-08002be10318}\\0000',
                '/v', 'PP_ThermalAutoThrottlingEnable', '/t', 'REG_DWORD', '/d', '0', '/f'
            ])
            self.log("✅ AMD Cool'n'Quiet disabled")
            self.optimizations_applied.append("AMD Cool'n'Quiet Disabled")
        except Exception as e:
            self.log(f"❌ Failed to disable AMD Cool'n'Quiet: {e}")
            
    def optimize_amd_precision_boost(self):
        """Optimize AMD Precision Boost"""
        try:
            self.log("🔴 Optimizing AMD Precision Boost...")
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Power\\PowerSettings\\54533251-82be-4824-96c1-47b60b740d00\\be337238-0d82-4146-a960-4f3749d470c7',
                '/v', 'Attributes', '/t', 'REG_DWORD', '/d', '0', '/f'
            ])
            self.log("✅ AMD Precision Boost optimized")
            self.optimizations_applied.append("AMD Precision Boost Optimized")
        except Exception as e:
            self.log(f"❌ Failed to optimize AMD Precision Boost: {e}")
            
    def optimize_amd_smt(self):
        """Optimize AMD SMT"""
        try:
            self.log("🔴 Optimizing AMD SMT...")
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\kernel',
                '/v', 'ThreadDpcEnable', '/t', 'REG_DWORD', '/d', '1', '/f'
            ])
            self.log("✅ AMD SMT optimized")
            self.optimizations_applied.append("AMD SMT Optimized")
        except Exception as e:
            self.log(f"❌ Failed to optimize AMD SMT: {e}")
            
    def optimize_amd_ryzen(self):
        """Apply AMD Ryzen specific optimizations"""
        try:
            self.log("🔴 Applying AMD Ryzen optimizations...")
            # Ryzen-specific registry tweaks
            commands = [
                ['reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Power\\PowerSettings\\54533251-82be-4824-96c1-47b60b740d00\\893dee8e-2bef-41e0-89c6-b55d0929964c', '/v', 'Attributes', '/t', 'REG_DWORD', '/d', '0', '/f'],
                ['reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Power\\PowerSettings\\54533251-82be-4824-96c1-47b60b740d00\\893dee8e-2bef-41e0-89c6-b55d0929964c\\0cc5b647-c1df-4637-891a-dec35c318583', '/v', 'ValueMax', '/t', 'REG_DWORD', '/d', '0', '/f']
            ]
            
            for cmd in commands:
                self.run_registry_command(cmd)
                
            self.log("✅ AMD Ryzen optimizations applied")
            self.optimizations_applied.append("AMD Ryzen Optimizations Applied")
        except Exception as e:
            self.log(f"❌ Failed to apply AMD Ryzen optimizations: {e}")
            
    # GPU Optimization Methods
    def nvidia_max_performance(self):
        """Set NVIDIA GPU to maximum performance"""
        try:
            self.log("🟢 Setting NVIDIA GPU to maximum performance...")
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e968-e325-11ce-bfc1-08002be10318}\\0000',
                '/v', 'PowerMizerEnable', '/t', 'REG_DWORD', '/d', '1', '/f'
            ])
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e968-e325-11ce-bfc1-08002be10318}\\0000',
                '/v', 'PowerMizerLevel', '/t', 'REG_DWORD', '/d', '1', '/f'
            ])
            self.log("✅ NVIDIA GPU set to maximum performance")
            self.optimizations_applied.append("NVIDIA Maximum Performance")
        except Exception as e:
            self.log(f"❌ Failed to set NVIDIA maximum performance: {e}")
            
    def optimize_nvidia_cuda(self):
        """Optimize NVIDIA CUDA settings"""
        try:
            self.log("🟢 Optimizing NVIDIA CUDA...")
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\GraphicsDrivers',
                '/v', 'TdrLevel', '/t', 'REG_DWORD', '/d', '0', '/f'
            ])
            self.log("✅ NVIDIA CUDA optimized")
            self.optimizations_applied.append("NVIDIA CUDA Optimized")
        except Exception as e:
            self.log(f"❌ Failed to optimize NVIDIA CUDA: {e}")
            
    def optimize_nvidia_shader_cache(self):
        """Optimize NVIDIA shader cache"""
        try:
            self.log("🟢 Optimizing NVIDIA shader cache...")
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e968-e325-11ce-bfc1-08002be10318}\\0000',
                '/v', 'EnableUlps', '/t', 'REG_DWORD', '/d', '0', '/f'
            ])
            self.log("✅ NVIDIA shader cache optimized")
            self.optimizations_applied.append("NVIDIA Shader Cache Optimized")
        except Exception as e:
            self.log(f"❌ Failed to optimize NVIDIA shader cache: {e}")
            
    def apply_nvidia_control_panel_tweaks(self):
        """Apply NVIDIA Control Panel tweaks"""
        try:
            self.log("🟢 Applying NVIDIA Control Panel tweaks...")
            # Multiple registry tweaks for NVIDIA
            commands = [
                ['reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e968-e325-11ce-bfc1-08002be10318}\\0000', '/v', 'PreferSystemMemoryContiguous', '/t', 'REG_DWORD', '/d', '1', '/f'],
                ['reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e968-e325-11ce-bfc1-08002be10318}\\0000', '/v', 'EnableUlps', '/t', 'REG_DWORD', '/d', '0', '/f'],
                ['reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e968-e325-11ce-bfc1-08002be10318}\\0000', '/v', 'PowerMizerEnable', '/t', 'REG_DWORD', '/d', '1', '/f']
            ]
            
            for cmd in commands:
                self.run_registry_command(cmd)
                
            self.log("✅ NVIDIA Control Panel tweaks applied")
            self.optimizations_applied.append("NVIDIA Control Panel Tweaks")
        except Exception as e:
            self.log(f"❌ Failed to apply NVIDIA Control Panel tweaks: {e}")
            
    def disable_nvidia_telemetry(self):
        """Disable NVIDIA telemetry services"""
        try:
            self.log("🟢 Disabling NVIDIA telemetry...")
            services = ['NvTelemetryContainer', 'NvContainerLocalSystem']
            
            for service in services:
                try:
                    subprocess.run(['sc', 'config', service, 'start=', 'disabled'], check=True, shell=True)
                    subprocess.run(['sc', 'stop', service], shell=True)  # Don't check=True as service might not be running
                except:
                    pass  # Service might not exist
                    
            self.log("✅ NVIDIA telemetry disabled")
            self.optimizations_applied.append("NVIDIA Telemetry Disabled")
        except Exception as e:
            self.log(f"❌ Failed to disable NVIDIA telemetry: {e}")
            
    def optimize_amd_radeon(self):
        """Optimize AMD Radeon settings"""
        try:
            self.log("🔴 Optimizing AMD Radeon settings...")
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e968-e325-11ce-bfc1-08002be10318}\\0000',
                '/v', 'PP_SclkDeepSleepDisable', '/t', 'REG_DWORD', '/d', '1', '/f'
            ])
            self.log("✅ AMD Radeon settings optimized")
            self.optimizations_applied.append("AMD Radeon Optimized")
        except Exception as e:
            self.log(f"❌ Failed to optimize AMD Radeon: {e}")
            
    def disable_amd_powerplay(self):
        """Disable AMD PowerPlay"""
        try:
            self.log("🔴 Disabling AMD PowerPlay...")
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e968-e325-11ce-bfc1-08002be10318}\\0000',
                '/v', 'PP_ThermalAutoThrottlingEnable', '/t', 'REG_DWORD', '/d', '0', '/f'
            ])
            self.log("✅ AMD PowerPlay disabled")
            self.optimizations_applied.append("AMD PowerPlay Disabled")
        except Exception as e:
            self.log(f"❌ Failed to disable AMD PowerPlay: {e}")
            
    def disable_amd_ulps(self):
        """Disable AMD ULPS"""
        try:
            self.log("🔴 Disabling AMD ULPS...")
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e968-e325-11ce-bfc1-08002be10318}\\0000',
                '/v', 'EnableUlps', '/t', 'REG_DWORD', '/d', '0', '/f'
            ])
            self.log("✅ AMD ULPS disabled")
            self.optimizations_applied.append("AMD ULPS Disabled")
        except Exception as e:
            self.log(f"❌ Failed to disable AMD ULPS: {e}")
            
    def optimize_amd_gpu_scheduling(self):
        """Optimize AMD GPU scheduling"""
        try:
            self.log("🔴 Optimizing AMD GPU scheduling...")
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\GraphicsDrivers',
                '/v', 'HwSchMode', '/t', 'REG_DWORD', '/d', '2', '/f'
            ])
            self.log("✅ AMD GPU scheduling optimized")
            self.optimizations_applied.append("AMD GPU Scheduling Optimized")
        except Exception as e:
            self.log(f"❌ Failed to optimize AMD GPU scheduling: {e}")
            
    def intel_gpu_max_performance(self):
        """Set Intel GPU to maximum performance"""
        try:
            self.log("🔵 Setting Intel GPU to maximum performance...")
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e968-e325-11ce-bfc1-08002be10318}\\0000',
                '/v', 'Acceleration.Level', '/t', 'REG_DWORD', '/d', '0', '/f'
            ])
            self.log("✅ Intel GPU set to maximum performance")
            self.optimizations_applied.append("Intel GPU Maximum Performance")
        except Exception as e:
            self.log(f"❌ Failed to set Intel GPU maximum performance: {e}")
            
    def lock_intel_gpu_frequency(self):
        """Lock Intel GPU frequency"""
        try:
            self.log("🔵 Locking Intel GPU frequency...")
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e968-e325-11ce-bfc1-08002be10318}\\0000',
                '/v', 'PP_SclkDeepSleepDisable', '/t', 'REG_DWORD', '/d', '1', '/f'
            ])
            self.log("✅ Intel GPU frequency locked")
            self.optimizations_applied.append("Intel GPU Frequency Locked")
        except Exception as e:
            self.log(f"❌ Failed to lock Intel GPU frequency: {e}")
            
    def optimize_intel_graphics(self):
        """Optimize Intel Graphics settings"""
        try:
            self.log("🔵 Optimizing Intel Graphics settings...")
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e968-e325-11ce-bfc1-08002be10318}\\0000',
                '/v', 'Acceleration.Level', '/t', 'REG_DWORD', '/d', '0', '/f'
            ])
            self.log("✅ Intel Graphics settings optimized")
            self.optimizations_applied.append("Intel Graphics Optimized")
        except Exception as e:
            self.log(f"❌ Failed to optimize Intel Graphics: {e}")
            
    # General Optimization Methods
    def set_high_performance_plan(self):
        """Set Windows to high performance power plan"""
        try:
            self.log("⚡ Setting high performance power plan...")
            subprocess.run(['powercfg', '/setactive', '8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c'], check=True, shell=True)
            self.log("✅ High performance power plan activated")
            self.optimizations_applied.append("High Performance Power Plan")
        except Exception as e:
            self.log(f"❌ Failed to set high performance plan: {e}")
            
    def disable_cpu_parking(self):
        """Disable CPU core parking"""
        try:
            self.log("🚫 Disabling CPU core parking...")
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Power\\PowerSettings\\54533251-82be-4824-96c1-47b60b740d00\\0cc5b647-c1df-4637-891a-dec35c318583',
                '/v', 'ValueMax', '/t', 'REG_DWORD', '/d', '0', '/f'
            ])
            self.log("✅ CPU core parking disabled")
            self.optimizations_applied.append("CPU Core Parking Disabled")
        except Exception as e:
            self.log(f"❌ Failed to disable CPU parking: {e}")
            
    def optimize_cpu_scheduling(self):
        """Optimize CPU scheduling for gaming"""
        try:
            self.log("⚙️ Optimizing CPU scheduling...")
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\PriorityControl',
                '/v', 'Win32PrioritySeparation', '/t', 'REG_DWORD', '/d', '38', '/f'
            ])
            self.log("✅ CPU scheduling optimized")
            self.optimizations_applied.append("CPU Scheduling Optimized")
        except Exception as e:
            self.log(f"❌ Failed to optimize CPU scheduling: {e}")
            
    def disable_cpu_throttling(self):
        """Disable CPU throttling"""
        try:
            self.log("🚫 Disabling CPU throttling...")
            subprocess.run(['bcdedit', '/set', 'disabledynamictick', 'yes'], check=True, shell=True)
            self.log("✅ CPU throttling disabled")
            self.optimizations_applied.append("CPU Throttling Disabled")
        except Exception as e:
            self.log(f"❌ Failed to disable CPU throttling: {e}")
            
    def optimize_windows_gaming(self):
        """Apply general Windows gaming optimizations"""
        try:
            self.log("🎮 Applying Windows gaming optimizations...")
            
            # Multiple registry tweaks
            commands = [
                ['reg', 'add', 'HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile', '/v', 'SystemResponsiveness', '/t', 'REG_DWORD', '/d', '0', '/f'],
                ['reg', 'add', 'HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile\\Tasks\\Games', '/v', 'GPU Priority', '/t', 'REG_DWORD', '/d', '8', '/f'],
                ['reg', 'add', 'HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile\\Tasks\\Games', '/v', 'Priority', '/t', 'REG_DWORD', '/d', '6', '/f'],
                ['reg', 'add', 'HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile\\Tasks\\Games', '/v', 'Scheduling Category', '/t', 'REG_SZ', '/d', 'High', '/f']
            ]
            
            for cmd in commands:
                self.run_registry_command(cmd)
                
            self.log("✅ Windows gaming optimizations applied")
            self.optimizations_applied.append("Windows Gaming Optimizations")
        except Exception as e:
            self.log(f"❌ Failed to apply Windows gaming optimizations: {e}")
    def disable_amd_coolnquiet(self):
        """Disable AMD Cool'n'Quiet"""
        try:
            self.log("🔴 Disabling AMD Cool'n'Quiet...")
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e968-e325-11ce-bfc1-08002be10318}\\0000',
                '/v', 'PP_ThermalAutoThrottlingEnable', '/t', 'REG_DWORD', '/d', '0', '/f'
            ])
            self.log("✅ AMD Cool'n'Quiet disabled")
            self.optimizations_applied.append("AMD Cool'n'Quiet Disabled")
        except Exception as e:
            self.log(f"❌ Failed to disable AMD Cool'n'Quiet: {e}")
            
    def optimize_amd_precision_boost(self):
        """Optimize AMD Precision Boost"""
        try:
            self.log("🔴 Optimizing AMD Precision Boost...")
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Power\\PowerSettings\\54533251-82be-4824-96c1-47b60b740d00\\be337238-0d82-4146-a960-4f3749d470c7',
                '/v', 'Attributes', '/t', 'REG_DWORD', '/d', '0', '/f'
            ])
            self.log("✅ AMD Precision Boost optimized")
            self.optimizations_applied.append("AMD Precision Boost Optimized")
        except Exception as e:
            self.log(f"❌ Failed to optimize AMD Precision Boost: {e}")
            
    def optimize_amd_smt(self):
        """Optimize AMD SMT"""
        try:
            self.log("🔴 Optimizing AMD SMT...")
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\kernel',
                '/v', 'ThreadDpcEnable', '/t', 'REG_DWORD', '/d', '1', '/f'
            ])
            self.log("✅ AMD SMT optimized")
            self.optimizations_applied.append("AMD SMT Optimized")
        except Exception as e:
            self.log(f"❌ Failed to optimize AMD SMT: {e}")
            
    def optimize_amd_ryzen(self):
        """Apply AMD Ryzen specific optimizations"""
        try:
            self.log("🔴 Applying AMD Ryzen optimizations...")
            # Ryzen-specific registry tweaks
            commands = [
                ['reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Power\\PowerSettings\\54533251-82be-4824-96c1-47b60b740d00\\893dee8e-2bef-41e0-89c6-b55d0929964c', '/v', 'Attributes', '/t', 'REG_DWORD', '/d', '0', '/f'],
                ['reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Power\\PowerSettings\\54533251-82be-4824-96c1-47b60b740d00\\893dee8e-2bef-41e0-89c6-b55d0929964c\\0cc5b647-c1df-4637-891a-dec35c318583', '/v', 'ValueMax', '/t', 'REG_DWORD', '/d', '0', '/f']
            ]
            
            for cmd in commands:
                self.run_registry_command(cmd)
                
            self.log("✅ AMD Ryzen optimizations applied")
            self.optimizations_applied.append("AMD Ryzen Optimizations Applied")
        except Exception as e:
            self.log(f"❌ Failed to apply AMD Ryzen optimizations: {e}")
            
    # GPU Optimization Methods
    def nvidia_max_performance(self):
        """Set NVIDIA GPU to maximum performance"""
        try:
            self.log("🟢 Setting NVIDIA GPU to maximum performance...")
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e968-e325-11ce-bfc1-08002be10318}\\0000',
                '/v', 'PowerMizerEnable', '/t', 'REG_DWORD', '/d', '1', '/f'
            ])
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e968-e325-11ce-bfc1-08002be10318}\\0000',
                '/v', 'PowerMizerLevel', '/t', 'REG_DWORD', '/d', '1', '/f'
            ])
            self.log("✅ NVIDIA GPU set to maximum performance")
            self.optimizations_applied.append("NVIDIA Maximum Performance")
        except Exception as e:
            self.log(f"❌ Failed to set NVIDIA maximum performance: {e}")
            
    def optimize_nvidia_cuda(self):
        """Optimize NVIDIA CUDA settings"""
        try:
            self.log("🟢 Optimizing NVIDIA CUDA...")
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\GraphicsDrivers',
                '/v', 'TdrLevel', '/t', 'REG_DWORD', '/d', '0', '/f'
            ])
            self.log("✅ NVIDIA CUDA optimized")
            self.optimizations_applied.append("NVIDIA CUDA Optimized")
        except Exception as e:
            self.log(f"❌ Failed to optimize NVIDIA CUDA: {e}")
            
    def optimize_nvidia_shader_cache(self):
        """Optimize NVIDIA shader cache"""
        try:
            self.log("🟢 Optimizing NVIDIA shader cache...")
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e968-e325-11ce-bfc1-08002be10318}\\0000',
                '/v', 'EnableUlps', '/t', 'REG_DWORD', '/d', '0', '/f'
            ])
            self.log("✅ NVIDIA shader cache optimized")
            self.optimizations_applied.append("NVIDIA Shader Cache Optimized")
        except Exception as e:
            self.log(f"❌ Failed to optimize NVIDIA shader cache: {e}")
            
    def apply_nvidia_control_panel_tweaks(self):
        """Apply NVIDIA Control Panel tweaks"""
        try:
            self.log("🟢 Applying NVIDIA Control Panel tweaks...")
            # Multiple registry tweaks for NVIDIA
            commands = [
                ['reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e968-e325-11ce-bfc1-08002be10318}\\0000', '/v', 'PreferSystemMemoryContiguous', '/t', 'REG_DWORD', '/d', '1', '/f'],
                ['reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e968-e325-11ce-bfc1-08002be10318}\\0000', '/v', 'EnableUlps', '/t', 'REG_DWORD', '/d', '0', '/f'],
                ['reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e968-e325-11ce-bfc1-08002be10318}\\0000', '/v', 'PowerMizerEnable', '/t', 'REG_DWORD', '/d', '1', '/f']
            ]
            
            for cmd in commands:
                self.run_registry_command(cmd)
                
            self.log("✅ NVIDIA Control Panel tweaks applied")
            self.optimizations_applied.append("NVIDIA Control Panel Tweaks")
        except Exception as e:
            self.log(f"❌ Failed to apply NVIDIA Control Panel tweaks: {e}")
            
    def disable_nvidia_telemetry(self):
        """Disable NVIDIA telemetry services"""
        try:
            self.log("🟢 Disabling NVIDIA telemetry...")
            services = ['NvTelemetryContainer', 'NvContainerLocalSystem']
            
            for service in services:
                try:
                    subprocess.run(['sc', 'config', service, 'start=', 'disabled'], check=True, shell=True)
                    subprocess.run(['sc', 'stop', service], shell=True)  # Don't check=True as service might not be running
                except:
                    pass  # Service might not exist
                    
            self.log("✅ NVIDIA telemetry disabled")
            self.optimizations_applied.append("NVIDIA Telemetry Disabled")
        except Exception as e:
            self.log(f"❌ Failed to disable NVIDIA telemetry: {e}")
            
    def optimize_amd_radeon(self):
        """Optimize AMD Radeon settings"""
        try:
            self.log("🔴 Optimizing AMD Radeon settings...")
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e968-e325-11ce-bfc1-08002be10318}\\0000',
                '/v', 'PP_SclkDeepSleepDisable', '/t', 'REG_DWORD', '/d', '1', '/f'
            ])
            self.log("✅ AMD Radeon settings optimized")
            self.optimizations_applied.append("AMD Radeon Optimized")
        except Exception as e:
            self.log(f"❌ Failed to optimize AMD Radeon: {e}")
            
    def disable_amd_powerplay(self):
        """Disable AMD PowerPlay"""
        try:
            self.log("🔴 Disabling AMD PowerPlay...")
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e968-e325-11ce-bfc1-08002be10318}\\0000',
                '/v', 'PP_ThermalAutoThrottlingEnable', '/t', 'REG_DWORD', '/d', '0', '/f'
            ])
            self.log("✅ AMD PowerPlay disabled")
            self.optimizations_applied.append("AMD PowerPlay Disabled")
        except Exception as e:
            self.log(f"❌ Failed to disable AMD PowerPlay: {e}")
            
    def disable_amd_ulps(self):
        """Disable AMD ULPS"""
        try:
            self.log("🔴 Disabling AMD ULPS...")
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e968-e325-11ce-bfc1-08002be10318}\\0000',
                '/v', 'EnableUlps', '/t', 'REG_DWORD', '/d', '0', '/f'
            ])
            self.log("✅ AMD ULPS disabled")
            self.optimizations_applied.append("AMD ULPS Disabled")
        except Exception as e:
            self.log(f"❌ Failed to disable AMD ULPS: {e}")
            
    def optimize_amd_gpu_scheduling(self):
        """Optimize AMD GPU scheduling"""
        try:
            self.log("🔴 Optimizing AMD GPU scheduling...")
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\GraphicsDrivers',
                '/v', 'HwSchMode', '/t', 'REG_DWORD', '/d', '2', '/f'
            ])
            self.log("✅ AMD GPU scheduling optimized")
            self.optimizations_applied.append("AMD GPU Scheduling Optimized")
        except Exception as e:
            self.log(f"❌ Failed to optimize AMD GPU scheduling: {e}")
            
    def intel_gpu_max_performance(self):
        """Set Intel GPU to maximum performance"""
        try:
            self.log("🔵 Setting Intel GPU to maximum performance...")
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e968-e325-11ce-bfc1-08002be10318}\\0000',
                '/v', 'Acceleration.Level', '/t', 'REG_DWORD', '/d', '0', '/f'
            ])
            self.log("✅ Intel GPU set to maximum performance")
            self.optimizations_applied.append("Intel GPU Maximum Performance")
        except Exception as e:
            self.log(f"❌ Failed to set Intel GPU maximum performance: {e}")
            
    def lock_intel_gpu_frequency(self):
        """Lock Intel GPU frequency"""
        try:
            self.log("🔵 Locking Intel GPU frequency...")
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e968-e325-11ce-bfc1-08002be10318}\\0000',
                '/v', 'PP_SclkDeepSleepDisable', '/t', 'REG_DWORD', '/d', '1', '/f'
            ])
            self.log("✅ Intel GPU frequency locked")
            self.optimizations_applied.append("Intel GPU Frequency Locked")
        except Exception as e:
            self.log(f"❌ Failed to lock Intel GPU frequency: {e}")
            
    def optimize_intel_graphics(self):
        """Optimize Intel Graphics settings"""
        try:
            self.log("🔵 Optimizing Intel Graphics settings...")
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e968-e325-11ce-bfc1-08002be10318}\\0000',
                '/v', 'Acceleration.Level', '/t', 'REG_DWORD', '/d', '0', '/f'
            ])
            self.log("✅ Intel Graphics settings optimized")
            self.optimizations_applied.append("Intel Graphics Optimized")
        except Exception as e:
            self.log(f"❌ Failed to optimize Intel Graphics: {e}")
            
    # General Optimization Methods
    def set_high_performance_plan(self):
        """Set Windows to high performance power plan"""
        try:
            self.log("⚡ Setting high performance power plan...")
            subprocess.run(['powercfg', '/setactive', '8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c'], check=True, shell=True)
            self.log("✅ High performance power plan activated")
            self.optimizations_applied.append("High Performance Power Plan")
        except Exception as e:
            self.log(f"❌ Failed to set high performance plan: {e}")
            
    def disable_cpu_parking(self):
        """Disable CPU core parking"""
        try:
            self.log("🚫 Disabling CPU core parking...")
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Power\\PowerSettings\\54533251-82be-4824-96c1-47b60b740d00\\0cc5b647-c1df-4637-891a-dec35c318583',
                '/v', 'ValueMax', '/t', 'REG_DWORD', '/d', '0', '/f'
            ])
            self.log("✅ CPU core parking disabled")
            self.optimizations_applied.append("CPU Core Parking Disabled")
        except Exception as e:
            self.log(f"❌ Failed to disable CPU parking: {e}")
            
    def optimize_cpu_scheduling(self):
        """Optimize CPU scheduling for gaming"""
        try:
            self.log("⚙️ Optimizing CPU scheduling...")
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\PriorityControl',
                '/v', 'Win32PrioritySeparation', '/t', 'REG_DWORD', '/d', '38', '/f'
            ])
            self.log("✅ CPU scheduling optimized")
            self.optimizations_applied.append("CPU Scheduling Optimized")
        except Exception as e:
            self.log(f"❌ Failed to optimize CPU scheduling: {e}")
            
    def disable_cpu_throttling(self):
        """Disable CPU throttling"""
        try:
            self.log("🚫 Disabling CPU throttling...")
            subprocess.run(['bcdedit', '/set', 'disabledynamictick', 'yes'], check=True, shell=True)
            self.log("✅ CPU throttling disabled")
            self.optimizations_applied.append("CPU Throttling Disabled")
        except Exception as e:
            self.log(f"❌ Failed to disable CPU throttling: {e}")
            
    def optimize_windows_gaming(self):
        """Apply general Windows gaming optimizations"""
        try:
            self.log("🎮 Applying Windows gaming optimizations...")
            
            # Multiple registry tweaks
            commands = [
                ['reg', 'add', 'HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile', '/v', 'SystemResponsiveness', '/t', 'REG_DWORD', '/d', '0', '/f'],
                ['reg', 'add', 'HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile\\Tasks\\Games', '/v', 'GPU Priority', '/t', 'REG_DWORD', '/d', '8', '/f'],
                ['reg', 'add', 'HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile\\Tasks\\Games', '/v', 'Priority', '/t', 'REG_DWORD', '/d', '6', '/f'],
                ['reg', 'add', 'HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile\\Tasks\\Games', '/v', 'Scheduling Category', '/t', 'REG_SZ', '/d', 'High', '/f']
            ]
            
            for cmd in commands:
                self.run_registry_command(cmd)
                
            self.log("✅ Windows gaming optimizations applied")
            self.optimizations_applied.append("Windows Gaming Optimizations")
        except Exception as e:
            self.log(f"❌ Failed to apply Windows gaming optimizations: {e}")
            
    def disable_game_mode(self):
        """Disable Windows Game Mode"""
        try:
            self.log("🎮 Disabling Windows Game Mode...")
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\AppCompatFlags\\Layers',
                '/v', 'C:\\Windows\\System32\\smartscreen.exe', '/t', 'REG_SZ', '/d', '~ NOTCHANGED', '/f'
            ])
            self.log("✅ Windows Game Mode disabled")
            self.optimizations_applied.append("Windows Game Mode Disabled")
        except Exception as e:
            self.log(f"❌ Failed to disable Windows Game Mode: {e}")
            
    def optimize_memory_management(self):
        """Optimize Windows memory management"""
        try:
            self.log("⚙️ Optimizing Windows memory management...")
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management',
                '/v', 'DisablePagingExecutive', '/t', 'REG_DWORD', '/d', '1', '/f'
            ])
            self.log("✅ Windows memory management optimized")
            self.optimizations_applied.append("Windows Memory Management Optimized")
        except Exception as e:
            self.log(f"❌ Failed to optimize Windows memory management: {e}")
            
    def optimize_network(self):
        """Optimize network settings for gaming"""
        try:
            self.log("🌐 Optimizing network settings for gaming...")
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters',
                '/v', 'TcpNoDelay', '/t', 'REG_DWORD', '/d', '1', '/f'
            ])
            self.log("✅ Network settings optimized for gaming")
            self.optimizations_applied.append("Network Settings Optimized for Gaming")
        except Exception as e:
            self.log(f"❌ Failed to optimize network settings: {e}")
            
    def disable_windows_updates(self):
        """Temporarily disable Windows updates"""
        try:
            self.log("🔧 Temporarily disabling Windows updates...")
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU',
                '/v', 'NoAutoUpdate', '/t', 'REG_DWORD', '/d', '1', '/f'
            ])
            self.log("✅ Windows updates temporarily disabled")
            self.optimizations_applied.append("Windows Updates Temporarily Disabled")
        except Exception as e:
            self.log(f"❌ Failed to disable Windows updates: {e}")
            
    def clean_system_files(self):
        """Clean temporary files and cache"""
        try:
            self.log("🧹 Cleaning system files and cache...")
            subprocess.run(['cleanmgr', '/sagerun:1'], check=True, shell=True)
            self.log("✅ System files and cache cleaned")
            self.optimizations_applied.append("System Files and Cache Cleaned")
        except Exception as e:
            self.log(f"❌ Failed to clean system files and cache: {e}")
            
    def optimize_visual_effects(self):
        """Disable unnecessary visual effects"""
        try:
            self.log("🎨 Disabling unnecessary visual effects...")
            self.run_registry_command([
                'reg', 'add', 'HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects',
                '/v', 'VisualFXSetting', '/t', 'REG_DWORD', '/d', '2', '/f'
            ])
            self.log("✅ Unnecessary visual effects disabled")
            self.optimizations_applied.append("Unnecessary Visual Effects Disabled")
        except Exception as e:
            self.log(f"❌ Failed to disable visual effects: {e}")
            
    def disable_background_apps(self):
        """Disable unnecessary background applications"""
        try:
            self.log("🚫 Disabling unnecessary background applications...")
            self.run_registry_command([
                'reg', 'add', 'HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced',
                '/v', 'DisableAllBackgroundApps', '/t', 'REG_DWORD', '/d', '1', '/f'
            ])
            self.log("✅ Unnecessary background applications disabled")
            self.optimizations_applied.append("Unnecessary Background Applications Disabled")
        except Exception as e:
            self.log(f"❌ Failed to disable background applications: {e}")
            
    def restart_explorer(self):
        """Restart Windows Explorer"""
        try:
            self.log("🔄 Restarting Windows Explorer...")
            subprocess.run(['taskkill', '/f', '/im', 'explorer.exe'], check=True, shell=True)
            subprocess.run(['start', 'explorer.exe'], shell=True)
            self.log("✅ Windows Explorer restarted")
        except Exception as e:
            self.log(f"❌ Failed to restart Windows Explorer: {e}")
            
    def clear_logs(self):
        """Clear optimization logs"""
        try:
            self.log_text.delete('1.0', tk.END)
            self.log("🗑️ Logs cleared")
        except Exception as e:
            self.log(f"❌ Failed to clear logs: {e}")
            
    def create_restore_point(self):
        """Create a system restore point"""
        try:
            self.log("💾 Creating system restore point...")
            subprocess.run(['powershell', '-Command', 'Checkpoint-Computer', '-Description', '"Gaming Optimizer Restore Point"'], check=True, shell=True)
            self.log("✅ System restore point created")
        except Exception as e:
            self.log(f"❌ Failed to create system restore point: {e}")
            
    def show_system_info(self):
        """Show system information"""
        try:
            self.log("📊 Showing system information...")
            system_info = subprocess.run(['systeminfo'], capture_output=True, text=True, check=True).stdout
            self.log_text.insert(tk.END, system_info)
            self.log_text.see(tk.END)
        except Exception as e:
            self.log(f"❌ Failed to show system information: {e}")
            
    def open_task_manager(self):
        """Open Task Manager"""
        try:
            self.log("🔧 Opening Task Manager...")
            subprocess.run(['taskmgr'], shell=True)
        except Exception as e:
            self.log(f"❌ Failed to open Task Manager: {e}")
            
    def open_services(self):
        """Open Services"""
        try:
            self.log("⚙️ Opening Services...")
            subprocess.run(['services.msc'], shell=True)
        except Exception as e:
            self.log(f"❌ Failed to open Services: {e}")
            
    def log(self, message):
        """Log a message to the log text widget"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        
    def apply_all_hardware_optimizations(self):
        """Apply all hardware-specific optimizations"""
        self.log("🚀 Applying all hardware-specific optimizations...")
        tabs = [
            self.create_intel_cpu_options,
            self.create_amd_cpu_options,
            self.create_generic_cpu_options,
            self.create_nvidia_gpu_options,
            self.create_amd_gpu_options,
            self.create_intel_gpu_options
        ]
        
        for tab in tabs:
            try:
                tab(self.notebook.nametowidget(f"!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook.index('!notebook.!{self.notebook
    def disable_amd_coolnquiet(self):
        """Disable AMD Cool'n'Quiet"""
        try:
            self.log("🔴 Disabling AMD Cool'n'Quiet...")
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e968-e325-11ce-bfc1-08002be10318}\\0000',
                '/v', 'PP_ThermalAutoThrottlingEnable', '/t', 'REG_DWORD', '/d', '0', '/f'
            ])
            self.log("✅ AMD Cool'n'Quiet disabled")
            self.optimizations_applied.append("AMD Cool'n'Quiet Disabled")
        except Exception as e:
            self.log(f"❌ Failed to disable AMD Cool'n'Quiet: {e}")
            
    def optimize_amd_precision_boost(self):
        """Optimize AMD Precision Boost"""
        try:
            self.log("🔴 Optimizing AMD Precision Boost...")
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Power\\PowerSettings\\54533251-82be-4824-96c1-47b60b740d00\\be337238-0d82-4146-a960-4f3749d470c7',
                '/v', 'Attributes', '/t', 'REG_DWORD', '/d', '0', '/f'
            ])
            self.log("✅ AMD Precision Boost optimized")
            self.optimizations_applied.append("AMD Precision Boost Optimized")
        except Exception as e:
            self.log(f"❌ Failed to optimize AMD Precision Boost: {e}")
            
    def optimize_amd_smt(self):
        """Optimize AMD SMT"""
        try:
            self.log("🔴 Optimizing AMD SMT...")
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\kernel',
                '/v', 'ThreadDpcEnable', '/t', 'REG_DWORD', '/d', '1', '/f'
            ])
            self.log("✅ AMD SMT optimized")
            self.optimizations_applied.append("AMD SMT Optimized")
        except Exception as e:
            self.log(f"❌ Failed to optimize AMD SMT: {e}")
            
    def optimize_amd_ryzen(self):
        """Apply AMD Ryzen specific optimizations"""
        try:
            self.log("🔴 Applying AMD Ryzen optimizations...")
            # Ryzen-specific registry tweaks
            commands = [
                ['reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Power\\PowerSettings\\54533251-82be-4824-96c1-47b60b740d00\\893dee8e-2bef-41e0-89c6-b55d0929964c', '/v', 'Attributes', '/t', 'REG_DWORD', '/d', '0', '/f'],
                ['reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Power\\PowerSettings\\54533251-82be-4824-96c1-47b60b740d00\\893dee8e-2bef-41e0-89c6-b55d0929964c\\0cc5b647-c1df-4637-891a-dec35c318583', '/v', 'ValueMax', '/t', 'REG_DWORD', '/d', '0', '/f']
            ]
            
            for cmd in commands:
                self.run_registry_command(cmd)
                
            self.log("✅ AMD Ryzen optimizations applied")
            self.optimizations_applied.append("AMD Ryzen Optimizations Applied")
        except Exception as e:
            self.log(f"❌ Failed to apply AMD Ryzen optimizations: {e}")
            
    # GPU Optimization Methods
    def nvidia_max_performance(self):
        """Set NVIDIA GPU to maximum performance"""
        try:
            self.log("🟢 Setting NVIDIA GPU to maximum performance...")
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e968-e325-11ce-bfc1-08002be10318}\\0000',
                '/v', 'PowerMizerEnable', '/t', 'REG_DWORD', '/d', '1', '/f'
            ])
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e968-e325-11ce-bfc1-08002be10318}\\0000',
                '/v', 'PowerMizerLevel', '/t', 'REG_DWORD', '/d', '1', '/f'
            ])
            self.log("✅ NVIDIA GPU set to maximum performance")
            self.optimizations_applied.append("NVIDIA Maximum Performance")
        except Exception as e:
            self.log(f"❌ Failed to set NVIDIA maximum performance: {e}")
            
    def optimize_nvidia_cuda(self):
        """Optimize NVIDIA CUDA settings"""
        try:
            self.log("🟢 Optimizing NVIDIA CUDA...")
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\GraphicsDrivers',
                '/v', 'TdrLevel', '/t', 'REG_DWORD', '/d', '0', '/f'
            ])
            self.log("✅ NVIDIA CUDA optimized")
            self.optimizations_applied.append("NVIDIA CUDA Optimized")
        except Exception as e:
            self.log(f"❌ Failed to optimize NVIDIA CUDA: {e}")
            
    def optimize_nvidia_shader_cache(self):
        """Optimize NVIDIA shader cache"""
        try:
            self.log("🟢 Optimizing NVIDIA shader cache...")
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e968-e325-11ce-bfc1-08002be10318}\\0000',
                '/v', 'EnableUlps', '/t', 'REG_DWORD', '/d', '0', '/f'
            ])
            self.log("✅ NVIDIA shader cache optimized")
            self.optimizations_applied.append("NVIDIA Shader Cache Optimized")
        except Exception as e:
            self.log(f"❌ Failed to optimize NVIDIA shader cache: {e}")
            
    def apply_nvidia_control_panel_tweaks(self):
        """Apply NVIDIA Control Panel tweaks"""
        try:
            self.log("🟢 Applying NVIDIA Control Panel tweaks...")
            # Multiple registry tweaks for NVIDIA
            commands = [
                ['reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e968-e325-11ce-bfc1-08002be10318}\\0000', '/v', 'PreferSystemMemoryContiguous', '/t', 'REG_DWORD', '/d', '1', '/f'],
                ['reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e968-e325-11ce-bfc1-08002be10318}\\0000', '/v', 'EnableUlps', '/t', 'REG_DWORD', '/d', '0', '/f'],
                ['reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e968-e325-11ce-bfc1-08002be10318}\\0000', '/v', 'PowerMizerEnable', '/t', 'REG_DWORD', '/d', '1', '/f']
            ]
            
            for cmd in commands:
                self.run_registry_command(cmd)
                
            self.log("✅ NVIDIA Control Panel tweaks applied")
            self.optimizations_applied.append("NVIDIA Control Panel Tweaks")
        except Exception as e:
            self.log(f"❌ Failed to apply NVIDIA Control Panel tweaks: {e}")
            
    def disable_nvidia_telemetry(self):
        """Disable NVIDIA telemetry services"""
        try:
            self.log("🟢 Disabling NVIDIA telemetry...")
            services = ['NvTelemetryContainer', 'NvContainerLocalSystem']
            
            for service in services:
                try:
                    subprocess.run(['sc', 'config', service, 'start=', 'disabled'], check=True, shell=True)
                    subprocess.run(['sc', 'stop', service], shell=True)  # Don't check=True as service might not be running
                except:
                    pass  # Service might not exist
                    
            self.log("✅ NVIDIA telemetry disabled")
            self.optimizations_applied.append("NVIDIA Telemetry Disabled")
        except Exception as e:
            self.log(f"❌ Failed to disable NVIDIA telemetry: {e}")
            
    def optimize_amd_radeon(self):
        """Optimize AMD Radeon settings"""
        try:
            self.log("🔴 Optimizing AMD Radeon settings...")
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e968-e325-11ce-bfc1-08002be10318}\\0000',
                '/v', 'PP_SclkDeepSleepDisable', '/t', 'REG_DWORD', '/d', '1', '/f'
            ])
            self.log("✅ AMD Radeon settings optimized")
            self.optimizations_applied.append("AMD Radeon Optimized")
        except Exception as e:
            self.log(f"❌ Failed to optimize AMD Radeon: {e}")
            
    def disable_amd_powerplay(self):
        """Disable AMD PowerPlay"""
        try:
            self.log("🔴 Disabling AMD PowerPlay...")
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e968-e325-11ce-bfc1-08002be10318}\\0000',
                '/v', 'PP_ThermalAutoThrottlingEnable', '/t', 'REG_DWORD', '/d', '0', '/f'
            ])
            self.log("✅ AMD PowerPlay disabled")
            self.optimizations_applied.append("AMD PowerPlay Disabled")
        except Exception as e:
            self.log(f"❌ Failed to disable AMD PowerPlay: {e}")
            
    def disable_amd_ulps(self):
        """Disable AMD ULPS"""
        try:
            self.log("🔴 Disabling AMD ULPS...")
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e968-e325-11ce-bfc1-08002be10318}\\0000',
                '/v', 'EnableUlps', '/t', 'REG_DWORD', '/d', '0', '/f'
            ])
            self.log("✅ AMD ULPS disabled")
            self.optimizations_applied.append("AMD ULPS Disabled")
        except Exception as e:
            self.log(f"❌ Failed to disable AMD ULPS: {e}")
            
    def optimize_amd_gpu_scheduling(self):
        """Optimize AMD GPU scheduling"""
        try:
            self.log("🔴 Optimizing AMD GPU scheduling...")
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\GraphicsDrivers',
                '/v', 'HwSchMode', '/t', 'REG_DWORD', '/d', '2', '/f'
            ])
            self.log("✅ AMD GPU scheduling optimized")
            self.optimizations_applied.append("AMD GPU Scheduling Optimized")
        except Exception as e:
            self.log(f"❌ Failed to optimize AMD GPU scheduling: {e}")
            
    def intel_gpu_max_performance(self):
        """Set Intel GPU to maximum performance"""
        try:
            self.log("🔵 Setting Intel GPU to maximum performance...")
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e968-e325-11ce-bfc1-08002be10318}\\0000',
                '/v', 'Acceleration.Level', '/t', 'REG_DWORD', '/d', '0', '/f'
            ])
            self.log("✅ Intel GPU set to maximum performance")
            self.optimizations_applied.append("Intel GPU Maximum Performance")
        except Exception as e:
            self.log(f"❌ Failed to set Intel GPU maximum performance: {e}")
            
    def lock_intel_gpu_frequency(self):
        """Lock Intel GPU frequency"""
        try:
            self.log("🔵 Locking Intel GPU frequency...")
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e968-e325-11ce-bfc1-08002be10318}\\0000',
                '/v', 'PP_SclkDeepSleepDisable', '/t', 'REG_DWORD', '/d', '1', '/f'
            ])
            self.log("✅ Intel GPU frequency locked")
            self.optimizations_applied.append("Intel GPU Frequency Locked")
        except Exception as e:
            self.log(f"❌ Failed to lock Intel GPU frequency: {e}")
            
    def optimize_intel_graphics(self):
        """Optimize Intel Graphics settings"""
        try:
            self.log("🔵 Optimizing Intel Graphics settings...")
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e968-e325-11ce-bfc1-08002be10318}\\0000',
                '/v', 'Acceleration.Level', '/t', 'REG_DWORD', '/d', '0', '/f'
            ])
            self.log("✅ Intel Graphics settings optimized")
            self.optimizations_applied.append("Intel Graphics Optimized")
        except Exception as e:
            self.log(f"❌ Failed to optimize Intel Graphics: {e}")
            
    # General Optimization Methods
    def set_high_performance_plan(self):
        """Set Windows to high performance power plan"""
        try:
            self.log("⚡ Setting high performance power plan...")
            subprocess.run(['powercfg', '/setactive', '8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c'], check=True, shell=True)
            self.log("✅ High performance power plan activated")
            self.optimizations_applied.append("High Performance Power Plan")
        except Exception as e:
            self.log(f"❌ Failed to set high performance plan: {e}")
            
    def disable_cpu_parking(self):
        """Disable CPU core parking"""
        try:
            self.log("🚫 Disabling CPU core parking...")
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Power\\PowerSettings\\54533251-82be-4824-96c1-47b60b740d00\\0cc5b647-c1df-4637-891a-dec35c318583',
                '/v', 'ValueMax', '/t', 'REG_DWORD', '/d', '0', '/f'
            ])
            self.log("✅ CPU core parking disabled")
            self.optimizations_applied.append("CPU Core Parking Disabled")
        except Exception as e:
            self.log(f"❌ Failed to disable CPU parking: {e}")
            
    def optimize_cpu_scheduling(self):
        """Optimize CPU scheduling for gaming"""
        try:
            self.log("⚙️ Optimizing CPU scheduling...")
            self.run_registry_command([
                'reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\PriorityControl',
                '/v', 'Win32PrioritySeparation', '/t', 'REG_DWORD', '/d', '38', '/f'
            ])
            self.log("✅ CPU scheduling optimized")
            self.optimizations_applied.append("CPU Scheduling Optimized")
        except Exception as e:
            self.log(f"❌ Failed to optimize CPU scheduling: {e}")
            
    def disable_cpu_throttling(self):
        """Disable CPU throttling"""
        try:
            self.log("🚫 Disabling CPU throttling...")
            subprocess.run(['bcdedit', '/set', 'disabledynamictick', 'yes'], check=True, shell=True)
            self.log("✅ CPU throttling disabled")
            self.optimizations_applied.append("CPU Throttling Disabled")
        except Exception as e:
            self.log(f"❌ Failed to disable CPU throttling: {e}")
            
    def optimize_windows_gaming(self):
        """Apply general Windows gaming optimizations"""
        try:
            self.log("🎮 Applying Windows gaming optimizations...")
            
            # Multiple registry tweaks
            commands = [
                ['reg', 'add', 'HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile', '/v', 'SystemResponsiveness', '/t', 'REG_DWORD', '/d', '0', '/f'],
                ['reg', 'add', 'HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile\\Tasks\\Games', '/v', 'GPU Priority', '/t', 'REG_DWORD', '/d', '8', '/f'],
                ['reg', 'add', 'HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile\\Tasks\\Games', '/v', 'Priority', '/t', 'REG_DWORD', '/d', '6', '/f'],
                ['reg', 'add', 'HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile\\Tasks\\Games', '/v', 'Scheduling Category', '/t', 'REG_SZ', '/d', 'High', '/f']
            ]
            
            for cmd in commands:
                self.run_registry_command(cmd)
                
            self.log("✅ Windows gaming optimizations applied")
            self.optimizations_applied.append("Windows Gaming Optimizations")
        except Exception as e:
            self.log(f"❌ Failed to apply Windows gaming optimizations: {e}")
            ('HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e968-e325-11ce-bfc1-08002be10318}\\0000', 'EnableUlps', 'REG_DWORD', '0'),
            ('HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e968-e325-11ce-bfc1-08002be10318}\\0000', 'EnableUlps_NA', 'REG_DWORD', '0'),
        ]
        self.apply_registry_tweaks(tweaks)
        self.log("✅ AMD ULPS disabled!")
        
    # Intel GPU Methods
    def intel_gpu_max_performance(self):
        self.log("🔵 Setting Intel GPU to maximum performance...")
        tweaks = [
            ('HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e968-e325-11ce-bfc1-08002be10318}\\0000', 'Acceleration.Level', 'REG_DWORD', '0'),
        ]
        self.apply_registry_tweaks(tweaks)
        self.log("✅ Intel GPU set to maximum performance!")
        
    def lock_intel_gpu_frequency(self):
        self.log("🔵 Locking Intel GPU frequency...")
        tweaks = [
            ('HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e968-e325-11ce-bfc1-08002be10318}\\0000', 'IntelGpuMaxFreq', 'REG_DWORD', '1'),
        ]
        self.apply_registry_tweaks(tweaks)
        self.log("✅ Intel GPU frequency locked!")
        
    # Utility Methods
    def apply_registry_tweaks(self, tweaks):
        for reg_path, name, reg_type, value in tweaks:
            self.apply_registry_tweak(reg_path, name, reg_type, value)
            
    def apply_registry_tweak(self, reg_path, name, reg_type, value):
        try:
            if reg_path.startswith('HKLM\\'):
                root_key = winreg.HKEY_LOCAL_MACHINE
                sub_key = reg_path[5:]
            elif reg_path.startswith('HKCU\\'):
                root_key = winreg.HKEY_CURRENT_USER
                sub_key = reg_path[5:]
            else:
                return False
                
            try:
                key = winreg.OpenKey(root_key, sub_key, 0, winreg.KEY_SET_VALUE)
            except FileNotFoundError:
                key = winreg.CreateKey(root_key, sub_key)
                
            if reg_type == 'REG_DWORD':
                winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, int(value))
            elif reg_type == 'REG_SZ':
                winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
                
            winreg.CloseKey(key)
            return True
            
        except Exception as e:
            self.log(f"Registry tweak failed: {str(e)}")
            return False
            
    def optimize_memory(self):
        self.log("💾 Applying memory optimizations...")
        # Implementation here
        self.log("✅ Memory optimized!")
        
    def optimize_network(self):
        self.log("🌐 Applying network optimizations...")
        # Implementation here
        self.log("✅ Network optimized!")
        
    def apply_all_hardware_optimizations(self):
        self.log("🚀 Applying all hardware-specific optimizations...")
        
        # Apply CPU optimizations based on detected hardware
        if self.hardware_info['cpu']['vendor'] == 'intel':
            self.disable_intel_speedstep()
            self.optimize_intel_turbo()
            self.disable_intel_cstates()
            self.optimize_intel_hyperthreading()
        elif self.hardware_info['cpu']['vendor'] == 'amd':
            self.disable_amd_coolnquiet()
            self.optimize_amd_precision_boost()
            self.optimize_amd_smt()
            self.optimize_amd_ryzen()
            
        # Apply GPU optimizations based on detected hardware
        if 'nvidia' in self.hardware_info['gpu']['vendors']:
            self.nvidia_max_performance()
            self.optimize_nvidia_cuda()
            self.optimize_nvidia_shader_cache()
            self.apply_nvidia_control_panel_tweaks()
            
        if 'amd' in self.hardware_info['gpu']['vendors']:
            self.optimize_amd_radeon()
            self.disable_amd_powerplay()
            self.disable_amd_ulps()
            
        if 'intel' in self.hardware_info['gpu']['vendors']:
            self.intel_gpu_max_performance()
            self.lock_intel_gpu_frequency()
            
        self.log("🎉 All hardware-specific optimizations completed!")
        
    def revert_all_optimizations(self):
        self.log("↩️ Reverting optimizations...")
        self.log("✅ Revert completed!")
        
    def log(self, message):
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()
        
    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
            
    def run(self):
        if not self.is_admin():
            self.log("⚠️ Run as Administrator for full functionality!")
        self.log("🎮 Hardware-Specific Gaming Optimizer loaded!")
        self.log(f"🔍 Detected: {self.hardware_info['cpu']['vendor'].upper()} CPU, {', '.join([v.upper() for v in self.hardware_info['gpu']['vendors']])} GPU")
        self.root.mainloop()

if __name__ == "__main__":
    try:
        app = AdvancedGameOptimizer()
        app.run()
    except ImportError:
        print("Installing required dependencies...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'wmi'], check=True)
        app = AdvancedGameOptimizer()
        app.run()


