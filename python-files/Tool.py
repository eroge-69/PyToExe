import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog, ttk
import ipaddress
import threading
from netmiko import ConnectHandler
from concurrent.futures import ThreadPoolExecutor, as_completed
import re

class NetworkDeviceBackupTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Network Device Scanner & Backup")

        # IP Bereich Eingabe
        frame_ip = ttk.LabelFrame(root, text="IP-Range eingeben")
        frame_ip.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        ttk.Label(frame_ip, text="Von:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_start_ip = ttk.Entry(frame_ip, width=15)
        self.entry_start_ip.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(frame_ip, text="Bis:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.entry_end_ip = ttk.Entry(frame_ip, width=15)
        self.entry_end_ip.grid(row=0, column=3, padx=5, pady=5)

        # Zugangsdaten
        frame_cred = ttk.LabelFrame(root, text="Zugangsdaten")
        frame_cred.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        ttk.Label(frame_cred, text="Benutzername:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_user = ttk.Entry(frame_cred, width=20)
        self.entry_user.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(frame_cred, text="Passwort:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.entry_pass = ttk.Entry(frame_cred, width=20, show="*")
        self.entry_pass.grid(row=0, column=3, padx=5, pady=5)

        # Geräteliste mit Scrollbar
        frame_list = ttk.LabelFrame(root, text="Gefundene Geräte")
        frame_list.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        self.device_listbox = tk.Listbox(frame_list, selectmode=tk.MULTIPLE, width=65, height=15)
        self.device_listbox.grid(row=0, column=0, sticky="nsew", padx=(5,0), pady=5)
        scrollbar = ttk.Scrollbar(frame_list, orient="vertical", command=self.device_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns", pady=5, padx=(0,5))
        self.device_listbox.config(yscrollcommand=scrollbar.set)

        frame_list.rowconfigure(0, weight=1)
        frame_list.columnconfigure(0, weight=1)

        # Fortschrittsbalken Scan
        self.progress_scan = ttk.Progressbar(root, orient="horizontal", length=600, mode="determinate")
        self.progress_scan.grid(row=3, column=0, padx=10, pady=(0,5), sticky="ew")

        # Fortschrittsbalken Backup
        self.progress_backup = ttk.Progressbar(root, orient="horizontal", length=600, mode="determinate")
        self.progress_backup.grid(row=4, column=0, padx=10, pady=(0,10), sticky="ew")

        # Buttons
        frame_buttons = ttk.Frame(root)
        frame_buttons.grid(row=5, column=0, pady=10)
        self.scan_button = ttk.Button(frame_buttons, text="Scan starten", command=self.start_scan)
        self.scan_button.grid(row=0, column=0, padx=10)
        self.backup_button = ttk.Button(frame_buttons, text="Backup erstellen", command=self.start_backup)
        self.backup_button.grid(row=0, column=1, padx=10)
        self.backup_all_button = ttk.Button(frame_buttons, text="Backup All", command=self.start_backup_all)
        self.backup_all_button.grid(row=0, column=2, padx=10)

        root.grid_rowconfigure(2, weight=1)
        root.grid_columnconfigure(0, weight=1)

        # Feste gültige Netmiko device_types (ohne dynamischen Import)
        self.device_type_mapping = {
            'aruba_os': 'hp_procurve',
            'hp_procurve': 'hp_procurve',
            'aruba_aoscx': 'aruba_aoscx',
            'cisco_ios': 'cisco_ios',
            'huawei': 'huawei',
            'fortinet': 'fortinet',
        }
        self.valid_device_types = {
            'cisco_ios', 'aruba_os', 'aruba_aoscx', 'hp_procurve', 'huawei', 'fortinet'
        }

    def get_netmiko_device_type(self, detected_type):
        candidate = self.device_type_mapping.get(detected_type)
        if candidate in self.valid_device_types:
            return candidate
        elif detected_type in self.valid_device_types:
            return detected_type
        else:
            return None

    def detect_device_type(self, ip, username, password):
        for detected_type in self.device_type_mapping.keys():
            netmiko_type = self.get_netmiko_device_type(detected_type)
            if not netmiko_type:
                continue
            try:
                conn = ConnectHandler(
                    device_type=netmiko_type,
                    ip=ip,
                    username=username,
                    password=password,
                    banner_timeout=20,
                    conn_timeout=10,
                )
                if netmiko_type == 'fortinet':
                    output = conn.send_command("get system status", expect_string=r'#')
                else:
                    output = conn.send_command("show version", expect_string=r'#')
                conn.disconnect()

                lower_out = output.lower()
                if 'aruba' in lower_out and 'aoscx' in lower_out:
                    return 'aruba_aoscx'
                elif 'aruba' in lower_out:
                    return 'aruba_os'
                elif 'cisco' in lower_out:
                    return 'cisco_ios'
                elif 'huawei' in lower_out:
                    return 'huawei'
                elif 'fortigate' in lower_out or 'fortinet' in lower_out:
                    return 'fortinet'
                elif 'procurve' in lower_out or 'hpe' in lower_out:
                    return 'hp_procurve'
                else:
                    return detected_type
            except Exception:
                continue
        return None

    def get_hostname(self, connection, device_type):
        try:
            prompt = connection.find_prompt()
            hostname = re.match(r'(\S+)[>#]', prompt)
            if hostname:
                return hostname.group(1)
        except Exception:
            pass
        try:
            if device_type in ['aruba_os', 'hp_procurve', 'huawei', 'cisco_ios', 'aruba_aoscx']:
                output = connection.send_command("show run | include hostname")
                match = re.search(r'hostname\s+(\S+)', output)
                if match:
                    return match.group(1)
            elif device_type == 'fortinet':
                output = connection.send_command("get system status")
                match = re.search(r'Hostname:\s+(\S+)', output)
                if match:
                    return match.group(1)
        except Exception:
            pass
        return "Unknown"

    def check_ip(self, ip, username, password):
        try:
            detected_type = self.detect_device_type(ip, username, password)
            if not detected_type:
                return None, ip, None
            netmiko_type = self.get_netmiko_device_type(detected_type)
            if not netmiko_type:
                return None, ip, None
            device_params = {
                'device_type': netmiko_type,
                'ip': ip,
                'username': username,
                'password': password,
            }
            conn = ConnectHandler(**device_params)
            conn.find_prompt()
            hostname = self.get_hostname(conn, detected_type)
            conn.disconnect()
            return detected_type, ip, hostname
        except Exception:
            return None, ip, None

    def scan_ips(self, start_ip, end_ip, username, password):
        device_list = []
        start_int = int(ipaddress.IPv4Address(start_ip))
        end_int = int(ipaddress.IPv4Address(end_ip))
        total = end_int - start_int + 1
        self.progress_scan['maximum'] = total
        self.progress_scan['value'] = 0

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for ip_int in range(start_int, end_int + 1):
                ip = str(ipaddress.IPv4Address(ip_int))
                futures.append(executor.submit(self.check_ip, ip, username, password))

            for future in as_completed(futures):
                device_type, ip, hostname = future.result()
                self.progress_scan['value'] += 1
                self.root.update_idletasks()
                if device_type:
                    device_list.append((device_type, ip, hostname))

        device_list.sort(key=lambda x: ipaddress.IPv4Address(x[1]))

        self.device_listbox.delete(0, tk.END)
        for device_type, ip, hostname in device_list:
            self.device_listbox.insert(tk.END, f"{ip} ({hostname}) [{device_type}]")
        messagebox.showinfo("Scan fertig", f"{len(device_list)} Geräte gefunden.")
        self.progress_scan['value'] = 0

    def extract_device_type(self, entry):
        match = re.search(r"\[([^\[\]]+)\]$", entry)
        return match.group(1) if match else None

    def backup_device(self, device_type, ip, username, password, folder):
        try:
            netmiko_type = self.get_netmiko_device_type(device_type)
            if not netmiko_type:
                raise ValueError(f"Ungültiger device_type: {device_type}")
            device_params = {
                'device_type': netmiko_type,
                'ip': ip,
                'username': username,
                'password': password,
            }
            conn = ConnectHandler(**device_params)

            if netmiko_type in ['hp_procurve', 'aruba_os', 'huawei', 'cisco_ios']:
                output = conn.send_command("show running-config")
            elif netmiko_type == 'aruba_aoscx':
                output = conn.send_command("show running-configuration")
            elif netmiko_type == 'fortinet':
                output = conn.send_command("show full-configuration")
            else:
                output = conn.send_command("show running-config")

            filepath = f"{folder}/backup_{ip}.txt"
            with open(filepath, "w") as f:
                f.write(output)

            conn.disconnect()
        except Exception as e:
            messagebox.showerror("Backup Fehler", f"{ip}: {e}")

    def backup_worker(self, devices, username, password, folder):
        total = len(devices)
        self.progress_backup['maximum'] = total
        self.progress_backup['value'] = 0

        for device_type, ip in devices:
            self.backup_device(device_type, ip, username, password, folder)
            self.progress_backup['value'] += 1
            self.root.update_idletasks()

        messagebox.showinfo("Backup fertig", f"Backups von {total} Geräten abgeschlossen.")
        self.progress_backup['value'] = 0

    def start_scan(self):
        start_ip = self.entry_start_ip.get().strip()
        end_ip = self.entry_end_ip.get().strip()
        username = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()
        if not (start_ip and end_ip and username and password):
            messagebox.showwarning("Fehler", "Bitte IP-Bereich und Zugangsdaten vollständig eingeben.")
            return
        self.device_listbox.delete(0, tk.END)
        threading.Thread(target=self.scan_ips, args=(start_ip, end_ip, username, password), daemon=True).start()

    def start_backup(self):
        selected = self.device_listbox.curselection()
        if not selected:
            messagebox.showwarning("Fehler", "Bitte mindestens ein Gerät auswählen.")
            return
        username = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()
        if not (username and password):
            messagebox.showwarning("Fehler", "Bitte Zugangsdaten eingeben.")
            return
        folder = filedialog.askdirectory(title="Backup-Ordner wählen")
        if not folder:
            return

        devices = []
        for idx in selected:
            entry = self.device_listbox.get(idx)
            ip = entry.split()[0]
            device_type = self.extract_device_type(entry)
            devices.append((device_type, ip))

        threading.Thread(target=self.backup_worker, args=(devices, username, password, folder), daemon=True).start()
        messagebox.showinfo("Backup gestartet", "Backups laufen im Hintergrund...")

    def start_backup_all(self):
        username = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()
        if not (username and password):
            messagebox.showwarning("Fehler", "Bitte Zugangsdaten eingeben.")
            return
        folder = filedialog.askdirectory(title="Backup-Ordner wählen")
        if not folder:
            return

        devices = []
        for idx in range(self.device_listbox.size()):
            entry = self.device_listbox.get(idx)
            ip = entry.split()[0]
            device_type = self.extract_device_type(entry)
            devices.append((device_type, ip))

        if not devices:
            messagebox.showwarning("Fehler", "Keine Geräte zum Backup gefunden.")
            return

        threading.Thread(target=self.backup_worker, args=(devices, username, password, folder), daemon=True).start()
        messagebox.showinfo("Backup gestartet", "Backups laufen im Hintergrund...")

if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkDeviceBackupTool(root)
    root.mainloop()
