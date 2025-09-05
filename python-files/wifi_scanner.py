import socket
import subprocess
import platform
from datetime import datetime
import ipaddress
from concurrent.futures import ThreadPoolExecutor, as_completed
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from tkinter.font import Font
import threading
import queue
import re

def get_network_info():
    """Get the local IP address and network mask to determine the network range."""
    try:
        # Create a socket to get the local IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't need to be reachable
            s.connect(('10.255.255.255', 1))
            ip = s.getsockname()[0]
        except Exception:
            ip = '127.0.0.1'
        finally:
            s.close()
        
        # Get the network interface information using ipconfig/ifconfig
        if platform.system() == 'Windows':
            # Windows
            process = subprocess.Popen('ipconfig', stdout=subprocess.PIPE)
            output = process.communicate()[0].decode('utf-8', 'ignore')
            
            # Find the network interface that matches our IP
            interface_section = None
            for section in output.split('\n\n'):
                if f'IPv4 Address. . . . . . . . . . . : {ip}' in section:
                    interface_section = section
                    break
            
            if interface_section:
                # Extract subnet mask
                subnet_mask = '255.255.255.0'  # Default fallback
                for line in interface_section.split('\n'):
                    if 'Subnet Mask' in line:
                        subnet_mask = line.split(':')[-1].strip()
                        break
                
                # Calculate network information
                network = ipaddress.IPv4Network(f"{ip}/{subnet_mask}", strict=False)
                return str(ip), str(network.network_address), str(network.netmask), network.hosts()
        else:
            # Linux/Mac
            process = subprocess.Popen(['ifconfig'], stdout=subprocess.PIPE)
            output = process.communicate()[0].decode('utf-8', 'ignore')
            
            # Find the network interface that matches our IP
            interface_section = None
            for section in output.split('\n\n'):
                if f'inet {ip}' in section or f'inet addr:{ip}' in section:
                    interface_section = section
                    break
            
            if interface_section:
                # Extract subnet mask
                subnet_mask = '255.255.255.0'  # Default fallback
                mask_match = re.search(r'netmask\s+([0-9.]+)', interface_section)
                if mask_match:
                    subnet_mask = mask_match.group(1)
                
                # Calculate network information
                network = ipaddress.IPv4Network(f"{ip}/{subnet_mask}", strict=False)
                return str(ip), str(network.network_address), str(network.netmask), network.hosts()
        
        # Fallback to default network if specific interface not found
        network = ipaddress.IPv4Network(f"{ip}/24", strict=False)
        return str(ip), str(network.network_address), str(network.netmask), network.hosts()
        
    except Exception as e:
        print(f"Error getting network info: {e}")
        # Fallback to default values
        try:
            ip = socket.gethostbyname(socket.gethostname())
            if ip.startswith('127.'):
                # If we get localhost, try to get a non-loopback address
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                try:
                    s.connect(('8.8.8.8', 80))
                    ip = s.getsockname()[0]
                finally:
                    s.close()
            
            network = ipaddress.IPv4Network(f"{ip}/24", strict=False)
            return str(ip), str(network.network_address), str(network.netmask), network.hosts()
        except:
            return None, None, None, None

def get_hostname(ip):
    """Get the hostname for a given IP address."""
    try:
        hostname = socket.gethostbyaddr(ip)[0]
        return hostname
    except (socket.herror, socket.gaierror):
        return "Unknown"
    except Exception as e:
        print(f"Error getting hostname for {ip}: {e}")
        return "Error"

def ping_host(ip):
    """Ping a host to check if it's alive."""
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', '-w', '500', ip]
    try:
        return subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0
    except Exception as e:
        print(f"Error pinging {ip}: {e}")
        return False

def scan_network():
    """Scan the network for active devices."""
    my_ip, network_addr, netmask, hosts = get_network_info()
    
    if not all([my_ip, network_addr, netmask, hosts]):
        print("Failed to get network information. Make sure you're connected to a network.")
        return []
    
    print(f"Scanning network: {network_addr} {netmask}")
    print("This might take a while...")
    
    active_hosts = []
    
    # Use ThreadPoolExecutor to speed up the scanning process
    with ThreadPoolExecutor(max_workers=100) as executor:
        # First, collect all IPs that respond to ping
        ping_results = list(executor.map(
            lambda ip: (str(ip), ping_host(str(ip))),
            hosts
        ))
        
        # Get hostnames for responsive IPs
        for ip, is_alive in ping_results:
            if is_alive:
                hostname = get_hostname(ip)
                active_hosts.append((ip, hostname))
    
    return active_hosts

class WiFiScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WiFi Network Scanner")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)
        
        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure fonts
        self.title_font = Font(family='Helvetica', size=12, weight='bold')
        self.normal_font = Font(family='Helvetica', size=10)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="WiFi Network Scanner", 
            font=self.title_font
        )
        title_label.pack(pady=(0, 10))
        
        # Network Info Frame
        info_frame = ttk.LabelFrame(main_frame, text="Network Information", padding="10")
        info_frame.pack(fill=tk.X, pady=5)
        
        # Network info labels
        self.ip_var = tk.StringVar(value="Not Available")
        self.network_var = tk.StringVar(value="Not Available")
        self.netmask_var = tk.StringVar(value="Not Available")
        
        ttk.Label(info_frame, text="Your IP:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(info_frame, textvariable=self.ip_var).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(info_frame, text="Network:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(info_frame, textvariable=self.network_var).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(info_frame, text="Netmask:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        ttk.Label(info_frame, textvariable=self.netmask_var).grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)
        
        # Scan button
        self.scan_button = ttk.Button(
            main_frame, 
            text="Start Scan", 
            command=self.start_scan_thread,
            style='Accent.TButton'
        )
        self.scan_button.pack(pady=10)
        
        # Progress frame
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame, 
            variable=self.progress_var, 
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.pack(fill=tk.X, expand=True)
        
        self.status_var = tk.StringVar(value="Ready to scan")
        ttk.Label(progress_frame, textvariable=self.status_var).pack()
        
        # Results frame
        results_frame = ttk.LabelFrame(main_frame, text="Scan Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Results treeview
        columns = ('ip', 'hostname', 'status')
        self.tree = ttk.Treeview(
            results_frame, 
            columns=columns, 
            show='headings',
            selectmode='browse'
        )
        
        # Configure columns
        self.tree.heading('ip', text='IP Address', anchor=tk.W)
        self.tree.heading('hostname', text='Hostname', anchor=tk.W)
        self.tree.heading('status', text='Status', anchor=tk.W)
        
        self.tree.column('ip', width=200, stretch=tk.NO)
        self.tree.column('hostname', width=300, stretch=tk.YES)
        self.tree.column('status', width=100, stretch=tk.NO)
        
        # Add scrollbars
        y_scroll = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        x_scroll = ttk.Scrollbar(results_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky='nsew')
        y_scroll.grid(row=0, column=1, sticky='ns')
        x_scroll.grid(row=1, column=0, sticky='ew')
        
        # Configure grid weights
        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)
        
        # Status bar
        self.status_bar = ttk.Label(
            main_frame, 
            text="Ready", 
            relief=tk.SUNKEN, 
            anchor=tk.W,
            padding=(5, 2)
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Configure main frame grid
        main_frame.grid_rowconfigure(0, weight=0)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Initialize network info
        self.update_network_info()
    
    def update_network_info(self):
        """Update the network information display"""
        try:
            my_ip, network_addr, netmask, _ = get_network_info()
            if all([my_ip, network_addr, netmask]):
                self.ip_var.set(my_ip)
                self.network_var.set(network_addr)
                self.netmask_var.set(netmask)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get network info: {str(e)}")
    
    def start_scan_thread(self):
        """Start the network scan in a separate thread"""
        self.scan_button.config(state=tk.DISABLED)
        self.tree.delete(*self.tree.get_children())
        self.status_var.set("Scanning network...")
        self.progress_var.set(0)
        
        # Start scan in a separate thread
        self.scan_thread = threading.Thread(target=self.start_scan, daemon=True)
        self.scan_thread.start()
        
        # Start checking the progress
        self.check_progress()
    
    def start_scan(self):
        """Perform the network scan"""
        try:
            my_ip, network_addr, netmask, hosts = get_network_info()
            if not all([my_ip, network_addr, netmask, hosts]):
                self.root.after(0, lambda: messagebox.showerror(
                    "Error", 
                    "Failed to get network information. Make sure you're connected to a network."
                ))
                return
            
            # Convert hosts to list for progress tracking
            hosts_list = list(hosts)
            total_hosts = len(hosts_list)
            
            # Update status with total hosts to scan
            self.root.after(0, lambda: self.status_var.set(
                f"Scanning network: {network_addr} {netmask} ({total_hosts} hosts)"
            ))
            
            active_hosts = []
            
            # Use ThreadPoolExecutor to speed up the scanning process
            with ThreadPoolExecutor(max_workers=100) as executor:
                # Map each IP to a future
                future_to_ip = {
                    executor.submit(self.scan_host, str(ip)): str(ip) 
                    for ip in hosts_list
                }
                
                # Process results as they complete
                for i, future in enumerate(as_completed(future_to_ip)):
                    ip = future_to_ip[future]
                    try:
                        result = future.result()
                        if result:
                            ip, hostname = result
                            active_hosts.append((ip, hostname))
                            self.root.after(0, self.add_host_to_tree, ip, hostname)
                    except Exception as e:
                        print(f"Error scanning {ip}: {e}")
                    
                    # Update progress
                    progress = ((i + 1) / total_hosts) * 100
                    self.progress_var.set(progress)
            
            # Sort results by IP
            active_hosts.sort(key=lambda x: tuple(map(int, x[0].split('.'))))
            
            # Update UI with results
            self.root.after(0, self.scan_completed, len(active_hosts))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Scan failed: {str(e)}"))
        finally:
            self.root.after(0, lambda: self.scan_button.config(state=tk.NORMAL))
    
    def scan_host(self, ip):
        """Scan a single host and return (ip, hostname) if active"""
        if ping_host(ip):
            hostname = get_hostname(ip)
            return (ip, hostname)
        return None
    
    def add_host_to_tree(self, ip, hostname):
        """Add a host to the results tree"""
        self.tree.insert('', tk.END, values=(ip, hostname, 'Online'))
    
    def scan_completed(self, num_devices):
        """Update UI when scan is completed"""
        self.status_var.set(f"Scan completed. Found {num_devices} devices.")
        self.status_bar.config(text=f"Scan completed. Found {num_devices} devices.")
        self.progress_var.set(100)
    
    def check_progress(self):
        """Check and update progress"""
        # This method is called periodically to update the UI
        # during the scan
        self.root.after(100, self.check_progress)

def main():
    root = tk.Tk()
    
    # Set window icon and style
    try:
        root.iconbitmap('wifi_icon.ico')  # You can add an icon file if desired
    except:
        pass  # Use default icon if custom icon is not available
    
    # Set theme colors
    root.tk_setPalette(background='#f0f0f0', foreground='black',
                      activeBackground='#e0e0e0', activeForeground='black')
    
    # Create the application
    app = WiFiScannerApp(root)
    
    # Start the application
    root.mainloop()

if __name__ == "__main__":
    main()
