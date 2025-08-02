import tkinter as tk
from tkinter import ttk, messagebox
import speedtest
import threading
from time import sleep

class SpeedTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Internet Speed Test (MBps)")
        self.root.geometry("500x400")
        self.root.minsize(450, 350)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Set style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.create_widgets()
        
        # Initialize speedtest
        self.st = speedtest.Speedtest()
        self.test_in_progress = False
        
    def create_widgets(self):
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.columnconfigure(0, weight=1)
        
        # Title
        self.title_label = ttk.Label(
            self.main_frame, 
            text="Internet Speed Test (MBps)", 
            font=('Helvetica', 16, 'bold')
        )
        self.title_label.grid(row=0, column=0, pady=10, sticky="n")
        
        # Server selection
        self.server_frame = ttk.LabelFrame(self.main_frame, text="Server Selection", padding=10)
        self.server_frame.grid(row=1, column=0, sticky="ew", pady=5)
        self.server_frame.columnconfigure(1, weight=1)
        
        self.server_label = ttk.Label(self.server_frame, text="Best server by distance:")
        self.server_label.grid(row=0, column=0, sticky="w")
        
        self.server_button = ttk.Button(
            self.server_frame, 
            text="Find Server", 
            command=self.find_best_server
        )
        self.server_button.grid(row=0, column=1, sticky="e")
        
        self.server_var = tk.StringVar()
        self.server_display = ttk.Label(self.server_frame, textvariable=self.server_var, wraplength=350)
        self.server_display.grid(row=1, column=0, columnspan=2, sticky="w", pady=5)
        
        # Test buttons
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.grid(row=2, column=0, sticky="ew", pady=10)
        
        self.download_button = ttk.Button(
            self.button_frame, 
            text="Download", 
            command=lambda: self.run_test("download")
        )
        self.download_button.pack(side=tk.LEFT, expand=True, padx=5)
        
        self.upload_button = ttk.Button(
            self.button_frame, 
            text="Upload", 
            command=lambda: self.run_test("upload")
        )
        self.upload_button.pack(side=tk.LEFT, expand=True, padx=5)
        
        self.full_test_button = ttk.Button(
            self.button_frame, 
            text="Full Test", 
            command=lambda: self.run_test("full")
        )
        self.full_test_button.pack(side=tk.LEFT, expand=True, padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(
            self.main_frame, 
            orient=tk.HORIZONTAL, 
            mode='determinate'
        )
        self.progress.grid(row=3, column=0, sticky="ew", pady=10)
        
        # Results display
        self.results_frame = ttk.LabelFrame(self.main_frame, text="Test Results (MBps)", padding=10)
        self.results_frame.grid(row=4, column=0, sticky="nsew", pady=5)
        self.results_frame.columnconfigure(0, weight=1)
        
        self.download_var = tk.StringVar(value="Download: -- MB/s")
        self.download_result = ttk.Label(
            self.results_frame, 
            textvariable=self.download_var,
            font=('Helvetica', 12)
        )
        self.download_result.grid(row=0, column=0, sticky="w", pady=2)
        
        self.upload_var = tk.StringVar(value="Upload: -- MB/s")
        self.upload_result = ttk.Label(
            self.results_frame, 
            textvariable=self.upload_var,
            font=('Helvetica', 12)
        )
        self.upload_result.grid(row=1, column=0, sticky="w", pady=2)
        
        self.ping_var = tk.StringVar(value="Ping: -- ms")
        self.ping_result = ttk.Label(
            self.results_frame, 
            textvariable=self.ping_var,
            font=('Helvetica', 12)
        )
        self.ping_result.grid(row=2, column=0, sticky="w", pady=2)
        
        # Configure grid weights for resizing
        self.main_frame.rowconfigure(4, weight=1)
        
    def find_best_server(self):
        def find_server():
            self.server_button.config(state=tk.DISABLED)
            self.server_var.set("Searching for best server...")
            
            try:
                self.st.get_best_server()
                server = self.st.best
                self.server_var.set(f"Server: {server['name']} ({server['country']}) - Distance: {server['d']:.2f} km")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to find server: {str(e)}")
                self.server_var.set("Server: Not found")
            finally:
                self.server_button.config(state=tk.NORMAL)
        
        threading.Thread(target=find_server, daemon=True).start()
    
    def run_test(self, test_type):
        if self.test_in_progress:
            messagebox.showwarning("Warning", "A test is already in progress")
            return
            
        self.test_in_progress = True
        self.progress['value'] = 0
        
        def perform_test():
            try:
                if test_type in ["download", "full"]:
                    self.download_var.set("Download: Testing...")
                    self.root.update()
                    
                    for i in range(10, 110, 10):
                        self.progress['value'] = i if test_type == "download" else i/2
                        self.root.update()
                        sleep(0.1)
                    
                    # Convert from bits to Megabytes (divide by 8, then by 1,000,000)
                    download_speed = self.st.download() / 8_000_000
                    self.download_var.set(f"Download: {download_speed:.2f} MB/s")
                    self.progress['value'] = 100 if test_type == "download" else 50
                
                if test_type in ["upload", "full"]:
                    self.upload_var.set("Upload: Testing...")
                    self.root.update()
                    
                    start = 0 if test_type == "upload" else 50
                    for i in range(start + 10, 110, 10):
                        self.progress['value'] = i
                        self.root.update()
                        sleep(0.1)
                    
                    # Convert from bits to Megabytes (divide by 8, then by 1,000,000)
                    upload_speed = self.st.upload() / 8_000_000
                    self.upload_var.set(f"Upload: {upload_speed:.2f} MB/s")
                    self.progress['value'] = 100
                
                if test_type == "full":
                    self.ping_var.set("Ping: Testing...")
                    self.root.update()
                    ping = self.st.results.ping
                    self.ping_var.set(f"Ping: {ping:.2f} ms")
                
            except Exception as e:
                messagebox.showerror("Error", f"Speed test failed: {str(e)}")
            finally:
                self.test_in_progress = False
        
        threading.Thread(target=perform_test, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = SpeedTestApp(root)
    root.mainloop()