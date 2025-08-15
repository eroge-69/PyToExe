import os
import hashlib
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import smtplib
from datetime import datetime
import shutil
import threading

class AntivirusApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Antivirus")
        self.root.geometry("900x600")
        
        # Configuration files
        self.config_file = "antivirus_config.json"
        self.signatures_file = "signatures.json"
        self.quarantine_dir = "Quarantine"
        
        # Initialize components
        self.load_config()
        self.load_signatures()
        self.setup_ui()
        
        # Scan control
        self.scan_running = False
        self.scan_thread = None
        
    def load_config(self):
        """Load or create configuration"""
        default_config = {
            "email_notifications": False,
            "email_sender": "",
            "email_password": "",
            "email_recipient": "",
            "scan_history": []
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    self.config = json.load(f)
            else:
                self.config = default_config
                self.save_config()
        except:
            self.config = default_config
    
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=4)
    
    def load_signatures(self):
        """Load virus signatures"""
        default_signatures = {
            "d41d8cd98f00b204e9800998ecf8427e": "EmptyFile.Virus",
            "5d41402abc4b2a76b9719d911017c592": "Example.Worm"
        }
        
        try:
            if os.path.exists(self.signatures_file):
                with open(self.signatures_file, "r") as f:
                    self.signatures = json.load(f)
            else:
                self.signatures = default_signatures
                self.save_signatures()
        except:
            self.signatures = default_signatures
    
    def save_signatures(self):
        """Save signatures to file"""
        with open(self.signatures_file, "w") as f:
            json.dump(self.signatures, f, indent=4)
    
    def setup_ui(self):
        """Set up the user interface"""
        # Create tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Scan tab
        self.setup_scan_tab()
        
        # Quarantine tab
        self.setup_quarantine_tab()
        
        # Settings tab
        self.setup_settings_tab()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN).pack(fill=tk.X)
    
    def setup_scan_tab(self):
        """Set up the scan tab"""
        scan_tab = ttk.Frame(self.notebook)
        self.notebook.add(scan_tab, text="Scan")
        
        # Scan location
        frame = ttk.LabelFrame(scan_tab, text="Scan Location", padding=10)
        frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.scan_path = tk.StringVar(value=os.getcwd())
        ttk.Entry(frame, textvariable=self.scan_path).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(frame, text="Browse", command=self.browse_scan_path).pack(side=tk.LEFT)
        
        # Scan options
        frame = ttk.LabelFrame(scan_tab, text="Scan Options", padding=10)
        frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.scan_type = tk.StringVar(value="quick")
        ttk.Radiobutton(frame, text="Quick Scan", variable=self.scan_type, value="quick").pack(anchor=tk.W)
        ttk.Radiobutton(frame, text="Full Scan", variable=self.scan_type, value="full").pack(anchor=tk.W)
        
        # Action buttons
        frame = ttk.Frame(scan_tab)
        frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(frame, text="Start Scan", command=self.start_scan).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame, text="Stop Scan", command=self.stop_scan).pack(side=tk.LEFT, padx=5)
        
        # Results
        frame = ttk.LabelFrame(scan_tab, text="Scan Results", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.results_tree = ttk.Treeview(frame, columns=("file", "threat", "action"), show="headings")
        self.results_tree.heading("file", text="File")
        self.results_tree.heading("threat", text="Threat")
        self.results_tree.heading("action", text="Action")
        
        scroll_y = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        scroll_x = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        
        self.results_tree.grid(row=0, column=0, sticky=tk.NSEW)
        scroll_y.grid(row=0, column=1, sticky=tk.NS)
        scroll_x.grid(row=1, column=0, sticky=tk.EW)
        
        # Action buttons for results
        frame = ttk.Frame(scan_tab)
        frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(frame, text="Quarantine", command=self.quarantine_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame, text="Delete", command=self.delete_selected).pack(side=tk.LEFT, padx=5)
    
    def setup_quarantine_tab(self):
        """Set up the quarantine tab"""
        quarantine_tab = ttk.Frame(self.notebook)
        self.notebook.add(quarantine_tab, text="Quarantine")
        
        # Ensure quarantine directory exists
        os.makedirs(self.quarantine_dir, exist_ok=True)
        
        # Quarantine list
        frame = ttk.LabelFrame(quarantine_tab, text="Quarantined Files", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.quarantine_tree = ttk.Treeview(frame, columns=("file", "original"), show="headings")
        self.quarantine_tree.heading("file", text="File")
        self.quarantine_tree.heading("original", text="Original Location")
        
        scroll_y = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.quarantine_tree.yview)
        scroll_x = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=self.quarantine_tree.xview)
        self.quarantine_tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        
        self.quarantine_tree.grid(row=0, column=0, sticky=tk.NSEW)
        scroll_y.grid(row=0, column=1, sticky=tk.NS)
        scroll_x.grid(row=1, column=0, sticky=tk.EW)
        
        # Action buttons
        frame = ttk.Frame(quarantine_tab)
        frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(frame, text="Restore", command=self.restore_quarantined).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame, text="Delete", command=self.delete_quarantined).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame, text="Refresh", command=self.refresh_quarantine).pack(side=tk.LEFT, padx=5)
        
        # Load quarantined files
        self.refresh_quarantine()
    
    def setup_settings_tab(self):
        """Set up the settings tab"""
        settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(settings_tab, text="Settings")
        
        # Email notifications
        frame = ttk.LabelFrame(settings_tab, text="Email Notifications", padding=10)
        frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.email_notify = tk.BooleanVar(value=self.config["email_notifications"])
        ttk.Checkbutton(frame, text="Enable email notifications", variable=self.email_notify, 
                       command=self.toggle_email_notify).pack(anchor=tk.W)
        
        ttk.Label(frame, text="Sender Email:").pack(anchor=tk.W)
        self.email_sender = ttk.Entry(frame)
        self.email_sender.insert(0, self.config["email_sender"])
        self.email_sender.pack(fill=tk.X, pady=2)
        
        ttk.Label(frame, text="Password:").pack(anchor=tk.W)
        self.email_pass = ttk.Entry(frame, show="*")
        self.email_pass.insert(0, self.config["email_password"])
        self.email_pass.pack(fill=tk.X, pady=2)
        
        ttk.Label(frame, text="Recipient:").pack(anchor=tk.W)
        self.email_recipient = ttk.Entry(frame)
        self.email_recipient.insert(0, self.config["email_recipient"])
        self.email_recipient.pack(fill=tk.X, pady=2)
        
        ttk.Button(frame, text="Save Email Settings", command=self.save_email_settings).pack(pady=5)
    
    def browse_scan_path(self):
        """Browse for scan path"""
        path = filedialog.askdirectory()
        if path:
            self.scan_path.set(path)
    
    def start_scan(self):
        """Start scanning files"""
        if self.scan_running:
            return
        
        # Clear previous results
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        self.scan_running = True
        self.status_var.set("Scanning...")
        
        # Start scan in background thread
        self.scan_thread = threading.Thread(target=self.run_scan, daemon=True)
        self.scan_thread.start()
    
    def run_scan(self):
        """Perform the actual scan"""
        scan_path = self.scan_path.get()
        scan_type = self.scan_type.get()
        
        try:
            if scan_type == "quick":
                # Scan common locations
                paths_to_scan = [
                    os.path.join(os.environ["USERPROFILE"], "Downloads"),
                    os.path.join(os.environ["USERPROFILE"], "Desktop"),
                    os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
                ]
            else:
                # Full scan of selected path
                paths_to_scan = [scan_path]
            
            for path in paths_to_scan:
                if os.path.exists(path):
                    self.scan_directory(path)
        
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
        
        finally:
            self.scan_running = False
            self.status_var.set("Scan complete")
    
    def scan_directory(self, directory):
        """Scan a directory for infected files"""
        for root, _, files in os.walk(directory):
            for file in files:
                if not self.scan_running:
                    return
                
                file_path = os.path.join(root, file)
                
                try:
                    # Skip large files (>10MB)
                    if os.path.getsize(file_path) > 10 * 1024 * 1024:
                        continue
                    
                    # Calculate file hash
                    with open(file_path, "rb") as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                    
                    # Check against signatures
                    if file_hash in self.signatures:
                        threat = self.signatures[file_hash]
                        self.results_tree.insert("", tk.END, values=(file_path, threat, "Pending"))
                
                except:
                    continue
    
    def stop_scan(self):
        """Stop the running scan"""
        if self.scan_running:
            self.scan_running = False
            self.status_var.set("Scan stopped")
    
    def quarantine_selected(self):
        """Quarantine selected files"""
        selected = self.results_tree.selection()
        if not selected:
            return
        
        for item in selected:
            file_path = self.results_tree.item(item, "values")[0]
            threat = self.results_tree.item(item, "values")[1]
            
            try:
                # Move file to quarantine
                filename = os.path.basename(file_path)
                quarantine_path = os.path.join(self.quarantine_dir, filename)
                
                # Handle duplicates
                counter = 1
                while os.path.exists(quarantine_path):
                    name, ext = os.path.splitext(filename)
                    quarantine_path = os.path.join(self.quarantine_dir, f"{name}_{counter}{ext}")
                    counter += 1
                
                shutil.move(file_path, quarantine_path)
                self.results_tree.set(item, "action", "Quarantined")
                
                # Add to quarantine list
                self.quarantine_tree.insert("", tk.END, values=(os.path.basename(quarantine_path), file_path))
            
            except Exception as e:
                messagebox.showerror("Error", f"Failed to quarantine: {str(e)}")
    
    def delete_selected(self):
        """Delete selected files"""
        selected = self.results_tree.selection()
        if not selected or not messagebox.askyesno("Confirm", "Permanently delete selected files?"):
            return
        
        for item in selected:
            file_path = self.results_tree.item(item, "values")[0]
            try:
                os.remove(file_path)
                self.results_tree.set(item, "action", "Deleted")
            except:
                pass
    
    def refresh_quarantine(self):
        """Refresh quarantine list"""
        for item in self.quarantine_tree.get_children():
            self.quarantine_tree.delete(item)
        
        if os.path.exists(self.quarantine_dir):
            for filename in os.listdir(self.quarantine_dir):
                file_path = os.path.join(self.quarantine_dir, filename)
                if os.path.isfile(file_path):
                    # Try to get original path from metadata
                    original = "Unknown"
                    meta_file = os.path.join(self.quarantine_dir, "metadata.json")
                    if os.path.exists(meta_file):
                        try:
                            with open(meta_file, "r") as f:
                                meta = json.load(f)
                                original = meta.get(filename, {}).get("original", "Unknown")
                        except:
                            pass
                    
                    self.quarantine_tree.insert("", tk.END, values=(filename, original))
    
    def restore_quarantined(self):
        """Restore quarantined files"""
        selected = self.quarantine_tree.selection()
        if not selected:
            return
        
        for item in selected:
            filename = self.quarantine_tree.item(item, "values")[0]
            original = self.quarantine_tree.item(item, "values")[1]
            
            if original == "Unknown":
                original = filedialog.asksaveasfilename(initialfile=filename)
                if not original:
                    continue
            
            try:
                shutil.move(
                    os.path.join(self.quarantine_dir, filename),
                    original
                )
                self.quarantine_tree.delete(item)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to restore: {str(e)}")
    
    def delete_quarantined(self):
        """Delete quarantined files"""
        selected = self.quarantine_tree.selection()
        if not selected or not messagebox.askyesno("Confirm", "Permanently delete selected quarantined files?"):
            return
        
        for item in selected:
            filename = self.quarantine_tree.item(item, "values")[0]
            try:
                os.remove(os.path.join(self.quarantine_dir, filename))
                self.quarantine_tree.delete(item)
            except:
                pass
    
    def toggle_email_notify(self):
        """Toggle email notifications"""
        self.config["email_notifications"] = self.email_notify.get()
        self.save_config()
    
    def save_email_settings(self):
        """Save email settings"""
        self.config["email_sender"] = self.email_sender.get()
        self.config["email_password"] = self.email_pass.get()
        self.config["email_recipient"] = self.email_recipient.get()
        self.save_config()
        messagebox.showinfo("Success", "Email settings saved")

def main():
    root = tk.Tk()
    app = AntivirusApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()