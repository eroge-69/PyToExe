import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import random
import requests
import dns.resolver

class TrafficGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Privacy Traffic Generator")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Control variables
        self.is_running = False
        self.thread = None
        
        # Configure style
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))
        self.style.configure("TButton", font=("Arial", 10))
        self.style.configure("Title.TLabel", font=("Arial", 14, "bold"))
        
        # Create widgets
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(main_frame, text="Privacy Traffic Generator", style="Title.TLabel")
        title.pack(pady=10)
        
        # Description
        desc = ttk.Label(main_frame, 
                         text="Generates background HTTP/DNS traffic to obscure\n your real browsing activity. Use responsibly.",
                         justify=tk.CENTER)
        desc.pack(pady=10)
        
        # Controls frame
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(pady=20, fill=tk.X)
        
        # Intensity control
        ttk.Label(controls_frame, text="Traffic Intensity:").grid(row=0, column=0, sticky=tk.W)
        self.intensity = ttk.Combobox(controls_frame, values=["Low", "Medium", "High"], width=10)
        self.intensity.grid(row=0, column=1, padx=5)
        self.intensity.set("Medium")
        
        # Button frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)
        
        # Buttons
        self.start_btn = ttk.Button(btn_frame, text="Start", command=self.start_traffic, width=10)
        self.start_btn.pack(side=tk.LEFT, padx=10)
        
        self.stop_btn = ttk.Button(btn_frame, text="Stop", command=self.stop_traffic, state=tk.DISABLED, width=10)
        self.stop_btn.pack(side=tk.LEFT, padx=10)
        
        # Status bar
        self.status = ttk.Label(main_frame, text="Status: Stopped", foreground="red")
        self.status.pack(pady=10)
        
        # Activity log
        self.log = tk.Text(main_frame, height=5, width=50, state=tk.DISABLED)
        self.log.pack(pady=5)
        self.log.tag_config("success", foreground="green")
        self.log.tag_config("error", foreground="red")
    
    def log_message(self, message, tags=()):
        self.log.config(state=tk.NORMAL)
        self.log.insert(tk.END, message + "\n", tags)
        self.log.see(tk.END)
        self.log.config(state=tk.DISABLED)
    
    def generate_traffic(self):
        domains = [
            "google.com", "youtube.com", "facebook.com", "amazon.com", "twitter.com",
            "wikipedia.org", "reddit.com", "instagram.com", "linkedin.com", "microsoft.com"
        ]
        
        # Map intensity to request intervals (seconds)
        intensity_map = {"Low": 20, "Medium": 10, "High": 5}
        interval = intensity_map[self.intensity.get()]
        
        self.log_message("Starting traffic generation...")
        
        while self.is_running:
            try:
                domain = random.choice(domains)
                # Randomly choose between HTTP and DNS
                if random.random() > 0.3:
                    # HTTP request
                    url = f"https://{domain}"
                    response = requests.get(url, timeout=5)
                    self.log_message(f"HTTP: {url} → Status {response.status_code}", "success")
                else:
                    # DNS query
                    resolver = dns.resolver.Resolver()
                    resolver.resolve(domain, 'A')
                    self.log_message(f"DNS: Resolved {domain}", "success")
                
                # Add some randomness to interval
                sleep_time = interval * (0.8 + random.random() * 0.4)
                time.sleep(sleep_time)
                
            except Exception as e:
                error_msg = str(e).split("\n")[0]
                self.log_message(f"Error: {error_msg}", "error")
                time.sleep(5)
    
    def start_traffic(self):
        if not self.is_running:
            self.is_running = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.status.config(text="Status: Running", foreground="green")
            self.log.delete(1.0, tk.END)
            
            # Start traffic generation in separate thread
            self.thread = threading.Thread(target=self.generate_traffic, daemon=True)
            self.thread.start()
    
    def stop_traffic(self):
        if self.is_running:
            self.is_running = False
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.status.config(text="Status: Stopped", foreground="red")
            self.log_message("Traffic generation stopped")

if __name__ == "__main__":
    root = tk.Tk()
    app = TrafficGeneratorApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.stop_traffic(), root.destroy()))
    root.mainloop()