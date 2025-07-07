import sys
import ctypes
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from ttkbootstrap import Style 
from PIL import Image, ImageTk
import os
import psutil
import socket
import uuid
import platform
import threading
import queue
import wmi
import speedtest

class ColoredText:
    """Class for handling colored text in tkinter Text widget"""
    def __init__(self, text_widget):
        self.text = text_widget
        self.setup_tags()
    
    def setup_tags(self):
        # Configure text styles with red/black theme
        self.text.tag_config('info', foreground='#FF4444')  # Light red
        self.text.tag_config('success', foreground='#00FF00')  # Bright green
        self.text.tag_config('warning', foreground='#FFAA00')  # Orange
        self.text.tag_config('error', foreground='#FF0000')  # Bright red
        self.text.tag_config('title', foreground='#FFFFFF', font=('Segoe UI', 12, 'bold'))  # White
        self.text.tag_config('header', foreground='#FF6666', font=('Segoe UI', 10, 'bold'))  # Medium red
        self.text.tag_config('highlight', foreground='#FFAAAA')  # Light pink
        self.text.tag_config('command', foreground='#CCCCCC')  # Light gray
        self.text.tag_config('system', foreground='#FF8888')  # Medium light red
        self.text.tag_config('network', foreground='#AA00FF')  # Purple
        self.text.tag_config('activation', foreground='#FF00FF')  # Magenta
    
    def insert(self, content, tag=None):
        self.text.config(state=tk.NORMAL)
        self.text.insert(tk.END, content + "\n", tag)
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)

