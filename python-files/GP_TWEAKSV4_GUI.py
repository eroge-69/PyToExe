#!/usr/bin/env python3
"""
GP_TWEAKSV.4.0 GUI - Interfaccia Grafica
Creata da Assistant per Giorgio Pennisi
Versione: 4.0 GUI Edition
Data: 2025-09-15

ATTENZIONE: Questo tool richiede privilegi di amministratore e può 
modificare impostazioni critiche del sistema. Utilizzare con cautela!
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import os
import winreg
import ctypes
import sys
from datetime import datetime
import threading
import json

class GPTweaksGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GP_TWEAKSV.4.0 - GUI Edition")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)
        
        # Stile moderno
        self.root.configure(bg='#1e1e1e')
        
        # Variabili
        self.backup_dir = None
        self.is_admin = self.check_admin()
        
        # Setup dell'interfaccia
        self.setup_styles()
        self.create_widgets()
        self.create_backup_dir()
        
        # Controllo privilegi
        if not self.is_admin:
            self.show_admin_warning()
    
    def check_admin(self):
        """Controlla se l'applicazione ha privilegi di amministratore"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def show_admin_warning(self):
        """Mostra warning per privilegi amministratore"""
        messagebox.showerror(
            "Privilegi Amministratore Richiesti",
            "Questa applicazione richiede privilegi di amministratore per funzionare correttamente.\n\n"
            "Riavvia l'applicazione come Amministratore per utilizzare tutte le funzioni."
        )
    
    def setup_styles(self):
        """Configura lo stile dell'interfaccia"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Colori personalizzati
        self.colors = {
            'bg_dark': '#1e1e1e',
            'bg_medium': '#2d2d2d',
            'bg_light': '#3d3d3d',
            'accent': '#0078d4',
            'success': '#107c10',
            'warning': '#ff8c00',
            'danger': '#d13438',
            'text': '#ffffff',
            'text_secondary': '#cccccc'
        }
        
        # Stili personalizzati
        self.style.configure('Title.TLabel', 
                           background=self.colors['bg_dark'],
                           foreground=self.colors['text'],
                           font=('Segoe UI', 16, 'bold'))
        
        self.style.configure('Subtitle.TLabel',
                           background=self.colors['bg_dark'],
                           foreground=self.colors['text_secondary'],
                           font=('Segoe UI', 10))
        
        self.style.configure('Custom.TButton',
                           background=self.colors['accent'],
                           foreground='white',
                           font=('Segoe UI', 10))
        
        self.style.configure('Warning.TButton',
                           background=self.colors['warning'],
                           foreground='white',
                           font=('Segoe UI', 10))
        
        self.style.configure('Danger.TButton',
                           background=self.colors['danger'],
                           foreground='white',
                           font=('Segoe UI', 10))
    
    def create_widgets(self):
        """Crea i widget dell'interfaccia"""
        # Frame principale
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        self.create_header(main_frame)
        
        # Notebook per le tab
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Tab principali
        self.create_basic_tweaks_tab()
        self.create_advanced_tweaks_tab()
        self.create_services_tab()
        self.create_backup_tab()
        self.create_info_tab()
        
        # Status bar
        self.create_status_bar(main_frame)
    
    def create_header(self, parent):
        """Crea l'header dell'applicazione"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Titolo
        title_label = ttk.Label(header_frame, text="GP_TWEAKSV.4.0", style='Title.TLabel')
        title_label.pack(anchor=tk.W)
        
        # Sottotitolo
        subtitle_text = "FPS BOOST - Granular Control Edition"
        if not self.is_admin:
            subtitle_text += " ⚠️ MODALITÀ LIMITATA (Non Amministratore)"
        
        subtitle_label = ttk.Label(header_frame, text=subtitle_text, style='Subtitle.TLabel')
        subtitle_label.pack(anchor=tk.W)
        
        # Warning generale
        warning_frame = ttk.Frame(header_frame)
        warning_frame.pack(fill=tk.X, pady=(5, 0))
        
        warning_text = ("⚠️ ATTENZIONE: Alto rischio di instabilità del sistema, BSOD o crash delle applicazioni.\n"
                       "PROCEDI SOLO CON UN BACKUP COMPLETO DEL SISTEMA O PUNTO DI RIPRISTINO.")
        warning_label = ttk.Label(warning_frame, text=warning_text, 
                                foreground=self.colors['warning'], 
                                font=('Segoe UI', 9, 'italic'),
                                wraplength=750)
        warning_label.pack(anchor=tk.W)
    
    def create_basic_tweaks_tab(self):
        """Crea la tab per i tweak di base"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🚀 Tweak Base")
        
        # Scroll frame
        canvas = tk.Canvas(tab, bg=self.colors['bg_dark'])
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Sezioni tweak
        self.create_cpu_section(scrollable_frame)
        self.create_gpu_section(scrollable_frame)
        self.create_memory_section(scrollable_frame)
        self.create_network_section(scrollable_frame)
    
    def create_cpu_section(self, parent):
        """Crea la sezione CPU tweaks"""
        frame = ttk.LabelFrame(parent, text="🔧 CPU Tweaks", padding=10)
        frame.pack(fill=tk.X, padx=5, pady=5)
        
        desc_label = ttk.Label(frame, 
                             text="Ottimizzazioni CPU: Piano Ultimate Performance e priorità gaming",
                             font=('Segoe UI', 9))
        desc_label.pack(anchor=tk.W, pady=(0, 10))
        
        cpu_btn = ttk.Button(frame, text="Applica CPU Tweaks", 
                           command=self.apply_cpu_tweaks,
                           style='Custom.TButton')
        cpu_btn.pack(anchor=tk.W)
        
        if not self.is_admin:
            cpu_btn.configure(state='disabled')
    
    def create_gpu_section(self, parent):
        """Crea la sezione GPU tweaks"""
        frame = ttk.LabelFrame(parent, text="🎮 GPU Tweaks", padding=10)
        frame.pack(fill=tk.X, padx=5, pady=5)
        
        desc_label = ttk.Label(frame, 
                             text="Ottimizzazioni GPU: Disabilita TDR e abilita Hardware Accelerated GPU Scheduling",
                             font=('Segoe UI', 9))
        desc_label.pack(anchor=tk.W, pady=(0, 10))
        
        gpu_btn = ttk.Button(frame, text="Applica GPU Tweaks", 
                           command=self.apply_gpu_tweaks,
                           style='Custom.TButton')
        gpu_btn.pack(anchor=tk.W)
        
        if not self.is_admin:
            gpu_btn.configure(state='disabled')
    
    def create_memory_section(self, parent):
        """Crea la sezione Memory tweaks"""
        frame = ttk.LabelFrame(parent, text="💾 Memory Tweaks", padding=10)
        frame.pack(fill=tk.X, padx=5, pady=5)
        
        desc_label = ttk.Label(frame, 
                             text="Ottimizzazioni Memoria: Forza kernel e driver in RAM",
                             font=('Segoe UI', 9))
        desc_label.pack(anchor=tk.W, pady=(0, 10))
        
        memory_btn = ttk.Button(frame, text="Applica Memory Tweaks", 
                              command=self.apply_memory_tweaks,
                              style='Custom.TButton')
        memory_btn.pack(anchor=tk.W)
        
        if not self.is_admin:
            memory_btn.configure(state='disabled')
    
    def create_network_section(self, parent):
        """Crea la sezione Network tweaks"""
        frame = ttk.LabelFrame(parent, text="🌐 Network Tweaks", padding=10)
        frame.pack(fill=tk.X, padx=5, pady=5)
        
        desc_label = ttk.Label(frame, 
                             text="Ottimizzazioni Rete: Disabilita auto-tuning TCP e offloading",
                             font=('Segoe UI', 9))
        desc_label.pack(anchor=tk.W, pady=(0, 10))
        
        network_btn = ttk.Button(frame, text="Applica Network Tweaks", 
                               command=self.apply_network_tweaks,
                               style='Custom.TButton')
        network_btn.pack(anchor=tk.W)
        
        if not self.is_admin:
            network_btn.configure(state='disabled')
    
    def create_advanced_tweaks_tab(self):
        """Crea la tab per i tweak avanzati (ALTO RISCHIO)"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="⚠️ Avanzati")
        
        warning_frame = ttk.Frame(tab)
        warning_frame.pack(fill=tk.X, padx=10, pady=10)
        
        warning_label = ttk.Label(warning_frame, 
                                text="🚨 MASSIMO RISCHIO - Tweak del Kernel e Sistema",
                                font=('Segoe UI', 12, 'bold'),
                                foreground=self.colors['danger'])
        warning_label.pack()
        
        # Kernel tweaks
        kernel_frame = ttk.LabelFrame(tab, text="⚡ Kernel Tweaks", padding=10)
        kernel_frame.pack(fill=tk.X, padx=10, pady=5)
        
        timer_btn = ttk.Button(kernel_frame, text="Timer Precisione Alta (bcdedit)", 
                             command=self.apply_timer_tweaks,
                             style='Danger.TButton')
        timer_btn.pack(pady=2, anchor=tk.W)
        
        mitigations_btn = ttk.Button(kernel_frame, text="Disabilita Mitigazioni CPU (RISCHIO SICUREZZA!)", 
                                   command=self.apply_mitigations_tweaks,
                                   style='Danger.TButton')
        mitigations_btn.pack(pady=2, anchor=tk.W)
        
        if not self.is_admin:
            timer_btn.configure(state='disabled')
            mitigations_btn.configure(state='disabled')
    
    def create_services_tab(self):
        """Crea la tab per i servizi"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🛠️ Servizi")
        
        # Frame principale con scroll
        canvas = tk.Canvas(tab, bg=self.colors['bg_dark'])
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Sezioni servizi
        self.create_telemetry_section(scrollable_frame)
        self.create_xbox_section(scrollable_frame)
        self.create_bloat_section(scrollable_frame)
    
    def create_telemetry_section(self, parent):
        """Sezione telemetria"""
        frame = ttk.LabelFrame(parent, text="📊 Telemetria e Diagnostica", padding=10)
        frame.pack(fill=tk.X, padx=5, pady=5)
        
        btn = ttk.Button(frame, text="Disabilita Servizi Telemetria", 
                       command=self.disable_telemetry_services,
                       style='Warning.TButton')
        btn.pack(anchor=tk.W)
        
        if not self.is_admin:
            btn.configure(state='disabled')
    
    def create_xbox_section(self, parent):
        """Sezione Xbox"""
        frame = ttk.LabelFrame(parent, text="🎮 Xbox e Game Bar", padding=10)
        frame.pack(fill=tk.X, padx=5, pady=5)
        
        btn = ttk.Button(frame, text="Disabilita Servizi Xbox", 
                       command=self.disable_xbox_services,
                       style='Warning.TButton')
        btn.pack(anchor=tk.W)
        
        if not self.is_admin:
            btn.configure(state='disabled')
    
    def create_bloat_section(self, parent):
        """Sezione bloatware"""
        frame = ttk.LabelFrame(parent, text="🗑️ Bloatware Generale", padding=10)
        frame.pack(fill=tk.X, padx=5, pady=5)
        
        desc_label = ttk.Label(frame, 
                             text="ATTENZIONE: Disabiliterà la stampa e altre funzionalità",
                             font=('Segoe UI', 9),
                             foreground=self.colors['warning'])
        desc_label.pack(anchor=tk.W, pady=(0, 5))
        
        btn = ttk.Button(frame, text="Disabilita Servizi Bloatware", 
                       command=self.disable_bloat_services,
                       style='Danger.TButton')
        btn.pack(anchor=tk.W)
        
        if not self.is_admin:
            btn.configure(state='disabled')
    
    def create_backup_tab(self):
        """Crea la tab per i backup"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="💾 Backup")
        
        # Info backup
        info_frame = ttk.LabelFrame(tab, text="📁 Informazioni Backup", padding=10)
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        if self.backup_dir:
            backup_label = ttk.Label(info_frame, text=f"Directory Backup: {self.backup_dir}")
            backup_label.pack(anchor=tk.W)
        
        # Pulsanti
        btn_frame = ttk.Frame(info_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        show_backup_btn = ttk.Button(btn_frame, text="Mostra Directory Backup", 
                                   command=self.show_backup_directory)
        show_backup_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        create_backup_btn = ttk.Button(btn_frame, text="Crea Nuovo Backup", 
                                     command=self.create_manual_backup)
        create_backup_btn.pack(side=tk.LEFT)
        
        if not self.is_admin:
            create_backup_btn.configure(state='disabled')
        
        # Log area
        log_frame = ttk.LabelFrame(tab, text="📝 Log Operazioni", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, 
                                                background=self.colors['bg_medium'],
                                                foreground=self.colors['text'])
        self.log_text.pack(fill=tk.BOTH, expand=True)
    
    def create_info_tab(self):
        """Crea la tab informazioni e MSI Guide"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="ℹ️ Info")
        
        # MSI Guide
        msi_frame = ttk.LabelFrame(tab, text="⚡ MSI Utility Guide", padding=10)
        msi_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        msi_text = """MSI (Message Signaled Interrupts) Utility Guide

Questo è un potente tweak manuale che può ridurre la latenza per l'hardware chiave.
NON è automatizzato. Devi farlo tu stesso.

PROCEDURA RACCOMANDATA:
1. Scarica "MSI Utility v3" da una fonte affidabile come Guru3D
2. Esegui l'utility come Amministratore
3. Seleziona questi dispositivi in ordine di importanza:
   - La tua scheda grafica principale (es. NVIDIA GeForce, AMD Radeon)
   - Il tuo adattatore di rete principale (es. Intel Ethernet, Realtek Gaming)
   - Il tuo controller NVMe/SATA (es. Standard NVM Express Controller)
4. Per OGNUNO di questi dispositivi:
   a. Spunta la casella 'MSI' alla sua sinistra
   b. Nella colonna 'interrupt priority' (estrema destra), seleziona 'High'
5. Clicca 'Apply' in basso a destra
6. RIAVVIA il PC per applicare le modifiche

ATTENZIONE: Non cambiare impostazioni per altri dispositivi (come controller USB
o dispositivi di sistema) a meno che tu non sia un esperto, poiché può causare
problemi di avvio."""
        
        msi_label = ttk.Label(msi_frame, text=msi_text, font=('Consolas', 10),
                            justify=tk.LEFT, wraplength=750)
        msi_label.pack(anchor=tk.W)
        
        # About
        about_frame = ttk.LabelFrame(tab, text="📋 Informazioni", padding=10)
        about_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        about_text = ("GP_TWEAKSV.4.0 GUI Edition\n"
                     "Interfaccia grafica per il popolare tool di tweaking\n"
                     "Creata per Giorgio Pennisi\n"
                     f"Data: {datetime.now().strftime('%Y-%m-%d')}")
        
        about_label = ttk.Label(about_frame, text=about_text, 
                              font=('Segoe UI', 10))
        about_label.pack(anchor=tk.W)
    
    def create_status_bar(self, parent):
        """Crea la status bar"""
        self.status_var = tk.StringVar()
        self.status_var.set("Pronto")
        
        status_bar = ttk.Label(parent, textvariable=self.status_var, 
                             relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_backup_dir(self):
        """Crea la directory di backup"""
        try:
            # Timestamp per backup univoco
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            script_dir = os.path.dirname(os.path.abspath(__file__))
            self.backup_dir = os.path.join(script_dir, "backups", f"V4_GUI_{timestamp}")
            os.makedirs(self.backup_dir, exist_ok=True)
            self.log(f"Directory backup creata: {self.backup_dir}")
        except Exception as e:
            self.log(f"Errore nella creazione directory backup: {e}")
    
    def log(self, message):
        """Aggiunge un messaggio al log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        try:
            self.log_text.insert(tk.END, log_message)
            self.log_text.see(tk.END)
        except:
            # Se il log text non è ancora disponibile
            print(log_message.strip())
    
    def update_status(self, message):
        """Aggiorna la status bar"""
        self.status_var.set(message)
        self.root.update_idletasks()
    
    # === IMPLEMENTAZIONI TWEAK ===
    
    def apply_cpu_tweaks(self):
        """Applica i tweak CPU"""
        def run_cpu_tweaks():
            try:
                self.update_status("Applicando CPU tweaks...")
                self.log("Avvio CPU tweaks...")
                
                # Backup delle impostazioni correnti
                self.backup_registry_key(r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games")
                
                # Applica Ultimate Performance (se disponibile)
                result = subprocess.run([
                    "powercfg", "-setactive", "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    # Fallback a High Performance
                    subprocess.run([
                        "powercfg", "-setactive", "381b4222-f694-41f0-9685-ff5bb260df2e"
                    ], capture_output=True, text=True)
                
                # Impostazioni core parking
                commands = [
                    ["powercfg", "-setacvalueindex", "SCHEME_CURRENT", "SUB_PROCESSOR", "CPMINCORES", "100"],
                    ["powercfg", "-setdcvalueindex", "SCHEME_CURRENT", "SUB_PROCESSOR", "CPMINCORES", "100"],
                    ["powercfg", "-setacvalueindex", "SCHEME_CURRENT", "SUB_PROCESSOR", "CPMAXCORES", "100"],
                    ["powercfg", "-setdcvalueindex", "SCHEME_CURRENT", "SUB_PROCESSOR", "CPMAXCORES", "100"],
                    ["powercfg", "-S", "SCHEME_CURRENT"]
                ]
                
                for cmd in commands:
                    subprocess.run(cmd, capture_output=True, text=True)
                
                # Registry tweaks per gaming
                self.set_registry_value(
                    r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games",
                    "GPU Priority", "REG_DWORD", 8
                )
                
                self.set_registry_value(
                    r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games",
                    "Priority", "REG_DWORD", 6
                )
                
                self.log("CPU tweaks applicati con successo!")
                self.update_status("CPU tweaks completati")
                messagebox.showinfo("Successo", "CPU tweaks applicati con successo!")
                
            except Exception as e:
                self.log(f"Errore durante CPU tweaks: {e}")
                self.update_status("Errore CPU tweaks")
                messagebox.showerror("Errore", f"Errore durante CPU tweaks: {e}")
        
        # Esegui in thread separato
        threading.Thread(target=run_cpu_tweaks, daemon=True).start()
    
    def apply_gpu_tweaks(self):
        """Applica i tweak GPU"""
        def run_gpu_tweaks():
            try:
                self.update_status("Applicando GPU tweaks...")
                self.log("Avvio GPU tweaks...")
                
                # Backup
                self.backup_registry_key(r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\GraphicsDrivers")
                
                # Disabilita TDR
                self.set_registry_value(
                    r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\GraphicsDrivers",
                    "TdrLevel", "REG_DWORD", 0
                )
                
                # Abilita Hardware Accelerated GPU Scheduling
                self.set_registry_value(
                    r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\GraphicsDrivers",
                    "HwSchMode", "REG_DWORD", 2
                )
                
                self.log("GPU tweaks applicati con successo!")
                self.update_status("GPU tweaks completati - Riavvio richiesto")
                messagebox.showinfo("Successo", "GPU tweaks applicati con successo!\n\nRIAVVIO RICHIESTO per applicare le modifiche.")
                
            except Exception as e:
                self.log(f"Errore durante GPU tweaks: {e}")
                self.update_status("Errore GPU tweaks")
                messagebox.showerror("Errore", f"Errore durante GPU tweaks: {e}")
        
        threading.Thread(target=run_gpu_tweaks, daemon=True).start()
    
    def apply_memory_tweaks(self):
        """Applica i tweak Memory"""
        def run_memory_tweaks():
            try:
                self.update_status("Applicando Memory tweaks...")
                self.log("Avvio Memory tweaks...")
                
                # Backup
                self.backup_registry_key(r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management")
                
                # Forza kernel e driver in RAM
                self.set_registry_value(
                    r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management",
                    "DisablePagingExecutive", "REG_DWORD", 1
                )
                
                self.set_registry_value(
                    r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management",
                    "LargeSystemCache", "REG_DWORD", 1
                )
                
                self.log("Memory tweaks applicati con successo!")
                self.update_status("Memory tweaks completati")
                messagebox.showinfo("Successo", "Memory tweaks applicati con successo!")
                
            except Exception as e:
                self.log(f"Errore durante Memory tweaks: {e}")
                self.update_status("Errore Memory tweaks")
                messagebox.showerror("Errore", f"Errore durante Memory tweaks: {e}")
        
        threading.Thread(target=run_memory_tweaks, daemon=True).start()
    
    def apply_network_tweaks(self):
        """Applica i tweak Network"""
        def run_network_tweaks():
            try:
                self.update_status("Applicando Network tweaks...")
                self.log("Avvio Network tweaks...")
                
                # Backup
                self.backup_registry_key(r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters")
                
                # Comandi netsh per ottimizzazioni TCP
                netsh_commands = [
                    ["netsh", "int", "tcp", "set", "global", "autotuninglevel=disabled"],
                    ["netsh", "int", "tcp", "set", "global", "congestionprovider=ctcp"],
                    ["netsh", "int", "tcp", "set", "global", "ecncapability=disabled"],
                    ["netsh", "int", "tcp", "set", "global", "timestamps=disabled"],
                    ["netsh", "int", "tcp", "set", "global", "chimney=disabled"],
                    ["netsh", "int", "tcp", "set", "global", "rsc=disabled"]
                ]
                
                for cmd in netsh_commands:
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    self.log(f"Comando: {' '.join(cmd)} - Risultato: {result.returncode}")
                
                self.log("Network tweaks applicati con successo!")
                self.update_status("Network tweaks completati")
                messagebox.showinfo("Successo", "Network tweaks applicati con successo!")
                
            except Exception as e:
                self.log(f"Errore durante Network tweaks: {e}")
                self.update_status("Errore Network tweaks")
                messagebox.showerror("Errore", f"Errore durante Network tweaks: {e}")
        
        threading.Thread(target=run_network_tweaks, daemon=True).start()
    
    def apply_timer_tweaks(self):
        """Applica i tweak timer alta precisione"""
        if not messagebox.askyesno("Conferma", 
                                  "ATTENZIONE: Questi tweak modificano la configurazione di boot.\n"
                                  "Un errore potrebbe rendere il sistema non avviabile.\n\n"
                                  "Digitare 'YES' per continuare:", 
                                  icon='warning'):
            return
        
        def run_timer_tweaks():
            try:
                self.update_status("Applicando Timer tweaks...")
                self.log("Avvio Timer tweaks...")
                
                # Backup configurazione boot corrente
                with open(os.path.join(self.backup_dir, "bcdedit_before_timer.txt"), "w") as f:
                    result = subprocess.run(["bcdedit", "/enum"], capture_output=True, text=True)
                    f.write(result.stdout)
                
                # Applica tweak timer
                commands = [
                    ["bcdedit", "/set", "useplatformclock", "true"],
                    ["bcdedit", "/set", "disabledynamictick", "yes"],
                    ["bcdedit", "/set", "tscsyncpolicy", "Enhanced"]
                ]
                
                for cmd in commands:
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    self.log(f"Comando: {' '.join(cmd)} - Risultato: {result.returncode}")
                    if result.returncode != 0:
                        self.log(f"Errore: {result.stderr}")
                
                self.log("Timer tweaks applicati con successo!")
                self.update_status("Timer tweaks completati - Riavvio richiesto")
                messagebox.showinfo("Successo", "Timer tweaks applicati con successo!\n\nRIAVVIO RICHIESTO per applicare le modifiche.")
                
            except Exception as e:
                self.log(f"Errore durante Timer tweaks: {e}")
                self.update_status("Errore Timer tweaks")
                messagebox.showerror("Errore", f"Errore durante Timer tweaks: {e}")
        
        threading.Thread(target=run_timer_tweaks, daemon=True).start()
    
    def apply_mitigations_tweaks(self):
        """Applica i tweak per disabilitare le mitigazioni CPU"""
        if not messagebox.askyesno("RISCHIO SICUREZZA", 
                                  "⚠️ ATTENZIONE: Disabilitare le mitigazioni CPU renderà il sistema\n"
                                  "vulnerabile agli exploit Spectre e Meltdown.\n\n"
                                  "Questo rappresenta un SERIO RISCHIO di SICUREZZA.\n\n"
                                  "Continuare solo se si comprende completamente il rischio.", 
                                  icon='warning'):
            return
        
        def run_mitigations_tweaks():
            try:
                self.update_status("Disabilitando mitigazioni CPU...")
                self.log("Avvio disabilitazione mitigazioni CPU...")
                
                # Backup
                self.backup_registry_key(r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management")
                
                # Disabilita mitigazioni
                self.set_registry_value(
                    r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management",
                    "FeatureSettingsOverride", "REG_DWORD", 3
                )
                
                self.set_registry_value(
                    r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management",
                    "FeatureSettingsOverrideMask", "REG_DWORD", 3
                )
                
                self.log("Mitigazioni CPU disabilitate!")
                self.update_status("Mitigazioni disabilitate - Riavvio richiesto")
                messagebox.showwarning("Completato", "Mitigazioni CPU disabilitate!\n\nRIAVVIO RICHIESTO per applicare le modifiche.\n\n⚠️ Il sistema è ora più vulnerabile agli attacchi.")
                
            except Exception as e:
                self.log(f"Errore durante disabilitazione mitigazioni: {e}")
                self.update_status("Errore mitigazioni")
                messagebox.showerror("Errore", f"Errore durante disabilitazione mitigazioni: {e}")
        
        threading.Thread(target=run_mitigations_tweaks, daemon=True).start()
    
    def disable_telemetry_services(self):
        """Disabilita servizi telemetria"""
        def run_telemetry():
            try:
                self.update_status("Disabilitando servizi telemetria...")
                self.log("Disabilitazione servizi telemetria...")
                
                services = ["DiagTrack"]
                
                for service in services:
                    # Stop service
                    subprocess.run(["sc", "stop", service], capture_output=True, text=True)
                    # Disable service
                    result = subprocess.run(["sc", "config", service, "start=", "disabled"], 
                                          capture_output=True, text=True)
                    self.log(f"Servizio {service}: {'Disabilitato' if result.returncode == 0 else 'Errore'}")
                
                self.log("Servizi telemetria disabilitati!")
                self.update_status("Telemetria disabilitata")
                messagebox.showinfo("Successo", "Servizi telemetria disabilitati con successo!")
                
            except Exception as e:
                self.log(f"Errore durante disabilitazione telemetria: {e}")
                messagebox.showerror("Errore", f"Errore: {e}")
        
        threading.Thread(target=run_telemetry, daemon=True).start()
    
    def disable_xbox_services(self):
        """Disabilita servizi Xbox"""
        def run_xbox():
            try:
                self.update_status("Disabilitando servizi Xbox...")
                self.log("Disabilitazione servizi Xbox...")
                
                services = ["XblGameSave", "XblAuthManager", "XboxGipSvc", "XboxNetApiSvc"]
                
                for service in services:
                    subprocess.run(["sc", "stop", service], capture_output=True, text=True)
                    result = subprocess.run(["sc", "config", service, "start=", "disabled"], 
                                          capture_output=True, text=True)
                    self.log(f"Servizio {service}: {'Disabilitato' if result.returncode == 0 else 'Errore'}")
                
                self.log("Servizi Xbox disabilitati!")
                self.update_status("Xbox disabilitato")
                messagebox.showinfo("Successo", "Servizi Xbox disabilitati con successo!")
                
            except Exception as e:
                self.log(f"Errore durante disabilitazione Xbox: {e}")
                messagebox.showerror("Errore", f"Errore: {e}")
        
        threading.Thread(target=run_xbox, daemon=True).start()
    
    def disable_bloat_services(self):
        """Disabilita servizi bloatware"""
        if not messagebox.askyesno("Conferma", 
                                  "ATTENZIONE: Questa operazione disabiliterà:\n"
                                  "- SuperFetch\n- Windows Search\n- Maps Broker\n- Spooler di stampa\n\n"
                                  "La stampa NON funzionerà più!\n\nContinuare?"):
            return
        
        def run_bloat():
            try:
                self.update_status("Disabilitando servizi bloatware...")
                self.log("Disabilitazione servizi bloatware...")
                
                services = ["SysMain", "WSearch", "MapsBroker", "Spooler"]
                
                for service in services:
                    subprocess.run(["sc", "stop", service], capture_output=True, text=True)
                    result = subprocess.run(["sc", "config", service, "start=", "disabled"], 
                                          capture_output=True, text=True)
                    self.log(f"Servizio {service}: {'Disabilitato' if result.returncode == 0 else 'Errore'}")
                
                self.log("Servizi bloatware disabilitati!")
                self.update_status("Bloatware disabilitato")
                messagebox.showinfo("Successo", "Servizi bloatware disabilitati!\n\n⚠️ La stampa non funzionerà più.")
                
            except Exception as e:
                self.log(f"Errore durante disabilitazione bloatware: {e}")
                messagebox.showerror("Errore", f"Errore: {e}")
        
        threading.Thread(target=run_bloat, daemon=True).start()
    
    def show_backup_directory(self):
        """Mostra la directory di backup"""
        if self.backup_dir and os.path.exists(self.backup_dir):
            subprocess.run(["explorer", self.backup_dir])
        else:
            messagebox.showwarning("Backup", "Directory di backup non trovata!")
    
    def create_manual_backup(self):
        """Crea un backup manuale"""
        def run_backup():
            try:
                self.update_status("Creando backup...")
                self.log("Creazione backup manuale...")
                
                # Export di chiavi registry critiche
                registry_keys = [
                    (r"HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers", "GraphicsDrivers.reg"),
                    (r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "MemoryManagement.reg"),
                    (r"HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters", "TcpipParameters.reg"),
                    (r"HKLM\SYSTEM\CurrentControlSet\Control\PriorityControl", "PriorityControl.reg")
                ]
                
                for reg_key, filename in registry_keys:
                    filepath = os.path.join(self.backup_dir, filename)
                    result = subprocess.run(["reg", "export", reg_key, filepath, "/y"], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        self.log(f"Backup creato: {filename}")
                    else:
                        self.log(f"Errore backup {filename}: {result.stderr}")
                
                # Backup configurazioni
                with open(os.path.join(self.backup_dir, "bcdedit_manual.txt"), "w") as f:
                    result = subprocess.run(["bcdedit", "/enum"], capture_output=True, text=True)
                    f.write(result.stdout)
                
                with open(os.path.join(self.backup_dir, "services_manual.txt"), "w") as f:
                    result = subprocess.run(["sc", "queryex", "type=", "service", "state=", "all"], 
                                          capture_output=True, text=True)
                    f.write(result.stdout)
                
                self.log("Backup manuale completato!")
                self.update_status("Backup completato")
                messagebox.showinfo("Successo", f"Backup creato con successo in:\n{self.backup_dir}")
                
            except Exception as e:
                self.log(f"Errore durante backup: {e}")
                messagebox.showerror("Errore", f"Errore durante backup: {e}")
        
        threading.Thread(target=run_backup, daemon=True).start()
    
    # === UTILITY FUNCTIONS ===
    
    def set_registry_value(self, key_path, value_name, value_type, value_data):
        """Imposta un valore nel registry"""
        try:
            # Converti il path per reg add
            cmd = ["reg", "add", key_path, "/v", value_name, "/t", value_type, "/d", str(value_data), "/f"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log(f"Registry: {key_path}\\{value_name} = {value_data}")
                return True
            else:
                self.log(f"Errore registry: {result.stderr}")
                return False
        except Exception as e:
            self.log(f"Errore impostazione registry: {e}")
            return False
    
    def backup_registry_key(self, key_path):
        """Crea backup di una chiave registry"""
        try:
            # Converti HKEY_LOCAL_MACHINE in HKLM per reg export
            backup_key = key_path.replace("HKEY_LOCAL_MACHINE", "HKLM")
            filename = backup_key.replace("\\", "_").replace("HKLM_", "") + ".reg"
            filepath = os.path.join(self.backup_dir, filename)
            
            result = subprocess.run(["reg", "export", backup_key, filepath, "/y"], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log(f"Backup registry: {filename}")
                return True
            else:
                self.log(f"Errore backup registry: {result.stderr}")
                return False
        except Exception as e:
            self.log(f"Errore backup registry: {e}")
            return False
    
    def run(self):
        """Avvia l'applicazione"""
        self.root.mainloop()

# === MAIN ===
if __name__ == "__main__":
    try:
        app = GPTweaksGUI()
        app.run()
    except Exception as e:
        print(f"Errore fatale: {e}")
        input("Premere Invio per uscire...")
