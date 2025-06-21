import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import threading
import time
import os
from datetime import datetime

class ModernSecurityTool:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_main_window()
        self.create_splash_screen()
        
    def setup_main_window(self):
        self.root.title("AUFI - Advanced Universal Forensic Interface")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1e1e1e')
        
        # Pencereyi ortala
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1200 // 2)
        y = (self.root.winfo_screenheight() // 2) - (800 // 2)
        self.root.geometry(f"1200x800+{x}+{y}")
        
        # Ana pencereyi gizle
        self.root.withdraw()
        
        # Stil konfigürasyonu
        self.setup_styles()
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Karanlık tema renkleri
        style.configure('Dark.TFrame', background='#1e1e1e')
        style.configure('Dark.TLabel', background='#1e1e1e', foreground='#ffffff', font=('Arial', 10))
        style.configure('Title.TLabel', background='#1e1e1e', foreground='#00ff88', font=('Arial', 16, 'bold'))
        style.configure('Dark.TButton', background='#2d2d2d', foreground='#ffffff', font=('Arial', 10))
        style.configure('Accent.TButton', background='#00ff88', foreground='#000000', font=('Arial', 10, 'bold'))
        style.configure('Dark.TEntry', background='#2d2d2d', foreground='#ffffff', fieldbackground='#2d2d2d')
        style.configure('Dark.TNotebook', background='#1e1e1e', tabposition='n')
        style.configure('Dark.TNotebook.Tab', background='#2d2d2d', foreground='#ffffff', padding=[12, 8])
        
    def create_splash_screen(self):
        # Splash screen penceresi
        self.splash = tk.Toplevel()
        self.splash.title("")
        self.splash.geometry("500x300")
        self.splash.configure(bg='#0a0a0a')
        self.splash.overrideredirect(True)
        
        # Splash screen'i ortala
        self.splash.update_idletasks()
        x = (self.splash.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.splash.winfo_screenheight() // 2) - (300 // 2)
        self.splash.geometry(f"500x300+{x}+{y}")
        
        # Logo ve başlık
        title_frame = tk.Frame(self.splash, bg='#0a0a0a')
        title_frame.pack(expand=True, fill='both')
        
        # Ana başlık
        title_label = tk.Label(title_frame, text="AUFI", font=('Arial', 32, 'bold'), 
                              fg='#00ff88', bg='#0a0a0a')
        title_label.pack(pady=(50, 10))
        
        subtitle_label = tk.Label(title_frame, text="Advanced Universal Forensic Interface", 
                                 font=('Arial', 12), fg='#888888', bg='#0a0a0a')
        subtitle_label.pack(pady=(0, 20))
        
        # Loading bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(title_frame, variable=self.progress_var, 
                                           maximum=100, length=300, mode='determinate')
        self.progress_bar.pack(pady=20)
        
        # Loading metni
        self.loading_label = tk.Label(title_frame, text="Initializing...", 
                                     font=('Arial', 10), fg='#888888', bg='#0a0a0a')
        self.loading_label.pack(pady=10)
        
        # Uyarı metni
        warning_label = tk.Label(title_frame, text="⚠️ For Educational and Legal Testing Only", 
                                font=('Arial', 9), fg='#ff6b6b', bg='#0a0a0a')
        warning_label.pack(pady=(20, 0))
        
        # Loading animasyonunu başlat
        self.start_loading_animation()
        
    def start_loading_animation(self):
        def animate():
            steps = [
                (20, "Loading modules..."),
                (40, "Checking dependencies..."),
                (60, "Initializing interface..."),
                (80, "Preparing tools..."),
                (100, "Ready!")
            ]
            
            for progress, text in steps:
                self.progress_var.set(progress)
                self.loading_label.config(text=text)
                self.splash.update()
                time.sleep(0.8)
            
            time.sleep(1)
            self.splash.destroy()
            self.show_main_interface()
        
        thread = threading.Thread(target=animate)
        thread.daemon = True
        thread.start()
    
    def show_main_interface(self):
        self.root.deiconify()
        self.create_main_interface()
        
    def create_main_interface(self):
        # Ana frame
        main_frame = ttk.Frame(self.root, style='Dark.TFrame')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Başlık
        header_frame = ttk.Frame(main_frame, style='Dark.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text="🔒 AUFI - Security Testing Suite", 
                               style='Title.TLabel')
        title_label.pack(side='left')
        
        # Zaman etiketi
        self.time_label = ttk.Label(header_frame, text="", style='Dark.TLabel')
        self.time_label.pack(side='right')
        self.update_time()
        
        # Notebook (Tab sistemi)
        self.notebook = ttk.Notebook(main_frame, style='Dark.TNotebook')
        self.notebook.pack(fill='both', expand=True)
        
        # Tabları oluştur
        self.create_nmap_tab()
        self.create_wireless_tab()
        self.create_output_tab()
        
        # Durum çubuğu
        self.create_status_bar(main_frame)
        
    def create_nmap_tab(self):
        # Nmap tab
        nmap_frame = ttk.Frame(self.notebook, style='Dark.TFrame')
        self.notebook.add(nmap_frame, text='🌐 Network Scanning')
        
        # Sol panel - Ayarlar
        left_panel = ttk.Frame(nmap_frame, style='Dark.TFrame')
        left_panel.pack(side='left', fill='y', padx=(0, 10), pady=10)
        
        ttk.Label(left_panel, text="Network Scanning", style='Title.TLabel').pack(pady=(0, 20))
        
        # Target input
        ttk.Label(left_panel, text="Target:", style='Dark.TLabel').pack(anchor='w')
        self.target_entry = ttk.Entry(left_panel, style='Dark.TEntry', width=30)
        self.target_entry.pack(pady=(5, 15), fill='x')
        self.target_entry.insert(0, "192.168.1.0/24")
        
        # Scan type
        ttk.Label(left_panel, text="Scan Type:", style='Dark.TLabel').pack(anchor='w')
        self.scan_type = ttk.Combobox(left_panel, values=[
            "Quick Scan (-T4 -F)",
            "Intense Scan (-T4 -A -v)",
            "Comprehensive (-p-)",
            "Stealth Scan (-sS -T2)",
            "UDP Scan (-sU --top-ports 1000)"
        ], state='readonly')
        self.scan_type.pack(pady=(5, 15), fill='x')
        self.scan_type.set("Quick Scan (-T4 -F)")
        
        # Buttons
        button_frame = ttk.Frame(left_panel, style='Dark.TFrame')
        button_frame.pack(fill='x', pady=10)
        
        self.scan_button = ttk.Button(button_frame, text="🚀 Start Scan", 
                                     command=self.start_nmap_scan, style='Accent.TButton')
        self.scan_button.pack(fill='x', pady=5)
        
        ttk.Button(button_frame, text="💾 Save Results", 
                  command=self.save_results, style='Dark.TButton').pack(fill='x', pady=5)
        
        # Sağ panel - Sonuçlar
        right_panel = ttk.Frame(nmap_frame, style='Dark.TFrame')
        right_panel.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        ttk.Label(right_panel, text="Scan Results", style='Title.TLabel').pack(anchor='w')
        
        # Sonuç text widget
        self.nmap_output = tk.Text(right_panel, bg='#1a1a1a', fg='#00ff00', 
                                  font=('Consolas', 10), wrap='word')
        self.nmap_output.pack(fill='both', expand=True, pady=(10, 0))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(right_panel, orient='vertical', command=self.nmap_output.yview)
        scrollbar.pack(side='right', fill='y')
        self.nmap_output.config(yscrollcommand=scrollbar.set)
        
    def create_wireless_tab(self):
        # Wireless tab
        wireless_frame = ttk.Frame(self.notebook, style='Dark.TFrame')
        self.notebook.add(wireless_frame, text='📡 Wireless Tools')
        
        # Ana container
        container = ttk.Frame(wireless_frame, style='Dark.TFrame')
        container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Başlık
        ttk.Label(container, text="Wireless Security Tools", style='Title.TLabel').pack(pady=(0, 20))
        
        # Üst panel - Genel ayarlar
        top_frame = ttk.Frame(container, style='Dark.TFrame')
        top_frame.pack(fill='x', pady=(0, 20))
        
        # Interface seçimi
        interface_frame = ttk.Frame(top_frame, style='Dark.TFrame')
        interface_frame.pack(side='left', padx=(0, 20))
        
        ttk.Label(interface_frame, text="Interface:", style='Dark.TLabel').pack(anchor='w')
        self.interface_entry = ttk.Entry(interface_frame, style='Dark.TEntry', width=15)
        self.interface_entry.pack(pady=(5, 0))
        self.interface_entry.insert(0, "wlan0")
        
        # BSSID
        bssid_frame = ttk.Frame(top_frame, style='Dark.TFrame')
        bssid_frame.pack(side='left', padx=(0, 20))
        
        ttk.Label(bssid_frame, text="Target BSSID:", style='Dark.TLabel').pack(anchor='w')
        self.bssid_entry = ttk.Entry(bssid_frame, style='Dark.TEntry', width=20)
        self.bssid_entry.pack(pady=(5, 0))
        
        # Alt panel - Tool seçenekleri
        tools_frame = ttk.Frame(container, style='Dark.TFrame')
        tools_frame.pack(fill='both', expand=True)
        
        # Sol taraf - Aircrack-ng
        left_tools = ttk.Frame(tools_frame, style='Dark.TFrame')
        left_tools.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        ttk.Label(left_tools, text="🔓 Password Cracking", style='Title.TLabel').pack(pady=(0, 10))
        
        ttk.Label(left_tools, text="Capture File:", style='Dark.TLabel').pack(anchor='w')
        capture_frame = ttk.Frame(left_tools, style='Dark.TFrame')
        capture_frame.pack(fill='x', pady=(5, 10))
        
        self.capture_entry = ttk.Entry(capture_frame, style='Dark.TEntry')
        self.capture_entry.pack(side='left', fill='x', expand=True)
        ttk.Button(capture_frame, text="📁", command=self.browse_capture_file, 
                  style='Dark.TButton', width=3).pack(side='right', padx=(5, 0))
        
        ttk.Label(left_tools, text="Wordlist:", style='Dark.TLabel').pack(anchor='w')
        wordlist_frame = ttk.Frame(left_tools, style='Dark.TFrame')
        wordlist_frame.pack(fill='x', pady=(5, 15))
        
        self.wordlist_entry = ttk.Entry(wordlist_frame, style='Dark.TEntry')
        self.wordlist_entry.pack(side='left', fill='x', expand=True)
        ttk.Button(wordlist_frame, text="📁", command=self.browse_wordlist_file, 
                  style='Dark.TButton', width=3).pack(side='right', padx=(5, 0))
        
        ttk.Button(left_tools, text="🔓 Start Cracking", command=self.start_crack, 
                  style='Accent.TButton').pack(fill='x', pady=5)
        
        # Sağ taraf - Saldırı araçları
        right_tools = ttk.Frame(tools_frame, style='Dark.TFrame')
        right_tools.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        ttk.Label(right_tools, text="⚡ Attack Tools", style='Title.TLabel').pack(pady=(0, 10))
        
        ttk.Button(right_tools, text="🚫 Deauth Attack", command=self.deauth_attack, 
                  style='Dark.TButton').pack(fill='x', pady=5)
        
        # Payload injection
        ttk.Label(right_tools, text="Payload File:", style='Dark.TLabel').pack(anchor='w', pady=(15, 0))
        payload_frame = ttk.Frame(right_tools, style='Dark.TFrame')
        payload_frame.pack(fill='x', pady=(5, 10))
        
        self.payload_entry = ttk.Entry(payload_frame, style='Dark.TEntry')
        self.payload_entry.pack(side='left', fill='x', expand=True)
        ttk.Button(payload_frame, text="📁", command=self.browse_payload_file, 
                  style='Dark.TButton', width=3).pack(side='right', padx=(5, 0))
        
        ttk.Button(right_tools, text="💉 Packet Injection", command=self.packet_injection, 
                  style='Dark.TButton').pack(fill='x', pady=5)
        
    def create_output_tab(self):
        # Output tab
        output_frame = ttk.Frame(self.notebook, style='Dark.TFrame')
        self.notebook.add(output_frame, text='📋 Output Log')
        
        # Frame
        container = ttk.Frame(output_frame, style='Dark.TFrame')
        container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Başlık ve kontroller
        header = ttk.Frame(container, style='Dark.TFrame')
        header.pack(fill='x', pady=(0, 10))
        
        ttk.Label(header, text="Command Output", style='Title.TLabel').pack(side='left')
        
        ttk.Button(header, text="🗑️ Clear", command=self.clear_output, 
                  style='Dark.TButton').pack(side='right', padx=(5, 0))
        ttk.Button(header, text="💾 Save Log", command=self.save_log, 
                  style='Dark.TButton').pack(side='right')
        
        # Output text
        self.output_text = tk.Text(container, bg='#0a0a0a', fg='#ffffff', 
                                  font=('Consolas', 9), wrap='word')
        self.output_text.pack(fill='both', expand=True)
        
        # Scrollbar
        output_scrollbar = ttk.Scrollbar(container, orient='vertical', command=self.output_text.yview)
        output_scrollbar.pack(side='right', fill='y')
        self.output_text.config(yscrollcommand=output_scrollbar.set)
        
    def create_status_bar(self, parent):
        # Status bar
        status_frame = ttk.Frame(parent, style='Dark.TFrame')
        status_frame.pack(fill='x', pady=(10, 0))
        
        self.status_label = ttk.Label(status_frame, text="Ready", style='Dark.TLabel')
        self.status_label.pack(side='left')
        
        # Progress bar
        self.main_progress = ttk.Progressbar(status_frame, mode='indeterminate', length=200)
        self.main_progress.pack(side='right', padx=(10, 0))
        
    def update_time(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)
        
    def log_output(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.output_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.output_text.see(tk.END)
        self.root.update()
        
    def update_status(self, message):
        self.status_label.config(text=message)
        
    def start_nmap_scan(self):
        target = self.target_entry.get()
        if not target:
            messagebox.showerror("Error", "Please enter a target!")
            return
            
        self.scan_button.config(state='disabled', text='Scanning...')
        self.main_progress.start()
        self.update_status("Running Nmap scan...")
        
        def run_scan():
            try:
                scan_type = self.scan_type.get()
                if "Quick" in scan_type:
                    cmd = f"nmap -T4 -F {target}"
                elif "Intense" in scan_type:
                    cmd = f"nmap -T4 -A -v {target}"
                elif "Comprehensive" in scan_type:
                    cmd = f"nmap -p- {target}"
                elif "Stealth" in scan_type:
                    cmd = f"nmap -sS -T2 {target}"
                else:
                    cmd = f"nmap -sU --top-ports 1000 {target}"
                
                self.log_output(f"Executing: {cmd}")
                
                process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, 
                                         stderr=subprocess.PIPE, text=True)
                
                output, error = process.communicate()
                
                if output:
                    self.nmap_output.delete(1.0, tk.END)
                    self.nmap_output.insert(tk.END, output)
                    self.log_output("Nmap scan completed successfully")
                
                if error:
                    self.log_output(f"Error: {error}")
                    
            except Exception as e:
                self.log_output(f"Exception occurred: {str(e)}")
            finally:
                self.scan_button.config(state='normal', text='🚀 Start Scan')
                self.main_progress.stop()
                self.update_status("Ready")
        
        thread = threading.Thread(target=run_scan)
        thread.daemon = True
        thread.start()
        
    def start_crack(self):
        capture_file = self.capture_entry.get()
        wordlist_file = self.wordlist_entry.get()
        
        if not capture_file or not wordlist_file:
            messagebox.showerror("Error", "Please select both capture and wordlist files!")
            return
            
        self.main_progress.start()
        self.update_status("Running aircrack-ng...")
        
        def run_crack():
            try:
                cmd = f"aircrack-ng -w {wordlist_file} {capture_file}"
                self.log_output(f"Executing: {cmd}")
                
                process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, 
                                         stderr=subprocess.PIPE, text=True)
                output, error = process.communicate()
                
                if output:
                    self.log_output(f"Aircrack-ng output:\n{output}")
                if error:
                    self.log_output(f"Error: {error}")
                    
            except Exception as e:
                self.log_output(f"Exception occurred: {str(e)}")
            finally:
                self.main_progress.stop()
                self.update_status("Ready")
        
        thread = threading.Thread(target=run_crack)
        thread.daemon = True
        thread.start()
        
    def deauth_attack(self):
        bssid = self.bssid_entry.get()
        interface = self.interface_entry.get()
        
        if not bssid or not interface:
            messagebox.showerror("Error", "Please enter BSSID and interface!")
            return
            
        # Uyarı mesajı
        result = messagebox.askyesno("Warning", 
                                   "This will perform a deauthentication attack. "
                                   "Only use on networks you own or have permission to test. "
                                   "Continue?")
        if not result:
            return
            
        self.main_progress.start()
        self.update_status("Running deauth attack...")
        
        def run_deauth():
            try:
                cmd = f"aireplay-ng --deauth 10 -a {bssid} {interface}"
                self.log_output(f"Executing: {cmd}")
                
                process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, 
                                         stderr=subprocess.PIPE, text=True)
                output, error = process.communicate()
                
                if output:
                    self.log_output(f"Deauth output:\n{output}")
                if error:
                    self.log_output(f"Error: {error}")
                    
            except Exception as e:
                self.log_output(f"Exception occurred: {str(e)}")
            finally:
                self.main_progress.stop()
                self.update_status("Ready")
        
        thread = threading.Thread(target=run_deauth)
        thread.daemon = True
        thread.start()
        
    def packet_injection(self):
        bssid = self.bssid_entry.get()
        interface = self.interface_entry.get()
        payload_file = self.payload_entry.get()
        
        if not all([bssid, interface, payload_file]):
            messagebox.showerror("Error", "Please fill all required fields!")
            return
            
        self.main_progress.start()
        self.update_status("Injecting packets...")
        
        def run_injection():
            try:
                cmd = f"aireplay-ng --bssid {bssid} -p 0 -c FF:FF:FF:FF:FF:FF -r {payload_file} {interface}"
                self.log_output(f"Executing: {cmd}")
                
                process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, 
                                         stderr=subprocess.PIPE, text=True)
                output, error = process.communicate()
                
                if output:
                    self.log_output(f"Injection output:\n{output}")
                if error:
                    self.log_output(f"Error: {error}")
                    
            except Exception as e:
                self.log_output(f"Exception occurred: {str(e)}")
            finally:
                self.main_progress.stop()
                self.update_status("Ready")
        
        thread = threading.Thread(target=run_injection)
        thread.daemon = True
        thread.start()
        
    def browse_capture_file(self):
        filename = filedialog.askopenfilename(
            title="Select Capture File",
            filetypes=[("Cap files", "*.cap"), ("All files", "*.*")]
        )
        if filename:
            self.capture_entry.delete(0, tk.END)
            self.capture_entry.insert(0, filename)
            
    def browse_wordlist_file(self):
        filename = filedialog.askopenfilename(
            title="Select Wordlist File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.wordlist_entry.delete(0, tk.END)
            self.wordlist_entry.insert(0, filename)
            
    def browse_payload_file(self):
        filename = filedialog.askopenfilename(
            title="Select Payload File",
            filetypes=[("All files", "*.*")]
        )
        if filename:
            self.payload_entry.delete(0, tk.END)
            self.payload_entry.insert(0, filename)
            
    def save_results(self):
        content = self.nmap_output.get(1.0, tk.END)
        if not content.strip():
            messagebox.showinfo("Info", "No results to save!")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            with open(filename, 'w') as f:
                f.write(content)
            messagebox.showinfo("Success", f"Results saved to {filename}")
            
    def save_log(self):
        content = self.output_text.get(1.0, tk.END)
        if not content.strip():
            messagebox.showinfo("Info", "No log to save!")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            with open(filename, 'w') as f:
                f.write(content)
            messagebox.showinfo("Success", f"Log saved to {filename}")
            
    def clear_output(self):
        self.output_text.delete(1.0, tk.END)
        
    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
        
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()

if __name__ == "__main__":
    app = ModernSecurityTool()
    app.run()