class SystemManager:
    def __init__(self):
        self._wmi = None
    
    @property
    def wmi(self):
        if self._wmi is None:
            self._wmi = wmi.WMI()
        return self._wmi 
    
    def activate_windows(self):
        try:
            result = subprocess.run(
                ["powershell", "-Command", "irm https://get.activated.win | iex"],
                capture_output=True,
                text=True,
                check=True
            )
            return f"Aktivace proběhla úspěšně\n{result.stdout}"
        except subprocess.CalledProcessError as e:
            return f"Chyba při aktivaci:\n{e.stderr}"
        except Exception as e:
            return f"CHYBA: {str(e)}"
    
    def get_system_info(self):
        try:
            import datetime
            boot_time = psutil.boot_time()
            now = datetime.datetime.now()
            boot_time_dt = datetime.datetime.fromtimestamp(boot_time)
            uptime = now - boot_time_dt
            sys_wmi = self.wmi.Win32_ComputerSystem()[0]
            bios = self.wmi.Win32_BIOS()[0]
            os_wmi = self.wmi.Win32_OperatingSystem()[0]
            gpus = self.get_gpu_info()
            # Síťová karta
            nics = self.wmi.Win32_NetworkAdapterConfiguration(IPEnabled=True)
            netinfo = []
            for nic in nics:
                netinfo.append(f"{nic.Description} (MAC: {nic.MACAddress}, IP: {nic.IPAddress[0] if nic.IPAddress else 'N/A'})")
            # Disk info (jen systémový disk)
            sys_disk = next((p for p in psutil.disk_partitions() if p.mountpoint == os_wmi.SystemDrive + "\\"), None)
            if sys_disk:
                disk_usage = psutil.disk_usage(sys_disk.mountpoint)
                disk_str = f"{sys_disk.device} - {disk_usage.total // (1024**3)} GB, volné: {disk_usage.free // (1024**3)} GB, použito: {disk_usage.percent}%"
            else:
                disk_str = "Nezjištěno"
            # Baterie
            try:
                battery = psutil.sensors_battery()
                if battery:
                    battery_str = f"{battery.percent}% {'(nabíjí se)' if battery.power_plugged else '(na baterii)'}"
                else:
                    battery_str = "Nenalezena"
            except Exception:
                battery_str = "Nelze zjistit"
            # Rozlišení obrazovky
            try:
                import tkinter
                root = tkinter.Tk()
                root.withdraw()
                screen_res = f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}"
                root.destroy()
            except Exception:
                screen_res = "Nelze zjistit"
            # Počet fyzických RAM modulů a velikost každého
            try:
                ram_modules = self.wmi.Win32_PhysicalMemory()
                ram_info = ", ".join([f"{int(m.Capacity)//(1024**3)}GB" for m in ram_modules])
                ram_count = len(ram_modules)
            except Exception:
                ram_info = "Nezjištěno"
                ram_count = "Nezjištěno"
            # Antivir
            try:
                avs = self.wmi.root.SecurityCenter2.AntiVirusProduct()
                av_names = [av.displayName for av in avs]
                av_str = ", ".join(av_names) if av_names else "Nenalezen"
            except Exception:
                av_str = "Nelze zjistit"
            # Virtualizace, Secure Boot, TPM
            try:
                secure_boot = next(iter(self.wmi.Win32_BootConfiguration()), None)
                secure_boot_str = "Ano" if getattr(secure_boot, "SecureBoot", 0) == 1 else "Ne"
            except Exception:
                secure_boot_str = "Nelze zjistit"
            try:
                tpm = self.wmi.Win32_Tpm()[0]
                tpm_str = "Ano" if tpm.IsEnabled_InitialValue else "Ne"
            except Exception:
                tpm_str = "Nelze zjistit"
            try:
                bios_type = "UEFI" if "EFI" in bios.Caption.upper() else "Legacy"
            except Exception:
                bios_type = "Nelze zjistit"
            # Výrobce CPU
            try:
                cpu_manufacturer = sys_wmi.Manufacturer
            except Exception:
                cpu_manufacturer = "Nezjištěno"
            # Sériové číslo základní desky
            try:
                board = self.wmi.Win32_BaseBoard()[0]
                board_serial = board.SerialNumber
            except Exception:
                board_serial = "Nezjištěno"
            info = [
                f"Operační systém: {platform.system()} {platform.release()} ({platform.version()})",
                f"Build Windows: {os_wmi.BuildNumber}",
                f"Jazyk systému: {os_wmi.OSLanguage}",
                f"Název počítače: {platform.node()}",
                f"Uživatel: {os.getlogin()}",
                f"Architektura: {platform.machine()}",
                f"Procesor: {platform.processor()} ({cpu_manufacturer})",
                f"Počet jader: {os.cpu_count()}",
                f"RAM: {psutil.virtual_memory().total / (1024**3):.2f} GB ({ram_count} modulů: {ram_info})",
                f"Výrobce základní desky: {getattr(sys_wmi, 'Manufacturer', 'Nezjištěno')}",
                f"Model: {getattr(sys_wmi, 'Model', 'Nezjištěno')}",
                f"Sériové číslo základní desky: {board_serial}",
                f"Sériové číslo BIOSu: {getattr(bios, 'SerialNumber', 'Nezjištěno')}",
                f"Verze BIOSu: {getattr(bios, 'SMBIOSBIOSVersion', 'Nezjištěno')}",
                f"Typ BIOSu: {bios_type}",
                f"Secure Boot: {secure_boot_str}",
                f"TPM: {tpm_str}",
                f"Antivir: {av_str}",
                f"Čas spuštění systému: {boot_time_dt.strftime('%d.%m.%Y %H:%M:%S')}",
                f"Uptime: {str(uptime).split('.')[0]}",
                f"GPU: {', '.join(gpus)}",
                f"Síťová karta: {', '.join(netinfo) if netinfo else 'Nezjištěno'}",
                f"Systémový disk: {disk_str}",
                f"Baterie: {battery_str}",
                f"Rozlišení obrazovky: {screen_res}"
            ]
            return "\n".join(info)
        except Exception as e:
            return f"CHYBA: {str(e)}"
    
    def get_gpu_info(self):
        try:
            gpus = self.wmi.Win32_VideoController()
            gpu_list = []
            for gpu in gpus:
                gpu_list.append(f"{gpu.Name} ({gpu.AdapterRAM // (1024**3)} GB VRAM, {gpu.DriverVersion})")
            return gpu_list if gpu_list else ["Nezjištěno"]
        except Exception:
            return ["Chyba detekce"]
    
    def get_disk_info(self):
        try:
            disk_info = []
            for part in psutil.disk_partitions():
                if part.mountpoint:
                    try:
                        usage = psutil.disk_usage(part.mountpoint)
                        disk_type = "SSD" if "SSD" in part.device.upper() or "NVME" in part.device.upper() else "HDD"
                        disk_info.append(
                            f"{part.device} ({disk_type}):\n"
                            f"  Systém: {'Ano' if part.mountpoint == os.environ.get('SystemDrive', 'C:')+'\\' else 'Ne'}\n"
                            f"  Celkem: {usage.total // (1024**3)} GB\n"
                            f"  Volné: {usage.free // (1024**3)} GB\n"
                            f"  Použito: {usage.percent}%\n"
                            f"  Souborový systém: {part.fstype}"
                        )
                    except Exception:
                        continue
            return "\n\n".join(disk_info) or "Žádné disky"
        except Exception as e:
            return f"CHYBA: {str(e)}"
    
    def get_battery_info(self):
        try:
            battery = psutil.sensors_battery()
            if battery:
                info = [
                    f"Stav: {battery.percent}%",
                    f"Nabíjení: {'Ano' if battery.power_plugged else 'Ne'}",
                    f"Zbývající čas: {battery.secsleft // 60 if battery.secsleft > 0 else 'Neznámý'} minut"
                ]
                return "\n".join(info)
            return "Baterie nenalezena"
        except Exception as e:
            return f"CHYBA: {str(e)}"
    
    def get_network_info(self):
        try:
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            mac = ":".join(["{:02x}".format((uuid.getnode() >> i) & 0xff) for i in range(5, -1, -1)])
            info = [
                "=== ZÁKLADNÍ INFORMACE ===",
                f"Hostname: {hostname}",
                f"IP adresa: {ip}",
                f"MAC adresa: {mac}",
                "",
                "=== SÍŤOVÁ ROZHRANÍ ==="
            ]
            interfaces = psutil.net_if_addrs()
            for interface_name, interface_addresses in interfaces.items():
                info.append(f"\nRozhraní: {interface_name}")
                for address in interface_addresses:
                    info.append(f"  {address.family.name}: {address.address}")
            # Výpis aktivních síťových připojení
            info.append("\n=== AKTIVNÍ PŘIPOJENÍ ===")
            connections = psutil.net_connections(kind='inet')
            found = False
            for conn in connections:
                if conn.raddr:
                    found = True
                    laddr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "?"

                    raddr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "?"
                    info.append(f"{laddr} -> {raddr} ({conn.status})")
            if not found:
                info.append("Žádná aktivní připojení")
            return "\n".join(info)
        except Exception as e:
            return f"CHYBA: {str(e)}"
    
    def get_connections(self):
        try:
            conns = []
            for conn in psutil.net_connections():
                if conn.status == "ESTABLISHED":
                    proc = ""
                    try:
                        proc = f" ({psutil.Process(conn.pid).name()})" if conn.pid else ""
                    except Exception:
                        pass
                    conns.append(f"{conn.laddr.ip}:{conn.laddr.port} -> {conn.raddr.ip}:{conn.raddr.port}{proc}")
            return "\n".join(conns) if conns else "Žádná aktivní připojení"
        except Exception as e:
            return f"CHYBA: {str(e)}"
    
    def get_users(self):
        try:
            users = []
            for user in self.wmi.Win32_UserAccount():
                # Kontrola členství ve skupině Administrators
                groups = [g.Name for g in user.associators(wmi_result_class='Win32_Group')]
                is_admin = "Ano" if "Administrators" in groups or "Administrátoři" in groups else "Ne"
                stav = "Zakázán" if user.Disabled else "Povoleno"
                users.append(f"{user.Name} (Admin: {is_admin}, {stav}, SID: {user.SID})")
            return "\n".join(users) if users else "Žádní uživatelé"
        except Exception as e:
            return f"CHYBA: {str(e)}"
    
    def run_diagnostics(self):
        try:
            issues = []
            disk = psutil.disk_usage(os.environ.get('SystemDrive', 'C:') + "\\")
            if disk.percent > 90:
                issues.append("Varování: Málo místa na systémovém disku")
            cpu_load = psutil.cpu_percent(interval=1)
            if cpu_load > 80:
                issues.append(f"Varování: Vysoké využití CPU ({cpu_load}%)")
            ram = psutil.virtual_memory()
            if ram.percent > 80:
                issues.append(f"Varování: Vysoké využití RAM ({ram.percent}%)")
            # Kontrola běžících služeb
            try:
                services = [s for s in self.wmi.Win32_Service() if s.State != "Running" and s.StartMode == "Auto"]
                if services:
                    issues.append("Nefungující automatické služby:\n" + "\n".join([s.Name for s in services]))
            except Exception:
                pass
            # Kontrola aktualizací
            try:
                updates = self.wmi.Win32_QuickFixEngineering()
                if not updates:
                    issues.append("Varování: Nebyly nalezeny žádné aktualizace systému.")
            except Exception:
                pass
            return "\n".join(issues) if issues else "Žádné problémy zjištěny"
        except Exception as e:
            return f"CHYBA: {str(e)}"
    
    def optimize(self):
        try:
            import shutil
            deleted = 0
            failed = 0
            # Složky k čištění
            folders = [
                os.getenv('TEMP'),
                os.path.expandvars(r'%SystemRoot%\Temp'),
                os.path.expandvars(r'%USERPROFILE%\AppData\Local\Temp'),
                os.path.expandvars(r'%USERPROFILE%\AppData\Local\Microsoft\Windows\INetCache'),
                os.path.expandvars(r'%USERPROFILE%\AppData\Local\Microsoft\Windows\Explorer'),
                os.path.expandvars(r'%USERPROFILE%\AppData\Local\Microsoft\Windows\WebCache'),
                os.path.expandvars(r'%USERPROFILE%\AppData\Local\Google\Chrome\User Data\Default\Cache'),
                os.path.expandvars(r'%USERPROFILE%\AppData\Local\Mozilla\Firefox\Profiles'),
                os.path.expandvars(r'%USERPROFILE%\AppData\Local\Microsoft\Edge\User Data\Default\Cache'),
                os.path.expandvars(r'%SystemRoot%\Logs'),
                os.path.expandvars(r'%USERPROFILE%\AppData\Local\CrashDumps'),
                os.path.expandvars(r'%USERPROFILE%\AppData\Local\Microsoft\Windows\WER'),
            ]
            for folder in folders:
                if folder and os.path.exists(folder):
                    for rootdir, dirs, files in os.walk(folder, topdown=False):
                        for name in files:
                            try:
                                file_path = os.path.join(rootdir, name)
                                os.remove(file_path)
                                deleted += 1
                            except Exception:
                                failed += 1
                        for name in dirs:
                            try:
                                dir_path = os.path.join(rootdir, name)
                                shutil.rmtree(dir_path, ignore_errors=True)
                            except Exception:
                                failed += 1
            # Vyprázdnit koš
            try:
                import winshell
                winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
            except Exception:
                pass
            # Vyčištění DNS cache
            try:
                subprocess.run(["ipconfig", "/flushdns"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass
            return f"Optimalizace dokončena. Smazáno {deleted} souborů, {failed} se nepodařilo smazat. DNS cache vyčištěna."
        except Exception as e:
            return f"CHYBA: {str(e)}"
    
    def create_admin(self, username, password):
        try:
            subprocess.run(['net', 'user', username, password, '/add'], check=True)
            subprocess.run(['net', 'localgroup', 'administrators', username, '/add'], check=True)
            return f"Účet {username} vytvořen"
        except Exception as e:
            return f"CHYBA: {str(e)}"
    
    def open_port(self, port, protocol="TCP"):
        """Otevře port ve firewallu"""
        try:
            subprocess.check_call([
                "netsh", "advfirewall", "firewall", "add", "rule",
                f"name=OpenPort{port}", f"dir=in", f"action=allow",
                f"protocol={protocol}", f"localport={port}"
            ])
            return f"Port {port}/{protocol} byl povolen ve firewallu."
        except Exception as e:
            return f"CHYBA: {str(e)}"

    def close_port(self, port, protocol="TCP"):
        """Zavře port ve firewallu"""
        try:
            subprocess.check_call([
                "netsh", "advfirewall", "firewall", "delete", "rule",
                f"name=OpenPort{port}", f"protocol={protocol}", f"localport={port}"
            ])
            return f"Port {port}/{protocol} byl odebrán z firewallu."
        except Exception as e:
            return f"CHYBA: {str(e)}"

    def list_wifi_networks(self):
        """Vrátí seznam dostupných WiFi sítí"""
        try:
            result = subprocess.check_output(
                ['netsh', 'wlan', 'show', 'networks', 'mode=Bssid'],
                encoding='utf-8', errors='ignore'
            )
            return result
        except Exception as e:
            return f"CHYBA: {str(e)}"

    def connect_wifi(self, ssid, password=None):
        """Pokusí se připojit k WiFi síti (musí být uložený profil nebo zadat heslo)"""
        try:
            if password:
                # Vytvoření dočasného XML profilu
                profile = f"""
                <WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
                    <name>{ssid}</name>
                    <SSIDConfig>
                        <SSID>
                            <name>{ssid}</name>
                        </SSID>
                    </SSIDConfig>
                    <connectionType>ESS</connectionType>
                    <connectionMode>auto</connectionMode>
                    <MSM>
                        <security>
                            <authEncryption>
                                <authentication>WPA2PSK</authentication>
                                <encryption>AES</encryption>
                                <useOneX>false</useOneX>
                            </authEncryption>
                            <sharedKey>
                                <keyType>passPhrase</keyType>
                                <protected>false</protected>
                                <keyMaterial>{password}</keyMaterial>
                            </sharedKey>
                        </security>
                    </MSM>
                </WLANProfile>
                """
                with open("wifi_profile.xml", "w", encoding="utf-8") as f:
                    f.write(profile)
                subprocess.check_call(['netsh', 'wlan', 'add', 'profile', 'filename="wifi_profile.xml"'])
                os.remove("wifi_profile.xml")
            subprocess.check_call(['netsh', 'wlan', 'connect', f'name={ssid}'])
            return f"Připojeno k síti {ssid}."
        except Exception as e:
            return f"CHYBA: {str(e)}"

    def disconnect_wifi(self):
        """Odpojí WiFi"""
        try:
            subprocess.check_call(['netsh', 'wlan', 'disconnect'])
            return "WiFi odpojena."
        except Exception as e:
            return f"CHYBA: {str(e)}"



    def flush_dns(self):
        try:
            subprocess.run(["ipconfig", "/flushdns"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return "DNS cache byla vymazána."
        except Exception as e:
            return f"CHYBA: {str(e)}"

    def show_system_log(self):
        try:
            result = subprocess.check_output(
                ['wevtutil', 'qe', 'System', '/q:*[System[(Level=2)]]', '/c:20', '/f:text'],
                encoding='utf-8', errors='ignore'
            )
            return result or "Žádné chyby v systémovém logu."
        except Exception as e:
            return f"CHYBA: {str(e)}"

    def list_processes(self):
        try:
            procs = []
            header = f"{'PID':>6} | {'Název procesu':<25} | {'CPU':>5} | {'RAM':>7} | {'Uživatel'}"
            procs.append(header)
            procs.append("-" * 65)
            for p in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_info']):
                pid = str(p.info['pid'])
                name = (p.info['name'] or "")[:25]
                cpu = f"{p.info['cpu_percent']:>3}%"
                ram = f"{(p.info['memory_info'].rss // (1024*1024)):>5} MB"
                user = p.info['username'] or ""
                procs.append(f"{pid:>6} | {name:<25} | {cpu:>5} | {ram:>7} | {user}")
            return "\n".join(procs)
        except Exception as e:
            return f"CHYBA: {str(e)}"
    
    def remove_user(self, username):
        """
        Odebere uživatelský účet z Windows.
        Tato akce trvale smaže uživatelský profil a data daného uživatele.
        Ovlivní Windows tak, že uživatel se již nebude moci přihlásit a jeho data budou odstraněna.
        """
        try:
            subprocess.run(['net', 'user', username, '/delete'], check=True)
            return f"Uživatel {username} byl odebrán."
        except Exception as e:
            return f"CHYBA: {str(e)}"

    def deactivate_windows(self):
        """
        Deaktivuje Windows odebráním produktového klíče.
        Systém Windows přejde do neregistrovaného stavu, zobrazí se vodoznak a některé funkce budou omezeny.
        """
        try:
            subprocess.run(['slmgr.vbs', '/upk'], check=True, shell=True)
            subprocess.run(['slmgr.vbs', '/cpky'], check=True, shell=True)
            return "Windows byl deaktivován (produktový klíč odebrán)."
        except Exception as e:
            return f"CHYBA: {str(e)}"

    def run_speedtest(self):
        try:
            st = speedtest.Speedtest()
            st.get_best_server()
            download = st.download()
            upload = st.upload()
            ping = st.results.ping
            return f"Ping: {ping:.1f} ms\nStahování: {download/1_000_000:.2f} Mbps\nOdesílání: {upload/1_000_000:.2f} Mbps"
        except Exception as e:
            return f"CHYBA: {str(e)}"

class ModernSystemManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Správce Systému")
        self.geometry("1200x800")
        self.style = Style(theme="darkly")  # tmavý motiv ttkbootstrap

        # Slovník pro povolení/zakázání systémových nástrojů
        self.sys_tools_enabled = {
            "Správce zařízení": True,
            "Správce služeb": True,
            "Správce disků": True,
            "Správce úloh": True,
            "Editor registru": True,
            "Prohlížeč událostí": True,
            "Konfigurace systému": True
        }

        # Nový seznam všech citlivých funkcí (NÁSTROJE, SÍŤ, DIAGNOSTIKA, OPTIMALIZACE)
        self.locked_functions = {
            "Aktivovat Windows": False,
            "Vytvořit admina": False,
            "Vymazat DNS cache": False,
            "Systémový log (chyby)": False,
            "Běžící procesy": False,
            "Odebrat uživatele": False,         # zamčeno
            "Deaktivovat Windows": False,       # zamčeno
            "Síťové informace": False,
            "Aktivní připojení": False,
            "Otevřít port": False,
            "Zavřít port": False,
            "Seznam WiFi sítí": False,
            "Připojit k WiFi": False,
            "Odpojit WiFi": False,
            "Diagnostika": False,
            "Optimalizace": False
        }

        # Initialize system manager
        self.system_manager = SystemManager()
        self.task_queue = queue.Queue()
        
        # Setup UI with red/black theme
        self.setup_ui()
        
        # Initialize colored text
        self.ctext = ColoredText(self.info_text)
        
        # Start queue checker
        self.after(100, self.check_queue)
    
    def setup_ui(self):
        """Set up the modern UI with red/black theme"""
        # Configure main window
        self.configure(bg='#000000')
        
        # Create main container
        self.main_container = tk.Frame(self, bg='#000000')
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header with logo
        self.setup_header()
        
        # Content area
        self.setup_content()
        
        # Footer
        self.setup_footer()
    
    def setup_header(self):
        """Create the header with logo and title"""
        header_frame = tk.Frame(self.main_container, bg="#000000")
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Logo placeholder (you can replace with actual image)
        self.logo_label = tk.Label(
            header_frame,
            text="⚙️",
            font=("Segoe UI", 24),
            fg="#FF0000",
            bg="#000000"
        )
        self.logo_label.pack(side=tk.LEFT)
        
        # Title
        self.title_label = tk.Label(
            header_frame,
            text="MODERNÍ SPRÁVCE SYSTÉMU",
            font=("Segoe UI", 20, "bold"),
            fg="#FFFFFF",
            bg="#111111"
        )
        self.title_label.pack(side=tk.LEFT, padx=10)
        
        # Správce by vufdux
        self.admin_label = tk.Label(
            header_frame,
            text="správce by vufdux",
            font=("Segoe UI", 10, "italic"),
            fg="#FF0000",
            bg="#000000"
        )
        self.admin_label.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Version
        self.version_label = tk.Label(
            header_frame,
            text="v1.2",
            font=("Segoe UI", 10),
            fg="#FF6666",
            bg="#000000"
        )
        self.version_label.pack(side=tk.RIGHT)
    
    def setup_content(self):
        """Set up the main content area with buttons and output"""
        content_frame = tk.Frame(self.main_container, bg='#000000')
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - buttons
        self.setup_button_panel(content_frame)
        
        # Right panel - output
        self.setup_output_panel(content_frame)
    
    def setup_button_panel(self, parent):
        """Create the button panel with modern black/red buttons and scrolling"""
        canvas = tk.Canvas(parent, bg='#000000', highlightthickness=0, width=270)
        canvas.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20), expand=False)

        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)

        button_frame = tk.Frame(canvas, bg='#000000')
        button_frame_id = canvas.create_window((0, 0), window=button_frame, anchor="nw")

        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        button_frame.bind("<Configure>", on_frame_configure)
        canvas.configure(yscrollcommand=scrollbar.set)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        categories = [
            ("SYSTÉM", [
                ("Systémové informace", self.show_system_info),
                ("Diagnostika", self.run_diagnostics),
                ("Optimalizace", self.optimize_system)
            ]),
            ("DISK", [
                ("Diskové informace", self.check_disk_space),
                ("Uživatelé", self.show_users)
            ]),
            ("SÍŤ", [
                ("Síťové informace", self.show_network_info),
                ("Aktivní připojení", self.show_connections),
                ("Otevřít port", self.open_port_dialog),
                ("Zavřít port", self.close_port_dialog),
                ("Seznam WiFi sítí", self.list_wifi_dialog),
                ("Připojit k WiFi", self.connect_wifi_dialog),
                ("Odpojit WiFi", self.disconnect_wifi_dialog),
            ]),
            ("NÁSTROJE", [
                ("Aktivovat Windows", self.activate_windows),
                ("Vytvořit admina", self.admin_tools),
                ("Vymazat DNS cache", self.flush_dns_dialog),
                ("Systémový log (chyby)", self.show_system_log_dialog),
                ("Běžící procesy", self.list_processes_dialog),
                ("Odebrat uživatele", self.remove_user_dialog),
                ("Deaktivovat Windows", self.deactivate_windows_dialog)
            ]),
            ("SYSTÉMOVÉ NÁSTROJE", [
                ("Správce zařízení", lambda: self.run_sys_tool("Správce zařízení")),
                ("Správce služeb", lambda: self.run_sys_tool("Správce služeb")),
                ("Správce disků", lambda: self.run_sys_tool("Správce disků")),
                ("Správce úloh", lambda: self.run_sys_tool("Správce úloh")),
                ("Editor registru", lambda: self.run_sys_tool("Editor registru")),
                ("Prohlížeč událostí", lambda: self.run_sys_tool("Prohlížeč událostí")),
                ("Konfigurace systému", lambda: self.run_sys_tool("Konfigurace systému")),
                ("Odemknout", self.unlock_functions_dialog)  # přejmenováno z "Správa systémových funkcí"
            ])
        ]

        # Ulož si referenci na tlačítka, která mají být vypínatelná
        self.btn_remove_user = None
        self.btn_deactivate_windows = None

        # Ulož si referenci na tlačítka systémových nástrojů
        self.sys_tool_buttons = {}

        # Zamykatelné tlačítko
        self.locked_buttons = {}

        for category, buttons in categories:
            # Kategorie label
            cat_label = tk.Label(
                button_frame,
                text=category,
                font=("Segoe UI", 11, "bold"),
                fg="#FFFFFF",
                bg="#181818",  # tmavší šedá pro oddělení kategorií
                anchor="w"
            )
            cat_label.pack(fill=tk.X, pady=(15, 5))

            # Tlačítka
            for text, command in buttons:
                btn = tk.Button(
                    button_frame,
                    text=text,
                    command=command,
                    bg="#111111",                # černé tlačítko
                    fg="#FFFFFF",                # bílé písmo
                    activebackground="#FF2222",  # jasně červená po kliknutí
                    activeforeground="#FFFFFF",
                    font=("Segoe UI", 10, "bold"),
                    relief=tk.FLAT,
                    bd=0,
                    padx=20,
                    pady=8,
                    width=20,
                    highlightthickness=0,           # odstraní modrý rámeček
                    borderwidth=0,                  # odstraní rámeček
                    highlightbackground="#111111",
                    highlightcolor="#111111"
                )
                btn.pack(fill=tk.X, pady=3)
                btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#FF2222"))
                btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#111111"))
                if text in self.locked_functions:
                    self.locked_buttons[text] = btn
                if text == "Odebrat uživatele":
                    self.btn_remove_user = btn
                if text == "Deaktivovat Windows":
                    self.btn_deactivate_windows = btn
                if category == "SYSTÉMOVÉ NÁSTROJE" and text != "Odemknout":
                    self.sys_tool_buttons[text] = btn

        # Funkce pro aktualizaci stavu zamčených tlačítek
        def update_locked_buttons():
            for name, btn in self.locked_buttons.items():
                btn.config(state=tk.NORMAL if self.locked_functions.get(name, False) else tk.DISABLED)
        self.update_locked_buttons = update_locked_buttons
        self.after(100, update_locked_buttons)

        # Funkce pro aktualizaci stavu tlačítek
        def update_sys_tool_buttons():
            for name, btn in self.sys_tool_buttons.items():
                btn.config(state=tk.NORMAL if self.sys_tools_enabled.get(name, True) else tk.DISABLED)
        self.update_sys_tool_buttons = update_sys_tool_buttons
        self.after(100, update_sys_tool_buttons)

    def setup_output_panel(self, parent):
        """Create the output panel with modern styling"""
        output_frame = tk.Frame(parent, bg='#000000')
        output_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.info_text = tk.Text(
            output_frame,
            wrap=tk.WORD,
            font=("Consolas", 11),
            bg='#000000',         # černé pozadí konzole
            fg='#FFFFFF',         # bílé písmo
            insertbackground='#FFFFFF',
            selectbackground='#222222',
            padx=15,
            pady=15,
            relief=tk.FLAT,
            highlightthickness=0,
            borderwidth=0,
        )
        
        scrollbar = ttk.Scrollbar(
            output_frame,
            orient=tk.VERTICAL,
            command=self.info_text.yview
        )
        self.info_text.config(yscrollcommand=scrollbar.set)
        
        self.info_text.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        output_frame.grid_rowconfigure(0, weight=1)
        output_frame.grid_columnconfigure(0, weight=1)
    
    def setup_footer(self):
        """Create the footer"""
        footer_frame = tk.Frame(self.main_container, bg='#000000')
        footer_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.status_label = tk.Label(
            footer_frame,
            text="Připraveno",
            font=("Segoe UI", 9),
            fg="#FFFFFF",
            bg="#181818",
            anchor="w"
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        close_btn = tk.Button(
            footer_frame,
            text="Zavřít",
            command=self.quit_app,
            bg="#111111",
            fg="#FFFFFF",
            activebackground="#FF2222",
            activeforeground="#FFFFFF",
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            bd=0,
            padx=15,
            pady=3
        )
        close_btn.pack(side=tk.RIGHT)
        close_btn.bind("<Enter>", lambda e, b=close_btn: b.config(bg="#FF2222"))
        close_btn.bind("<Leave>", lambda e, b=close_btn: b.config(bg="#111111"))
    
    def check_queue(self):
        """Process tasks from the queue"""
        try:
            while True:
                callback, result = self.task_queue.get_nowait()
                callback(result) if result is not None else callback()
        except queue.Empty:
            pass
        self.after(100, self.check_queue)
    
    def run_in_thread(self, func, args=(), callback=None):
        """Run function in background thread"""
        def thread_wrapper():
            try:
                result = func(*args)
                if callback:
                    self.task_queue.put((callback, result))
            except Exception as e:
                self.task_queue.put((lambda: messagebox.showerror("Chyba", str(e)), None))
        
        threading.Thread(target=thread_wrapper, daemon=True).start()
    
    def display_section(self, title, content, content_tag='info'):
        """Display formatted section with title and content"""
        self.ctext.insert(title, 'title')
        self.ctext.insert(content, content_tag)
        self.status_label.config(text="Operace dokončena")
    
    # Button command methods
    def show_system_info(self):
        self.clear_output()
        self.status_label.config(text="Načítám systémové informace...")
        self.display_section("\n=== SYSTÉMOVÉ INFORMACE ===\n", "Načítám...", 'command')
        self.run_in_thread(
            self.system_manager.get_system_info,
            callback=lambda res: self.display_section("\nVýsledky:\n", res, 'system')
        )
    
    def check_disk_space(self):
        self.clear_output()
        self.status_label.config(text="Kontroluji stav disků...")
        self.display_section("\n=== DISKOVÉ INFORMACE ===\n", "Kontroluji...", 'command')
        self.run_in_thread(
            self.system_manager.get_disk_info,
            callback=lambda res: self.display_section("\nVýsledky:\n", res, 'highlight')
        )
    
    def show_network_info(self):
        self.clear_output()
        self.status_label.config(text="Načítám síťové informace...")
        self.display_section("\n=== SÍŤOVÉ INFORMACE ===\n", "Načítám...", 'command')
        self.run_in_thread(
            self.system_manager.get_network_info,
            callback=lambda res: self.display_section("\nVýsledky:\n", res, 'network')
        )
    
    def show_connections(self):
        self.clear_output()
        self.status_label.config(text="Načítám aktivní připojení...")
        self.display_section("\n=== SÍŤOVÁ PŘIPOJENÍ ===\n", "Načítám...", 'command')
        self.run_in_thread(
            self.system_manager.get_connections,
            callback=lambda res: self.display_section("\nVýsledky:\n", res, 'info')
        )
    
    def show_users(self):
        self.clear_output()
        self.status_label.config(text="Načítám seznam uživatelů...")
        self.display_section("\n=== UŽIVATELSKÉ ÚČTY ===\n", "Načítám...", 'command')
        self.run_in_thread(
            self.system_manager.get_users,
            callback=lambda res: self.display_section("\nVýsledky:\n", res, 'info')
        )
    
    def run_diagnostics(self):
        self.clear_output()
        self.status_label.config(text="Provádím diagnostiku...")
        self.display_section("\n=== DIAGNOSTIKA SYSTÉMU ===\n", "Provádím...", 'command')
        self.run_in_thread(
            self.system_manager.run_diagnostics,
            callback=lambda res: self.display_section("\nVýsledky:\n", res, 'warning' if "Varování:" in res else 'success')
        )
    
    def optimize_system(self):
        self.clear_output()
        self.status_label.config(text="Provádím optimalizaci...")
        self.display_section("\n=== OPTIMALIZACE SYSTÉMU ===\n", "Provádím...", 'command')
        self.run_in_thread(
            self.system_manager.optimize,
            callback=lambda res: self.display_section("\nVýsledky:\n", res, 'success')
        )
    
    def activate_windows(self):
        self.clear_output()
        self.status_label.config(text="Spouštím aktivaci Windows...")
        self.display_section("\n=== AKTIVACE WINDOWS ===\n", "Spouštím...", 'command')
        self.run_in_thread(
            self.system_manager.activate_windows,
            callback=lambda res: self.display_section("\nVýsledky:\n", res, 'activation')
        )
    
    def admin_tools(self):
        username = simpledialog.askstring("Admin", "Uživatelské jméno:")
        if username:
            password = simpledialog.askstring("Admin", "Heslo:", show="*")
            if password:
                self.clear_output()
                self.status_label.config(text=f"Vytvářím účet {username}...")
                self.display_section("\n=== VYTVÁŘÍM ADMIN ÚČET ===\n", f"Vytvářím...", 'command')
                self.run_in_thread(
                    self.system_manager.create_admin,
                    args=(username, password),
                    callback=lambda res: self.display_section("\nVýsledky:\n", res, 'success' if "vytvořen" in res else 'error')
                )
    
    def open_port_dialog(self):
        port = simpledialog.askinteger("Otevřít port", "Zadejte číslo portu:")
        if port:
            protocol = simpledialog.askstring("Protokol", "Zadejte protokol (TCP/UDP):", initialvalue="TCP")
            self.clear_output()
            self.status_label.config(text=f"Otevírám port {port}/{protocol}...")
            self.display_section("\n=== OTEVÍRÁNÍ PORTU ===\n", f"Otevírám port {port}/{protocol}...", 'command')
            self.run_in_thread(
                self.system_manager.open_port,
                args=(port, protocol),
                callback=lambda res: self.display_section("\nVýsledky:\n", res, 'success' if "povolen" in res else 'error')
            )

    def close_port_dialog(self):
        port = simpledialog.askinteger("Zavřít port", "Zadejte číslo portu:")
        if port:
            protocol = simpledialog.askstring("Protokol", "Zadejte protokol (TCP/UDP):", initialvalue="TCP")
            self.clear_output()
            self.status_label.config(text=f"Zavírám port {port}/{protocol}...")
            self.display_section("\n=== ZAVÍRÁNÍ PORTU ===\n", f"Zavírám port {port}/{protocol}...", 'command')
            self.run_in_thread(
                self.system_manager.close_port,
                args=(port, protocol),
                callback=lambda res: self.display_section("\nVýsledky:\n", res, 'success' if "odebrán" in res else 'error')
            )

    def list_wifi_dialog(self):
        self.clear_output()
        self.status_label.config(text="Načítám WiFi sítě...")
        self.display_section("\n=== DOSTUPNÉ WIFI SÍTĚ ===\n", "Načítám...", 'command')
        self.run_in_thread(
            self.system_manager.list_wifi_networks,
            callback=lambda res: self.display_section("\nVýsledky:\n", res, 'network')
        )

    def connect_wifi_dialog(self):
        ssid = simpledialog.askstring("Připojit k WiFi", "Zadejte název WiFi sítě (SSID):")
        if ssid:
            password = simpledialog.askstring("Heslo", "Zadejte heslo (nechte prázdné pro uložený profil):", show="*")
            self.clear_output()
            self.status_label.config(text=f"Připojuji k WiFi {ssid}...")
            self.display_section("\n=== PŘIPOJENÍ K WIFI ===\n", f"Připojuji k {ssid}...", 'command')
            self.run_in_thread(
                self.system_manager.connect_wifi,
                args=(ssid, password),
                callback=lambda res: self.display_section("\nVýsledky:\n", res, 'success' if "Připojeno" in res else 'error')
            )

    def disconnect_wifi_dialog(self):
        self.clear_output()
        self.status_label.config(text="Odpojuji WiFi...")
        self.display_section("\n=== ODPOJENÍ WIFI ===\n", "Odpojuji...", 'command')
        self.run_in_thread(
            self.system_manager.disconnect_wifi,
            callback=lambda res: self.display_section("\nVýsledky:\n", res, 'success' if "odpojena" in res else 'error')
        )
    
    def flush_dns_dialog(self):
        self.clear_output()
        self.status_label.config(text="Mažu DNS cache...")
        self.display_section("\n=== VYMAZÁNÍ DNS CACHE ===\n", "Mažu...", 'command')
        self.run_in_thread(
            self.system_manager.flush_dns,
            callback=lambda res: self.display_section("\nVýsledky:\n", res, 'success' if "vymazána" in res else 'error')
        )

    def show_system_log_dialog(self):
        self.clear_output()
        self.status_label.config(text="Načítám systémový log...")
        self.display_section("\n=== SYSTÉMOVÝ LOG (CHYBY) ===\n", "Načítám...", 'command')
        self.run_in_thread(
            self.system_manager.show_system_log,
            callback=lambda res: self.display_section("\nVýsledky:\n", res, 'error' if "CHYBA" in res else 'info')
        )

    def list_processes_dialog(self):
        self.clear_output()
        self.status_label.config(text="Načítám běžící procesy...")
        self.display_section("\n=== BĚŽÍCÍ PROCESY ===\n", "Načítám...", 'command')
        self.run_in_thread(
            self.system_manager.list_processes,
            callback=lambda res: self.display_section("\nVýsledky:\n", res, 'info')
        )
    
    def select_from_list(self, title, prompt, items):
        """Zobrazí dialog s výběrem položky ze seznamu"""
        win = tk.Toplevel(self)
        win.title(title)
        win.geometry("400x400")
        win.grab_set()
        tk.Label(win, text=prompt, font=("Segoe UI", 11, "bold")).pack(pady=10)
        lb = tk.Listbox(win, font=("Segoe UI", 10), selectmode=tk.SINGLE)
        lb.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        for item in items:
            lb.insert(tk.END, item)
        selected = {"value": None}
        def on_ok():
            sel = lb.curselection()
            if sel:
                selected["value"] = lb.get(sel[0])
                win.destroy()
        btn = tk.Button(win, text="Vybrat", command=on_ok, bg="#FF0000", fg="#FFF")
        btn.pack(pady=10)
        win.wait_window()
        return selected["value"]

    def remove_user_dialog(self):
        """Dialog pro odebrání uživatele (respektuje zamčení)"""
        if not self.locked_functions["Odebrat uživatele"]:
            messagebox.showwarning("Zakázáno", "Funkce odebrání uživatele je zakázána správcem.")
            return
        # Získání seznamu uživatelů
        users_raw = self.system_manager.get_users()
        users = []
        for line in users_raw.splitlines():
            if "(" in line:
                users.append(line.split(" (")[0])
        if not users:
            messagebox.showinfo("Uživatelé", "Nebyli nalezeni žádní uživatelé.")
            return
        username = self.select_from_list("Odebrat uživatele", "Vyberte uživatele k odebrání:", users)
        if username:
            self.clear_output()
            self.status_label.config(text=f"Odebírám uživatele {username}...")
            self.display_section("\n=== ODEBRÁNÍ UŽIVATELE ===\n", f"Odebírám {username}...", 'command')
            self.run_in_thread(
                self.system_manager.remove_user,
                args=(username,),
                callback=lambda res: self.display_section("\nVýsledky:\n", res, 'success' if "odebrán" in res else 'error')
            )

    def deactivate_windows_dialog(self):
        """Dialog pro deaktivaci Windows (respektuje zamčení)"""
        if not self.locked_functions["Deaktivovat Windows"]:
            messagebox.showwarning("Zakázáno", "Funkce deaktivace Windows je zakázána správcem.")
            return
        if messagebox.askyesno("Deaktivovat Windows", "Opravdu chcete deaktivovat Windows?"):
            self.clear_output()
            self.status_label.config(text="Deaktivuji Windows...")
            self.display_section("\n=== DEAKTIVACE WINDOWS ===\n", "Deaktivuji...", 'command')
            self.run_in_thread(
                self.system_manager.deactivate_windows,
                callback=lambda res: self.display_section("\nVýsledky:\n", res, 'activation' if "deaktivován" in res else 'error')
            )

    def unlock_functions_dialog(self):
        """Dialog pro odemykání funkcí s heslem a možností odemknout vše"""
        win = tk.Toplevel(self)
        win.title("Odemknout funkce")
        win.geometry("420x350")
        win.resizable(False, False)
        win.grab_set()

        tk.Label(win, text="Vyberte funkci pro povolení/zakázání:", font=("Segoe UI", 11, "bold")).pack(pady=10)

        func_names = list(self.locked_functions.keys())
        lb = tk.Listbox(win, font=("Segoe UI", 10), selectmode=tk.SINGLE, height=min(len(func_names), 12))
        for name in func_names:
            lb.insert(tk.END, name)
        lb.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        switch_var = tk.BooleanVar(value=False)
        switch_btn = tk.Checkbutton(
            win, text="Povolit funkci", variable=switch_var,
            onvalue=True, offvalue=False, font=("Segoe UI", 10, "bold"),
            bg="#000000", fg="#FF6666", selectcolor="#1E1E1E", anchor="e"
        )
        switch_btn.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)

        def on_select(event=None):
            sel = lb.curselection()
            if sel:
                name = func_names[sel[0]]
                switch_var.set(self.locked_functions[name])
        lb.bind("<<ListboxSelect>>", on_select)
        lb.selection_set(0)
        on_select()

        def on_switch():
            sel = lb.curselection()
            if sel:
                pwd = simpledialog.askstring("Heslo", "Zadejte heslo pro odemknutí:", show="☺")
                if pwd == "0000":
                    name = func_names[sel[0]]
                    self.locked_functions[name] = switch_var.get()
                    self.update_locked_buttons()
                else:
                    messagebox.showerror("Chyba", "Špatné heslo!")
                    switch_var.set(self.locked_functions[func_names[sel[0]]])
        switch_var.trace_add("write", lambda *a: on_switch())

        # Tlačítko "Odemknout vše"
        def unlock_all():
            pwd = simpledialog.askstring("Heslo", "Zadejte heslo pro odemknutí všeho (výchozí: 0000):", show="*")
            if pwd == "0000":
                for name in self.locked_functions:
                    self.locked_functions[name] = True
                self.update_locked_buttons()
                messagebox.showinfo("Hotovo", "Všechny funkce byly odemčeny.")
                win.lift()
            else:
                messagebox.showerror("Chyba", "Špatné heslo!")

        btn_unlock_all = tk.Button(win, text="Odemknout vše", command=unlock_all, bg="#FF6666", fg="#FFF", font=("Segoe UI", 10, "bold"))
        btn_unlock_all.pack(pady=(5, 0))

        tk.Button(win, text="Zavřít", command=win.destroy, bg="#FF0000", fg="#FFF").pack(pady=10)

    def manage_sys_tools_dialog(self):
        """Dialog pro správu povolení/zakázání systémových nástrojů"""
        win = tk.Toplevel(self)
        win.title("Správa systémových funkcí")
        win.geometry("400x250")
        win.resizable(False, False)
        win.grab_set()

        tk.Label(win, text="Vyberte nástroj pro povolení/zakázání:", font=("Segoe UI", 11, "bold")).pack(pady=10)

        tool_names = list(self.sys_tools_enabled.keys())
        lb = tk.Listbox(win, font=("Segoe UI", 10), selectmode=tk.SINGLE, height=len(tool_names))
        for name in tool_names:
            lb.insert(tk.END, name)
        lb.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        switch_var = tk.BooleanVar(value=True)
        switch_btn = tk.Checkbutton(
            win, text="Povolit nástroj", variable=switch_var,
            onvalue=True, offvalue=False, font=("Segoe UI", 10, "bold"),
            bg="#000000", fg="#FF6666", selectcolor="#1E1E1E", anchor="e"
        )
        switch_btn.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)

        def on_select(event=None):
            sel = lb.curselection()
            if sel:
                name = tool_names[sel[0]]
                switch_var.set(self.sys_tools_enabled[name])
        lb.bind("<<ListboxSelect>>", on_select)
        lb.selection_set(0)
        on_select()

        def on_switch():
            sel = lb.curselection()
            if sel:
                name = tool_names[sel[0]]
                self.sys_tools_enabled[name] = switch_var.get()
                self.update_sys_tool_buttons()
        switch_var.trace_add("write", lambda *a: on_switch())

        # Zavřít tlačítko
        tk.Button(win, text="Zavřít", command=win.destroy, bg="#FF0000", fg="#FFF").pack(pady=10)

    def clear_output(self):
        """Clear the output text area"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.config(state=tk.DISABLED)
        self.status_label.config(text="Připraveno")
    
    def quit_app(self):
        """Quit the application"""
        self.destroy()

    def run_sys_tool(self, tool_name):
        """Spustí vybraný systémový nástroj, pokud je povolen"""
        if not self.sys_tools_enabled.get(tool_name, True):
            messagebox.showwarning("Zakázáno", f"Funkce {tool_name} je zakázána správcem.")
            return
        try:
            if tool_name == "Správce zařízení":
                subprocess.Popen("devmgmt.msc", shell=True)
            elif tool_name == "Správce služeb":
                subprocess.Popen("services.msc", shell=True)
            elif tool_name == "Správce disků":
                subprocess.Popen("diskmgmt.msc", shell=True)
            elif tool_name == "Správce úloh":
                subprocess.Popen("taskmgr", shell=True)
            elif tool_name == "Editor registru":
                subprocess.Popen("regedit", shell=True)
            elif tool_name == "Prohlížeč událostí":
                subprocess.Popen("eventvwr", shell=True)
            elif tool_name == "Konfigurace systému":
                subprocess.Popen("msconfig", shell=True)
        except Exception as e:
            messagebox.showerror("Chyba", f"Nelze spustit {tool_name}: {str(e)}")

def run_as_admin():
    """Restart the program with admin privileges"""
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

if __name__ == "__main__":
    # Check and install required libraries
    required_libs = ["ttkbootstrap", "Pillow", "wmi", "psutil"]
    for lib in required_libs:
        try:
            __import__(lib)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib], 
                                stdout=subprocess.DEVNULL, 
                                stderr=subprocess.DEVNULL)
    
    run_as_admin()
    try:
        app = ModernSystemManager()
        app.mainloop()
    except Exception as e:
        messagebox.showerror("Chyba", f"Nelze spustit aplikaci: {str(e)}")
