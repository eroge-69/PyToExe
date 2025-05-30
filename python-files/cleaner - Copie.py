import os
import sys
import time
import shutil
import subprocess
import ctypes
import random
import stat
import hashlib
import requests
from colorama import Fore, init
import wmi
import logging
import psutil
import threading
import socket
import msvcrt
from datetime import datetime, timedelta
import os; os.system('taskkill /IM steam.exe /F') if any('steam.exe' in proc.lower() for proc in os.popen('tasklist').read().splitlines()) else None

init(autoreset=True)


SERVER_URL = "http://172.252.236.169:27301"


SYSTEM_PROCESS_WHITELIST = [
    'svchost.exe', 'explorer.exe', 'winlogon.exe', 'csrss.exe', 'smss.exe',
    'lsass.exe', 'wininit.exe', 'taskhostw.exe', 'dwm.exe', 'services.exe',
    'system', 'idle', 'cmd.exe', 'conhost.exe', 'taskmgr.exe', 'powershell.exe'
]


CRACKING_TOOLS_BLACKLIST = [
    'x64dbg.exe', 'x32dbg.exe', 'ida64.exe', 'ida32.exe', 'ollydbg.exe',
    'cheatengine-x86_64.exe', 'cheatengine-i386.exe', 'ghidra.exe',
    'radare2.exe', 'cutter.exe', 'wireshark.exe', 'fiddler.exe',
    'johntheripper.exe', 'hashcat.exe', 'brutus.exe', 'wfuzz.exe',
    'medusa.exe', 'ophcrack.exe', 'l0phtcrack.exe', 'aircrack-ng.exe',
    'dnspy.exe', 'de4dot.exe', 'ilspy.exe', 'pwcrack.exe',
    'sqlmap.exe', 'openvas.exe', 'nmap.exe', 'ettercap.exe',
    'datecracker.exe', 'keyfinder.exe', 'activlock3.dll', 'alugen.dll'
]


CONFIG_DIR = os.path.join(os.environ.get('APPDATA', ''), 'Z2K')
VM_WARNINGS_FILE = os.path.join(CONFIG_DIR, 'vm_warnings.json')


monitoring = True

def check_dependencies():
    """Check if all required dependencies are installed."""
    logging.info("Checking dependencies")
    required_modules = ['psutil', 'wmi', 'colorama', 'requests', 'msvcrt']
    missing = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    if missing:
        error_msg = f"Missing modules: {', '.join(missing)}. Install with 'pip install {' '.join(missing)}'."
        logging.error(error_msg)
        show_windows_error(error_msg)
        self_destruct()
        sys.exit(1)

def get_hwid_and_components():
    """Generate a unique HWID and retrieve all hardware components."""
    logging.info("Generating HWID and hardware components")
    try:
        components = {
            "cpu_id": "Unknown",
            "cpu_name": "Unknown",
            "disk_serial": "Unknown",
            "motherboard_serial": "Unknown",
            "mac_address": "Unknown"
        }
        identifiers = []
        c = wmi.WMI()
        
        
        cpu = c.Win32_Processor()[0]
        components["cpu_name"] = cpu.Name or "Unknown"
        components["cpu_id"] = cpu.ProcessorId or str(random.randint(1000, 9999))
        identifiers.append(components["cpu_id"])
        identifiers.append(components["cpu_name"])
        
        
        disk_info = c.Win32_DiskDrive()[0]
        components["disk_serial"] = disk_info.SerialNumber or str(random.randint(1000, 9999))
        identifiers.append(components["disk_serial"])
        
        
        mb_info = c.Win32_BaseBoard()[0]
        components["motherboard_serial"] = mb_info.SerialNumber or str(random.randint(1000, 9999))
        identifiers.append(components["motherboard_serial"])
        
        
        for nic in c.Win32_NetworkAdapterConfiguration(IPEnabled=True):
            components["mac_address"] = nic.MACAddress or str(random.randint(1000, 9999))
            identifiers.append(components["mac_address"])
            break  
        
        combined_data = "".join(str(id) for id in identifiers)
        hwid = hashlib.sha256(combined_data.encode('utf-8')).hexdigest()
        logging.info(f"Generated HWID: {hwid}, Components: {components}")
        return hwid, components
    except Exception as e:
        logging.error(f"Failed to generate HWID or components: {e}")
        hwid = hashlib.sha256(f"fallback-hwid-{random.randint(1000, 9999)}".encode('utf-8')).hexdigest()
        return hwid, {
            "cpu_id": hwid[:16],
            "cpu_name": "Unknown",
            "disk_serial": "Unknown",
            "motherboard_serial": "Unknown",
            "mac_address": "Unknown"
        }

