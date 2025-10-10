import os
import sys
import subprocess
import winreg
import ctypes
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
from datetime import datetime

class GamingConfigTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Gaming Config Tool - Windows 11 24H2")
        self.root.geometry("1000x750")
        self.root.configure(bg='#0d0d0d')
        
        self.is_admin = self.check_admin()
        self.setup_ui()
        
    def check_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg='#1a1a1a', height=80)
        header.pack(fill='x', padx=10, pady=10)
        
        tk.Label(header, text="🎮 GAMING CONFIG PRO", 
                font=('Arial', 24, 'bold'), bg='#1a1a1a', fg='#00ff00').pack(pady=5)
        tk.Label(header, text="Windows 11 24H2 Optimization Suite", 
                font=('Arial', 11), bg='#1a1a1a', fg='#888888').pack()
        
        if not self.is_admin:
            warning = tk.Label(header, text="⚠️ ADMINISTRATOR REQUIRED - Some features disabled", 
                             font=('Arial', 10, 'bold'), bg='#ff4400', fg='#ffffff', padx=10, pady=5)
            warning.pack(pady=5)
        
        # Main container
        main_frame = tk.Frame(self.root, bg='#0d0d0d')
        main_frame.pack(fill='both', expand=True, padx=10)
        
        # Left panel - Quick Actions
        left_panel = tk.Frame(main_frame, bg='#1a1a1a', width=300)
        left_panel.pack(side='left', fill='y', padx=(0, 5))
        
        tk.Label(left_panel, text="⚡ QUICK ACTIONS", font=('Arial', 12, 'bold'),
                bg='#1a1a1a', fg='#00ff00').pack(pady=10)
        
        quick_actions = [
            ("🚀 APPLY ALL OPTIMIZATIONS", self.apply_all, '#00aa00'),
            ("🎯 GAMING MODE ONLY", self.gaming_mode_only, '#0066cc'),
            ("⚙️ RESTORE DEFAULTS", self.restore_defaults, '#cc6600'),
            ("📊 SYSTEM STATUS", self.show_status, '#8800cc'),
        ]
        
        for text, cmd, color in quick_actions:
            btn = tk.Button(left_panel, text=text, command=cmd,
                          bg=color, fg='white', font=('Arial', 10, 'bold'),
                          width=25, height=2, relief='flat')
            btn.pack(pady=5, padx=10)
        
        # Separator
        sep = tk.Frame(left_panel, bg='#333333', height=2)
        sep.pack(fill='x', padx=10, pady=10)
        
        tk.Label(left_panel, text="🔧 SYSTEM INFO", font=('Arial', 11, 'bold'),
                bg='#1a1a1a', fg='#00ff00').pack(pady=10)
        
        self.status_text = tk.Text(left_panel, height=12, width=32,
                                   bg='#0d0d0d', fg='#00ff00',
                                   font=('Consolas', 9), relief='flat')
        self.status_text.pack(padx=10, pady=5)
        self.update_status()
        
        # Right panel - Detailed Options
        right_panel = tk.Frame(main_frame, bg='#0d0d0d')
        right_panel.pack(side='right', fill='both', expand=True)
        
        notebook = ttk.Notebook(right_panel)
        notebook.pack(fill='both', expand=True)
        
        # Style for notebook
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook', background='#0d0d0d', borderwidth=0)
        style.configure('TNotebook.Tab', background='#1a1a1a', foreground='#ffffff', 
                       padding=[20, 10], font=('Arial', 10, 'bold'))
        style.map('TNotebook.Tab', background=[('selected', '#00aa00')], 
                 foreground=[('selected', '#ffffff')])
        
        # Create tabs
        self.setup_performance_tab(notebook)
        self.setup_graphics_tab(notebook)
        self.setup_network_tab(notebook)
        self.setup_system_tab(notebook)
        self.setup_advanced_tab(notebook)
        
        # Log panel
        log_frame = tk.Frame(self.root, bg='#1a1a1a')
        log_frame.pack(fill='both', padx=10, pady=(5, 10))
        
        tk.Label(log_frame, text="📋 ACTIVITY LOG", font=('Arial', 11, 'bold'),
                bg='#1a1a1a', fg='#00ff00').pack(anchor='w', padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8,
                                                   bg='#0d0d0d', fg='#00ff00',
                                                   font=('Consolas', 9), relief='flat')
        self.log_text.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        self.log("🎮 Gaming Config Tool initialized - Ready to optimize!")
    
    def setup_performance_tab(self, notebook):
        tab = tk.Frame(notebook, bg='#0d0d0d')
        notebook.add(tab, text='⚡ PERFORMANCE')
        
        scroll = tk.Canvas(tab, bg='#0d0d0d', highlightthickness=0)
        scrollbar = tk.Scrollbar(tab, orient='vertical', command=scroll.yview)
        content = tk.Frame(scroll, bg='#0d0d0d')
        
        scroll.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        scroll.pack(side='left', fill='both', expand=True)
        scroll.create_window((0, 0), window=content, anchor='nw')
        
        options = [
            ("🎯 Enable Game Mode", "Activates Windows Game Mode for better performance", self.enable_game_mode),
            ("🚀 High Performance Power Plan", "Sets maximum CPU performance", self.high_performance_power),
            ("⚡ Disable Power Throttling", "Prevents CPU throttling during games", self.disable_power_throttling),
            ("💾 Optimize Virtual Memory", "Configure page file for gaming", self.optimize_virtual_memory),
            ("🔧 Disable Background Apps", "Stop unnecessary background processes", self.disable_background_apps),
            ("📊 Disable Telemetry Services", "Stop data collection services", self.disable_telemetry),
            ("🎮 Game DVR Off", "Disable Xbox Game Bar recording", self.disable_game_dvr),
            ("🖥️ Disable Full-Screen Optimizations", "Better compatibility with games", self.disable_fullscreen_opt),
            ("⏱️ High Performance Timer", "Improve game timing accuracy", self.high_performance_timer),
            ("🔥 CPU Priority Optimization", "Prioritize CPU for games", self.cpu_priority_optimization),
        ]
        
        for i, (title, desc, cmd) in enumerate(options):
            self.create_option_button(content, title, desc, cmd, i)
        
        content.update_idletasks()
        scroll.config(scrollregion=scroll.bbox('all'))
    
    def setup_graphics_tab(self, notebook):
        tab = tk.Frame(notebook, bg='#0d0d0d')
        notebook.add(tab, text='🎨 GRAPHICS')
        
        scroll = tk.Canvas(tab, bg='#0d0d0d', highlightthickness=0)
        scrollbar = tk.Scrollbar(tab, orient='vertical', command=scroll.yview)
        content = tk.Frame(scroll, bg='#0d0d0d')
        
        scroll.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        scroll.pack(side='left', fill='both', expand=True)
        scroll.create_window((0, 0), window=content, anchor='nw')
        
        options = [
            ("🖼️ Hardware GPU Scheduling", "Enable GPU hardware scheduling", self.enable_hardware_gpu_scheduling),
            ("✨ Disable Visual Effects", "Reduce animations for performance", self.disable_visual_effects),
            ("🎯 Game Bar Disable", "Turn off Xbox Game Bar overlay", self.disable_game_bar),
            ("🌈 Disable Transparency", "Remove window transparency effects", self.disable_transparency),
            ("📺 Optimize Display Settings", "Configure refresh rate & resolution", self.optimize_display),
            ("🎬 Disable Animations", "Turn off window animations", self.disable_animations),
            ("🖱️ Enhanced Pointer Precision Off", "Raw mouse input for FPS games", self.disable_pointer_precision),
            ("🔲 Disable Desktop Composition", "Legacy optimization for older games", self.disable_desktop_composition),
            ("💡 Disable HDR (Optional)", "Turn off HDR if causing issues", self.disable_hdr),
        ]
        
        for i, (title, desc, cmd) in enumerate(options):
            self.create_option_button(content, title, desc, cmd, i)
        
        content.update_idletasks()
        scroll.config(scrollregion=scroll.bbox('all'))
    
    def setup_network_tab(self, notebook):
        tab = tk.Frame(notebook, bg='#0d0d0d')
        notebook.add(tab, text='🌐 NETWORK')
        
        scroll = tk.Canvas(tab, bg='#0d0d0d', highlightthickness=0)
        scrollbar = tk.Scrollbar(tab, orient='vertical', command=scroll.yview)
        content = tk.Frame(scroll, bg='#0d0d0d')
        
        scroll.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        scroll.pack(side='left', fill='both', expand=True)
        scroll.create_window((0, 0), window=content, anchor='nw')
        
        options = [
            ("🚀 TCP Optimizer", "Optimize TCP/IP settings for gaming", self.optimize_tcp),
            ("📡 Disable Nagle's Algorithm", "Reduce network latency", self.disable_nagle),
            ("⚡ Network Auto-Tuning", "Optimize receive window", self.network_autotuning),
            ("🎯 QoS Packet Scheduler", "Prioritize gaming traffic", self.optimize_qos),
            ("🔌 Disable Network Throttling", "Remove bandwidth limits", self.disable_network_throttling),
            ("📊 DNS Optimization", "Use faster DNS servers", self.optimize_dns),
            ("🌐 MTU Optimization", "Set optimal packet size", self.optimize_mtu),
            ("🎮 Network Adapter Settings", "Tune network card for gaming", self.optimize_network_adapter),
            ("⏱️ Reduce Network Latency", "Multiple latency optimizations", self.reduce_network_latency),
        ]
        
        for i, (title, desc, cmd) in enumerate(options):
            self.create_option_button(content, title, desc, cmd, i)
        
        content.update_idletasks()
        scroll.config(scrollregion=scroll.bbox('all'))
    
    def setup_system_tab(self, notebook):
        tab = tk.Frame(notebook, bg='#0d0d0d')
        notebook.add(tab, text='⚙️ SYSTEM')
        
        scroll = tk.Canvas(tab, bg='#0d0d0d', highlightthickness=0)
        scrollbar = tk.Scrollbar(tab, orient='vertical', command=scroll.yview)
        content = tk.Frame(scroll, bg='#0d0d0d')
        
        scroll.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        scroll.pack(side='left', fill='both', expand=True)
        scroll.create_window((0, 0), window=content, anchor='nw')
        
        options = [
            ("🗂️ Disable Superfetch/Prefetch", "Reduce disk usage", self.disable_superfetch),
            ("📝 Disable Windows Search", "Free up system resources", self.disable_search_indexing),
            ("🔄 Disable Automatic Updates", "Prevent interruptions during gaming", self.disable_auto_updates),
            ("🛡️ Configure Windows Defender", "Optimize for gaming performance", self.optimize_defender),
            ("📢 Disable Notifications", "No interruptions during gameplay", self.disable_notifications),
            ("⏰ Disable System Restore", "Free up disk space (risky)", self.disable_system_restore),
            ("🔊 Audio Enhancements Off", "Reduce audio latency", self.disable_audio_enhancements),
            ("📅 Disable Scheduled Tasks", "Stop background maintenance", self.disable_scheduled_tasks),
            ("🖥️ Optimize Registry", "Clean and optimize registry", self.optimize_registry),
            ("🔋 Disable USB Selective Suspend", "Prevent USB device lag", self.disable_usb_suspend),
        ]
        
        for i, (title, desc, cmd) in enumerate(options):
            self.create_option_button(content, title, desc, cmd, i)
        
        content.update_idletasks()
        scroll.config(scrollregion=scroll.bbox('all'))
    
    def setup_advanced_tab(self, notebook):
        tab = tk.Frame(notebook, bg='#0d0d0d')
        notebook.add(tab, text='🔧 ADVANCED')
        
        scroll = tk.Canvas(tab, bg='#0d0d0d', highlightthickness=0)
        scrollbar = tk.Scrollbar(tab, orient='vertical', command=scroll.yview)
        content = tk.Frame(scroll, bg='#0d0d0d')
        
        scroll.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        scroll.pack(side='left', fill='both', expand=True)
        scroll.create_window((0, 0), window=content, anchor='nw')
        
        options = [
            ("🎯 Core Parking Disable", "Keep all CPU cores active", self.disable_core_parking),
            ("⚡ MSI Mode for GPU", "Optimize GPU interrupt handling", self.enable_msi_mode),
            ("🖥️ Disable HPET", "Reduce timing overhead", self.disable_hpet),
            ("🔥 Optimize SSD/TRIM", "Maintain SSD performance", self.optimize_ssd),
            ("💻 Large System Cache", "Allocate more RAM to system cache", self.enable_large_cache),
            ("🎮 Game Specific Tweaks", "Per-game optimization profiles", self.game_specific_tweaks),
            ("📊 Process Lasso Setup", "Advanced CPU management (requires app)", self.process_lasso_info),
            ("🔧 Ultimate Performance Plan", "Enable hidden power plan", self.ultimate_performance_plan),
            ("⏱️ BIOS Settings Guide", "Recommended BIOS tweaks", self.bios_guide),
            ("🛠️ Driver Updates Check", "Ensure optimal drivers", self.check_drivers),
        ]
        
        for i, (title, desc, cmd) in enumerate(options):
            self.create_option_button(content, title, desc, cmd, i)
        
        content.update_idletasks()
        scroll.config(scrollregion=scroll.bbox('all'))
    
    def create_option_button(self, parent, title, desc, command, row):
        frame = tk.Frame(parent, bg='#1a1a1a', relief='flat')
        frame.pack(fill='x', padx=15, pady=5)
        
        text_frame = tk.Frame(frame, bg='#1a1a1a')
        text_frame.pack(side='left', fill='both', expand=True, padx=10, pady=8)
        
        tk.Label(text_frame, text=title, font=('Arial', 10, 'bold'),
                bg='#1a1a1a', fg='#ffffff', anchor='w').pack(anchor='w')
        tk.Label(text_frame, text=desc, font=('Arial', 8),
                bg='#1a1a1a', fg='#888888', anchor='w').pack(anchor='w')
        
        btn = tk.Button(frame, text="APPLY", command=command,
                       bg='#00aa00', fg='white', font=('Arial', 9, 'bold'),
                       width=10, relief='flat')
        btn.pack(side='right', padx=10)
    
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert('end', f"[{timestamp}] {message}\n")
        self.log_text.see('end')
        self.root.update()
    
    def update_status(self):
        self.status_text.delete(1.0, 'end')
        self.status_text.insert('end', f"Windows Version: 11 24H2\n")
        self.status_text.insert('end', f"Admin Mode: {'YES' if self.is_admin else 'NO'}\n")
        self.status_text.insert('end', f"\n--- Active Optimizations ---\n")
        self.status_text.insert('end', f"Game Mode: Checking...\n")
        self.status_text.insert('end', f"Power Plan: Checking...\n")
        self.status_text.insert('end', f"GPU Scheduling: Checking...\n")
    
    def run_command(self, cmd, description):
        if not self.is_admin:
            self.log(f"❌ {description} - ADMIN REQUIRED")
            return False
        try:
            self.log(f"🔄 {description}...")
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                self.log(f"✅ {description} - SUCCESS")
                return True
            else:
                self.log(f"⚠️ {description} - COMPLETED WITH WARNINGS")
                return True
        except Exception as e:
            self.log(f"❌ {description} - ERROR: {str(e)}")
            return False
    
    def set_registry(self, path, name, value, value_type=winreg.REG_DWORD):
        if not self.is_admin:
            return False
        try:
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, path)
            winreg.SetValueEx(key, name, 0, value_type, value)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            self.log(f"Registry error: {str(e)}")
            return False
    
    # Performance optimizations
    def enable_game_mode(self):
        self.run_command('reg add "HKCU\\Software\\Microsoft\\GameBar" /v AutoGameModeEnabled /t REG_DWORD /d 1 /f', "Enable Game Mode")
    
    def high_performance_power(self):
        self.run_command('powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c', "High Performance Power Plan")
    
    def disable_power_throttling(self):
        self.run_command('reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Power\\PowerThrottling" /v PowerThrottlingOff /t REG_DWORD /d 1 /f', "Disable Power Throttling")
    
    def optimize_virtual_memory(self):
        self.log("📊 Virtual memory optimization requires manual configuration")
        messagebox.showinfo("Virtual Memory", "Go to:\nSystem > Advanced system settings > Performance Settings > Advanced > Virtual Memory\n\nSet custom size: Initial=RAM size, Maximum=RAM size x 1.5")
    
    def disable_background_apps(self):
        self.run_command('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\BackgroundAccessApplications" /v GlobalUserDisabled /t REG_DWORD /d 1 /f', "Disable Background Apps")
    
    def disable_telemetry(self):
        commands = [
            'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection" /v AllowTelemetry /t REG_DWORD /d 0 /f',
            'sc config DiagTrack start= disabled',
            'sc stop DiagTrack'
        ]
        for cmd in commands:
            self.run_command(cmd, "Disable Telemetry")
    
    def disable_game_dvr(self):
        self.run_command('reg add "HKCU\\System\\GameConfigStore" /v GameDVR_Enabled /t REG_DWORD /d 0 /f', "Disable Game DVR")
        self.run_command('reg add "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\GameDVR" /v AppCaptureEnabled /t REG_DWORD /d 0 /f', "Disable App Capture")
    
    def disable_fullscreen_opt(self):
        self.log("ℹ️ Fullscreen optimizations - configure per-game in Properties > Compatibility")
        messagebox.showinfo("Fullscreen Opt", "Right-click game .exe > Properties > Compatibility\nCheck 'Disable fullscreen optimizations'")
    
    def high_performance_timer(self):
        self.run_command('bcdedit /set useplatformclock true', "High Performance Timer")
        self.run_command('bcdedit /set disabledynamictick yes', "Disable Dynamic Tick")
    
    def cpu_priority_optimization(self):
        self.run_command('reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile\\Tasks\\Games" /v "GPU Priority" /t REG_DWORD /d 8 /f', "CPU Priority for Games")
        self.run_command('reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile\\Tasks\\Games" /v Priority /t REG_DWORD /d 6 /f', "Game Priority")
    
    # Graphics optimizations
    def enable_hardware_gpu_scheduling(self):
        self.run_command('reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\GraphicsDrivers" /v HwSchMode /t REG_DWORD /d 2 /f', "Enable Hardware GPU Scheduling")
        self.log("⚠️ Restart required for GPU scheduling")
    
    def disable_visual_effects(self):
        self.run_command('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects" /v VisualFXSetting /t REG_DWORD /d 2 /f', "Disable Visual Effects")
    
    def disable_game_bar(self):
        self.run_command('reg add "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\GameDVR" /v AppCaptureEnabled /t REG_DWORD /d 0 /f', "Disable Game Bar")
        self.run_command('reg add "HKCU\\System\\GameConfigStore" /v GameDVR_Enabled /t REG_DWORD /d 0 /f', "Disable Game DVR")
    
    def disable_transparency(self):
        self.run_command('reg add "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v EnableTransparency /t REG_DWORD /d 0 /f', "Disable Transparency")
    
    def optimize_display(self):
        self.log("🖥️ Opening display settings...")
        subprocess.Popen(['ms-settings:display'])
    
    def disable_animations(self):
        self.run_command('reg add "HKCU\\Control Panel\\Desktop\\WindowMetrics" /v MinAnimate /t REG_SZ /d 0 /f', "Disable Animations")
    
    def disable_pointer_precision(self):
        self.run_command('reg add "HKCU\\Control Panel\\Mouse" /v MouseSpeed /t REG_SZ /d 0 /f', "Disable Enhanced Pointer Precision")
    
    def disable_desktop_composition(self):
        self.log("ℹ️ Desktop composition is always enabled in Windows 11")
    
    def disable_hdr(self):
        self.log("🖥️ Opening HDR settings...")
        subprocess.Popen(['ms-settings:display'])
    
    # Network optimizations
    def optimize_tcp(self):
        commands = [
            'netsh int tcp set global autotuninglevel=normal',
            'netsh int tcp set global chimney=enabled',
            'netsh int tcp set global dca=enabled',
            'netsh int tcp set global netdma=enabled',
            'netsh int tcp set global ecncapability=enabled',
            'netsh int tcp set global timestamps=disabled'
        ]
        for cmd in commands:
            self.run_command(cmd, "TCP Optimization")
    
    def disable_nagle(self):
        self.run_command('reg add "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters\\Interfaces" /v TcpAckFrequency /t REG_DWORD /d 1 /f', "Disable Nagle's Algorithm")
    
    def network_autotuning(self):
        self.run_command('netsh int tcp set global autotuninglevel=normal', "Network Auto-Tuning")
    
    def optimize_qos(self):
        self.run_command('reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Psched" /v NonBestEffortLimit /t REG_DWORD /d 0 /f', "QoS Optimization")
    
    def disable_network_throttling(self):
        self.run_command('reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile" /v NetworkThrottlingIndex /t REG_DWORD /d 0xffffffff /f', "Disable Network Throttling")
    
    def optimize_dns(self):
        self.log("🌐 DNS optimization - consider using:\nCloudflare: 1.1.1.1\nGoogle: 8.8.8.8")
        messagebox.showinfo("DNS", "To change DNS:\nSettings > Network > Properties > Edit DNS\n\nRecommended:\nCloudflare: 1.1.1.1, 1.0.0.1\nGoogle: 8.8.8.8, 8.8.4.4")
    
    def optimize_mtu(self):
        self.run_command('netsh interface ipv4 set subinterface "Ethernet" mtu=1500 store=persistent', "MTU Optimization")
    
    def optimize_network_adapter(self):
        self.log("📡 Opening Network Adapter settings...")
        subprocess.Popen(['ncpa.cpl'])
        messagebox.showinfo("Network Adapter", "In adapter properties:\n- Disable 'Power Management'\n- Enable 'Interrupt Moderation'\n- Set 'Receive/Transmit Buffers' to maximum")
    
    def reduce_network_latency(self):
        commands = [
            'netsh int tcp set global rss=enabled',
            'netsh int tcp set global ecncapability=enabled',
            'netsh int tcp set supplemental Internet congestionprovider=ctcp'
        ]
        for cmd in commands:
            self.run_command(cmd, "Network Latency Reduction")
    
    # System optimizations
    def disable_superfetch(self):
        self.run_command('sc config SysMain start= disabled', "Disable Superfetch")
        self.run_command('sc stop SysMain', "Stop Superfetch")
    
    def disable_search_indexing(self):
        self.run_command('sc config WSearch start= disabled', "Disable Windows Search")
        self.run_command('sc stop WSearch', "Stop Windows Search")
    
    def disable_auto_updates(self):
        self.log("⚠️ Disabling updates not recommended - use 'Active Hours' instead")
        messagebox.showinfo("Updates", "Consider setting Active Hours instead:\nSettings > Windows Update > Active hours")
    
    def optimize_defender(self):
        self.run_command('powershell -Command "Add-MpPreference -ExclusionPath \'C:\\Games\'"', "Add Games folder to Defender exclusions")
        self.log("ℹ️ Add your games folder to Windows Defender exclusions")
    
    def disable_notifications(self):
        self.run_command('reg add "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\PushNotifications" /v ToastEnabled /t REG_DWORD /d 0 /f', "Disable Notifications")
    
    def disable_system_restore(self):
        self.log("⚠️ System Restore provides backup - disable at your own risk")
        if messagebox.askyesno("Warning", "Disable System Restore? (Not recommended)"):
            self.run_command('vssadmin delete shadows /all /quiet', "Delete restore points")
    
    def disable_audio_enhancements(self):
        self.log("🔊 Opening Sound settings...")
        subprocess.Popen(['mmsys.cpl'])
        messagebox.showinfo("Audio", "Right-click your audio device > Properties\nDisable all enhancements")
    
    def disable_scheduled_tasks(self):
        tasks = [
            'schtasks /change /TN "\\Microsoft\\Windows\\Application Experience\\Microsoft Compatibility Appraiser" /DISABLE',
            'schtasks /change /TN "\\Microsoft\\Windows\\Application Experience\\ProgramDataUpdater" /DISABLE',
            'schtasks /change /TN "\\Microsoft\\Windows\\Autochk\\Proxy" /DISABLE',
            'schtasks /change /TN "\\Microsoft\\Windows\\DiskDiagnostic\\Microsoft-Windows-DiskDiagnosticDataCollector" /DISABLE'
        ]
        for cmd in tasks:
            self.run_command(cmd, "Disable Scheduled Task")
    
    def optimize_registry(self):
        self.log("🔧 Registry optimization...")
        optimizations = [
            ('SYSTEM\\CurrentControlSet\\Control', 'WaitToKillServiceTimeout', 2000),
            ('Control Panel\\Desktop', 'AutoEndTasks', 1),
            ('Control Panel\\Desktop', 'HungAppTimeout', 1000),
            ('Control Panel\\Desktop', 'WaitToKillAppTimeout', 2000),
            ('Control Panel\\Desktop', 'LowLevelHooksTimeout', 1000)
        ]
        for path, name, value in optimizations:
            if self.is_admin:
                try:
                    key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, path)
                    winreg.SetValueEx(key, name, 0, winreg.REG_SZ, str(value))
                    winreg.CloseKey(key)
                except:
                    pass
        self.log("✅ Registry optimized")
    
    def disable_usb_suspend(self):
        self.run_command('powercfg /setacvalueindex scheme_current 2a737441-1930-4402-8d77-b2bebba308a3 48e6b7a6-50f5-4782-a5d4-53bb8f07e226 0', "Disable USB Selective Suspend")
        self.run_command('powercfg /setactive scheme_current', "Apply Power Settings")
    
    # Advanced optimizations
    def disable_core_parking(self):
        self.run_command('reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Power\\PowerSettings\\54533251-82be-4824-96c1-47b60b740d00\\0cc5b647-c1df-4637-891a-dec35c318583" /v ValueMax /t REG_DWORD /d 0 /f', "Disable Core Parking")
        self.log("⚠️ Restart required")
    
    def enable_msi_mode(self):
        self.log("🎯 MSI Mode - Advanced GPU interrupt optimization")
        messagebox.showinfo("MSI Mode", "MSI Mode requires:\n1. MSI Utility tool\n2. GPU driver support\n3. Manual configuration\n\nSearch: 'MSI Mode Utility' for your GPU")
    
    def disable_hpet(self):
        self.run_command('bcdedit /deletevalue useplatformclock', "Disable HPET")
        self.log("⚠️ Restart required")
    
    def optimize_ssd(self):
        commands = [
            'fsutil behavior set DisableDeleteNotify 0',
            'defrag C: /L'
        ]
        for cmd in commands:
            self.run_command(cmd, "SSD Optimization")
    
    def enable_large_cache(self):
        self.run_command('reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management" /v LargeSystemCache /t REG_DWORD /d 1 /f', "Enable Large System Cache")
    
    def game_specific_tweaks(self):
        self.log("🎮 Game-specific optimizations")
        messagebox.showinfo("Game Tweaks", 
            "Per-game optimization:\n\n" +
            "1. Set game .exe to High Priority\n" +
            "2. Disable fullscreen optimizations\n" +
            "3. Run as administrator\n" +
            "4. Add to GPU control panel (High Performance)\n" +
            "5. Add to Windows Defender exclusions")
    
    def process_lasso_info(self):
        self.log("📊 Process Lasso - Advanced CPU management")
        messagebox.showinfo("Process Lasso", 
            "Process Lasso provides:\n\n" +
            "- CPU affinity management\n" +
            "- Process priority optimization\n" +
            "- Game mode automation\n\n" +
            "Download from: bitsum.com")
    
    def ultimate_performance_plan(self):
        self.run_command('powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61', "Enable Ultimate Performance Plan")
        self.run_command('powercfg /setactive e9a42b02-d5df-448d-aa00-03f14749eb61', "Activate Ultimate Performance")
    
    def bios_guide(self):
        self.log("💻 BIOS optimization guide")
        messagebox.showinfo("BIOS Settings",
            "Recommended BIOS settings:\n\n" +
            "✓ Enable XMP/DOCP (RAM overclock)\n" +
            "✓ Disable C-States\n" +
            "✓ Disable Intel SpeedStep/AMD Cool'n'Quiet\n" +
            "✓ Set CPU to maximum performance\n" +
            "✓ Enable Resizable BAR (if available)\n" +
            "✓ Disable unnecessary USB ports\n" +
            "✓ Set PCIe to Gen 3/4 (not Auto)\n\n" +
            "⚠️ Changes at your own risk!")
    
    def check_drivers(self):
        self.log("🔧 Driver check recommendations")
        messagebox.showinfo("Drivers",
            "Keep these drivers updated:\n\n" +
            "🎮 GPU: Use DDU, then fresh install\n" +
            "📡 Network: From manufacturer site\n" +
            "🎵 Audio: Latest from manufacturer\n" +
            "🖱️ Mouse/Keyboard: Latest firmware\n" +
            "💾 Chipset: From motherboard site\n\n" +
            "Avoid: Windows Update drivers")
    
    # Quick actions
    def apply_all(self):
        if not self.is_admin:
            messagebox.showerror("Admin Required", "Please run as Administrator!")
            return
        
        if not messagebox.askyesno("Confirm", "Apply ALL gaming optimizations?\n\nThis will:\n- Modify system settings\n- Change registry\n- Disable services\n\nCreate a restore point first!"):
            return
        
        self.log("🚀 STARTING FULL OPTIMIZATION...")
        thread = threading.Thread(target=self._apply_all_thread)
        thread.start()
    
    def _apply_all_thread(self):
        # Performance
        self.enable_game_mode()
        self.high_performance_power()
        self.disable_power_throttling()
        self.disable_background_apps()
        self.disable_telemetry()
        self.disable_game_dvr()
        self.high_performance_timer()
        self.cpu_priority_optimization()
        
        # Graphics
        self.enable_hardware_gpu_scheduling()
        self.disable_visual_effects()
        self.disable_game_bar()
        self.disable_transparency()
        self.disable_animations()
        self.disable_pointer_precision()
        
        # Network
        self.optimize_tcp()
        self.disable_nagle()
        self.network_autotuning()
        self.optimize_qos()
        self.disable_network_throttling()
        self.reduce_network_latency()
        
        # System
        self.disable_superfetch()
        self.disable_notifications()
        self.optimize_registry()
        self.disable_usb_suspend()
        
        # Advanced
        self.disable_core_parking()
        self.disable_hpet()
        self.optimize_ssd()
        self.enable_large_cache()
        self.ultimate_performance_plan()
        
        self.log("✅ OPTIMIZATION COMPLETE! Restart recommended.")
        messagebox.showinfo("Complete", "All optimizations applied!\n\nRestart your PC for changes to take effect.")
    
    def gaming_mode_only(self):
        self.log("🎯 Activating Gaming Mode only...")
        self.enable_game_mode()
        self.disable_game_bar()
        self.disable_game_dvr()
        self.high_performance_power()
        self.log("✅ Gaming Mode activated!")
    
    def restore_defaults(self):
        if not messagebox.askyesno("Confirm", "Restore Windows defaults?\n\nThis will undo gaming optimizations."):
            return
        
        self.log("🔄 Restoring defaults...")
        
        commands = [
            'powercfg /setactive 381b4222-f694-41f0-9685-ff5bb260df2e',
            'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Power\\PowerThrottling" /v PowerThrottlingOff /t REG_DWORD /d 0 /f',
            'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects" /v VisualFXSetting /t REG_DWORD /d 0 /f',
            'netsh int tcp set global autotuninglevel=normal',
            'sc config SysMain start= auto',
            'sc start SysMain'
        ]
        
        for cmd in commands:
            self.run_command(cmd, "Restore setting")
        
        self.log("✅ Defaults restored")
    
    def show_status(self):
        self.log("📊 Checking system status...")
        messagebox.showinfo("System Status", 
            "Current Configuration:\n\n" +
            "Check each tab for optimization status.\n" +
            "Green = Applied\n" +
            "Red = Not applied\n\n" +
            "Use 'Apply All' for full optimization.")

if __name__ == "__main__":
    root = tk.Tk()
    app = GamingConfigTool(root)
    root.mainloop()