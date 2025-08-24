import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, Menu
import subprocess
import threading
import time
import datetime
import sys
import re

class NetworkDiagnosticTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Network Diagnostic Tool")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Variabel tema
        self.themes = {
            "Default": {"bg": "SystemButtonFace", "fg": "black"},
            "Dark": {"bg": "#2e2e2e", "fg": "white"},
            "Blue": {"bg": "#e6f2ff", "fg": "black"},
            "Green": {"bg": "#e6ffe6", "fg": "black"},
            "Red": {"bg": "#ffe6e6", "fg": "black"}
        }
        self.current_theme = "Default"
        
        # Buat menu bar
        self.create_menu()
        
        # Variabel untuk menyimpan hasil
        self.ping_process = None
        self.tracert_process = None
        self.is_pinging = False
        self.is_tracerting = False
        self.log_content = ""
        
        # Buat notebook (tab)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Frame untuk Ping Load
        self.ping_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.ping_frame, text='Ping Load')
        
        # Frame untuk Traceroute
        self.tracert_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.tracert_frame, text='Traceroute')
        
        # Frame untuk Logs
        self.logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.logs_frame, text='Logs')
        
        # Frame untuk Hasil
        self.results_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.results_frame, text='Hasil Ping')
        
        # Setup Ping Load tab
        self.setup_ping_tab()
        
        # Setup Traceroute tab
        self.setup_tracert_tab()
        
        # Setup Logs tab
        self.setup_logs_tab()
        
        # Setup Results tab
        self.setup_results_tab()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Timer real-time
        self.timer_var = tk.StringVar()
        self.update_timer()
        
        # Terapkan tema default
        self.apply_theme(self.current_theme)
        
    def create_menu(self):
        # Buat menu bar
        menubar = Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Start
        start_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Start", menu=start_menu)
        start_menu.add_command(label="Start Ping", command=self.start_ping)
        start_menu.add_command(label="Start Traceroute", command=self.start_tracert)
        
        # Menu Stop
        stop_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Stop", menu=stop_menu)
        stop_menu.add_command(label="Stop Ping", command=self.stop_ping)
        stop_menu.add_command(label="Stop Traceroute", command=self.stop_tracert)
        
        # Menu Logs
        logs_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Logs", menu=logs_menu)
        logs_menu.add_command(label="View Logs", command=self.show_logs)
        logs_menu.add_command(label="Clear Logs", command=self.clear_logs)
        logs_menu.add_command(label="Save Logs", command=self.save_logs)
        
        # Menu Theme
        theme_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Theme", menu=theme_menu)
        theme_menu.add_command(label="Default", command=lambda: self.apply_theme("Default"))
        theme_menu.add_command(label="Dark", command=lambda: self.apply_theme("Dark"))
        theme_menu.add_command(label="Blue", command=lambda: self.apply_theme("Blue"))
        theme_menu.add_command(label="Green", command=lambda: self.apply_theme("Green"))
        theme_menu.add_command(label="Red", command=lambda: self.apply_theme("Red"))
        
        # Menu Help
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
    def apply_theme(self, theme_name):
        self.current_theme = theme_name
        theme = self.themes[theme_name]
        
        # Terapkan warna ke widget
        self.root.configure(bg=theme["bg"])
        
        # Widget yang perlu diubah warna latar dan teks
        widgets = [
            self.ping_frame, self.tracert_frame, self.logs_frame, self.results_frame,
            self.ping_output, self.tracert_output, self.logs_text, self.results_text
        ]
        
        for widget in widgets:
            try:
                widget.configure(bg=theme["bg"], fg=theme["fg"])
            except:
                pass
        
        # Status bar
        self.status_bar.configure(background=theme["bg"], foreground=theme["fg"])
        
        self.log_message(f"Theme changed to {theme_name}")
        
    def show_about(self):
        about_text = "Network Diagnostic Tool\n\n" \
                    "Aplikasi untuk melakukan ping load dan traceroute\n" \
                    "dengan berbagai fitur dan tema warna."
        messagebox.showinfo("About", about_text)
        
    def show_logs(self):
        self.notebook.select(self.logs_frame)
        
    def setup_ping_tab(self):
        # Target host
        ttk.Label(self.ping_frame, text="Target Host:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.host_var = tk.StringVar(value="google.com")
        ttk.Entry(self.ping_frame, textvariable=self.host_var, width=30).grid(row=0, column=1, padx=5, pady=5)
        
        # Packet size range (32-1024 kbps)
        ttk.Label(self.ping_frame, text="Packet Size (32-1024 bytes):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.packet_size_var = tk.IntVar(value=64)
        ttk.Spinbox(self.ping_frame, from_=32, to=1024, textvariable=self.packet_size_var, width=10).grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Duration (1-199 menit)
        ttk.Label(self.ping_frame, text="Duration (1-199 minutes):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.duration_var = tk.IntVar(value=5)
        ttk.Spinbox(self.ping_frame, from_=1, to=199, textvariable=self.duration_var, width=10).grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Interval (1-1500 ms)
        ttk.Label(self.ping_frame, text="Interval (1-1500 ms):").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.interval_var = tk.IntVar(value=1000)
        ttk.Spinbox(self.ping_frame, from_=1, to=1500, textvariable=self.interval_var, width=10).grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Timer options
        ttk.Label(self.ping_frame, text="Timer:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.timer_frame = ttk.Frame(self.ping_frame)
        self.timer_frame.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(self.timer_frame, textvariable=self.timer_var).pack(side=tk.LEFT)
        ttk.Button(self.timer_frame, text="+3", command=lambda: self.add_to_timer(3)).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.timer_frame, text="+7", command=lambda: self.add_to_timer(7)).pack(side=tk.LEFT, padx=2)
        
        # Buttons
        self.button_frame = ttk.Frame(self.ping_frame)
        self.button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        self.start_btn = ttk.Button(self.button_frame, text="Start Ping", command=self.start_ping)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(self.button_frame, text="Stop Ping", command=self.stop_ping, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Ping output
        ttk.Label(self.ping_frame, text="Ping Output:").grid(row=6, column=0, padx=5, pady=5, sticky=tk.W)
        self.ping_output = scrolledtext.ScrolledText(self.ping_frame, width=70, height=15)
        self.ping_output.grid(row=7, column=0, columnspan=2, padx=5, pady=5)
        
    def setup_tracert_tab(self):
        # Target host for traceroute
        ttk.Label(self.tracert_frame, text="Target Host:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.tracert_host_var = tk.StringVar(value="google.com")
        ttk.Entry(self.tracert_frame, textvariable=self.tracert_host_var, width=30).grid(row=0, column=1, padx=5, pady=5)
        
        # Buttons
        self.tracert_button_frame = ttk.Frame(self.tracert_frame)
        self.tracert_button_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        self.tracert_start_btn = ttk.Button(self.tracert_button_frame, text="Start Traceroute", command=self.start_tracert)
        self.tracert_start_btn.pack(side=tk.LEFT, padx=5)
        
        self.tracert_stop_btn = ttk.Button(self.tracert_button_frame, text="Stop Traceroute", command=self.stop_tracert, state=tk.DISABLED)
        self.tracert_stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Traceroute output
        ttk.Label(self.tracert_frame, text="Traceroute Output:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.tracert_output = scrolledtext.ScrolledText(self.tracert_frame, width=70, height=15)
        self.tracert_output.grid(row=3, column=0, columnspan=2, padx=5, pady=5)
        
    def setup_logs_tab(self):
        # Logs display
        ttk.Label(self.logs_frame, text="Activity Logs:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.logs_text = scrolledtext.ScrolledText(self.logs_frame, width=70, height=20)
        self.logs_text.grid(row=1, column=0, padx=5, pady=5, sticky=tk.NSEW)
        
        # Buttons
        self.logs_button_frame = ttk.Frame(self.logs_frame)
        self.logs_button_frame.grid(row=2, column=0, pady=10)
        
        ttk.Button(self.logs_button_frame, text="Clear Logs", command=self.clear_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.logs_button_frame, text="Save Logs", command=self.save_logs).pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        self.logs_frame.grid_rowconfigure(1, weight=1)
        self.logs_frame.grid_columnconfigure(0, weight=1)
        
    def setup_results_tab(self):
        # Results display
        ttk.Label(self.results_frame, text="Ping Results Summary:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.results_text = scrolledtext.ScrolledText(self.results_frame, width=70, height=20)
        self.results_text.grid(row=1, column=0, padx=5, pady=5, sticky=tk.NSEW)
        
        # Buttons
        self.results_button_frame = ttk.Frame(self.results_frame)
        self.results_button_frame.grid(row=2, column=0, pady=10)
        
        ttk.Button(self.results_button_frame, text="Clear Results", command=self.clear_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.results_button_frame, text="Save Results", command=self.save_results).pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        self.results_frame.grid_rowconfigure(1, weight=1)
        self.results_frame.grid_columnconfigure(0, weight=1)
        
    def update_timer(self):
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        self.timer_var.set(current_time)
        self.root.after(1000, self.update_timer)
        
    def add_to_timer(self, minutes):
        try:
            current = datetime.datetime.now()
            new_time = current + datetime.timedelta(minutes=minutes)
            messagebox.showinfo("Timer", f"Timer set: {current.strftime('%H:%M:%S')} + {minutes} min = {new_time.strftime('%H:%M:%S')}")
        except Exception as e:
            self.log_message(f"Error setting timer: {str(e)}")
            
    def log_message(self, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_content += log_entry
        self.logs_text.insert(tk.END, log_entry)
        self.logs_text.see(tk.END)
        self.status_var.set(message)
        
    def start_ping(self):
        host = self.host_var.get()
        if not host:
            messagebox.showerror("Error", "Please enter a target host")
            return
            
        packet_size = self.packet_size_var.get()
        duration = self.duration_var.get()
        interval = self.interval_var.get()
        
        self.is_pinging = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        self.ping_output.delete(1.0, tk.END)
        self.log_message(f"Starting ping to {host} with packet size {packet_size} bytes, duration {duration} min, interval {interval} ms")
        
        # Start ping in a separate thread
        ping_thread = threading.Thread(target=self.run_ping, args=(host, packet_size, duration, interval))
        ping_thread.daemon = True
        ping_thread.start()
        
    def stop_ping(self):
        self.is_pinging = False
        if self.ping_process:
            try:
                self.ping_process.terminate()
            except:
                pass
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.log_message("Ping stopped by user")
        
    def run_ping(self, host, packet_size, duration, interval):
        try:
            # Calculate count based on duration and interval
            count = int((duration * 60 * 1000) / interval)
            if count <= 0:
                count = 10  # Default to 10 packets if calculation fails
                
            # Determine ping command based on OS
            if sys.platform.startswith('win'):
                cmd = ['ping', '-n', str(count), '-l', str(packet_size), '-w', str(interval), host]
            else:
                cmd = ['ping', '-c', str(count), '-s', str(packet_size), '-i', str(interval/1000), host]
                
            self.ping_process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1
            )
            
            # Read output in real-time
            for line in iter(self.ping_process.stdout.readline, ''):
                if not self.is_pinging:
                    break
                self.ping_output.insert(tk.END, line)
                self.ping_output.see(tk.END)
                self.root.update_idletasks()
                
            # Wait for process to complete
            self.ping_process.wait()
            
            # Process completed
            if self.is_pinging:
                self.root.after(0, self.ping_completed)
                
        except Exception as e:
            self.root.after(0, lambda: self.log_message(f"Ping error: {str(e)}"))
            self.root.after(0, self.ping_completed)
            
    def ping_completed(self):
        self.is_pinging = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.log_message("Ping completed")
        
        # Extract and display summary in results tab
        output = self.ping_output.get(1.0, tk.END)
        self.process_ping_results(output)
        
    def process_ping_results(self, output):
        # Simple parsing of ping results
        lines = output.split('\n')
        summary = "Ping Results Summary:\n\n"
        
        # Extract relevant information
        for line in lines:
            if "bytes from" in line or "Reply from" in line:
                summary += line + "\n"
            elif "packet loss" in line or "Packet loss" in line:
                summary += f"\nPacket Loss: {line}\n"
            elif "Minimum" in line or "min/avg/max" in line:
                summary += f"Statistics: {line}\n"
                
        # Add timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        summary = f"Test performed at: {timestamp}\n" + summary
        
        # Display in results tab
        self.results_text.insert(tk.END, summary + "\n" + "="*50 + "\n\n")
        self.results_text.see(tk.END)
        
    def start_tracert(self):
        host = self.tracert_host_var.get()
        if not host:
            messagebox.showerror("Error", "Please enter a target host")
            return
            
        self.is_tracerting = True
        self.tracert_start_btn.config(state=tk.DISABLED)
        self.tracert_stop_btn.config(state=tk.NORMAL)
        
        self.tracert_output.delete(1.0, tk.END)
        self.log_message(f"Starting traceroute to {host}")
        
        # Start traceroute in a separate thread
        tracert_thread = threading.Thread(target=self.run_tracert, args=(host,))
        tracert_thread.daemon = True
        tracert_thread.start()
        
    def stop_tracert(self):
        self.is_tracerting = False
        if self.tracert_process:
            try:
                self.tracert_process.terminate()
            except:
                pass
        self.tracert_start_btn.config(state=tk.NORMAL)
        self.tracert_stop_btn.config(state=tk.DISABLED)
        self.log_message("Traceroute stopped by user")
        
    def run_tracert(self, host):
        try:
            # Determine traceroute command based on OS
            if sys.platform.startswith('win'):
                cmd = ['tracert', host]
            else:
                cmd = ['traceroute', host]
                
            self.tracert_process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1
            )
            
            # Read output in real-time
            for line in iter(self.tracert_process.stdout.readline, ''):
                if not self.is_tracerting:
                    break
                self.tracert_output.insert(tk.END, line)
                self.tracert_output.see(tk.END)
                self.root.update_idletasks()
                
            # Wait for process to complete
            self.tracert_process.wait()
            
            # Process completed
            if self.is_tracerting:
                self.root.after(0, self.tracert_completed)
                
        except Exception as e:
            self.root.after(0, lambda: self.log_message(f"Traceroute error: {str(e)}"))
            self.root.after(0, self.tracert_completed)
            
    def tracert_completed(self):
        self.is_tracerting = False
        self.tracert_start_btn.config(state=tk.NORMAL)
        self.tracert_stop_btn.config(state=tk.DISABLED)
        self.log_message("Traceroute completed")
        
    def clear_logs(self):
        self.logs_text.delete(1.0, tk.END)
        self.log_content = ""
        self.log_message("Logs cleared")
        
    def save_logs(self):
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"network_logs_{timestamp}.txt"
            with open(filename, 'w') as f:
                f.write(self.log_content)
            self.log_message(f"Logs saved to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save logs: {str(e)}")
            
    def clear_results(self):
        self.results_text.delete(1.0, tk.END)
        self.log_message("Results cleared")
        
    def save_results(self):
        try:
            results = self.results_text.get(1.0, tk.END)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ping_results_{timestamp}.txt"
            with open(filename, 'w') as f:
                f.write(results)
            self.log_message(f"Results saved to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save results: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkDiagnosticTool(root)
    root.mainloop()