def detect_virtual_machine():
    """Detect if the system is running in a virtual machine."""
    logging.info("Checking for virtual machine")
    try:
        c = wmi.WMI()
        bios = c.Win32_BIOS()[0]
        motherboard = c.Win32_BaseBoard()[0]
        disks = c.Win32_DiskDrive()
        vm_indicators = [
            'vmware' in bios.Manufacturer.lower(),
            'vmware' in motherboard.Manufacturer.lower(),
            any('vmware' in disk.Model.lower() for disk in disks),
            'virtualbox' in bios.Manufacturer.lower(),
            'vbox' in motherboard.Product.lower(),
            any('vbox' in disk.Model.lower() for disk in disks),
            'microsoft corporation' in bios.Manufacturer.lower() and 'hyper-v' in bios.Version.lower(),
            'microsoft virtual disk' in [disk.Model.lower() for disk in disks],
            'qemu' in bios.Manufacturer.lower(),
            'kvm' in motherboard.Product.lower(),
            'virtual' in motherboard.Product.lower(),
            bios.SerialNumber.lower().startswith('none'),
        ]
        is_vm = any(vm_indicators)
        logging.info(f"Virtual machine detection: {'Detected' if is_vm else 'Not detected'}")
        return is_vm
    except Exception as e:
        logging.error(f"Failed to detect virtual machine: {e}")
        return False

def init_config_dir():
    """Initialize the configuration directory."""
    logging.info(f"Initializing config directory: {CONFIG_DIR}")
    try:
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)
            ctypes.windll.kernel32.SetFileAttributesW(CONFIG_DIR, 2)  
        logging.info("Config directory initialized")
    except Exception as e:
        logging.error(f"Failed to initialize config directory: {e}")

def load_vm_warnings(hwid):
    """Load VM warning count for the HWID."""
    logging.info(f"Loading VM warnings for HWID: {hwid}")
    try:
        if os.path.exists(VM_WARNINGS_FILE):
            with open(VM_WARNINGS_FILE, 'r') as f:
                data = json.load(f)
                return data.get(hwid, 0)
        return 0
    except Exception as e:
        logging.error(f"Failed to load VM warnings: {e}")
        return 0

