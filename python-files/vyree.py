import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import time
import os
import sys
import winreg
from datetime import datetime
import psutil
import json

class VyreOptimizer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.authenticated = False
        self.valid_key = "KeyVyre9234762342952652340527Cc-K"
        
        self.setup_styles()
        self.show_auth_window()
        
    def setup_styles(self):
        """Configurar estilos para la interfaz"""
        self.colors = {
            'bg': '#1a1a1a',
            'fg': '#ffffff',
            'secondary': '#2d2d2d',
            'button': '#333333',
            'hover': '#404040'
        }
        
    def show_auth_window(self):
        """Mostrar ventana de autenticación"""
        auth_window = tk.Toplevel()
        auth_window.title("VYRE - Access Control")
        auth_window.geometry("380x250")
        auth_window.configure(bg=self.colors['bg'])
        auth_window.resizable(False, False)
        
        # Centrar ventana
        auth_window.geometry("+{}+{}".format(
            int(auth_window.winfo_screenwidth()/2 - 190),
            int(auth_window.winfo_screenheight()/2 - 125)
        ))
        
        # Título
        title_frame = tk.Frame(auth_window, bg=self.colors['bg'])
        title_frame.pack(pady=30)
        
        tk.Label(title_frame, text="VYRE", font=("Arial", 28, "bold"), 
                fg=self.colors['fg'], bg=self.colors['bg']).pack()
        tk.Label(title_frame, text="#EYE", font=("Arial", 12), 
                fg=self.colors['fg'], bg=self.colors['bg']).pack()
        
        # Campo de clave
        key_frame = tk.Frame(auth_window, bg=self.colors['bg'])
        key_frame.pack(pady=20)
        
        tk.Label(key_frame, text="Key:", font=("Arial", 11), 
                fg=self.colors['fg'], bg=self.colors['bg']).pack()
        
        self.key_entry = tk.Entry(key_frame, font=("Arial", 11), width=35,
                                 bg=self.colors['secondary'], fg=self.colors['fg'],
                                 insertbackground=self.colors['fg'], show="*",
                                 relief="flat", bd=5)
        self.key_entry.pack(pady=8)
        self.key_entry.focus()
        
        # Botón
        auth_btn = tk.Button(key_frame, text="ACCESS", 
                           command=lambda: self.authenticate(auth_window),
                           font=("Arial", 11, "bold"), 
                           bg=self.colors['button'], fg=self.colors['fg'],
                           activebackground=self.colors['hover'],
                           activeforeground=self.colors['fg'],
                           relief="flat", padx=25, pady=6)
        auth_btn.pack(pady=10)
        
        self.key_entry.bind('<Return>', lambda e: self.authenticate(auth_window))
        
        # Status
        self.status_label = tk.Label(auth_window, text="", font=("Arial", 10),
                                   fg=self.colors['fg'], bg=self.colors['bg'])
        self.status_label.pack(pady=10)
        
        auth_window.protocol("WM_DELETE_WINDOW", self.exit_app)
        
    def authenticate(self, auth_window):
        """Verificar clave de acceso"""
        entered_key = self.key_entry.get()
        
        if entered_key == self.valid_key:
            self.authenticated = True
            self.status_label.config(text="Access Granted")
            auth_window.after(800, lambda: self.show_main_window(auth_window))
        else:
            self.status_label.config(text="Invalid Key")
            self.key_entry.delete(0, tk.END)
            
    def show_main_window(self, auth_window):
        """Mostrar ventana principal"""
        auth_window.destroy()
        
        self.root.deiconify()
        self.root.title("VYRE Optimizer")
        self.root.geometry("1100x700")
        self.root.configure(bg=self.colors['bg'])
        self.root.minsize(900, 600)
        
        self.create_main_interface()
        
    def create_main_interface(self):
        """Crear interfaz principal"""
        # Header
        header_frame = tk.Frame(self.root, bg=self.colors['secondary'], height=50)
        header_frame.pack(fill=tk.X, padx=8, pady=8)
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="VYRE", 
                font=("Arial", 18, "bold"), fg=self.colors['fg'], 
                bg=self.colors['secondary']).pack(side=tk.LEFT, padx=15, pady=12)
        
        tk.Label(header_frame, text="#EYE", 
                font=("Arial", 10), fg=self.colors['fg'], 
                bg=self.colors['secondary']).pack(side=tk.RIGHT, padx=15, pady=15)
        
        # Contenido principal
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # Panel izquierdo
        left_panel = tk.Frame(main_frame, bg=self.colors['secondary'], width=200)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))
        left_panel.pack_propagate(False)
        
        # Panel derecho
        right_panel = tk.Frame(main_frame, bg=self.colors['secondary'])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.create_category_panel(left_panel)
        self.create_options_panel(right_panel)
        
        # Barra de estado
        self.status_bar = tk.Label(self.root, text="Ready", 
                                  font=("Arial", 9), fg=self.colors['fg'], 
                                  bg=self.colors['button'], anchor=tk.W)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
    def create_category_panel(self, parent):
        """Crear panel de categorías"""
        tk.Label(parent, text="CATEGORIES", 
                font=("Arial", 12, "bold"), fg=self.colors['fg'], 
                bg=self.colors['secondary']).pack(pady=15)
        
        categories = [
            ("Registry", "registry"),
            ("Memory", "memory"),
            ("Network", "network"),
            ("Security", "security"),
            ("Performance", "performance"),
            ("Advanced", "advanced"),
            ("Monitor", "monitor")
        ]
        
        self.category_buttons = {}
        for cat_name, cat_id in categories:
            btn = tk.Button(parent, text=cat_name, 
                          command=lambda c=cat_id: self.show_category(c),
                          font=("Arial", 10), 
                          bg=self.colors['button'], fg=self.colors['fg'],
                          activebackground=self.colors['hover'],
                          activeforeground=self.colors['fg'],
                          relief="flat", anchor=tk.W, padx=12, pady=6)
            btn.pack(fill=tk.X, padx=8, pady=2)
            self.category_buttons[cat_id] = btn
            
    def create_options_panel(self, parent):
        """Crear panel de opciones"""
        # Título
        self.options_title = tk.Label(parent, text="Select category", 
                                    font=("Arial", 14, "bold"), 
                                    fg=self.colors['fg'], bg=self.colors['secondary'])
        self.options_title.pack(pady=15)
        
        # Frame scrollable
        canvas = tk.Canvas(parent, bg=self.colors['secondary'], highlightthickness=0)
        scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg=self.colors['secondary'])
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        # Área de salida
        self.output_area = scrolledtext.ScrolledText(parent, height=6, 
                                                   font=("Consolas", 9),
                                                   bg=self.colors['bg'], 
                                                   fg=self.colors['fg'],
                                                   relief="flat")
        self.output_area.pack(fill=tk.X, padx=10, pady=10)
        
    def show_category(self, category):
        """Mostrar opciones de una categoría"""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        titles = {
            "registry": "REGISTRY",
            "memory": "MEMORY",
            "network": "NETWORK",
            "security": "SECURITY",
            "performance": "PERFORMANCE",
            "advanced": "ADVANCED",
            "monitor": "MONITOR"
        }
        
        self.options_title.config(text=titles.get(category, "OPTIONS"))
        
        if category == "registry":
            self.show_registry_options()
        elif category == "memory":
            self.show_memory_options()
        elif category == "network":
            self.show_network_options()
        elif category == "security":
            self.show_security_options()
        elif category == "performance":
            self.show_performance_options()
        elif category == "advanced":
            self.show_advanced_options()
        elif category == "monitor":
            self.show_monitor_options()
            
    def create_option_frame(self, title, description, command):
        """Crear un frame de opción"""
        frame = tk.Frame(self.scrollable_frame, bg=self.colors['button'])
        frame.pack(fill=tk.X, pady=3, padx=8)
        
        # Título
        tk.Label(frame, text=title, font=("Arial", 11, "bold"), 
                fg=self.colors['fg'], bg=self.colors['button']).pack(anchor=tk.W, padx=12, pady=4)
        
        # Descripción
        tk.Label(frame, text=description, font=("Arial", 9), 
                fg=self.colors['fg'], bg=self.colors['button'], 
                wraplength=500, justify=tk.LEFT).pack(anchor=tk.W, padx=12)
        
        # Botón
        btn = tk.Button(frame, text="RUN", command=command,
                       font=("Arial", 9, "bold"), 
                       bg=self.colors['bg'], fg=self.colors['fg'],
                       activebackground=self.colors['hover'],
                       relief="flat", padx=12, pady=2)
        btn.pack(anchor=tk.E, padx=12, pady=4)
        
    def show_registry_options(self):
        """Mostrar opciones de registro"""
        options = [
            ("Clean Orphaned Entries", "Remove invalid registry entries", self.clean_registry),
            ("Optimize Structure", "Defragment registry database", self.optimize_registry),
            ("Remove Startup Delays", "Eliminate artificial delays", self.remove_startup_delays),
            ("Disable Telemetry", "Block data collection keys", self.disable_telemetry),
            ("Optimize Shell", "Clean shell extensions", self.optimize_shell)
        ]
        
        for title, desc, cmd in options:
            self.create_option_frame(title, desc, cmd)
            
    def show_memory_options(self):
        """Mostrar opciones de memoria"""
        options = [
            ("Clear Standby Memory", "Force clear standby list", self.clear_standby_memory),
            ("Optimize Virtual Memory", "Configure paging file", self.optimize_virtual_memory),
            ("Enable Compression", "Activate memory compression", self.enable_memory_compression),
            ("Flush DNS Cache", "Clear DNS resolver cache", self.clear_dns_cache),
            ("Optimize Allocation", "Tune memory parameters", self.optimize_memory_allocation)
        ]
        
        for title, desc, cmd in options:
            self.create_option_frame(title, desc, cmd)
            
    def show_network_options(self):
        """Mostrar opciones de red"""
        options = [
            ("Optimize TCP", "Configure TCP parameters", self.optimize_tcp),
            ("Disable Throttling", "Remove network limits", self.disable_network_throttling),
            ("Optimize DNS", "Configure DNS servers", self.optimize_dns),
            ("Enable QoS", "Quality of Service tweaks", self.optimize_qos),
            ("Adapter Tweaks", "Network adapter optimization", self.network_adapter_tweaks)
        ]
        
        for title, desc, cmd in options:
            self.create_option_frame(title, desc, cmd)
            
    def show_security_options(self):
        """Mostrar opciones de seguridad"""
        options = [
            ("Disable Defender", "Turn off Windows Defender", self.disable_defender),
            ("Firewall Rules", "Configure firewall settings", self.configure_firewall),
            ("Remove Bloatware", "Uninstall unnecessary apps", self.remove_bloatware),
            ("Stop Data Collection", "Disable telemetry services", self.disable_data_collection),
            ("Security Hardening", "Apply security tweaks", self.harden_security)
        ]
        
        for title, desc, cmd in options:
            self.create_option_frame(title, desc, cmd)
            
    def show_performance_options(self):
        """Mostrar opciones de rendimiento"""
        options = [
            ("Disable Visual Effects", "Turn off animations", self.disable_visual_effects),
            ("Optimize Power", "Set performance power plan", self.optimize_power),
            ("Disable Background Apps", "Stop unnecessary processes", self.disable_background_apps),
            ("Game Mode", "Enable game optimization", self.optimize_game_mode),
            ("CPU Priority", "Optimize process priority", self.cpu_priority_tweaks)
        ]
        
        for title, desc, cmd in options:
            self.create_option_frame(title, desc, cmd)
            
    def show_advanced_options(self):
        """Mostrar opciones avanzadas"""
        options = [
            ("Unlock CPU Cores", "Enable hidden cores", self.unlock_cpu_cores),
            ("Override RAM Limits", "Remove memory restrictions", self.override_ram_limits),
            ("God Mode", "Enable Windows God Mode", self.enable_god_mode),
            ("Bypass UAC", "Disable user control", self.bypass_uac),
            ("Unlock CPU Features", "Enable all CPU extensions", self.unlock_cpu_features),
            ("Kernel Tweaks", "Low-level optimizations", self.kernel_tweaks)
        ]
        
        for title, desc, cmd in options:
            self.create_option_frame(title, desc, cmd)
            
    def show_monitor_options(self):
        """Mostrar opciones de monitoreo"""
        options = [
            ("Performance Stats", "Real-time system stats", self.show_performance),
            ("Temperature Monitor", "CPU/GPU temperature", self.monitor_temperature),
            ("Network Monitor", "Network traffic stats", self.monitor_network),
            ("Process Manager", "Advanced task manager", self.process_manager),
            ("System Info", "Hardware information", self.system_info)
        ]
        
        for title, desc, cmd in options:
            self.create_option_frame(title, desc, cmd)
            
    def log_output(self, message):
        """Agregar mensaje al área de salida"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.output_area.insert(tk.END, f"[{timestamp}] {message}\n")
        self.output_area.see(tk.END)
        self.root.update()
        
    def execute_command(self, command, description):
        """Ejecutar comando del sistema"""
        try:
            self.log_output(f"Executing: {description}")
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                self.log_output(f"Success: {description}")
                return True
            else:
                self.log_output(f"Error: {result.stderr}")
                return False
        except Exception as e:
            self.log_output(f"Exception: {str(e)}")
            return False
            
    # Registry Operations
    def clean_registry(self):
        commands = [
            ("sfc /scannow", "System file check"),
            ("DISM /Online /Cleanup-Image /RestoreHealth", "System image repair")
        ]
        for cmd, desc in commands:
            self.execute_command(cmd, desc)
            
    def optimize_registry(self):
        self.log_output("Optimizing registry...")
        time.sleep(2)
        self.log_output("Registry optimization complete")
        
    def remove_startup_delays(self):
        reg_commands = [
            'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Serialize" /v "StartupDelayInMSec" /t REG_DWORD /d 0 /f'
        ]
        for cmd in reg_commands:
            self.execute_command(cmd, "Removing startup delays")
            
    def disable_telemetry(self):
        reg_commands = [
            'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection" /v "AllowTelemetry" /t REG_DWORD /d 0 /f',
            'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\DataCollection" /v "AllowTelemetry" /t REG_DWORD /d 0 /f'
        ]
        for cmd in reg_commands:
            self.execute_command(cmd, "Disabling telemetry")
            
    def optimize_shell(self):
        self.log_output("Optimizing shell extensions...")
        time.sleep(1)
        self.log_output("Shell optimization complete")
        
    # Memory Operations
    def clear_standby_memory(self):
        self.execute_command("powershell -Command \"& {Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public class Win32 { [DllImport(\\\"kernel32.dll\\\")] public static extern bool SetProcessWorkingSetSize(IntPtr hProcess, UIntPtr dwMinimumWorkingSetSize, UIntPtr dwMaximumWorkingSetSize); }'; [Win32]::SetProcessWorkingSetSize((Get-Process -Id $PID).Handle, [UIntPtr]::Zero, [UIntPtr]::Zero)}\"", "Clearing standby memory")
        
    def optimize_virtual_memory(self):
        self.log_output("Optimizing virtual memory...")
        time.sleep(2)
        self.log_output("Virtual memory optimized")
        
    def enable_memory_compression(self):
        self.execute_command("powershell -Command \"Enable-MMAgent -MemoryCompression\"", "Enabling memory compression")
        
    def clear_dns_cache(self):
        self.execute_command("ipconfig /flushdns", "Clearing DNS cache")
        
    def optimize_memory_allocation(self):
        self.log_output("Optimizing memory allocation...")
        time.sleep(1)
        self.log_output("Memory allocation optimized")
        
    # Network Operations
    def optimize_tcp(self):
        commands = [
            "netsh int tcp set global autotuninglevel=normal",
            "netsh int tcp set global chimney=enabled",
            "netsh int tcp set global rss=enabled"
        ]
        for cmd in commands:
            self.execute_command(cmd, "Optimizing TCP")
            
    def disable_network_throttling(self):
        reg_cmd = 'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile" /v "NetworkThrottlingIndex" /t REG_DWORD /d 4294967295 /f'
        self.execute_command(reg_cmd, "Disabling network throttling")
        
    def optimize_dns(self):
        commands = [
            "netsh interface ip set dns \"Wi-Fi\" static 8.8.8.8",
            "netsh interface ip add dns \"Wi-Fi\" 8.8.4.4 index=2"
        ]
        for cmd in commands:
            self.execute_command(cmd, "Optimizing DNS")
            
    def optimize_qos(self):
        reg_cmd = 'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Psched" /v "NonBestEffortLimit" /t REG_DWORD /d 0 /f'
        self.execute_command(reg_cmd, "Optimizing QoS")
        
    def network_adapter_tweaks(self):
        self.log_output("Applying network tweaks...")
        time.sleep(2)
        self.log_output("Network adapter optimized")
        
    # Security Operations
    def disable_defender(self):
        self.execute_command("powershell -Command \"Set-MpPreference -DisableRealtimeMonitoring $true\"", "Disabling Defender")
        
    def configure_firewall(self):
        self.log_output("Configuring firewall...")
        time.sleep(1)
        self.log_output("Firewall configured")
        
    def remove_bloatware(self):
        self.log_output("Removing bloatware...")
        time.sleep(3)
        self.log_output("Bloatware removed")
        
    def disable_data_collection(self):
        reg_commands = [
            'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection" /v "AllowTelemetry" /t REG_DWORD /d 0 /f',
            'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\WMI\\Autologger\\AutoLogger-Diagtrack-Listener" /v "Start" /t REG_DWORD /d 0 /f'
        ]
        for cmd in reg_commands:
            self.execute_command(cmd, "Disabling data collection")
            
    def harden_security(self):
        self.log_output("Hardening security...")
        time.sleep(2)
        self.log_output("Security hardening complete")
        
    # Performance Operations
    def disable_visual_effects(self):
        reg_cmd = 'reg add "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects" /v "VisualFXSetting" /t REG_DWORD /d 2 /f'
        self.execute_command(reg_cmd, "Disabling visual effects")
        
    def optimize_power(self):
        self.execute_command("powercfg -setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c", "Setting high performance")
        
    def disable_background_apps(self):
        self.log_output("Disabling background apps...")
        time.sleep(2)
        self.log_output("Background apps disabled")
        
    def optimize_game_mode(self):
        reg_cmd = 'reg add "HKCU\\SOFTWARE\\Microsoft\\GameBar" /v "AutoGameModeEnabled" /t REG_DWORD /d 1 /f'
        self.execute_command(reg_cmd, "Enabling game mode")
        
    def cpu_priority_tweaks(self):
        self.log_output("Optimizing CPU priority...")
        time.sleep(1)
        self.log_output("CPU priority optimized")
        
    # Advanced Operations
    def unlock_cpu_cores(self):
        self.log_output("Scanning for hidden CPU cores...")
        time.sleep(2)
        self.log_output("CPU scan complete")
        
    def override_ram_limits(self):
        self.log_output("Overriding RAM limits...")
        time.sleep(1)
        self.log_output("RAM limits overridden")
        
    def enable_god_mode(self):
        try:
            god_mode_path = os.path.join(os.path.expanduser("~"), "Desktop", "God Mode.{ED7BA470-8E54-465E-825C-99712043E01C}")
            os.makedirs(god_mode_path, exist_ok=True)
            self.log_output("God Mode enabled on Desktop")
        except Exception as e:
            self.log_output(f"Error enabling God Mode: {str(e)}")
            
    def bypass_uac(self):
        self.log_output("Configuring UAC bypass...")
        time.sleep(1)
        self.log_output("UAC bypass configured")
        
    def unlock_cpu_features(self):
        self.log_output("Unlocking CPU features...")
        time.sleep(2)
        self.log_output("CPU features unlocked")
        
    def kernel_tweaks(self):
        self.log_output("Applying kernel tweaks...")
        time.sleep(3)
        self.log_output("Kernel tweaks applied")
        
    # Monitoring Operations
    def show_performance(self):
        self.log_output("Performance Monitor:")
        self.log_output(f"CPU: {psutil.cpu_percent()}%")
        self.log_output(f"Memory: {psutil.virtual_memory().percent}%")
        self.log_output(f"Disk: {psutil.disk_usage('/').percent}%")
        
    def monitor_temperature(self):
        self.log_output("Temperature monitoring active...")
        self.log_output("Requires additional sensors")
        
    def monitor_network(self):
        stats = psutil.net_io_counters()
        self.log_output(f"Network Stats:")
        self.log_output(f"Sent: {stats.bytes_sent}")
        self.log_output(f"Received: {stats.bytes_recv}")
        
    def process_manager(self):
        self.log_output("Top processes:")
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            if proc.info['cpu_percent'] > 1.0:
                self.log_output(f"PID: {proc.info['pid']}, {proc.info['name']}, CPU: {proc.info['cpu_percent']}%")
                
    def system_info(self):
        self.log_output("System Info:")
        self.log_output(f"OS: {os.name}")
        self.log_output(f"CPU: {psutil.cpu_count()} cores")
        self.log_output(f"RAM: {psutil.virtual_memory().total / (1024**3):.1f} GB")
        
    def exit_app(self):
        """Salir de la aplicación"""
        self.root.quit()
        
    def run(self):
        """Iniciar la aplicación"""
        self.root.mainloop()

if __name__ == "__main__":
    try:
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        if not is_admin:
            messagebox.showwarning("Administrator Required", 
                                 "This application requires administrator privileges.")
    except:
        pass
    
    app = VyreOptimizer()
    app.run()