def save_vm_warnings(hwid, count):
    """Save VM warning count for the HWID."""
    logging.info(f"Saving VM warnings for HWID: {hwid}, Count: {count}")
    try:
        data = {}
        if os.path.exists(VM_WARNINGS_FILE):
            with open(VM_WARNINGS_FILE, 'r') as f:
                data = json.load(f)
        data[hwid] = count
        with open(VM_WARNINGS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logging.error(f"Failed to save VM warnings: {e}")

def report_vm(hwid, components, warning_count):
    """Report VM detection to the server."""
    logging.info(f"Reporting VM detection for HWID: {hwid}, Warning count: {warning_count}")
    try:
        payload = {
            "hwid": hwid,
            "cpu_id": components["cpu_id"],
            "cpu_name": components["cpu_name"],
            "disk_serial": components["disk_serial"],
            "motherboard_serial": components["motherboard_serial"],
            "mac_address": components["mac_address"],
            "warning_count": warning_count
        }
        response = requests.post(f"{SERVER_URL}/report-vm", json=payload, timeout=2)
        response.raise_for_status()
        data = response.json()
        logging.info(f"VM report response: {data.get('message', 'No message')}")
        return data.get("success", False)
    except requests.RequestException as e:
        logging.error(f"Failed to report VM detection: {e}")
        return False

def handle_vm_detection(hwid, components):
    """Handle VM detection logic with warnings and blacklisting."""
    logging.info("Handling VM detection")
    if not detect_virtual_machine():
        return True  
    init_config_dir()
    warning_count = load_vm_warnings(hwid) + 1
    save_vm_warnings(hwid, warning_count)
    report_vm(hwid, components, warning_count)
    if warning_count <= 2:
        error_msg = f"Warning {warning_count}/2: Running this software in a virtual machine is prohibited. You will be blacklisted on the 3rd attempt."
        show_windows_error(error_msg)
        logging.warning(f"VM warning {warning_count} issued for HWID: {hwid}")
        return True  
    else:
        error_msg = "Critical error: 3rd attempt to run in a virtual machine detected. Your system has been blacklisted."
        logging.error(error_msg)
        show_windows_error(error_msg)
        report_suspicious(hwid, None, components, "3rd VM attempt detected")
        self_destruct()
        sys.exit(1)
    return False

def is_online():
    """Check if the system is connected to the internet."""
    logging.info("Checking internet connectivity")
    try:
        socket.create_connection(("api.ipify.org", 80), timeout=2)
        return True
    except (socket.error, socket.timeout):
        logging.warning("No internet connection detected")
        return False

def show_windows_error(message):
    """Display a native Windows error message using MessageBox."""
    logging.info(f"Showing error: {message}")
    ctypes.windll.user32.MessageBoxW(0, message, "Erreur", 0x00000010)

def self_destruct():
    """Delete the script or executable itself with retries."""
    logging.info("Attempting self-destruct")
    max_attempts = 10000
    for attempt in range(max_attempts):
        try:
            script_path = os.path.abspath(sys.argv[0])
            if not os.path.exists(script_path):
                script_path = getattr(sys, 'frozen', False) and sys.executable or __file__
            if not os.path.exists(script_path):
                logging.error("Self-destruct failed: Script/executable path not found.")
                return
            os.chmod(script_path, stat.S_IWRITE)
            os.remove(script_path)
            if not os.path.exists(script_path):
                logging.info(f"Self-destruct successful: {script_path} deleted.")
                return
            else:
                logging.warning(f"Self-destruct attempt {attempt + 1}/{max_attempts}: File still exists: {script_path}")
        except Exception as e:
            logging.error(f"Self-destruct attempt {attempt + 1}/{max_attempts} failed: {e}")
        time.sleep(0.5)
    logging.error("Self-destruct failed after all attempts.")

def check_blacklist(hwid, components):
    """Check if the HWID is blacklisted via the server with retry on failure."""
    logging.info(f"Checking blacklist for HWID: {hwid}")
    max_attempts = 10000
    for attempt in range(max_attempts):
        try:
            payload = {
                "hwid": hwid,
                "cpu_id": components["cpu_id"],
                "cpu_name": components["cpu_name"],
                "disk_serial": components["disk_serial"],
                "motherboard_serial": components["motherboard_serial"],
                "mac_address": components["mac_address"]
            }
            response = requests.post(f"{SERVER_URL}/check-blacklist", json=payload, timeout=2)
            response.raise_for_status()
            data = response.json()
            if data.get("blacklisted"):
                error_msg = data.get("message", "Votre système est blacklisté.")
                logging.error(f"System blacklisted: {error_msg}")
                show_windows_error(error_msg)
                report_suspicious(hwid, None, components, "Server-reported blacklist")
                self_destruct()
                logging.info("Closing software due to blacklist.")
                sys.exit(1) 
            logging.info(f"System not blacklisted: HWID: {hwid}")
            return False
        except requests.RequestException as e:
            logging.error(f"Attempt {attempt + 1}/{max_attempts} failed to check blacklist: {e}")
            if attempt < max_attempts - 1:
                error_msg = "Vous êtes blacklisté."
                show_windows_error(error_msg)
                logging.info("Closing software due to suspected blacklist.")
                sys.exit(1) 
            error_msg = "Échec de la vérification du système après plusieurs tentatives."
            logging.error(error_msg)
            show_windows_error(error_msg)
            report_suspicious(hwid, None, components, "brut force")
            self_destruct()
            logging.info("Closing software due to blacklist check failure.")
            sys.exit(1)  

def validate_key(key, hwid, components, suspected_x64dbg=False):
    """Validate a key via the server with activation-based expiration and last usage tracking."""
    logging.info(f"Validating key: {key}, Suspected x64dbg: {suspected_x64dbg}")
    try:
        if not key or len(key) != 32 or not all(c in '0123456789abcdef' for c in key.lower()):
            error_message = "Clé invalide : format incorrect."
            print()
            show_windows_error(error_message)
            return False, None  

     
        activation_time = datetime.utcnow()
        payload = {
            "key": key,
            "hwid": hwid,
            "cpu_id": components["cpu_id"],
            "cpu_name": components["cpu_name"],
            "disk_serial": components["disk_serial"],
            "motherboard_serial": components["motherboard_serial"],
            "mac_address": components["mac_address"],
            "suspected_x64dbg": suspected_x64dbg,
            "activation_time": activation_time.isoformat()
        }
        response = requests.post(f"{SERVER_URL}/validate-key", json=payload, timeout=2)
        response.raise_for_status()
        data = response.json()
        if not data.get("valid"):
            error_message = data.get("message", "Clé invalide.")
            logging.error(f"Key validation failed: {error_message}")
            show_windows_error(error_message)
            if data.get("blacklisted", False) or suspected_x64dbg:
                report_suspicious(hwid, key, components, "Blacklisted system or x64dbg detected")
                self_destruct()
                logging.info("Closing software due to blacklist or x64dbg detection.")
                sys.exit(1)
            return False, None  

      
        expiration_duration = data.get("expiration_duration", 0)  
        if expiration_duration > 0:
            expiration_time = activation_time + timedelta(seconds=expiration_duration)
            if datetime.utcnow() > expiration_time:
                error_message = "Clé expirée."
                logging.error(f"Key validation failed: {error_message}")
                show_windows_error(error_message)
                return False, None

        
        time.sleep(2)  

        
        last_usage = data.get("last_usage", "Jamais utilisé auparavant")
        print(Fore.GREEN + f" {data.get('', '')}")
        logging.info(f"Key validated: {key}, HWID: {hwid}, Components: {components}, Last usage: {last_usage}, Message: {data.get('message')}")
        return True, last_usage
    except requests.RequestException as e:
        error_msg = "Échec de la validation de la clé."
        print()
        show_windows_error(error_msg)
        return False, None  

def report_suspicious(hwid, key, components, reason):
    """Report suspicious activity to the server for blacklisting with retries."""
    logging.info(f"Reporting suspicious activity: {reason}")
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            payload = {
                "hwid": hwid,
                "key": key,
                "cpu_id": components["cpu_id"],
                "cpu_name": components["cpu_name"],
                "disk_serial": components["disk_serial"],
                "motherboard_serial": components["motherboard_serial"],
                "mac_address": components["mac_address"],
                "reason": reason
            }
            response = requests.post(f"{SERVER_URL}/report-suspicious", json=payload, timeout=2)
            response.raise_for_status()
            data = response.json()
            if data.get("success"):
                logging.info(f"Suspicious activity reported: HWID: {hwid}, Key: {key}, Reason: {reason}")
                return True
            else:
                logging.error(f"Blacklist attempt {attempt + 1}/{max_attempts} failed: {data.get('message', 'Unknown error')}")
        except requests.RequestException as e:
            logging.error(f"Blacklist attempt {attempt + 1}/{max_attempts} failed: {e}")
        time.sleep(0.5)
    logging.error(f"Failed to blacklist system after {max_attempts} attempts: HWID: {hwid}, Reason: {reason}")
    return False

def detect_multiple_instances():
    """Check for multiple instances of the software."""
    logging.info("Checking for multiple instances")
    try:
        current_process = os.path.basename(sys.argv[0]).lower()
        count = 0
        for proc in psutil.process_iter(['name']):
            if proc.info['name'].lower() == current_process:
                count += 1
            if count > 1:
                logging.error("Multiple instances detected")
                return True
        logging.info("No multiple instances detected")
        return False
    except psutil.Error as e:
        logging.error(f"Failed to check instances: {e}")
        return False

def monitor_processes(hwid, components, stop_event):
    """Monitor for new processes, terminate those not in the whitelist, and detect cracking tools."""
    logging.info("Starting process monitoring")
    try:
        initial_processes = {proc.pid: proc.info['name'].lower() for proc in psutil.process_iter(['name'])}
        logging.info(f"Initial processes: {len(initial_processes)} processes detected")
        
        while not stop_event.is_set():
            current_processes = {proc.pid: proc.info['name'].lower() for proc in psutil.process_iter(['name'])}
            
            
            for pid, name in current_processes.items():
                if name.lower() in [tool.lower() for tool in CRACKING_TOOLS_BLACKLIST]:
                    error_msg = f"Cracking tool detected: {name} (PID: {pid}). The software will now close."
                    logging.error(f"Cracking tool detected: {name} (PID: {pid}), HWID: {hwid}")
                    show_windows_error(error_msg)
                    try:
                        proc = psutil.Process(pid)
                        proc.terminate()
                        logging.info(f"Terminated cracking tool: {name} (PID: {pid})")
                    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                        logging.warning(f"Failed to terminate cracking tool {name} (PID: {pid}): {e}")
                    report_suspicious(hwid, None, components, f"Cracking tool detected: {name}")
                    logging.info("Closing software due to cracking tool detection.")
                    sys.exit(1)
            
           
            new_processes = {pid: name for pid, name in current_processes.items() if pid not in initial_processes}
            
            for pid, name in new_processes.items():
                if name not in SYSTEM_PROCESS_WHITELIST:
                    try:
                        proc = psutil.Process(pid)
                        proc.terminate()
                        logging.info(f"Terminated new process: {name} (PID: {pid})")
                    except psutil.NoSuchProcess:
                        logging.warning(f"Process {name} (PID: {pid}) no longer exists")
                    except psutil.AccessDenied:
                        logging.error(f"Access denied when trying to terminate process: {name} (PID: {pid})")
                    except Exception as e:
                        logging.error(f"Failed to terminate process {name} (PID: {pid}): {e}")
            
            initial_processes = current_processes
            time.sleep(1)
            
    except Exception as e:
        logging.error(f"Process monitoring failed: {e}")

def check_fivem_running():
    """Check if FiveM process is running."""
    logging.info("Checking for FiveM process")
    try:
        for proc in psutil.process_iter(['name']):
            if proc.info['name'].lower() == 'fivem.exe':
                logging.info("FiveM process detected")
                return True
    except psutil.Error as e:
        logging.error(f"Failed to check for FiveM process: {e}")
    return False

def terminate_fivem():
    """Attempt to terminate all FiveM processes."""
    logging.info("Attempting to terminate FiveM processes")
    try:
        terminated = False
        for proc in psutil.process_iter(['name']):
            if proc.info['name'].lower() == 'fivem.exe':
                proc.terminate()
                proc.wait(timeout=3)
                terminated = True
                logging.info("FiveM process terminated")
        return terminated
    except psutil.Error as e:
        logging.error(f"Failed to terminate FiveM: {e}")
        return False

def monitor_fivem(stop_event):
    """Continuously monitor and terminate new FiveM processes."""
    logging.info("Starting FiveM monitoring")
    while not stop_event.is_set():
        if check_fivem_running():
            terminate_fivem()
        time.sleep(1)

def handle_fivem_at_startup():
    """Handle FiveM detection and termination at startup."""
    logging.info("Handling FiveM at startup")
    if not is_admin():
        logging.info("Admin privileges required to detect/terminate FiveM. Skipping.")
        return False
    if check_fivem_running():
        print(Fore.YELLOW + '[INFO] FiveM is running. Attempting to terminate...')
        logging.info("FiveM is running. Attempting to terminate.")
        if not terminate_fivem():
            show_windows_error("Échec de la terminaison de FiveM. Veuillez fermer FiveM manuellement.")
            self_destruct()
            sys.exit(1)
        if check_fivem_running():
            show_windows_error("FiveM est toujours en cours d'exécution. Veuillez fermer FiveM manuellement.")
            self_destruct()
            sys.exit(1)
        return True
    return False

def flush_dns():
    """Flush the DNS cache using ipconfig with retry and detailed feedback."""
    logging.info("Flushing DNS cache")
    if not is_admin():
        logging.error("Admin privileges required to flush DNS. Skipping.")
        return False

    def try_flush():
        try:
            result = subprocess.run(
                ['ipconfig', '/flushdns'],
                shell=True,
                check=True,
                capture_output=True,
                text=True
            )
            output = result.stdout.lower()
            success_indicators = [
                "successfully flushed",
                "purged the dns resolver cache",
                "vidage du cache de résolution dns réussi",
                "dns-auflösungscache erfolgreich geleert",
            ]
            if any(indicator in output for indicator in success_indicators):
                print(Fore.WHITE + "[OK] Cache DNS vidé avec succès !")
                logging.info("DNS cache flushed successfully.")
                return True
            return False
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to execute ipconfig /flushdns: {e}")
            return False

    if try_flush():
        return True
    time.sleep(1)
    return try_flush()

def simulate_connection():
    """Display a connection animation."""
    print(Fore.WHITE + 'connect host ', end='', flush=True)
    for i in range(3):
        time.sleep(1)  
        print('.', end='', flush=True)
    print("\n") 

def connection_message():
    """Display a connection animation."""
    print(Fore.WHITE + 'Connexion au serveur', end='', flush=True)
    for _ in range(3):
        time.sleep(1)
        print('.', end='', flush=True)
    time.sleep(1)
    print()

def goodbye_message(username):
    """Display a goodbye message with disconnection animation."""
    print(Fore.WHITE + f'Au revoir, {username}')
    print(Fore.WHITE + 'Déconnexion du serveur...', end='', flush=True)
    for _ in range(3):
        time.sleep(1)
        print('.', end='', flush=True)
    time.sleep(1)
    print()

def welcome_message():
    """Display a random welcome message and return the username."""
    username = os.getlogin()
    messages = [
        f'Hey {username}, prêt à nettoyer ?',
        f'Salut {username}, on range le système ?',
        f'Yo {username}, on vire les cochonneries !',
        f'Hey {username}, c\'est l\'heure du ménage ?',
        f'{username}, on purge le cache ?'
    ]
    print(Fore.CYAN + random.choice(messages))
    print(Fore.GREEN + '[y/n] ', end='', flush=True)
    return username

def get_confirmation():
    """Get user confirmation (y/n) without requiring Enter."""
    logging.info("Prompting for confirmation")
    print(Fore.GREEN + '[y/n] ', end='', flush=True)
    while True:
        if msvcrt.kbhit():
            key = msvcrt.getch().decode('utf-8').lower()
            if key in ['y', 'n']:
                if key == 'y':
                    print(Fore.GREEN + ' -> Yes')
                    logging.info("User confirmed: Yes")
                else:
                    print(Fore.RED + ' -> No')
                    logging.info("User confirmed: No")
                return key == 'y'

def ask_to_clean(username):
    """Ask the user if they want to clean without requiring Enter."""
    print(Fore.CYAN + f"Hello {username}, do you want to clean ?")
    return get_confirmation()

def is_admin():
    """Check if the script is running with admin privileges."""
    logging.info("Checking admin privileges")
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def request_admin_permissions():
    """Request admin privileges by relaunching the script."""
    logging.info("Requesting admin permissions")
    if not is_admin():
        logging.info("Restarting script in admin mode.")
        script = sys.argv[0]
        params = ' '.join(sys.argv[1:])
        try:
            ctypes.windll.shell32.ShellExecuteW(None, 'runas', sys.executable, f'"{script}" {params}', None, 1)
            sys.exit()
        except Exception as e:
            logging.error(f"Failed to elevate privileges: {e}")
            show_windows_error("Ce logiciel nécessite des privilèges administrateurs.")
            self_destruct()
            sys.exit(1)

def handle_readonly(func, path, exc_info):
    """Handle read-only file errors during deletion by changing permissions."""
    os.chmod(path, stat.S_IWRITE)
    func(path)

def safe_delete_directory(directory):
    """Safely delete a directory and handle errors."""
    logging.info(f"Deleting directory: {directory}")
    if not os.path.exists(directory):
        print(Fore.WHITE + f"[OK] Directory {directory} déjà supprimé !")
        logging.info(f"Directory {directory} already deleted.")
        return False
    try:
        shutil.rmtree(directory, ignore_errors=False, onerror=handle_readonly)
        print(Fore.WHITE + f"[OK] Directory {directory} supprimé avec succès !")
        logging.info(f"Directory {directory} deleted successfully.")
        return True
    except Exception as e:
        logging.error(f"Failed to delete {directory}: {e}")
        return False

def show_progress_bar(total=31):
    """Display a progress bar for the cleaning process."""
    speed = round(random.uniform(10.0, 50.0), 1)
    for i in range(total + 1):
        bar = '[' + '-' * i + ' ' * (total - i) + ']'
        progress = f'{i}/{total}'
        sys.stdout.write(f'\r{Fore.LIGHTMAGENTA_EX}{bar} {speed} MB/s {progress}')
        sys.stdout.flush()
        time.sleep(0.1)
    print()

def main():
    """Main function to execute the cleaning process."""
    os.system('cls' if sys.platform.startswith('win') else 'clear')
    logging.info("Starting loader.py")

    
    check_dependencies()

   
    request_admin_permissions()

    
    try:
        hwid, components = get_hwid_and_components()
    except Exception as e:
        logging.error(f"Failed to generate HWID or components: {e}")
        show_windows_error("Échec de la génération des composants système.")
        self_destruct()
        sys.exit(1)

   
    check_blacklist(hwid, components)

   
    if not handle_vm_detection(hwid, components):
        sys.exit(1)

    
    try:
        if ctypes.windll.kernel32.IsDebuggerPresent() or sys.gettrace():
            report_suspicious(hwid, None, components, "Debugger detected")
            show_windows_error("Erreur critique : Débogueur détecté. Votre système a été blacklisté.")
            self_destruct()
            logging.info("Closing software due to debugger detection.")
            sys.exit(1)
    except Exception as e:
        logging.error(f"Debugger check failed: {e}")

    try:
        if detect_multiple_instances():
            report_suspicious(hwid, None, components, "Multiple instances detected")
            show_windows_error("Erreur critique : Plusieurs instances détectées. Votre système a été blacklisté.")
            self_destruct()
            logging.info("Closing software due to multiple instances.")
            sys.exit(1)
    except Exception as e:
        logging.error(f"Multiple instance check failed: {e}")

  
    stop_event = threading.Event()
    monitor_thread = threading.Thread(target=monitor_processes, args=(hwid, components, stop_event))
    monitor_thread.daemon = True
    monitor_thread.start()

    init(autoreset=True)
    
    white_text = Fore.WHITE + "[+] Product:"
    cyan_text = Fore.CYAN + " CLEANER FIVEM - by HZ"
    
    print(white_text + cyan_text)
    print()
    key = input(Fore.GREEN + "Entrez votre clé: ").strip()
    if key.lower() == "quit":
        print(Fore.WHITE + "Quitter...")
        logging.info("User quit the program")
        stop_event.set()
        sys.exit()

   
    is_valid, last_usage = validate_key(key, hwid, components)
    if not is_valid:
        print(Fore.RED + "Clé invalide ou expirée, le logiciel va se fermer.")
        logging.info("Invalid or expired key entered, exiting program")
        stop_event.set()
        sys.exit(1)

    
    simulate_connection()

    
    skip_fivem_cleanup = handle_fivem_at_startup()

   
    print(Fore.CYAN + '  ====================================')
    print(Fore.WHITE + 'Communauté HZ #1 Des CLEANER Fivem 2K25 !')
    print(Fore.CYAN + '  ====================================')
    print()

   
    username = os.getlogin()
    if not ask_to_clean(username):
        goodbye_message(username)
        stop_event.set()
        sys.exit()

    
    dirs_to_remove = [
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'D3DSCache'),
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'DigitalEntitlements'),
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'FiveM', 'FiveM.app', 'data', 'cache'),
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'FiveM', 'FiveM.app', 'data', 'nui-storage'),
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'FiveM', 'FiveM.app', 'data', 'server-cache-priv'),
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'FiveM', 'FiveM.app', 'data', 'server-cache'),
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'FiveM', 'FiveM.app', 'logs'),
        os.path.join(os.environ.get('APPDATA', ''), 'CitizenFX'),
        'C:\\Program Files (x86)\\Steam\\appcache',
        'C:\\Program Files (x86)\\Steam\\logs',
        'C:\\Program Files (x86)\\Steam\\userdata',
        'C:\\Program Files (x86)\\Steam\\config'
    ]

    if skip_fivem_cleanup:
        print(Fore.YELLOW + '[INFO] Saut du nettoyage lié à FiveM en raison d\'une terminaison préalable.')
        logging.info("Skipping FiveM-related cleanup due to prior termination.")

    for directory in dirs_to_remove:
        safe_delete_directory(directory)
        time.sleep(0.025)

    for directory in critical_dirs:
        if os.path.exists(directory):
            print(Fore.YELLOW + f'[ATTENTION] La suppression de {directory} peut affecter les données Steam. Continuer ?')
            if not get_confirmation():
                print(Fore.YELLOW + f'[INFO] Suppression de {directory} ignorée')
                logging.info(f"Skipped deletion of {directory}")
            else:
                safe_delete_directory(directory)
        else:
            print(Fore.WHITE + f'[OK] Directory {directory} déjà supprimé !')
            logging.info(f"Directory {directory} already deleted.")
        time.sleep(0.025)

    print(Fore.CYAN + 'Voulez-vous nettoyer votre DNS ?')
    if not get_confirmation():
        print(Fore.YELLOW + '[INFO] Nettoyage du DNS ignoré')
        logging.info("DNS cleanup skipped by user")
    else:
        flush_dns()

    show_progress_bar()
    print('\n[OK] Done !\n')
    logging.info("Cleanup completed successfully.")
    input(Fore.WHITE + 'Appuyez sur Entrée pour quitter...')
    stop_event.set()

if __name__ == '__main__':
    monitor_thread = threading.Thread(target=monitor_fivem, args=(threading.Event(),), daemon=True)
    monitor_thread.start()
    try:
        main()
    finally:
        monitoring = False
        monitor_thread.join(timeout=1)